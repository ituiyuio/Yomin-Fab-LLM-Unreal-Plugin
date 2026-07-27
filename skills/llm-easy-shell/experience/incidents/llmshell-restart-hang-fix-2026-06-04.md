---
name: llmshell-restart-hang-fix-2026-06-04
description: llm-shell --restart 卡死 / LLM 拿不到反馈 的 6 个根因 + 单 JSON 契约修复方案 (2026-06-04)
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 58b0ac5b-4431-44e1-b004-7f4a9d15ab67
---

# llm-shell --restart 在引擎崩溃场景下卡死 / LLM 拿不到反馈

**Why**:
用户报告:`llmshell 的 restart 命令在引擎崩溃的情况下好像是会被卡出,导致返回不了 restart 信息,llm 拿不到`

排查时发现 6 个根因叠加导致 LLM 在 stdout 看不到干净的 JSON,反而被进度消息 / 中间响应 / 5 分钟沉默轮询 淹没。

**根因清单** (位置都在 `.claude/skills/llm-easy-shell/llm-shell/main.cpp`):

1. `ExecuteRestart` 入口**没有**调 `DetectCrash` (单命令/REPL 模式都有)
 - 编辑器已崩的场景下,LLM 拿不到 "上次崩了" 信息
2. `WaitForEditorReady` 5 分钟轮询循环**没有** `DetectCrash` 检查
 - 新编辑器在 startup 期间崩了,循环傻等 5 分钟
3. 所有 `printf("[llm-shell]...")` 进度消息用 stdout,污染 LLM JSON 解析
4. `printf("%s\n", response)` 直接把中间 `info`/`stop` socket 响应打到 stdout
5. UBT build 输出 (powershell `& build.bat`) 泄露到 stdout (`Using bundled DotNet...`)
6. `ExecuteRestart` 所有失败路径 (build fail / 5min timeout / 项目不匹配) `return 1` **不打 JSON**

**How to apply** (实施过的修复,以后改这块代码要保持):

- 加了 `EmitRestartResult(success, stage, error, output, crashLog, priorCrashLog)` 辅助函数,统一 stdout 单 JSON 输出
- 加了 `WaitForEditorResult {ready, crashed, timedOut, infoJson, crashLog}` struct,`WaitForEditorReady` 循环里每轮调 `DetectCrash`
- 入口加 `DetectCrash` 预检,**同时**捕获 Case 1 (lastPid!=0 && curPid==0) 和 Case 2 (lastPid!=0 && curPid!=0 && diff) — Case 2 `DetectCrash` 返回 false 但仍加载 crashLog,需要单独判断 `crashLog != nullptr`
- 所有 `printf("[llm-shell]...")` 改 `fprintf(stderr, ...)`
- 中间 `printf("%s\n", response)` 改 `fprintf(stderr, ...)`
- UBT build 命令末尾加 `2>&1 | Out-Null` 抑制输出 (UBT log 在 `%LocalAppData%\UnrealBuildTool\Log.txt` 保留可查)
- `AllocatePortForInstance` 里 `printf("...Allocated port...")` 也改 stderr

**新 JSON 契约** (LLM 解析的格式):

```json
// 成功
{"success":true,"stage":"complete","output":{...editor info...},"priorCrashLog":"..."}

// 失败 — 各种 stage
{"success":false,"stage":"init","error":"...","priorCrashLog":"..."}
{"success":false,"stage":"verify","error":"...","priorCrashLog":"..."}
{"success":false,"stage":"build","error":"...","priorCrashLog":"..."}
{"success":false,"stage":"start","error":"Editor crashed during startup","crashed":true,"crashLog":"...","priorCrashLog":"..."}
{"success":false,"stage":"start","error":"Editor did not respond within 5 minutes after start","priorCrashLog":"..."}
```

**Verify**:
- 真实测试场景: 编辑器崩了后跑 `--restart` → stdout 1 个 JSON,7 秒内 bail out (不是 5 分钟),含 priorCrashLog + 新 crashLog
- 编辑器在线 + fake prior crash (Case 2) → success JSON 含 priorCrashLog
- 编辑器在线 + 干净状态 → success JSON 无 crash 字段

**相关 commit 模式**:
之前 `4e8fd52 fix(llm-shell): resolve restart hang by using info command probe` 只修了一半 (TCP 监听 vs game thread 准备),崩溃场景下的 5 分钟静默轮询没修。本次补全。
