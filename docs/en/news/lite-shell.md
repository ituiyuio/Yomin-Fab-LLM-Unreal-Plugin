---
layout: doc
title: Lite Shell Released
date: 2026-06-10
tag: Skill
summary: |
  A read-only subset of LLM Easy Shell — 9 safe commands, designed to let agents browse scenes and assets without any side effects.
emoji: 🔍
slug: lite-shell
---

# Lite Shell Released

We released **LLM Easy Shell Lite**: a read-only subset of Easy Shell, designed for safe browsing.

## 9 commands, all read-only

- `list_actors` / `inspect_actor` — browse actors in the scene
- `list_assets` / `inspect_asset` — browse assets under `/Game/`
- `get_property` — read any property
- `screenshot` — capture the current viewport
- `evaluate_python` — run read-only Python in a sandboxed env

## Relationship to the full version

- Lite Shell uses port range **15201–15250** (full version: 15151–15200)
- Depends on only 2 engine plugins (`PythonScriptPlugin` + `EditorScriptingUtilities`)
- Completely free, drop-in for read-only workflows

## Use cases

- Doc agents: let AI understand the current project state
- Tutorial agents: let AI demo without mutating anything
- CI agents: let AI inventory assets at PR time
