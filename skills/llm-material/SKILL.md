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

**示例目录**: `Plugins/LLMMaterial/Config/Examples/` - 包含完整的材质示例 `.llmmat` 文件

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

LLMMat 支持在 `.llmmat` 中编写 HLSL 着色器代码片段，生成 `.ush` 文件供材质引用。所有生成的 `.ush` 文件输出到统一目录 `/Game/Shaders/`。

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
    "/Game/Shaders/MyExistingFunc.ush"
  ]
}
```

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

生成的 `.ush` 文件：
```
/Game/Shaders/
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
| `Power` | 幂运算 | Base, Exp | Result |
| `Sine` / `Cosine` | 正弦/余弦 | Input | Result |
| `Abs` | 绝对值 | Input | Result |
| `Min` / `Max` | 最小/最大值 | A, B | Result |
| `Clamp` | 限制范围 | Input, Min, Max | Result |
| `Lerp` | 线性插值 | A, B, Alpha | Result |

### Constants
| Type | Description | Properties |
|------|-------------|------------|
| `Constant` | 标量常量 | Value (float) |
| `Constant2Vector` | 2D 向量 | Constant [X, Y] |
| `Constant3Vector` | 3D 向量/颜色 | Constant [R, G, B] |
| `Constant4Vector` | 4D 向量/颜色+Alpha | Constant [R, G, B, A] |

### Textures
| Type | Description | Properties | Inputs | Outputs |
|------|-------------|------------|--------|---------|
| `TextureSample` | 纹理采样 | Texture (path) | UVs | RGB, R, G, B, A |
| `TextureCoordinate` | UV 坐标 | CoordinateIndex | - | UV |

### Parameters (参数)
| Type | Description | Properties |
|------|-------------|------------|
| `ScalarParameter` | 标量参数 | ParameterName, DefaultValue |
| `VectorParameter` | 向量参数 | ParameterName, DefaultValue |
| `TextureSampleParameter` | 纹理参数 | ParameterName, Texture |

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
- 输入: `A`, `B`, `Base`, `Exp`, `UVs`, `Input`

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
- `PostProcess` - 后处理材质
- `UserInterface` - UI 材质
- `VirtualTexture` - 虚拟纹理

**混合模式 (BlendMode)**:
- `Opaque` - 不透明（默认）
- `Masked` - 遮罩（使用 OpacityMask）
- `Translucent` - 半透明
- `Additive` - 加法混合
- `Modulate` - 调制混合

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

### 硅胶材质模板（参考 M_SiliconeDoll 设计 - Substrate + USH 混合模式）

> **⚠️ 这是模板/教学示例，不是已存在的资产**。`Content/Materials/M_SiliconeDoll.llmmat` **不存在**（filesystem 0 hits 全工程），只是文档作者当初设想的"完整硅胶材质应当长这样"的教学范本。生产可用的硅胶资产只有 3 个：
> - `Content/Core/LLM/Materials/M_SiliconeSkin_v3.llmmat`（最接近本模板，纯 SSS 单 slab MSS_Diffusion）
> - `Content/Core/LLM/Materials/M_TPESilicone_v7_NoSSS.llmmat`（TPE 硅胶，无 SSS）
> - `Content/Core/LLM/Materials/M_TPESilicone_v8_AiCup.llmmat`（TPE 硅胶 v8，AiCup 用例）
>
> 唯一存在的 USH 文件只有 `Content/Shaders/SiliconeFresnel.ush` 1 个（`SiliconeSSSApprox.ush` / `SiliconeRimGlow.ush` / `SiliconeComposite.ush` 0 hits 全工程）。要参考真实写法，**打开 M_SiliconeSkin_v3.llmmat** 看其 `substrate.slabs.sss_skin` 节点配置。

写实硅胶质感材质的设计思路，适用于硅胶娃娃、软体机器人等场景。使用 SubstrateSlabBSDF 提供精确 PBR + SSS，配合 USH Custom HLSL 节点实现 Fresnel rim light 和 SSS 近似透光。

核心特性：
- **SubstrateSlabBSDF**：物理精确的 PBR，SSSMFP/SSSMFPScale 控制次表面散射颜色和半径
- **SiliconeFresnel**（USH，唯一已实现）：基于 IOR 计算 F0 的 Fresnel，边缘过渡更柔和（vs 玻璃的 sharp edge）
- **SiliconeSSSApprox**（USH，模板）：背光区域近似 SSS，红光穿透比蓝光更强
- **SiliconeRimGlow**（USH，模板）：边缘光晕，用于轮廓 highlight

关键参数（参考 M_SiliconeSkin_v3 实际值）：

| 参数 | 默认值 | 说明 |
|------|--------|-----|
| `param_basecolor` | [0.92, 0.72, 0.62] | 基底颜色（暖粉调，M_SiliconeSkin_v3 实际值） |
| `param_roughness` | 0.18 | 粗糙度（M_SiliconeSkin_v3 实际值） |
| `param_ior` | 1.42 | 折射率（硅胶典型值 1.40-1.50） |
| `param_fresnel_exp` | 3.5 | Fresnel 指数（越大边缘越窄） |
| `param_sss_scale` | 1.2 | SSS 散射半径 |
| `param_sss_mfp_r/g/b` | 0.60/0.25/0.12 | SSS Mean Free Path 三通道（M_SiliconeSkin_v3 实际值，红散射最强） |
| `param_rim_color` | [1.0, 0.95, 0.90] | 边缘光颜色 |
| `param_rim_str` | 0.4 | 边缘光强度 |
| `param_translucency` | 0.3 | SSS 透光强度 |

生产资产查看（不要按模板路径生成，路径不存在）：
```bash
# 查看 M_SiliconeSkin_v3 实际配置（最接近模板设计的真实资产）
cat Content/Core/LLM/Materials/M_SiliconeSkin_v3.llmmat

# 验证 USH 文件实际只有 1 个
ls Content/Shaders/Silicone*.ush
# → SiliconeFresnel.ush（其他 3 个模板列出的 USH 文件 0 hits 全工程）
```

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
  "subsurfaceProfile": "/Engine/EngineResources/DefaultSkin.DefaultSkin",
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

> **Source of truth**: 以下命令列表与 `Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterialModule.cpp::BuildAbilityInfoJson()` 注册表一致(LLMEasyShell dispatcher 仅放行注册的子命令)。
> 通用资产操作(创建/删除/复制/移动/查看/设置参数)由 **LLMEasyShell 主系统** 提供 (`new` `rm` `cp` `mv` `cat` `set`)，不在 material ability 重复注册。

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
- `--domain` - 材质域（Surface/PostProcess/UI/VirtualTexture）
- `--blending` - 混合模式（Opaque/Masked/Translucent/Additive）

**export**:
- `assetPath` - 要导出的材质资产路径
- `--output` - 输出 JSON 文件路径（可选，默认导出到 `Saved/Exported_<MaterialName>.llmmat`）

**export-schema**:
- `--output` - 输出 schema 文件路径（可选，默认导出到 `Config/MaterialExpressionSchema.llmschema`）

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
