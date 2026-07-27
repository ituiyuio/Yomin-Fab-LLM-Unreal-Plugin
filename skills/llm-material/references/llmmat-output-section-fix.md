---
name: llmmat-output-section-fix
description: LLMMaterial export pipeline missing output: section — two bugs fixed: FLLMMaterialOutput::IsValid() too strict, and SerializeMaterialOutputs not capturing PinName
type: reference
originSessionId: a275a0a9-d449-4494-9ddf-61412cd2ed92
---

# LLMMaterial Export output: Section Fix

## Root Cause 1: `FLLMMaterialOutput::IsValid()` Required PinName
`FLLMMaterialOutput::IsValid()` returned `bUseNode ? (!NodeId.IsEmpty() && !PinName.IsEmpty()) : ...` — it required BOTH `NodeId` AND `PinName`. But `SerializeMaterialOutputs` always called `FromNode(NodeId, TEXT(""))` with empty `PinName`. Result: all outputs were silently discarded by the `IsValid()` gate in `GraphDefinitionToJson`'s `SetOutput` lambda.

## Root Cause 2: SerializeMaterialOutputs Didn't Capture PinName
The lambda originally returned only `UMaterialExpression*`. Without access to `FExpressionInput`, it couldn't get `OutputIndex` → couldn't resolve the actual output pin name.

## Fix 1: Relax `IsValid()` — LLMMaterialGraphTypes.h
Changed to `return !NodeId.IsEmpty();` — PinName may be empty (builder uses default output). The `SetOutput` lambda in `GraphDefinitionToJson` already handles empty `PinName` gracefully (just omits the "pin" key in JSON).

## Fix 2: Capture PinName via `FExpressionInput::OutputIndex` — LLMMaterialSerializer.cpp
- Changed lambda return type from `TPair<UMaterialExpression*, FString>` to a local `FPropertyInput` struct with `{Expression, PinName, ConstantValue, bHasConstant}`
- Primary path: direct `EditorOnlyData->Property.Expression` + `OutputIndex` → `Expression->Outputs[OutputIndex].OutputName`
- Fallback 1: `UMaterialEditingLibrary::GetMaterialPropertyInputNode`
- Fallback 2: `Material::GetExpressionsInPropertyChain`
- When no expression connected: use UE material property defaults (Metallic=0, Specular=0.5, Opacity/OpacityMask=1.0)

## Affected Files
- `LLMMaterialGraphTypes.h` — `IsValid()` now only requires NodeId
- `LLMMaterialSerializer.cpp` — `SerializeMaterialOutputs` captures PinName from OutputIndex, handles constant defaults
- `MaterialExportCommand.cpp` — added debug logging for output section

## Export Result (M_TPESilicone_v4)
```json
"output": {
 "baseColor": { "node": "Lerp_1_25", "pin": "Result" },
 "metallic": 0,
 "roughness": { "node": "Clamp_2_17", "pin": "Result" },
 "specular": 0.5,
 "emissive": { "node": "Multiply_21_31", "pin": "Result" },
 "opacity": 1,
 "opacityMask": 1
}
```

## Known Limitation
`SetupOutput` in `MaterialGraphBuilder` does NOT implement constant output setting (line 1214-1216 logs `EditorOnlyData is nullptr` warning + line 1221 `switch (Property)` handles node-based routing; no constant output setting branch). Round-trip import of `.llmmat` with constant output values won't restore them — material will use UE defaults. Node-based outputs are fully connected correctly.

> [tool-fix-151 2026-06-29] doc-fossil line drift closure: `SetupOutput` claim "line 1216-1221 logs warning" → 实际 L1214-1216 warning + L1221 switch Property。RootCause: 2026-04 ~2026-06 FProperty system 注入 (FName PropertyName lookup) 把 `switch (Property)` 从 L1216 推到 L1221, 中间插入 PropertyName 解析 block (L1218-1220)。fix 保持 anchor 跟 cpp 实际 1:1 锁定。
