---
layout: default
title: 自定义 HLSL
parent: LLMMaterial
nav_order: 6
---

# 自定义 HLSL

LLMMaterial 支持在 .llmmat 中编写 HLSL 着色器代码片段，生成 .ush 文件供材质引用。所有生成的 .ush 文件输出到统一目录 `/Game/Shaders/`。

## functions - 内联定义生成 .ush

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

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 是 | 函数名，同时作为 .ush 文件名 |
| `returnType` | 否 | 返回类型，默认 float |
| `description` | 否 | 文档注释 |
| `parameters[].name` | 是 | 参数名 |
| `parameters[].type` | 是 | 参数类型（float, float2, float3, float4 等） |
| `parameters[].defaultValue` | 否 | 默认值 |
| `body` | 是 | HLSL 函数体，支持多行 |

## ushIncludes - 引用已有 .ush

```json
{
  "ushIncludes": [
    "/Game/Shaders/MyExistingFunc.ush"
  ]
}
```

## Custom 节点 HeaderRef - 引用函数

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

### 优先级

`HeaderRef` > `Code`（两者同时存在时，HeaderRef 优先）

### Include 路径规则

- HeaderRef 不含 `/`：映射为 `Shaders/{FuncName}.ush`
- HeaderRef 含 `/` 或 `.ush`：直接作为 include 路径

## 完整示例：Fresnel 材质

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

### 生成的 .ush 文件

```hlsl
// /Game/Shaders/MyFresnel.ush
float MyFresnel(float3 Normal, float3 ViewDir, float Power) {
    float cosTheta = dot(Normal, ViewDir);
    return pow(1.0 - cosTheta, Power);
}
```

Custom 节点自动填充 `Code = "return MyFresnel(Normal, ViewDir, Power);"`
