---
name: llm-easy-shell-lite
description: |
  操作运行中的 Unreal Engine 编辑器。Lite 是 LLMEasyShell 的最精简子集：9 个**内置只读**
  查询命令 + 1 个自维护命令 (`livecoding`，Windows only；别名 `reload`/`lc`) + 已注册的
  plugin ability + 开放 PyAbility 调度。
  ⚠️ **只读边界仅覆盖内置 9 个命令**：PyAbility runtime（完整 UE Python API）与第三方
  plugin ability（material/ui/whitebox/statetree/metasound 的 generate / delete / compile）
  是两处**开放面**，Lite 不做权限隔离。适合需要最小依赖的编辑器探测，或明确只用内置
  只读命令的场景。

  **触发场景**：
  - 场景浏览：列出 Actor、查看详情、发现函数和属性
  - 资产浏览：搜索资产、查看资产内容（不修改）
  - 日志查看：编辑器错误日志、Niagara 验证消息
  - 状态查询：项目信息、PIE 状态、game state

  **触发关键词**：ls, cat, find, discover, info, help, gamestate, log, msglog, python, livecoding / reload (Windows only), /Actor/, /Assets/, /Game/, /Level/

  **不触发**：任何需要写入的操作（set/spawn/rm/cp/mv/call/save/new/addcomp/play/stop/pause/undo/redo）、
  截图、C++ 代码编写、AngelScript 脚本、**`mcp *`（Lite 不实现 MCP 命令，需要用 full 版本 [llm-easy-shell](../llm-easy-shell/SKILL.md)**。

  **完整写操作 / 截图 / Python ability 数百个命令（2026-10-25 runtime 读数 370，时点快照 —— 同名时插件那份赢）**：用 full 版本 [llm-easy-shell](../llm-easy-shell/SKILL.md)。
---

## 能力范围（Lite 实际能跑什么）

> **定位：Lite 是 agent 的观测面，不是权限面。**
> 硬只读只覆盖**内置 9 个查询命令**。另外两处是**开放面**，Lite 不做权限隔离：
> ① **PyAbility runtime** —— 完整 UE Python API，`.py` 写什么就能做什么；
> ② **第三方 plugin ability** —— 插件自己定义命令集与写语义，`generate` / `delete` /
> `compile` 都能从 Lite 直接调到。
> 想要硬只读保证：只用内置 9 个命令，或别装你不希望 agent 触达的插件。

### 1. 9 个只读命令（核心）+ 1 个自维护命令

```bash
ls /Level/Actors                    # 看场景 Actor 列表
ls /Assets                          # 看资产目录（cat 支持详情）
cat /Actor/{name}                   # 看 Actor / Component / Asset 详情
cat /Actor/{name}/{component}       # 看 Component 详情（支持别名匹配）
find Actor {pattern}                # 按名称 pattern 搜索场景 Actor
find Asset {pattern}                # 按名称 pattern 搜索资产
find /Game {pattern}                # 按路径搜索（* 通配符）
find /Assets {pattern}              # 按路径搜索（别名）
discover /Actor/{name} --funcs      # 查看可用函数（call 前必看）
discover /Actor/{name} --props      # 查看属性（set 前必看）
info                                # 项目 + 编辑器 + PIE 状态（livecoding 字段判断）
help                                # 列出所有可用命令和注册的 ability
gamestate                           # 查询 PIE 中 wave/health/gold/enemies（按形状启发式找 pawn/wave manager，字段名走约定）
log --errors                        # 查看编辑器错误日志
msglog --niagara                    # 查看 Niagara 验证消息
livecoding --status                 # 看 LiveCoding 编译状态（Windows only；别名 reload / lc）
```

> Lite 不实现 MCP 命令（`Plugins/LLMEasyShellLite/Source/LLMEasyShellLite/Private/` 无 `ShellCommand_Mcp.cpp`，与 full 版本 9 个查询类只读命令对齐 — full 内置 37 = 这 9 个查询 + 28 个写/PIE/控制/调试命令；37 为 2026-10-26 读数，`ui state` 外迁 LLMSurvivorShell 后的**发行体**口径，装该宿主插件时 runtime 为 38）。需要 `mcp status` / `mcp tools` 等用 full 版本 [llm-easy-shell](../llm-easy-shell/SKILL.md)。

**路径规则**：

| 路径 | 含义 |
|------|------|
| `/Actor/{label}` | 场景 Actor |
| `/Actor/{label}/{component}` | Actor 上的 Component |
| `/Game/{path}` | 资产（UE 标准路径，cat 支持） |
| `/Assets/{path}` | 资产（`/Game` 的别名，cat 支持） |
| `/Class/{name}` | 类信息（cat 支持） |

### 2. Plugin Ability（由 LLM 系列插件注册）

