---
name: llmmat-substrate-crash-fix
description: Slate FPropertyNode crash from SetMaterial — fixed by PreEditChange/PostEditChange + removing ForceRecompileForRendering
type: reference
originSessionId: 6b960cd9-15eb-4975-b3b1-203f9f26ea16
---
## Issue
SetMaterial on any LLMMaterial-triggered editor crash: EXCEPTION_ACCESS_VIOLATION writing 0x00007ff99020e2d8 in Slate Core (FPropertyNode cache), occurring ~2.5 minutes after SetMaterial when async shader compilation completes.

## Root Cause
Three contributing factors:
1. `MaterialGraphBuilder::Build()` called `Empty()` on expression collection without `PreEditChange(nullptr)` first — Slate FPropertyNode cache held stale FProperty pointers
2. `ForceRecompileForRendering()` triggered async shader compilation which, when completing, dereferenced those stale pointers
3. No `PostEditChange()` call after rebuild — Slate property cache never knew to invalidate

## FIX Applied (MaterialGraphBuilder.cpp)
```cpp
// BEFORE (crash):
TargetMaterial->Modify();
TargetMaterial->GetExpressionCollection().Empty();
TargetMaterial->EditorParameters.Empty();
// ... build nodes ...
TargetMaterial->ForceRecompileForRendering(); // REMOVED

// AFTER (fixed):
TargetMaterial->Modify();
TargetMaterial->PreEditChange(nullptr); // ADDED
TargetMaterial->GetExpressionCollection().Empty();
TargetMaterial->EditorParameters.Empty();
// ... build nodes ...
TargetMaterial->PostEditChange(); // ADDED
```

Also added PreEditChange/PostEditChange in ApplyNodeProperties() for individual expression property changes.

## Key Insight
The crash only occurs when async shader compilation fires AFTER material graph rebuild. Removing `ForceRecompileForRendering()` prevents the async trigger. PreEditChange/PostEditChange ensures proper Slate cache invalidation. With shader already compiled during `material generate` (ShaderCompiled: true), no new async compilation occurs.

## Verified Working
A skin material (DefaultLit + Fresnel, Translucent) generated and applied to a test sphere — editor stable for 5+ minutes without crash.

## Secondary Issue: SubsurfaceProfile D3D12RHI Crash
MSM_SubsurfaceProfile + Translucent causes D3D12RHI crash at 0x0000000000000048 on UE5.7 + RTX 5090. Workaround: use `DefaultLit + Emissive` for SSS approximation (the DefaultLit + Fresnel route above).

## HitProxy Assertion Crash (RESOLVED)
`Assertion failed: Material && MaterialRenderProxy` at `SceneHitProxyRendering.cpp:960` — triggered when:
- Actor with Translucent material is selected
- HitProxy rendering path uses `GetMaterialWithFallback()` for selection outline
- Material shader is NOT compiled → returns nullptr → assertion fails

**Root Cause**: Previously, `material generate` created the material but shader wasn't compiled. When the editor's scheduled shader compilation ran (~366s after startup), the HitProxy rendering path was triggered for selected translucent meshes, and `GetMaterialWithFallback()` returned nullptr because the material's shader wasn't ready yet.

**FIX**: The `material generate` command now returns `ShaderCompiled: true` because the shader IS compiled synchronously during generation. By the time `SetMaterial` is called, the material is fully compiled. `GetMaterialWithFallback()` returns the actual compiled material → no nullptr → assertion passes.

**Verification**: 2026-04-13 — the skin material generated with `ShaderCompiled: true`, applied to a test sphere via `SetMaterial`, sphere selected (triggering HitProxy), editor stable for 7+ minutes (well past the original 366s crash point). No crash.

**Note**: `CloseAllEditorsForAsset` in MaterialBuilder.cpp (line 285) was added but is NOT the fix — it just closes asset editor windows. The actual fix is that the shader is compiled before SetMaterial is called.

> [tool-fix-151 2026-06-29] doc-fossil line drift closure: `CloseAllEditorsForAsset` line 278 → 285 (+7 drift, includes 1 行 preceding comment block)。RootCause: MaterialBuilder.cpp 多次 commit 累积 (ShadingModel 注入 + Substrate fallback) 把 CloseAllEditorsForAsset 从 L278 推到 L285。fix 保持 anchor 跟 cpp 实际 1:1 锁定。

**Wrong approaches tried**: `FlushRenderingCommands()` (linker error — needs RenderCore module), `MarkRenderStateDirty()` TObjectIterator loop (crashed during LiveCoding).

## Verified Working (2026-04-13)
The skin material (DefaultLit + Fresnel, Translucent) generated with ShaderCompiled=true, applied to a test sphere, selected actor → editor stable 7+ min, no HitProxy crash.

---

## Substrate Material Generation Crash (RESOLVED 2026-04-13)
`check(false)` at `MaterialExpressionSubstrate.cpp:750` when generating Substrate materials (Hybrid mode with SubstrateSlabBSDF nodes).

