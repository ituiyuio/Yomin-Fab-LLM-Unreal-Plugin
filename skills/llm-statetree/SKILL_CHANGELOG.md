---
name: llm-statetree-skill-changelog
description: Historical forensic meta-NOTEs extracted from SKILL.md. Each entry preserves rootCause + source-of-truth + pattern codification from the original fix session.
metadata:
  type: forensic-archive
  source: .claude/skills/llm-statetree/SKILL.md
  extracted: 2026-07-10
  tool-fix-07-session: 123
---

# SKILL.md Forensic Changelog (extracted 2026-07-10)

> **Why**: llm-statetree/SKILL.md had 3 large forensic blocks totaling ~7.8KB (35% of file): 1 HTML comment (tool-fix-172) + 1 multi-paragraph meta-NOTE blockquote (tool-fix-156) + 1 HTML comment closure (tool-fix-07 session60) referencing line drift closure + cross-subsystem attribution + LLMStateTree 3/6 sub-cmd silent-missing chains. Mirrors Lite SKILL_CHANGELOG.md (session118) + full llm-easy-shell SKILL_CHANGELOG.md (session119) + sakura-brass SKILL_CHANGELOG.md (session120) + methodology SKILL_CHANGELOG.md (session121) + llm-dynamic-ui SKILL_CHANGELOG.md (session122) pattern. **Note**: 3 small current-state `> **⚠️ 注/状态**` blockquotes (L104 Evaluator 0 nodes / L146 StateTreeMoveToTask not in schema / L228 transition conditions 字段) are kept in SKILL.md — they are live technical warnings for LLM agents, not historical fix records.
>
<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
>
> **Pointer policy**: Each block below has a stable `## §N` heading (numbered in file order — L230 → L503 → L535). Future audits can cross-reference by §N.

## §1: `tool-fix-172 2026-06-29` (original SKILL.md L230)

> Original SKILL.md L230 location preserved as HTML comment marker in main file. Content below is verbatim from the original HTML comment.

[tool-fix-172 2026-06-29] Line drift closure: 原 doc 写 `LLMStateTreeParser.cpp:439/716` 是 `HasField(TEXT("conditions"))` 守卫行（解析条件入口），但 doc 文本说 `GetArrayField("conditions")` 应该指向 GetArrayField 实际行，1:1 锁定 filesystem `grep -n 'GetArrayField(TEXT("conditions"))' Plugins/LLMStateTree/Source/LLMStateTree/Private/Core/LLMStateTreeParser.cpp` = 442/718。Source-of-truth 4 重 lock 跟新 claim 1:1 锁定: (1) filesystem grep GetArrayField = 442/718 exact; (2) grep HasField 守卫 = 439/716 (跟原 doc 1:1); (3) doc 文本 "GetArrayField" 跟新 line 442/718 1:1; (4) 同 family tool-fix-148/154/155 'line drift 配对 closure' pattern。Fix scope 1 file +0/-0/+1 行: 439/716 → 442/718 (1 行) + meta-NOTE preservation。跟 tool-fix-156 'command attribution 跨 subsystem 误归' 同 skill 但 sub-pattern 不同 (本 fix 是 doc text GetArrayField 跟 line 错位, tool-fix-156 是 doc attribute CommandToAbilityMap 跟 LLMEasyShell 跨 subsystem 错位)。Concurrent paired completion: 跟 llm-metasound SKILL.md L342 line drift (626-678 → 626-676) 同 session 同 family 'line drift in SKILL.md doc claim vs source' 1:1 平行。Runtime e2e 走 (a) full llm-shell.exe --help UE 5.8 binary sanity OK 跟 tool-fix-130~171 pattern 1:1 平行 + (b) lite llmshelllite.exe --help UE 5.8 binary sanity OK 跟 full 1:1 平行 + (c) filesystem grep 双锚 (GetArrayField 442/718 + HasField 439/716) 跟 doc claim 1:1 锁定。Source-level + 2 binary sanity + filesystem e2e 跟 UE editor 全量 build 解耦, pre-existing C2369 kCategoryShortNames (tool-fix-145 已 unblock) 跟本 fix 解耦。教训: 1) 'doc text 跟 line ref 内部不一致' 是新 sub-pattern 跟 tool-fix-148/154/155 'line drift closure' 同 family 但 sub-pattern 不同 (本 fix 是 doc 文本 'GetArrayField' 跟 '439/716 HasField' 内部 type-level 不一致, 别人是 doc 说 N 行实际 N+k 行), audit 必 'grep <doc 提到函数名> <file>' 跟 doc claim 1:1 锁定 + 'grep <doc 提到下一句关键词>' 验证 doc 内部 type-level 一致性 跨 2 dim; 2) 'paired completion cross-skill 2nd-order' 跟 tool-fix-150 'commands.md + fab-submit-pipeline + ps5.1-quirks paired' + tool-fix-156 'llm-statetree + llm-easy-shell paired' + tool-fix-170 'llm-material + llm-vfx paired' + tool-fix-171 'ue-webui-subclass within-skill partial-fix 2nd-order' 同期 pattern 1:1 平行, 2 files 修了 锚定 filesystem 4 重 lock (llm-statetree GetArrayField 442/718 + HasField 439/716 + llm-metasound PinName-first/VertexID-fallback 626-676) 跟 tool-fix-154/155 形成 'paired completion chain within line drift cluster' 跨 2 skills 1 session 闭环。