`help` 输出里的 `abilities` 段列出当前已注册的 ability。当前 Lite 配套的常见 ability：

| Ability | 来源插件 | 主要能力 |
|---------|----------|----------|
| `llmstatetree` | LLMStateTree | generate / inspect / export / copy / delete / compile |
| `ui` | LLMDynamicUI | generate / export / list-types / export-schema |
| `material` | LLMMaterial | generate / export / list-types / describe-type / export-schema |
| `llmms` | LLMMetaSound | generate / export / inspect |
| `llmwhitebox` | LLMWhitebox | create-box / create-subtract-box / create-cylinder / create-sphere / create-cone / create-stairs / list-brushes / get-brush / delete-brush / move-rotate / build-room / build-wall-segment / apply-default-material / rebuild-bsp-lighting / build-bsp |
| `uireactionbus` | UIWebBridge | send / subscribe / snapshot / bench / replay / diff |
| `python` | LLMEasyShellLite 内置 PyAbility | Lite PyAbility 框架（放 .py 到 `Content/Python/LLMShellAbilitiesLite/abilities/` 即注册） |

> **数据源**：`help` 实际输出 = `LLMEasyShellLiteSubsystem::RegisterAbility(TEXT("python"), PythonAbility)` + `LLMEasyShellLiteSubsystem::RegisterAbility(AbilityName, Info)` 模板 + 各 LLM 插件 `OnAllModuleLoadingPhasesComplete` 时序反射注册（LLMStateTreeEditorModule `FLLMStateTreeEditorModule::RegisterAsLLMEasyShellAbility` (full) + `::RegisterAsLLMEasyShellLiteAbility` (lite) / LLMDynamicUIEditorModule `::RegisterWithLLMEasyShell` (full AddLambda, v1.1 fix) + `::RegisterWithLLMEasyShellLite` (lite AddLambda) / LLMMaterialModule `FLLMMaterialModule::RegisterAsLLMEasyShellAbility` (full AddRaw) + `::RegisterAsLLMEasyShellLiteAbility` (lite AddRaw) / LLMMetaSoundEditorModule `FLLMMetaSoundEditorModule::RegisterAsLLMEasyShellAbility` (full AddRaw) + `::RegisterAsLLMEasyShellLiteAbility` (lite AddRaw) / LLMWhiteboxModule `FLLMWhiteboxModule::RegisterAsLLMEasyShellAbility` (full AddRaw) + `::RegisterAsLLMEasyShellLiteAbility` (lite AddRaw) / UIWebBridgeEditorModule `::RegisterAsLLMEasyShellAbility` + Lite/full `RegisterCommandHandlerReflective`）。缺哪个请检查对应 plugin module 是否加载。
>
> **锚符号名，不锚行号**（`references/lite-vs-full.md` r2294 教训）：本段早期版本写死 `:552` / `:571` / `:41` / `:45` 等行号，代码一挪就全漂 —— 实测 6 组锚点里 4 组当时已失效（`RegisterAbility(TEXT("python"))` / `RegisterAbility(AbilityName, Info)` 等实际位置均不在 doc 原写处；具体行号持续漂移，此处不写死）。故改为符号名。
>
<!-- Forensic: see SKILL_CHANGELOG.md §1 -->

<!-- Forensic: see SKILL_CHANGELOG.md §2 -->

这些是 **只读相关的子命令**（inspect / list-types / describe-type / export-schema / export），可以放心使用。
**任何会写资产/场景的子命令**（generate / copy / delete / compile）**在 Lite 里同样能直接调到** ——
Lite 与这些插件共享同一个 handler 实例，不做过滤、不做沙箱。写语义属于插件自己，不在 Lite 承诺的
只读范围内 —— 调之前自己评估风险，或改用 full 版 skill。

### 3. PyAbility 执行框架（已注册 + 4 内置 .py ability）

Lite 注册了 PyAbility 执行框架（`LLMEasyShellLiteSubsystem::RegisterAbility(TEXT("python"), PythonAbility)`），**内置 4 个 `.py` ability**（`simple` 端到端 demo + `gamestate` / `mesh_check` / `vfx_coverage` 三个只读子集），外加框架自身自动注册的 `reload`（重扫 abilities 目录 + 装 blocklist）—— 运行时 `help` 的 `python` 段共 **5** 个子命令。跑 `python simple hello world` 验证 PyAbility 框架可用；filesystem 锚定 `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/`。

<!-- Forensic: see SKILL_CHANGELOG.md §3 -->
如需注册自定义命令，在 `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/` 下放 `.py` 文件即可（不要 `_` 或 `__` 前缀，否则不注册）。⚠️ 你放的 `.py` 能调用完整 UE Python API —— **只读与否由你的代码决定，Lite 不做隔离**。

