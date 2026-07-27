# LLMEasyShell Lite vs Full 能力对照表

Lite 是 LLMEasyShell 的**最精简只读子集**，只暴露查询类能力。Full 版提供完整 36 命令 + Python ability 271 子命令 (53 内置 plugin + 228 game-specific − 5 重名 − 6 私有 + 1 reload) + 写操作能力 + 截图能力。

> [tool-fix-141 2026-06-29] 闭合 tool-fix-140 (commit 8b0c152) 留下的 sub-fossil：命令数 28 → 36。原 doc 写 "完整 28 命令" 是 tool-fix-140 部分修复 Python ability 25+ → 175 时漏修的 fossil，源-of-truth = `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp:L1460-1495` 36 个 `RegisterCommand` 调用 1:1 对齐（`find Plugins/LLMEasyShell/Source/LLMEasyShell/Private -name 'ShellCommand_*.cpp' | wc -l` = 36 同源 double lock），跟 `llm-easy-shell/SKILL.md:207 '36 个原生命令 = 28 核心 + 7 UI 调试 + 1 已弃用 livelog'` + `llm-easy-shell/references/commands.md:7,15,16 '共 36 个,直接通过 CommandDispatcher 注册'` 全部一致。Runtime `./llm-shell.exe --help` 二进制输出 UE 5.8 binary 仍 health（无 crash、无 command list 注册差异）。
>
> [tool-fix-149 2026-06-29] tool-fix-141 meta-NOTE 内 fossil 锚定 sub-closure: L1457-1492 → L1460-1495 (跟 tool-fix-149 commands.md L16 锁定 1:1)。tool-fix-141 写 meta-NOTE 时是当时已 fossil 的 cpp 注释锚定 (tool-fix-146 2026-06-29 commit d43280d 跟 tool-fix-141 同日 ship 注释里 fossil 锚点 L1458-1493 跟 cpp 实际 L1460-1495 差 3-4 行), tool-fix-141 信任了 self-claimed anchor 没回 cpp 验证。Source-of-truth 跟 commands.md:16 同。
>
> [tool-fix-149 2026-06-29] 闭合 tool-fix-140/141 (175) 留下的 sub-fossil：Python ability 175 → 185。Survivor 项目 2026-06 下半月继续加 9 个 game-specific abilities (Content/Features/Survivor/Scripts/ 从 135 扩到 144)，跟 plugin 重名 4 个 (gensokyo_characters_test / gensokyo_e2e_test / gensokyo_regression_test / portal_interaction_test) 从 5 减到 4。验证：runtime `./llm-shell.exe -q -j -c help` JSON `python` ability 实际 commands 数 = 184 + 1 reload = 185（runtime 1:1 验证）；canonical source-of-truth = plugin 44 + project 144 = 188 raw 文件，去重 4 后 184 + reload = 185（4 重 lock 全部对齐，跟 tool-fix-140/141 partial-fix 模式互补 closure 1 rootCause family）。
>
> [tool-fix-159 2026-06-29] 闭合 tool-fix-149 (commit 87a2a53) 留下的 0-day re-occurrence：185 → 193。Survivor 项目 v238-v250 wave 8 HUD widget 期间又加 8 个 game-specific abilities (player_action_timeline_hud_v238 / skill_learning_journal_hud_v239 / hint_hud_v240 / run_history_hud_v241 / character_mastery_hud_v245 / run_grade_hud_v247 / pet_mastery_hud_v248 / bestiary_hud_v249, Content/Features/Survivor/Scripts/ 从 144 扩到 152)。Dups 仍 4 跟 tool-fix-149 一致未变。验证：filesystem plugin 44 + project 152 - 4 dups + 1 reload = 193 (3 重 lock: filesystem 193 + meta-NOTE chain tool-fix-140/149/159 + doc claim 193 全部对齐, runtime 4 重 lock 待 editor 启动验证)。Drift signature: 144 → 152 = +8 over 1 day, 跟 tool-fix-142 → tool-fix-157 sakura-brass 0-day re-occurrence + tool-fix-149 → tool-fix-159 同 family 'tool-fix-N partial-fix 0-day cycle when HUD widget directory is active during a session'。
>
> [tool-fix-160 2026-06-29] 闭合 tool-fix-159 (commit d2584fb) 留下的 0-day re-occurrence 3rd cycle：193 → 195。Survivor 项目 v251-v252 wave 2 HUD widget 期间又加 2 个 game-specific abilities (identity_hud_v251 / statistics_trends_hud_v252, Content/Features/Survivor/Scripts/ 从 152 扩到 154)。Dups 仍 4 跟 tool-fix-149/159 一致未变。验证：filesystem plugin 44 + project 154 - 4 dups + 1 reload = 195 (3 重 lock: filesystem 195 + meta-NOTE chain tool-fix-140/149/159/160 + doc claim 195 全部对齐, runtime 4 重 lock 待 editor 启动验证)。Drift signature: 152 → 154 = +2 over hours, 跟 tool-fix-149 → tool-fix-159 → tool-fix-160 同 family 'tool-fix-N partial-fix 0-day cycle when HUD widget directory is active during a session' (paired completion of tool-fix-159 4th cycle, 跟 tool-fix-140→149→159 paired completion chain 1:1 平行)。
>
> [tool-fix-162 2026-06-29] 闭合 tool-fix-160 (commit f6db4d4) 留下的 0-day re-occurrence 4th cycle：195 → 196。Survivor 项目 v253 wave 1 HUD widget 期间又加 1 个 game-specific ability (showcase_hud_v253, commit ac3cced Showcase HUD v1.0 第 253 子系统, Content/Features/Survivor/Scripts/ 从 154 扩到 155)。Dups 仍 4 跟 tool-fix-149/159/160 一致未变。验证：filesystem plugin 44 + project 155 - 4 dups + 1 reload = 196 (3 重 lock: filesystem 196 + meta-NOTE chain tool-fix-140/149/159/160/162 + doc claim 196 全部对齐, runtime 4 重 lock 待 editor 启动验证)。Drift signature: 154 → 155 = +1 over hours, 跟 tool-fix-149 → tool-fix-159 → tool-fix-160 → tool-fix-162 同 family 'tool-fix-N partial-fix 0-day cycle when HUD widget directory is active during a session' (paired completion of tool-fix-160 5th cycle, 跟 tool-fix-140→149→159→160 paired completion chain 1:1 平行)。
>
> [tool-fix-140 2026-06-29] 原 doc 写 "28 命令 + Python ability 25+ 子命令" 是 2026-06-14 baseline 当时的快照。Runtime 当前验证: Full 实际有 36 个原生命令（不是 28）+ 196 个 Python ability（不是 175，tool-fix-149 2026-06-29 进一步 +10 → tool-fix-159 2026-06-29 又 +8 → tool-fix-160 2026-06-29 又 +2 → tool-fix-162 2026-06-29 又 +1），命令数扩到 36 是 2026-06 月陆续加的 `addcomp`/`lc`/`reload`/`mkdir`/`gamestate`/`ui`/`material`/`vfx` 等。详见 llm-easy-shell/SKILL.md L207。

