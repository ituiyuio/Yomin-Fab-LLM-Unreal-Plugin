---
name: llmshelllite-actual-capabilities-2026-06-14
description: "llmshelllite (Lite) is NOT a copy of full — 2026-06-14 baseline verified 9 read-only commands + 3 plugin abilities (statetree/ui/material), 2026-06-29 [tool-fix-133] runtime re-verified 5 abilities (python framework + material/llmstatetree/ui/llmms) after llmms was added in 2026-06-21+. Port 15201-15250. ✅ [tool-fix-285 2026-07-09] `-q`/`-j` flags 1:1 ported from full; ✅ [tool-fix-166 2026-06-29] 1 built-in `simple.py` demo registered; no log --compile, no screenshots, no write commands. Python framework + 1 built-in demo (Lite 与 full python ability 270 个独有子命令对齐时需要 full skill — runtime 当前实测 270 (canonical 271 = 53 内置 plugin + 228 game-specific − 5 重名 − 6 私有 + 1 reload, post-reload 状态), 见 [tool-fix-07 session3 2026-07-09 + session141 2026-07-10 + session150 2026-07-11 forward-fossil closure + session153 2026-07-11 arithmetic-fossil 闭合 (原 "runtime 272 = 271 − 1 + 1" 算式 broken — 271−1+1=271 ≠ 272)]). ✅ [tool-fix-07 session76 2026-07-10] runtime re-verified 7 abilities (python + llmstatetree + ui + material + llmms + llmwhitebox + uireactionbus) — llmwhitebox [tool-fix-07 session36 2026-07-09] + uireactionbus (UIWebBridge Phase 4 2026-07-10 added)."
metadata:
 node_type: memory
 type: project
 originSessionId: 0b724056-879d-4ca8-82ee-bae7851dfa7e
---

# llmshelllite 真实能力边界（2026-06-14 baseline + 2026-06-29 tool-fix-133 重新验证 + 2026-07-10 tool-fix-07 session76 扩展到 7 abilities）

> [tool-fix-133 2026-06-29] 历史 context：原 doc 写 "3 plugin ability + No python ability" 是 2026-06-14 当日真实 snapshot（彼时 llmms 还没作为 Lite ability 注册 — `LLMMetaSound` `RegisterAsLLMEasyShellAbility` 在 2026-06-21 mcp feature 上线后才有 Lite 接入 + `python` ability 框架也已在 baseline 时存在但 doc 描述模糊）。**当前 runtime truth（`./llmshelllite.exe help` 2026-07-10 实测）= 7 abilities**: python (framework, 1 command) + material (5 commands) + llmstatetree (6 commands) + ui (4 commands) + llmms (3 commands) + llmwhitebox (15 commands) + uireactionbus (6 commands, UIWebBridge Phase 4). LLM 看 SKILL.md L62-68 表（current canonical 7 abilities）跟本 forensic record L14 (现修后 7 abilities) 1:1 闭环.

## Lite 实际有 ✅（2026-07-10 runtime verify）
- **9 个只读命令**: ls/cat/find/discover/info/help/gamestate/log/msglog
- **7 个 ability**（2026-06-14 baseline 时 3 个 + llmms 2026-06-21+ + llmwhitebox [tool-fix-07 session36 2026-07-09] + uireactionbus 2026-07-10 UIWebBridge Phase 4）: python (framework, **1 内置 `simple` demo** [tool-fix-166 2026-06-29] closed '0 内置' fossil) / material (5 cmds) / llmstatetree (6 cmds) / ui (4 cmds) / llmms (3 cmds) / llmwhitebox (15 cmds) / uireactionbus (6 cmds, send/subscribe/snapshot/bench/replay/diff)
- **PyAbility 执行框架**（[tool-fix-166 2026-06-29] 1 内置 `simple.py` demo 注册; 框架注册但需用户放 .py 到 `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/`）
- **端口段 15201-15250**（与 full 15151-15200 不冲突）
- 二进制: `D:/UnrealEngine/CODEO/.claude/skills/llm-easy-shell-lite/llmshelllite/llmshelllite.exe` (tool-fix-169 2026-06-29 directory rename 跟 binary name 对齐)

