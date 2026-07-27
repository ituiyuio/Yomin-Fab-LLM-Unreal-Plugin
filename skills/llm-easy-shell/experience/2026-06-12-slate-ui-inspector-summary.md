---
name: 2026-06-12-slate-ui-inspector-summary
description: "LLMEasyShell ui 7 命令族 (dump/find/info/shot/press/type/tick) 4-PR 实施完成, 26 commits on master, DoD 6/7 met"
metadata:
 node_type: memory
 type: project
 originSessionId: 7b661671-8cab-45c8-a837-84138c692c7e
---

# 总览

LLMEasyShell `ui` 命令族 4-PR 实施 (2026-06-12) — 26 commits on master, 7 spec 命令全部 wired。

# 7 命令
- `ui dump` (PR1) — UMG tree JSON (Tree walker 走 UWidget → SWidget)
- `ui find` (PR2) — 按 text/class/path/visible-only/limit 找
- `ui info` (PR2) — 单节点 detail (UWebBrowser→cef_state)
- `ui shot` (PR2+PR4) — `--out` 整 VP / `--path` 单 widget (FWidgetRenderer)
- `ui press` (PR3) — mouse|key via FSlateApplication event injection
- `ui type` (PR3) — focus + 逐字符 key 注入
- `ui tick` (PR3) — polling until match or timeout

# 4 PR 文件
- `2026-06-12-slate-ui-inspector-pr1.md` — ui dump
- `2026-06-12-slate-ui-inspector-pr2.md` — ui find/info/shot
- `2026-06-12-slate-ui-inspector-pr3.md` — ui press/type/tick
- `2026-06-12-slate-ui-inspector-pr4.md` — ui shot --widget

# 3 真 bug 可观测性
- z-order bug: `ui find --class UWebShopWidget` + `ui find --class UWebBuildMenuWidget` 对比 (z-order 真实链 PR2.1)
- WebBrowser CEF: `ui info --path ...WebBrowser` 看 `cef_state.page_loaded` (proxy: !url.IsEmpty() || !title.IsEmpty())
- GameOver 风暴: `ui find --class UWebGameOverWidget` 期望 count=1

# 关键架构决策
- **UShellCommandBase + RegisterCommand** pattern (NOT IShellCommand + static-init, plan 在 PR1 这点写错)
- **MapUIToShellError** shared via UIErrorMapping.h (3rd-duplication rule of three)
- **FSlateApplication::Process*Event 5.7** 实际签名: FKeyEvent/FPointerEvent 构造器 (plan 写错)
- **SWidget::GetGeometry() 5.7 已删**: 用 GetCachedGeometry()
- **不引 IAutomationDriver / SlateAccessibility** (LLMEasyShellLite 不动)
- **editor-only** (WITH_LLMEASYSHELL 守护)

# Plan deviations (累计 18)
PR1: 5, PR2: 6, PR3: 5, PR4: 2 — 见各 PR memory + UI.aia "Plan deviations" 段

# 仍待 user 验证
- 完整 `Build.bat` link — 需关 editor, 跑 Build.bat
- 3 bug-regression scripts runtime — 需 PIE
- PIE end-to-end (dump→press→tick→dump) — 需 PIE

# 验收 (per spec §13)
6/7 met, 1 (PIE runtime) deferred
