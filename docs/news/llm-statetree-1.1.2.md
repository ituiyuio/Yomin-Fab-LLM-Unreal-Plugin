---
layout: doc
title: LLMStateTree v1.1.2 — UE 5.8 C4996 修复 + 4 个 NPC 对话样例
date: 2026-07-26
tag: Plugin
summary: |
  LLMStateTree v1.1.2 在初版 (2026-07-02) 修 UE 5.8 build C4996 deprecation + doc-fossil 的基础上，新增 4 个 NPC 对话 StateTree 样例（Reimu Priestess / Rumia Cat / Patchouli Oracle / Rumia Merchant），让 LLM agent 可以参考更复杂的多状态机拓扑。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8 全部 PASS。
emoji: 🌲
slug: llm-statetree-1.1.2
---

# LLMStateTree v1.1.2

> Patch bump — 主要修复 UE 5.8 编译告警并新增 NPC 对话样例。`.llmstate` DSL / StateTree 生成 API / 节点反射接口保持不变。

## ✨ 新增功能

- **4 个 NPC 对话 StateTree 样例** (`66a455f`) — `Config/Examples/NpcDialogs/` 目录新增 4 个完整的 NPC 对话状态机，每个 148 行：
  - `Npc_ReimuPriestess.llmstate` — 博丽巫女 (idle / greet / talk / farewell 多状态循环)
  - `Npc_RumiaCat.llmstate` — 宵暗妖怪 (猫形态巡游 + 玩家接近对话)
  - `Npc_PatchouliOracle.llmstate` — 魔法使 (知识问答 + 元素条件触发)
  - `Npc_RumiaMerchant.llmstate` — 商人 (买卖分支 + 价格比较)
  - LLM agent 可直接参考作为生成 NPC 对话 AI 的模板

## 🐛 修复

- **UE 5.8 上 2 处 C4996 deprecation warning** —
  `UE::StateTree::Delegates::OnRequestCompile` 在 UE 5.8 标记 deprecated，
  触发 C4996 warning 而 Fab marketplace scanner 把 C4996 当 error 处理。
  `statetree compile` 命令改走 `LLMStateTreeCompat::RecompileStateTree`：
  - UE 5.5-5.7：走旧 delegate（non-deprecated）
  - UE 5.8+：走 `UStateTreeEditingSubsystem::CompileStateTree`（canonical API）
- **doc-fossil "UE 5.7+"** 修正为 "UE 5.5+ (5.5/5.6/5.7/5.8 multi-UE build)"，
  涉及 `README.md` / `Documentation.md` / `VERSION-NOTES.md` 三处

## ⚡ 改进

- `LLMStateTreeCompatShim.h` 新增 `LLMSTATETREE_UE_5_8_PLUS` 编译期 detection macro
  和 `RecompileStateTree(UStateTree*)` 桥接函数，call site 不再散落 `#ifdef`

## 💥 破坏性变更

- 无

## 🔧 内部重构

- 多 UE compat shim 加第 4 个 bridge（compile API），跟既有 3 个 bridge
  （`MakeBinding` / `AddBindingToEditor` / `GetRootParametersBag` /
  `AddPropertyToBag`）保持一致的风格
- CRLF → LF renormalize (`7bf3d43`) — 567 文件行尾统一

---

**引擎支持**：UE 5.5（已测）、UE 5.6（已测）、UE 5.7（已测）、UE 5.8（已测）
— `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。

**文件格式**：`.llmstate`（JSON）、`.llmstateschema`（Schema）、`UStateTree`（UAsset）。

**Source 改动**：4 个 NPC 样例（4 files +592/-0）+ `LLMStateTreeCompatShim.h`（+50/-0 净）+
`LLMStateTreeCommandHandler.cpp`（+12/-6 净）+ 文档 3 处微调。

**验证**：4 UE `RunUAT BuildPlugin -rocket` 零 error / 零 C4996 / 零 C4701。