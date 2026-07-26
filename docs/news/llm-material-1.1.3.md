---
layout: doc
title: LLMMaterial v1.1.3 — UE 5.8 平台声明漂移修复 + 源码 LF 归一化
date: 2026-07-26
tag: Fix
summary: |
  LLMMaterial v1.1.3 是 v1.1.2 之后的纯文档 / 源码清洁补丁。修正 VERSION-NOTES.md 平台支持列表（"UE 5.7" → "UE 5.8"），并将 567 个工作树文件统一从 CRLF 重归一为 LF（对齐 `.gitattributes` `text eol=lf` 策略）。源码契约、`.llmmat` 格式、引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）全部保持不变。
emoji: 🐛
slug: llm-material-1.1.3
---

# LLMMaterial v1.1.3

> 纯 compat / hygiene 补丁。无新功能、无 API 变更。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）保持不变。

## 🐛 修复

- **`VERSION-NOTES.md` 平台支持列表漂移** — 1.1.0 写 "UE 5.8+"，但 1.1.2 发布多版本 5.5/5.6/5.7/5.8 后没及时同步；改为 "5.5 / 5.6 / 5.7 / 5.8"。跟 `tool-fix-07 session16` 同期 11 表面 README / aiac "UE 5.7" 漂移修复同 cycle 1:1 平行处理。
- **`.uplugin` `FabURL` PLACEHOLDER → 真实 ProductID** — `com.epicgames.launcher://ue/Fab/product/109df9bd-955a-420a-ae17-d23e5040f81c`，首次发布后从 PLACEHOLDER 切到真实 ID。

## 🔧 内部重构

- **CRLF → LF 归一化（mechanical no-op）** — 567 个工作树文件原本是 CRLF，git 记录为 LF，导致每次 diff 出现 ±100% 噪声（`Sidebar.html` 一次 churn 1231 行）。锁 `.gitattributes` 为 `text eol=lf` 后，本 commit 把工作树对齐策略。无语义改动 — 纯字节级换行符清理。

## ✅ 验证

- 干净 `RunUAT.bat BuildPlugin ... -rocket` 在 **UE 5.5 / 5.6 / 5.7 / 5.8** 全跑通（**零 error / 零 C4996 / 零 C4701**）。
- 4 zip SHA-256 已写入 `.publishready/zips/LLMMaterial/manifest.json`，可直接传 Google Drive / Dropbox 给 Fab Publisher Portal。

## 🔧 兼容性

- 破坏性变更：无。源码 + 二进制契约跟 1.1.2 完全一致。`.llmmat` 文件 1.0 / 1.1.0 / 1.1.1 / 1.1.2 写的仍然有效。
- 引擎矩阵：5.5 / 5.6 / 5.7 / 5.8（Win64）— 未变。

---

**引擎支持**：UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmmat`（JSON）、`.llmschema`（Schema）、Material UAsset。
**Fab ProductID**：`109df9bd-955a-420a-ae17-d23e5040f81c`