---

## 命令对比

| 命令类别 | Full | Lite | Lite 说明 |
|----------|------|------|-----------|
| `ls` / `cat` / `find` / `discover` / `info` / `help` | ✅ | ✅ | 完全相同 |
| `gamestate` | ✅ | ✅ | 完全相同 |
| `log --errors` | ✅ | ✅ | 完全相同 |
| `log --compile` | ✅ | ❌ | Lite 不支持编译日志捕获，要 Advanced skill |
| `msglog --niagara` | ✅ | ✅ | 完全相同 |
| `set` / `spawn` / `rm` / `cp` / `mv` / `call` | ✅ | ❌ | Lite 无写操作 |
| `save` / `new` / `mkdir` / `addcomp` | ✅ | ❌ | Lite 无资产管理 |
| `play` / `stop` / `pause` | ✅ | ❌ | Lite 无 PIE 控制 |
| `undo` / `redo` / `reload` | ✅ | ❌ | Lite 无编辑历史 |
| `livecoding` / `lc` | ✅ | ❌ | Lite 无编译周期管理 |

---

## Ability 对比

| Ability | 来源 | Full | Lite |
|---------|------|------|------|
| `llmstatetree` | LLMStateTree plugin | ✅ | ✅ |
| `ui` | LLMDynamicUI plugin | ✅ | ✅ |
| `material` | LLMMaterial plugin | ✅ | ✅ |
| `llmms` | LLMMetaSound plugin | ✅ | ✅ |
| `llmwhitebox` | LLMWhitebox plugin | ✅ 15 commands | ✅ 15 commands (跟 Full 1:1) |
| `uireactionbus` | UIWebBridge plugin | ✅ 6 commands | ✅ 6 commands (跟 Full 1:1) |
| `python` | LLMEasyShell Lite PyAbility | ✅ 271 内置子命令 (53 plugin + 228 project − 5 重名 − 6 私有 + 1 reload) | ⚠️ 框架注册 + 1 内置 `simple` demo (端到端验证) |

