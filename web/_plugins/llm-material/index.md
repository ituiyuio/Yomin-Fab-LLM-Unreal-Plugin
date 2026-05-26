---
layout: default
title: LLMMaterial
has_children: true
nav_order: 2
---

# LLMMaterial

JSON驱动的 UE5 Material 资产生成系统。用 JSON 定义材质节点图，AI 输出 .llmmat 文件，自动生成可编译的 Material Blueprint 资产。

## 核心特性

- JSON ↔ Material 双向转换
- 完整 Expression 节点支持（30+ 类型）
- UE5 Substrate BSDF 材质支持
- 自定义 HLSL 函数（.ush）生成
- 自动节点布局（Sugiyama 算法）
- 编辑器内面板，导入/预览/生成
- SubsurfaceProfile 皮肤材质
- 纹理参数与采样支持
- Material Domain 与 Blend Mode 配置
- Schema 驱动的类型系统

## 快速预览

```json
{
  "version": "1.0",
  "name": "RedMetal",
  "domain": "Surface",
  "shadingModel": "DefaultLit",
  "nodes": [
    { "id": "color", "type": "Constant3Vector",
      "properties": { "Constant": [1.0, 0.0, 0.0] }}
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

## 支持的材质类型

| 分类 | 支持内容 |
|------|---------|
| Domain | Surface, PostProcess, UserInterface, VirtualTexture |
| BlendMode | Opaque, Masked, Translucent, Additive, Modulate |
| ShadingModel | DefaultLit, Unlit, Subsurface, SubsurfaceProfile, ClearCoat, Hair, Cloth, Eye, Strata |
| Substrate | SubstrateSlabBSDF, SubstrateHairBSDF, VerticalLayering, HorizontalMixing |

## 下一步

- [快速开始](getting-started.html) - 安装和基本使用
- [节点类型](node-types.html) - 所有支持的节点
- [Substrate](substrate.html) - UE5 Substrate 材质
- [完整示例](examples.html) - 各种材质类型示例
