# Node Types

LLMMetaSound supports all MetaSound node types discovered from the INodeClassRegistry.

**Schema File:** `Plugins/LLMMetaSound/Config/Schemas/LLMMetaSoundSchema.llmmetasoundschema`

---

## Asset Types

The top-level `AssetType` field (`"Source"` or `"Patch"`) is **authoritative** — when present it takes precedence over the legacy `Metadata.NodeType`. Both spellings work; new authoring should use `AssetType`.

### Source (UMetaSoundSource)

UMetaSoundSource with transport (OnPlay trigger, auto-connected).

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "MySound",
    "MetasoundDescription": "My custom sound"
  }
}
```

### Patch (UMetaSoundPatch)

UMetaSoundPatch — pure DSP patch / subgraph without transport.

```json
{
  "AssetType": "Patch"
}
```

### Channel Layout (OutputFormat)

`OutputFormat` declares the source's channel layout: `"Mono"` (default), `"Stereo"`, `"Quad"`, `"5dot1"`, `"7dot1"`. Set it when a node publishes more than one audio output (e.g. a stereo mixer's `Out L` / `Out R`) — otherwise a stereo graph on a mono source silently drops a channel.

---

## Graph Structure

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "TriangleSub",
    "MetasoundDescription": "Triangle wave with sub-octave"
  },
  "Inputs": [
    { "Name": "Gain", "TypeName": "Primitive:Float" },
    { "Name": "Frequency", "TypeName": "Primitive:Float" }
  ],
  "Outputs": [
    { "Name": "Audio", "TypeName": "Primitive:Float" }
  ],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Triangle", "ClassPath": "UE.Triangle.Audio", "Name": "MainOsc", "InputDefaults": {} },
    { "NodeID": 2, "ClassName": "Envelope Follower", "ClassPath": "UE.Envelope Follower", "Name": "AmpEnv", "InputDefaults": {} }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromPinName": "Audio", "ToNodeID": 2, "ToPinName": "In" }
  ]
}
```

---

## Node Fields

| Field | Type | Description |
|-------|------|-------------|
| `NodeID` | int | Unique integer ID referenced by edges |
| `ClassName` | string | MetaSound node class (e.g., `"Oscillator"`, `"Triangle"`) |
| `Name` | string | Display name for the node |
| `Location` | object | X, Y position in graph editor |
| `InputDefaults` | object | Default values for input pins |

---

## Input Default Format

```json
"InputDefaults": {
  "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 },
  "Enable": { "LiteralType": "Boolean", "AsBool": true }
}
```

### Literal Types

| LiteralType | Field | Description |
|-------------|-------|-------------|
| `Float` | `AsFloat` | Float value |
| `Boolean` | `AsBool` | Boolean value |
| `Int` | `AsInt` | Integer value |
| `String` | `AsString` | String value |

---

## Edge Format

```json
"Edges": [
  { "FromNodeID": 1, "FromPinName": "Audio", "ToNodeID": 2, "ToPinName": "In" }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `FromNodeID` | int | Source node ID |
| `FromPinName` | string | Source pin name, resolved against the engine's live vertex list |
| `ToNodeID` | int | Target node ID |
| `ToPinName` | string | Target pin name, resolved against the engine's live vertex list |
| `FromVertexID` / `ToVertexID` | int | **Deprecated** legacy pin indices — used only when the corresponding `*PinName` is empty |

Pin names are stable across UE versions and self-document intent (e.g. `Audio`, `In`, `Out`, `Audio Envelope`). Prefer them for new authoring.

---

## Node Categories

### Generators

| ClassName | Description |
|-----------|-------------|
| `Triangle` | Triangle wave oscillator |
| `Saw` | Sawtooth wave oscillator |
| `Square` | Square wave oscillator |
| `Noise` | White noise generator |
| `LFO` | Low frequency oscillator |

### Filters

| ClassName | Description |
|-----------|-------------|
| `Ladder Filter` | Ladder filter (LP/HP/BP) |
| `Biquad` | Biquad filter |
| `OnePole` | One-pole filter |

### Envelopes

| ClassName | Description |
|-----------|-------------|
| `Envelope Follower` | Amplitude envelope |
| `ADSR` | Attack-Decay-Sustain-Release envelope |

### Effects

| ClassName | Description |
|-----------|-------------|
| `Delay` | Delay effect |
| `Reverb` | Reverb effect |
| `Chorus` | Chorus effect |
| `Compressor` | Dynamics compressor |

### Mix

| ClassName | Description |
|-----------|-------------|
| `Gain` | Volume/gain control |
| `Mixer` | Multi-channel mixer |
| `MonoToStereo` | Mono to stereo conversion |
| `StereoToMono` | Stereo to mono conversion |

### Utility

| ClassName | Description |
|-----------|-------------|
| `Output` | Graph output node |
| `Split` | Signal splitter |
| `Merge` | Signal merger |

---

## Common Patterns

### Simple Oscillator with Envelope

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "TriangleSub",
    "MetasoundDescription": "Triangle wave with envelope"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Triangle", "ClassPath": "UE.Triangle.Audio", "Name": "MainOsc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 110.0 } } },
    { "NodeID": 2, "ClassName": "Envelope Follower", "ClassPath": "UE.Envelope Follower", "Name": "AmpEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromPinName": "Audio", "ToNodeID": 2, "ToPinName": "In" }
  ]
}
```

### Oscillator → Filter → Envelope

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "SawDiscord",
    "MetasoundDescription": "Sawtooth with filter"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Saw", "ClassPath": "UE.Saw.Audio", "Name": "SawOsc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 175.0 } } },
    { "NodeID": 2, "ClassName": "Ladder Filter", "ClassPath": "UE.Ladder Filter.Audio", "Name": "HPF", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Envelope Follower", "ClassPath": "UE.Envelope Follower", "Name": "AmpEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromPinName": "Audio", "ToNodeID": 2, "ToPinName": "In" },
    { "FromNodeID": 2, "FromPinName": "Out", "ToNodeID": 3, "ToPinName": "In" }
  ]
}
```

### Graph Interface (with Inputs/Outputs)

```json
{
  "AssetType": "Source",
  "Metadata": {
    "NodeName": "ModularSynth"
  },
  "Inputs": [
    { "Name": "Gain", "TypeName": "Primitive:Float" },
    { "Name": "Frequency", "TypeName": "Primitive:Float" }
  ],
  "Outputs": [
    { "Name": "Audio", "TypeName": "Primitive:Float" }
  ],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Triangle", "Name": "Osc", "InputDefaults": {} }
  ],
  "Edges": []
}
```
