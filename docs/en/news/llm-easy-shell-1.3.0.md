---
layout: doc
title: LLMEasyShell v1.3.0 — Trace Tab + ui press --root
date: 2026-10-27
tag: Plugin
summary: |
  Feature release: a live command-trace window in the editor — the
  "LLM Shell Trace" tab lists every shell command as it executes with a
  detail pane, filter box, failures-only toggle and auto-scroll; opens
  from the Play-toolbar port widget and auto-opens once per session
  (`LLMEasyShell.TraceAutoOpen 0` disables). Public C++ data plane:
  500-entry ring buffer (`GetRecentTraces()`) + `FOnShellCommandTraced`
  multicast. `ui press` gains `--root <UClass>` multi-root resolution
  with honest 0-hit diagnostics. UE 5.5 / 5.6 / 5.7 / 5.8 all build
  with zero errors and zero warnings via BuildPlugin -rocket.
emoji: 🐚
slug: llm-easy-shell-1.3.0
---

# LLMEasyShell v1.3.0

> 🚀 **Feature bump — watch the shell work.** A live trace window in the
> editor, a public C++ trace data plane, and `ui press --root` for
> multi-root widget resolution. Engine compatibility unchanged:
> 5.5 / 5.6 / 5.7 / 5.8.

## ✨ New Features

- **Trace Tab — a live command-trace window** — a new "LLM Shell Trace"
  nomad tab shows every shell command as it executes: a single-column
  live list with a detail pane (Input / Output / Error) for the selected
  row, plus a filter box, a failures-only toggle, auto-scroll, and
  Clear. Open it by clicking the port status widget on the Play toolbar
  (the old click-to-copy-port action moved to a *Copy port* button in
  the tab header), or let it open itself: once per editor session the
  tab auto-opens when the first traced command arrives. Set
  `LLMEasyShell.TraceAutoOpen 0` to disable auto-open; closing the tab
  manually keeps it closed for the rest of the session.
- **Public C++ trace data plane** — the subsystem now keeps an in-memory
  ring buffer of the last 500 traces (`GetRecentTraces()`; Input/Output
  truncated for display) and broadcasts `FOnShellCommandTraced` on the
  game thread after each command. The JSONL archive under
  `Saved/LLMEasyShell/traces/` remains the full-fidelity persistent
  record — the ring buffer is display-only.
- **`ui press --root <UClass>`** (`9a00f9a`) — resolve the widget path
  from a specified root widget class: short-name exact match,
  Blueprint-generated classes take the `_C` suffix — the same semantics
  as `ui dump --root`. Omitting `--root` keeps behavior byte-for-byte
  unchanged.

## 🐛 Bug Fixes

- **Honest 0-hit diagnostics for `ui press`** (`9a00f9a`) — when PIE is
  running but the `--root` class matches zero of N widgets, the error
  now reports `PIE running, 0 of N UUserWidget match root class` and
  suggests `ui find --all`, instead of the misleading "Start PIE first".
- **Trace Tab engine compatibility** (release engineering) — the Trace
  Tab was developed against UE 5.8 only; the first 4-engine `-rocket`
  validation caught two APIs that break on 5.5–5.7.
  `FCoreDelegates` post-engine-init is now version-gated
  (`GetOnPostEngineInit()` accessor on 5.8, direct delegate member on
  5.5–5.7) and the deprecated `SListView::ItemHeight` argument (no-op
  outside tile view) was removed. All four engines build with zero
  errors and zero warnings.

## 💥 Breaking Changes

- None.

## ⚙ Requirements (unchanged)

- Unreal Engine 5.5 / 5.6 / 5.7 / 5.8 (one Project Version per UE)
- 9 engine plugin dependencies (see `README.md`): `PythonScriptPlugin`,
  `GameplayAbilities`, `GameplayTagsEditor`, `EnhancedInput`, `PoseSearch`,
  `Chooser`, `StructUtils`, `Niagara`, `EditorScriptingUtilities`
- `WebBrowserWidget` enabled in host `.uproject` for CEF-state UI introspection
- `ModelContextProtocol` enabled in host `.uproject` on UE 5.8 (for the `mcp`
  command; auto-stubbed on 5.5–5.7)

---

*LLMEasyShell v1.3.0 — YominUnreal*
