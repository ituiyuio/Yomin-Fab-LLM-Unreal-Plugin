---
name: ue55-material-api-survey-2026-06-17
description: "UE 5.5/5.6/5.7 Material API 跨版本调查汇总 — SubsurfaceProfile.Implementation / 命名空间 / enum 变化 / UMaterial 字段 — 用于 LLMMaterial Fab multi-UE 兼容性补丁"
metadata:
 node_type: memory
 type: reference
 originSessionId: 430031d1-8356-4aa6-9aa7-b8861d9e7338
---

# UE 5.5/5.6/5.7 Material API 跨版本调查汇总 (2026-06-17)

为支撑 LLMMaterial 插件在 UE 5.5/5.6/5.7 三个 Fab 引擎版本上的 clean-build,
对 Material 域 API 做了四组系统化调查。以下是综合发现。

## 0. RM_IndexOfRefractionFromF0 (5.7 only, **不是 5.6+**)

| UE | `ERefractionMode::RM_IndexOfRefractionFromF0` | 来源 |
|---|---|---|
| 5.5 | **不存在** | grep 0 匹配 |
| 5.6 | **不存在** ⚠️ 5.6 也没有! (2026-06-17 实测: 误用 `#if >= 5.6` 包裹 → 5.6 编译报 C2838/C2065 找不到 enum) | grep 0 匹配 |
| 5.7 | **新增** | `Engine/Classes/Engine/EngineTypes.h:392` |

**关键陷阱**:`RM_IndexOfRefractionFromF0` 是 **5.7 only**,不是 5.6+。跨版本保护必须用 `#if ENGINE_MINOR_VERSION >= 7`,5.5/5.6 都要跳过。LLMMaterial 1.1.0 修错过一次(原来 `#if >= 5.6` 触发 5.6 编译失败),正确是 `#if >= 5.7`。

## 1. SubsurfaceProfile.Implementation (5.6 新增)

| UE | `FSubsurfaceProfileStruct::Implementation` | 类型 | 来源 |
|---|---|---|---|
| 5.5 | **不存在** | — | `Engine/Classes/Engine/SubsurfaceProfile.h` grep 0 匹配 |
| 5.6 | **新增** | `ESubsurfaceImplementationTechniqueHint` | 同文件 line 98-102 |
| 5.7 | **保留** | 同上 | line 98-102 |

5.6/5.7 枚举值:`SIH_AFIS` / `SIH_Separable`,默认 `SIH_AFIS`。

**跨版本写法(必须条件编译):**
```cpp
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 Profile->Settings.Implementation = ESubsurfaceImplementationTechniqueHint::SIH_AFIS;
#else
 Profile->Settings.bEnableBurley = true; // 5.5 唯一能调的字段
#endif
```

5.5 想控制 AFIS 行为只能走控制台变量 `r.SSS.Burley.Quality` / `r.SSS.HalfRes` /
`r.SSS.HalfRes.ForceSeparable`(由 5.6 头文件注释 line 17 引用)。

## 2. Material 相关命名空间

| 命名空间 | 5.5 | 5.6 | 5.7 | 引入版本 |
|---|---|---|---|---|
| `UE::MaterialInterface` | 存在 | 存在 | 存在 | 至少 5.5 之前 |
| `UE::MaterialInterface::Private::SerializeInlineShaderMaps` | 存在 | 存在 | 存在 | 至少 5.5 之前 |
| `UE::MaterialTranslatorUtils` | **不存在** | **不存在** | **新增** | **5.7** |
| `UE::Substrate` | 不存在 | 不存在 | 不存在 | N/A |
| `UE::MaterialX` | 不存在 | 不存在 | 不存在 | N/A |

5.7 新增的 `UE::MaterialTranslatorUtils` 在 5.5/5.6 完全无符号,任何引用都要 `#if >= 5.7` 保护。
Substrate 在源码中**只走类型/字段前缀路线**,没有 namespace 封装。

`UE::MaterialInterface::Private` 内部成员(`SerializeInlineShaderMaps`)三版签名一致,可直接调用;
其他内部符号稳定性不保证,优先走 UMaterial/UMaterialInterface 公共 API。

## 3. Material enum 跨版本变化

### 不变的 enum(三版完全相同,无需 #if 保护)
- `EBlendMode` (含 `BLEND_TranslucentColoredTransmittance` Substrate only)
- `EMaterialShadingModel` (含 `MSM_Strata` Hidden)
- `EMaterialProperty` (含 `MP_ShadingModel`,**不是 `MP_ShadingModelType`**)
- `ESubstrateShadingModel`
- `EMaterialDomain`
- `EMaterialFloatPrecisionMode`
- `EMaterialSamplerType`
- `EMaterialShadingRate`
- `ECompiledMaterialProperty` / `ECompiledPartialDerivativeVariation`
- `EMaterialTextureParameterType`
- `ELWCFunctionKind` / `EMaterialCommonBasis` / `EDeferredParamStrictness`

### 5.6 新增的 enum
- `EMaterialTranslateValidationFlags` (in `MaterialShared.h` line 1828, 5.7 line 1905)
 ```cpp
 enum class EMaterialTranslateValidationFlags : uint32 {
 None = 0,
 Strict_RuntimeVirtualTexture = 1 << 0,
 };
 ```

### EMaterialValueType 跨版本剧烈变化(关键!)

| 版本 | 底层类型 | 新增值 |
|---|---|---|
| 5.5 | `int` (32-bit) | — |
| 5.6 | **`uint64`** | `MCT_TextureMaterialCache` |
| 5.7 | `uint64` | + `MCT_Float3x3`, `MCT_Float4x4`, `MCT_LWCMatrix`, `MCT_MaterialCacheABuffer`, `MCT_Unexposed` |

