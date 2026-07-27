---
name: llm-shell-w26-3-2-restart-timeout
description: "llm-shell --restart 五个隐性 bug 综合修复 (2026-06-04)：stdout 中文污染 + post-port-up crash miss + 短轮询 + 嵌套 JSON 失败"
metadata:
 node_type: memory
 type: project
 originSessionId: <current session>
---

# llm-shell W26.3.2 (2026-06-04) — --restart 综合修复

## 症状
用户报告: "llmshell的restart命令基本每次都会超时, 引擎已经启动了之后不会返回引擎状态去结束等待"

8 次连续跑 (28-88s 范围), 实际 7 次 EXIT 0 但 stdout 各种问题。

## 五个根因 + 修复 (全在 .claude/skills/llm-easy-shell/llm-shell/main.cpp)

### Bug 1 (W26.3.2a): taskkill 中文输出污染 stdout
- 位置: 旧 line 2659 `system("taskkill /PID X /F 2>&1")`
- 症状: editor 关不掉走 force kill 时, `taskkill` 本地化成功消息 (中文 "成功: 已终止 PID 为 70872 的进程") 打到 llm-shell stdout
- Run 2 实测 stdout 第一行: `�ɹ�: ����ֹ PID Ϊ 70872 �Ľ��̡�` 然后才是 JSON → LLM 解析失败
- 修复: `taskkill /F >NUL 2>&1`

### Bug 2 (W26.3.2b): inline port wait break 后不再 DetectCrash
- 位置: 旧 line 2830 (现 ~2848) `portUp = true; break;` 之后无 DetectCrash
- 症状: editor 启动期间 (EditorInit 末段) 崩了, port 已 bind 但 game-thread 没 up. inline 循环 break 时 DetectCrash 没机会跑
- 实测: 0xc access violation 崩在 CoreUObject/Engine, 跟 missing DLL 类似时序
- 修复: port up break 之后立即再调 DetectCrash, 崩了立即 return 带 crashLog

### Bug 3 (W26.3.2c): post-info-probe DetectCrash
- 位置: 旧 line 2866 (新位置) infoJson.empty() 时不检查 crash
- 症状: editor 在 post-port-up check 后才崩, info probe 自然拿不到 JSON
- 修复: infoJson empty 时再调一次 DetectCrash, 崩了 return crashLog

### Bug 4 (W26.3.2d): info probe single-shot 拿不到 JSON
- 位置: 旧 line 2852-2864 (现 ~2897-2926) 一次 SendCommand 就 return
- 症状: editor 启动后 game-thread 没 up serve commands, single-shot probe 3s timeout 后空
- W26.3.1 修复尝试用 "echo → reconnect" 模式但 server 端不 echo (LLMEasyShellTcpServer.cpp 310-380 不 echo), 修复方向错
- 修复: 短轮询 8 次 × 1.5s = 12s total, 第一次成功立即 break (大多 1-2 次成功)

### Bug 5 (W26.3.2e): ExtractInnerInfoJson 嵌套失败 (W26.1 旧 bug)
- 位置: 旧 line 2379-2431 ExtractInnerInfoJson
- 症状: search key `"output":"` 不匹配 pretty-printed JSON (`"output": "..."` 有空格), ExtractInnerInfoJson 返回 "", EmitRestartResult 走 fallback 嵌 raw response
- LLM 端拿到 3-level 嵌套: `j.output.output.output` (string) 才能拿到 state
- 修复: search `"output":`, 跳 whitespace, 期望 `"`, 然后 unwrap. 同时移除原 "key" (带多余 backslashes) 简化代码

## 修复后验证 (Run 7, Run 8)

stdout 1746-2237 bytes, flat editor state:
```json
{
 "success": true,
 "stage": "complete",
 "output": {
 "project": "CODEO",
 "engineVersion": "++UE5+Release-5.7-CL-51494982",
 "port": 15151,
 "pieState": "Stopped",
 "editorState": "Idle",
 "livecoding": { "compiling": false, ... }
 }
}
```

LLM 端 2-level: `j.output.project`, `j.output.pieState` 直接拿到.

- Run 7: 33.678s, exit 0
- Run 8: 30.706s, exit 0
- Run 1 (修复前): 27.985s 但 stdout `{"success":true,"stage":"complete"}` 无 output 字段
- Run 2 (修复前): 88.209s + stdout 中文污染

## Why
用户原话: "llmshell的restart命令基本每次都会超时"

实际测下来 llm-shell 本身没真"卡住" (大多 28-33s 跑完). 是 LLM 客户端**无法**解析不规范的 stdout 反复 retry → 用户看到超时. 修复 5 个根因后, LLM 端能 parse 出 flat editor state, 不再误判为超时.

## How to apply
- 改 ExecuteRestart / ExtractInnerInfoJson 必须保持 W26.3.2 修复
- inline 等待 loop 60s cap 不变 (W26.3 设计), info probe 12s 上限不变
- post-port-up + post-info-probe 二次 DetectCrash 是**关键**, editor 启动期 crash 必须立即报告
- ExtractInnerInfoJson 一定要支持 pretty-printed JSON (whitespace), 不能再 fallback 到 raw response
- taskkill / system() 命令末尾必须 `>NUL 2>&1` 不能用 `2>&1` (会污染 stdout)
