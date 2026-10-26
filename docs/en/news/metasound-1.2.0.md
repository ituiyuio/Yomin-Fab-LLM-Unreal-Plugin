---
layout: doc
title: LLMMetaSound v1.2.0 — Formalized DSL Contract + Headless Generation
date: 2026-10-26
tag: Release
summary: |
  LLMMetaSound v1.2.0 (v1.1.1 → v1.2.0) formalizes the `.llmmetasound` DSL contract: a top-level authoritative `AssetType` field, `ClassPath` disambiguation for overloaded operator nodes, pin-name edges (`FromPinName` / `ToPinName`) as the preferred stable dialect, and an `OutputFormat` channel layout (Mono / Stereo / Quad / 5.1 / 7.1) so a stereo graph on a mono source no longer silently drops a channel. A new headless console channel (`LLMMetaSound.Inspect` + `LLMMetaSound.Generate`) produces `.uasset` from DSL without a GUI editor, CI-ready. One-shot is now the safe default, ambiguous class resolution fails loud with candidates, three new example files ship, and UE 5.7 compatibility is restored (5.7 / 5.8 verified with clean `BuildPlugin -rocket` runs).
emoji: 🔊
slug: metasound-1-2-0
---

# LLMMetaSound v1.2.0

> Engine support: UE 5.7 / 5.8 — UE 5.5 / 5.6 remain unsupported (5.7+ MetaSound API surface, unchanged since v1.1.1).

## ✨ New Features

- **Formalized DSL contract** — the `.llmmetasound` dialect is now pinned down:
  - Top-level `AssetType` field (`"Source"` / `"Patch"`) is authoritative and takes precedence over `Metadata.NodeType`
  - `ClassPath` field (e.g. `UE.Multiply.Audio by Float`) disambiguates overloaded operator nodes; short-name fallback retained
  - Pin-name edges (`FromPinName` / `ToPinName`) resolved against the engine's live vertex list — stable across UE versions; legacy `FromVertexID` / `ToVertexID` still accepted but deprecated
  - `OutputFormat` channel layout — Mono / Stereo / Quad / 5.1 / 7.1; a stereo graph on a mono source no longer silently loses a channel
- **Headless generation channel** — two console commands make DSL → `.uasset` work without a live GUI editor:
  - `LLMMetaSound.Inspect <file>` — read-only graph check with an explicit `WIRING=UNWIRED` verdict (a "successfully generated" silent asset can no longer masquerade as an audible one)
  - `LLMMetaSound.Generate <file> <PackagePath> [overwrite] [oneshot]` — generate + save, CI-ready
- **3 new example files** — `InterfaceSynth`, `StereoWidePad`, `SubBassPatch` (9 examples total, all regenerated in the new dialect)

## 🐛 Bug Fixes

- **One-shot default** — a source that did not declare `UE.Source.OneShot` was judged `bLooping` by `USoundBase`, spawning an orphaned sound on every play; one-shot is now the default
- **Ambiguous class resolution fails loud** — an ambiguous `ClassName` match now errors with the candidate list instead of silently falling back
- **UE 5.7 compatibility restored** — shadowed local in the serializer (C4456, warnings-as-errors) and the 5.8-only `EGetObjectsFlags` parameter are now version-guarded (`UE_VERSION_OLDER_THAN`), so 5.7 and 5.8 compile from one source tree

## ⚡ Improvements

- Legacy dedicated panel retired — the unified Slate panel (Window → LLMMetaSound) covers generate, re-export, and logs
- Parser test suite (~430 lines) covering the new contract ships in the editor module
- Schema exporter emits `classPath` for every node, giving LLMs the exact disambiguation key

## 💥 Breaking Changes

- DSL dialect formalized: pin-name edges preferred, vertex-ID edges deprecated (still functional); top-level `AssetType` takes precedence over `Metadata.NodeType`
- The legacy dedicated panel class was removed (replaced by the unified panel)

---

**Engine support**: UE 5.7 (tested), UE 5.8 (tested) — separate zip + Project Version per UE, `BuildPlugin -rocket` clean runs (zero errors, zero consequential warnings).
**File format**: `.llmmetasound` (JSON), `.llmmetasoundschema` (Schema), `UMetaSoundSource` / `UMetaSoundPatch` (UAsset).
