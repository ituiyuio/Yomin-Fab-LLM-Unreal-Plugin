# Examples

The `Plugins/LLMMetaSound/Examples/` folder in the plugin contains 6 complete `.llmmetasound` files demonstrating different audio synthesis patterns.

---

## TriangleSub

Triangle wave with sub-octave character.

**File:** `Plugins/LLMMetaSound/Examples/TriangleSub.llmmetasound`

**Nodes:** Triangle → Envelope Follower

**Frequency:** 110 Hz

---

## SawDiscord

Sawtooth wave with dissonant filter resonance.

**File:** `Plugins/LLMMetaSound/Examples/SawDiscord.llmmetasound`

**Nodes:** Saw → Ladder Filter → Envelope Follower

**Frequency:** 175 Hz

---

## SquareBass

Deep square wave bass with filter and envelope.

**File:** `Plugins/LLMMetaSound/Examples/SquareBass.llmmetasound`

**Nodes:** Square → Ladder Filter → Envelope Follower

**Frequency:** 80 Hz

---

## SquareLead

Square wave lead synth with filter and envelope.

**File:** `Plugins/LLMMetaSound/Examples/SquareLead.llmmetasound`

**Nodes:** Square → Ladder Filter → Envelope Follower

**Frequency:** 440 Hz

---

## TrianglePad

Soft triangle wave pad with gentle envelope.

**File:** `Plugins/LLMMetaSound/Examples/TrianglePad.llmmetasound`

**Nodes:** Triangle → Envelope Follower

**Frequency:** 220 Hz

---

## NoiseBurst

White noise burst with percussive envelope.

**File:** `Plugins/LLMMetaSound/Examples/NoiseBurst.llmmetasound`

**Nodes:** Noise → Envelope Follower

---

## Using Examples

1. Open the LLM MetaSound Panel: Window → LLM MetaSound
2. Click "Load File" and navigate to `Plugins/LLMMetaSound/Examples/`
3. Select any `.llmmetasound` file
4. Click "Generate MetaSound"
5. The MetaSound asset is created in your project's Content folder

---

## File Format Summary

| Field | Description |
|-------|-------------|
| `Metadata.NodeName` | Asset display name |
| `Metadata.NodeType` | `"MetasoundSource"` or `"MetasoundGraph"` (subgraph/Patch) |
| `Inputs[]` | Graph-level input interface |
| `Outputs[]` | Graph-level output interface |
| `Nodes[]` | Graph nodes |
| `Edges[]` | Connections between pins |