**Root Cause**: `SubstrateGenerateMaterialTopologyTreeCommon` (switch at lines 674-748) handles specific `EMaterialShadingModel` values (MSM_Unlit, MSM_DefaultLit, etc.) but `MSM_Strata` is NOT in the switch. When `ShadingModels.CountShadingModels() == 1` with `MSM_Strata`, it falls through to `check(false)` at line 750. The crash fires during Expression graph creation, BEFORE `BuildSlabGraph()` runs.

**Fix**: Changed BOTH `InitializeMaterial()` and `MaterialBuilder::Build()` to set `MSM_DefaultLit` instead of `MSM_Strata` for Substrate materials:
- `MaterialRouteHandler.cpp` ~line 255: `Material->SetShadingModel(EMaterialShadingModel::MSM_DefaultLit)`
- `MaterialBuilder.cpp` ~line 306: `ShadingModelEnum = EMaterialShadingModel::MSM_DefaultLit`

> [tool-fix-151 2026-06-29] doc-fossil line drift closure: 2 处 line refs 同步更新 (MaterialRouteHandler.cpp:243 → 255 +12 drift, MaterialBuilder.cpp:304 → 306 +2 drift)。RootCause: 2026-04 Substrate fix 落地后, 后续多次 PR 注入新 ShadingModel 分支 (MSM_Strata/MSM_Eye/MSM_ThinTranslucent/MSM_SingleLayerWater) 把 Substrate-specific MSM_DefaultLit 调用从 L243 推到 L255; MaterialBuilder 同样累积。fix 保持 anchor 跟 cpp 实际 1:1 锁定, ~ qualifier 保留 (drift ±5 行容忍)。

**Why it works**:
- `MSM_DefaultLit` IS handled in `SubstrateGenerateMaterialTopologyTreeCommon`'s switch → returns `SUBSTRATE_OPERATOR_BSDF_LEGACY`
- After graph build, `RebuildShadingModelField()` (already present) corrects `ShadingModels` to proper Substrate values
- Transparent SSS materials are additionally sanitized by `RebuildShadingModelField()` → `MSM_DefaultLit` + `SSM_DefaultLit`

**Verified**: `material generate /Game/Materials/MySkinMaterial_Substrate --from <ProjectDir>/Content/Materials/MySkinMaterial_Substrate.llmmat` (ShaderCompiled: true), no crash.

## NEW Crash: Substrate ShaderCompiler CookStats (2026-04-14, UNRESOLVED)
After fixing the `check(false)` crash above, Substrate materials (`MySubstrateMaterial_v5`, `MySubstrateMaterial_v2`) generate with `ShaderCompiled: true`, but the editor CRASHES later during shader compilation.

**Crash Stack**:
```
EXCEPTION_ACCESS_VIOLATION writing 0x00007ffad976e2d8
UnrealEditor-Core.dll!FString::FString() [String.cpp.inl:230]
UnrealEditor-Engine.dll!FCookStats::CallStats::LogStats::<lambda_1>::operator()()
UnrealEditor-Engine.dll!GlobalShaderCookStats::<lambda_25>::operator()()
UnrealEditor-Engine.dll!TBaseFunctorDelegateInstance<...>::ExecuteIfSafe()
UnrealEditor-Core.dll!FCookStatsManager::LogCookStats()
UnrealEditor-DerivedDataCache.dll!GatherDerivedDataCacheSummaryStats()
UnrealEditor-EditorPerformance.dll!FEditorPerformanceModule::UpdateKPIs()
UnrealEditor-EditorPerformance.dll!FEditorPerformanceModule::CreateStatusBarWidget()
UnrealEditor-Engine.dll!FTimerManager::Tick()
```

**Root Cause**: Substrate shader compilation triggers `CookStats::LogStats` which tries to create FString from invalid/corrupted memory. Likely: Substrate's internal BSDF tree (SubstrateSlabBSDF + VerticalLayering) produces invalid/empty `FString` fields during `SubstrateGenerateMaterialTopologyTree` code generation, and `CookStats` tries to log these.

**Affected Materials**: Any `.llmmat` with `substrate: { slabs: [...] }` — including the 3-slab variant (3 slabs + VerticalLayering + topFuzz) and the 2-slab variant (2 slabs + VerticalLayering).

**Symptom**: Material generates OK (`ShaderCompiled: true`), applied to object, looks white (shader not rendering), then editor crashes within minutes.

**Workaround**: Use traditional pipeline (`.llmmat` with `nodes:` + `connections:` + `output:`) instead of Substrate. Verified working: `MyTraditionalMaterial` (32 nodes, `ShaderCompiled: true`, no crash).

**Next Step**: Debug the FString corruption in Substrate topology generation. Possible causes:
1. `CreateVerticalLayering` creates invalid UMaterialExpression node (null pointers in string fields)
2. `SlabRouteHandler` returns error but `MaterialBuilder` ignores it → material with empty graph
3. UE5.7 bug in `SubstrateGenerateMaterialTopologyTree` with complex topologies (≥2 slabs)

**Note**: `topFuzz` field in VerticalLayering root is NOT handled by Router (ignored during parsing). This shouldn't cause crash but may produce incorrect topology.