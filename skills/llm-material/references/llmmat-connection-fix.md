---
name: llmmat-connection-fix
description: MaterialGraphBuilder requires explicit Inputs arrays in custom node llmmat definitions
type: reference
originSessionId: 16776774-e009-47aa-b37a-9548c2fda7c3
---
# LLMMaterial DSL Connection Fix

## Root Cause
`MaterialGraphBuilder::CreateConnection()` (line 776) searches `CustomExpr->Inputs[i].InputName` for matching connection target pins. But `UMaterialExpressionCustom::Inputs` is only populated when the llmmat node definition has an explicit `Inputs` property array. The HLSL parameter names in the `Code` field do NOT auto-populate the Inputs array.

> [tool-fix-151 2026-06-29] doc-fossil line drift closure: `CreateConnection` line 658 → 776 (+118 drift). RootCause: 2026-04 ~2026-06 多次 PR 注入 helpers (HLSLParser/USHGenerator/Inputs-empty cleanup) 把 CreateConnection 从 L658 推到 L776。fix 保持 anchor 跟 cpp 实际 1:1 锁定。

## Fix
For every `Custom` type node in llmmat, explicitly define an `Inputs` array matching the HLSL parameter names:

```json
{ "id": "liquid_core", "type": "Custom", "properties": {
 "HeaderRef": "MyFunc",
 "OutputType": "CMOT_Float1",
 "Inputs": [
 { "InputName": "Normal" },
 { "InputName": "ViewDir" },
 { "InputName": "IOR" }
 ]
}}
```

## ALSO: Inputs Must Be Parsed BEFORE ProcessCustomNode
Bug found: `MaterialGraphBuilder::CreateExpressionNode()` called `ShaderGenerator->ProcessCustomNode()` BEFORE parsing the `Inputs` property, resulting in `return MyFunc(None, A, B, C);` (spurious first empty argument). Fix: move Inputs parsing before HeaderRef/ProcessCustomNode call. Also call `CustomExpr->Inputs.Empty()` first to clear UE's default empty input.

## ALSO: USHGenerator Filesystem Path
Bug found: `USHGenerator::Initialize()` set `ShaderOutputDir = "/Game/Shaders"` (UE content path, not filesystem path). Files were never written. Fix: `ShaderOutputDir = FPaths::Combine(FPaths::ProjectContentDir(), TEXT("Shaders"))`.

## Affected Files
- `<ProjectDir>/Content/Materials/MyGlassMaterial_Complete.llmmat` — recreated with all Inputs arrays
- `<ProjectDir>/Content/Materials/MyGlassMaterial_Advanced.llmmat` — already had Inputs arrays (correct)
- `Plugins/LLMMaterial/Source/LLMMaterial/Builder/MaterialGraphBuilder.cpp` — Inputs-first ordering, Inputs.Empty() before adding
- `Plugins/LLMMaterial/Source/LLMMaterial/Builder/USHGenerator.cpp` — filesystem path fix

## Also Fixed
> 以下 3 项发生在 **host project 侧**（消费 LLMMaterial 的那个工程自己的玻璃材质模块），不在 LLMMaterial 插件内 —— 列在这里只为记录当时的连带修复。

- The host project's `GlassMaterialLayer::UpdateBaseParameters()` hardcoded DeepColor instead of using `OpticalConfig.DeepColor`
- Added `DeepColor` field to the `FLiquidGlassOptical` struct in `LiquidGlassTypes.h`
- Updated the default material path to the "Complete" variant in both `LiquidGlassComponent.cpp` and `GlassMaterialLayer.cpp`
