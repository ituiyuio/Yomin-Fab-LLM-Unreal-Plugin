---
layout: doc
title: Agent Online
date: 2026-06-19
tag: Release
summary: |
  AI agents can now connect directly to the Unreal Editor via LLM Easy Shell — 27 native commands and 25 Python sub-commands, covering actor manipulation, property editing, Live Coding, and screenshots.
emoji: ⚡
slug: agent-online
---

# Agent Online

We just upgraded **LLM Easy Shell** to "Agent Online" — AI agents can now drive a running Unreal Editor directly.

## What's new

- **27 native commands** covering actor CRUD, property editing, and level management
- **25 Python sub-commands** to invoke any `unreal` module API
- **Live Coding trigger** — let the agent hot-reload C++ after edits
- **Screenshot pullback** — the agent can "see" the editor viewport (PNG via TCP)

## Why "Online"

The previous Easy Shell was an offline pipeline (agent writes JSON → asset compiles). With this upgrade, the agent and the Editor share a **persistent TCP connection** (ports 15151–15200), so the agent can loop "inspect → edit → screenshot verify" in a real feedback cycle.

## Getting started

```bash
# In the Editor
Edit → Plugins → LLM Easy Shell → Enable → Restart
# A TCP port is auto-assigned; status is written to .current_port
```

Then point your agent at `skills/llm-easy-shell/SKILL.md` and you're set.