**5.6 底层类型 int → uint64 隐式转换/截断风险高**:
```cpp
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 using FMaterialValueTypeBits = uint64;
#else
 using FMaterialValueTypeBits = int32;
#endif
```

## 4. UMaterial 字段跨版本差异 (核心)

### 5.5 独有,5.6 移除
- `bMobileEnableHighQualityBRDF` (line 865 in 5.5)
- `ExpressionExecBegin_DEPRECATED` (单数 TObjectPtr,5.7 完全删除)
- `ExpressionExecEnd_DEPRECATED` (同上)
- `OverrideNumericParameterDefault` (5.7 拆分为 Set/Clear)
- `GetUsedTextures` 5 参数签名 (5.7 改为 TOptional 2 参数)
- `GetMaterialResource(ERHIFeatureLevel::Type,...)` (5.7 改用 EShaderPlatform)
- `IsCompilingOrHadCompileError(ERHIFeatureLevel::Type)` (5.7 弃用 + 加 ShaderPlatform 重载)
- `FColorMaterialInput::Constant` 类型 `FColor` (5.6 改 FLinearColor,二进制兼容)
- `bUsedWithMaterialCache` (5.6 短暂存在,5.7 又删)

### 5.6 新增(5.5 不存在)
- `SubstrateVersion` (UMaterialEditorOnlyData)
- `bIsSubsutrateAutoConvertedAndNotSaved` (注意源码拼写错误 Sub**s**utrate)
- `IsSubstrateAutoConverted()`
- `bSubstrateRoughnessTracking` (UMaterial 主体)
- `HasSubstrateRoughnessTracking() const`
- `UserRequestsConvertMaterialToSubstrateMaterial()`
- `bCompatibleWithLumenCardSharing` + `IsCompatibleWithLumenCardSharing()`
- `bIsTranslucencyVelocityFromDepth` / `IsTranslucencyVelocityFromDepth()` override
- `bAllowTranslucentLocalLightShadow` / `TranslucentLocal/DirectionalLightShadowQuality`
- `bUsedWithStaticMesh`
- `bRelaxRuntimeVirtualTextureRestrictions[ForOldContent]`
- `OnCookEvent(...)` override
- `SyncLayersRuntimeGraphCache(...)` override
- `GetShaderTags` / `GetMaterialTranslateValidationFlags` / `AppendCompileStateDebugInfo`
- `enum class EMaterialTranslateValidationFlags` 前向声明
- UMaterial 改用现代显式构造函数(替代 `GENERATED_UCLASS_BODY()`)
- `bEnableExecWire` 标记 `UE_DEPRECATED(5.8, ...)`(5.8 移除)
- `ConvertMaterialToSubstrateMaterial` 增加 `bRequestedByUser` 参数

### 5.7 新增(5.5/5.6 不存在)
- `bUsedWithVoxels` (Nanite voxel meshes,5.7 独有)
- `IsMobileSeparateTranslucencyEnabled() const`
- `GetSubsurfaceProfileRoot_Internal()` 无参重载
- `bCachingUniformExpressions` private mutable
- `StartCacheUniformExpressions / FinishCacheUniformExpressions`
- `SetNumericParameterDefault / ClearNumericParameterDefault` override
- `IsCompilingOrHadCompileError(EShaderPlatform)` 重载
- `bRootNodeOverridesDefaultDistortion` 改名为 `..._DEPRECATED` 后缀
- `FMaterialsWithDirtyUsageFlags::IsDefault()` 从 `FORCEINLINE` 改 `inline`

## 5. 跨版本代码保护模式汇总

```cpp
#include "Misc/EngineVersionComparison.h"

// Substrate 5.6+ 字段
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 Material->bSubstrateRoughnessTracking = false;
 Material->GetEditorOnlyData()->SubstrateVersion; // 5.5 无此字段
#endif

// bUsedWithVoxels 仅 5.7+
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 FProperty* Prop = Material->GetClass()->FindPropertyByName(TEXT("bUsedWithVoxels"));
#endif

// bMobileEnableHighQualityBRDF 仅 5.5
#if ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION == 5
 Material->bMobileEnableHighQualityBRDF = true;
#endif

// GetUsedTextures 签名变化
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 Material->GetUsedTextures(OutTextures);
#else
 Material->GetUsedTextures(OutTextures, EMaterialQualityLevel::Num, true,
 ERHIFeatureLevel::Num, true);
#endif

// GetMaterialResource 5.7 切换
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 FMaterialResource* R = Material->GetMaterialResource(EShaderPlatform, QualityLevel);
#else
 FMaterialResource* R = Material->GetMaterialResource(ERHIFeatureLevel::Num, EMaterialQualityLevel::Num);
#endif

// IsCompilingOrHadCompileError 5.7 弃用旧重载
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 if (Material->IsCompilingOrHadCompileError(EShaderPlatform)) { ... }
#else
 if (Material->IsCompilingOrHadCompileError(ERHIFeatureLevel::Num)) { ... }
#endif

// OverrideNumericParameterDefault 5.7 拆分
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 Material->SetNumericParameterDefault(Type, Info, Value, EShaderPlatform);
 Material->ClearNumericParameterDefault(Type, Info, EShaderPlatform);
#else
 Material->OverrideNumericParameterDefault(Type, Info, Value, bOverride, ERHIFeatureLevel::Num);
#endif

// bEnableExecWire 5.6 起 deprecation warning
PRAGMA_DISABLE_DEPRECATION_WARNINGS
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION <= 7
 Material->bEnableExecWire = false;
#endif
PRAGMA_ENABLE_DEPRECATION_WARNINGS

// bRootNodeOverridesDefaultDistortion 5.7 改名
FProperty* Prop = Material->GetClass()->FindPropertyByName(
 ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 ? TEXT("bRootNodeOverridesDefaultDistortion_DEPRECATED")
 : TEXT("bRootNodeOverridesDefaultDistortion"));
```

