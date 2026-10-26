---
layout: doc
title: LLMEasyShell v1.2.0 — 任何插件都能在其上生长的外壳
date: 2026-10-26
tag: Plugin
summary: |
  平台宿主版：Python ability 宿主开放给所有插件 —— 把 `.py` 能力丢进任意插件的
  `Content/Python/<Package>/abilities/` 即被自动发现。新增两个一行调用的扩展点
  （`RegisterShellCommand` / `AddPythonAbilityRoot`）与六个内置 ability；插件从此
  彻底项目无关 —— 宿主项目条件依赖、21 个项目专属 ability、`ui state` 命令全部
  退役。原先被困在宿主检查后面的 13 个 UI/输入/截图 helper 现在任何项目可用。
  UE 5.5 / 5.6 / 5.7 / 5.8 经 BuildPlugin -rocket 全部零警告编译通过。
emoji: 🐚
slug: llm-easy-shell-1.2.0
---

# LLMEasyShell v1.2.0

> 🚢 **Minor bump —— 依赖永远单向。** LLMEasyShell 升级为平台宿主：它发现其他
> 插件提供的 ability 与命令，但永远不知道那些插件存在。引擎兼容范围不变：
> 5.5 / 5.6 / 5.7 / 5.8。

## ✨ 新增功能

- **Python ability 宿主开放给所有插件** (`b709101f1`) —— 加载器曾有四处硬编码
  指向本插件自身目录（扫描根、包导入路径、描述查找、reload 哈希缓存），任何
  别处的 `.py` 都不可见。现在改为**按插件发现**：每个启用插件都会被检查
  `<Plugin>/Content/Python/<Package>/abilities/*.py`。优先级确定化 —— 插件宿主
  胜过项目脚本目录，按插件名排序。
- **两个新扩展点** (`b709101f1`) —— `RegisterShellCommand()` 让任意插件往分发表
  注册 C++ 命令；`AddPythonAbilityRoot()` 注册额外 Python ability 目录。两者都
  不需要本插件知道调用方存在。
- **项目脚本目录按形制发现** (`7dfb41a0e`) —— 加载器扫描
  `Content/Features/<任意-feature>/Scripts`；新增 feature 目录即生效，无需改插件。
  `bpcomp` 运行时解析宿主脚本模块名，不再假设固定名字。
- **六个新内置 Python ability** —— `automation_check_test` /
  `automation_dump_api` / `automation_list_tests` / `automation_run_and_wait` /
  `automation_sanity_check`（编辑器自动化测试族，由内部一次性化石泛化）与
  `vfxsim`（Niagara 仿真探针）。
- **13 个 UI/输入/截图 helper 解锁** (`7dfb41a0e`) —— 它们从来只需要引擎，却被与
  真正需要项目代码的那一个 helper 一起关在同一道宿主检查后面。检查退役，它们
  现在所有项目可用。
- **多引擎兼容加固** (`da7b269a8`) —— 模拟输入、动画状态机默认态、属性反射三处
  引擎 API 版本门补齐；5.5 / 5.6 / 5.7 / 5.8 在 `BuildPlugin -rocket` 下全部
  零错误零弃用警告。

## 🐛 修复

- **PIE `play --wait` 不可能成功** —— 等待路径重写（`be2cc3f16`）；`play` 假成功
  而编辑器正在死（PIE 通道修复，`ab3d3dd9e`）；截图视口真实性专项
  （`28a9fa896`）。
- **`info` 不再说谎** —— `errorCount` 归真，死锁探针不再报假 BUSY
  （`635859030`）。
- **Live Coding stale-Intermediate 升级判据** 抽成可测策略层（`ReloadGatePolicy`）
  并配行为断言 —— 60 秒超时不再被无证据地「判词」成杀软崩溃（`b7a0d3980`）。
- **LLMEasyShellLite `_base.py` 导入崩溃** —— abilities 目录可被顶层导入后，
  包相对导入抛 `ImportError`；改绝对导入，两种上下文都可用（`b709101f1`）。

## 💥 破坏性变更

- **宿主项目面从本插件退役** (`7dfb41a0e`) —— `WITH_LLMEASYSHELL_CODEO` 条件依赖、
  `ui state` 命令、项目 cheat、项目专属 Python ability 全部迁往宿主项目自己的
  插件。它们依赖宿主项目代码，在任何其他项目里本来就不可用。通用插件现在出货
  **37 命令 + 46 个全部项目无关的内置 Python ability**（v1.1.1 文档写的 48
  abilities 含 223 个项目专属子命令 —— 正是那批只在原宿主项目里能用的东西）。
- **文档矩阵归真** —— README 曾写 "UE 5.8+"，而产品实际为 5.5–5.8 各出引擎匹配
  包；`ModelContextProtocol` 如实落档为 UE 5.8-only 宿主依赖（宿主 `.uproject`
  须启用；5.5–5.7 上 `mcp` 命令返回不可用提示）。

## ⚙ 环境要求（不变）

- Unreal Engine 5.5 / 5.6 / 5.7 / 5.8（每个 UE 一个 Project Version）
- 9 个引擎插件依赖（见 `README.md`）：`PythonScriptPlugin`、`GameplayAbilities`、
  `GameplayTagsEditor`、`EnhancedInput`、`PoseSearch`、`Chooser`、`StructUtils`、
  `Niagara`、`EditorScriptingUtilities`
- `WebBrowserWidget` 在宿主 `.uproject` 启用（CEF 态 UI 内省）
- `ModelContextProtocol` 在 UE 5.8 宿主 `.uproject` 启用（`mcp` 命令；
  5.5–5.7 自动桩化）

---

*LLMEasyShell v1.2.0 — YominUnreal*
