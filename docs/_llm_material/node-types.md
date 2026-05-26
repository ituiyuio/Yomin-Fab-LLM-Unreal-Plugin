---
layout: default
title: 节点类型
parent: LLMMaterial
nav_order: 3
---

# 节点类型

## 数学运算

| 类型 | 描述 | 输入 | 输出 |
|------|------|------|------|
| `Add` | 加法 | A, B | Result |
| `Subtract` | 减法 | A, B | Result |
| `Multiply` | 乘法 | A, B | Result |
| `Divide` | 除法 | A, B | Result |
| `Power` | 幂运算 | Base, Exp | Result |
| `Sine` | 正弦 | Input | Result |
| `Cosine` | 余弦 | Input | Result |
| `Abs` | 绝对值 | Input | Result |
| `Clamp` | 限制范围 | Input, Min, Max | Result |
| `Lerp` | 线性插值 | A, B, Alpha | Result |
| `Max` | 最大值 | A, B | Result |
| `Min` | 最小值 | A, B | Result |

## 常量

| 类型 | 描述 | 属性 |
|------|------|------|
| `Constant` | 标量常量 | `Value` (float) |
| `Constant2Vector` | 2D 向量 | `Constant` [X, Y] |
| `Constant3Vector` | 3D 向量/颜色 | `Constant` [R, G, B] |
| `Constant4Vector` | 4D 向量/颜色+Alpha | `Constant` [R, G, B, A] |

## 纹理

| 类型 | 描述 | 属性 | 输出 |
|------|------|------|------|
| `TextureSample` | 纹理采样 | `Texture` (资产路径) | RGB, R, G, B, A |
| `TextureCoordinate` | UV 坐标 | `CoordinateIndex` | UV |

## 参数

| 类型 | 描述 | 属性 |
|------|------|------|
| `ScalarParameter` | 标量参数 | `ParameterName`, `DefaultValue` |
| `VectorParameter` | 向量参数 | `ParameterName`, `DefaultValue` |
| `TextureSampleParameter` | 纹理参数 | `ParameterName`, `Texture` |

## 坐标

| 类型 | 描述 | 输出 |
|------|------|------|
| `VertexColor` | 顶点颜色 | RGB, R, G, B, A |
| `WorldPosition` | 世界坐标 | XYZ |
| `CameraPosition` | 相机位置 | XYZ |
| `Time` | 时间 | - |

## 工具

| 类型 | 描述 | 输入 | 输出 |
|------|------|------|------|
| `ComponentMask` | 通道遮罩 | Input | R, G, B, A |
| `AppendVector` | 向量组合 | A, B | Result |
| `Desaturation` | 去饱和 | Input, Fraction | Result |

## 自定义 HLSL

| 类型 | 描述 | 属性 | 输入 |
|------|------|------|------|
| `Custom` | 自定义 HLSL 代码 | `Code` 或 `HeaderRef` + `OutputType` | 动态（通过 Inputs 定义） |

### Custom 节点属性

- `Code` - 直接写入的 HLSL 代码
- `HeaderRef` - 引用 `functions` 中定义的函数名
- `OutputType` - 输出类型：`CMOT_Float1`/`CMOT_Float2`/`CMOT_Float3`/`CMOT_Float4`
- `Description` - 节点描述
- `Inputs` - 动态输入引脚数组：`[{"InputName": "Param1"}, {"InputName": "Param2"}]`

## 常见引脚名称

### 输出
- `Result` - 结果输出
- `RGB` - RGB 通道
- `R`, `G`, `B`, `A` - 单通道输出
- `XYZ` - 三通道输出
- `UV` - 纹理坐标

### 输入
- `A`, `B` - 数学运算输入
- `Base`, `Exp` - 幂运算输入
- `UVs`, `Input` - 通用输入
- `Min`, `Max` - 范围限制
- `Alpha` - 插值因子
- `Fraction` - 去饱和因子
