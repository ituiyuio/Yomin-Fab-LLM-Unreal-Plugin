---
name: llmmat-nanite-crash
description: LLMMaterial Substrate material save crash - NaniteVF assertion
type: reference
originSessionId: f503f7c1-d9dc-4e77-944e-7b6c8dd73019
date: 2026-04-19
---
# Substrate + Nanite Crash (LLMMaterial Bug)

## Symptom
Assertion failed on material save: `ShaderMapId.ContainsVertexFactoryType(FNaniteVertexFactory)`
崩溃调用栈：`MaterialShader.cpp:2532` → `SubmitCompileJobs` → `GenerateThumbnailForObjectToSaveToDisk`

## Root Cause
`MaterialBuilder.cpp` 第 430-433 行对 Substrate 材质设置 `bUsedWithNanite = false`（修复前原行为是 `bUsedWithNanite = true`，已替换；`bUsedWithNanite = true` 触发 ShaderMapId 断言崩溃）。
同时材质有 `NaniteOverrideMaterial.bEnableOverride = True`（UMaterial 默认值）。
两者组合触发 UE 断言：shader map 没有 FNaniteVertexFactory 但期望有。

## Fix
`Plugins/LLMMaterial/Source/LLMMaterial/Builder/MaterialBuilder.cpp` 第 430-433 行：
```cpp
// 禁用 Nanite（Substrate + Nanite 在 UE5.7 会触发 ShaderMapId NaniteVF 断言崩溃）
if (GraphDefinition.Substrate.HasSlabs())
{
 Material->bUsedWithNanite = false; // 原为 true
 UE_LOG(LogTemp, Log, TEXT("MaterialBuilder: Set bUsedWithNanite=false for Substrate material..."));
}
```
Substrate 材质在 UE5.7 下不应启用 Nanite。

## Verification
- M_TPESilicone_v8_AiCup 重新生成后保存成功，无崩溃
- 2026-04-19
