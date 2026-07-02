---
layout: doc
title: LLMStateTree v1.1.2 — UE 5.5/5.6/5.7/5.8 C4996 Fix
date: 2026-07-02
tag: Plugin
summary: |
  LLMStateTree v1.1.2 patch release. Fixes two C4996 deprecation warnings on UE 5.8 build (Fab marketplace scanner treats C4996 as an error), routed through a multi-UE compat shim bridging old and new APIs. Also corrects the "UE 5.7+" doc-fossil in README / Documentation.md / VERSION-NOTES.md.
emoji: 🌲
slug: llm-statetree-1.1.2
---

# LLMStateTree v1.1.2

> Patch bump. Zero user-facing API changes — only fixes UE 5.8 compile warnings + doc fossil.

## 🐛 Bug Fixes

- **2 × C4996 deprecation warnings on UE 5.8** —
  `UE::StateTree::Delegates::OnRequestCompile` is marked deprecated on UE 5.8,
  triggering a C4996 warning that Fab marketplace scanner treats as an error.
  The `statetree compile` command now goes through `LLMStateTreeCompat::RecompileStateTree`:
  - UE 5.5-5.7: uses the old delegate (non-deprecated)
  - UE 5.8+: uses `UStateTreeEditingSubsystem::CompileStateTree` (canonical API)
- **doc-fossil "UE 5.7+"** corrected to "UE 5.5+ (5.5/5.6/5.7/5.8 multi-UE build)",
  touching `README.md` / `Documentation.md` / `VERSION-NOTES.md`

## ⚡ Improvements

- `LLMStateTreeCompatShim.h` adds a `LLMSTATETREE_UE_5_8_PLUS` compile-time detection macro
  and a `RecompileStateTree(UStateTree*)` bridge function; call sites no longer
  scatter `#ifdef` blocks.

## 💥 Breaking Changes

- None

## 🔧 Internal Refactors

- Multi-UE compat shim gains a 4th bridge (compile API), matching the style of the
  existing 3 bridges (`MakeBinding` / `AddBindingToEditor` / `GetRootParametersBag` /
  `AddPropertyToBag`).

---

**Engine support**: UE 5.5 (tested), UE 5.6 (tested), UE 5.7 (tested), UE 5.8 (tested)
— `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.

**File format**: `.llmstate` (JSON), `.llmstateschema` (Schema), `UStateTree` (UAsset).

**Source**: 4 files changed — `LLMStateTreeCompatShim.h` (+50/-0 net),
`LLMStateTreeCommandHandler.cpp` (+12/-6 net),
`Documentation.md` (+3/-3 net), `README.md` (+1/-1 net),
`VERSION-NOTES.md` (+1/-1 net).