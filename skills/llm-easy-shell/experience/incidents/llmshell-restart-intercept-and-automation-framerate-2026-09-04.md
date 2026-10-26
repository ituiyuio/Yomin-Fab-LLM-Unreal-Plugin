---
name: llmshell-restart-intercept-and-automation-framerate
description: "llm-shell 两坑：--restart 拦截路径与编辑器内 automation 的 FWaitForInteractiveFrameRate 节流（失焦 ~3 FPS 导致 latent command 不跑）"
metadata:
  node_type: memory
  type: feedback
---

# llm-shell 两个坑 (2026-09-04)

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


## 1. `-c "restart"` 空转陷阱 → 已修(客户端拦截)

**现象** (两种失败签名, 只有第一种归因于缺 handler):
① 编辑器在线: `-c "restart"` 被派到插件, 插件无 `restart` command handler → 回
   `Unknown command: restart`,`restart` 只是 SKILL.md 里的概念名;真正的重启工作流只在
   客户端 `--restart` 旗标里(main.cpp `ExecuteRestart`)。
② 编辑器离线/已被关: connection failure — 此时任何服务端 handler 都无济于事, 只有客户端
   侧工作流能救。两种情况共同点: 都不会重建/重启。

**修复** (2026-09-04, main.cpp main() Execute 段): **单命令模式** (`-c`,含 JoinArgsToCommand
的位置参数形式) 下 bare `restart` 命令(trim + case-insensitive)在客户端拦截,直接转
`ExecuteRestart`,与 `--restart` 等价。范围注记: REPL/管道模式的裸 `restart` 不在拦截范围
(仍会收到 Unknown command)。重编:`llm-shell/compile.ps1`。

**教训**: SKILL.md 命令表里的名字 ≠ 插件侧一定有 handler;旗标类工作流(--restart)只能走客户端。排查先分辨「连接失败」与「Unknown command」两种签名, 归因才不会错。

## 2. 编辑器内 `Automation RunTests` 卡在 FWaitForInteractiveFrameRate

**现象**: `execute_console_command('Automation RunTests X')` 日志显示 `Queued` 后 90s+ 无结果,
日志报 `FWaitForInteractiveFrameRate: Waited N seconds. Current FPS=3`。

**根因**: 编辑器窗口失焦/后台时 Slate 节流(editor preference "Use Less CPU when in Background")
到 ~3 FPS;automation  latent command 要求 ≥10 FPS 持续 5s 才开跑,570s 超时才放行。

**解法**: 跑测试前把编辑器窗口 Activate 到前台(Win32 SetForegroundWindow 即可),
或 `t.IdleWhenNotForeground 0`(对部分节流路径有效,对 Slate 后台节流不一定)。
前台后 FPS 回升 37+,queued 测试立即开跑。

**验证口径**: 结果看 `Saved/Logs/CODEO.log` 的 `LogAutomationController: Display: Test Completed.
Result={Success} Name={...} Path={...}` 行 — 不要用 `run_automation` ability(尾巴带 `; Quit`
会杀编辑器,CI 专用);用 `python pyexec` + `execute_console_command` 不带 Quit,编辑器保持在线。