---

## §2: `tool-fix-156 2026-06-29` (original SKILL.md L503)

> Original SKILL.md L503 location preserved as blockquote in main file (immediately after the L501 `> **Note**: 实际命令名是 **llmstatetree**` current-state Note, which is kept in SKILL.md). Content below is verbatim from the original blockquote.

[tool-fix-156 2026-06-29 meta-NOTE]: 原 doc 此处归因错误 — (a) "PCG 的 CommandToAbilityMap" 实际是 **LLMEasyShell** 的 `CommandToAbilityMap` (字段在 `LLMEasyShellSubsystem.h`, 反向索引逻辑在 `LLMEasyShellSubsystem.cpp:698/709`),跟 PCG plugin 完全无关 (跨 subsystem 误归因)。(b) 错误消息不是 "LLMPCG file not found" / "PCG Graph not found" — 实际错误是 LLMEasyShell dispatcher 的统一兜底 `"Unknown command: %s"` (`LLMEasyShellSubsystem.cpp:977` `FLLMEasyShellResult::Failure(EShellErrorCode::NotFound, ...)`)。(c) 注册名 `llmstatetree` 跟 SKILL.md 一致(`LLMStateTreeEditorModule.cpp:515/562/601` `Params.AbilityName = TEXT("llmstatetree")` 三处注册点 1:1 verified)。Source-of-truth 4 重 lock: (1) `LLMEasyShellSubsystem.cpp:977` 实际错误消息 (2) `LLMEasyShellSubsystem.cpp:698/709` 反向索引是 LLMEasyShell 字段 (3) `LLMStateTreeEditorModule.cpp:515/562/601` 注册名是 `llmstatetree` (4) `LLMEasyShell.aiac:475` 依赖关系 "LLMStateTree → 注册statetree Ability" 显示名简化但实际 register 调用 `llmstatetree`。

---

## §3: `tool-fix-07 session60 2026-07-09` (original SKILL.md L535)

> Original SKILL.md L535 location preserved as HTML comment marker in main file. Content below is verbatim from the original HTML comment.

