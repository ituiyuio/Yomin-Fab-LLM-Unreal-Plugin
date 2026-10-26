---
name: llmshell-livecoding-compile-method-2026-06-24
description: "编辑 C++ 时绝对不要调 Build.bat — 编辑器跑着就 'Unable to build while Live Coding is active',应走 'llm-shell livecoding' 触发 Live Coding 补丁或 'llm-shell --restart' 重启编译。LLM 在 ezue 自模式下必须用这个路径。路径: .claude/skills/llm-easy-shell/llm-shell/llm-shell.exe (commit 9bf1f35 期间踩坑, 2026-06-24)"
metadata:
 type: feedback
 originSessionId: 4b605858-4e93-4d28-8ef5-698345091dfc
---

# 编辑器跑着时的正确编译方法 (CareerStats v1.0 UI 期间踩坑, 2026-06-24)

## 痛点 (commit 9bf1f35 CareerStats v1.0 UI 期间)

写完 `WebCareerStatsWidget.h/.cpp` + `CareerStats.html` + `MainMenu.html` 改 + `SurvivorGameMode.h/.cpp` 改 + `LLMEasyShellGameplayLib.cpp` 改,直接跑:

```bash
cd "C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles"
./Build.bat CODEOEditor Win64 Development -Project="D:/UnrealEngine/CODEO/CODEO.uproject" -WaitMutex -FromMsBuild
```

返回:

```
Unable to build while Live Coding is active. Exit the editor and game, or press Ctrl+Alt+F11 if iterating on code in the editor or game
Result: Failed (OtherCompilationError)
```

试了 `-NoLiveCoding` / `-AllowLiveCoding` / `-SkipLiveCodingCheck` / `-Rebuild` **全部都失败**。原因:编辑器进程持有 `UnrealEditor-CODEO.dll` 文件锁,UBT 无法重写二进制,而且 Live Coding 模式下 `--Rebuild` 也会撞同一检查。

## 正确路径

**编辑器跑着的时候,必须用 `llm-shell` 而不是 `Build.bat`:**

```bash
# 改函数体 / UPROPERTY 增删 / 大多数情况
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -q -j -c "livecoding"

# 新增 C++ 类 / USTRUCT 改字段 / 继承层次变 / 不确定
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -q -j --restart
```

**绝对不要**:
- ❌ `Build.bat` (编辑器跑着必失败)
- ❌ `Build.bat -NoLiveCoding` (无效)
- ❌ `Build.bat -Rebuild` (撞 Live Coding 锁)
- ❌ 让用户"先关编辑器再编译" (ezue 自模式下用户不在线,得自己解决)

## livecoding vs restart 决策

| 场景 | 命令 | 说明 |
|------|------|------|
| 改函数体 | `livecoding` | 函数指令替换,不重实例化 |
| 改 UPROPERTY/UFUNCTION | `livecoding` | 多数情况可以 |
| **新增 C++ 类** | `restart` | LiveCoding 必失败,必须重启 |
| USTRUCT 加字段 | `restart` | 反射系统元数据变 |
| 继承层次变 | `restart` | 需要重新实例化对象 |
| 不确定 | `restart` | 安全选择 |

新增 .h/.cpp (本次 `WebCareerStatsWidget.h/.cpp` 就是) → 必须 `livecoding` 先试,**失败再 `--restart`**,不要用 `Build.bat`。

## How to apply

ezue 自模式下编译 C++ 标准流程:
1. 写完代码 `git commit` (代码不依赖 build pass)
2. `./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -q -j -c "info"` 查 `livecoding.compiling` + `pieState`
3. `compiling=false` 时:
 - 加新类 / USTRUCT 改字段 → `llm-shell --restart` (等 5-10min)
 - 改函数体 / 现有 UPROPERTY → `llm-shell livecoding` (等 30-90s)
4. 验证: `info` 查 `livecoding.compiling=false` + `livecoding.phase=idle`
5. 编译失败时**报告 build error 让用户决策**,不要自启 fallback 路径

## 实测成功样本 (2026-09-21, 掉落物面片 billboard 修复)

改 `Source/CODEO/Private/Survivor/Core/LootItem.cpp` 的函数体(`ALootItem::Tick` 内的
朝向公式)后走 livecoding:

```bash
# 安装位 .claude/skills/llm-easy-shell/llm-shell/llm-shell.exe（本仓 skills/llm-easy-shell/llm-shell/llm-shell.exe）
./llm-shell/llm-shell.exe -q -j -c "livecoding"  # 示例按 llm-shell/ 工作目录
```

返回 `"success": true, "errorCount": 0`,日志里能看到
`[1/7] Compile [x64] LootItem.cpp [NoUba]` → `Result: Succeeded`,总耗时 **24.22s**。
`requiresRestart: false` ⇒ **纯函数体改动确实不需要 `--restart`**,流程表是准的。

补充坑:`Build.bat` 失败时报的是
`Unable to build while Live Coding is active. Exit the editor and game...`
+ `Result: Failed (OtherCompilationError)`,
同时伴随 `SetFileInformationByHandle (FileDispositionInfo) failed on ... Trace.uba
(Access is denied.)` —— 看见 `Trace.uba Access is denied` 即可确认是"编辑器占锁",
不是代码问题,直接转 `livecoding` 通道。

## livecoding 失败的 Recommendation 修复 (2026-06-24 同一 session)

`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Reload.cpp` 3 个失败分支的 `Recommendation` 字符串之前是通用建议("Fix compilation errors before continuing" / "Wait for LiveCoding to finish, then check status"),对 LLM 没 actionable 指导,跟 [[llmshell-livecoding-error-hint-2026-06-23]] 类似的"LLM 看到不知道下一步"问题。

改成显式 `llm-shell --restart` 推荐:

| 失败分支 | line | 原 Recommendation | 新 Recommendation |
|----------|------|-------------------|-------------------|
| Timeout (编译卡住) | 642 | "Wait for LiveCoding to finish, then check status" | "Run 'llm-shell --restart' to do a full UBT rebuild (Live Coding hung)" |
| `bHasCompleted && !bSuccess` (编译失败) | 650 | "Fix compilation errors before continuing" | "Run 'llm-shell --restart' to do a full UBT rebuild (Live Coding can't recover from this failure)" |
| `bHasErrorsInLog` (日志检测错误) | 704 | "Fix compilation errors before continuing" | "Run 'llm-shell --restart' to do a full UBT rebuild (Live Coding can't recover from this failure)" |

3 个分支都已经 `bRequiresRestart = true`,所以 LLM 看到 `livecoding.requiresRestart=true + livecoding.recommendation="Run 'llm-shell --restart'..."` 直接知道下一步走 `--restart` 全量编译路径。

## 旧 memory 修正

[llmshell-livecoding-error-hint-2026-06-23] 之前是给 LLM 加 hint 字符串让它**别再**撞"Build.bat Live Coding is active"错误。本 memory 是**正向**的"用对方法"指南 — 两者互补,前者是被动防御(看到 Build.bat 错误知道下一步),后者是主动指南(直接用对命令)。本 session 第三次扩展:在 livecoding 自己的失败路径里加 `llm-shell --restart` 推荐,把"livecoding 失败 → --restart"链路打通。
