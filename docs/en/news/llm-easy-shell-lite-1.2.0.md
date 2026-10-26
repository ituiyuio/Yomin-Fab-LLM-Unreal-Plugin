---
layout: doc
title: LLMEasyShellLite v1.2.0 — registry-driven help, project-agnostic gamestate
date: 2026-10-26
tag: Plugin
summary: |
  Lite Shell v1.2.0 makes the command surface self-describing: `help` now
  enumerates the command registry instead of a hardcoded list, so `livecoding`
  and its aliases finally show up. `gamestate` resolves the player pawn in any
  project instead of a host-specific class, and the "read-only" claim is scoped
  to what Lite actually enforces. The plugin now ships with zero
  project-specific content. UE 5.5 / 5.6 / 5.7 / 5.8 all compile clean via
  BuildPlugin -rocket.
emoji: 🐚
slug: llm-easy-shell-lite-1.2.0
---

# LLMEasyShellLite v1.2.0

> 🚢 **Minor bump — the command set is unchanged.** The same 9 read-only
> commands plus the `livecoding` self-maintenance command. What changes is
> that Lite now *describes itself accurately*: `help` enumerates the registry,
> and `gamestate` works outside the host project. Engine compatibility
> unchanged: 5.5 / 5.6 / 5.7 / 5.8.

## ✨ New Features

- **`help` enumerates the command registry** — the command list used to be a
  hardcoded table of nine names, so anything registered outside that table was
  invisible. `livecoding` (aliases `reload` / `lc`) was registered on Windows
  but never advertised: `help livecoding` and `help reload` both answered
  "Unknown command", and the only way to learn the command existed was the
  prose in the skill file. `help` now walks the dispatcher registry, so a
  registered command is always discoverable — and each entry carries its
  description and its aliases.
- **`help <command>` resolves aliases** — `help reload` now reports the
  canonical command name (`livecoding`) together with its usage string.
- **Third-party plugin abilities are labelled as open surfaces** — `help` still
  lists them, but the docs now state plainly that a plugin's command set and
  write semantics belong to that plugin, and that Lite neither filters nor
  sandboxes them.

## 🐛 Bug Fixes

- **`gamestate` finds the player in any project** — the player lookup was
  hardcoded to a host-specific character class, so it silently found nothing
  outside that project. It now resolves the pawn in three steps (player
  controller → player-controlled pawn → "Player"-named character), matching the
  Advanced shell.
- **`wave.paused` / `wave.waveActive` expose the raw flags** — `isActive` is
  `bWaveActive && !bPaused`; collapsing both into one boolean made "the wave
  never continued" and "the wave is paused" indistinguishable.
- **`enemyCount` no longer counts dying actors** — actors that are being
  destroyed were still in the actor list during the death VFX, inflating the
  count.
- **`reload`'s upgrade verdicts are a pure, testable policy layer** — the two
  Live Coding escalation criteria moved into their own file so the verdict can
  be asserted directly instead of inferred from log text.
- **Live Coding log verdicts stop guessing** — the log device no longer
  concludes a crash family when the only signal in the log is a cancelled
  compile.

## ⚡ Improvements

- **The "read-only" claim is scoped to what is actually enforced** — the
  guarantee covers the 9 built-in commands. The Python runtime and third-party
  plugin abilities are documented as open surfaces: Lite is an observation
  plane, not a permission boundary.
- **No project-specific content ships** — host-specific asset names, absolute
  paths and placeholder publisher fields were removed from the sources, the
  help text and the shipped documentation. The plugin now passes the Fab
  publish pipeline's project-content gate for the first time.
- **Doc reconciliation** — README, Documentation.md, VERSION-NOTES.md and the
  agent skill now agree with the runtime on the command count, the ability
  count and the canonical command names.

## 💥 Breaking Changes

- **None of the built-in commands changed.**
- **`python scene` is gone.** The `scene` ability was dropped after it turned
  out to be broken with no existing caller. The remaining bundled abilities are
  `simple` (an end-to-end demo), `gamestate`, `mesh_check` and `vfx_coverage`.
- **The Python ability loader now discovers by plugin shape** — a `.py` living
  in another plugin's `Content/Python/<Package>/abilities/` is visible to the
  Advanced shell. Lite's own bundled abilities are unaffected.

## Compatibility

- UE 5.5 / 5.6 / 5.7 / 5.8 — each Fab Project Version ships an independent zip
  (UE 5.5 / 5.6 / 5.7 / 5.8, `EngineVersion` 5.5.0 / 5.6.0 / 5.7.0 / 5.8.0)
- Mac/Linux: the 9 read-only commands and the Python abilities work;
  `livecoding` returns not-implemented
- Same port range: **15201–15250** (disjoint from Advanced's 15151–15200)
- Dependencies unchanged: PythonScriptPlugin + EditorScriptingUtilities

## Known Limitations

- The Python runtime is an open environment — a `.py` you drop into the
  abilities directory can call the full UE Python API. The `@read_only`
  decorator is a marker; the write-API blocklist cannot intercept UE Python
  C++ bindings (they are immutable) and is a courtesy reminder, not a sandbox.
- Third-party plugin abilities carry the plugin's own write semantics. Lite
  ships no permission boundary for them.
