---
layout: doc
title: LLMEasyShell v1.2.0 — the shell any plugin can build on
date: 2026-10-26
tag: Plugin
summary: |
  Platform-host release: Python ability hosting is open to every plugin — drop
  `.py` abilities into any plugin's `Content/Python/<Package>/abilities/` and
  they are discovered automatically. Two new one-call extension points
  (`RegisterShellCommand` / `AddPythonAbilityRoot`), six new built-in abilities,
  and the plugin is now fully project-agnostic: the host-project conditional
  dependency, the 21 project-owned abilities, and the `ui state` command are
  gone. 13 UI/input/screenshot helpers previously trapped behind the host check
  now work everywhere. UE 5.5 / 5.6 / 5.7 / 5.8 all compile clean via
  BuildPlugin -rocket.
emoji: 🐚
slug: llm-easy-shell-1.2.0
---

# LLMEasyShell v1.2.0

> 🚢 **Minor bump — the dependency stays one-way.** LLMEasyShell becomes a
> platform host: it discovers abilities and commands provided by other plugins
> without ever knowing those plugins exist. Engine compatibility unchanged:
> 5.5 / 5.6 / 5.7 / 5.8.

## ✨ New Features

- **Python ability hosting is open to every plugin** (`b709101f1`) — the
  ability loader used to hard-code this plugin's own directory in four places
  (scan root, package import path, description lookup, reload-hash cache), so a
  `.py` living anywhere else was simply invisible. The scan is now
  plugin-discovery based: every enabled plugin is checked for
  `<Plugin>/Content/Python/<Package>/abilities/*.py`. Precedence is
  deterministic — plugin hosts win over the project script directory, ordered
  by plugin name.
- **Two new extension points** (`b709101f1`) — `RegisterShellCommand()` adds a
  C++ command to the dispatch table from any plugin, and `AddPythonAbilityRoot()`
  registers an extra Python ability directory. Neither requires this plugin to
  know the caller exists.
- **Project script directory discovered by shape** (`7dfb41a0e`) — the loader
  scans `Content/Features/<any-feature>/Scripts`; adding a feature directory is
  enough, no plugin edit. `bpcomp` resolves the host's script module at runtime
  instead of assuming a fixed name.
- **Six new built-in Python abilities** — `automation_check_test` /
  `automation_dump_api` / `automation_list_tests` / `automation_run_and_wait` /
  `automation_sanity_check` (editor test automation, generalized from internal
  one-shot fossils) and `vfxsim` (Niagara simulation probing).
- **13 UI / input / screenshot helpers unblocked** (`7dfb41a0e`) — they only
  ever needed the engine, but were gated behind the same host-project check as
  the one helper that genuinely needed project code. The guard is gone; they
  work in every project now.
- **Multi-UE compatibility hardening** (`da7b269a8`) — simulated input, anim
  state machine default state, and property reflection APIs are now
  version-gated; 5.5 / 5.6 / 5.7 / 5.8 all build with zero errors and zero
  deprecation warnings under `BuildPlugin -rocket`.

## 🐛 Bug Fixes

- **PIE `play --wait` could never succeed** — the wait path was rewritten
  (`be2cc3f16`); `play` also reported success while the editor was dying
  (PIE channel repair, `ab3d3dd9e`), and the screenshot viewport truthfulness
  pass (`28a9fa896`).
- **`info` no longer lies** — `errorCount` is honest and the deadlock probe no
  longer reports false BUSY (`635859030`).
- **Live Coding stale-Intermediate criteria** extracted into a testable policy
  layer (`ReloadGatePolicy`) with behavior assertions — a 60 s timeout is no
  longer "diagnosed" as an antivirus crash without evidence (`b7a0d3980`).
- **LLMEasyShellLite `_base.py` import crash** — the package-relative import
  raised `ImportError` once the abilities directory was importable top-level;
  now absolute, works both ways (`b709101f1`).

## 💥 Breaking Changes

- **The host-project surface is gone from this plugin** (`7dfb41a0e`) — the
  `WITH_LLMEASYSHELL_CODEO` conditional dependency, the `ui state` command, the
  project cheat, and the project-owned Python abilities moved to the host
  project's own plugin. They required the host project's code and could not
  work in any other project. The generic plugin now ships **37 commands and 46
  built-in Python abilities, all project-agnostic** (v1.1.1 documented 48
  abilities including 223 project-specific sub-commands — those were the ones
  that only worked in the original host project).
- **Documentation matrix corrected** — the README claimed "UE 5.8+" while the
  product ships engine-matched packages for 5.5–5.8; `ModelContextProtocol` is
  now documented as the UE 5.8-only host dependency it actually is (host
  `.uproject` must enable it; on 5.5–5.7 the `mcp` command returns a
  not-available hint).

## ⚙ Requirements (unchanged)

- Unreal Engine 5.5 / 5.6 / 5.7 / 5.8 (one Project Version per UE)
- 9 engine plugin dependencies (see `README.md`): `PythonScriptPlugin`,
  `GameplayAbilities`, `GameplayTagsEditor`, `EnhancedInput`, `PoseSearch`,
  `Chooser`, `StructUtils`, `Niagara`, `EditorScriptingUtilities`
- `WebBrowserWidget` enabled in host `.uproject` for CEF-state UI introspection
- `ModelContextProtocol` enabled in host `.uproject` on UE 5.8 (for the `mcp`
  command; auto-stubbed on 5.5–5.7)

---

*LLMEasyShell v1.2.0 — YominUnreal*