## 6. 通用建议

- **不要硬编码访问 bUsedWith* 字段**:三个版本 bUsedWith* 字段集变动频繁,统一走
 `FindPropertyByName` + `ContainerPtrToValuePtr<bool>` 反射最稳。
- **EMaterialValueType 必须用 uint64** 跨版本统一,5.5 用 int32 仅在 5.5 内部用,跨版本比较时强转 uint64。
- **5.5 → 5.6 是 Substrate / Lumen / Translucency 增强主战场**;5.7 主要是渲染管线现代化
 (ERHIFeatureLevel → EShaderPlatform)。
- **DEPRECATED 字段命名风格变化**:5.5 多用独立名字,5.7 出现 `原名_DEPRECATED` 后缀,
 反射代码需兼容两种风格。

## 7. 关键源文件路径

- `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Public/Materials/Material.h`
- `C:/Program Files/Epic Games/UE_5.6/Engine/Source/Runtime/Engine/Public/Materials/Material.h`
- `C:/Program Files/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Public/Materials/Material.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/MaterialShared.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/MaterialValueType.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Classes/Engine/SubsurfaceProfile.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Classes/Engine/EngineTypes.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/SceneTypes.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialInterface.h`
- `C:/Program Files/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Private/Materials/MaterialShared.cpp` (UE::MaterialTranslatorUtils 定义,line 5939)

---

## 8. 扩展调查 — 任务 #12 (2026-06-17 续)

任务 #10 已覆盖的 enum 列表(避免重复):
EMaterialProperty / EBlendMode / EMaterialShadingModel / ESubstrateShadingModel /
EMaterialDomain / EMaterialFloatPrecisionMode / EMaterialSamplerType /
EMaterialShadingRate / ECompiledMaterialProperty / ECompiledPartialDerivativeVariation /
EMaterialTextureParameterType / ELWCFunctionKind / EMaterialCommonBasis /
EDeferredParamStrictness / EMaterialValueType / EMaterialTranslateValidationFlags

### 8.1 任务 #10 遗漏的 enum 调查结论

| Enum | 5.5 | 5.6 | 5.7 | 关键差异 |
|---|---|---|---|---|
| **EFallbackPrecision** | 不存在 | 不存在 | 不存在 | 旧名,5.5+ 用 `EMaterialFloatPrecisionMode` |
| **EStrataShadingModel** | 不存在 | 不存在 | 不存在 | 5.0+ 统一为 `ESubstrateShadingModel` |
| **EMaterialParameterType** | `MaterialTypes.h:184` | `MaterialTypes.h:185` | **`Materials/MaterialParameters.h:186`** | 5.7 头文件迁移 + **新增 `ParameterCollection` 值** |
| **EMaterialParameterAssociation** | `MaterialTypes.h:23` | `MaterialTypes.h:23` | `Materials/MaterialParameters.h:24` | 头文件迁移,值集不变 (Layer/Blend/Global) |
| **EMaterialFunctionUsage** | `MaterialFunctionInterface.h:32` | 同(31) | 同(32) | 值集不变;5.5 字段无默认,5.6+ 默认 `Default` |
| **EMaterialAttributeBlend** | `MaterialExpressionBlendMaterialAttributes.h:13` | 同 | 同 | 值集不变 (Blend/UseA/UseB) |
| **EMaterialSceneAttributeInputMode** | `MaterialExpressionSceneColor.h:13` | 同 | 同 | 值集不变 (Coordinates/OffsetFraction) |
| **ETranslucencyLightingMode** | `EngineTypes.h:310` | `EngineTypes.h:312` | `EngineTypes.h:313` | 值集不变 (TLM_*) |
| **EDecalBlendMode** | `Material.h:72` | `Material.h:73` | `Material.h:73` | 值集不变 (DBM_*) |
| **EFunctionInputType** | `MaterialExpressionFunctionInput.h:18` | 同 | 同 | 值集不变;**5.7 全部加 `UMETA(DisplayName)`** |
| **ECustomMaterialOutputType** | `MaterialExpressionCustom.h:16` | 同 | 同 | 值集不变 (CMOT_*) |
| **EMaterialExposedTextureProperty** | `MaterialExpressionTextureProperty.h:16` | 同 | 同 | 值集不变 (TMTM_*) |
| **EBlendableLocation** | `EngineTypes.h` | 同 | 同 | 值集不变 (BL_*) |
| **FMaterialAttributeDefintion** (typo) | `MaterialAttributeDefinitionMap.h` | 同 | 同 | UE 长期保留 typo,跨版本一致 |
| **EParameterAccessMode** | 不存在 | 不存在 | 不存在 | 无替代,使用材质实例 API |
| **EFlattenMaterialProperties** | 不存在 | 不存在 | 不存在 | 无替代,使用 MaterialAttributeLayers |
| **EAlphaBlendingMode** | 不存在 | 不存在 | 不存在 | 用 `bUseAlphaToCoverage` bool |
| **EAlphaCompositeMode** | 不存在 | 不存在 | 不存在 | 用 UMaterial bool 字段 |
| **EMaterialTranslucencyPass** / **ETranslucencyPass** | 不存在 | 不存在 | 不存在 | 无对应 enum |
| **EMaterialFunctionKind** | 不存在 | 不存在 | 不存在 | 用 `EMaterialFunctionUsage` |
| **EFunctionInputSortPriority** | 不存在 | 不存在 | 不存在 | `SortPriority` 字段是 `int32` |
| **EMaterialSamplerSource** | 不存在 | 不存在 | 不存在 | 用 `ESamplerSourceMode` (SSM_*) |
| **EMaterialLayerUsage** | 不存在 | 不存在 | 不存在 | 用 `EMaterialFunctionUsage::MaterialLayer` / `MaterialLayerBlend` |

