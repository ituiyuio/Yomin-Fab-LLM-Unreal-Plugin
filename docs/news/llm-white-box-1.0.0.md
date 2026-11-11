---
layout: doc
title: LLMWhiteBox v1.0.0 — 给 LLM agent 的 BSP 关卡白盒，附山谷城堡示例
date: 2026-11-11
tag: Plugin
summary: |
  LLM White Box 首个公开版本：15 条返回 JSON 的命令，直接在持久关卡里造出真正的
  BSP 几何体（盒体、减法开洞、圆柱、球、圆锥、楼梯、一键房间、一键墙段），外加按
  命名组批量刷材质、BSP 重编译，以及可复现的 `python castle build` 生成器 —— 一次
  编辑器调用重建 1040 支刷子的山谷 + 中世纪城堡白盒。UE 5.5 / 5.6 / 5.7 / 5.8
  全部 BuildPlugin -rocket 干净通过。
emoji: 🧱
slug: llm-white-box-1.0.0
---

# LLMWhiteBox v1.0.0

> 🧱 **首个发布版。** 把关卡白盒做成命令面：agent 铺一个房间、挖一个门洞、给整组
> `Masonry_*` 刷上材质、重编译 BSP —— 每一步都回 JSON。附带一份可复现的
> 山谷 + 中世纪城堡示例关卡。引擎兼容：5.5 / 5.6 / 5.7 / 5.8。

## ✨ 新增功能

- **15 条返回 JSON 的 BSP 建刷命令** —— `create-box`、`create-subtract-box`、
  `create-cylinder`、`create-sphere`、`create-cone`、`create-stairs`，
  外加 `build-room`（一次 4 墙 + 地 + 顶）与 `build-wall-segment`
  （沿任意连线拉墙并正确旋转）。
- **查询 / 变换 / 删除** —— `list-brushes`、`get-brush`、`move-rotate`、
  `delete-brush`。
- **渲染链** —— `apply-default-material`（按命名组过滤，一次重刷一整类）、
  `rebuild-bsp-lighting`，以及加强版 `build-bsp`。
- **示例关卡生成器 `python castle build`** —— 一次编辑器调用，从源码确定性地重建
  完整的山谷 + 中世纪城堡白盒（1040 支 BSP 刷子、19 个材质组、程序化天空穹顶、
  24 座远山、7 个机位预设）。
- **机器可读的刷子 / builder 契约**：
  `Config/Schemas/BrushSchema.llmwhiteboxschema`。

## 🐛 发布前修掉的 bug

- **刷子建出来时 per-poly 材质是 NULL**，所以只渲染出线框。现在材质写在 builder
  跑完之后，新建即带面。
- **`apply-default-material` 硬编码了一个名字前缀**，换一张关卡就命中 0 支刷子，
  命令却报 success。
- **`build-wall-segment` 算出了旋转却没用** —— 任意斜向墙都退化成沿轴直墙。
- **`create-stairs` 只在 Z 方向叠盒**，造出来的是塔，不是阶。
- **体积刷**（`NavMeshBoundsVolume` / `DefaultPhysicsVolume` /
  `PostProcessVolume`）被当白盒几何上报，甚至能被删掉。现在查询一律排除，
  破坏性命令一律拒绝。
- **刷子重名可能把编辑器整个弄崩**；现在按引擎的方式检测冲突，并以普通错误上报。

## ⚡ 改进

- **零编译期耦合** —— 插件靠反射在运行时注册进 LLMEasyShell / LLMEasyShell Lite。
  宿主装其中之一才有命令面；C++ API 脱离 shell 照样能用。
- **`delete-brush` 必须带 `--confirm=true`。**
- **仅编辑器模块**（`UnrealEd`、`EditorScriptingUtilities`）收进
  `Target.bBuildEditor` 里。
- **完整英文 README + Documentation.md**：Technical Information 区块、编译环境、
  命令参考、故障排查。

## 💥 破坏性变更

无 —— 这是首个发布版本。

---

## 安装

从 [Fab](https://www.fab.com/) 取对应引擎版本的构建，丢进工程的 `Plugins/` 目录。
同一工程里还要启用 **LLM Easy Shell** 或 **LLM Easy Shell Lite** —— 它才是
`whitebox ...` 命令面的来源。引擎插件 **EditorScriptingUtilities** 和
**PythonScriptPlugin** 由插件描述文件自动开启。

完整说明见 [LLM White Box →](../llm-white-box/)
