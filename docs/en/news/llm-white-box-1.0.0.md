---
layout: doc
title: LLMWhiteBox v1.0.0 — BSP whiteboxing for LLM agents, with a castle-in-a-valley sample
date: 2026-11-11
tag: Plugin
summary: |
  First public release of LLM White Box: 15 JSON-returning commands that build
  real BSP geometry (boxes, subtractive cuts, cylinders, spheres, cones, stairs,
  one-shot rooms, one-shot wall segments) directly in the persistent level,
  plus named-group material filtering, BSP recompile, and a deterministic
  `python castle build` generator that rebuilds a 1040-brush valley-and-castle
  blockout in one editor call. UE 5.5 / 5.6 / 5.7 / 5.8 all compile clean via
  BuildPlugin -rocket.
emoji: 🧱
slug: llm-white-box-1.0.0
---

# LLMWhiteBox v1.0.0

> 🧱 **First release.** Level whiteboxing as a command surface: an agent lays out
> a room, punches a doorway, drops a material on the whole `Masonry_*` group and
> recompiles the BSP — and gets JSON back every time. Ships with a reproducible
> castle-in-a-valley sample level. Engine compatibility: 5.5 / 5.6 / 5.7 / 5.8.

## ✨ New Features

- **15 JSON-returning commands for BSP brush creation** — `create-box`,
  `create-subtract-box`, `create-cylinder`, `create-sphere`, `create-cone`,
  `create-stairs`, plus `build-room` (4 walls + floor + ceiling in one call) and
  `build-wall-segment` (a wall along any line, correctly rotated).
- **Query / transform / delete** — `list-brushes`, `get-brush`, `move-rotate`,
  `delete-brush`.
- **Render pipeline** — `apply-default-material` (named-group filtering — one
  call re-materializes a whole category), `rebuild-bsp-lighting`, and the
  stronger `build-bsp`.
- **Sample level generator `python castle build`** — rebuilds a complete valley
  + medieval castle blockout (1040 BSP brushes, 19 material groups, procedural
  sky dome, 24 far mountains, 7 camera presets) from source, deterministically,
  in one editor call.
- **Machine-readable brush/builder contract**:
  `Config/Schemas/BrushSchema.llmwhiteboxschema`.

## 🐛 Fixes landed before release

- **Brushes were created with a NULL per-poly material and rendered as
  wireframe only.** Material is now written after the builder runs, so a new
  brush is visible immediately.
- **`apply-default-material` matched a hard-coded name prefix**, so on any
  other level it touched zero brushes yet reported success.
- **`build-wall-segment` computed a rotation and discarded it** — every
  diagonal wall came out axis-aligned.
- **`create-stairs` stacked boxes in Z** and produced a tower instead of a
  flight of steps.
- **Volume brushes** (`NavMeshBoundsVolume`, `DefaultPhysicsVolume`,
  `PostProcessVolume`) were reported as whitebox geometry and could be deleted.
  They are now excluded from queries and refused by destructive commands.
- **A brush-name collision could take the editor down**; collisions are now
  detected the way the engine detects them and reported as a normal error.

## ⚡ Improvements

- **Zero compile-time coupling** — the plugin registers into LLMEasyShell /
  LLMEasyShell Lite at runtime by reflection. The host needs one of the shell
  plugins for the command surface; the C++ API stays usable without them.
- **`delete-brush` requires `--confirm=true`.**
- **Editor-only modules** (`UnrealEd`, `EditorScriptingUtilities`) are gated
  behind `Target.bBuildEditor`.
- **Full English README + Documentation.md**: Technical Information block,
  build environment, command reference, troubleshooting.

## 💥 Breaking Changes

None — this is the first published version.

---

## Install

Grab the build for your engine version from
[Fab](https://www.fab.com/) and drop it into your project's `Plugins/` folder.
Enable **LLM Easy Shell** or **LLM Easy Shell Lite** in the same project — that
is what exposes the `whitebox ...` commands. The engine plugins
**EditorScriptingUtilities** and **PythonScriptPlugin** are enabled
automatically by the plugin descriptor.

Full reference: [LLM White Box →](../../llm-white-box/)
