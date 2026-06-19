---
outline: [2, 3]
---

# LLM MetaSound

DSL-driven MetaSound audio generation for Unreal Engine 5. The agent writes `.llmmetasound` JSON, the editor turns it into a real `UMetaSoundSource` or `UMetaSoundPatch` — generators, filters, envelopes, mixers, bus I/O, with type-safe edges.

> **Skill file:** [`skills/llm-metasound/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-metasound/SKILL.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Create or design a UE5 MetaSound graph (`UMetaSoundSource` or `UMetaSoundPatch`)
- Convert an audio description into a `.llmmetasound` file
- Inspect or modify an existing MetaSound JSON
- Look up a MetaSound node type (Oscillators, Filters, Envelopes, Mixers, etc.)
- Query node input/output ports, types, and default values

**Triggers:** `.llmmetasound`, MetaSound, audio, sound, oscillator, filter, envelope, mixer, UMetaSoundSource, UMetaSoundPatch.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM MetaSound** plugin | Distributed via this repository (Fab listing coming soon) |
| Enabled in editor | Edit → Plugins → AI → **LLM MetaSound** → restart editor |
| MetaSound engine plugin | Built into UE 5.7; no extra install |

---

## Quick Example

Ask the agent:

> "Give me a triangle wave at 440Hz with a short attack-release envelope."

The agent produces a `.llmmetasound` file:

```json
{
  "Metadata": {
    "NodeName": "MyTriangle",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Triangle wave with AR envelope"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    {
      "NodeID": 1,
      "ClassName": "Triangle",
      "Name": "Osc1",
      "InputDefaults": {
        "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 }
      }
    },
    {
      "NodeID": 2,
      "ClassName": "Envelope Follower",
      "Name": "AmpEnv",
      "InputDefaults": {
        "Enable":   { "LiteralType": "Boolean", "AsBool": true },
        "Attack":   { "LiteralType": "Float",   "AsFloat": 0.01 },
        "Release":  { "LiteralType": "Float",   "AsFloat": 0.20 }
      }
    }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
  ]
}
```

Save it, open the LLM MetaSound panel, click **Generate** — the `UMetaSoundSource` is on disk.

---

## What the Skill Knows

The full skill body contains:

- **All node types** — Oscillators (Sine, Triangle, Saw, Square, Noise), Filters, Envelopes, Mixers, Bus I/O
- **Edge types** — type-safe vertex connections (auto, audio, trigger, float, int)
- **`UMetaSoundSource` vs `UMetaSoundPatch`** — source = playable sound; patch = reusable audio graph referenced by sources
- **Input / Output declarations** — exposed parameters, bus bindings
- **6 example files** — TriangleSub, SawDiscord, SquareBass, SquareLead, TrianglePad, NoiseBurst
- **Builder subsystem** — uses UE5's MetaSound Builder Subsystem for robust asset creation

---

## Compiling the JSON into an Asset

```
# Manual: editor panel
Tools → LLM MetaSound Panel → select .llmmetasound file → Generate

# CLI (with llm-easy-shell installed)
metasound generate /Game/Audio/MyTriangle --from MyTriangle.llmmetasound
```

The MetaSound asset opens in the MetaSound editor.

---

## Round-Trip

Already have a MetaSound? Use **Export to JSON** in the editor panel to dump it to a `.llmmetasound` file. The agent edits it, you re-generate.

---

## Related Skills

- [**llm-easy-shell** →](./llm-easy-shell) — drive the editor from the CLI.
- [**llm-easy-shell-lite** →](./llm-easy-shell-lite) — read-only exploration.
