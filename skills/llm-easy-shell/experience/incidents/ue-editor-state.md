---
name: ue-editor-state
description: Unreal Engine editor state tracking — llm-easy-shell 必须感知 UE 状态才能安全操作
type: project
---

# UE 编辑器状态与安全操作

## 关键状态及其含义

| 状态 | 触发时机 | llm-easy-shell 行为 |
|------|----------|---------------------|
| `Idle` | 编辑器正常空闲 | 可执行命令 |
| `Preparing Patch` | 热重载时编译 patch | **完全阻塞**，所有命令超时 → 需等待 |
| `Reloading` | Patch 编译完成，应用 reload | 短暂阻塞 |
| `Compiling` | 蓝图/C++ 编译中 | 可能阻塞，命令可能超时 |
| `PIE` / `SIE` | Play-in-Editor / Simulate | 特定命令不可用 |
| `Saving` | 编辑器正在保存资产 | 短暂阻塞 |

## 现状

目前 llm-easy-shell **没有**状态感知机制。每次操作都假设编辑器处于 Idle 状态，但实际上：
- 热重载（`FModuleManager::ReloadModules`）会触发 Preparing Patch → Reloading，期间编辑器阻塞
- 用户手动编译 C++ 也会触发阻塞
- PIE 状态下某些 Actor 操作行为不同

## 待解决

**方案 A**：命令执行前先 ping 编辑器（如发送一个无害的 `echo` 或读取 editor actor 数量），超时则判定为非 Idle 状态，告知用户等待。

**方案 B**：提供显式状态查询命令（如 `ue status`），让用户在阻塞操作前主动查询。

**方案 C**：自动重试 + 指数退避——命令超时时等待 N 秒后重试，总超时内多次尝试。

**推荐**：先实现方案 A（最小改动），同时考虑方案 C 的降级策略。

**Why:** 用户手动回退了我的改动（因为我触发了热重载），暴露了 llm-easy-shell 缺乏状态感知的根本问题。热重载的 Preparing Patch 阶段是用户最常遇到的阻塞场景。

**How to apply:** 后续开发 llm-easy-shell 命令时，优先考虑状态检查机制；与 UE 编辑器交互前先确认状态。