> **⚠️ 注意**：full 版本的 `python <name>` 数百个子命令（2026-10-25 runtime 读数 370 —— 同名时插件那份赢，涵盖 material / blueprint / asset / vfx / scene / level / umg /
> curve / datatable / editor / gameplay / reactive / hd3d / achievement / affix / archive / artifact / bestiary / biome / boss / bounty / build / career / character / chest / combat / curse / daily / death / equipment / events / evolution / firework / gameplayability / gameplaytag / glacier / heatmap / hints / identity / item / levelup / lifetime / loot / lore / metasound / missions / music / mutator / pcg / pets / pity / player / portal / reaction / reactive / relics / run / save / settings / showcase / sidebar / skilltree / sorceress / speedrun / stage / statistics / stats / status / tarot / trophy / wave / wealth / weapon / weather / wfc / cottage / webui / cheatgui / ability_cooldown / ability_usage / achievement_mastery / achievement_timeline / artifact_stats / biome_cycle / bomb_weapon / boss_rush / build_code / build_templates / career_stats / character_mastery / combat_statistics / combat_tempo / HUD widget abilities 等；上面这串域清单取自某一宿主工程的时点快照，仅示意广度）**Lite 没有内置**。Lite 有 `python` 框架 + 4 个内置 ability（`simple` / `gamestate` / `mesh_check` / `vfx_coverage`）；full 版独有的 Python 子命令请用 full skill 调用。
>
> **数量的真源是运行时，不是文档**：`python reload` 的输出（"Reloaded. Available commands: …"）或装载器日志里的 `Discovered N Python ability commands`。宿主工程的项目脚本目录（如 `Content/Features/<Feature>/Scripts/`）一直在长，写死数字必然变成化石 —— 2026-10-25 之前文档写 271、runtime 已到 370；2026-10-26 复核 filesystem 原始 .py 已 ~387 枚（插件托管 51+9+2+21 + 项目 304，去重/`_` 前缀规则后以 runtime 为准）。任何精确分解（N 插件 + M 项目）都是时点快照，别当常量引用。
>
<!-- Forensic: see SKILL_CHANGELOG.md §4 -->
>
<!-- Forensic: see SKILL_CHANGELOG.md §5 -->
>
<!-- Forensic: see SKILL_CHANGELOG.md §6 -->
>
<!-- Forensic: see SKILL_CHANGELOG.md §7 -->
>
<!-- Forensic: see SKILL_CHANGELOG.md §8 -->
>
<!-- Forensic: see SKILL_CHANGELOG.md §9 -->

---

## 端口

Lite 独占 TCP 端口段 **15201–15250**（50 端口）。Full LLMEasyShell 占用 15151–15200，
**完全互不重叠**——CLI 无需协商，各扫各的段。Lite 默认 15201。

端口文件：`llmshelllite/.current_port`

<!-- Forensic: see SKILL_CHANGELOG.md §10 -->

<!-- Forensic: see SKILL_CHANGELOG.md §11 -->

<!-- Forensic: see SKILL_CHANGELOG.md §12 -->

---

## Lite v1.1.0-lite — capability changes

**New since 1.0.0-lite:**

- `livecoding` (Windows only): triggers LiveCoding compile; use `--status` to query compile state. **别名 `reload` / `lc`** —— 命令真名是 `livecoding`，`reload` 是别名（两个都能用；`help` 输出里 `name` 字段是 `livecoding`，`aliases` 数组是 `reload` / `lc`）。
- Win32 ready-signal hook: lets `llm-shell --restart` wait on Lite editor readiness.
- 4 bundled Python abilities: `simple` (端到端 demo) + `gamestate` / `mesh_check` / `vfx_coverage` (read subset)。⚠️ 早期版本写的 `scene` 不存在 —— filesystem 里没有 `scene.py`，runtime 也没有该 ability。
- 5 promo tips in `help` output: LLMMaterial, LLMDynamicUI, LLMStateTree, LLMMetaSound, LLMEasyShell (Advanced). All same-publisher paid plugins.
- `@read_only` decorator with write-API blocklist (best-effort, not safety guarantee).

**Still NOT in Lite (by design):**

- Write *built-in* commands (set/spawn/rm/cp/mv/etc.), PIE control, UI introspection, MCP, screenshots, `log --compile` upgrade.
- ⚠️ 此清单只管**内置命令**。第三方 plugin ability 与 PyAbility runtime 的写能力**不在 Lite 控制范围内**(见上方定位)。

---


> **Forensic history**: 12 historical `[tool-fix-*]` meta-NOTE blockquotes moved to [SKILL_CHANGELOG.md](SKILL_CHANGELOG.md) (28KB forensic / 6KB actionable, this file 81% → ~19% meta-NOTE after extraction).

## 完整文档

- [experience/README.md](experience/README.md) — Lite 经验索引
- [references/lite-vs-full.md](references/lite-vs-full.md) — Lite vs Full 能力对照表