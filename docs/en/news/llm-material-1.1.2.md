---
layout: doc
title: LLMMaterial v1.1.2 — Multi-UE 5.5/5.6/5.7/5.8 Build Regression Fix
date: 2026-07-02
tag: Fix
summary: |
  LLMMaterial v1.1.2 fixes a UE 5.8 build regression plus the Documentation.md / README.md "UE 5.7+" fossil. MaterialBuilder.cpp L432-466 accessed 21 deprecated `UMaterial::bUsedWithXxx` members that UE 5.8 flags as C4996; we wrap the access with `PRAGMA_DISABLE_DEPRECATION_WARNINGS` instead of switching to `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)` (private on UE 5.5/5.6/5.7, only public on UE 5.8). Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.
emoji: 🐛
slug: llm-material-1.1.2
---

# LLMMaterial v1.1.2

> Pure compat patch. No new features, no API changes. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.

## 🐛 Bug Fixes

- **`MaterialBuilder.cpp` UE 5.8 C4996 deprecation warnings** — L432 (`bUsedWithNanite`) + L444-466 (21 direct `bUsedWithXxx` member accesses) are all flagged by UE 5.8 as `warning C4996: ... Please update your code to the new API before upgrading to the next release`. The ideal replacement `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)` is `private` on UE 5.5/5.6/5.7 and only became public on UE 5.8, so it cannot be used directly. We wrap the 22 lines of direct access with `PRAGMA_DISABLE_DEPRECATION_WARNINGS` / `PRAGMA_ENABLE_DEPRECATION_WARNINGS`, mirroring the `[tool-fix-274]` `[tool-fix-260]` series handled in the same cycle 1:1.
- **`Documentation.md` / `README.md` claim drift** — both files claimed "UE 5.7+", but 1.1.1 already shipped multi-UE 5.5/5.6/5.7/5.8. Aligned to "5.5 / 5.6 / 5.7 / 5.8".
- **`.uplugin` / README / Documentation footnote `v1.1.1 → v1.1.2` synchronized**.

## ⚡ Improvements

- **`MaterialBuilder.cpp` comment explaining the UE 5.5/5.6/5.7 suppression rationale** — added a 4-line comment block above the PRAGMA block documenting the `SetUsageByFlag` private → public version boundary, so future contributors don't fall into the same trap.

## ✅ Verified

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (zero errors, zero C4996 deprecation warnings, zero C4701 uninitialized warnings).
- 4 zip SHA-256 written to `.publishready/zips/LLMMaterial/manifest.json`, ready to upload to Google Drive / Dropbox for the Fab Publisher Portal.

## 🔧 Compatibility

- Breaking change: none. Source and binary contracts identical to 1.1.1. `.llmmat` files written by 1.0 / 1.1.0 / 1.1.1 remain valid input.
- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64) — unchanged.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.

**File format**: `.llmmat` (JSON), `.llmschema` (Schema), Material UAsset.