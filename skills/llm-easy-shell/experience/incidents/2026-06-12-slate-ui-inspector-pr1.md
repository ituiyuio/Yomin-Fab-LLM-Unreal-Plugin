---
name: 2026-06-12-slate-ui-inspector-pr1
description: "LLMEasyShell ui dump PR1 落地 — 14 commits (86ff2b9..94ca4f2), 不开新插件, 内置 ability 模式"
metadata: 
 node_type: memory
 type: project
 originSessionId: 7b661671-8cab-45c8-a837-84138c692c7e
---

# 落地

PR1 把 `ui dump` 命令族 (7 个中的第 1 个) 落地到 LLMEasyShell 主模块, 不开新插件。

# Why
- z-order / WebBrowser CEF / GameOver 风暴 3 个真 bug 共同缺可观测性
- 最小可用工具先出, 后 PR 增量加 find/info/press/type/shot/tick

# How to apply
- **命令注册 pattern 是 UObject-based**: `UShellCommandBase` 子类 + `NewObject<>` + `ULLMEasyShellSubsystem::RegisterBuiltInCommands` 注册 (不是 plan 写的 `IShellCommand` + static-init, plan 在这点是错的)
- **错误协议用 UIServiceErrors**: 13 个 `EUIErrorCode`, builder helper (`WithHint`/`WithCandidate`) 强制 spec §6 的 "always include hint or candidates" invariant, `ensureMsgf` 在 `ToJson` 强制检查
- **UWidget 路径寻址 3-mode**: Name/Index/Ordinal, L0 test 覆盖 5 个 case
- **Build 验证模式**: editor 运行时全 link 被 Live Coding 拦截, 实施时用 syntax-check + .obj 兜底; 全 link 留给 editor 关闭后跑

# Known limitations (PR1 末)
- `viewport_z_order` 永远 0 (TObjectIterator heuristic, 真实 ZOrder 链是 PR2)
- PIE smoke test COMPILED 但 NOT runtime-passed (user 需手动关 editor 跑 automation test)
- 5 个 plan deviation (C++17 cast / Name[N] expansion / EditorContext / IShellCommand→UShellCommandBase / build fallback) — 见 UI.aia 详情

# Verification (PR1 done)
- 14 commits on master, 7 new files + 2 modified
- L0 test (PathParser::Tokenize) 编译 + linked
- PIE smoke test 编译成功, runtime 需 user 验证
- 3 真 bug 可观测性: PR1 给 z-order bug 提供 `ui dump --filter Shop` 输出, GameOver 风暴给 `ui find --class UWebGameOverWidget` (PR2), WebBrowser 黑屏给 `ui info --path ...WebBrowser` (PR2)
