---
name: llm-white-box-skill-changelog
description: Historical forensic meta-NOTEs extracted from SKILL.md. Each entry preserves rootCause + source-of-truth + pattern codification from the original fix session.
metadata:
  type: forensic-archive
  source: .claude/skills/llm-white-box/SKILL.md
  extracted: 2026-07-10
  tool-fix-07-session: 125
---

# SKILL.md Forensic Changelog (extracted 2026-07-10)

> **Why**: llm-white-box/SKILL.md had 1 large forensic HTML comment (~3.8KB, 24% of file): the tool-fix-07 session61 closure (0→15 sub-cmd silent-missing) bundled with session93 follow-up (L141 stale breakdown) + session98 follow-up (cascade-end anchor off-by-15 drift). Mirrors Lite SKILL_CHANGELOG.md (session118) + full llm-easy-shell SKILL_CHANGELOG.md (session119) + sakura-brass SKILL_CHANGELOG.md (session120) + methodology SKILL_CHANGELOG.md (session121) + llm-dynamic-ui SKILL_CHANGELOG.md (session122) + llm-statetree SKILL_CHANGELOG.md (session123) + llm-metasound SKILL_CHANGELOG.md (session124) pattern.
>
<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
>
> **Pointer policy**: Each block below has a stable `## §N` heading (numbered in file order — L168). Future audits can cross-reference by §N.

## §1: `tool-fix-07 session61+93+98 2026-07-09/10` (original SKILL.md L168)

> Original SKILL.md L168 location preserved as HTML comment marker in main file. Content below is verbatim from the original HTML comment (consolidated: session61 main closure + session93 follow-up + session98 follow-up).

<!-- [tool-fix-07 session61 2026-07-09] closure: llm-white-box SKILL.md `## CLI Commands` 段 0→15 sub-cmd silent-missing doc-fossil — runtime `llm-shell -q -j -c help llmwhitebox` commands=[create-box, create-subtract-box, create-cylinder, create-sphere, create-cone, create-stairs, list-brushes, get-brush, delete-brush, move-rotate, build-room, build-wall-segment, apply-default-material, rebuild-bsp-lighting, build-bsp] 15 entries 1:1 锁定, 但本 SKILL.md 历来 0% 文档化 ability sub-cmd — 本 fix 闭合最痛点 class (15/15 silent missing, 100% silent, 跟 session60 LLMStateTree 3/6 partial-coverage 跟 session61 llm-metasound 3/3 zero-coverage 同 family 但 silent-side 比例不同)。Source-of-truth 4 重 lock: (a) runtime help JSON 15 entries; (b) filesystem `LLMWhiteboxCommandHandler.cpp:266-447` `if (Command == TEXT("..."))` 15 entries in `ExecuteWithResult` cascade + `LLMWhiteboxModule.cpp:54/56` 2 AddRaw 注册 OnAllModuleLoadingPhasesComplete = 15 sub-commands dispatcher + 2 ability registration; (c) SKILL.md 内 'Render Pipeline — The Two Non-Obvious Steps' 段提及 `apply-default-material` + `rebuild-bsp-lighting` 但仅作 prose 描述, 缺独立 CLI 段; (d) 新 doc table 15 row 跟 runtime 15 entry 1:1 lock。Fix scope 1 file +25/-0 净 (1 段 CLI Commands + 15 row table + 1 bash workflow + 1 meta-NOTE blockquote)。Pattern codified — `count-llmwhitebox-subcmd-drift` 是新 audit category 跟 session60 `count-llmstatetree-subcmd-drift` + session61 `count-llmms-subcmd-drift` + `count-llmdynamicui-subcmd-drift` 同 'LLM ability forward-fossil defense' family 1:1 平行但本 fix class 是 **largest zero-coverage** (15 silent = 100%)。 [session93 2026-07-10 follow-up] L141 breakdown `6 callsites + 9 additional static functions` 跟 L168 (b) 上方 source-of-truth claim 同 fossil — Module.cpp L54/56 AddRaw 实际只 2 调用 (full + lite 注册),15 sub-commands 全部由 LLMWhiteboxCommandHandler.cpp:266-447 dispatcher cascade 实现, 补 docstring + 移除 stale breakdown, paired sync doc-audit count 82→83 categories 35→36 (新 stale-llmwhitebox-addraw-callcount-drift audit pattern)。 [tool-fix-07 session98 2026-07-10 follow-up] L141 + L168 (b) 内 `LLMWhiteboxCommandHandler.cpp:266-447` cascade-end anchor off-by-15 drift — L447 is `LLMWhiteboxHandlerInternal::GetVector(Args, TEXT("start"), FVector::ZeroVector),` (5th arg of BuildWallSegment call, 位于 build-wall-segment cascade body 内), 真实 cascade-end 在 L462 (build-wall-segment 闭合 `}`), 函数 ExecuteWithResult 闭合于 L465. 修复: L141 + L168 (b) 内 `266-447` → `266-462` (cascade-end). 5-surface paired sync 92p/41c → 93p/42c (新 stale-llmwhitebox-cascade-end-anchor-drift audit pattern). 跟 session89 stale-vfx-factory-line-drift + session93 stale-llmwhitebox-addraw-callcount-drift 同 family 但 polarity 是 single-line-anchor off-by-N drift (前 2 个是 whole-function-line off-by-N). -->

---

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
