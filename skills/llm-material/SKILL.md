---
name: llm-material
description: |
  LLMMaterial is a DSL-driven UE5 Material asset generation system. Use this skill when users need to:
  (1) Create or design UE5 Materials (surface, translucent, emissive, etc.)
  (2) Convert material descriptions into generatable DSL format (.llmmat JSON)
  (3) Understand or modify existing Material DSL definitions
  (4) Learn about supported Expression node types (Add, Multiply, TextureSample, etc.)
  (5) Query Material Graph connection methods and output settings
  (6) Write HLSL shader functions (.ush) and reference them in materials
---

# LLMMaterial - DSL Schema Guide

### **Composition Over Inheritance**

## File Format

Material definition files use the `.llmmat` extension (LLM Material DSL), formatted as JSON.

## Reference Files

**Expression Schema**: `Plugins/LLMMaterial/Content/MaterialExpressionSchema.json` - Contains complete definitions for all Material Expression nodes (inputs, outputs, properties)

**Examples Directory**: `Plugins/LLMMaterial/Content/Examples/` - Contains complete material example `.llmmat` files

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

## Shader Headers (USH) - HLSL Function Support

LLMMat supports writing HLSL shader code snippets in `.llmmat` files, generating `.ush` files for materials to reference. All generated `.ush` files are output to `/Game/Shaders/`.

### `functions` - Inline Definition Generating .ush

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

Field description:
- `name` (required) - Function name, also used as `.ush` filename
- `returnType` (optional, default `float`) - Return type
- `description` (optional) - Documentation comment
- `parameters[].name` (required) - Parameter name
- `parameters[].type` (required) - Parameter type (`float`, `float2`, `float3`, `float4`, etc.)
- `parameters[].defaultValue` (optional) - Default value
- `body` (required) - HLSL function body, supports multiple lines

### `ushIncludes` - Reference Existing .ush

```json
{
  "ushIncludes": [
    "/Game/Shaders/MyExistingFunc.ush"
  ]
}
```

### Custom Node `HeaderRef` - Reference Functions

Use `Custom` node and set `HeaderRef` property to reference a function name. The system automatically generates `return FuncName(args);` call code:

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

**Priority**: `HeaderRef` > `Code` (when both exist, `HeaderRef` takes precedence)

**Include Path Rules**:
- `HeaderRef` without `/`: maps to `Shaders/{FuncName}.ush`
- `HeaderRef` with `/` or `.ush`: used directly as include path

### Full Example: Fresnel Material

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

Generated `.ush` files:
```
/Game/Shaders/
  MyFresnel.ush    ← auto-generated
```

Custom node automatically fills `Code = "return MyFresnel(Normal, ViewDir, Power);"`.

## Color Formats

Multiple color formats are supported:

| Format | Example | Description |
|--------|---------|-------------|
| RGB array | `[1.0, 0.0, 0.0]` | Float values 0-1 |
| RGBA array | `[1.0, 0.0, 0.0, 1.0]` | With alpha |
| Hex | `"#FF0000"` | Hexadecimal color |
| Scalar | `0.5` | For single-channel like Metallic/Roughness |

## Node Types (Expression Node Types)

### Math Operations
| Type | Description | Inputs | Outputs |
|------|-------------|--------|---------|
| `Add` | Addition | A, B | Result |
| `Multiply` | Multiplication | A, B | Result |
| `Subtract` | Subtraction | A, B | Result |
| `Divide` | Division | A, B | Result |
| `Power` | Power | Base, Exp | Result |
| `Sine` / `Cosine` | Sine/Cosine | Input | Result |
| `Abs` | Absolute value | Input | Result |
| `Min` / `Max` | Min/Max | A, B | Result |
| `Clamp` | Clamp range | Input, Min, Max | Result |
| `Lerp` | Linear interpolation | A, B, Alpha | Result |

### Constants
| Type | Description | Properties |
|------|-------------|------------|
| `Constant` | Scalar constant | Value (float) |
| `Constant2Vector` | 2D vector | Constant [X, Y] |
| `Constant3Vector` | 3D vector/color | Constant [R, G, B] |
| `Constant4Vector` | 4D vector/color+Alpha | Constant [R, G, B, A] |

### Textures
| Type | Description | Properties | Inputs | Outputs |
|------|-------------|------------|--------|---------|
| `TextureSample` | Texture sample | Texture (path) | UVs | RGB, R, G, B, A |
| `TextureCoordinate` | UV coordinates | CoordinateIndex | - | UV |

