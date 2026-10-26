---
layout: doc
title: Lite Shell Released
date: 2026-06-10
tag: Skill
summary: |
  A minimal subset of LLM Easy Shell — 9 read-only query commands + 1 self-maintenance command, designed to let agents browse scenes and assets without side effects.
emoji: 🔍
slug: lite-shell
---

# Lite Shell Released

We released **LLM Easy Shell Lite**: a minimal subset of Easy Shell, designed for safe browsing.

> **2026-10-26 correction**: the original version of this post listed seven command names
> that never existed (`list_actors`, `inspect_actor`, …) and claimed `evaluate_python`
> ran "in a sandboxed env". Neither was true — the list below is the real command set,
> and the PyAbility runtime gives **full UE Python API access with no sandbox**
> (read-only-ness is your code's responsibility). See `skills/llm-easy-shell-lite/SKILL.md`
> for the honest read/write boundary.

## 9 read-only query commands + 1 self-maintenance command

- `ls` / `cat` / `find` / `discover` / `info` / `help` — browse actors, components, assets, classes, functions and properties
- `gamestate` — query PIE state (wave / health / gold / enemies, heuristic)
- `log --errors` / `msglog --niagara` — editor error log, Niagara validation messages
- `livecoding --status` (alias `reload` / `lc`, Windows only) — LiveCoding compile status; triggering a compile is a self-maintenance action, not read-only

## Relationship to the full version

- Lite Shell uses port range **15201–15250** (full version: 15151–15200)
- Depends on only 2 engine plugins (`PythonScriptPlugin` + `EditorScriptingUtilities`)
- Completely free, drop-in for read-only workflows — but note: third-party plugin
  abilities (`material` / `ui` / `metasound` … generate / delete / compile) reachable
  from Lite are **not** filtered by it; Lite is an observation surface, not a permission surface

## Use cases

- Doc agents: let AI understand the current project state
- Tutorial agents: let AI demo without mutating anything
- CI agents: let AI inventory assets at PR time
