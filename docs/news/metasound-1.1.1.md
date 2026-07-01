---
layout: doc
title: LLMMetaSound v1.1.1 — UE 5.8 + Fab 4.x 合规
date: 2026-07-01
tag: Plugin
summary: |
  LLMMetaSound v1.1.1 发布 UE 5.7 / 5.8 双版本 zip。修复 6 个 C4996 警告（PRAGMA 包裹），FabURL 改为 launcher 协议，放弃 UE 5.5 / 5.6 兼容（MetaSound API 表层变化太大）。
emoji: 🔊
slug: metasound-1.1.1
---

# LLMMetaSound v1.1.1

> 仅支持 UE 5.7 / 5.8。放弃 UE 5.5 / 5.6 — MetaSound API 表层变化太大，stub 向后兼容成本远超价值。

## ✨ 新功能

- **JSON → UMetaSoundSource / UMetaSoundPatch 生成器** — 用 JSON 描述 MetaSound 图，插件自动构建完整资产
- **双向 roundtrip** — UMetaSound ↔ `.llmmetasound` JSON
- **类型安全的边验证** — 顶点类型不匹配的边在保存前被拒绝
- **`OnPlay` + 最终音频输出自动连接** — 通用管线自动布线
- **Slate 编辑器面板** — Window → LLMMetaSound
- **Schema 导出 (`.llmmetasoundschema`)** — 暴露 401 个已注册 MetaSound 节点类供 LLM 上下文使用
- **重载操作消歧** — `ClassPath` 字段正确选择 `UE.Multiply.Audio by Float` 变体
- **Pin-name 优先的边解析** — `FromPinName` / `ToPinName` 对引擎实时顶点列表解析（跨 UE 版本稳定）；旧版 `FromVertexID` / `ToVertexID` 仍兼容

## 🐛 Bug 修复

- **UE 5.8 上 6 个 C4996 `IterateRegistry` 弃用警告** — 每次调用包裹 `PRAGMA_DISABLE_DEPRECATION_WARNINGS` / `PRAGMA_ENABLE_DEPRECATION_WARNINGS`（Fab 把 C4996 当 error 处理）
- **`FabURL` 之前是 `https://www.fab.com/listings/PLACEHOLDER`** — 改为 launcher 协议 `com.epicgames.launcher://ue/Fab/product/PLACEHOLDER`（Fab 4.x 合规）
- **`EngineVersion` 字段** 从 `5.7.0` 升级到 `5.8.0` 跟 `.uplugin` 对齐
- **Plguagin → Plugin repo URL fossil** 13 个文档面（tool-fix-128）

## ⚡ 改进

- **生成器加固** 适配 LLM-friendly DSL 约定（容错空白、大小写、部分名字匹配）
- **去掉 `EditObject` 调用** — 避免 `SynchronizePinLiteral` 硬断言
- **Tutorials 按钮** 添加 + `LOCTEXT` 重定义修复
- **README / Documentation 改写** — Fab marketplace 风格（Agent Online 品牌、Overview / Problem / Solution / How to Use 结构）；`DocsURL` 笔误修正

## 💥 破坏性变更

- **UE 5.5 和 5.6 不再支持** — 插件用了 5.7+ MetaSound API 表层（`EMetasoundFrontendClassAccessFlags`、`FMetasoundFrontendGraphClass::GetDefaultInterface`、`MetasoundFrontendNodeClassRegistry.h`、`FMetaSoundAssetCookOptions`）

## 🔧 内部重构

- **Editor 模块依赖拆分** — `LLMEasyShell` / `LLMEasyShellLite` 通过 `CheckModuleExists` + `WITH_LLMEASYSHELL={0,1}` 实现编译时软依赖（`.uplugin` 不强制依赖，宿主项目无这些模块也能启动）

---

**引擎支持**：UE 5.7（已测）、UE 5.8（已测） — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmmetasound`（JSON）、`.llmmetasoundschema`（Schema）、`UMetaSoundSource` / `UMetaSoundPatch`（UAsset）。