### Parameters
| Type | Description | Properties |
|------|-------------|------------|
| `ScalarParameter` | Scalar parameter | ParameterName, DefaultValue |
| `VectorParameter` | Vector parameter | ParameterName, DefaultValue |
| `TextureSampleParameter` | Texture parameter | ParameterName, Texture |

### Coordinates
| Type | Description | Outputs |
|------|-------------|---------|
| `VertexColor` | Vertex color | RGB, R, G, B, A |
| `WorldPosition` | World position | XYZ |
| `CameraPosition` | Camera position | XYZ |
| `Time` | Time | - |

### Utilities
| Type | Description | Inputs | Outputs |
|------|-------------|--------|---------|
| `ComponentMask` | Channel mask | Input | R, G, B, A (based on mask config) |
| `AppendVector` | Vector append | A, B | Result |
| `Desaturation` | Desaturation | Input, Fraction | Result |

### Custom (HLSL)
| Type | Description | Properties | Inputs |
|------|-------------|------------|--------|
| `Custom` | Custom HLSL code | `Code` or `HeaderRef`+`OutputType`+`Inputs` | Dynamic (defined via Inputs) |

**Property Description**:
- `Code` - Directly written HLSL code (e.g., `return sin(vormal) * 0.5 + 0.5;`)
- `HeaderRef` - References function name defined in `functions`, auto-generates `return FuncName(args);`
- `OutputType` - Output type: `CMOT_Float1`/`CMOT_Float2`/`CMOT_Float3`/`CMOT_Float4`
- `Description` - Node description
- `Inputs` - Dynamic input pin array: `[{"InputName": "Param1"}, {"InputName": "Param2"}]`

**Note**: `HeaderRef` has higher priority than `Code`. When both exist, `HeaderRef` is used.

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

**Required Fields**:
- `id` - Unique node identifier (used for connection references)
- `type` - Expression type name (e.g., "Add", "Multiply", "TextureSample")

**Optional Fields**:
- `displayName` - Display name (shown in editor)
- `properties` - Node property configuration

## Connection Format

```json
{
  "from": "sourceNodeId",
  "fromPin": "outputPinName",
  "to": "targetNodeId",
  "toPin": "inputPinName"
}
```

**Connection Fields**:
- `from` - Source node ID
- `fromPin` - Source node output pin name (e.g., "Result", "RGB")
- `to` - Target node ID
- `toPin` - Target node input pin name (e.g., "A", "B", "BaseColor")

**Common Pin Names**:
- Output: `Result`, `RGB`, `R`, `G`, `B`, `A`
- Input: `A`, `B`, `Base`, `Exp`, `UVs`, `Input`

## Material Outputs

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

**Output Types**:
- `baseColor` - Base color (RGB)
- `metallic` - Metallic (0-1)
- `roughness` - Roughness (0-1)
- `specular` - Specular (0-1)
- `normal` - Normal map (RGB)
- `emissive` - Emissive (RGB)
- `opacity` - Opacity (0-1)
- `opacityMask` - Opacity mask (0-1)
- `worldPositionOffset` - World position offset (XYZ)

**Output Formats**:
- Node reference: `{ "node": "nodeId", "pin": "outputName" }`
- Constant value: `0.5` or `"#FF0000"` or `[1.0, 0.0, 0.0]`

## Material Properties

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

**Domain**:
- `Surface` - Surface material (default)
- `PostProcess` - Post-process material
- `UserInterface` - UI material
- `VirtualTexture` - Virtual texture

**BlendMode**:
- `Opaque` - Opaque (default)
- `Masked` - Masked (uses OpacityMask)
- `Translucent` - Translucent
- `Additive` - Additive
- `Modulate` - Modulate

**ShadingModel**:
- `DefaultLit` - Default Lit (default)
- `Unlit` - Unlit
- `Subsurface` - Subsurface (requires SubsurfaceColor output)
- `SubsurfaceProfile` - SubsurfaceProfile asset (requires subsurfaceProfile property)
- `ClearCoat` - Clear Coat
- `Hair` - Hair
- `Cloth` - Cloth
- `Eye` - Eye
- `TwoSidedFoliage` - Two Sided Foliage
- `SingleLayerWater` - Single Layer Water
- `ThinTranslucent` - Thin Translucent
- `Strata` - Strata

