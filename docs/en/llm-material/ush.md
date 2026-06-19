# Custom HLSL

LLMMaterial supports writing HLSL shader code snippets in .llmmat files, generating .ush files for materials to reference. All generated .ush files are output to the unified directory `/Game/Shaders/`.

## functions - Inline Definition Generate .ush

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

### Field Description

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Function name, also used as .ush filename |
| `returnType` | No | Return type, default is float |
| `description` | No | Documentation comment |
| `parameters[].name` | Yes | Parameter name |
| `parameters[].type` | Yes | Parameter type (float, float2, float3, float4, etc.) |
| `parameters[].defaultValue` | No | Default value |
| `body` | Yes | HLSL function body, supports multiple lines |

## ushIncludes - Reference Existing .ush

```json
{
  "ushIncludes": [
    "/Game/Shaders/MyExistingFunc.ush"
  ]
}
```

## Custom Node HeaderRef - Reference Function

Use the `Custom` node and set the `HeaderRef` property to reference a function name. The system automatically generates `return FuncName(args);` call code:

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

### Priority

`HeaderRef` > `Code` (when both exist, HeaderRef takes precedence)

### Include Path Rules

- HeaderRef without `/`: Maps to `Shaders/{FuncName}.ush`
- HeaderRef with `/` or `.ush`: Used directly as include path

## Complete Example: Fresnel Material

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

### Generated .ush File

```hlsl
// /Game/Shaders/MyFresnel.ush
float MyFresnel(float3 Normal, float3 ViewDir, float Power) {
    float cosTheta = dot(Normal, ViewDir);
    return pow(1.0 - cosTheta, Power);
}
```

The Custom node automatically fills `Code = "return MyFresnel(Normal, ViewDir, Power);"`
