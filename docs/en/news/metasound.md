---
layout: doc
title: MetaSound Plugin Launched
date: 2026-05-30
tag: Plugin
summary: |
  The fourth plugin — LLM MetaSound — is live. It compiles UMetaSoundSource and UMetaSoundPatch from JSON.
emoji: 🔊
slug: metasound
---

# MetaSound Plugin Launched

We released **LLM MetaSound**: the fourth member of the "JSON → asset" family.

## What it generates

- `UMetaSoundSource` — full MetaSound assets
- `UMetaSoundPatch` — sub-graphs / patches
- Supports **generators / filters / envelopes / mixers / bus IO** — the full node set
- Automatic node wiring — no need to draw connections when writing JSON

## Example

```json
{
  "version": "1.0",
  "name": "Kick",
  "type": "Source",
  "graph": {
    "nodes": [
      { "id": "osc", "type": "SineOscillator", "params": { "frequency": 60 } },
      { "id": "env", "type": "ADEnvelope",     "params": { "attack": 0.001, "decay": 0.12 } },
      { "id": "out", "type": "Output" }
    ],
    "connections": [
      { "from": "osc", "to": "env" },
      { "from": "env", "to": "out" }
    ]
  }
}
```

## Where to find it

- Repo: `skills/llm-metasound/SKILL.md`
- Wiki: `/llm-metasound/`
- Fab listing: coming soon
