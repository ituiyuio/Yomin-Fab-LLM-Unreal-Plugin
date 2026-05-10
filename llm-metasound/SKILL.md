---
name: llm-metasound
description: |
  LLMMetaSound is a DSL-driven UE5 MetaSound audio asset generation system. Use this skill when users need to:
  (1) Create or design UE5 MetaSound audio graphs (UMetaSoundSource / UMetaSoundPatch)
  (2) Convert audio descriptions into generatable DSL format (.llmmetasound JSON)
  (3) Understand or modify existing MetaSound JSON definitions
  (4) Learn about supported node types (Oscillators, Filters, Envelopes, Mixers, etc.)
  (5) Query node input/output ports, types, and default values
---

# LLMMetaSound - MetaSound Audio Asset DSL

## File Format

MetaSound definitions use the `.llmmetasound` extension, formatted as LLM-friendly JSON.

## Reference Files

**Node Schema**: `Config/Schemas/LLMMetaSoundSchema.llmmetasoundschema` — Contains complete definitions for all available MetaSound node types

**Examples Directory**: `Examples/` — Contains `.llmmetasound` example files

## Quick Start

```json
{
  "Metadata": {
    "NodeName": "MySynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "A simple synthesizer"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Sine", "Name": "Osc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 } } },
    { "NodeID": 2, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
  ]
}
```

## DSL Reference

### Metadata

```json
"Metadata": {
  "NodeName": "MySound",           // Asset name (required)
  "NodeType": "MetasoundSource",  // or "MetasoundPatch"
  "MetasoundDescription": "..."    // Description (optional)
}
```

`NodeType` determines the asset type:
- `MetasoundSource` → UMetaSoundSource (playable audio)
- `MetasoundPatch` → UMetaSoundPatch (pure DSP subgraph)

### Inputs / Outputs

Graph interface members (optional):

```json
"Inputs": [
  {
    "Name": "Frequency",
    "TypeName": "Primitive:Float",
    "LiteralValue": { "LiteralType": "Float", "AsFloat": 440.0 }
  }
],
"Outputs": [
  {
    "Name": "Audio",
    "TypeName": "Audio:Buffer"
  }
]
```

### LiteralValue Format

```json
{ "LiteralType": "Float",    "AsFloat": 440.0 }
{ "LiteralType": "Integer",   "AsInteger": 2 }
{ "LiteralType": "Boolean",   "AsBool": true }
{ "LiteralType": "String",    "AsString": "Hello" }
{ "LiteralType": "FloatArray", "AsFloatArray": [1.0, 2.0, 3.0] }
```

**VertexID**: Port index on the node (0-based), determined by the node definition.

### Nodes

```json
"Nodes": [
  {
    "NodeID": 1,
    "ClassName": "Input",         // Node class name (required)
    "Name": "Freq",               // Display name (optional)
    "TypeName": "Primitive:Float", // Required for Input/Output nodes
    "InputDefaults": {             // Default values (optional)
      "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 }
    }
  }
]
```

**Interface nodes** (Input/Output):
- `ClassName` must be `"Input"` or `"Output"`
- `TypeName` must be specified, e.g., `"Primitive:Float"`, `"Audio:Buffer"`

**External nodes** (Oscillator, Filter, etc.):
- `ClassName` uses the registered class name
- `TypeName` can be omitted for External nodes

### Edges

```json
"Edges": [
  {
    "FromNodeID": 1,     // Source node ID
    "FromVertexID": 0,   // Source output port index
    "ToNodeID": 2,       // Target node ID
    "ToVertexID": 0       // Target input port index
  }
]
```

**Connection type rules**:
- `Audio:Buffer` → `Audio:Buffer` (audio to audio)
- `Primitive:Float` → `Primitive:Float` (float to float)
- Audio cannot connect directly to float — use `ConversionAudioToFloat`

## Node Categories

### Generators

