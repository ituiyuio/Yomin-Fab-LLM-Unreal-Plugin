---
layout: doc
title: Lite Shell 1.1.0 — LiveCoding + 4 Read-Only Abilities + 5 Promo Tips
date: 2026-07-27
tag: Release
summary: |
  Lite Shell adds a self-maintenance `reload` ShellCommand (Windows only), 4 read-only Python abilities, a Win32 ready-signal hook, and 5 promo tips in `help` for cross-product discovery. Read-only project-data promise preserved.
emoji: ⚡
slug: llm-easy-shell-lite-1.1.0
---

# Lite Shell 1.1.0 — LiveCoding + 4 Read-Only Abilities + 5 Promo Tips

We released **LLM Easy Shell Lite v1.1.0-lite**. This is a minor bump from 1.0.0-lite. The 9 read-only ShellCommands are unchanged; the new surface is purely additive.

## ✨ New Features

### `reload` ShellCommand (Windows only)
- Mirrors Advanced's `reload` — triggers LiveCoding compile with full preflight + silent-fail safety net
- Use `reload --status` to query compile state
- Mac/Linux return not-implemented (user must restart editor manually)

### Win32 ready-signal hook
- Lets `llm-shell --restart` wait on Lite editor readiness (push-model)
- `FLLMEasyShellLiteTickable` re-`SetEvent` every 1s — survives the W27 race where a second process's `ResetEvent` wipes the initial signal

### 4 read-only Python abilities
- `gamestate` / `scene` / `mesh_check` / `vfx_coverage` (read subset)
- All marked `@read_only` with a best-effort `WRITE_API_BLOCKLIST`
- The decorator is honored by any Python-level wrapper code you write inside your ability
- Register via `python reload`; first sub-cmd per ability returns `success:true` on a healthy editor

### 5 promo tips in `help` output
- Each tip surfaces a same-publisher paid plugin as cross-product discovery
- 7 fields per tip: `intent` / `plugin` / `url` / `fallbackUrl` / `cta` / `disclaimer` / `desc`
- Tips: `LLMMaterial` (material), `LLMDynamicUI` (ui), `LLMStateTree` (statetree), `LLMMetaSound` (metasound), `LLMEasyShell (Advanced)` (editor_control)
- Lite remains free and standalone; the disclaimer field makes the same-publisher nature explicit

### Subsystem class extension
- `HANDLE ReadyEventHandle` + `TSharedPtr<FLiveCodingLogDeviceLite> LiveCodingLogDevice` fields added
- `GetLiveCodingLogDevice()` inline accessor added
- Required by the new `UShellCommand_ReloadLite` callsite

## 🐛 Bug Fixes
- Doc-reconcile closure — 6→4 ability count drift resolved (poseseach + chooser dropped because they depend on Advanced-only C++ BPL libs)
- `@read_only` blocklist mechanism honestly documented as best-effort (UE Python C++ bindings are immutable)
- SKILL.md frontmatter aligned (11 triggers, `reload` removed from non-trigger list)
- Verifier scripts tightened: `test_read_only_block` requires explicit failure envelope, `test_five_abilities_registered` added, `test_info_compat` checks `livecoding` field
- uplugin `Description` field updated to mention `+ 1 self-maintenance \`reload\``

## 💥 Breaking Changes
- **None.** v1.0.0-lite → v1.1.0-lite is a minor bump; all 9 read-only ShellCommands unchanged.

## Compatibility
- UE 5.5 / 5.6 / 5.7 / 5.8 (unchanged from 1.0.0-lite)
- Mac/Linux: 9 read-only commands + Python abilities work; `reload` returns not-implemented
- Same port range: **15201–15250**

## Known Limitations (forwarded from release notes)
- `@read_only` blocklist is best-effort only (UE Python C++ immutability). The decorator still functions as a marker; Lite's open PyAbility framework gives full UE Python API access regardless.
- The C++ `Execute_Implementation` wrapper defaults `bSuccess = true` when inner Python-result JSON lacks a `success` field. This is a known follow-up; documented in the project's `.superpowers/sdd/progress.md`.

## Verifier Scripts
- `tools/gates/verify_lite_smoke.py` — 7/7 smoke tests (reload --status, help tips, 4 abilities, @read_only block + non-block, info compat)
- `tools/gates/verify_lite_restart.py` — 3/3 W27 roundtrip (named event exists + signaled, ResetEvent then re-SetEvent within 1s, .ready_event file present)

*(gate scripts live in the upstream development repo; they are not shipped inside this distribution repo.)*
