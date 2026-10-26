---
outline: [2, 3]
---

# LLM MetaSound

JSON-Driven MetaSound Asset Generator for Unreal Engine 5.

Generate complete UMetaSoundSource and UMetaSoundPatch assets from JSON (`.llmmetasound` files, in `Plugins/LLMMetaSound/Examples/`) with auto-connected nodes and type-safe edges — no manual MetaSound editor work required.

---

## Features

- **One JSON, Complete Audio Graph** — Nodes, edges, and connections generated from a single `.llmmetasound` file
- **LLM-First Design** — AI outputs JSON directly, no MetaSound editor knowledge required
- **Bidirectional Conversion** — JSON → UMetaSoundSource/Patch, UMetaSoundSource/Patch → JSON
- **Builder Subsystem Integration** — Uses UE5 MetaSound Builder Subsystem for robust asset creation
- **Auto-Connect** — Automatically connects OnPlay trigger and audio source nodes
- **Type Safety** — Validates vertex types before creating edges, prevents invalid connections
- **6 Example Files** — TriangleSub, SawDiscord, SquareBass, SquareLead, TrianglePad, NoiseBurst
- **Full MetaSound Support** — Works with UMetaSoundSource and UMetaSoundPatch

---

## Quick Start

1. Menu → Tools → **LLM MetaSound**
2. Load a `.llmmetasound` file or paste JSON
3. Click **Generate MetaSound**
4. The generated MetaSound asset opens automatically

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "MySound",
    "MetasoundDescription": "My custom sound"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Triangle", "ClassPath": "UE.Triangle.Audio", "Name": "Osc1", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 } } },
    { "NodeID": 2, "ClassName": "Envelope Follower", "ClassPath": "UE.Envelope Follower", "Name": "AmpEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromPinName": "Audio", "ToNodeID": 2, "ToPinName": "In" }
  ]
}
```

---

## Version Info

| Item | Value |
|------|-------|
| Plugin Version | 1.2.0 |
| Engine | UE 5.7 / 5.8 |
| Modules | LLMMetaSoundEditor (Editor) |
| Publisher | YominUnreal |
| Required Plugins | Metasound (engine) |
