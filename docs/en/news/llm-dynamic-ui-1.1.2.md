---
layout: doc
title: LLMDynamicUI v1.1.2 — Multi-UE 5.5/5.6/5.7 Build Regression Fix
date: 2026-07-02
tag: Fix
summary: |
  LLMDynamicUI v1.1.2 closes a multi-UE build regression. LLMUMGGenerator.cpp used EGetObjectsFlags::None (UE 5.8-only enum) without version guards, breaking 5.5/5.6/5.7 builds with C2653. Wrapped with ENGINE_MAJOR_VERSION/MINOR_VERSION guards falling back to bool=true on older engines. Also closes Documentation.md / README.md 'UE 5.7+' claim drift to match the 1.1.1 multi-UE matrix.
emoji: 🐛
slug: llm-dynamic-ui-1.1.2
---

# LLMDynamicUI v1.1.2

> Pure compat patch. No new features, no API changes. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.

## 🐛 Bug Fixes

- **`ForEachObjectWithOuter` enum-flag guard for UE 5.5/5.6/5.7** — `LLMUMGGenerator.cpp` `BackupClassPropertyReferences` used `EGetObjectsFlags::None`, an enum introduced in UE 5.8 only. All 5.5/5.6/5.7 builds failed with `error C2653: 'EGetObjectsFlags': is not a class or namespace name`. Wrapped with `ENGINE_MAJOR_VERSION/MINOR_VERSION` guards falling back to `bool bIncludeNestedObjects=true` on older engines. Mirrors the existing `UPackage::GetMetaData()` guard pattern at L278.
- **`Documentation.md` / `README.md` claim drift** — both files claimed "UE 5.7+" but 1.1.1 already shipped multi-UE 5.5/5.6/5.7/5.8. Aligned to "5.5 / 5.6 / 5.7 / 5.8+".

## ✅ Verified

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (zero errors, zero C4996 deprecation warnings, zero C4701 uninitialized warnings).

## 🔧 Compatibility

- Breaking change: none. Source and binary contracts identical to 1.1.1. `.llmui` files written by 1.1.0 / 1.1.1 remain valid input.
- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64) — unchanged.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.
**File formats**: `.llmui` (JSON), `.llmschema` (Schema), UMG Widget Blueprint (UAsset).