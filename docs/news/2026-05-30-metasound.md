---
title: MetaSound 插件上线
date: 2026-05-30
tag: Plugin
summary: |
  第四个插件 —— LLM MetaSound —— 上线。从 JSON 编译 UMetaSoundSource 和 UMetaSoundPatch。
emoji: 🔊
slug: metasound
---

# MetaSound 插件上线

我们发布了 **LLM MetaSound** 插件：第四个"JSON → 资产"家族的成员。

## 能生成什么

- `UMetaSoundSource` —— 完整 MetaSound 资产
- `UMetaSoundPatch` —— 子图 / patch
- 支持 **generators / filters / envelopes / mixers / bus IO** 全节点类型
- 节点自动连接 —— 写 JSON 时不需要画线

## 一个例子

```json
{
  "version": "1.0",
  "name": "Kick",
  "type": "Source",
  "graph": {
    "nodes": [
      { "id": "osc", "type": "SineOscillator", "params": { "frequency": 60 } },
      { "id": "env", "type": "ADEnvelope",     "params": { "attack": 0.001, "decay": 0.12 } },
      { "id": "out", "type": "Output" }
    ],
    "connections": [
      { "from": "osc", "to": "env" },
      { "from": "env", "to": "out" }
    ]
  }
}
```

## 上哪里

- 仓库：`skills/llm-metasound/SKILL.md`
- Wiki：`/llm-metasound/`
- Fab 列表：准备中
