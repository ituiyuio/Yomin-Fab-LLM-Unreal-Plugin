---
layout: doc
title: LLMEasyShell v1.1.0 — Fab-shippable split (LLMSurvivorShell companion + 4-UE compat)
date: 2026-07-05
tag: Major
summary: |
  LLMEasyShell v1.1.0 把项目耦合的 143 个 Survivor helpers (LLMSurvivorGameplayLib 模块 + 50+ Survivor dead includes) 拆分到新 LLMSurvivorShell 插件 (project-only,保留 CODEO dep),LLMEasyShell full 现在 100% standalone,Fab 4 个 UE 版本 (5.5/5.6/5.7/5.8) 全部 PASS。14 个 UI E2E helpers (强依赖 CODEO UWebUIBase + UE 5.8 FInputKeyEventArgs) 用 WITH_LLMEASYSHELL_CODEO 包裹。MCP / WebBrowserWidget / Chooser API / FInputKeyEventArgs 跨版本 #if 守卫全补齐。
emoji: 🚢
slug: llm-easy-shell-1.1.0
---

# LLMEasyShell v1.1.0

> 🚢 首次可 Fab-shippable release。之前 v1.0.0 强耦合 host project `CODEO` 模块,无法在干净 Fab HostProject 上构建。v1.1.0 拆分后 LLMEasyShell full 真正 project-agnostic。

## ✨ 亮点 (跟 v1.0.0 一致,首次对外)

- **Agent runtime** — TCP 监听端口 15151–15200,接纯文本命令返 JSON。LLM agent loop / CLI / test harness 都能驱动编辑器,不用写自定义传输。
- **36 个原生 editor commands** — scene / asset / property / function 反射 / PIE 控制 / Live Coding / log 抓取 / UI 内省 / 截图 / MCP。
- **C++ Ability 框架** — 插件通过 `ULLMEasyShellAbilityCommandObject` 注册类型化命令,启动时自动发现。Material / VFX / UI / PCG / Quixel / LLMMS / StateTree 都作为 ability ship。
- **Python Ability 框架** — `.py` 丢进 `abilities/`,`python reload` 后立即可用 `python <name>`。
- **25+ 内置 Python abilities** — asset / blueprint / property / gameplay / animation / curve / datatable / chooser / level / scene / editor / material / vfx / umg / pose search / navigation / perf / HD3D demo set。
- **Live Coding + Restart** — `livecoding` / `lc` / `reload` + `--restart` 编辑器带 crash 检测 + push-model ready signal。
- **PIE 控制 + Slate composite 截图** — `play` / `stop` / `pause` / `select` / `focus` + 直出 PNG。
- **UI 内省 + 模拟输入** — dump UMG widget tree,点击按钮,输入文本。
- **跟 LLMEasyShell Lite 共存** — Lite 在 15201–15250 端口,互不冲突。

## 🆕 本次新增 (v1.1.0)

- 🆕 **Standalone Fab 包** — `LLMEasyShell` 现在 project-agnostic。干净 HostProject 在 UE 5.5/5.6/5.7/5.8 全编译通过。
- 🆕 **`LLMSurvivorShell` 伴生插件 (project-only)** — 143 个 Survivor-specific helpers (`TriggerSurvivorWeaponEvolution`、`UnlockSurvivorMastery`、`InspectSurvivorSaveManager` 等) 搬到独立 `LLMSurvivorShell` 插件。host 项目需要 Survivor gameplay helpers 时一并装,保留 `CODEO` dep 留在项目内。
- 🆕 **MCP 引擎版本守卫** — `ModelContextProtocol` (UE 5.8+ Experimental) dep 按引擎版本 gate。5.5/5.6/5.7 stub `mcp` 命令返 "host plugin not enabled" 提示。
- 🆕 **WebBrowserWidget 引擎版本守卫** — `WITH_LLMEASYSHELL_WEBBROWSER` macro 控制 CEF state block。host `.uproject` 启用后 `ui info` / `uishot` 输出 CEF state。
- 🆕 **Chooser API 跨版本兼容** — UE 5.8 用 `DeleteRows(TArrayView<int32>)` + `GetDebugSelectedRows()`,UE 5.7 fallback 到 `DeleteRows(TArray<uint32>)` + `MatchedRow=INDEX_NONE`。
- 🆕 **UI E2E helpers `WITH_LLMEASYSHELL_CODEO` 守卫** — 14 个 `Simulate*` / `FindUIWidget` / `TriggerWebUICallback` 等强依赖 CODEO `UWebUIBase` + UE 5.8 `FInputKeyEventArgs`,没有 CODEO 时返 `{"error":"host_codeo_required"}` JSON 提示。

