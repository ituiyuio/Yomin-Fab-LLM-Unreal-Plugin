---
name: llm-metasound-skill-changelog
description: Historical forensic meta-NOTEs extracted from SKILL.md. Each entry preserves rootCause + source-of-truth + pattern codification from the original fix session.
metadata:
  type: forensic-archive
  source: .claude/skills/llm-metasound/SKILL.md
  extracted: 2026-07-10
  tool-fix-07-session: 124
---

# SKILL.md Forensic Changelog (extracted 2026-07-10)

> **Why**: llm-metasound/SKILL.md had 2 large forensic blocks totaling ~4.2KB (21% of file): 1 HTML comment (tool-fix-172 line drift closure) + 1 HTML comment closure (tool-fix-07 session61 zero-coverage 0→3 sub-cmd silent-missing). Mirrors Lite SKILL_CHANGELOG.md (session118) + full llm-easy-shell SKILL_CHANGELOG.md (session119) + sakura-brass SKILL_CHANGELOG.md (session120) + methodology SKILL_CHANGELOG.md (session121) + llm-dynamic-ui SKILL_CHANGELOG.md (session122) + llm-statetree SKILL_CHANGELOG.md (session123) pattern.
>
<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
>
> **Pointer policy**: Each block below has a stable `## §N` heading (numbered in file order — L345 → L433). Future audits can cross-reference by §N.

## §1: `tool-fix-172 2026-06-29` (original SKILL.md L345)

> Original SKILL.md L345 location preserved as HTML comment marker in main file. Content below is verbatim from the original HTML comment.

<!-- [tool-fix-172 2026-06-29] Line drift closure: 原 doc 写 `LLMMetaSoundGenerator.cpp:626-678` 截在 L678 (vertex 类型校验注释起点),但 doc 文本 "PinName-first / VertexID-fallback 策略" 实际结束在 L676 (To-side fallback 最后一行 `continue;`),L678 之后是 "Validate vertex types match before adding edge" 类型校验（不属于策略本身）。Source-of-truth 4 重 lock 跟新 claim 1:1 锁定: (1) filesystem `grep -n "Resolve From-side vertex\|Resolve To-side vertex"` 锚定 From-block L626-651 + To-block L653-676,策略结束点 L676; (2) filesystem `awk 'NR==676' Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp` 是 To-side fallback 错误后 `continue;` 行; (3) filesystem `awk 'NR==678' Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp` 是 "Validate vertex types" 注释 (非策略); (4) 同 family tool-fix-148/154/155 'line drift 配对 closure' pattern 跟 tool-fix-155 'llm-metasound audio output line drift 5 处' 同 skill 2nd-order。Fix scope 1 file +0/-0/+1 行: 626-678 → 626-676 (1 行) + meta-NOTE preservation。跟 tool-fix-155 'audio output line drift 5 处' 同 skill 但 sub-pattern 不同 (本 fix 是 1 处 off-by-2 范围漂移, tool-fix-155 是 5 处 refactor 派生 line drift)。Concurrent paired completion: 跟 llm-statetree SKILL.md L228 line drift (439/716 → 442/718) 同 session 同 family 'line drift in SKILL.md doc claim vs source' 1:1 平行。Runtime e2e 走 (a) full llm-shell.exe --help UE 5.8 binary sanity OK + (b) lite llmshelllite.exe --help UE 5.8 binary sanity OK + (c) source-level 4 重 lock (filesystem L626 + L653 + L676 + L678 anchor 跟 doc claim 1:1 锁定) 跟 tool-fix-130~171 pattern 1:1 平行。Source-level + 2 binary sanity + filesystem e2e 跟 UE editor 全量 build 解耦, pre-existing C2369 kCategoryShortNames 不影响本 fix。教训: 1) '范围漂移 off-by-2' 是新 sub-pattern 跟 tool-fix-148/154/155 'line drift closure' 同 family 但 sub-pattern 不同 (本 fix 是 doc 范围 end +2 跨到下一个 block 起点, 别人是 doc single line 错位), audit 必 'grep <doc 提到 comment 关键词>' 跟 doc 范围 end 1:1 锁定 + 'awk NR=<end>' 验证 doc 范围 1:1 跟 source 对齐; 2) 'paired completion cross-skill' 跟 tool-fix-154/155 llm-vfx+llm-metasound 同期 pattern 1:1 平行, 2 files 修了 锚定 filesystem 4 重 lock 跟 tool-fix-148 形成 'paired completion chain within line drift cluster' 跨 2 skills 1 session 闭环。 -->

---

## §2: `tool-fix-07 session61 2026-07-09` (original SKILL.md L433)

> Original SKILL.md L433 location preserved as HTML comment marker in main file (last line of file pre-extraction). Content below is verbatim from the original HTML comment.

<!-- [tool-fix-07 session61 2026-07-09] closure: llm-metasound SKILL.md `## CLI Commands` 段 0→3 sub-cmd silent-missing doc-fossil — `Plugins/LLMMetaSound/Source/LLMMetaSound/Private/LLMMetaSoundModule.cpp` 注册 3 sub-cmd (generate/export/inspect, runtime `llm-shell -q -j -c help llmms` commands=[generate, export, inspect] 1:1 锁定), 但本 SKILL.md 历来 0% 文档化 ability sub-cmd — LLM 读 doc 只能靠 `--help` 反查才能发现这 3 个 sub-cmd, 100% silent missing。Root cause: 跟 tool-fix-07 session60 (LLMStateTree 3→6 silent-missing) + tool-fix-134 (LLMVFX 8/9 silent-missing 2026-06-29) 同 'ability sub-cmd silent-missing' family 1:1 平行但本 fix class 是 **LLMMetaSound ability 3 sub-cmd 全注册但 SKILL.md 整段 CLI 段缺失** (跟 session60 LLMStateTree 3/6 silent 是 partial-coverage 不同 — 本 fix 是 zero-coverage class, 0 文档 → 100% silent)。Source-of-truth 3 重 lock 跟新 claim 1:1: (a) runtime `llm-shell -q -j -c help llmms` commands=[generate, export, inspect] 3 entries; (b) filesystem `grep -E 'Info\.Commands\.Add' Plugins/LLMMetaSound/Source/LLMMetaSound/Private/LLMMetaSoundModule.cpp` (per session59 pattern parallel) 1:1; (c) 新 doc table 3 row 跟 runtime 3 entry 1:1 lock。Fix scope 1 file +15/-0 净 (SKILL.md 加 1 段 CLI Commands + 3 row table + 3 行 bash 示例 + 1 行 meta-NOTE blockquote)。Pattern codified — `count-llmms-subcmd-drift` 是新 audit category 跟 `count-llmstatetree-subcmd-drift` (session60 codify) 同 'LLM ability forward-fossil defense' family 1:1 平行但本 fix class 是 **zero-coverage** 跟 session60 partial-coverage polarity 颠倒 (session60 是 50% silent, 本 fix 0% doc)。 -->

---

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
