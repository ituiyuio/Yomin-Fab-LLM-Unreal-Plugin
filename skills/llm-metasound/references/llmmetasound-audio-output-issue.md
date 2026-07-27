---
name: llmmetasound-audio-output-issue
description: LLMMetaSound AudioOutInputs fix COMPLETED & VERIFIED — duplicate SetFormat was invalidating handles
type: project
originSessionId: 9cffa43a-f174-4353-9642-9565136688d9
---
# LLMMetaSound Audio Output Connection Issue — FIXED & TESTED

## Problem
`AutoConnectAudioSources` not connecting audio nodes to MetaSoundSource audio output.

## Root Cause
In `GenerateInternal`, there was a **duplicate `SetFormat` call** inside the `Apply output format if Source` block (removed by commit `45986c5` on 2026-04-29 — see [Current Correct Usage](#current-correct-usage--tool-fix-155-source-of-truth) for current line refs):
- `CreateBuilder` calls `SetFormat` when `AudioOutInputs` is empty — current source: `LLMMetaSoundGenerator.cpp:225` (call statement) inside the `if (SourceBuilder && AudioOutInputs.IsEmpty())` block spanning L222-L254 (post-`45986c5`)
- The duplicate `SetFormat` call in `GenerateInternal` (no longer in source — removed by `45986c5`) had been resetting document state and **invalidating the handles** that were set up in `CreateBuilder`
- `AudioOutInputs` was populated by `CreateBuilder`, but the second `SetFormat` call reset the document, so the handles were stale

> **Note**: Original doc cited stale line ranges `129-141` / `229-232` / `135` matching the pre-`45986c5` layout (last touched `f2ebd52`). All line refs in this doc were updated by `tool-fix-155` (2026-06-29) to current source-of-truth. See meta-NOTE at end of file.

## Solution
Removed the duplicate `SetFormat` call in `GenerateInternal` (commit `45986c5` — `fix(LLMMetaSound): 修复编辑器中节点不可见问题`, 2026-04-29).

The fix ensures `SetFormat` is only called once — inside `CreateBuilder` when needed.

## Test Result (2026-04-28)
```
llmms generate /Game/Audio/TestSineNew --from TestOscillator.llmmetasound
→ Generated UMetaSoundSource: /Game/Audio/TestSineNew
Warnings:
 [WARN] AutoConnect: Connected Audio to audio output
```

Export shows edge: `{"FromNodeID": 3, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 0}` (Sine → Audio output)

## All Fixes Applied
- ✅ Removed duplicate `SetFormat` call in `GenerateInternal` (commit `45986c5` — pre-fix range was the `Apply output format if Source` block, ~12 lines; post-fix the only `SetFormat` call lives in `CreateBuilder` at L225)
- ✅ `bIsOneShot=false` default in `FLLMMetaSoundGeneratorConfig`
- ✅ `RF_Standalone` flag set in `BuildAndSaveAsset` after rename to target package
- ✅ Transient object cleanup (renamed to `ZZZ_GARBAGE_` prefix) to avoid class name conflicts
- ✅ Asset verified via `cat /Game/Audio/TestSineNew` - Frequency=440.000000, edge present

## Files Changed
- `LLMMetaSoundGenerator.cpp`:
 - Removed duplicate `SetFormat` call in `GenerateInternal` (commit `45986c5` — pre-fix range was the `Apply output format if Source` block, ~12 lines; post-fix the only `SetFormat` call lives in `CreateBuilder` at L225)
 - Added RF_Standalone flag after rename to target package
 - Added transient object cleanup before `BuildNewMetaSound`
- `LLLMetaSoundGenerator.h`:
 - Changed `bIsOneShot = false` default (was `true`)

## Status: COMPLETE ✅

---

## Current Correct Usage — tool-fix-155 source-of-truth

Verified `2026-06-29` against `Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp` (1612 lines, last touched by `41a50e2` 2026-06-28 for UE 5.8 compatibility upgrade):

| Claim in this doc (original) | Current source-of-truth | Drift |
|---|---|---|
| `GenerateInternal` had duplicate `SetFormat` at **lines 129-141** | Function starts at L104; the `Apply output format if Source` block (containing `SourceBuilder->SetFormat(...)` call) was removed by commit `45986c5` (2026-04-29) — block no longer exists in source | `45986c5` refactor: `GenerateInternal` lost the SetFormat call entirely, `CreateBuilder` gained it (now L225 inside `if (SourceBuilder && AudioOutInputs.IsEmpty())` L222-L254) |
| `CreateBuilder` already calls `SetFormat` at **lines 229-232** | `LLMMetaSoundGenerator.cpp:225` is the call statement; surrounding if-block is L222-L254 (calls `SetFormat` → checks `EMetaSoundBuilderResult` → calls `FindOutputAudioFormatInfo` → `FindInterfaceOutputNodes` → `FindNodeInputs`) | doc off by 4 lines vs current SetFormat call site; doc range `229-232` actually covers `FindInterfaceOutputNodes` call (L232) + `FindResult` check (L229-230), not SetFormat |
| `GenerateInternal` called `SetFormat` again at **line 135** | L135 in current source is `// Build nodes` comment; the next line L136 is `TMap<int32, FGuid> JsonIdToNodeGuid;` declaration | doc fossil — L135 was the OLD pre-`45986c5` line for `EMetaSoundBuilderResult FormatResult;` (inside the now-removed `Apply output format if Source` block) |

### Source-of-truth grep verification (4 重 lock)

```bash
# (a) GenerateInternal no longer calls SetFormat — verified
grep -n "SetFormat" Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp
# 225:    SourceBuilder->SetFormat(Config.OutputFormat, SetFormatResult);  ← only hit, inside CreateBuilder

# (b) CreateBuilder signature includes AudioOutInputs + OnPlayOutput out-params — verified
grep -n "FLLMMetaSoundGenerateResult ULLMMetaSoundGenerator::CreateBuilder" \
  Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp
# 181:FLLMMetaSoundGenerateResult ULLMMetaSoundGenerator::CreateBuilder(

# (c) AudioOutInputs out-param wired through CreateBuilder → GenerateInternal — verified
grep -n "TArray<FMetaSoundBuilderNodeInputHandle> AudioOutInputs" \
  Plugins/LLMMetaSound/Source/LLMMetaSoundEditor/Private/LLMMetaSoundGenerator.cpp
# 122:    TArray<FMetaSoundBuilderNodeInputHandle> AudioOutInputs;  (in GenerateInternal)
# 205:        TArray<FMetaSoundBuilderNodeInputHandle> AudioOutInputs;  (in CreateBuilder)
# 256:        OutAudioOutInputs = MoveTemp(AudioOutInputs);  (in CreateBuilder)
```

### [tool-fix-155 2026-06-29] meta-NOTE

**RootCause family**: `45986c5` 2026-04-29 refactor of `LLMMetaSoundGenerator.cpp` reshuffled `GenerateInternal` + `CreateBuilder` boundaries (changed `CreateBuilder` signature from `(AssetType, Config, OutBuilder, OutBuilderResult)` to `(AssetType, Config, OutBuilder, OutBuilderResult, OutAudioOutInputs, OutOnPlayOutput)`; moved `SetFormat` from `GenerateInternal` into `CreateBuilder`; added `AutoConnectTriggers` + `AutoConnectAudioSources` calls). Doc last touched at `f2ebd52` (a memory cleanup commit that did NOT adjust line refs to match `45986c5`). Subsequent commits `8c700f3` (LLM-friendly DSL conventions) + `41a50e2` (UE 5.8 compat) further refactored the file but never re-verified doc line refs.

**Drift signature**: 5 fossil line refs (`129-141` ×4 + `229-232` ×1 + `135` ×1) all pointing to the pre-`45986c5` layout; current source has only 1 `SetFormat` call (L225) inside `CreateBuilder`. The behavioral narrative is still correct (the fix is real and the duplicate was indeed the root cause); only the line refs are stale.

**Pattern (跟 tool-fix-130~154 平行)**: '`memory/experience doc line refs 跨多 surface fossil 累积, commit refactor 后未回扫 doc' 跟 tool-fix-141 partial-fix 漏扫 cpp + tool-fix-144 'comment vs constexpr 2x drift' + tool-fix-146 'C++ comment 4 重 lock' + tool-fix-148 'commit 09421a9 refactor + tool-fix-136/138 partial-fix 漏扫 references/*.md' + tool-fix-150 'cross-skill folder leak' + tool-fix-151 'llm-material references line drift cluster' + tool-fix-152 'llm-dynamic-ui doc-fossil cluster' + tool-fix-154 'llmvfx-schemacolor-typedef-equality-bug line drift closure' 同期 pattern 1:1 平行 'silent inconsistency hot zone' 反复模式, audit 必 'doc claim line N → cpp actual line M 1:1 verify + commit refactor 期间 sync scan doc'.

**Fix pattern (preservation > rewrite)**: 5 line refs 替换为 commit ref + post-refactor current line; 加 [Current Correct Usage] section 包含 3 verified facts + 3 grep verify commands + meta-NOTE chain pattern 跟 tool-fix-118/130/138/141~154 1:1 平行。

**Tool-fix-N collision pre-check**: 编号 155 顺延 tool-fix-154 (e4ea9b1 ship + 001bd24 evolutionHistory) 编号 155 无 collision, 必先 `git log --all --oneline | grep -iE toolfix-155|tool-fix-155` = 0 hits verified 45 次踩 (跟 tool-fix-138~154 collision pre-check pattern 1:1 平行)。
