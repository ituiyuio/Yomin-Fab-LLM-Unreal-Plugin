---
layout: doc
title: LLMDynamicUI v1.1.2 — UE 5.5/5.6/5.7 多版本构建回归修复
date: 2026-07-02
tag: Fix
summary: |
  LLMDynamicUI v1.1.2 修复多版本构建回归。LLMUMGGenerator.cpp 用 EGetObjectsFlags::None（仅 UE 5.8 引入）未做版本守卫，5.5/5.6/5.7 全部 C2653 编译失败。补 ENGINE_MAJOR_VERSION/MINOR_VERSION 守卫，老版本回退 bool=true。Documentation.md / README.md "UE 5.7+" 跟 1.1.1 多版本声明对不齐的 fossil 同步修正。
emoji: 🐛
slug: llm-dynamic-ui-1.1.2
---

# LLMDynamicUI v1.1.2

> 纯 compat 补丁。无新功能、无 API 变更。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）保持不变。

## 🐛 修复

- **`ForEachObjectWithOuter` 枚举标志的 UE 5.5/5.6/5.7 版本守卫** — `LLMUMGGenerator.cpp` 的 `BackupClassPropertyReferences` 用了 `EGetObjectsFlags::None`，这个枚举是 UE 5.8 才引入的，5.5/5.6/5.7 编译全部报 `error C2653: 'EGetObjectsFlags': is not a class or namespace name`。补 `ENGINE_MAJOR_VERSION/MINOR_VERSION` 守卫，老版本回退 `bool bIncludeNestedObjects=true`。跟同文件 L278 现有 `UPackage::GetMetaData()` 守卫模式一致。
- **`Documentation.md` / `README.md` 声明漂移** — 两个文件都说 "UE 5.7+"，但 1.1.1 已经发布多版本 5.5/5.6/5.7/5.8。统一改为 "5.5 / 5.6 / 5.7 / 5.8+"。

## ✅ 验证

- 干净 `RunUAT.bat BuildPlugin ... -rocket` 在 **UE 5.5 / 5.6 / 5.7 / 5.8** 全跑通（零 error / 零 C4996 弃用警告 / 零 C4701 未初始化警告）。

## 🔧 兼容性

- 破坏性变更：无。源码 + 二进制契约跟 1.1.1 完全一致。`.llmui` 文件 1.1.0 / 1.1.1 写的仍然有效。
- 引擎矩阵：5.5 / 5.6 / 5.7 / 5.8（Win64）— 未变。

---

**引擎支持**：UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmui`（JSON）、`.llmschema`（Schema）、UMG Widget Blueprint（UAsset）。