---
name: 2026-06-12-slate-ui-inspector-pr2
description: "LLMEasyShell ui find/info/shot PR2 落地 (7 commits on top of PR1), 3 bug-regression scripts ready (待 editor restart 后实跑)"
metadata: 
 node_type: memory
 type: project
 originSessionId: 7b661671-8cab-45c8-a837-84138c692c7e
---

# 落地

PR2 在 PR1 `ui dump` 基础上加 3 个命令:
- `ui find` (按 text/class/path/visible-only/limit 找)
- `ui info` (单节点 detail, 包含 UWebBrowser→cef_state 字段)
- `ui shot --out` (整 VP 截图, 走 ULLMEasyShellEditorLib::CaptureActiveViewport)

+ 3 bug-regression scripts (`Tests/Scripts/test_*_regression.py`) — definition of done 待 editor restart 实跑。

# Why
- 3 真 bug (z-order / WebBrowser CEF / GameOver 风暴) 都需要 query + drill-down 能力
- `ui dump` 给全局视图, `ui find/info` 给局部, `ui shot` 给视觉证据

# How to apply
- **`ui info` 对 UWebBrowser 暴露 cef_state 字段**: url, title, page_loaded (proxy: !url.IsEmpty() || !title.IsEmpty()). 5.7 UWebBrowser 没有 LoadState UPROPERTY, 要更深的状态需要 wrapper / friend.
- **实际 API**: `ULLMEasyShellEditorLib::CaptureActiveViewport(OutFile, Width, Height, bUsePIE, bAsync, bShowUI)` (NOT `TakeScreenshot`)。plan 在这点写错。
- **错误码映射**: 走 `UIErrorMapping.h` 的 `MapUIToShellError`, 3rd-duplication rule-of-three 后从 per-file namespace 提取为 shared header.
- **3 脚本 runtime 验证需 editor restart**: 当前 editor + Live Coding 锁住, 编译链接都没真正跑过; 3 脚本 .py 语法 OK, 但实际调 ui find/info 时会返 "Unknown command" 除非 editor 重启拉新 C++.

# Known limitations (PR2 末)
- `viewport_z_order` 字段在 PR1+PR2 永远 0 (TObjectIterator heuristic, 真实 ZOrder 链是 PR2.1)
- 3 脚本编译/link/runtime 全验证 都没跑 (env 阻塞, 用户需手动关 editor 跑 build + automation test)
- `ui shot` MVP only (--out); --path/--widget 留 PR4 (FWidgetRenderer)
- 6 个 plan deviation: UIShot API 4 个 + helper-promotion timing + .gitignore !Tests/

# Verification (PR2 done)
- 22 commits on master (PR1 15 + PR2 7)
- 4 shell 命令 (ui dump / find / info / shot) wired + registered
- UIServiceErrors + UIErrorMapping 协议完整
- 3 bug-regression scripts 准备就绪 (待 PIE 实跑)
- spec §6 invariant (always include hint or candidates) 走 `ensureMsgf` 强制
- L0 test (PathParser::Tokenize) 编译 + linked (PR1)
- PIE smoke test 编译成功 (PR1, runtime 待 user 验证)
