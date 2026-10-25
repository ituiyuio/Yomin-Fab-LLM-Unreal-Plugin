---
layout: doc
title: LLMDynamicUI v1.1.4 — Editor Parent Class Picker + Standalone Build Fix
date: 2026-10-26
tag: Feature
summary: |
  LLMDynamicUI v1.1.4 adds a UMG parent-class picker to the editor panel (enumerates loaded UUserWidget subclasses, including your project's widget bases and the CommonUI bases) and really implements the previously advertised-but-ignored `ui generate --common-ui` / `--layer` and `ui list-types --category` flags. It also fixes a batch of claim drift: the ability tool list de-duplicated, its version field re-attached to the real plugin version, ghost types removed from the catalog. One fix is key for Fab users: the editor module's hard compile-time dependency on LLMEasyShell is now a conditional soft dependency — marketplace installs (no shell) compile and link cleanly, with notifications falling back to the engine notification manager. The `.llmui` format is unchanged.
emoji: ✨
slug: llm-dynamic-ui-1.1.4
---

# LLMDynamicUI v1.1.4

> Mixed feature + fix patch. The `.llmui` format is unchanged. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.

## ✨ New Features

- **Parent Class picker in the editor panel** — the panel enumerates the `UUserWidget` subclasses currently loaded (your project's own widget base classes and the CommonUI base classes among them) and lets you pick the UMG parent for the widget being generated. The choice is written to the root-level `parentClass` field of the generated `.llmui`.
- **Generic `parentClass` resolution** — `/Script/<Module>.<Class>` native classes from any module and simple class names resolved through a runtime registry (`ULLMParentClassRegistry`); no more hardcoded host-module paths. Native resolution uses a zero-IO `FindObject` hit instead of a failing asset-load round trip per generation.
- **`ui generate --common-ui` / `--layer <Menu|Game|Popup>` really implemented** — previously advertised by the usage text but silently ignored; `--common-ui` now explicitly asks for a CommonUI base class and `--layer` implies it and selects the layer. Unknown categories return a clear error instead of silently listing everything.
- **`ui list-types --category <X>` filtering really implemented** — same treatment; the advertised flag and the implementation now agree.

## 🐛 Bug Fixes

- **Marketplace-install path bug** — Export Schema used to write into a hardcoded `Plugins/LLMDynamicUI/Config` inside the user's project (the path does not exist for plugins installed under `Engine/Plugins/Marketplace/`, so a stray directory tree appeared). It now resolves the real plugin root via the plugin manager with an `EnginePluginsDir` fallback.
- **`.llmui` export directory is configurable** — new `ExportedLLMDefsPath` setting (default `/Game/UI/LLMDefs/`) replaces the hardcoded `Content/LLMDefs/UI`.
- **Type catalog de-ghosted** — removed advertised-but-nonexistent types (ListView / TreeView / LLMDynamicUIBase), added RetainerBox / InvalidationBox (24 types + CommonUI aliases + SDFBox), easing count aligned to 34.
- **`ui` ability tool list de-duplicated** — the list was registered twice, verbatim, with LLMEasyShell and LLMEasyShellLite; it is now a single source. Its `version` field follows `FLLMVersionInfo::PluginVersion` instead of a hardcoded `"1.0"`.
- **Non-functional SDF box shells removed from the UMG palette** — the widget pair referenced a material asset that never existed; agents and users can no longer pick an empty shell.
- **The editor module did not compile without the LLMEasyShell host plugin** — the editor-notification helper was a hard compile-time dependency, which marketplace installs do not have. It is now a conditional soft dependency: with the shell present, notifications route to its unified helper; without it, the module compiles and links cleanly and notifications fall back to the engine notification manager (`FSlateNotificationManager`). **For Fab users: the plugin is now fully standalone.**

## 🔧 Compatibility

- Breaking change: none. The `.llmui` format is unchanged, and existing `parentClass` values keep working.
- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64) — unchanged.

## ✅ Verification

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (**zero errors / zero warnings**).
- In-project incremental build (LLMEasyShell present) passes; `LLMDynamicUIEditor` DLL links cleanly.
- 4 zip SHA-256 hashes recorded in `.publishready/zips/LLMDynamicUI/manifest.json`.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.
**File formats**: `.llmui` (JSON), `.llmschema` (Schema), UMG Widget Blueprint (UAsset).
