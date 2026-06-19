---
outline: [2, 3]
---

# LLM Material

DSL-driven Material asset generation for Unreal Engine 5. The agent writes `.llmmat` JSON, the editor turns it into a real `UMaterial` — full expression graph, UE5 Substrate, and inline HLSL `.ush` shader functions.

> **Skill file:** [`skills/llm-material/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-material/SKILL.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Create or design a UE5 Material (surface, translucent, emissive, decal, post-process)
- Convert a material description into a `.llmmat` file
- Inspect or modify an existing `.llmmat` file
- Look up an Expression node (Add, Multiply, TextureSample, Custom, etc.)
- Write an HLSL shader function (`.ush`) and reference it from a material

**Triggers:** `.llmmat`, Material, expression graph, Substrate, HLSL, `.ush`, Custom node, `MaterialExpression`.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM Material** plugin | Install from Fab or copy from this repo to `Plugins/` |
| Enabled in editor | Edit → Plugins → AI → **LLM Material** → restart editor |

For Substrate materials, the project must have Substrate enabled in project settings. The skill body covers both legacy and Substrate paths.

---

## Quick Example

Ask the agent:

> "Give me an emissive cyan material with a pulsing Fresnel glow."

The agent produces a `.llmmat` file:

```json
{
  "version": "1.0",
  "name": "FresnelPulse",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "functions": [
    {
      "name": "PulseWave",
      "returnType": "float",
      "parameters": [
        { "name": "Time",  "type": "float" },
        { "name": "Speed", "type": "float", "defaultValue": "2.0" }
      ],
      "body": "return 0.5 + 0.5 * sin(Time * Speed);"
    }
  ],
  "nodes": [
    { "id": "time",  "type": "Time",                "properties": {} },
    { "id": "pulse", "type": "Custom",
      "properties": { "OutputType": "CMOT Float 1", "Code": "return PulseWave(Time, 2.0);" } },
    { "id": "fresnel", "type": "Fresnel",           "properties": { "Exponent": 3.0 } },
    { "id": "mult",    "type": "Multiply",
      "properties": { "A": { "node": "pulse" }, "B": { "node": "fresnel" } } },
    { "id": "cyan",    "type": "Constant3Vector",   "properties": { "Constant": [0.0, 1.0, 1.0] } },
    { "id": "emissive", "type": "Multiply",
      "properties": { "A": { "node": "cyan" }, "B": { "node": "mult" } } }
  ],
  "output": {
    "emissiveColor": { "node": "emissive", "pin": "Result" }
  }
}
```

Save it, open the LLM Material panel, click **Generate** — the `FresnelPulse` material appears.

---

## What the Skill Knows

The full skill body contains:

- **All expression node types** — Add, Multiply, TextureSample, Constant3Vector, Lerp, Fresnel, Time, Panner, Custom, etc. The agent reads the schema at `Plugins/LLMMaterial/Content/MaterialExpressionSchema.json` for the canonical list.
- **Connection rules** — which inputs accept which output types, when the agent needs an explicit `Custom` node, etc.
- **Output pins** — `baseColor`, `metallic`, `roughness`, `normal`, `emissive`, `opacity`, `worldPositionOffset`, etc.
- **Substrate** — modern UE5 material architecture (slab + node + sub-node model). The skill covers both legacy and Substrate authoring.
- **USH (HLSL functions)** — `functions[]` blocks generate `.ush` files; `ushIncludes[]` references existing ones; `Custom` nodes with `HeaderRef` call into them.
- **Examples** — full reference examples in `Plugins/LLMMaterial/Content/Examples/`.

---

## Compiling the JSON into an Asset

```
# Manual: editor panel
Tools → LLM Material Panel → select .llmmat file → Generate

# CLI (with llm-easy-shell installed)
material generate /Game/Materials/FresnelPulse --from FresnelPulse.llmmat
```

The generated Material asset opens in the Material Editor for further tuning.

---

## Round-Trip

Already have a Material you want to author against? Use the editor panel's **Export Material** button to dump the current state to a `.llmmat` file. The agent edits the file, you re-generate.

---

## Related Skills

- [**llm-easy-shell** →](./llm-easy-shell) — drive the editor from the CLI.
- [**llm-easy-shell-lite** →](./llm-easy-shell-lite) — read-only exploration: "what shader does this material use?"