| ClassName | Description |
|-----------|-------------|
| `Sine` | Sine wave oscillator |
| `Saw` | Sawtooth wave oscillator |
| `Square` | Square wave oscillator |
| `Triangle` | Triangle wave oscillator |
| `Noise` | White noise |
| `Perlin Noise (audio)` | Perlin noise (audio) |
| `Perlin Noise (float)` | Perlin noise (float) |
| `LFO` | Low frequency oscillator |
| `Additive Synth` | Additive synthesizer |
| `SuperOscillatorMono` | Super oscillator (mono) |
| `SuperOscillatorStereo` | Super oscillator (stereo) |
| `Subharmonizer` | Subharmonizer |

### Filters

| ClassName | Description |
|-----------|-------------|
| `Ladder Filter` | Moog-style ladder filter |
| `Biquad Filter` | Biquad filter |
| `State Variable Filter` | State variable filter |
| `DynamicFilter` | Dynamic filter |
| `Flanger` | Flanger effect |
| `Bitcrusher` | Bitcrusher effect |
| `WaveShaper` | Wave shaper |
| `RingMod` | Ring modulator |
| `One-Pole Low Pass Filter` | One-pole low pass |
| `One-Pole High Pass Filter` | One-pole high pass |

### Envelopes

| ClassName | Description |
|-----------|-------------|
| `Envelope Follower` | Envelope follower |
| `ADSR Envelope` | ADSR envelope |
| `AD Envelope` | AD envelope |
| `Fade` | Fade in/out |

### Math

| ClassName | Description |
|-----------|-------------|
| `Add` | Addition |
| `Subtract` | Subtraction |
| `Multiply` | Multiplication |
| `Divide` | Division |
| `Clamp` | Clamp to range |
| `MapRange` | Map range |
| `Abs` | Absolute value |
| `Max` | Maximum |
| `Min` | Minimum |
| `Power` | Power |
| `InterpTo` | Interpolation |

### Triggers

| ClassName | Description |
|-----------|-------------|
| `Trigger Delay` | Trigger delay |
| `Trigger Once` | Single trigger |
| `Trigger Select (N)` | N-way trigger select |
| `Trigger Sequence (N)` | N-step trigger sequence |
| `Trigger Route (Float, N)` | N-way float trigger route |
| `Trigger Route (Audio, N)` | N-way audio trigger route |
| `Trigger On Value Change` | Value change trigger |
| `Trigger Toggle` | Trigger toggle |
| `TriggerRepeat` | Repeat trigger |

### Delays

| ClassName | Description |
|-----------|-------------|
| `Delay` | Delay |
| `Stereo Delay` | Stereo delay |
| `Delay Pitch Shift` | Pitch shift delay |
| `Diffuser` | Diffuser |
| `GrainDelayNode` | Grain delay |
| `Plate Reverb` | Plate reverb |

### Mix

| ClassName | Description |
|-----------|-------------|
| `Audio Mixer (Mono, N)` | N-channel mono mixer |
| `Audio Mixer (Stereo, N)` | N-channel stereo mixer |

### Wave Player

| ClassName | Description |
|-----------|-------------|
| `Wave Player` | Sample player |

### External IO

| ClassName | Description |
|-----------|-------------|
| `Audio Bus Reader (N)` | N-channel audio bus reader |
| `Audio Bus Writer (N)` | N-channel audio bus writer |
| `Wave Writer` | Sample writer |

### Conversions

| ClassName | Description |
|-----------|-------------|
| `ConversionAudioToFloat` | Audio → Float |
| `ConversionFloatToAudio` | Float → Audio |
| `ConversionFloatToTime` | Float → Time |
| `ConversionTimeToFloat` | Time → Float |
| `BPMToSeconds` | BPM → Seconds |

## Common Patterns

### Oscillator → Filter → Envelope (Most Common Template)

```json
{
  "Metadata": {
    "NodeName": "BasicSynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Basic oscillator with filter and envelope"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Saw", "Name": "Osc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 110.0 } } },
    { "NodeID": 2, "ClassName": "Ladder Filter", "Name": "LPF", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 1 }
  ]
}
```

