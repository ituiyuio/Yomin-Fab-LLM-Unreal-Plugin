---
name: llmmat-substrate-pipeline
description: LLMMaterial Substrate build pipeline — complete end-to-end verified with TPE material
type: reference
originSessionId: f503f7c1-d9dc-4e77-944e-7b6c8dd73019
---
# LLMMaterial Substrate Pipeline (Verified 2026-04-15)

## Complete Data Flow
```
.llmmat → ParseSubstrate() → FLLMSubstrateGraphDefinition
→ MaterialBuilder::Build() → ULLMMaterialRouter::Build()
→ ULLMSlabRouteHandler::BuildSlabGraph()
→ 18 nodes: 2× SubstrateSlabBSDF, 1× SubstrateVerticalLayering,
 1× SubstrateShadingModels, 14× Constant/Constant3Vector
→ ShaderCompiled: true ✅
```

## Valid .llmmat Substrate Inputs for UMaterialExpressionSubstrateSlabBSDF (UE5.7)
- DiffuseAlbedo, F0, F90, Roughness, Anisotropy
- Normal, Tangent
- SSSMFP, SSSMFPScale, SSSPhaseAnisotropy
- EmissiveColor
- SecondRoughness, SecondRoughnessWeight
- FuzzRoughness, FuzzAmount, FuzzColor

## INVALID (not on SubstrateSlabBSDF in UE5.7)
- `CoverAmount` → doesn't exist, silently ignored
- `Coverage` → only on UMaterialExpressionSubstrateWeight, not on Slab
- `TransmittanceColor` → on base class UMaterialExpressionSubstrateBSDF

## Architecture Files
- LLMMaterial/Core/LLMMaterialGraphTypes.h: FLLMSlabDefinition, FLLMSlabComposition, FLLMSubstrateGraphDefinition
- LLMMaterial/Core/LLMMaterialParser.cpp: ParseSubstrate, ParseSlab, ParseSlabInput
- LLMMaterial/Router/MaterialRouter.cpp: Route detection (Substrate/Traditional/Hybrid)
- LLMMaterial/Router/MaterialRouteHandler.cpp: ULLMSlabRouteHandler (full build pipeline)
- LLMMaterial/Builder/MaterialBuilder.cpp: bUseMaterialAttributes=true + UpdateCachedExpressionData

## Test Case
- `material generate /Game/Materials/M_TPESilicone_v6_AiCup --from D:/UnrealEngine/CODEO/Content/Materials/M_TPESilicone_v6_AiCup.llmmat`
- Result: `ShaderCompiled: true`, 17 nodes, 15 connections
