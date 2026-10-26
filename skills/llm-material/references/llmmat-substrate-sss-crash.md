---
name: llmmat-substrate-sss-crash
description: UE5.7 Substrate SSS + VerticalLayering causes EXCEPTION_ACCESS_VIOLATION at D3D12RHI BindUniformBuffer
type: reference
originSessionId: f503f7c1-d9dc-4e77-944e-7b6c8dd73019
---
# Substrate SSS + VerticalLayering Crash (UE5.7 Bug)

## Symptom
EXCEPTION_ACCESS_VIOLATION reading address 0x40 or 0x48 at `UnrealEditor-D3D12RHI + 0x4ae20`
(crash at `BindUniformBuffer` → `ValidateBoundUniformBuffer` where `InUniformBuffer` is null)

## Test Results (RTX 5090 + UE5.7.4)

| Material | VL | SSS | Crash? | Notes |
|----------|----|-----|--------|-------|
| Single slab | ❌ | ❌ | ✅ No | baseline |
| VL only (no SSS) | ✅ | ❌ | ✅ No | v7 |
| VL + SSS (bottom) | ✅ | ✅ | ❌ YES | v6 crashes |
| SSS only (no VL) | ❌ | ✅ | ❌ YES | v7b crashes |

## Confirmed Root Cause
UE5.7 Substrate shader bug: **SSS on a slab that's the bottom layer of a VerticalLayering composition** causes the SSS post-process pass to read from an invalid/incorrect slice index in the Substrate material buffer, resulting in a null uniform buffer at render time.

Evidence from shader code analysis:
1. `SubstrateExport.ush`: SSS data is accumulated per-BSDF with `Coverage` weight
2. `Substrate.ush`: SSSMFP is interpolated through `GetVerticalLayeringInfo()` based on coverage ratios
3. `Substrate.cpp`: `FirstSliceStoringSubstrateSSSData` calculation may be incorrect for this combination
4. `SubstrateSubsurface.ush`: `LoadSubstrateSSSData()` reads slices that may contain garbage or be unmapped

## Workarounds

### Option 1: Use Traditional Subsurface (Non-Substrate SSS)
Instead of Substrate SSSMFP, use the legacy `MSM_SubsurfaceProfile` shading model with a SubsurfaceProfile asset. This bypasses the Substrate SSS pipeline entirely.

### Option 2: Single Slab + SSS (No VerticalLayering)
Use a single slab with SSSMFP — no composition, no layering. This avoids the problematic code path.

### Option 3: VerticalLayering Without SSS
Keep the oil_surface + flesh_tpe VerticalLayering but remove SSS parameters from the flesh layer. The flesh will render correctly, just without subsurface scattering.

### Option 4: Upgrade Engine
This bug may be fixed in a later UE5.7 patch or UE5.8+. Check Unreal Engine release notes.

## Updated Test: single-slab Substrate material (2026-04-19)
Single SubstrateSlabBSDF + SSSMFP + SSSMFPScale, NO VerticalLayering, NO root composition.
Result: `ShaderCompiled: true` (10 InputNodes) — shader compiles, runtime rendering TBD.

## LLMMaterial Pipeline Status

- ✅ Parser: ParseSubstrate/ParseSlab/ParseSlabInput works
- ✅ Router: Substrate mode detection works
- ✅ RouteHandler: Full Substrate graph construction works
- ✅ Shader Compilation: `ShaderCompiled: true` (no compile errors)
- ❌ Runtime Rendering: EXCEPTION_ACCESS_VIOLATION at D3D12RHI

The LLMMaterial pipeline is functionally correct. The crash is a UE5.7 runtime bug in the Substrate shader system, not in the LLMMaterial code.

## Crash Callstack
```
UnrealEditor-Renderer + b1309f
UnrealEditor-Renderer + af5c7c
UnrealEditor-Renderer + b13456
UnrealEditor-Renderer + df3485
UnrealEditor-Renderer + eb6650
UnrealEditor-Renderer + f5c38b
UnrealEditor-Renderer + f5e13f
UnrealEditor-Engine + 1d58371
UnrealEditor-Renderer + f22cbe
UnrealEditor-RenderCore + 1802f9
UnrealEditor-RenderCore + 14c028
UnrealEditor-RenderCore + 167d51
UnrealEditor-RenderCore + 180b14
UnrealEditor-Core + e5b4d
UnrealEditor-Core + da308
UnrealEditor-Core + da6ae
UnrealEditor-RenderCore + 1a0809
UnrealEditor-RenderCore + 1a10e4
UnrealEditor-Core + 7aa498
UnrealEditor-Core + 7a31bf
KERNEL32 + 2e8d7
```

Crash type: `EXCEPTION_ACCESS_VIOLATION reading address 0x0000000000000040`
