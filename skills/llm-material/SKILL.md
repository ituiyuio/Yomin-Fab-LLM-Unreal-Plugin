---
name: llm-material
description: |
  LLMMaterial 是一个 DSL 驱动的 UE5 Material 资产生成系统。当用户需要：
  (1) 创建或设计 UE5 Material 材质（表面材质、透明材质、自发光等）
  (2) 将材质描述转换为可生成的 DSL 格式（.llmmat JSON）
  (3) 理解或修改现有的 Material DSL 定义
  (4) 需要了解支持的 Expression 节点类型（Add、Multiply、TextureSample 等）
  (5) 查询 Material Graph 连接方式和输出设置
  (6) 编写 HLSL 着色器函数（.ush）并在材质中引用
  请使用此技能。
---

# LLMMaterial - DSL Schema Guide

## File Format

Material 定义文件使用 `.llmmat` 扩展名（LLM Material DSL），格式为 JSON。

## Reference Files

**Expression Schema**: `Plugins/LLMMaterial/Config/MaterialExpressionSchema.llmschema` - 包含所有 Material Expression 节点的完整定义（输入、输出、属性）

**示例目录**: `Plugins/LLMMaterial/Config/Examples/` - 完整的材质示例 `.llmmat` 文件（参数 / Fresnel / Panner / 贴图通道 / 顶点色 / Masked+opacityMask / 两种 Substrate 组合算子）。文件名以 `Invalid` 开头的是**故意坏**的负样本（用来证明解析器会拒绝坏定义）—— 别照着抄。

## Quick Start

```json
{
  "version": "1.0",
  "name": "MyRedMaterial",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": {
        "Constant": [1.0, 0.0, 0.0]
      }
    }
  ],
  "connections": [
    {
      "from": "color",
      "fromPin": "Result",
      "to": "output",
      "toPin": "BaseColor"
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

## Shader Headers (USH) - HLSL 函数支持

LLMMat 支持在 `.llmmat` 中编写 HLSL 着色器代码片段，生成 `.ush` 文件供材质引用。所有生成的 `.ush` 文件输出到统一目录 `<ProjectContentDir>/Shaders/`。

> **路径形态**：这是**文件系统路径**（`<Project>/Content/Shaders/`），**不是** UE content path `/Game/Shaders/`。`USHGenerator::Initialize()` 用 `FPaths::Combine(FPaths::ProjectContentDir(), TEXT("Shaders"))` 拼出来；把它当 content path 用会得到"文件从没被写出来"的错觉（历史上确实踩过，见 `references/llmmat-connection-fix.md`）。
>
> **引用路径 ≠ 落盘路径**：`HeaderRef` / `ushIncludes` 里写的是**工程相对 include 路径** `Shaders/<FuncName>.ush`（插件内部按此拼装），而文件实际落在 `<Project>/Content/Shaders/<FuncName>.ush`。另外插件只推导 include 路径，**不会**自动写进 `UMaterialExpressionCustom::IncludeFilePaths`——需要在材质里手工补上该 include 才能真正编到。

### `functions` - 内联定义生成 .ush

```json
{
  "functions": [
    {
      "name": "FunctionName",
      "returnType": "float",
      "description": "Optional documentation",
      "parameters": [
        { "name": "ParamName", "type": "float3" },
        { "name": "Scale", "type": "float", "defaultValue": "1.0" }
      ],
      "body": "return ParamName * Scale;"
    }
  ]
}
```

字段说明：
- `name`（必需）- 函数名，同时作为 `.ush` 文件名
- `returnType`（可选，默认 `float`）- 返回类型
- `description`（可选）- 文档注释
- `parameters[].name`（必需）- 参数名
- `parameters[].type`（必需）- 参数类型（`float`, `float2`, `float3`, `float4` 等）
- `parameters[].defaultValue`（可选）- 默认值
- `body`（必需）- HLSL 函数体，支持多行

### `ushIncludes` - 引用已有 .ush

```json
{
  "ushIncludes": [
    "Shaders/MyExistingFunc.ush"
  ]
}
```

> `ushIncludes` 是**工程相对 include 路径**（同一目录即 `<Project>/Content/Shaders/`），不是 UE content path。

### Custom 节点 `HeaderRef` - 引用函数

使用 `Custom` 节点并设置 `HeaderRef` 属性引用函数名，系统自动生成 `return FuncName(args);` 调用代码：

```json
{
  "nodes": [
    {
      "id": "fresnel",
      "type": "Custom",
      "properties": {
        "HeaderRef": "MyFresnel",
        "OutputType": "CMOT_Float1",
        "Inputs": [
          { "InputName": "Normal" },
          { "InputName": "ViewDir" },
          { "InputName": "Power" }
        ]
      }
    }
  ]
}
```

**优先级**：`HeaderRef` > `Code`（两者同时存在时，`HeaderRef` 优先）

**Include 路径规则**：
- `HeaderRef` 不含 `/`：映射为 `Shaders/{FuncName}.ush`
- `HeaderRef` 含 `/` 或 `.ush`：直接作为 include 路径

### 完整示例：Fresnel 材质

```json
{
  "version": "1.0",
  "name": "GlassMaterial",
  "functions": [
    {
      "name": "MyFresnel",
      "returnType": "float",
      "description": "Schlick Fresnel approximation",
      "parameters": [
        { "name": "Normal", "type": "float3" },
        { "name": "ViewDir", "type": "float3" },
        { "name": "Power", "type": "float", "defaultValue": "5.0" }
      ],
      "body": "float cosTheta = dot(Normal, ViewDir);\nreturn pow(1.0 - cosTheta, Power);"
    }
  ],
  "nodes": [
    {
      "id": "fresnel",
      "type": "Custom",
      "properties": {
        "HeaderRef": "MyFresnel",
        "OutputType": "CMOT_Float1",
        "Inputs": [
          { "InputName": "Normal" },
          { "InputName": "ViewDir" },
          { "InputName": "Power" }
        ]
      }
    }
  ],
  "output": {
    "emissive": { "node": "fresnel", "pin": "Result" }
  }
}
```

生成的 `.ush` 文件（文件系统路径）：
```
<ProjectContentDir>/Shaders/
  MyFresnel.ush    ← 自动生成