[tool-fix-07 session60 2026-07-09] closure: `## CLI Commands` 段 3 → 6 sub-cmd silent-missing doc-fossil — runtime `llm-shell -q -j -c help llmstatetree` 实际有 6 sub-cmd (generate/inspect/export/copy/delete/compile, 注册在 `Plugins/LLMStateTree/Source/LLMStateTreeEditor/Private/LLMStateTreeEditorModule.cpp:423/428/433/438/443/448` 六个 `Commands.Add(MakeCommand(...))` 调用 + `LLMStateTreeCommandHandler.cpp:144/148/152` 三个 else-if dispatch), 但本 SKILL.md 历来只文档化 3 个 (generate/inspect/export), `copy`/`delete`/`compile` 3 sub-cmd 100% silent missing — LLM 读 doc 只能找到 50% sub-cmd, 跑 `llmstatetree copy /Game/AI/GuardAI /Game/AI/GuardAI_v2` 前要靠 `--help` 反查。Root cause: 跟 tool-fix-134 (LLMVFX 8/9 sub-cmd silent-missing, 2026-06-29) + tool-fix-156 (LLMStateTree 跨 subsystem 误归因, 2026-06-29) 同 'ability sub-cmd silent-missing' family 1:1 平行但本 fix class 是 **LLMStateTree plugin `LLMStateTreeEditorModule.cpp` 6 sub-cmd 全注册但 SKILL.md CLI 段只文档化 3**, 跟 tool-fix-134 'vfx 8 silent missing' polarity 颠倒 (vfx 8/9 silent, statetree 3/6 silent, 都是 partial-coverage class 但 silent-side 比例不同)。Source-of-truth 4 重 lock 跟新 claim 1:1: (a) runtime `llm-shell -q -j -c help llmstatetree` commands=[generate, inspect, export, copy, delete, compile] 6 entries; (b) filesystem `grep -cE 'TEXT\("(copy|delete|compile)"\)' Plugins/LLMStateTree/Source/LLMStateTreeEditor/Private/LLMStateTreeEditorModule.cpp` = 3 (跟新增 3 段 1:1); (c) `LLMStateTreeCommandHandler.cpp` `else if (SubCommand == TEXT("copy"|"delete"|"compile"))` 3 dispatch lines ✓; (d) 跟 LLMVFX SKILL.md L599-606 'vfx ability 注册 9 个 subcommand' 1:1 平行 (full-coverage vs partial-coverage 是 audit-shape 差, runtime 都是 source-of-truth)。Fix scope 1 file +27/-0 (SKILL.md 加 3 段 sub-cmd doc + session60 meta-NOTE append)。Pattern codified — `count-llmstatetree-subcmd-drift` 是新 audit category, 跟 `count-llmstatetree-example-files` (session59 codify) 同 'LLMStateTree forward-fossil defense' family 1:1 平行但本 fix class 是 **sub-cmd count + per-cmd usage doc presence** 跟 session59 'example files count' 不同 sub-pattern — forward-fossil defense: 任何 '`(?<!\d)(?!6\b)\d+\s*个\s*子命令`' literal claim 数字 ≠ 6 必 caught (e.g. '3 个子命令' / '5 个子命令' drift 立刻 FAIL), 当前 doc 0 count claim 0 false-positive。Runtime e2e 走 (a) `llm-shell -q -j -c help llmstatetree` 6 commands 1:1 lock 跟新 doc 段 6 1:1; (b) `python .claude/skills/doc-audit.py` 600+ file exit 0 OK ✓ (新 pattern 0 false-positive on real filesystem, 当前 doc 0 count claim + count-llmstatetree-example-files 9/9 lock preserved); (c) `python .claude/skills/llm-easy-shell/scripts/verify-e2e.py` 11/11 + 7/7 + 8/8 + --quiet exit 0 全绿; (d) regression fixture inject '`llmstatetree generate, inspect, export`' 4-cmd listing → doc-audit FAIL 1 drift [count-llmstatetree-subcmd-drift] exit 1 ✓ → revert → exit 0 OK ✓。Concurrent: 无 collision, tool-fix-07 session60 chronological 顺延 session59 (2aa4a77) + session58 (8a27e7d) + session57 (14154e8 + 6c9e7bd + 753f780) + earlier。Pre-existing C2369 kCategoryShortNames 跟本 fix 解耦 — 純 SKILL.md markdown 段 add 3 sub-cmd doc + meta-NOTE append, 0 effect on UCLASS/UENUM/USTRUCT reflection, 无 livecoding/rebuild 必要。**Task 不 mark completed: true** — tool-fix-07 是 ongoing doc-fossil + audit-tool + runtime-bug 大伞 project, 本 session 闭合 'LLMStateTree 3/6 sub-cmd silent-missing' sub-class 但 60+ session 后续肯定还有别的 ability sub-cmd silent-missing (LLMMS 3 sub-cmd / LLMVFX 9 sub-cmd / LLMQuixel 6 sub-cmd / LLMWhitebox 15 sub-cmd / LLMMaterial 5 sub-cmd / LLMDynamicUI 4 sub-cmd 等 6 个 ability 还有 audit-coverage 漏洞没扫), 应让 harness 多 session 接力。Fix scope 1 file +27/-0 净 (SKILL.md +3 段 sub-cmd doc + 1 meta-NOTE blockquote + 1 行 separator)。

---

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->

## §4: 6→8 sub-cmd — `preview` / `nodes` 从“文档承诺但代码不存在”到真实交付

> Original SKILL.md CLI section extended in the 2026-10-25 contract-hardening pass. Content below is the forensic record of that change.

Root cause: `VERSION-NOTES.md` 已对外承诺 1.1.0 交付 `preview` 与 `nodes` 两个子命令，但
`LLMStateTreeCommandHandler::HandleStateTreeCommand` 实际只有 generate / inspect / export / copy /
delete / compile 六个，两个承诺的子命令根本不存在 —— agent 调一下就拿到
`Unknown statetree subcommand`。根因与 tool-fix-07 session60（3→6 sub-cmd silent-missing）同系，
但方向相反：那次是代码有文档没有，这次是文档有代码没有 —— 对外已发布的
Version Notes 承诺属于已交付能力，撤回文档才是正确选择。

Fix: 在 `LLMStateTreeCommandHandler` 实现 `preview`（解析为 JSON 回显，不写资产，复用
`ULLMStateTreeSerializer::DefinitionToJsonString`）与 `nodes`（反射得到的节点类型 + 属性 schema）；
同时两个命令必须同时注册进 `LLMStateTreeEditorModule.cpp` 的 ability JSON `commands` 数组，
否则 LLMEasyShell 的 `ExecuteSingle` 会在 handler 运行前就把它们静默拦下来
（此机制在 `LLMStateTreeEditorModule.cpp:396-399` 的注释里写明）。

Side effects: 命令总数 6 → 8（preview/nodes 交付）；随后同日 `schema` 子命令交付,终态 = **9**,
`doc-audit.py` 的 `count-llmstatetree-subcmd-drift` pattern 锚定 9（否则会把新的正确计数误报为 stale）;
`count-llmstatetree-example-files` 因项目专属内容迁出 LLMStateTree(NpcDialogs 4 枚 → LLMSurvivorShell)
且样例集加厚(FlatFormatAI + DslLab)终态 = **7**(5 AI 行为 + 2 特性夹具)。
