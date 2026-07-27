---
name: llmdynamicui-1-1-0-tagged-pre-patch-2026-06-17
description: LLMDynamicUI 1.1.0 tag was created before UE 5.5/5.6 compat patches landed — bumped to 1.1.1 (63c3b28) instead of force-overwriting the old tag
metadata: 
 node_type: memory
 type: project
 originSessionId: 430031d1-8356-4aa6-9aa7-b8861d9e7338
---

# LLMDynamicUI 1.1.0 tagged before compat patches — bumped to 1.1.1

**Date:** 2026-06-17
**Branch:** `release/llm-dynamic-UI`
**Worktree:** `D:\UnrealEngine\CODEO\.lrh\worktrees\llm-dynamic-UI`

## What happened

1. User asked to tag `release/llm-dynamic-UI` as 1.1.0. The `.uplugin`
 `VersionName` was already "1.1.0" so I tagged commit `e8c2f48` and pushed
 `llm-dynamic-UI/1.1.0`.

   [tool-fix-152 2026-06-29] meta-NOTE: `e8c2f48` commit subject 是
   "chore(llmvfx): regenerate NiagaraModuleSchema defaults"(verified
   `git log --oneline -1 e8c2f48`)。该 commit 是 release/llm-dynamic-UI 分支
   latest tip 当时指向的 commit(跟 llmvfx 同步开发的混合历史),并不是
   LLMDynamicUI 专用 commit。tag 是 lightweight tag 指向该 commit hash
   作为 branch tip,所以 `llm-dynamic-UI/1.1.0 → e8c2f48` 在 audit 时
   会看到 llmvfx chore subject — 这是预期行为不是 bug,doc 没 claim 该
   commit 是 LLMDynamicUI 专用。
2. User then asked to re-run the multi-UE Fab build flow to validate before
 publishing. **5.6 failed** — `GetTransientPackageAsObject()` doesn't exist
 pre-5.7. I patched 5.6 (`f642045`).
3. **5.7 broke from that patch** — I replaced
 `GetTransientPackageAsObject()` (5.7-only) with bare `GetTransientPackage()`
 which returns `UPackage*`, but `NewObject<>`'s `Outer` is `UObject*`, causing
 C2446 on the ternary. User said: "你直接改了，有没有可能5.7就过不了了"
 (correctly predicting the regression). Fixed with `(UObject*)GetTransientPackage()`
 cast across 7 sites.
4. User then asked to add UE 5.5 to the test scope. **5.5 failed** with
 `UPackage::GetMetaData()` return type mismatch (5.5 returns `UMetaData*`,
 5.6+ returns `FMetaData&`). Fixed with `ENGINE_MINOR_VERSION` preprocessor
 guards (`3679adf`).
5. By the time everything was green, the 1.1.0 tag pointed to a commit
 *missing* the compat patches.

## Why not `git tag -f` to overwrite

- `llm-dynamic-UI/1.1.0` was already on origin, and `git ls-remote` shows
 it dereferences to `e8c2f48` (the pre-patch commit).
- Force-overwriting would mean: anyone who already fetched 1.1.0 keeps a
 divergent reference; future `git checkout 1.1.0` would silently
 yield different source. Audit trail becomes confused.
- The compat patches are **bug fixes**, not new features. Semver
 clearly says: patch bump (1.1.0 → 1.1.1).

## Resolution

1. `.uplugin` VersionName 1.1.0 → 1.1.1
2. `README.md:132` footer `v1.1.0` → `v1.1.1`
3. `VERSION-NOTES.md`: prepend 1.1.1 — Multi-UE Compatibility section
 (UE 5.5/5.6/5.7 verified via clean `-rocket` build)
4. Commit: `63c3b28 chore(llm-dynamic-ui): bump 1.1.0 → 1.1.1 (multi-UE compat patch release)`
5. Tag: `llm-dynamic-UI/1.1.1 → 63c3b28`
6. Pushed to origin (note: `--follow-tags` did **not** push the new tag —
 the remote on this machine requires explicit `git push origin refs/tags/<name>`)

## Final tag state

```
llm-dynamic-UI/1.0.0 → 85aa699 (historical)
llm-dynamic-UI/1.1.0 → e8c2f48 (released, but pre-compat-patch)
llm-dynamic-UI/1.1.1 → 63c3b28 (current release with 5.5/5.6/5.7 compat)
```

**Why:** Force-overwriting a pushed tag is dirty — it changes the meaning
of a tag that's been seen by others, breaks reproducibility for anyone who
already fetched it, and obscures audit trails.
**How to apply:** When you discover a tagged release has gaps (missing
patches, broken compat, etc.), bump to the next semver patch version rather
than force-rewriting history. The original tag stays as a historical
reference, the new tag carries the corrected source.

Related: [[ue55-upackage-getmetadata-and-gettransientpackage-2026-06-17]] (the
actual API diffs that needed patching), [[multi-ue-fab-build-skill-2026-06-17]]
(the skill that surfaced the 5.6/5.5 build failures).
