---
layout: doc
title: LLMDynamicUI v1.1.3 — Schema 别名 + Easing 计数漂移闭环
date: 2026-07-26
tag: Fix
summary: |
  LLMDynamicUI v1.1.3 是 v1.1.2 之后的纯文档 / schema 漂移闭环补丁。修复 4 项累积维护：WidgetTypeSchema.llmschema ↔ C++ LLMUnifiedTypeRegistry.cpp TypeMap 别名同步（缺 6 个 widget）、ELLMEasingType 15→34 计数修正（5 表面）、`python ui easings` 命令引用清理、`UE 5.7+` → `UE 5.8+` 声明漂移。无 C++ / 无 API 变更。
emoji: 🐛
slug: llm-dynamic-ui-1.1.3
---

# LLMDynamicUI v1.1.3

> 纯维护补丁。无 C++ / 无 API 变更。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）保持不变。

## 🐛 修复

- **Widget 别名 schema 漂移闭环** — `WidgetTypeSchema.llmschema` 只有 3 条 alias，但 `LLMUnifiedTypeRegistry.cpp` TypeMap 声明了 10 条。6 个 widget（CanvasPanel、CommonBorder、CommonButton、TextBlock、CommonText、CommonImage、EditableText、EditableTextBox、ComboBox）在 schema 端 alias 缺失，外加 SDF 在 `SDFSchema.llmschema`。修复后：9 条 in-schema alias + SDF in SDFSchema（9/9 镜像）。`LLMUnifiedTypeRegistry_AutoDiscovery.cpp` 的 `Meta.Aliases.Add()` 现已跟 TypeMap 逐项同步。新增 `doc-audit` 类 `schema-aliases-vs-cpp-typemap` 加 6 条单目标正则防御下次 schema-regen 回归。
- **Easing 函数计数漂移** — 5 个表面（`.uplugin` Description + `Documentation.md` ×2 + `README.md` + `VERSION-NOTES.md`）写 "15" 种 easing。`ELLMEasingType` 枚举实际有 34 项（Linear + 3 类通用 EaseIn/EaseOut/InOut + 10 族 × In/Out/InOut 变体：Quad/Cubic/Quart/Quint/Sine/Expo/Circ/Elastic/Back/Bounce）。所有表面同步更新。新增 `doc-audit` `count-easing-function` pattern 守住修正后的计数。
- **失效的 `python ui easings` 命令引用** — `VERSION-NOTES.md` 引用了一个不存在的 `ui easings` 命令。`ui` ability 实际只暴露 `generate` / `export` / `list-types` / `export-schema`。引用删除。
- **`UE 5.7` 声明漂移** — `VERSION-NOTES.md` 引用 "UE 5.7"，但 `.uplugin` `EngineVersion` 已是 `5.8.0`，实际 Fab 提交矩阵是 5.5 / 5.6 / 5.7 / 5.8。改为 "UE 5.8+"。

## 🔧 内部重构

- **CRLF → LF 归一化** — 567 个工作树文件从 CRLF → LF，对齐 `.gitattributes` `text eol=lf` 策略。纯字节级换行符清理，无语义改动。

## ✅ 验证

- 干净 `RunUAT.bat BuildPlugin ... -rocket` 在 **UE 5.5 / 5.6 / 5.7 / 5.8** 全跑通（**零 error / 零 C4996**）。
- 4 zip SHA-256 已写入 `.publishready/zips/LLMDynamicUI/manifest.json`，可直接传 Google Drive / Dropbox 给 Fab Publisher Portal。

## 🔧 兼容性

- 破坏性变更：无。源码 + 二进制契约跟 1.1.2 完全一致。`.llmui` 文件 1.0 / 1.1.0 / 1.1.1 / 1.1.2 写的仍然有效。
- 引擎矩阵：5.5 / 5.6 / 5.7 / 5.8（Win64）— 未变。

---

**引擎支持**：UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmui`（JSON）、`.llmschema`（Schema）、UMG Widget Blueprint（UAsset）。
**Fab ProductID**：`d84f1501-b45a-49c2-8069-40132482d0fd`