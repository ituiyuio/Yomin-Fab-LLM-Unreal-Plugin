---
layout: doc
title: LLMStateTree v1.1.2 — UE 5.5/5.6/5.7/5.8 C4996 修复
date: 2026-07-02
tag: Plugin
summary: |
  LLMStateTree v1.1.2 patch 发布。修复 UE 5.8 build 报 2 处 C4996 deprecation warning（Fab marketplace scanner 把 C4996 当 error 处理），通过 multi-UE compat shim 桥接新旧 API。修正 README / Documentation.md / VERSION-NOTES.md 的 "UE 5.7+" doc-fossil。
emoji: 🌲
slug: llm-statetree-1.1.2
---

# LLMStateTree v1.1.2

> Patch bump。零 user-facing API 变化 — 仅修 UE 5.8 编译告警 + 文档 fossil。

## 🐛 Bug 修复

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

---

**引擎支持**：UE 5.5（已测）、UE 5.6（已测）、UE 5.7（已测）、UE 5.8（已测）
— `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。

**文件格式**：`.llmstate`（JSON）、`.llmstateschema`（Schema）、`UStateTree`（UAsset）。

**Source**：4 个文件改动 — `LLMStateTreeCompatShim.h`（+50/-0 净）、
`LLMStateTreeCommandHandler.cpp`（+12/-6 净）、
`Documentation.md`（+3/-3 净）、`README.md`（+1/-1 净）、
`VERSION-NOTES.md`（+1/-1 净）。
