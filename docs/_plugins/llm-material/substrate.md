---
layout: default
title: Substrate 材质
parent: LLMMaterial
nav_order: 4
---

# Substrate 材质

LLMMaterial 支持 UE5 Substrate 分层材质系统。当 .llmmat 文件包含 `substrate` 字段时，系统自动使用 Substrate 路由模式。

## 路由模式

| 模式 | 条件 | 说明 |
|------|------|------|
| Traditional | 只有 `nodes` | 使用传统 Material Expression 构建 |
| Substrate | 只有 `substrate.slabs` | 完全 Substrate 管线 |
| Hybrid | `nodes` + `substrate.slabs` | Expression + Substrate 混合 |

## 基本结构

```json
{
  "version": "1.0",
  "name": "MySubstrateMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [...],
    "compositions": [...],
    "root": {...}
  }
}
```

## Slab 类型

| 类型 | 描述 | 关键输入 |
|------|------|----------|
| `SubstrateSlabBSDF` | 基础表面 BSDF（默认） | DiffuseAlbedo, Roughness, F0, Metallic, Normal |
| `SubstrateHairBSDF` | 头发 BSDF | BackboneRadius, Density, DirectVectorization |
| `SubstrateUnlitBSDF` | 无光照 BSDF | EmissiveRadiance |
| `SubstrateEyeBSDF` | 眼睛 BSDF | IrisDistance, PupilRadius |
| `SubstrateSingleLayerWaterBSDF` | 单层水面 | Extinction, Scattering |

## Composition 类型

| 类型 | 描述 | 必需字段 |
|------|------|----------|
| `VerticalLayering` | 垂直分层（上下叠层） | `top` slab ID |
| `HorizontalMixing` | 水平混合（两 slab 融合） | `slabA`, `slabB`, `MixRatio` |
| `Add` | 添加两 slab | `slabA`, `slabB` |
| `Weight` | 权重节点 | `slab` ID, `weight` |
| `Select` | 选择节点 | `slabA`, `slabB`, `Threshold` |

## Slab 输入值格式

```json
"inputs": {
  "DiffuseAlbedo": [0.8, 0.8, 0.8],   // RGB 数组 = Constant3Vector
  "Roughness": 0.3,                      // 标量 = Constant
  "F0": [0.04, 0.04, 0.04],           // RGB 数组（默认为 0.04 菲涅尔）
  "Metallic": 0.0,                      // 标量
  "Normal": "/Game/Textures/Normal",     // 纹理引用
  "BaseColor": { "node": "node_id" }    // 引用 Expression 节点 (Hybrid 模式)
}
```

## 示例：简单 Substrate 材质

```json
{
  "version": "1.0",
  "name": "SimpleSubstrate",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [
      {
        "id": "main_slab",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.8, 0.8, 0.8],
          "Roughness": 0.3,
          "F0": [0.04, 0.04, 0.04],
          "Metallic": 0.0
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "main_slab"
    }
  }
}
```

## 示例：双层材质

```json
{
  "version": "1.0",
  "name": "TwoLayerMaterial",
  "substrate": {
    "slabs": [
      {
        "id": "surface_layer",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.9, 0.85, 0.8],
          "Roughness": 0.15
        }
      },
      {
        "id": "base_layer",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.7, 0.65, 0.6],
          "Roughness": 0.6
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "surface_layer",
      "bottom": "base_layer",
      "topThickness": 0.01
    }
  }
}
```

## 注意事项

- **ShadingModel 自动切换**：Substrate 材质会自动将 ShadingModel 设为 `MSM_Strata`
- **Hybrid 模式**：`nodes` 中的 Expression 节点可以被 `substrate.slabs[].inputs[]` 中的 `{ "node": "node_id" }` 引用
- **纹理输入**：纹理使用资产路径字符串，系统自动创建 `TextureObject` 或 `TextureSample` 节点
- **不含 bottom 的 VerticalLayering**：当 root 只指定 `top` 时，Top slab 直接作为 root
