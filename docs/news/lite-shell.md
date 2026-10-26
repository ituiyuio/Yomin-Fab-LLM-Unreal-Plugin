---
layout: doc
title: Lite Shell 发布
date: 2026-06-10
tag: Skill
summary: |
  LLM Easy Shell 的最精简子集 —— 9 个只读查询指令 + 1 个自维护指令，适合让 agent 浏览场景和资产。
emoji: 🔍
slug: lite-shell
---

# Lite Shell 发布

我们发布了 **LLM Easy Shell Lite**：Easy Shell 的最精简子集，专为"安全浏览"设计。

> **2026-10-26 勘误**：本文原版列了 7 个从未存在过的指令名（`list_actors` / `inspect_actor` 等），
> 并声称 `evaluate_python` "在受限沙箱里跑只读 Python"。两者都不成立 —— 下方是真实指令集，
> 且 PyAbility runtime 给的是**完整 UE Python API、无沙箱**（只读与否由你的代码负责）。
> 诚实的读写边界见 `skills/llm-easy-shell-lite/SKILL.md`。

## 9 个只读查询指令 + 1 个自维护指令

- `ls` / `cat` / `find` / `discover` / `info` / `help` —— 浏览 actor、组件、资产、类、函数与属性
- `gamestate` —— 查询 PIE 状态（wave / health / gold / enemies，启发式）
- `log --errors` / `msglog --niagara` —— 编辑器错误日志、Niagara 验证消息
- `livecoding --status`（别名 `reload` / `lc`，Windows only）—— LiveCoding 编译状态；触发编译是自维护动作，不算只读

## 和完整版的关系

- Lite Shell 使用端口段 **15201–15250**（完整版是 15151–15200）
- 只依赖 2 个 engine plugin（`PythonScriptPlugin` + `EditorScriptingUtilities`）
- 完全免费，可直接装在只读工作流里 —— 但注意：Lite 能直接调到的第三方 plugin ability
  （`material` / `ui` / `metasound` 的 generate / delete / compile 等）**不经过** Lite 过滤；
  Lite 是观测面，不是权限面

## 适用场景

- 文档 agent：让 AI 读懂工程现状
- 教学 agent：让 AI 演示但不修改
- CI agent：让 AI 在 PR 阶段做资产盘点
