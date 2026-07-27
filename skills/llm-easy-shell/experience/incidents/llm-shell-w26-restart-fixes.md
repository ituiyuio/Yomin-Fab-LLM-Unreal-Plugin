---
name: llm-shell-w26-restart-fixes
description: "llm-shell --restart 三个 bug 修复 (W26.1 output嵌套/W26.2 编译错吞/W26.3 5min game-thread wait), commit dc41ca8 + 693f260"
metadata: 
 node_type: memory
 type: project
 originSessionId: 98e4cd69-1f68-4f2e-a574-a89cb3b694ce
---

# llm-shell W26 (2026-06-04) — --restart 三个 bug 修复

## Bug 1 (W26.1): 启动后 output 字段嵌套 JSON 导致 LLM 端解析超时
- **症状**: `EmitRestartResult(true, "complete", "", waitResult.infoJson, ...)` 把 raw `{"success":true,"output":"<inner JSON>"}` 塞进 `"output"`, LLM 看到双重嵌套, 解析不出 editor state
- **修复** (commit dc41ca8): 新增 `ExtractInnerInfoJson()` helper, 提取 inner editor state JSON, 平铺到 `"output"` 字段. Fallback 留 raw response (defensive).

## Bug 2 (W26.2): 编译错被 `Out-Null` 吞掉
- **症状**: Build 命令以 `2>&1 | Out-Null` 收尾, build 失败时 LLM 只拿到 "Build failed with code 1", 必须手动去 `%LocalAppData%\UnrealBuildTool\Log.txt` 找 UBT 真实错
- **修复** (commit dc41ca8): 改用 `*> 'C:\Users\...\Temp\llm_shell_build_<pid>.log' 2>&1` 把 build stdout+stderr 全写到 temp 文件. 失败时 tail 最后 60 行 embed 到 `output.buildOutput` + `output.buildLogPath`. 成功时 best-effort 删 temp.

## Bug 3 (W26.3): 5min game-thread ready wait 永远 timeout
- **症状**: `WaitForEditorReady` 5min timeout + 1s loop + "info" command 要求 valid JSON. 但 editor 启动初期 LLMEasyShell 接受 TCP 时 game-thread 还没 ready, `SendCommand` 返回 capturedLogs (含 "Field usage was not found" 警告) 而非 valid info JSON. loop retry 5min 才 timeout. 实际 restart = 5min build + 5min wait = 10min.
- **修复** (commit 693f260): 改用 `WaitForPortToBeListening` (TCP listen 即可, 60s safety cap). 每个 tick 调 `DetectCrash` 短-circuit early crash. port up 后 best-effort info probe (1 try, 3s timeout) 抓 editor state. probe 失败时 `output` 留空, LLM 可立即 re-query.

## Why
用户原话: "每次都是到10分钟, 这肯定是不对的. restart理应在引擎启动之后收到消息并且立刻返回的."

## How to apply
- 启动: `--restart` 期望 5-10s 完成 (port listen) + 短 best-effort info probe
- Build 错: 现在会 inline 在 `output.buildOutput` (tail 60 行), 不需要查 UBT log
- output 字段: 平铺 editor state (project/level/pieState/livecoding), 不再嵌套
- 如果 editor 启动崩了 (如 missing DLL 0xc), 立即检测, 不会等 60s
- 三个 fix 都在 `.claude/skills/llm-easy-shell/llm-shell/main.cpp`, build 用 `compile.ps1` (CMake 也行)
