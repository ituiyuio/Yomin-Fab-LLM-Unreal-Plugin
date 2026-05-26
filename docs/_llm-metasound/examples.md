---
layout: default
title: Examples
parent: LLM MetaSound
nav_order: 2
---

# Examples

The `Examples/` folder in the plugin contains 6 complete `.llmmetasound` files demonstrating different audio synthesis patterns.

---

## TriangleSub

Triangle wave with sub-octave character.

**File:** `Examples/TriangleSub.llmmetasound`

**Nodes:** Triangle → Envelope Follower

**Frequency:** 110 Hz

---

## SawDiscord

Sawtooth wave with dissonant filter resonance.

**File:** `Examples/SawDiscord.llmmetasound`

**Nodes:** Saw → Ladder Filter → Envelope Follower

**Frequency:** 175 Hz

---

## SquareBass

Deep square wave bass with filter and envelope.

**File:** `Examples/SquareBass.llmmetasound`

**Nodes:** Square → Ladder Filter → Envelope Follower

**Frequency:** 80 Hz

---

## SquareLead

Square wave lead synth with filter and envelope.

**File:** `Examples/SquareLead.llmmetasound`

**Nodes:** Square → Ladder Filter → Envelope Follower

**Frequency:** 440 Hz

---

## TrianglePad

Soft triangle wave pad with gentle envelope.

**File:** `Examples/TrianglePad.llmmetasound`

**Nodes:** Triangle → Envelope Follower

**Frequency:** 220 Hz

---

## NoiseBurst

White noise burst with percussive envelope.

**File:** `Examples/NoiseBurst.llmmetasound`

**Nodes:** Noise → Envelope Follower

---

## Using Examples

1. Open the LLM MetaSound Panel: Window → LLM MetaSound
2. Click "Load File" and navigate to `Examples/`
3. Select any `.llmmetasound` file
4. Click "Generate MetaSound"
5. The MetaSound asset is created in your project's Content folder

---

## File Format Summary

| Field | Description |
|-------|-------------|
| `Metadata.NodeName` | Asset display name |
| `Metadata.NodeType` | `"MetasoundSource"` or `"MetasoundPatch"` |
| `Inputs[]` | Graph-level input interface |
| `Outputs[]` | Graph-level output interface |
| `Nodes[]` | Graph nodes |
| `Edges[]` | Connections between pins |