## 🐛 修复 (vs v1.0.0 internal)

- 🐛 **`Result: Failed (RulesError) Could not find definition for module 'CODEO'`** — `LLMEasyShell.Build.cs` 不再硬依赖 `CODEO`。Survivor-specific 代码搬到 `LLMSurvivorShell`。
- 🐛 **`Result: Failed (RulesError) Could not find definition for module 'ModelContextProtocol'` 在 UE 5.5/5.6/5.7** — 引擎版本检查 gate。
- 🐛 **`FChooserColumnBase::DeleteRows(TArrayView<int32>)` 在 UE 5.7 不存在** — fallback 到 `TArray<uint32>` 重载。
- 🐛 **`UChooserTable::GetDebugSelectedRows()` 在 UE 5.7 不存在** — fallback `MatchedRow = INDEX_NONE`。
- 🐛 **`UWebUIBase` undeclared identifier 当 host project 无 CODEO** — `TriggerWebUICallback` 整段 `WITH_LLMEASYSHELL_CODEO` gate。
- 🐛 **`FInputKeyEventArgs` 5-arg 构造在 UE 5.5/5.6/5.7 不存在** — 整个 UE 5.8 输入模拟 block gate。
- 🐛 **`LLMEasyShellGameplayLib.cpp` 50+ stale `Survivor/Core/...` include** — 死代码 + 残留 unused include 全清。

## 💥 破坏性变更 (vs v1.0.0 internal)

- 💥 **Fab 包不再含 `LLMSurvivorGameplayLib` 模块**。143 个 Survivor helpers 现在在 `LLMSurvivorShell` 伴生插件。需要这功能的 host 项目装 `LLMSurvivorShell` (project-only)。
- 💥 **UI E2E helpers 需要 host `CODEO`** — `SimulateKey`、`FindUIWidget`、`TriggerWebUICallback` 等返 `host_codeo_required` JSON 当 host 没定义 `CODEO`。可用 host 项目自带的模拟层,或 vendor in `UWebUIBase` + 装 `LLMSurvivorShell`。

## 📦 跟 LLMEasyShell Lite 共存

LLMEasyShell 在 15151–15200 端口,跟 **LLMEasyShell Lite** (15201–15250) 完全独立。可装任一或都装 — 监听器运行时互不冲突。

## ⚙ 要求

- Unreal Engine 5.5 / 5.6 / 5.7 / 5.8 (每个 UE 一个 Project Version)
- 9 个 engine plugin 依赖 (见 `README.md`):`PythonScriptPlugin`、`GameplayAbilities`、`GameplayTagsEditor`、`EnhancedInput`、`PoseSearch`、`Chooser`、`StructUtils`、`Niagara`、`EditorScriptingUtilities`
- `WebBrowserWidget` 在 host `.uproject` 启用 (UE engine plugin ships `EnabledByDefault:false`)

## 📝 已知限制

- Live Coding 和 `log --compile` 仅 Windows。
- 首次 PIE / WebBrowser 加载 3–5s cold start,不是 bug。
- `ModelContextProtocol` (`mcp` 命令) 仅 UE 5.8+ 激活 (老版本自动 stub)。
- `WITH_LLMEASYSHELL_CODEO=0` (默认 Fab HostProject) → UI E2E helpers 返 `host_codeo_required` JSON。

---

*LLMEasyShell v1.1.0 — YominUnreal*