### Synthesizer with Input Interface

```json
{
  "Metadata": {
    "NodeName": "ParametricSynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Synthesizer with frequency and gain inputs"
  },
  "Inputs": [
    { "Name": "Frequency", "TypeName": "Primitive:Float", "LiteralValue": { "LiteralType": "Float", "AsFloat": 440.0 } },
    { "Name": "Gain", "TypeName": "Primitive:Float", "LiteralValue": { "LiteralType": "Float", "AsFloat": 1.0 } }
  ],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Input", "Name": "FreqIn", "TypeName": "Primitive:Float" },
    { "NodeID": 2, "ClassName": "Input", "Name": "GainIn", "TypeName": "Primitive:Float" },
    { "NodeID": 3, "ClassName": "Sine", "Name": "Osc", "InputDefaults": {} },
    { "NodeID": 4, "ClassName": "Multiply", "Name": "GainMul", "InputDefaults": {} },
    { "NodeID": 5, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 0 },
    { "FromNodeID": 3, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 1 },
    { "FromNodeID": 4, "FromVertexID": 0, "ToNodeID": 5, "ToVertexID": 1 }
  ]
}
```

### ADSR Envelope Template

```json
{
  "Metadata": {
    "NodeName": "ADSRTest",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "ADSR envelope test"
  },
  "Nodes": [
    { "NodeID": 1, "ClassName": "Noise", "Name": "Noise", "InputDefaults": {} },
    { "NodeID": 2, "ClassName": "ADSR Envelope", "Name": "Env", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Multiply", "Name": "Mul", "InputDefaults": {} },
    { "NodeID": 4, "ClassName": "Envelope Follower", "Name": "OutputEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 1 },
    { "FromNodeID": 3, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 1 }
  ]
}
```

## Examples

All example files are located in `Examples/`:

| File | Structure | Description |
|------|-----------|-------------|
| `SquareBass.llmmetasound` | Square → Ladder Filter → Envelope Follower | Deep square bass |
| `SawDiscord.llmmetasound` | Saw → Ladder Filter → Envelope Follower | Dissonant saw |
| `TrianglePad.llmmetasound` | Triangle → Envelope Follower | Soft triangle pad |
| `TriangleSub.llmmetasound` | Triangle → Envelope Follower | Triangle sub |
| `NoiseBurst.llmmetasound` | Noise → Envelope Follower | Percussive noise |
| `SquareLead.llmmetasound` | Square → Ladder Filter → Envelope Follower | Square lead |

## VertexID Quick Reference

When unsure about port indices, export an existing asset via the LLMMetaSound editor panel to see the correct VertexIDs.

Common node port indices (defined by registry, may vary by UE version):

**Oscillators (Sine/Saw/Square/Triangle/Noise)**:
- index 0 = Audio (output)
- index 1 = Frequency (input)
- index 2 = FM (input, optional)

**Ladder Filter**:
- index 0 = Audio (output)
- index 0 = Audio (input)
- index 1 = Cutoff (input)
- index 2 = Resonance (input)

**Envelope Follower**:
- index 0 = Audio (output)
- index 1 = Audio (input)
- index 2 = Enable (input, boolean)

## Troubleshooting

1. **Node class name not found**: Use the `className` value from the Schema, not `displayName`
2. **Connection failed**: Check if TypeName matches (`Audio:Buffer` cannot directly connect to `Primitive:Float`)
3. **VertexID uncertain**: Export existing asset from editor panel to view, or look up the node's `inputs`/`outputs` order in the Schema
4. **Input/Output nodes**: Each interface member needs a corresponding node with `ClassName="Input"/"Output"`
5. **Default values not taking effect**: `InputDefaults` can only set Input ports, Output ports cannot have default values

## Editor Workflow

1. Open Editor → Window → LLMMetaSound Panel
2. Paste or write `.llmmetasound` JSON in the panel
3. Click Generate to create the MetaSound asset
4. Export existing MetaSound to JSON via Export button for modification and regeneration