### 8.2 关键跨版本变化(任务 #10 之外的)

#### 头文件迁移 — 5.7 MaterialTypes.h → Materials/MaterialParameters.h
- 5.7 把 `EMaterialParameterType` / `EMaterialParameterAssociation` /
 `FMaterialParameterInfo` / `FMaterialAttributeDefinitionMap` 等从
 `Public/MaterialTypes.h` 迁到 `Public/Materials/MaterialParameters.h`。
- 跨版本 include 写法:
 ```cpp
 #if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 #include "Materials/MaterialParameters.h"
 #else
 #include "MaterialTypes.h"
 #endif
 ```
- 注:用 `MaterialShared.h` 间接 include 也可避免显式 include 切换。

#### 5.7 新增 enum 值
- `EMaterialParameterType::ParameterCollection`(5.7+)

#### 5.6 字段/API 变化
- `MaterialFunctionUsage` 字段 5.5 无默认,5.6+ 默认 `Default`
- `bCompilingFunctionPreview`(5.5)→ `UE_DEPRECATED(5.6,...)`(5.6)→ **移除(5.7)**
- `DEFAULT_MATERIALLAYERBLEND_PATH` 宏 5.5 → `DEFAULT_SUBSTRATE_MATERIALLAYERBLEND_PATH` 5.6+
- `FMaterialCachedData::AddParameter` 5.6+ 新增 `FText& OutErrorMessage` 参数

#### 5.7 行为变化
- 5.7 弃用 `GetRelevance(ERHIFeatureLevel::Type)`,改用 `GetRelevance(EShaderPlatform)`
- 5.7 `MaterialExpressionTextureProperty` 增加 `Build(MIR::FEmitter&)` 虚函数 override
- 5.7 `EFunctionInputType` 全部成员加 `UMETA(DisplayName)`
- 5.7 `IsDualBlendingEnabled()` 移除 `EShaderPlatform` 参数(变 0 参)

### 8.3 跨版本保护代码模式

```cpp
// 5.7+ 新增 EMaterialParameterType::ParameterCollection
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 if (ParamType == EMaterialParameterType::ParameterCollection) { /* ... */ }
#endif

// include 路径跨版本兼容
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 #include "Materials/MaterialParameters.h"
#else
 #include "MaterialTypes.h"
#endif

// 5.6+ 才有 FMaterialCachedData::AddParameter 带 FText 错误参数
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 FText ErrMsg;
 AddParameter(Info, Meta, OutTex, OutTexCollection, ErrMsg);
#else
 AddParameter(Info, Meta, OutTex, OutTexCollection);
#endif

// bCompilingFunctionPreview 5.6 deprecated,5.7 移除
#if ENGINE_MAJOR_VERSION < 5 || (ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION < 6)
 FuncInput->bCompilingFunctionPreview = true;
#endif
```

### 8.4 任务 #12 补充的关键文件路径

- `C:/Program Files/Epic Games/UE_5.5/Engine/Source/Runtime/Engine/Public/MaterialTypes.h`
- `C:/Program Files/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Public/Materials/MaterialParameters.h` (5.7 迁移后位置)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialFunctionInterface.h` (EMaterialFunctionUsage)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialExpressionFunctionInput.h` (EFunctionInputType)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialAttributeDefinitionMap.h` (FMaterialAttributeDefintion typo)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/SamplerSourceMode.h` (ESamplerSourceMode)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialExpressionBlendMaterialAttributes.h` (EMaterialAttributeBlend)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialExpressionSceneColor.h` (EMaterialSceneAttributeInputMode)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialExpressionCustom.h` (ECustomMaterialOutputType)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialExpressionTextureProperty.h` (EMaterialExposedTextureProperty)

---

## 9. 深度调查 — 任务 #13 (2026-06-17 续)

任务 #11 已完成 UMaterial 字段基础差异,本任务 #13 深入 Substrate / Nanite-Voxels-Lumen / Translucency-Subsurface 三大领域,补充字段元数据(Category/EditCondition/DisplayName/Keywords)、virtual/override 关系、default 值、EditorOnly 分类细节。

### 9.1 Substrate 深度调查(任务 #11 基础上)

#### 关键新增字段详细对照

| 字段 | 容器 | Category | 其他 meta | Default | 三版状态 |
|---|---|---|---|---|---|
| `SubstrateConversionVersion` (int32) | UMaterialEditorOnlyData | 裸 UPROPERTY (无 Category) | 无 | int32=0(语义 -1 通过 ResetSubstrateConversionVersion 表达) | 三版一致 |
| `SubstrateVersion` (int32) | UMaterialEditorOnlyData | 裸 UPROPERTY | 无 | int32=0 | **5.6 新增**,5.7 沿用 |
| `bIsSubsutrateAutoConvertedAndNotSaved` (bool,拼写 bug) | UMaterialEditorOnlyData | 裸 UPROPERTY | 无 | `= false` | **5.6 新增** |
| `bIsThinSurface` (uint8:1) | UMaterial 主体 | Material | 无 | bitfield 0 | 三版一致 |
| `bSubstrateRoughnessTracking` (uint8:1) | UMaterial 主体 | **Substrate**(注意:非 Material) | BlueprintReadOnly, `meta=(DisplayName="Roughness Tracking")` | bitfield 0 | **5.6 新增** |
| `bEnableExecWire` (uint8:1) | UMaterial 主体 | Material | **5.6 起 `UE_DEPRECATED(5.8, "Experimental bEnableExecWire is no longer supported.")`** | bitfield 0 | 5.5 正常 / 5.6-5.7 deprecated 但未删除 |
| `SubstrateCompilationConfig` (非 UPROPERTY) | UMaterial 主体 | N/A | 头文件 5.7 迁移 | bFullSimplify=false, BytesPerPixelOverride=-1, ClosuresPerPixelOverride=-1 | 三版字段一致 |

