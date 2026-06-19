# Node Types

## Math Operations

| Type | Description | Inputs | Output |
|------|-------------|--------|--------|
| `Add` | Addition | A, B | Result |
| `Subtract` | Subtraction | A, B | Result |
| `Multiply` | Multiplication | A, B | Result |
| `Divide` | Division | A, B | Result |
| `Power` | Power | Base, Exp | Result |
| `Sine` | Sine | Input | Result |
| `Cosine` | Cosine | Input | Result |
| `Abs` | Absolute value | Input | Result |
| `Clamp` | Clamp range | Input, Min, Max | Result |
| `Lerp` | Linear interpolation | A, B, Alpha | Result |
| `Max` | Maximum | A, B | Result |
| `Min` | Minimum | A, B | Result |

## Constants

| Type | Description | Properties |
|------|-------------|------------|
| `Constant` | Scalar constant | `Value` (float) |
| `Constant2Vector` | 2D vector | `Constant` [X, Y] |
| `Constant3Vector` | 3D vector/color | `Constant` [R, G, B] |
| `Constant4Vector` | 4D vector/color+alpha | `Constant` [R, G, B, A] |

## Textures

| Type | Description | Properties | Output |
|------|-------------|------------|--------|
| `TextureSample` | Texture sampling | `Texture` (asset path) | RGB, R, G, B, A |
| `TextureCoordinate` | UV coordinates | `CoordinateIndex` | UV |

## Parameters

| Type | Description | Properties |
|------|-------------|------------|
| `ScalarParameter` | Scalar parameter | `ParameterName`, `DefaultValue` |
| `VectorParameter` | Vector parameter | `ParameterName`, `DefaultValue` |
| `TextureSampleParameter` | Texture parameter | `ParameterName`, `Texture` |

## Coordinates

| Type | Description | Output |
|------|-------------|--------|
| `VertexColor` | Vertex color | RGB, R, G, B, A |
| `WorldPosition` | World position | XYZ |
| `CameraPosition` | Camera position | XYZ |
| `Time` | Time | - |

## Utility

| Type | Description | Inputs | Output |
|------|-------------|--------|--------|
| `ComponentMask` | Channel mask | Input | R, G, B, A |
| `AppendVector` | Vector append | A, B | Result |
| `Desaturation` | Desaturation | Input, Fraction | Result |

## Custom HLSL

| Type | Description | Properties | Inputs |
|------|-------------|------------|--------|
| `Custom` | Custom HLSL code | `Code` or `HeaderRef` + `OutputType` | Dynamic (defined via Inputs) |

### Custom Node Properties

- `Code` - Directly written HLSL code
- `HeaderRef` - References function defined in `functions`
- `OutputType` - Output type: `CMOT_Float1`/`CMOT_Float2`/`CMOT_Float3`/`CMOT_Float4`
- `Description` - Node description
- `Inputs` - Dynamic input pin array: `[{"InputName": "Param1"}, {"InputName": "Param2"}]`

## Common Pin Names

### Outputs
- `Result` - Result output
- `RGB` - RGB channel
- `R`, `G`, `B`, `A` - Single channel outputs
- `XYZ` - Three-channel output
- `UV` - Texture coordinates

### Inputs
- `A`, `B` - Math operation inputs
- `Base`, `Exp` - Power operation inputs
- `UVs`, `Input` - General inputs
- `Min`, `Max` - Range limits
- `Alpha` - Interpolation factor
- `Fraction` - Desaturation factor