> `python <name>` Full 包含：`material` / `blueprint` / `asset` / `vfx` / `scene` / `level` / `umg` / `curve` / `datatable` / `editor` / `gameplay` / `gameplaytag` / `gameplayability` / `navigation` / `poseseach` / `chooser` / `property` / `bpcomp` / `bpprop` / `reparent` / `perf` / `anim` / `reactive` / `hd3d` / `hd3dpostprocess` / `hd3dscene` 等
> Lite 端 `python` 框架已注册（`LLMEasyShellLiteSubsystem.cpp:552 RegisterAbility(TEXT("python"), PythonAbility)`）+ **1 个内置 `simple` demo ability**（验证 PyAbility 端到端可用，filesystem 锚定 `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/simple.py`）；用户可放 .py 到 `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/` 注册自定义只读命令。

---

## 截图能力对比

| 截图路径 | Full | Lite |
|----------|------|------|
| `python editor screenshot` (PIE 视口) | ✅ | ❌ |
| `editor_shot.ps1` (Win32 窗口) | ✅ `.claude/skills/llm-easy-shell/scripts/editor_shot.ps1` | ❌ |

**Lite 需要截图怎么办**：用 full skill [llm-easy-shell](../../llm-easy-shell/SKILL.md)。

---

## CLI 旗标对比

| 旗标 | Full | Lite |
|------|------|------|
| `-q` / `--quiet` | ✅ 重定向 stderr noise 到 quiet log | ✅ 已实现 ([tool-fix-285 2026-07-09]) |
| `-j` / `--json-only` | ✅ 解包嵌套 JSON output | ✅ 已实现 ([tool-fix-285 2026-07-09]) |

**Lite 跑命令直接看 stdout**（带 stderr noise 是预期行为）。

---

## 端口对比

| 范围 | 用途 |
|------|------|
| 15151–15200 | Full LLMEasyShell |
| 15201–15250 | Lite LLMEasyShell |

两个 CLI 端口段**严格不重叠**，可同时运行。

---

## 何时用哪个

**用 Lite**：
- 只需要查询（看场景、看资产、看日志、看 game state）
- 不确定要不要改东西（安全探索）
- 想最小依赖

**用 Full**：
- 需要写操作（改属性、生成资产、PIE 控制）
- 需要截图
- 需要 `python <name>` 271 子命令
- 需要 `-q` / `-j` 旗标（让 LLM parse 更简单）
- 需要 `log --compile`

**两者切换**：在不同目录运行不同二进制，不冲突。