#### virtual/override 关系(5.6 起新增)

| 方法 | UMaterialInterface 声明 | UMaterial override | 5.5 | 5.6 | 5.7 |
|---|---|---|---|---|---|
| `HasSubstrateRoughnessTracking() const` | virtual,默认 `return true` | override 返回 `bSubstrateRoughnessTracking` | 不存在 | 声明 + override | 同 5.6 |
| `IsSubstrateAutoConverted() const` | 无 | UMaterialEditorOnlyData 成员,非 virtual | 不存在 | 新增 | 同 5.6 |
| `UserRequestsConvertMaterialToSubstrateMaterial()` | 无 | UMaterial 成员,`#if WITH_EDITOR` | 不存在 | 新增 | 同 5.6 |
| `ConvertMaterialToSubstrateMaterial(bAllowEmpty)` | 无 | UMaterial private,`#if WITH_EDITOR` | 1 参 | **5.6 增加可选 `bRequestedByUser=false`** | 同 5.6 |

#### EditorOnly vs Runtime 分类
- **EditorOnlyData**:`SubstrateConversionVersion` / `SubstrateVersion` / `bIsSubsutrateAutoConvertedAndNotSaved` / `ResetSubstrateConversionVersion` / `IsSubstrateAutoConverted` / `FrontMaterial` / `FrontMaterial_DEPRECATED`
- **UMaterial 主体(运行时可见)**:`bIsThinSurface` / `bSubstrateRoughnessTracking` / `bEnableExecWire`(deprecated) / `SubstrateCompilationConfig` / `HasSubstrateFrontMaterialConnected` / `HasSubstrateRoughnessTracking` (override)
- **`#if WITH_EDITOR` 包裹**:`ConvertMaterialToSubstrateMaterial` / `UserRequestsConvertMaterialToSubstrateMaterial`

#### 关键观察
- 5.5 → 5.6 是 Substrate **主要扩展点**(新增 4 字段 + 4 方法 + 1 virtual)
- 5.6 → 5.7 **完全沿用**,无新增 Substrate 字段
- `bIsSubsutrateAutoConvertedAndNotSaved` 拼写 bug (Sub**s**utrate 双 s)5.6-5.7 未修复
- `bEnableExecWire` 字段未删除,target 5.8(注释说 5.6 引入,实际是 5.5 就有)
- `FSubstrateMaterialInput` 三版完全一致(空 struct,继承 FMaterialInput)
- `FSubstrateCompilationConfig` 三版字段完全一致(3 字段),仅头文件位置 5.7 迁移到 Materials/MaterialParameters.h

---

### 9.2 Nanite / Voxels / Lumen 深度调查

#### 完整 bUsedWith* 字段清单(三版对比)

| 字段 | 5.5 行号 | 5.6 行号 | 5.7 行号 | 类型 | 备注 |
|---|---|---|---|---|---|
| bUsedWithSkeletalMesh | 667 | 685 | 685 | uint8:1 | 一致 |
| bUsedWithEditorCompositing | 674 | 692 | 692 | uint8:1 | 一致 |
| bUsedWithParticleSprites | 681 | 699 | 699 | uint8:1 | 一致 |
| bUsedWithBeamTrails | 688 | 706 | 706 | uint8:1 | 一致 |
| bUsedWithMeshParticles | 695 | 713 | 713 | uint8:1 | 一致 |
| bUsedWithNiagaraSprites | 703 | 721 | 721 | uint8:1 | 一致 |
| bUsedWithNiagaraRibbons | 706 | 724 | 724 | uint8:1 | 一致 |
| bUsedWithNiagaraMeshParticles | 709 | 727 | 727 | uint8:1 | 一致 |
| bUsedWithGeometryCache | 712 | 730 | 730 | uint8:1 | 一致 |
| **bUsedWithMaterialCache** | (无) | 733 | (无) | uint8:1 | **5.6 短暂存在,5.7 移除** |
| bUsedWithStaticLighting | 719 | 740 | 737 | uint8:1 | 一致 |
| bUsedWithMorphTargets | 726 | 747 | 744 | uint8:1 | 一致 |
| bUsedWithSplineMeshes | 733 | 754 | 751 | uint8:1 | 一致 |
| bUsedWithInstancedStaticMeshes | 740 | 761 | 758 | uint8:1 | 一致 |
| bUsedWithGeometryCollections | 747 | 768 | 765 | uint8:1 | 一致 |
| bUsedWithClothing | 767 | 788 | 785 | uint8:1 | 一致 |
| bUsedWithWater | 774 | 795 | 792 | uint32:1 | 一致 |
| bUsedWithHairStrands | 781 | 802 | 799 | uint32:1 | 一致 |
| bUsedWithLidarPointCloud | 788 | 809 | 806 | uint32:1 | 一致 |
| bUsedWithVirtualHeightfieldMesh | 795 | 816 | 813 | uint32:1 | 一致 |
| bUsedWithNanite | 802 | 823 | 820 | uint32:1 | 一致 |
| **bUsedWithVoxels** | (无) | (无) | 827 | **uint8:1**(注意:不是 uint32) | **5.7 新增** |
| bUsedWithVolumetricCloud | 809 | 830 | 834 | uint32:1 | 一致 |
| bUsedWithHeterogeneousVolumes | 816 | 837 | 841 | uint32:1 | 一致 |
| **bUsedWithStaticMesh** | (无) | 844 | 848 | uint32:1 | **5.6 新增** |
| bUsedWithUI_DEPRECATED | 823 | 851 | 855 | uint8:1 | 一致(deprecated) |
| bUsedWithNeuralNetworks | 1031 | 1089 | 1093 | uint8:1 | 一致 |

