# Node Types

LLMMetaSound supports all MetaSound node types discovered from the INodeClassRegistry.

**Schema File:** `Plugins/LLMMetaSound/Config/Schemas/LLMMetaSoundSchema.llmmetasoundschema`

---

## Asset Types

### MetasoundSource

UMetaSoundSource with transport (OnPlay trigger).

```json
{
  "Metadata": {
    "NodeName": "MySound",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "My custom sound"
  }
}
```

### MetasoundGraph

UMetaSoundPatch — pure DSP patch / subgraph without transport.

---

## Graph Structure

```json
{
  "Metadata": {
    "NodeName": "TriangleSub",
    "NodeType": "MetasoundSource",
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
    { "NodeID": 1, "ClassName": "Triangle", "Name": "MainOsc", "InputDefaults": {} },
    { "NodeID": 2, "ClassName": "Envelope Follower", "Name": "AmpEnv", "InputDefaults": {} }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
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
  { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `FromNodeID` | int | Source node ID |
| `FromVertexID` | int | Source pin index |
| `ToNodeID` | int | Target node ID |
| `ToVertexID` | int | Target pin index |

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
  "Metadata": {
    "NodeName": "TriangleSub",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Triangle wave with envelope"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Triangle", "Name": "MainOsc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 110.0 } } },
    { "NodeID": 2, "ClassName": "Envelope Follower", "Name": "AmpEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
  ]
}
```

### Oscillator → Filter → Envelope

```json
{
  "Metadata": {
    "NodeName": "SawDiscord",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Sawtooth with filter"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Saw", "Name": "SawOsc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 175.0 } } },
    { "NodeID": 2, "ClassName": "Ladder Filter", "Name": "HPF", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Envelope Follower", "Name": "AmpEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 1 }
  ]
}
```

### Graph Interface (with Inputs/Outputs)

```json
{
  "Metadata": {
    "NodeName": "ModularSynth",
    "NodeType": "MetasoundSource"
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
