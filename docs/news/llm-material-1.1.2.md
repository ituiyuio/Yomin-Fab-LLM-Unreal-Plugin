---
layout: doc
title: LLMMaterial v1.1.2 — UE 5.5/5.6/5.7/5.8 多版本构建回归修复
date: 2026-07-02
tag: Fix
summary: |
  LLMMaterial v1.1.2 修复 UE 5.8 编译回归 + Documentation.md / README.md "UE 5.7+" fossil。MaterialBuilder.cpp L432-466 用了 21 个被 UE 5.8 标 C4996 弃用的 `UMaterial::bUsedWithXxx` 直接成员访问；用 `PRAGMA_DISABLE_DEPRECATION_WARNINGS` 局部抑制，避开 UE 5.5/5.6/5.7（`SetUsageByFlag` 私有）的兼容性坑。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）保持不变。
emoji: 🐛
slug: llm-material-1.1.2
---

# LLMMaterial v1.1.2

> 纯 compat 补丁。无新功能、无 API 变更。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）保持不变。

## 🐛 修复

- **`MaterialBuilder.cpp` 的 UE 5.8 C4996 弃用警告** — L432 (`bUsedWithNanite`) + L444-466（21 个 `bUsedWithXxx` 直接成员访问）全部被 UE 5.8 标记 `warning C4996: ... Please update your code to the new API before upgrading to the next release`。理想替代品 `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)` 在 UE 5.5/5.6/5.7 是 `private`，UE 5.8 才公开，因此不能直接切换。用 `PRAGMA_DISABLE_DEPRECATION_WARNINGS` / `PRAGMA_ENABLE_DEPRECATION_WARNINGS` 局部块包住这 22 行直访，跟 `[tool-fix-274]` `[tool-fix-260]` 系列同 cycle 1:1 平行处理。
- **`Documentation.md` / `README.md` 声明漂移** — 两个文件都说 "UE 5.7+"，但 1.1.1 已经发布多版本 5.5/5.6/5.7/5.8。统一改为 "5.5 / 5.6 / 5.7 / 5.8"。
- **`.uplugin` / README / Documentation 脚注 `v1.1.1 → v1.1.2` 同步**。

## ⚡ 改进

- **`MaterialBuilder.cpp` 注释说明 UE 5.5/5.6/5.7 抑制理由** — 在 PRAGMA 块上方加了 4 行注释，记录 `SetUsageByFlag` 私有 → 公开的版本边界，避免后人重构时踩坑。

## ✅ 验证

- 干净 `RunUAT.bat BuildPlugin ... -rocket` 在 **UE 5.5 / 5.6 / 5.7 / 5.8** 全跑通（**零 error / 零 C4996 弃用警告 / 零 C4701 未初始化警告**）。
- 4 zip SHA-256 已写入 `.publishready/zips/LLMMaterial/manifest.json`，可直接传 Google Drive / Dropbox 给 Fab Publisher Portal。

## 🔧 兼容性

- 破坏性变更：无。源码 + 二进制契约跟 1.1.1 完全一致。`.llmmat` 文件 1.0 / 1.1.0 / 1.1.1 写的仍然有效。
- 引擎矩阵：5.5 / 5.6 / 5.7 / 5.8（Win64）— 未变。

---

**引擎支持**：UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmmat`（JSON）、`.llmschema`（Schema）、Material UAsset。