#### EMaterialUsage 枚举变化

| 版本 | 值数 | 新增/移除 |
|---|---|---|
| 5.5 | 21 | — |
| 5.6 | 23 | **新增 MATUSAGE_MaterialCache, MATUSAGE_StaticMesh** |
| 5.7 | 23 | **移除 MATUSAGE_MaterialCache, 新增 MATUSAGE_Voxels**(顺序:Nanite → Voxels → VolumetricCloud → HeterogeneousVolumes → StaticMesh) |

#### 5.5 独有 `bMobileEnableHighQualityBRDF`(5.6 移除)

```cpp
// 5.5 Material.h:869
UPROPERTY(EditAnywhere, Category=Mobile)
uint8 bMobileEnableHighQualityBRDF : 1;
```

- 5.5 还有 `FMaterial::IsMobileHighQualityBRDFEnabled()`(MaterialShared.h:2173,默认 `= false`)和 `FMaterialResource::IsMobileHighQualityBRDFEnabled()` override
- **5.6/5.7 完全删除**,无 `UE_DEPRECATED` 警告,直接 hard-remove
- **移除原因推测**:Substrate 在 5.6 成为默认材质框架,Mobile/Desktop 渲染路径统一,Mobile 专用 BRDF 质量开关失去意义;关联的 `bUsedWithMaterialCache` 也属同批"被试验性引入又移除的 mobile 性能优化字段"

#### IsCompatibleWithLumenCardSharing() (5.6 新增)

| 类 | 5.5 | 5.6 | 5.7 |
|---|---|---|---|
| UMaterialInterface 声明 | (无) | MaterialInterface.h:1016 | 1047 |
| UMaterial override | (无) | Material.h:1293 | 1302 |
| UMaterialInstance override | (无) | MaterialInstance.h:926 | 984 |

签名 `virtual bool IsCompatibleWithLumenCardSharing() const`,基类默认实现返回 true(推断)。

#### bCompatibleWithLumenCardSharing (5.6 新增,UMaterial 字段)

- 行号 5.6:933 / 5.7:937
- Category: **Material + AdvancedDisplay**
- Type: uint8:1
- BlueprintReadOnly
- 注释:"When true, allows to share Lumen Cards between different instances..."

#### FMaterial 层虚函数(Nanite/Voxels/MaterialCache)

| 方法 | 5.5 | 5.6 | 5.7 |
|---|---|---|---|
| `IsUsedWithNanite()` | MaterialShared.h:2152 | 2208 | 2344 |
| `SupportsMaterialCache()` | (无) | 2211 | (移除) |
| `IsUsedWithVoxels()` | (无) | (无) | **2345 (5.7 新增)** |
| `SamplesMaterialCache()` | (无) | (无) | 2348 (5.7 新增) |
| `HasMaterialCacheOutput()` | (无) | (无) | 2349 (5.7 新增) |

#### Displacement 字段(三版一致,但 5.6 起 bEnableTessellation 加 Keywords="Displacement")

| 字段 | Category | EditCondition | DisplayAfter |
|---|---|---|---|
| bEnableTessellation (5.6+ 加 Keywords="Displacement") | Nanite | 无 | — |
| bEnableDisplacementFade | Nanite | bEnableTessellation (InlineEditConditionToggle) | — |
| DisplacementScaling | Nanite | bEnableTessellation | bEnableTessellation |
| DisplacementFadeRange | Nanite | bEnableDisplacementFade | DisplacementScaling |

#### Displacement 虚函数 override 关系

| 方法 | UMaterialInterface | UMaterial | UMaterialInstance | UMaterialInstanceDynamic |
|---|---|---|---|---|
| GetDisplacementScaling | 5.5:949 / 5.6:997 / 5.7:1027 | 5.5:1219 / 5.6:1281 / 5.7:1290 | 5.5:无 / 5.6:无 / **5.7:962** | 5.5:有 / 5.6:217 / 5.7:219 |
| GetDisplacementFadeRange | 5.5:951 / 5.6:999 / 5.7:1029 | 5.5:1221 / 5.6:1283 / 5.7:1292 | 5.5:无 / 5.6:无 / **5.7:964** | 5.5:有 / 5.6:219 / 5.7:221 |
| IsDisplacementFadeEnabled | 5.5:950 / 5.6:998 / 5.7:1028 | (基类 false) | (无) | 5.5:有 / 5.6:218 / 5.7:220 |

5.7 起 UMaterialInstance 显式 override displacement 方法(5.5/5.6 由 UMaterialInstanceDynamic override 链)。

#### 跨版本代码保护模式

```cpp
// 5.7+ bUsedWithVoxels (uint8:1,不是 uint32)
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 uint8 V = Material->bUsedWithVoxels;
#endif

// 5.6+ bCompatibleWithLumenCardSharing + IsCompatibleWithLumenCardSharing()
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 if (Material->bCompatibleWithLumenCardSharing) { ... }
 bool bCan = Material->IsCompatibleWithLumenCardSharing();
#else
 bool bCan = true; // 5.5 默认支持
#endif

// 5.6+ bUsedWithStaticMesh
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 if (Material->bUsedWithStaticMesh) { ... }
#endif

// 5.5 独有 bMobileEnableHighQualityBRDF
#if ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION == 5
 if (Material->bMobileEnableHighQualityBRDF) { ... }
#endif

// 5.6 短暂 bUsedWithMaterialCache — 避免依赖(很快移除)
#if ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION == 6
 // bUsedWithMaterialCache 存在但 5.7 移除,不要写硬依赖
#endif
```

