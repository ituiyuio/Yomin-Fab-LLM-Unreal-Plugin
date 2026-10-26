---
name: llm-easy-shell-skill-changelog
description: Historical forensic meta-NOTEs extracted from SKILL.md. Each entry preserves rootCause + source-of-truth + pattern codification from the original fix session.
metadata:
  type: forensic-archive
  source: .claude/skills/llm-easy-shell/SKILL.md
  extracted: 2026-07-10
---

# SKILL.md Forensic Changelog (extracted 2026-07-10)

> **Why**: llm-easy-shell/SKILL.md was 22% meta-NOTE blockquote (~7.4KB forensic / 25.6KB actionable content). Moved all `[tool-fix-*]` blockquotes here to keep the main skill doc readable for first-time agents. Mirrors Lite SKILL_CHANGELOG.md pattern (session118 extraction).
>
<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
>
> **Pointer policy**: Each block below has a stable `## §N` heading (chronological by fix-session). Future audits can cross-reference by §N.

## §1: `tool-fix-144 2026-06-29`

> Original SKILL.md L169 location preserved as HTML comment in main file. Content below is verbatim from the original blockquote.

> [tool-fix-144 2026-06-29] livecoding max wait drift 120s → 60s。active claim '最长 60s' 跟 source-of-truth (Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Reload.cpp:405 `constexpr double MaxWaitSeconds = 60.0;`) 1:1 对齐。原 doc 写 '最长 120s' 跟 cpp 60.0 constexpr drift 2x（实际 polling loop cap = 60.0，客户端 RECV_TIMEOUT_MS = 70000ms = 60s + 10s buffer 跟 server 端对齐）。3 surfaces 1 rootCause family 同步修复：ShellCommand_Reload.cpp:404 code comment + SKILL.md:155 + references/commands.md:242。Pattern 跟 tool-fix-130~143 doc-fossil fix 1:1 平行（meta-NOTE 解释 rootCause + source-of-truth 锚定 + preservation > rewrite）。

## §2: `tool-fix-173 2026-06-29`

> Original SKILL.md L170 location preserved as HTML comment in main file. Content below is verbatim from the original blockquote.

> [tool-fix-173 2026-06-29] line drift closure: ShellCommand_Reload.cpp:402 → :405 (off-by-3)。痛点: tool-fix-144 (2026-06-29) 写 meta-NOTE 时把 MaxWaitSeconds constexpr 锚定在 L402,但 2026-06-29 中段 livecoding polling loop 上面多加了 3 行 setup comment (workaround 'return -1; on first iteration + 中段插 3 行 client/server state comment'),L402 实际是 `// 客户端 RECV_TIMEOUT_MS = 70000ms = 60s + 10s buffer` 普通注释,MaxWaitSeconds constexpr 在 L405。Source-of-truth 2 重 lock 跟新 claim 1:1 锁定: (1) filesystem `grep -n "constexpr double MaxWaitSeconds" Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Reload.cpp` = L405 (1:1 anchor); (2) `awk 'NR==402 || NR==405' ShellCommand_Reload.cpp` L402=client RECV_TIMEOUT 注释 + L405=`constexpr double MaxWaitSeconds = 60.0;` (跟原 doc 锚定的 402 差 3 行进入下一个 setup block)。Fix scope 1 行 + 1 meta-NOTE: L160 锚点 402 → 405 + 改同段 'ShellCommand_Reload.cpp:401 code comment' 引用 → 404。Paired completion 跟 tool-fix-173 experience/02 + experience/03 同 family 但 sub-pattern 不同 (本 fix 是 setup comment 3 行插入导致 off-by-3, 别人是 refactor 派生 off-by-64 / off-by-94)。Runtime e2e 走 (a) full llm-shell.exe --help UE 5.8 binary sanity OK + (b) lite llmshelllite.exe --help UE 5.8 binary sanity OK + (c) source-level 2 重 lock (filesystem grep 405 exact + awk NR==402 跟 NR==405 diff 3 行) 跟 binary sanity e2e 跟 tool-fix-130~172 pattern 1:1 平行。Pre-existing C2369 kCategoryShortNames 跟本 fix 解耦。

## §3: `tool-fix-07 session34 2026-07-09`

> Original SKILL.md L231 location preserved as HTML comment in main file. Content below is verbatim from the original blockquote.

