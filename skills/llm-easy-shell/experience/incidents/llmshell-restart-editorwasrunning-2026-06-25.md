---
name: llmshell-restart-editorwasrunning-2026-06-25
description: "2026-06-25 llm-shell --restart JSON 修 (commit d679d4a): 当 editor 未运行时,save/shutdown 静默跳过,只在 stderr 打印,JSON 结果看不出区别. 1 tracking bool + 1 optional param + 1 JSON field (editorWasRunning:true|false). LLM 拿 JSON 不再误判 save 状态."
metadata: 
 node_type: memory
 type: reference
 originSessionId: 1fe8999f-79f8-499e-a7a8-e31a7a2c9cd0
---

llm-shell --restart 在 editor 未运行时,sock == INVALID_SOCKET → 进入 `else { fprintf(stderr, "Editor not running. Skipping save/shutdown steps.\n"); }` 静默跳过,然后继续 build+launch. 最终 EmitRestartResult(true, "complete", ...) 跟 editor 跑着的成功 restart 看起来一模一样 — JSON 结果只暴露 success/stage/error,没暴露 editor 状态. LLM (or user) 拿到 JSON 没法区分 "editor 跑着 + save + 关闭 + rebuild + relaunch" vs "editor 没跑 + 直接 build + launch". 误判 LLM 可能假设 save 发生过.

**修法** (commit d679d4a, +26 / -8):
1. `EmitRestartResult` 加 optional param `bool editorWasRunning = false` (默认 false 不破坏现有调用)
2. `ExecuteRestart` 加 `bool editorWasRunning = false` 跟踪,当 `sock != INVALID_SOCKET` 时设 true
3. 7 处 EmitRestartResult 调用全加 `, editorWasRunning` 参数 (replace_all 一次完成)
4. JSON emit 加 `\"editorWasRunning\":` + true/false

**文件**: `.claude/skills/llm-easy-shell/llm-shell/main.cpp:3139-3190` (EmitRestartResult) + `:3194` (tracking var) + `:3268` (set true at sock connect) + 7 处 call sites.

**build**: `powershell -ExecutionPolicy Bypass -File _compile.ps1` (vcvars64.bat → MSVC cl.exe /std:c++20 → 警告 0 错误 → 516KB exe). 编辑后记得 `dos2unix` 转回 LF 不然 diff 噪声 4193 行 (Windows 编辑器加 CRLF).

**验证**: `./llm-shell.exe --help` 跑通 (binary functional). 没跑真实 --restart 因为需要 editor + 5-10 分钟.

**Why**: LLM 自动化读取 JSON result 需要这字段决定下一步 (retry save logic? just proceed?). 之前 LLM 拿到 stage:complete 可能误以为 save 发生了.

**How to apply**: 后续 LLM 在处理 `--restart` JSON 时,看 `editorWasRunning:false` 应当知道 save/shutdown 被 skip,不要假设 save 状态.

跟 [[webui-calljs-apply-discards-object-arg-2026-06-25]] + [[webui-calljs-paren-syntax-2026-06-25]] 模式一致 — 根因修 (JSON contract 缺关键状态字段) > 调用方散改适配.