---

### 9.3 Translucency / Subsurface 深度调查

#### Translucency 字段(三版差异)

| 字段 | 5.5 | 5.6 | 5.7 | 备注 |
|---|---|---|---|---|
| bEnableResponsiveAA / bScreenSpaceReflections / bContactShadows | 有 | 有 | 有 | 一致 |
| TranslucencyPass (TEnumAsByte<EMaterialTranslucencyPass>) | 有 | 有 | 有 | 一致 |
| TranslucencyLightingMode | 有 | 有 | 有 | 一致 |
| bEnableMobileSeparateTranslucency | 有 | 有 | 有 | 一致 |
| TranslucencyDirectionalLightingIntensity | 有 | 有 | 有 | 一致 |
| TranslucentShadowDensityScale 等 5 个 Translucent* 字段 | 有 | 有 | 有 | 一致 |
| bDisableDepthTest / bWriteOnlyAlpha | 有 | 有 | 有 | 一致 |
| AllowTranslucentCustomDepthWrites / bAllowFrontLayerTranslucency | 有 | 有 | 有 | 一致 |
| bUseTranslucencyVertexFog / bApplyCloudFogging / bComputeFogPerPixel | 有 | 有 | 有 | 一致 |
| bOutputTranslucentVelocity | 有 | 有 | 有 | 一致 |
| **bIsTranslucencyVelocityFromDepth (uint8:1)** | (无) | **1033** | **1037** | **5.6 新增**,DisplayName="Velocity From Depth Only", `editcondition="bOutputTranslucentVelocity"` |
| **IsTranslucencyVelocityFromDepth() const override** | (无) | 有 | 有 | **5.6 新增** |
| **bAllowTranslucentLocalLightShadow (uint8:1)** | (无) | **941** | **945** | **5.6 新增**,DisplayName="Allow Local Light Shadow" |
| **TranslucentLocalLightShadowQuality (float = 0)** | (无) | **945** | **949** | **5.6 新增** |
| **TranslucentDirectionalLightShadowQuality (float = 0)** | (无) | **949** | **953** | **5.6 新增** |
| **IsMobileSeparateTranslucencyEnabled() const** | (无) | (无) | **1304** | **5.7 新增** |

#### Subsurface 字段(三版差异)

| 字段 | 5.5 | 5.6 | 5.7 | 备注 |
|---|---|---|---|---|
| FColorMaterialInput SubsurfaceColor (in UMaterialEditorOnlyData) | 有 | 有 | 有 | **5.6 改 FLinearColor 类型**(原 FColor),二进制兼容 |
| GetSubsurfaceProfile_Internal / NumSubsurfaceProfileRoot_Internal | 有 | 有 | 有 | 一致 |
| GetSubsurfaceProfileRoot_Internal (uint32 Index) | 有 | 有 | 有 | 一致 |
| GetSubsurfaceProfileOverride_Internal | 有 | 有 | 有 | 一致 |
| **GetSubsurfaceProfileRoot_Internal() 无参重载** | (无) | (无) | 有 | **5.7 新增** |

#### FColorMaterialInput 类型变化(5.6)

| 版本 | ::Constant 类型 |
|---|---|
| 5.5 | `FColor` |
| 5.6 | `FLinearColor` |
| 5.7 | `FLinearColor` |

二进制序列化兼容(FPixelFormat 内部转换),但 FColor → FLinearColor 直接赋值会触发隐式转换。

#### Translucency/Subsurface override 方法

