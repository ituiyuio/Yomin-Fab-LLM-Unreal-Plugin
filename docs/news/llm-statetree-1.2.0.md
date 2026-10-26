---
layout: doc
title: LLMStateTree v1.2.0 — Agent 命令面 9 子命令 + 契约硬化
date: 2026-10-26
tag: Plugin
summary: |
  LLMStateTree v1.2.0 把插件升级为 agent-first：`llmstatetree` 命令面扩到 9 个子命令（新增 preview / nodes / schema），LLM agent 可免写资产预解析、反射列出项目实际可用节点、导出节点 schema 快照。同一批完成 DSL 契约硬化：往返保真修齐（此前 export→re-import 丢全部参数）、未识别词表从静默默认改为报错、弃用告警透出到 agent 信封。样例语料扩到 7 个并兼任往返回归语料。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8 全部 PASS。
emoji: 🌲
slug: llm-statetree-1.2.0
---

# LLMStateTree v1.2.0

> Minor bump — 新增 agent 命令面与样例，同时 DSL 校验从严（见破坏性变更）。引擎兼容范围不变：5.5 / 5.6 / 5.7 / 5.8。

## ✨ 新增功能

- **Agent 命令面：`llmstatetree` 9 子命令** (`d11041e38`) — `generate` / `preview` / `nodes` / `schema` / `inspect` / `export` / `copy` / `delete` / `compile`
  - `preview` — 解析 `.llmstate` 不写资产，供 LLM 干跑验证
  - `nodes` — 按反射列出**本项目**实际可用的 StateTree 节点类型（权威清单；随包 schema 只是快照）
  - `schema` — 把节点 schema 落到文件，供 agent 离线查阅
- **节点用户名** (`d11041e38`) — task / condition / evaluator 现在可以从 DSL 携带用户命名，往返不再丢
- **2 个新样例，语料至 7 个** (`d11041e38`) — `FlatFormatAI.llmstate`（扁平输入格式：稳定 `id` + `parent` 链接 + 顶层 transitions 数组）与 `DslLab.llmstate`（DSL 特性全集夹具：全部参数类型 / 条件类型 / 操作数 / 触发器 / 优先级 / 延迟 / consideration）。样例兼任回归语料：往返门禁对每个样例跑 preview → generate → export → generate → export 双重比对

## 🐛 修复缺陷

- **往返保真** (`d11041e38`) — Serializer 把参数写成数组而 Parser 按对象读，export→re-import 会静默丢掉全部参数；已修齐。`linkedAsset` / `eventTag` / `delayed` 转移字段补解析，旧形态文档仍兼容
- **`delete --force` 真生效；重写保护真拦截；重复状态名报错** (`d11041e38`) — 此前三者都是静默失效
- **根状态 `type: "Group"` 不再静默降级为 State** (`d11041e38`) — 降级会连带丢掉 group 的 SelectionBehavior

## 💥 破坏性变更

- **校验从严** (`d11041e38`) — 未识别的绑定域 / 触发器 / 转移类型 / 优先级 / 状态类型 / 选择行为 / 操作数从「静默落默认值」一律改为报错
- **版本相关词表** — 转移类型 `Parent` / `NextParent` / `NextSelectableParent` 需 UE 5.8，操作数 `Multiply` 需 UE 5.7；旧引擎上使用会得到明确报错（本批修复同时补齐了这些词条在 5.5-5.7 的编译门槛）
- **NpcDialogs 样例移出分发包** (`7dfb41a0e`) — 4 个项目专属 NPC 对话文件不再随插件分发（迁至项目专属插件），通用包保持项目无关

## ⚡ 改进

- **告警真管道** (`d11041e38`) — 解析弃用/校验告警此前只进引擎日志，agent 信封看不到；现在随 preview / generate 结果信封透出
- **多 UE 编译加固** (`d11041e38` + 本批) — 新契约面在 5.5 / 5.6 / 5.7 / 5.8 四引擎全量 `-rocket` 编译通过（0 错 0 警）