```

Custom 节点自动填充 `Code = "return MyFresnel(Normal, ViewDir, Power);"`。

## Color Formats (颜色格式)

支持多种颜色格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| RGB 数组 | `[1.0, 0.0, 0.0]` | 浮点值 0-1 |
| RGBA 数组 | `[1.0, 0.0, 0.0, 1.0]` | 带透明度 |
| Hex | `"#FF0000"` | 十六进制颜色 |
| 标量 | `0.5` | 用于 Metallic/Roughness 等单通道 |

## Node Types (Expression 节点类型)

### Math Operations
| Type | Description | Inputs | Outputs |
|------|-------------|--------|---------|
| `Add` | 加法 | A, B | Result |
| `Multiply` | 乘法 | A, B | Result |
| `Subtract` | 减法 | A, B | Result |
| `Divide` | 除法 | A, B | Result |
| `Power` | 幂运算 | Base, Exponent | Result |
| `Sine` / `Cosine` | 正弦/余弦 | Input | Result |
| `Abs` | 绝对值 | Input | Result |
| `Min` / `Max` | 最小/最大值 | A, B | Result |
| `Clamp` | 限制范围 | Input, Min, Max | Result |
| `LinearInterpolate` | 线性插值(别名 `Lerp`) | A, B, Alpha | Result |

> **引脚名必须逐字对**：`Power` 的指数输入叫 **`Exponent`**（不是 `Exp`），`Desaturation` 的比例输入叫 `Fraction`（是**输入**不是属性），`StaticSwitchParameter` 的两路是 **`A` / `B`**（不是 `True`/`False`）。写错的后果不是报错那么简单 —— 2026-10-25 之前插件把"连不上"只记成一句 warning，材质照样生成、命令照样报 Success。**现在成功消息里会带 `[warnings]` 段，看到就当失败处理。**

### Constants
| Type | Description | Properties |
|------|-------------|------------|
| `Constant` | 标量常量 | R (float)(别名 `Value`) |
| `Constant2Vector` | 2D 向量 | R, G (float) |
| `Constant3Vector` | 3D 向量/颜色 | Constant [R, G, B] |
| `Constant4Vector` | 4D 向量/颜色+Alpha | Constant [R, G, B, A] |

### Textures
| Type | Description | Properties | Inputs | Outputs |
|------|-------------|------------|--------|---------|
| `TextureSample` | 纹理采样 | Texture (path), SamplerType | UVs | RGB, R, G, B, A |
| `TextureSampleParameter2D` | 纹理参数 | ParameterName, Texture, SamplerType | UVs | RGB, R, G, B, A |
| `TextureCoordinate` | UV 坐标 | CoordinateIndex | - | UV |

> **法线贴图必须显式声明采样方式**：`"SamplerType": "Normal"`。不写就会按 Color 采样，shader 编译直接失败
> （`Sampler type is Color, should be Normal`）。

### Parameters (参数)
| Type | Description | Properties |
|------|-------------|------------|
| `ScalarParameter` | 标量参数 | ParameterName, DefaultValue |
| `VectorParameter` | 向量参数 | ParameterName, DefaultValue |
| `TextureSampleParameter2D` | 纹理参数 | 同上方 Textures 表（ParameterName, Texture, SamplerType）—— 列两处是分类视角不同, 属性集以 Textures 表为准 |
| `StaticSwitchParameter` | 静态开关 | ParameterName, DefaultValue (bool) |

### Coordinates
| Type | Description | Outputs |
|------|-------------|---------|
| `VertexColor` | 顶点颜色 | RGB, R, G, B, A |
| `WorldPosition` | 世界坐标 | XYZ |
| `CameraPosition` | 相机位置 | XYZ |
| `Time` | 时间 | - |

### Utilities
| Type | Description | Inputs | Outputs |
|------|-------------|--------|---------|
| `ComponentMask` | 通道遮罩 | Input | R, G, B, A (根据 mask 配置) |
| `AppendVector` | 向量组合 | A, B | Result |
| `Desaturation` | 去饱和 | Input, Fraction | Result |
| `Fresnel` | 菲涅耳(边缘) | Exponent, Normal | Result |
| `Panner` | UV 滚动 | Coordinate, Time, Speed（不接则走属性 ConstCoordinate / SpeedX / SpeedY） | Result |

> `Fresnel` 在 UE 5.8 的引脚是 **`Exponent`**（旧版的 `Bias` / `Scale` 已被引擎删掉，写了会被忽略并报 warning），另有 `BaseReflectFraction` 属性（float, 默认 0.04）与可选输入 `Normal`（2026-10-26 按引擎头 `MaterialExpressionFresnel.h` 归正——原表格行把 `Normal` 错排在属性列且断言"只有 Exponent"）。
> `Panner` 的 `Speed` 是 **float2 输入**（不接则用 `SpeedX`/`SpeedY` 属性），`Time` 不接则用游戏时间。

### Custom (HLSL)
| Type | Description | Properties | Inputs |
|------|-------------|------------|--------|
| `Custom` | 自定义 HLSL 代码 | `Code` 或 `HeaderRef`+`OutputType`+`Inputs` | 动态（通过 Inputs 定义） |

**属性说明**：
- `Code` - 直接写入的 HLSL 代码（如 `return sin(Normal) * 0.5 + 0.5;`）
- `HeaderRef` - 引用 `functions` 中定义的函数名，自动生成 `return FuncName(args);`
- `OutputType` - 输出类型：`CMOT_Float1`/`CMOT_Float2`/`CMOT_Float3`/`CMOT_Float4`
- `Description` - 节点描述
- `Inputs` - 动态输入引脚数组：`[{"InputName": "Param1"}, {"InputName": "Param2"}]`

**注意**：`HeaderRef` 优先级高于 `Code`，两者同时存在时使用 `HeaderRef`。

## Node Definition Format

```json
{
  "id": "uniqueNodeId",
  "type": "ExpressionType",
  "displayName": "Optional Display Name",
  "properties": {
    "PropertyName": "value"
  }
}
```

**必需字段**:
- `id` - 节点唯一标识符（用于连接引用）
- `type` - Expression 类型名（如 "Add", "Multiply", "TextureSample"）

**可选字段**:
- `displayName` - 显示名称（用于编辑器中展示）
- `properties` - 节点属性配置

## Connection Format

```json
{
  "from": "sourceNodeId",
  "fromPin": "outputPinName",
  "to": "targetNodeId",
  "toPin": "inputPinName"
}
```

**连接字段**:
- `from` - 源节点 ID
- `fromPin` - 源节点输出引脚名称（如 "Result", "RGB"）
- `to` - 目标节点 ID
- `toPin` - 目标节点输入引脚名称（如 "A", "B", "BaseColor"）

**常见引脚名称**:
- 输出: `Result`, `RGB`, `R`, `G`, `B`, `A`
- 输入: `A`, `B`, `Base`, `Exponent`, `UVs`, `Input`（2026-10-26 勘误：原写 `Exp`，正是 Power 表下方警告里点名的错名）

## Material Outputs (材质输出)

```json
"output": {
  "baseColor": { "node": "nodeId", "pin": "Result" },
  "metallic": 0.0,
  "roughness": 0.5,
  "specular": { "node": "nodeId", "pin": "R" },
  "normal": { "node": "nodeId", "pin": "RGB" },
  "emissive": { "node": "nodeId", "pin": "Result" },
  "opacity": 1.0,
  "opacityMask": { "node": "nodeId", "pin": "A" },
  "worldPositionOffset": { "x": 0, "y": 0, "z": 0 }
}
```

**输出类型**:
- `baseColor` - 基础颜色 (RGB)
- `metallic` - 金属度 (0-1)
- `roughness` - 粗糙度 (0-1)
- `specular` - 高光 (0-1)
- `normal` - 法线贴图 (RGB)
- `emissive` - 自发光 (RGB)
- `opacity` - 透明度 (0-1)
- `opacityMask` - 透明遮罩 (0-1)
- `worldPositionOffset` - 世界位置偏移 (XYZ)

**输出格式**:
- 节点引用: `{ "node": "nodeId", "pin": "outputName" }`
- 常量值: `0.5` 或 `"#FF0000"` 或 `[1.0, 0.0, 0.0]`

> **常量输出会真的落到材质上**（2026-10-25 修复：之前常量分支是空壳，`metallic`/`roughness`/`specular`/`opacity`/`opacityMask` 全被静默丢弃、材质退回引擎默认值，而命令照样报 Success）。颜色类输出喂标量会按 `(v, v, v)` 补齐。
>
> **`material generate` 的成功消息里带 `[warnings]` 段就当失败处理** —— 那里是"属性名不存在 / 连不上引脚"的信号，材质跟你写的不一样。

## Material Properties (材质属性)

```json
{
  "version": "1.0",
  "name": "MyMaterial",
  "description": "Optional description",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "twoSided": false,
  "nodes": [...],
  "connections": [...],
  "output": {...}
}
```

**材质域 (Domain)**:
- `Surface` - 表面材质（默认）
- `DeferredDecal` - 延迟贴花
- `LightFunction` - 光源函数
- `Volume` - 体积材质
- `PostProcess` - 后处理材质
- `UserInterface` - UI 材质
- `RuntimeVirtualTexture` - 运行时虚拟纹理

> **别名**（仍能解析，导出侧不产出）：`UI` = `UserInterface`、`Decal` = `DeferredDecal`、`VirtualTexture` = `Surface`（老词表写法，历史上就等价 Surface；真要 RVT 域请写 `RuntimeVirtualTexture`）。
>
> 域 / 混合模式的词表由 `FLLMEnumLookup` 一张表决定，**导出侧与解析侧同源** ⇒ `material export` 出来的 `domain` / `blendMode` 一定解析得回同一个值。

**混合模式 (BlendMode)**:
- `Opaque` - 不透明（默认）
- `Masked` - 遮罩（使用 OpacityMask）
- `Translucent` - 半透明
- `Additive` - 加法混合
- `Modulate` - 调制混合
- `AlphaComposite` - 预乘 alpha 合成
- `AlphaHoldout` - alpha 镂空

**着色模型 (ShadingModel)**:
- `DefaultLit` - 默认光照（默认）
- `Unlit` - 无光照
- `Subsurface` - 次表面散射（需要 SubsurfaceColor 输出）
- `SubsurfaceProfile` - SubsurfaceProfile 资产散射（需要 subsurfaceProfile 属性）
- `ClearCoat` - 清漆涂层
- `Hair` - 头发
- `Cloth` - 布料
- `Eye` - 眼睛
- `TwoSidedFoliage` - 双面植被
- `SingleLayerWater` - 单层水面
- `ThinTranslucent` - 薄透明
- `Strata` - 分层材质

**SubsurfaceProfile 资产引用**:
当 `shadingModel` 为 `SubsurfaceProfile` 时，系统会自动创建 SubsurfaceProfile 资产（如果不存在）。可选地可以指定 `subsurfaceProfile` 属性：

```json
{
  "shadingModel": "SubsurfaceProfile",
  "subsurfaceProfile": "/Game/Materials/MySkinSSS.MySkinSSS"
}
```

如果不指定 `subsurfaceProfile`，系统会在材质同一目录下自动创建 `{材质名}_SSS` 的 SubsurfaceProfile 资产，包含适合皮肤/硅胶渲染的参数（Burley SSS 模型、AFIS 高质量渲染）。

> 给了路径但资产**不存在**时，系统会打一条 `SubsurfaceProfile not found` warning 并回落到上面的自动创建，不会静默失败。UE 5.8 的引擎内容里**没有** `DefaultSkin` 之类的现成 SubsurfaceProfile 可直接引用（`/Engine/EngineResources/`、`/Engine/EngineMaterials/` 下均无），所以最省事的做法是干脆省略这个字段。

## Substrate Materials (UE5 Substrate)

LLMMaterial 支持 UE5 Substrate 分层材质系统。当 `.llmmat` 文件包含 `substrate` 字段时，系统自动使用 Substrate 路由模式。

### Substrate 路由模式

| 模式 | 条件 | 说明 |
|------|------|------|
| Traditional | 只有 `nodes` | 使用传统 Material Expression 构建 |
| Substrate | 只有 `substrate.slabs` | 完全 Substrate 管线 |
| Hybrid | `nodes` + `substrate.slabs` | Expression + Substrate 混合 |

### Substrate Schema

```json
{
  "version": "1.0",
  "name": "MySubstrateMaterial",
  "description": "UE5 Substrate material",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [
      {
        "id": "slab_id",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.8, 0.8, 0.8],
          "Roughness": 0.3,
          "F0": [0.04, 0.04, 0.04],
          "Metallic": 0.0,
          "Specular": 0.5,
          "Normal": [0.5, 0.5, 1.0],
          "Bump": [0.5, 0.5, 1.0],
          "TopRoughness": 0.2,
          "BottomRoughness": 0.4,
          "FuzzColor": [0.5, 0.5, 0.5],
          "FuzzRoughness": 0.5
        }
      }
    ],
    "compositions": [
      {
        "type": "HorizontalMixing",
        "slabA": "slab_id_a",
        "slabB": "slab_id_b",
        "MixRatio": 0.5
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "slab_id",
      "bottom": "slab_id_base",
      "topThickness": 0.01
    }
  }
}
```

### Slab 类型

| Type | Description | 关键输入 |
|------|-------------|---------|
| `SubstrateSlabBSDF` | 基础表面 BSDF（默认） | DiffuseAlbedo, Roughness, F0, Metallic, Normal |
| `SubstrateHairBSDF` | 头发 BSDF | BackboneRadius,Density,DirectVectorization, etc. |
| `SubstrateUnlitBSDF` | 无光照 BSDF | EmissiveRadiance |
| `SubstrateEyeBSDF` | 眼睛 BSDF | IrisDistance, PupilRadius, etc. |
| `SubstrateSingleLayerWaterBSDF` | 单层水面 | Extinction, Scattering |

### Composition 类型

| Type | Description | 必需字段 |
|------|-------------|---------|
| `VerticalLayering` | 垂直分层（上下叠层） | `top` slab ID |
| `HorizontalMixing` | 水平混合（两 slab 融合） | `slabA`, `slabB`, `MixRatio` |
| `Add` | 添加两 slab | `slabA`, `slabB` |
| `Weight` | 权重节点 | `slab` ID, `weight` |
| `Select` | 选择节点 | `slabA`, `slabB`, `Threshold` |

### Root Composition 说明

- 如果 `root` 只有 `top`（无 `bottom`），则直接使用 top slab 作为 root
- `topThickness` 默认 0.01
- `bUseParameterBlending` 默认 false

### Slab 输入值格式

```json
"inputs": {
  "DiffuseAlbedo": [0.8, 0.8, 0.8],   // RGB 数组 = Constant3Vector
  "Roughness": 0.3,                      // 标量 = Constant
  "F0": [0.04, 0.04, 0.04],             // RGB 数组（默认为 0.04 菲涅尔）
  "Metallic": 0.0,                       // 标量
  "Normal": "/Game/Textures/Normal",      // 纹理引用
  "BaseColor": { "node": "node_id" }     // 引用 Expression 节点 (Hybrid 模式)
}
```

### 示例：硅胶材质（SubstrateSlabBSDF）

```json
{
  "version": "1.0",
  "name": "SiliconeMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [
      {
        "id": "silicone_surface",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.95, 0.92, 0.88],
          "Roughness": 0.15,
          "F0": [0.04, 0.04, 0.04]
        }
      },
      {
        "id": "silicone_base",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.85, 0.82, 0.78],
          "Roughness": 0.4
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "silicone_surface",
      "bottom": "silicone_base",
      "topThickness": 0.005
    }
  }
}
```

### Substrate 注意事项

1. **ShadingModel 自动切换**：Substrate 材质会自动将 ShadingModel 设为 `MSM_Strata`
2. **Hybrid 模式**：`nodes` 中的 Expression 节点可以被 `substrate.slabs[].inputs[]` 中的 `{ "node": "node_id" }` 引用。支持的 key 有：`node`、`nodeId`、`node_id`、`nodeRef`（均等价）
3. **纹理输入**：纹理使用资产路径字符串，系统自动创建 `TextureObject` 或 `TextureSample` 节点
4. **不含 bottom 的 VerticalLayering**：当 root 只指定 `top` 时，Top slab 直接作为 root（无需 VerticalLayering 节点）
5. **导出可往返**（2026-10-25 修复）：`material export` 会把材质里的 substrate 拓扑**还原**成 `substrate` 块（slabs + root），导出的文件能直接再 `material generate`。以前导出的是拍平的表达式节点、再导入报 `Orphaned node` / `Dangling node`。只有真正表达不了的部分才会给 warning（嵌套组合、Select 阈值 ≠ 0.5、没有 FrontMaterial）。
6. **slab 输入名 == UE 属性名**：`inputs` 的 key 就是 UE 表达式上那个 `FExpressionInput` 的属性名（`DiffuseAlbedo` / `Roughness` / `F0` / `SSSMFP` / ...）。两侧同名，引擎加了新引脚不用改 DSL 词表；Hair / Unlit / Eye / SingleLayerWater 的输入以前会被**静默丢弃**，现在都通吃。

## Common Patterns

### 简单颜色材质
```json
{
  "version": "1.0",
  "name": "RedMaterial",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [1.0, 0.0, 0.0] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

### 纹理材质
```json
{
  "version": "1.0",
  "name": "TextureMaterial",
  "nodes": [
    {
      "id": "tex",
      "type": "TextureSample",
      "properties": { "Texture": "/Game/Textures/MyTexture" }
    }
  ],
  "output": {
    "baseColor": { "node": "tex", "pin": "RGB" }
  }
}
```

### 金属材质
```json
{
  "version": "1.0",
  "name": "MetalMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.8, 0.8, 0.9] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" },
    "metallic": 1.0,
    "roughness": 0.3
  }
}
```

### 透明玻璃材质
```json
{
  "version": "1.0",
  "name": "GlassMaterial",
  "domain": "Surface",
  "blendMode": "Translucent",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.9, 0.95, 1.0] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" },
    "metallic": 0.0,
    "roughness": 0.1,
    "opacity": 0.5
  }
}
```

### 颜色 + 纹理混合
```json
{
  "version": "1.0",
  "name": "TintedTexture",
  "nodes": [
    {
      "id": "tex",
      "type": "TextureSample",
      "properties": { "Texture": "/Game/Textures/BaseColor" }
    },
    {
      "id": "tint",
      "type": "Constant3Vector",
      "properties": { "Constant": [1.0, 0.8, 0.6] }
    },
    {
      "id": "multiply",
      "type": "Multiply"
    }
  ],
  "connections": [
    { "from": "tex", "fromPin": "RGB", "to": "multiply", "toPin": "A" },
    { "from": "tint", "fromPin": "Result", "to": "multiply", "toPin": "B" }
  ],
  "output": {
    "baseColor": { "node": "multiply", "pin": "Result" }
  }
}
```

### 硅胶材质模板（Substrate + USH 混合模式）

> **⚠️ 这是模板/教学示例，不是已存在的资产**。本节出现的 `.llmmat` / `.ush` 文件名都是**范本占位符**，不是任何工程里现成存在的文件。历史上本节曾把不存在的资产写成"生产可用资产"，LLM 照着路径跑 `material generate` 立刻掉进 file-not-found / wrong-reference 调试循环（完整 forensics 见 SKILL_CHANGELOG §1）。

**先核实，再引用**——在任何工程里动手前，先列出该工程真实存在的资产，只用真实存在的文件当参考：

```bash
# 列出本工程实际的 .llmmat 资产
find . -name "*.llmmat" -not -path "./.git/*"

# 列出本工程实际存在的 .ush 着色器头文件（生成目录 <ProjectContentDir>/Shaders/）
ls Content/Shaders/*.ush
```

确认哪个 `.llmmat` 真的存在之后，再打开它看 `substrate.slabs` 的节点配置作为写法参考。

写实硅胶质感材质的设计思路，适用于硅胶娃娃、软体机器人等场景。使用 SubstrateSlabBSDF 提供精确 PBR + SSS，配合 USH Custom HLSL 节点实现 Fresnel rim light 和 SSS 近似透光。

核心特性：
- **SubstrateSlabBSDF**：物理精确的 PBR，SSSMFP/SSSMFPScale 控制次表面散射颜色和半径
- **SiliconeFresnel**（USH 范本名）：基于 IOR 计算 F0 的 Fresnel，边缘过渡更柔和（vs 玻璃的 sharp edge）
- **SiliconeSSSApprox**（USH 范本名）：背光区域近似 SSS，红光穿透比蓝光更强
- **SiliconeRimGlow**（USH 范本名）：边缘光晕，用于轮廓 highlight

> 上面 3 个 USH 名字都是**范本名**——只有你在 `functions[]` 里定义了同名函数，才会真的被生成到 `<Project>/Content/Shaders/`。

关键参数（硅胶基底典型值）：

| 参数 | 默认值 | 说明 |
|------|--------|-----|
| `param_basecolor` | [0.92, 0.72, 0.62] | 基底颜色（暖粉调，硅胶典型值） |
| `param_roughness` | 0.18 | 粗糙度（硅胶典型值） |
| `param_ior` | 1.42 | 折射率（硅胶典型值 1.40-1.50） |
| `param_fresnel_exp` | 3.5 | Fresnel 指数（越大边缘越窄） |
| `param_sss_scale` | 1.2 | SSS 散射半径 |
| `param_sss_mfp_r/g/b` | 0.60/0.25/0.12 | SSS Mean Free Path 三通道（红散射最强） |
| `param_rim_color` | [1.0, 0.95, 0.90] | 边缘光颜色 |
| `param_rim_str` | 0.4 | 边缘光强度 |
| `param_translucency` | 0.3 | SSS 透光强度 |

<!-- Forensic: see SKILL_CHANGELOG.md §1 (tool-fix-170 SiliconeDoll template asset/USH fossil closure) -->

### Subsurface 皮肤材质（SubsurfaceProfile）
```json
{
  "version": "1.0",
  "name": "SkinMaterial",
  "description": "Realistic skin with SubsurfaceProfile",
  "domain": "Surface",
  "blendMode": "Translucent",
  "shadingModel": "SubsurfaceProfile",
  "subsurfaceProfile": "/Game/Materials/SkinMaterial_SSS.SkinMaterial_SSS",
  "twoSided": true,
  "nodes": [
    {
      "id": "skinColor",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.89, 0.67, 0.55] }
    },
    {
      "id": "roughness",
      "type": "Constant",
      "properties": { "R": 0.6 }
    },
    {
      "id": "fresnel",
      "type": "Fresnel",
      "properties": { "Exponent": 5.0 }
    },
    {
      "id": "sssEmissive",
      "type": "Multiply"
    }
  ],
  "connections": [
    { "from": "fresnel", "fromPin": "Result", "to": "sssEmissive", "toPin": "A" },
    { "from": "skinColor", "fromPin": "Result", "to": "sssEmissive", "toPin": "B" }
  ],
  "output": {
    "baseColor": { "node": "skinColor", "pin": "Result" },
    "roughness": { "node": "roughness", "pin": "Result" },
    "emissive": { "node": "sssEmissive", "pin": "Result" }
  }
}
```

### 法线贴图材质
```json
{
  "version": "1.0",
  "name": "NormalMapMaterial",
  "nodes": [
    {
      "id": "baseColor",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.5, 0.5, 0.5] }
    },
    {
      "id": "normalTex",
      "type": "TextureSample",
      "properties": { "Texture": "/Game/Textures/Normal" }
    }
  ],
  "output": {
    "baseColor": { "node": "baseColor", "pin": "Result" },
    "normal": { "node": "normalTex", "pin": "RGB" }
  }
}
```

### 自发光材质
```json
{
  "version": "1.0",
  "name": "EmissiveMaterial",
  "nodes": [
    {
      "id": "emissiveColor",
      "type": "Constant3Vector",
      "properties": { "Constant": [2.0, 0.5, 0.0] }
    }
  ],
  "output": {
    "emissive": { "node": "emissiveColor", "pin": "Result" }
  }
}
```

## Auto-Layout (自动布局)

当 `material generate` 生成材质时，节点会自动按拓扑顺序排列：

- **数据流方向**：从左到右，Source 节点（Constant/Parameter/Texture）→ 运算节点 → 输出
- **列距**：280px（可配置）
- **Y轴对齐**：所有列共享同一全局行网格，节点按分类对号入行
- **孤立节点**：位于最左侧列下方

**全局行网格对齐算法**：
1. 计算最大列节点数 `MaxNodesInColumn`
2. 构建全局行网格：`RowGrid[i] = GridOriginY - (MaxNodesInColumn - 1) * RowHeight * 0.5 + i * RowHeight`
3. 每个节点按分类行号放置：Source → Row 0, Operator → Row 1, Utility → Row 2, Other → 最后

**节点分类排序**（同列内）：
1. Source（常量/参数/纹理）→ Row 0（顶部）
2. Operator（数学运算）→ Row 1
3. Utility（遮罩/变换/插值）→ Row 2
4. Other → 后续行

**布局算法**：
- 基于 Sugiyama 分层布局（BFS 拓扑排序）
- 双向重心排序减少连线交叉
- 支持回路处理（放在最后一列）
- 全局行网格确保所有列节点列对齐

修改布局参数请编辑：
```
Plugins/LLMMaterial/Source/LLMMaterial/Core/LLMMaterialTypes.h
```
`FLLMMaterialLayoutConfig` struct 中的 `ColumnWidth`、`RowHeight`、`SourceColX`、`GridOriginY` `static constexpr float` 常量（`Builder/MaterialGraphLayout.cpp:41-44` 读取）。原 `MaterialGraphBuilder.cpp::LayoutNodes()` 已退化为 9 行 delegate 到 `FMaterialGraphLayout::ApplySugiyama`。

## Editor Workflow

### JSON → Material (生成)
1. 使用 `material generate` 命令：
   ```
   material generate /Game/Materials/MyMaterial --from C:/Temp/myMaterial.llmmat
   ```
2. 或者在编辑器面板中粘贴 JSON 并点击 "Generate"
3. 生成的 Material 资产会自动打开

### Material → JSON (导出)
1. 使用 `material export` 命令：
   ```
   material export /Game/Materials/MyMaterial --output C:/Temp/export.llmmat
   ```
2. 导出的 JSON 可用于修改和重新生成

## Command Reference

> **Source of truth**: 以下命令列表与 `Plugins/LLMMaterial/Source/LLMMaterial/Commands/MaterialCommandRegistry.h` 的命令注册表一致(`LLMMaterialModule.cpp::BuildAbilityInfoJson()` 由该注册表派生,是 ability JSON 的唯一来源)。
> **LLMEasyShell dispatcher 只放行注册表里的子命令** —— 注册表之外的命令名一律到不了处理器,会直接返回 `Unknown command`。想加新命令 = 新建 `Commands/Material<Name>Command.{h,cpp}` + 在注册表里加一条,两条路径共用同一张表。
> 通用资产操作(创建/删除/复制/移动/查看/设置参数)由 **LLMEasyShell 主系统** 提供 (`new` `rm` `cp` `mv` `cat` `set`),不在 material ability 重复注册。

<!-- Forensic: see SKILL_CHANGELOG.md §2 (tool-fix-07 session62 5-subcommand count closure) -->

### Shell 命令

```bash
# 从 JSON 生成材质
material generate <assetPath> --from <filePath> [--domain <domain>] [--blending <blending>]

# 导出材质到 JSON
material export <assetPath> [--output <filePath>]

# 导出 Expression Schema (所有节点类型 + pin + property)
material export-schema [--output <filePath>]

# 列出可用 MaterialExpression 节点类型
material list-types [--category <category>] [--search <keyword>]

# 查看节点类型详情 (pin / property / DSL 示例)
material describe-type <typeName>
```

### 参数说明

**generate**:
- `assetPath` - 目标材质资产路径（如 `/Game/Materials/MyMaterial`）
- `--from` - 源 JSON 文件路径(支持 UE 路径 `/Game/...` `/Plugin/...` 或文件系统绝对路径)
- `--domain` - 材质域（Surface/DeferredDecal/LightFunction/Volume/PostProcess/UserInterface/RuntimeVirtualTexture）
- `--blending` - 混合模式（Opaque/Masked/Translucent/Additive/Modulate/AlphaComposite/AlphaHoldout）

**export**:
- `assetPath` - 要导出的材质资产路径
- `--output` - 输出 JSON 文件路径（可选，默认导出到 `Saved/LLMMaterial/Exported_<MaterialName>.llmmat`）

**export-schema**:
- `--output` - 输出 schema 文件路径（可选，默认导出到 `Saved/LLMMaterial/MaterialExpressionSchema.llmschema`）

> 默认输出落在**工程的 Saved 目录**（可写），不写回插件目录——Fab 安装的插件目录是只读的。插件配置项 `SchemaExportPath` 若已设置则优先于该默认值。
>
> **编辑器面板**（Window ▸ Tools ▸ LLMMaterial）用同一套规则：Domain / Blend 两个下拉可以覆盖 `.llmmat` 里声明的值（留空 = 用文件自己的值），可选项与 shell 的 `--domain` / `--blending` 取自同一张词表；面板的 "Export Material" / "Export Schema" 与命令落在同一目录。

**list-types**:
- `--category` - 按分类过滤（Math/Texture/Constant/Coordinates/...）
- `--search` - 按名称子串搜索

**describe-type**:
- `typeName` - 节点类型名（如 `Multiply` / `TextureSample` / `Add`）

## Schema Reference

查看完整的 Expression 类型定义：
```
Plugins/LLMMaterial/Config/MaterialExpressionSchema.llmschema
```

或在编辑器中使用命令导出：
```
material export-schema --output C:/Temp/schema.json
```

## 经验库 / Known Pitfalls

`references/` 目录汇总了 12 个 Material 踩坑（Substrate / Nanite / multi-UE 兼容 / build pre-existing）：

- **Substrate 崩溃 + SSS**：`llmmat-substrate-crash-fix.md`, `llmmat-substrate-sss-crash.md`, `llmmat-substrate-pipeline.md`
- **Nanite + Substrate 错配**：`llmmat-nanite-crash.md`
- **多 UE 兼容**：`ue55-material-api-survey-2026-06-17.md`（SubsurfaceProfile.Implementation 仅 5.6+, GetMaterialResource 5.7 EShaderPlatform）
- **隐式零值陷阱**：`llmmat-value-vs-constant-zeroblack.md`（属性名必须 `Constant` 不是 `Value`）
- **Silent Success 回归**：`llmmat-silent-success-regression-2026-06-09.md`
- **Build.cs 软依赖完整模式**：`llmmat-soft-dep-check-module-exists-2026-06-09.md`
- **BlendableLocation 验证**：`llmmat-blendablelocation-verify-batch-a-2026-06-11.md`
- **连接修复**：`llmmat-connection-fix.md`
- **输出节点修复**：`llmmat-output-section-fix.md`
- **LLMEasyShell Lite 集成**：`llmmaterial-llmeashyshell-lite-integration.md`