## Lite 没有 ❌（用 full [llm-easy-shell](../../llm-easy-shell/SKILL.md)）
- 任何写操作（set/spawn/rm/cp/mv/call/save/new/addcomp）
- PIE 控制（play/stop/pause）
- 编译周期（livecoding/restart/undo/redo/reload）
- `log --compile`（Lite 报 "Compile log capture is only available in LLMEasyShell Advanced"）
- 截图（PIE 截图 + Win32 editor_shot.ps1 都没有）
- ~~`-q` / `-j` CLI 旗标（Lite 实现没带，stdout 直接显示 stderr noise）~~ [tool-fix-285 2026-07-09] 已闭合：Lite `main.cpp` 1:1 port `g_QuietMode` + `g_JsonOnlyMode` + ExtractInnerOutputJson + `-q`/`--quiet`/`-j`/`--json-only` arg-loop，跟 full `llm-shell` 1:1 对齐
- ~~`python <name>` 196 子命令 (44 plugin + 155 project − 4 重名 + 1 reload, ...)~~ [tool-fix-07 session3 2026-07-09] 已闭合：当前 full 实际是 **271** (53 plugin + 228 project − 5 重名 − 6 私有 + 1 reload, 含 `cottage_build`/`gensokyo_characters_test`/`gensokyo_e2e_test`/`gensokyo_regression_test`/`portal_interaction_test` 5 dup + 1 reload auto-add)，+75 over 12d 见 [llm-easy-shell/SKILL.md:218](../../llm-easy-shell/SKILL.md) + [llm-easy-shell-lite/SKILL.md:19](../SKILL.md)

## 已知 Lite 缺陷
- ~~**Preflight 不识别 plugin ability**: 每次跑 `material generate` / `ui list-types` / `statetree inspect` 都会先看到红色 `[preflight] Unknown command: '<name>'` warning，但子命令本身能跑~~ [tool-fix-284 2026-07-09] 已闭合：`KNOWN_COMMANDS` + `FALLBACK_COMMANDS` 硬编码扩到 17 (原 9 native + `python` → +7 plugin: material/ui/llmstatetree/vfx/llmms/pcg/llmwhitebox)，preflight 不再报 plugin ability 红色 unknown
- ~~**`<ability> --help` 不工作**: `material --help` / `ui --help` / `statetree --help` 全报 unknown command，但子命令直接调用能跑~~ [tool-fix-07 session5 2026-07-09] 已闭合：`ShellCommand_Help.cpp` delegate `CommandDispatcher` (single-source-of-truth) + `help` 列表改 iterate dispatcher (sort + aliases) + `help <cmd>` 加 dispatcher-fallback 调 `Reg.Command->GetDescription/GetUsage()`，8 漏报命令 (mcp + 7 ui) 全部 now help 1:1
- **find Actor Enemy* 可能返回 0**: 不是 Lite 坏了，是场景里没 Enemy（Survivor 是按需生成）

## SKILL.md 已重写（2026-06-14）
- 之前 SKILL.md 写得像 full（-q/-j/log --compile/python ability 全列），实际 Lite 跑不通
- 现在只描述 Lite 真实能力，链接到 full skill 做"需要写操作"
- 清理了 full 残留：删 `references/commands.md` / `references/llm-screenshot.md` / `scripts/` 空目录 / experience 4 个 full 文件
- 现在的 Lite skill 文件结构（行数为 2026-06-14 重写时快照,后续 .md 编辑会让 line count drift,实际行数请用 `wc -l` 验证）：
 ```
 SKILL.md (~109 行)
 experience/README.md (~39 行索引)
 experience/debugging.md (~317 行, full 共享 C++ 实现)
 experience/02-pyability-framework.md (~80 行)
 references/lite-vs-full.md (~85 行对照表)
 ```

## Why
用户偏好: "Lite 保持最干净状态，只保证查询能力 + llm 系列插件 ability + pyability 框架"

## How to apply
- LLM 想跑 Lite 跑不通的功能时（如 set/spawn/截图）→ 直接跳 full skill
- 不要在 Lite 文档里宣传 Lite 没实现的功能
- 跨能力检查: 看到 SKILL.md 列了某命令 → 先用 `info` + `help` 验证它真的能跑