**SubsurfaceProfile Asset Reference**:
When `shadingModel` is `SubsurfaceProfile`, the system automatically creates a SubsurfaceProfile asset (if it doesn't exist). Optionally specify the `subsurfaceProfile` property:

```json
{
  "shadingModel": "SubsurfaceProfile",
  "subsurfaceProfile": "/Game/Materials/MySkinSSS.MySkinSSS"
}
```

If `subsurfaceProfile` is not specified, the system automatically creates a `{MaterialName}_SSS` SubsurfaceProfile asset in the same directory as the material, containing parameters suitable for skin/silicone rendering (Burley SSS model, AFIS high-quality rendering).

## Substrate Materials (UE5 Substrate)

LLMMaterial supports UE5 Substrate layered material system. When a `.llmmat` file contains a `substrate` field, the system automatically uses Substrate routing mode.

### Substrate Routing Modes

| Mode | Condition | Description |
|------|-----------|-------------|
| Traditional | Only `nodes` | Use traditional Material Expression construction |
| Substrate | Only `substrate.slabs` | Full Substrate pipeline |
| Hybrid | `nodes` + `substrate.slabs` | Expression + Substrate mixed |

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

### Slab Types

| Type | Description | Key Inputs |
|------|-------------|------------|
| `SubstrateSlabBSDF` | Base surface BSDF (default) | DiffuseAlbedo, Roughness, F0, Metallic, Normal |
| `SubstrateHairBSDF` | Hair BSDF | BackboneRadius, Density, DirectVectorization, etc. |
| `SubstrateUnlitBSDF` | Unlit BSDF | EmissiveRadiance |
| `SubstrateEyeBSDF` | Eye BSDF | IrisDistance, PupilRadius, etc. |
| `SubstrateSingleLayerWaterBSDF` | Single layer water | Extinction, Scattering |

### Composition Types

| Type | Description | Required Fields |
|------|-------------|----------------|
| `VerticalLayering` | Vertical layering (top/bottom stack) | `top` slab ID |
| `HorizontalMixing` | Horizontal mixing (two slab fusion) | `slabA`, `slabB`, `MixRatio` |
| `Add` | Add two slabs | `slabA`, `slabB` |
| `Weight` | Weight node | `slab` ID, `weight` |
| `Select` | Select node | `slabA`, `slabB`, `Threshold` |

### Root Composition Notes

- If `root` only has `top` (no `bottom`), the top slab is used directly as root
- `topThickness` defaults to 0.01
- `bUseParameterBlending` defaults to false

### Slab Input Value Format

```json
"inputs": {
  "DiffuseAlbedo": [0.8, 0.8, 0.8],   // RGB array = Constant3Vector
  "Roughness": 0.3,                      // Scalar = Constant
  "F0": [0.04, 0.04, 0.04],             // RGB array (default 0.04 Fresnel)
  "Metallic": 0.0,                       // Scalar
  "Normal": "/Game/Textures/Normal",      // Texture reference
  "BaseColor": { "node": "node_id" }     // Reference Expression node (Hybrid mode)
}
```

### Substrate Notes

1. **ShadingModel Auto-Switch**: Substrate materials automatically set ShadingModel to `MSM_Strata`
2. **Hybrid Mode**: Expression nodes in `nodes` can be referenced in `substrate.slabs[].inputs[]` via `{ "node": "node_id" }`. Supported keys: `node`, `nodeId`, `node_id`, `nodeRef` (all equivalent)
3. **Texture Inputs**: Textures use asset path strings, the system automatically creates `TextureObject` or `TextureSample` nodes
4. **VerticalLayering without bottom**: When root only specifies `top`, the top slab is used directly as root (no VerticalLayering node needed)

## Common Patterns

### Simple Color Material
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

### Texture Material
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

### Metal Material
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

### Translucent Glass Material
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

### Color + Texture Blend
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

### Subsurface Skin Material (SubsurfaceProfile)
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
    { "from": "fresnel", "fromPin": "Output", "to": "sssEmissive", "toPin": "A" },
    { "from": "skinColor", "fromPin": "Result", "to": "sssEmissive", "toPin": "B" }
  ],
  "output": {
    "baseColor": { "node": "skinColor", "pin": "Result" },
    "roughness": { "node": "roughness", "pin": "Result" },
    "emissive": { "node": "sssEmissive", "pin": "Result" }
  }
}
```

### Normal Map Material
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

### Emissive Material
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

## Schema Reference

View complete Expression type definitions:
```
Plugins/LLMMaterial/Content/MaterialExpressionSchema.json
```
