---
layout: default
title: 快速开始
parent: LLMMaterial
nav_order: 2
---

# 快速开始

## 安装

1. 将 `LLMMaterial` 插件复制到项目的 `Plugins/` 目录
2. 在 UE 编辑器中启用插件（Edit → Plugins → AI → LLMMaterial）
3. 重启编辑器

## 创建第一个材质

### Step 1: 编写 JSON 文件

创建一个 `MyRedMaterial.llmmat` 文件：

```json
{
  "version": "1.0",
  "name": "MyRedMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": {
        "Constant": [1.0, 0.0, 0.0]
      }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

### Step 2: 生成材质资产

在编辑器中打开 LLMMaterial 面板（Window → LLMMaterial），或使用命令行：

```bash
material generate /Game/Materials/MyRedMaterial --from MyRedMaterial.llmmat
```

### Step 3: 查看结果

生成的 Material 资产会自动打开，你可以在 Material Editor 中进一步调整。

## 文件格式详解

### 基本结构

```json
{
  "version": "1.0",           // 版本号
  "name": "MaterialName",     // 材质名称
  "domain": "Surface",        // 材质域
  "blendMode": "Opaque",      // 混合模式
  "shadingModel": "DefaultLit", // 着色模型
  "nodes": [...],             // 节点数组
  "connections": [...],       // 连接数组（可选）
  "output": {...}            // 输出配置
}
```

### 节点定义

```json
{
  "id": "uniqueNodeId",       // 节点唯一标识符
  "type": "Constant3Vector",   // 节点类型
  "displayName": "My Color",   // 显示名称（可选）
  "properties": {              // 节点属性
    "PropertyName": "value"
  }
}
```

### 输出配置

```json
"output": {
  "baseColor": { "node": "color", "pin": "Result" },
  "metallic": 1.0,
  "roughness": 0.5,
  "normal": { "node": "normalTex", "pin": "RGB" },
  "emissive": { "node": "emissive", "pin": "Result" }
}
```

## 使用编辑器面板

LLMMaterial 提供了一个三栏式编辑器面板：

- **文件列表**（左）：管理 .llmmat 文件
- **节点树**（中）：查看材质结构
- **属性面板**（右）：编辑节点属性

### 工具栏按钮

- **Generate**：从选中的 .llmmat 文件生成材质
- **Export Material**：将现有材质导出为 JSON
- **Export Schema**：导出表达式 Schema 参考