| 方法 | 5.5 | 5.6 | 5.7 |
|---|---|---|---|
| GetMaterialRelevance | 存在 | 签名未变 | **5.7 弃用 ERHIFeatureLevel::Type 重载**,改用 EShaderPlatform(任务 #12 已确认) |
| IsTranslucent / IsTranslucentMaterial | 一致 | 一致 | 一致 |
| GetTranslucencyMode | 一致 | 一致 | 一致 |
| RequiresSceneTextureCopy | 一致 | 一致 | 一致 |
| IsOpaque | 一致 | 一致 | 一致 |

#### 跨版本代码保护模式

```cpp
// 5.6+ Translucency 字段
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 if (Material->bIsTranslucencyVelocityFromDepth) { ... }
 if (Material->bAllowTranslucentLocalLightShadow) {
 float Q = Material->TranslucentLocalLightShadowQuality;
 }
 bool bVelFromDepth = Material->IsTranslucencyVelocityFromDepth();
#else
 bool bVelFromDepth = false; // 5.5 默认 false
#endif

// 5.7+ IsMobileSeparateTranslucencyEnabled
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 if (Material->IsMobileSeparateTranslucencyEnabled()) { ... }
#endif

// 5.6+ FColorMaterialInput::Constant 类型
// 旧代码 (FColor): Material->SubsurfaceColor.Constant.R
// 5.6+ (FLinearColor): Material->SubsurfaceColor.Constant.R (FLinearColor::R 仍是 float)
// 反射访问需注意类型
```

---

### 9.4 任务 #13 总结:三大领域跨版本保护清单

#### 必加 #if ENGINE_MINOR_VERSION 保护的字段(按 5.6+ 优先)

| 字段 | 引入版本 | 用途 |
|---|---|---|
| `bSubstrateRoughnessTracking` | 5.6+ | Substrate 渲染 |
| `SubstrateVersion` | 5.6+ | Substrate 编译版本 |
| `bIsSubsutrateAutoConvertedAndNotSaved` | 5.6+ | Substrate 转换状态 |
| `HasSubstrateRoughnessTracking()` virtual | 5.6+ | Substrate API |
| `IsSubstrateAutoConverted()` | 5.6+ | Substrate API |
| `UserRequestsConvertMaterialToSubstrateMaterial()` | 5.6+ | Substrate API |
| `ConvertMaterialToSubstrateMaterial(bAllowEmpty, bRequestedByUser=false)` | 5.6+(新增可选参数) | Substrate 转换 |
| `bCompatibleWithLumenCardSharing` | 5.6+ | Lumen 优化 |
| `IsCompatibleWithLumenCardSharing()` virtual | 5.6+ | Lumen API |
| `bUsedWithStaticMesh` | 5.6+ | Static Mesh 优化 |
| `bIsTranslucencyVelocityFromDepth` | 5.6+ | Translucency 优化 |
| `IsTranslucencyVelocityFromDepth()` override | 5.6+ | Translucency API |
| `bAllowTranslucentLocalLightShadow` | 5.6+ | Translucency 阴影 |
| `TranslucentLocalLightShadowQuality` | 5.6+ | Translucency 阴影质量 |
| `TranslucentDirectionalLightShadowQuality` | 5.6+ | Translucency 阴影质量 |
| `bUsedWithVoxels` (uint8:1) | **5.7+** | Nanite Voxels |
| `IsMobileSeparateTranslucencyEnabled()` | **5.7+** | Mobile 渲染路径 |
| `GetSubsurfaceProfileRoot_Internal()` 无参 | **5.7+** | Subsurface API |
| `FMaterial::IsUsedWithVoxels()` | **5.7+** | FMaterial 层 |

#### 5.5 独有,5.6 移除的字段(避免使用)

| 字段 | 5.5 行号 | 备注 |
|---|---|---|
| `bMobileEnableHighQualityBRDF` | 869 | Mobile 渲染优化,5.6 直接 hard-remove(无 deprecation) |

#### 5.6 短暂存在,5.7 移除的字段(避免依赖)

| 字段 | 5.6 行号 | 备注 |
|---|---|---|
| `bUsedWithMaterialCache` | 733 | Material Cache 试验字段 |
| `FMaterial::SupportsMaterialCache()` | 2211 | FMaterial 层配套 |

#### 5.6 标记 deprecation,5.8 移除(5.6/5.7 仍可访问)

| 字段 | 备注 |
|---|---|
| `bEnableExecWire` | `UE_DEPRECATED(5.8, "Experimental bEnableExecWire is no longer supported.")` |

#### 跨版本保护代码完整模板

```cpp
#include "Misc/EngineVersionComparison.h"

// === 通用访问模式 ===
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 constexpr bool bHasVoxels = true;
 constexpr bool bHasLumenCard = true; // 5.6 已有
 constexpr bool bHasSubstrateRoughness = true; // 5.6 已有
 constexpr bool bHasMobileSepTrans = true;
#else
 constexpr bool bHasVoxels = false;
 constexpr bool bHasLumenCard = (ENGINE_MINOR_VERSION >= 6);
 constexpr bool bHasSubstrateRoughness = (ENGINE_MINOR_VERSION >= 6);
 constexpr bool bHasMobileSepTrans = false;
#endif

// === Substrate 设置(5.6+) ===
void ConfigureSubstrateSettings(UMaterial* Mat)
{
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 Mat->bSubstrateRoughnessTracking = true;
 if (Mat->GetEditorOnlyData()->IsSubstrateAutoConverted()) { /* ... */ }
 if (Mat->UserRequestsConvertMaterialToSubstrateMaterial()) { /* ... */ }
#else
 // 5.5 跳过此功能
#endif
}

// === Lumen 优化(5.6+) ===
void ConfigureLumen(UMaterial* Mat)
{
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 Mat->bCompatibleWithLumenCardSharing = true;
 if (Mat->IsCompatibleWithLumenCardSharing()) { /* ... */ }
#endif
}

// === Translucency 高级设置(5.6+/5.7+) ===
void ConfigureTranslucency(UMaterial* Mat)
{
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 6
 Mat->bIsTranslucencyVelocityFromDepth = true;
 Mat->bAllowTranslucentLocalLightShadow = true;
 Mat->TranslucentLocalLightShadowQuality = 1.0f;
#endif
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 if (Mat->IsMobileSeparateTranslucencyEnabled()) { /* ... */ }
#endif
}

// === Voxels(5.7+) ===
void ConfigureVoxels(UMaterial* Mat)
{
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION >= 7
 Mat->bUsedWithVoxels = true;
#endif
}

// === bEnableExecWire(deprecation 包裹) ===
PRAGMA_DISABLE_DEPRECATION_WARNINGS
#if ENGINE_MAJOR_VERSION >= 5 && ENGINE_MINOR_VERSION <= 7
 Mat->bEnableExecWire = false; // 5.5/5.6/5.7 仍可访问
#endif
PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

### 9.5 任务 #13 关键文件路径

- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/Material.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialInterface.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/MaterialShared.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialOverrideNanite.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialInstance.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Public/Materials/MaterialInstanceDynamic.h`
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Classes/Engine/EngineTypes.h`
- `C:/Program Files/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Public/Materials/MaterialParameters.h` (5.7 迁移后)
- `C:/Program Files/Epic Games/UE_5.X/Engine/Source/Runtime/Engine/Private/Materials/MaterialInterface.cpp` (HasSubstrateRoughnessTracking 默认实现 5.6:1518-1521, 5.7:1665-1668)
