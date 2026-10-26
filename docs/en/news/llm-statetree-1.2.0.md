---
layout: doc
title: LLMStateTree v1.2.0 — 9 Sub-command Agent Surface + Contract Hardening
date: 2026-10-26
tag: Plugin
summary: |
  LLMStateTree v1.2.0 goes agent-first: the `llmstatetree` command surface grows to 9 sub-commands (new: preview / nodes / schema) so LLM agents can dry-run a document without writing an asset, list the node types the project actually has via reflection, and dump node schema snapshots. The same batch hardens the DSL contract: roundtrip fidelity fixed (export→re-import used to drop every parameter), unknown vocabulary now errors instead of silently falling back to defaults, and validation warnings surface in the agent envelope. Sample corpus grows to 7 and doubles as the roundtrip regression corpus. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 all PASS.
emoji: 🌲
slug: llm-statetree-1.2.0
---

# LLMStateTree v1.2.0

> Minor bump — new agent command surface and samples, plus stricter DSL validation (see Breaking Changes). Engine compatibility unchanged: 5.5 / 5.6 / 5.7 / 5.8.

## ✨ New Features

- **Agent command surface: 9 `llmstatetree` sub-commands** (`d11041e38`) — `generate` / `preview` / `nodes` / `schema` / `inspect` / `export` / `copy` / `delete` / `compile`
  - `preview` — parses a `.llmstate` without writing an asset, for LLM dry-run validation
  - `nodes` — lists the StateTree node types **this project** actually has, discovered by reflection (the authoritative list; the bundled schema is only a snapshot)
  - `schema` — dumps the node schema to a file for offline agent reference
- **Node user names** (`d11041e38`) — tasks / conditions / evaluators can now carry user-written names from the DSL; no longer lost on round trip
- **2 new samples, corpus now 7** (`d11041e38`) — `FlatFormatAI.llmstate` (flat input format: stable `id`s + `parent` links + all transitions in one top-level array) and `DslLab.llmstate` (full DSL feature-coverage fixture: every parameter type / condition type / operand / trigger / priority / delay / consideration). The samples double as the regression corpus: the roundtrip gate runs each through preview → generate → export → generate → export with dual comparison

## 🐛 Bug Fixes

- **Roundtrip fidelity** (`d11041e38`) — the serializer wrote parameters as an array while the parser read an object, so export→re-import silently dropped every parameter; fixed. `linkedAsset` / `eventTag` / `delayed` transition fields are now parsed; legacy document shapes still accepted
- **`delete --force` now forces; overwrite protection now blocks; duplicate state names error** (`d11041e38`) — all three were silent no-ops before
- **Root state `type: "Group"` no longer silently downgraded to State** (`d11041e38`) — the downgrade also dropped the group's SelectionBehavior

## 💥 Breaking Changes

- **Stricter validation** (`d11041e38`) — unrecognized binding scopes / triggers / transition types / priorities / state types / selection behaviors / operands now produce errors instead of silently falling back to defaults
- **Version-dependent vocabulary** — transition types `Parent` / `NextParent` / `NextSelectableParent` require UE 5.8 and operand `Multiply` requires UE 5.7; using them on older engines now fails with a clear error (this batch also restored the compile gates that make those engines build at all)
- **NpcDialogs samples removed from the distributed package** (`7dfb41a0e`) — the 4 project-specific NPC conversation trees no longer ship with the plugin (relocated to a project-only plugin); the distributed package stays project-agnostic

## ⚡ Improvements

- **Warnings now reach agents** (`d11041e38`) — parser deprecation/validation warnings used to go only to the engine log, invisible to the agent envelope; they now surface in the preview / generate result envelope
- **Multi-UE build hardening** (`d11041e38` + this batch) — the new contract surface compiles clean (0 errors / 0 warnings) on all of 5.5 / 5.6 / 5.7 / 5.8 via `BuildPlugin -rocket`
