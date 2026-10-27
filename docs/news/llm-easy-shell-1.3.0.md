---
layout: doc
title: LLMEasyShell v1.3.0 — Trace Tab 实时追踪窗口 + ui press --root
date: 2026-10-27
tag: Plugin
summary: |
  功能版：编辑器内新增实时命令追踪窗口 —— "LLM Shell Trace" tab
  逐条显示正在执行的 shell 命令，带详情面板（Input / Output /
  Error）、过滤框、只看失败开关与自动滚动；从 Play 工具栏端口状态
  控件打开，每编辑器会话首条命令自动弹出一次
  （`LLMEasyShell.TraceAutoOpen 0` 可禁用）。对外公开 C++ 数据面：
  500 条环形缓冲（`GetRecentTraces()`）+ `FOnShellCommandTraced`
  多播委托。`ui press` 新增 `--root <UClass>` 多根路径解析与
  0 命中诚实诊断。UE 5.5 / 5.6 / 5.7 / 5.8 经 BuildPlugin -rocket
  全部零错误零警告编译通过。
emoji: 🐚
slug: llm-easy-shell-1.3.0
---

# LLMEasyShell v1.3.0

> 🚀 **功能版 —— 看着 shell 干活。** 编辑器内实时追踪窗口、公开的
> C++ 追踪数据面、`ui press --root` 多根解析。引擎兼容范围不变：
> 5.5 / 5.6 / 5.7 / 5.8。

## ✨ 新增功能

- **Trace Tab —— 实时命令追踪窗口** —— 新的 "LLM Shell Trace" nomad
  tab 逐条显示正在执行的 shell 命令：单列实时列表 + 选中项详情面板
  （Input / Output / Error），顶部过滤框 / 只看失败开关 / 自动滚动 /
  Clear。入口：Play 工具栏端口状态控件点击（原"点击复制端口"已移到
  窗口头部的 *Copy port* 按钮）；每编辑器会话首条命令到达且窗口未开
  时自动打开一次。`LLMEasyShell.TraceAutoOpen 0` 可整体禁用自动弹窗；
  手动关闭后本会话不再弹。
- **公开的 C++ 追踪数据面** —— subsystem 内置最近 500 条命令的内存
  环形缓冲（`GetRecentTraces()`，Input/Output 展示截断），每条命令
  trace 完成后在 game thread 广播 `FOnShellCommandTraced`。
  `Saved/LLMEasyShell/traces/` 下的 JSONL 归档仍是全文持久记录 ——
  环形缓冲只服务实时展示。
- **`ui press --root <UClass>`**（`9a00f9a`）—— 从指定根 widget 类
  解析路径：class 短名精确匹配，BP 生成类带 `_C` 后缀，与
  `ui dump --root` 语义一致。不传 `--root` 时行为与旧版逐字节一致。

## 🐛 修复

- **`ui press` 0 命中诊断归真**（`9a00f9a`）—— PIE 已在运行但
  `--root` 类匹配 0/N 个 widget 时，错误如实报
  `PIE running, 0 of N UUserWidget match root class` 并提示
  `ui find --all`，不再误导 "Start PIE first"。
- **Trace Tab 引擎兼容加固**（发布工程）—— Trace Tab 最初只对着
  UE 5.8 开发；首次四引擎 `-rocket` 验证发现两处 5.5–5.7 不可用的
  API。`FCoreDelegates` post-engine-init 现已版本门控（5.8 走
  `GetOnPostEngineInit()` 访问器，5.5–5.7 走直接委托成员），弃用的
  `SListView::ItemHeight` 参数（tile 视图之外的 no-op）已移除。
  四引擎全部零错误零警告编译通过。

## 💥 破坏性变更

- 无。

## ⚙ 环境要求（不变）

- Unreal Engine 5.5 / 5.6 / 5.7 / 5.8（每引擎一个 Project Version）
- 9 个引擎插件依赖（见 `README.md`）：`PythonScriptPlugin`、
  `GameplayAbilities`、`GameplayTagsEditor`、`EnhancedInput`、
  `PoseSearch`、`Chooser`、`StructUtils`、`Niagara`、
  `EditorScriptingUtilities`
- 宿主 `.uproject` 需启用 `WebBrowserWidget`（CEF 状态 UI 内省）
- UE 5.8 宿主需启用 `ModelContextProtocol`（`mcp` 命令；5.5–5.7
  自动降级为提示）

---

*LLMEasyShell v1.3.0 — YominUnreal*
