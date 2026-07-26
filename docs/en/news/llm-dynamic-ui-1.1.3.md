---
layout: doc
title: LLMDynamicUI v1.1.3 — Schema Alias + Easing Count Drift Closure
date: 2026-07-26
tag: Fix
summary: |
  LLMDynamicUI v1.1.3 closes four doc-fossil / schema-drift maintenance fixes accumulated since 1.1.2: WidgetTypeSchema.llmschema ↔ C++ LLMUnifiedTypeRegistry.cpp TypeMap alias sync (6 missing widgets), ELLMEasingType 15→34 count correction across 5 surfaces, broken `python ui easings` command reference removal, and `UE 5.7+` → `UE 5.8+` claim drift. No C++ / no API changes.
emoji: 🐛
slug: llm-dynamic-ui-1.1.3
---

# LLMDynamicUI v1.1.3

> Pure maintenance patch. No C++ / no API changes. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.

## 🐛 Bug Fixes

- **Widget alias schema drift closed** — `WidgetTypeSchema.llmschema` carried 3 alias entries while `LLMUnifiedTypeRegistry.cpp` TypeMap declared 10. Six widgets (CanvasPanel, CommonBorder, CommonButton, TextBlock, CommonText, CommonImage, EditableText, EditableTextBox, ComboBox) were missing from the schema-side aliases, plus SDF lives in `SDFSchema.llmschema`. After fix: 9 in-schema aliases + SDF in SDFSchema (9/9 mirror). `LLMUnifiedTypeRegistry_AutoDiscovery.cpp` `Meta.Aliases.Add()` now syncs every TypeMap entry. New `doc-audit` class `schema-aliases-vs-cpp-typemap` adds 6 single-target regex patterns to defend next schema-regen regressions.
- **Easing function count drift** — listing claimed "15" easings in 5 surfaces (`.uplugin` Description + `Documentation.md` ×2 + `README.md` + `VERSION-NOTES.md`). The `ELLMEasingType` enum has 34 entries (Linear + 3 generic EaseIn/EaseOut/EaseInOut + 10 family × In/Out/InOut variants: Quad/Cubic/Quart/Quint/Sine/Expo/Circ/Elastic/Back/Bounce). All surfaces updated. New `doc-audit` `count-easing-function` pattern defends the corrected count.
- **Broken `python ui easings` command reference** — `VERSION-NOTES.md` referenced a `ui easings` command that does not exist. The `ui` ability exposes only `generate` / `export` / `list-types` / `export-schema`. Reference removed.
- **`UE 5.7` claim drift** — `VERSION-NOTES.md` referenced "UE 5.7" while the `.uplugin` `EngineVersion` has been `5.8.0` and the actual Fab submission matrix is 5.5 / 5.6 / 5.7 / 5.8. Updated to "UE 5.8+".

## 🔧 Internal

- CRLF renormalization — 567 working-tree files normalized from CRLF → LF to match `.gitattributes` `text eol=lf` policy. Mechanical line-ending fix only.

## ✅ Verified

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (zero errors, zero C4996 deprecation warnings).

## 🔧 Compatibility

- Breaking change: none. Source and binary contracts identical to 1.1.2. `.llmui` files written by 1.0 / 1.1.0 / 1.1.1 / 1.1.2 remain valid input.
- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64) — unchanged.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.
**File formats**: `.llmui` (JSON), `.llmschema` (Schema), UMG Widget Blueprint (UAsset).