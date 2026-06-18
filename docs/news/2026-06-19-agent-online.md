---
title: Agent Online
date: 2026-06-19
tag: Release
summary: |
  AI 代理现可通过 LLM Easy Shell 直连 Unreal Editor — 27 个原生指令 + 25 个 Python 子指令，覆盖 actor 操作、属性编辑、Live Coding、截图。
emoji: ⚡
slug: agent-online
---

# Agent Online

我们刚刚把 **LLM Easy Shell** 升级到了"Agent Online"阶段 —— AI 代理现在可以直接驱动一个正在运行的 Unreal Editor。

## 这次能做什么

- **27 个原生指令** 覆盖 actor 增删改查、属性编辑、关卡管理
- **25 个 Python 子指令** 调用任何 `unreal` 模块 API
- **Live Coding** 触发：让 agent 改完 C++ 自动热重载
- **截图拉回**：agent 可以"看到"编辑器画面（PNG via TCP）

## 为什么是"Online"

之前的 Easy Shell 是离线管线（agent 写 JSON → 编译资产）。这次升级后，agent
和 Editor 之间有一条 **TCP 长连接**（端口 15151–15200），agent 可以在 loop
里反复"探查 → 编辑 → 截图验证"，形成真正的反馈环。

## 怎么开始

```bash
# 在 Editor 里
Edit → Plugins → LLM Easy Shell → Enable → Restart
# TCP 端口会自动分配，状态写到 .current_port
```

接着让你的 agent 读 `skills/llm-easy-shell/SKILL.md` 即可上手。