> [tool-fix-07 session34 2026-07-09] closure: 「已注册 Skills」plugin 列表遗漏 LLMWhitebox doc-fossil 闭合 — 原 L229 列 8 plugin (vfx/material/ui/pcg/llmms/llmstatetree/quixel/python) 但 runtime `./llm-shell.exe -q -j -c help` 实际返 9 plugin ability (8 原有 + `llmwhitebox` / LLMWhitebox / 15 commands / `whitebox create-box|create-subtract-box|create-cylinder|create-sphere|create-cone|create-stairs|list-brushes|get-brush|delete-brush|move-rotate|build-room|build-wall-segment|apply-default-material|rebuild-bsp-lighting|build-bsp`)。Root cause: tool-fix-262 (2026-06-29, methodology SKILL.md L1216-1226 '## 参考案例' table 3→9 plugin row closure) 跟 tool-fix-284 (2026-07-09, Lite preflight FALLBACK_COMMANDS 7 plugin hardcode) 都跟 `Plugins/LLMWhitebox/` 同期 ship 但本文件 L229 「已注册 Skills」列表在 tool-fix-262 后未 sync (跨 skill ref-table-drift 同期 pattern 跟 session8 methodology SKILL.md L1219 '## 参考案例' table LLMEasyShell row 28→36 + 196→265 count-drift 1:1 平行)。Source-of-truth 4 重 lock 跟新 claim 1:1: (1) filesystem `ls Plugins/LLMWhitebox/LLMWhitebox.uplugin` ✓ + `cat Plugins/LLMWhitebox/LLMWhitebox.uplugin | jq .EngineVersion` = "5.8.0" 跟 CODEO.uproject EngineAssociation:5.8 1:1 lock; (2) runtime `./llm-shell.exe -q -j -c help` JSON parse `llmwhitebox` ability present, enabled=True, plugin=LLMWhitebox, version=0.1.0, commands=15 ✓ 跟 list 1:1; (3) lite SKILL.md L105 `tool-fix-284` meta-NOTE 显式 list 7 plugin ability (含 `llmwhitebox`) ✓ 跟新 list 1:1 cross-skill lock; (4) Plugins/ 目录共 11 LLM 插件 (LLMDynamicUI/LLMEasyShell/LLMEasyShellLite/LLMMaterial/LLMMetaSound/LLMPCG/LLMQuixel/LLMStateTree/LLMSurvivorShell/LLMVFX/LLMWhitebox) 其中 9 注册 ability + 2 是 C++ helper library (LLMSurvivorShell 366+ UFUNCTION + AgoraPlugin utility), 「已注册 Skills」列表 9 项跟 runtime 1:1 lock。Fix scope 1 file +1 char (L229 list 加 `llmwhitebox (LLMWhitebox)`)。未加新 audit pattern — 本 class drift (list-omission vs runtime) static-regex 难 catch (regex 只能正向匹配 literal token, 负向匹配 'literal X missing from list Y' 需 multi-line state machine), 靠 future session invariant 'Plugins/ 加新 LLM plugin 时必同步更新本 L229 列表 + methodology SKILL.md L1216-1226 table + Lite FALLBACK_COMMANDS (tool-fix-284 7-plugin list)' 4 重 lock 1:1。Runtime e2e 走 (a) `python .claude/skills/doc-audit.py` 600 file exit 0 OK ✓ + (b) `./llm-shell.exe -q -j -c help` 11 ability 1:1 lock 新 list ✓ + (c) `./llmshelllite.exe -q -j -c 'help llmwhitebox'` 返 whitebox ability enabled=True + 15 command list ✓ (跟 full runtime 1:1, Lite preflight 也能 resolve) + (d) binary sanity `./llm-shell.exe --help` UE 5.8 ✓ + (e) Lite `./llmshelllite.exe --help` UE 5.8 ✓。Concurrent session: 无 collision, tool-fix-07 session34 chronological 顺延 session33 (54b98c8) + session32 (5e78eef) + session31 (3e65286) + session30 (9ea7c33) + session29 (d2fb043) + session28 (8e47425) + session27 (047ed3a) + session26 (621f800) + session25 (b32a073) + session24 (6166ec0) + session23 (4d3c4c6) + session22 (47a80f3+d790e1a) + session21 (70fd7be) + session20 (3955fee) + session19 (937fe71) + session18 (74749f2) + session17 (8ab1c1b) + session16 (803aa48) + session15 (dbb6161) + session14 (82e210b) + session13 (ae0ed82) + earlier。Pre-existing C2369 kCategoryShortNames (tool-fix-145 unblocked) 跟本 fix 解耦。

## §4: `2026-10-26` references 勘误批（commands.md / editor-shot-win32.md / llm-screenshot.md / SKILL.md 截图段）

> 本批为**文档面勘误**，无源码改动：(1) commands.md 原生命令计数勘误 —— r2294（10-23）曾把基准从 36 订正为 38，10-25 `ui state` 外迁 LLMSurvivorShell 后真值回 **37**（`RegisterBuiltInCommands` 存活调用 37、`ShellCommand_*.cpp` 37 枚同源；装宿主插件时 runtime 38），本批把 38 全部归正并完整记录三段沿革；(2) commands.md 三处行号化石（`:977` / `:623-630` / `Types.h:1900-2055`）改锚符号名；(3) editor-shot-win32.md / llm-screenshot.md 与 editor_shot.ps1 对齐（`-Pie` 退出码 6、独立窗口前置条件、参数表、异步截图取舍、`-ExecutionPolicy Bypass`）；(4) SKILL.md 截图段 `saved:` 样例从相对路径改为解析后绝对路径口径。配套：verify-e2e.py Build.cs 锁判据重写 + ue-bridge 棘轮 303→0（见该文件内勘误注）。
