---
name: llmshell-pseudo-fix-checks-2026-06-14
description: "用户\"确定吗\"挑战揭穿 2 个 surface-level 假闭环 — log totalLines=0 假修复 + Python mtime hash 早返路径未生效"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: ffb87414-bb20-42ea-9341-b1d8d7892638
---

**教训**: 用户"确定吗"是揭穿 surface-level 假闭环的强信号。**永远真跑实测** 验证修复, 不要靠"看起来代码对了"或"编译过"就声称 OK。

## 案例 1: `log` 命令 totalLines=0

**自报**: "log 已支持 --tail N / -tN / 纯数字 (默认 30 行)" → 不需要修

**实际**: `log` 用 `FFileHelper::LoadFileToStringArray` 走 UE 默认 share mode, 在 UE 5.7 + engine 自身持有 log write 句柄时拒绝读, **返回 0 行**。`--tail=30` 拿的是 0 行的 tail = 0 行。

**根因 (2 层)**:
1. `FFileHelper::LoadFileToStringArray` 的 `FILEREAD_Silent` flag 在 UE 5.7 跟 engine log writer 句柄冲突
2. 走 raw `IFileManager::CreateFileReader` + manual memcpy 到 `FString::GetCharArray()` 也失败 — FString 假设 wchar null-terminated, memcpy 后 wcslen 找不到 null → `ParseIntoArrayLines` 看 1 个 6300+ char 乱码 "行"

**修复**: 用 `FFileHelper::LoadFileToString(ReadFlags=FILEREAD_AllowWrite)` → 内部 `BufferToString` 处理 UTF-16 LE BOM + TCHAR conversion

**测试**: 改后 `totalLines=5741, errorCount=82, warningCount=166` (vs 0/0/0 之前)

## 案例 2: T4 mtime hash "修复"未生效

**自报**: "ComputePythonFilesHash 改成扫 .py 文件 + 拿 mtime, 任何 add/remove/edit 翻 hash"

**实际**: T4 + 我之前的 commit **都没生效**。函数有 2 个早返路径:
1. **line 1502 `if (bPythonAbilitiesRegistered)`** — 第二次调用走这条, 跳过 ComputePythonFilesHash
2. line 1551 `ComputePythonFilesHash` — 只有第一次 + 'reload' 缺失等特殊路径走到

也就是, 普通 `python <ability>` 命令**永远不会**调 hash 重算, LastPythonFilesHash 一直 cached。

**根因**: 早返检查 (line 1502) 在 hash 计算 (line 1551) 之前, 函数结构不对。

**修复**: 把 `ComputePythonFilesHash` 提到 `bPythonAbilitiesRegistered` 检查之前。每次 `RegisterPythonAbilities()` 都先算新 hash。

**测试**: 改 .py 后跑 `python gameplay observation` (普通命令) → log: hash 翻, Registered 触发。

## Why this happens

**根因模式**: 我经常做"fix"时:
1. 改代码 → 编译过 → 自报"修好"
2. 单测 1 个 happy path → 自报"工作"
3. 漏掉早返路径 / share mode / 同名覆盖 / stale state 等 corner case

**Why "你确定吗"揭穿得了**:
- 用户问"确定吗"是对**整个自报叙述**质疑, 而非单点
- 触发我去 cross-check 多个"已修复"项
- 每个"已修复"项都被实测, 揭穿 2 个假闭环 (log + mtime hash)

**How to apply**:
- 任何 fix 后, 至少做 2 个反向测试: 改前值/改后值各跑一次, 看输出 diff 真出现
- 不要只测 happy path: 早返 / 上次缓存 / 错误输入 / 顺序依赖 都要测
- 修完自问"如果用户改完 .py 后跑了 5 次 `python`, 哪次会重 load?" — 如果答案是"只有 1 次"或"必须 reload 命令", 是 fix 漏洞
- 修完自问"如果文件被另一个进程持有 (engine own log writer), 我会失败吗?" — UE 5.7 file IO 默认 share mode 不允许这种情况
- "确定吗"触发时, **重读自报 claim**, 然后真去验证每条, 不要只验证最明显的 1 条
