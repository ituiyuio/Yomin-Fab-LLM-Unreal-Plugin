---
layout: doc
title: LLMMetaSound v1.1.1 — UE 5.8 + Fab 4.x Compliance
date: 2026-07-01
tag: Plugin
summary: |
  LLMMetaSound v1.1.1 ships UE 5.7 / 5.8 zips. Six C4996 deprecation warnings suppressed (PRAGMA wrappers), FabURL realigned to launcher protocol, UE 5.5 / 5.6 dropped due to MetaSound API surface changes.
emoji: 🔊
slug: metasound-1.1.1
---

# LLMMetaSound v1.1.1

> UE 5.7 / 5.8 only. UE 5.5 / 5.6 dropped — MetaSound API surface changed too much for a backward-compatible stub.

## ✨ New Features

- **JSON → UMetaSoundSource / UMetaSoundPatch** generator — describe a MetaSound graph in JSON, plugin constructs the asset end-to-end
- **Bidirectional roundtrip** — UMetaSound ↔ `.llmmetasound` JSON
- **Type-safe edge validation** — mismatched vertex types are rejected before the asset is saved
- **Auto-connect for `OnPlay` + final audio output** — common plumbing is wired automatically
- **Slate editor panel** — Window → LLMMetaSound
- **Schema export (`.llmmetasoundschema`)** — exposes all 401 registered MetaSound node classes for LLM context
- **Overloaded-operation disambiguation** — `ClassPath` field picks the right `UE.Multiply.Audio by Float` variant
- **Pin-name-first edge resolution** — `FromPinName` / `ToPinName` resolved against the engine's live vertex list (stable across UE versions); legacy `FromVertexID` / `ToVertexID` still works as fallback

## 🐛 Bug Fixes

- **6 × C4996 `IterateRegistry` deprecation warnings** on UE 5.8 — wrapped each call in `PRAGMA_DISABLE_DEPRECATION_WARNINGS` / `PRAGMA_ENABLE_DEPRECATION_WARNINGS` (Fab treats C4996 as error)
- **`FabURL` was `https://www.fab.com/listings/PLACEHOLDER`** — replaced with launcher protocol `com.epicgames.launcher://ue/Fab/product/PLACEHOLDER` (Fab 4.x compliance)
- **`EngineVersion` field** updated to `5.8.0` to match `.uplugin`
- **Plguagin → Plugin repo URL fossil** in 13 doc surfaces (tool-fix-128)

## ⚡ Improvements

- **Generator hardened** for LLM-friendly DSL conventions (robust to whitespace, case, partial-name matches)
- **No `EditObject` call** — avoids the `SynchronizePinLiteral` hard assertion during asset save
- **Tutorials button** added + `LOCTEXT` redefinition resolved
- **README / Documentation rewrites** — Fab marketplace-style (Agent Online brand, Overview / Problem / Solution / How to Use structure); `DocsURL` typo corrected

## 💥 Breaking Changes

- **UE 5.5 and 5.6 are no longer supported** — plugin uses 5.7+ MetaSound API surface (`EMetasoundFrontendClassAccessFlags`, `FMetasoundFrontendGraphClass::GetDefaultInterface`, `MetasoundFrontendNodeClassRegistry.h`, `FMetaSoundAssetCookOptions`)

## 🔧 Internal Refactors

- **Editor module dependency split** — `LLMEasyShell` / `LLMEasyShellLite` are compile-time soft dependencies via `CheckModuleExists` + `WITH_LLMEASYSHELL={0,1}` (no `.uplugin` requirement, host project stays bootable without them)

---

**Engine support**: UE 5.7 (tested), UE 5.8 (tested) — `EngineVersion: "5.8.0"` in `.uplugin`, separate zip + Project Version per UE.
**File format**: `.llmmetasound` (JSON), `.llmmetasoundschema` (Schema), `UMetaSoundSource` / `UMetaSoundPatch` (UAsset).
