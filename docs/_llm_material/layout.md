---
layout: default
title: 自动布局
parent: LLMMaterial
nav_order: 7
---

# 自动布局

当 `material generate` 生成材质时，节点会自动按拓扑顺序排列。

## 布局规则

- **数据流方向**：从左到右，Source 节点（Constant/Parameter/Texture）→ 运算节点 → 输出
- **列距**：280px（可配置）
- **Y轴对齐**：所有列共享同一全局行网格，节点按分类对号入行
- **孤立节点**：位于最左侧列下方

## 全局行网格对齐算法

1. 计算最大列节点数 `MaxNodesInColumn`
2. 构建全局行网格：`RowGrid[i] = GridOriginY - (MaxNodesInColumn - 1) * RowHeight * 0.5 + i * RowHeight`
3. 每个节点按分类行号放置：Source → Row 0, Operator → Row 1, Utility → Row 2, Other → 最后

## 节点分类排序

同列内节点按以下顺序排列：

1. **Source**（常量/参数/纹理）→ Row 0（顶部）
2. **Operator**（数学运算）→ Row 1
3. **Utility**（遮罩/变换/插值）→ Row 2
4. **Other** → 后续行

## 布局算法

- 基于 Sugiyama 分层布局（BFS 拓扑排序）
- 双向重心排序减少连线交叉
- 支持回路处理（放在最后一列）
- 全局行网格确保所有列节点列对齐

## 修改布局参数

布局参数位于：`Plugins/LLMMaterial/Source/LLMMaterial/Builder/MaterialGraphBuilder.cpp`

函数 `LayoutNodes()` 中的常量：

- `ColumnWidth` - 列宽
- `RowHeight` - 行高
- `SourceColX` - 源节点列 X 坐标
- `GridOriginY` - 网格原点 Y 坐标

## 示例

给定以下节点定义：

```json
{
  "nodes": [
    { "id": "color", "type": "Constant3Vector" },
    { "id": "roughness", "type": "Constant" },
    { "id": "multiply", "type": "Multiply" }
  ],
  "connections": [
    { "from": "color", "to": "multiply" },
    { "from": "roughness", "to": "multiply" }
  ]
}
```

自动布局结果：

```
Column 0 (Source):     Column 1 (Operator):
[color]────────────→[multiply]
[roughness]────────→|
```
