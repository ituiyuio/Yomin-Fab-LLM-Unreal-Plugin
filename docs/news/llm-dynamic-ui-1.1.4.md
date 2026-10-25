---
layout: doc
title: LLMDynamicUI v1.1.4 — 编辑器父类选择器 + 独立构建修复
date: 2026-10-26
tag: Feature
summary: |
  LLMDynamicUI v1.1.4 给编辑器面板加了 UMG 父类选择器（枚举已加载的 UUserWidget 子类，含宿主项目与 CommonUI 基类），并把此前只写在用法文本里的 `ui generate --common-ui` / `--layer`、`ui list-types --category` 真正实现。同时修掉一批声明漂移：ability 工具列表去重、version 字段接回插件真实版本、类型清单去幽灵。另一项对 Fab 用户关键：编辑器模块对 LLMEasyShell 的硬编译依赖改为条件软依赖——市场安装（无 Shell）现在编译链接干净，通知回落到引擎通知管理器。`.llmui` 格式未变。
emoji: ✨
slug: llm-dynamic-ui-1.1.4
---

# LLMDynamicUI v1.1.4

> 新功能 + 修复混合补丁。`.llmui` 格式未变。引擎矩阵 5.5 / 5.6 / 5.7 / 5.8（Win64）不变。

## ✨ 新功能

- **编辑器面板父类选择器** — 面板枚举当前已加载的 `UUserWidget` 子类（宿主项目自己的 widget 基类、CommonUI 基类都在列），生成 UMG 时可直接选父类；选择写入 `.llmui` 根级 `parentClass` 字段。
- **通用 `parentClass` 解析** — 支持 `/Script/<Module>.<Class>` 任意模块原生类 + 简单类名走运行时注册表（`ULLMParentClassRegistry`）解析，不再硬编码宿主模块路径。原生类路径改用 `FindObject` 零 IO 命中，去掉了每次生成白跑一次失败 LoadObject 的浪费。
- **`ui generate --common-ui` / `--layer <Menu|Game|Popup>` 真实现** — 此前被 usage 文本宣传但实现静默忽略；现在 `--common-ui` 显式要求 CommonUI 基类，`--layer` 隐含它并选择层级。未知 category 返回明确错误而非静默全量输出。
- **`ui list-types --category <X>` 过滤真实现** — 同上，宣传与实现对齐。

## 🐛 修复

- **市场安装路径 bug** — 编辑器面板 Export Schema 此前把文件写进用户项目里硬编码的 `Plugins/LLMDynamicUI/Config`（装在 `Engine/Plugins/Marketplace/` 下的插件该路径不存在 ⇒ 在用户项目里凭空造目录树）。改为经插件管理器取真实插件根 + `EnginePluginsDir` 兜底。
- **`.llmui` 导出目录可配置** — 新增 `ExportedLLMDefsPath` 配置项（默认 `/Game/UI/LLMDefs/`），替换硬编码的 `Content/LLMDefs/UI`。
- **类型清单去幽灵** — 移除宣称存在但实际不存在的类型（ListView / TreeView / LLMDynamicUIBase），补上 RetainerBox / InvalidationBox（24 类型 + CommonUI 别名 + SDFBox），easing 计数对齐 34。
- **`ui` ability 工具列表去重** — 此前对 LLMEasyShell 与 LLMEasyShellLite 各挂了一份逐字相同的定义，现收敛为单一来源；`version` 字段从硬编码 `"1.0"` 接回 `FLLMVersionInfo::PluginVersion`。
- **UMG 控件面板移除 SDF 空壳** — 引用从未存在过的材质资产的 SDFBox 控件对已删除，agent/用户不会再误选到无资产的空壳。
- **无 LLMEasyShell 时编辑器模块编译失败** — 编辑器通知 helper 此前是硬编译依赖，市场安装（没有 Shell 插件）编不过。现改为条件软依赖：有 Shell 走统一通知入口；无 Shell 编译链接干净，通知回落到引擎通知管理器（`FSlateNotificationManager`）。**对 Fab 用户：插件现在完全独立可用。**

## 🔧 兼容性

- 破坏性变更：无。`.llmui` 格式未变，既有 `parentClass` 值继续有效。
- 引擎矩阵：5.5 / 5.6 / 5.7 / 5.8（Win64）— 未变。

## ✅ 验证

- 干净 `RunUAT.bat BuildPlugin ... -rocket` 在 **UE 5.5 / 5.6 / 5.7 / 5.8** 全跑通（**零 error / 零 warning**）。
- 项目内（LLMEasyShell 在场）增量编译 PASS，`LLMDynamicUIEditor` DLL 正常落盘链接。
- 4 zip SHA-256 已写入 `.publishready/zips/LLMDynamicUI/manifest.json`。

---

**引擎支持**：UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`，每 UE 独立 zip + Project Version。
**文件格式**：`.llmui`（JSON）、`.llmschema`（Schema）、UMG Widget Blueprint（UAsset）。
