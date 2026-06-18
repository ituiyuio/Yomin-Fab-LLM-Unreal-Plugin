---
layout: news-entry
title: Lite Shell 发布
date: 2026-06-10
tag: Skill
summary: |
  LLM Easy Shell 的只读子集 —— 9 个安全指令，适合让 agent 浏览场景和资产而不会有副作用。
emoji: 🔍
slug: lite-shell
---

# Lite Shell 发布

我们发布了 **LLM Easy Shell Lite**：Easy Shell 的只读子集，专为"安全浏览"设计。

## 9 个指令，全部只读

- `list_actors` / `inspect_actor` —— 浏览场景中的 actor
- `list_assets` / `inspect_asset` —— 浏览 `/Game/` 下的资产
- `get_property` —— 读取任意属性
- `screenshot` —— 截图当前视口
- `evaluate_python` —— 在受限沙箱里跑只读 Python

## 和完整版的关系

- Lite Shell 使用端口段 **15201–15250**（完整版是 15151–15200）
- 只依赖 2 个 engine plugin（`PythonScriptPlugin` + `EditorScriptingUtilities`）
- 完全免费，可直接装在只读工作流里

## 适用场景

- 文档 agent：让 AI 读懂工程现状
- 教学 agent：让 AI 演示但不修改
- CI agent：让 AI 在 PR 阶段做资产盘点
