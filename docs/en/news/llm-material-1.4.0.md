---
layout: doc
title: LLMMaterial v1.4.0 — Substrate Round Trip + Single Generation Path
date: 2026-10-26
tag: Release
summary: |
  LLMMaterial v1.4.0 (v1.1.2 → v1.2.0 → v1.3.0 → v1.4.0) makes Substrate materials fully round-trippable: `material export` rebuilds the `substrate` block topology (slabs, composition tree) instead of dumping flat nodes, so an exported file feeds straight back into `material generate`. The editor panel and the shell command now share one generation path, export and parse share one enum table (no more silent domain/blend downgrades), slab I/O is reflection-based (Hair / Unlit / Eye / SingleLayerWater slabs keep all inputs), a 12-file example set ships in `Config/Examples/`, and the Python `material` ability auto-registers when LLMEasyShell / LLMEasyShellLite is installed. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged — all four verified with clean `BuildPlugin -rocket` runs.
emoji: 🧱
slug: llm-material-1-4-0
---

# LLMMaterial v1.4.0

> Covers everything since v1.1.2: the single-generation-path + project-generic boundary (1.2.0), the GUI / tool-list reconciliation (1.3.0), and the Substrate round trip (1.4.0). `.llmmat` format unchanged. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 unchanged.

## ✨ New Features

- **Substrate round trip** — `material export` of a Substrate material now produces a re-importable `.llmmat`: slabs are grouped back into `substrate.slabs`, the composition tree into `substrate.root`, and substrate-owned expressions are removed from the flat node list so the two representations cannot collide.
- **Single generation path** — the editor panel and the `material generate` shell command share one implementation, so behavior and warnings no longer diverge between the two entry points.
- **Domain / Blend Mode override in the editor panel** — the GUI can now override the same fields the command's `--domain` / `--blend` flags do.
- **Bundled Python ability package** — with `LLMEasyShell` / `LLMEasyShellLite` installed, the full `material` command toolbox auto-registers from `<Plugin>/Content/Python/LLMMaterialAbilities/`; no manual ability setup. The GUI panel works fully without them.
- **12-file example set** in `Config/Examples/` — parameters, Fresnel, UV panning, texture channels, vertex colour, masked cut-outs, and both Substrate composition operators. Files named `Invalid*` are deliberately broken negative cases, not templates.

## 🐛 Bug Fixes

- **Pure-Substrate `.llmmat` (slabs, zero nodes) silently produced an empty material** while the panel logged success — the panel only checked the node count and ignored `Substrate.HasSlabs()`.
- **Export → generate round trip silently downgraded enums** — `RuntimeVirtualTexture` / `AlphaComposite` / `AlphaHoldout` exported fine but parsed back as `Surface` / `Opaque`. Export and parse now share one canonical enum table; an `LLMMaterial.Enums.RoundTrip` test pins every engine enum value.
- **`--domain DeferredDecal` / `LightFunction` / `Volume` silently produced a `Surface` material** — the builder's enum branch is now an exhaustive switch.
- **Non-`SubstrateSlabBSDF` slabs (Hair / Unlit / Eye / SingleLayerWater) had all inputs silently dropped** — the builder wired slab inputs through a hardcoded 17-pin chain that cast every branch to `SubstrateSlabBSDF`. Slab I/O is now by property name through reflection: every slab type and pin works, and a new pin needs no code change.
- **The editor panel never showed build warnings** (property not found, pin not connectable) — it now surfaces the same `[warnings]` section the shell reports, plus the non-round-trippable export warning.
- **`Export Schema` wrote into the plugin source tree** — a path that does not exist on a Fab install. It now calls the registry's own exporter and lands next to the command output (`Saved/LLMMaterial/MaterialExpressionSchema.llmschema`); panel and command exports land in the same `Saved/LLMMaterial/` directory.
- **A blanket "not round-trippable" export warning** — a substrate material that exported perfectly was still reported as unusable. The export now reports only what is actually lossy: a nested composition, a `Select` threshold other than 0.5, or a material with no `FrontMaterial`.
- **UE 5.8 compile adaptation** — deprecation warnings cleared across the engine matrix.

## 💥 Breaking Changes

- **None.** The `.llmmat` format is unchanged — substrate definitions look exactly like the ones shipped in `Config/Examples`. One behavioral note: a Substrate export now contains a `substrate` block where it previously contained flat nodes; tools that consumed the flat form should read the `substrate` block instead.

## ✅ Verified

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (zero errors, zero warnings each).
- 4 per-UE zips + SHA-256 in `manifest.json`, ready for the Fab Publisher Portal (one Project Version per UE).

## 🔧 Compatibility

- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64 / Mac / Linux declared, Win64 verified).
- `.llmmat` files written by 1.0 – 1.3.0 remain valid input.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — per-UE independent zip + Project Version.

**File format**: `.llmmat` (JSON), `.llmmatschema` (Schema), Material UAsset.
