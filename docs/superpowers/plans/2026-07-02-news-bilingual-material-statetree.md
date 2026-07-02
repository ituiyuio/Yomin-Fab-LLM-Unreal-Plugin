# News Bilingual — Material & StateTree v1.1.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Translate the two Chinese-only `/news/` entries for `LLMMaterial v1.1.2` and `LLMStateTree v1.1.2` into English so the English locale sidebar carries 8 entries (currently 6).

**Architecture:** Two new `.md` files under `docs/en/news/`. No code, no config, no theme changes — VitePress's `loadNewsEntries('en/news')` in `docs/.vitepress/config.ts` already auto-discovers entries at build time. `slug` matches the Chinese version byte-for-byte so locale-switch URL parity holds.

**Tech Stack:** VitePress 1.6 (build-time directory scan), Markdown (no Vue / TypeScript touched in this plan).

---

## File Structure

```
docs/
└── en/
    └── news/
        ├── llm-material-1.1.2.md         # CREATE  — translate from docs/news/llm-material-1.1.2.md
        └── llm-statetree-1.1.2.md        # CREATE  — translate from docs/news/llm-statetree-1.1.2.md
```

**Why only two files:** the rest of the i18n wiring (`config.ts:43-65 loadNewsEntries`, `config.ts:276 newsSidebar`) already handles discovery, sorting, and locale routing. Zero config edits required.

**No tests in this plan:** VitePress news entries are content, not code — there is no unit-test surface. Verification is structural (file existence + front-matter shape + build success) and is consolidated into Task 3.

## Global Constraints

- Front-matter **must** contain all 7 fields: `layout`, `title`, `date`, `tag`, `summary`, `emoji`, `slug`.
- `slug` **must** equal the Chinese version byte-for-byte (`llm-material-1.1.2` and `llm-statetree-1.1.2`).
- `date` **must** equal `2026-07-02` (matches Chinese version).
- `tag` must be `Fix` for Material, `Plugin` for StateTree (matches Chinese version).
- `emoji` must be 🐛 for Material, 🌲 for StateTree (matches Chinese version).
- All code identifiers, version strings, file names, command lines, and tooling tokens must be preserved verbatim — translate prose and section-title text only.
- No edits to `docs/.vitepress/config.ts`, `docs/news/README.md`, or any existing English news entry.
- All commits on `main` branch; commit message format: `docs(i18n): …`.

---

## Task 1: Translate LLMMaterial v1.1.2 news entry

**Files:**
- Create: `docs/en/news/llm-material-1.1.2.md`

- [ ] **Step 1: Verify Chinese source still exists and is unchanged**

Run (from repo root):
```bash
test -f docs/news/llm-material-1.1.2.md && echo OK || echo MISSING
```
Expected: `OK`. If `MISSING`, abort — the translation source has been removed or renamed.

- [ ] **Step 2: Create `docs/en/news/llm-material-1.1.2.md` with full translated content**

Write the following file verbatim:

```markdown
---
layout: doc
title: LLMMaterial v1.1.2 — Multi-UE 5.5/5.6/5.7/5.8 Build Regression Fix
date: 2026-07-02
tag: Fix
summary: |
  LLMMaterial v1.1.2 fixes a UE 5.8 build regression plus the Documentation.md / README.md "UE 5.7+" fossil. MaterialBuilder.cpp L432-466 accessed 21 deprecated `UMaterial::bUsedWithXxx` members that UE 5.8 flags as C4996; we wrap the access with `PRAGMA_DISABLE_DEPRECATION_WARNINGS` instead of switching to `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)` (private on UE 5.5/5.6/5.7, only public on UE 5.8). Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.
emoji: 🐛
slug: llm-material-1.1.2
---

# LLMMaterial v1.1.2

> Pure compat patch. No new features, no API changes. Engine matrix 5.5 / 5.6 / 5.7 / 5.8 (Win64) unchanged.

## 🐛 Bug Fixes

- **`MaterialBuilder.cpp` UE 5.8 C4996 deprecation warnings** — L432 (`bUsedWithNanite`) + L444-466 (21 direct `bUsedWithXxx` member accesses) are all flagged by UE 5.8 as `warning C4996: ... Please update your code to the new API before upgrading to the next release`. The ideal replacement `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)` is `private` on UE 5.5/5.6/5.7 and only became public on UE 5.8, so it cannot be used directly. We wrap the 22 lines of direct access with `PRAGMA_DISABLE_DEPRECATION_WARNINGS` / `PRAGMA_ENABLE_DEPRECATION_WARNINGS`, mirroring the `[tool-fix-274]` `[tool-fix-260]` series handled in the same cycle 1:1.
- **`Documentation.md` / `README.md` claim drift** — both files claimed "UE 5.7+", but 1.1.1 already shipped multi-UE 5.5/5.6/5.7/5.8. Aligned to "5.5 / 5.6 / 5.7 / 5.8".
- **`.uplugin` / README / Documentation footnote `v1.1.1 → v1.1.2` synchronized**.

## ⚡ Improvements

- **`MaterialBuilder.cpp` comment explaining the UE 5.5/5.6/5.7 suppression rationale** — added a 4-line comment block above the PRAGMA block documenting the `SetUsageByFlag` private → public version boundary, so future contributors don't fall into the same trap.

## ✅ Verified

- Clean `RunUAT.bat BuildPlugin ... -rocket` passes on **UE 5.5 / 5.6 / 5.7 / 5.8** (zero errors, zero C4996 deprecation warnings, zero C4701 uninitialized warnings).
- 4 zip SHA-256 written to `.publishready/zips/LLMMaterial/manifest.json`, ready to upload to Google Drive / Dropbox for the Fab Publisher Portal.

## 🔧 Compatibility

- Breaking change: none. Source and binary contracts identical to 1.1.1. `.llmmat` files written by 1.0 / 1.1.0 / 1.1.1 remain valid input.
- Engine matrix: 5.5 / 5.6 / 5.7 / 5.8 (Win64) — unchanged.

---

**Engine support**: UE 5.5 / 5.6 / 5.7 / 5.8 — `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.

**File format**: `.llmmat` (JSON), `.llmschema` (Schema), Material UAsset.
```

- [ ] **Step 3: Run structural checks on the new file**

Run (from repo root):
```bash
test -f docs/en/news/llm-material-1.1.2.md && echo FILE_OK
grep -q '^layout: doc$' docs/en/news/llm-material-1.1.2.md && echo LAYOUT_OK
grep -q '^title: LLMMaterial v1.1.2' docs/en/news/llm-material-1.1.2.md && echo TITLE_OK
grep -q '^date: 2026-07-02$' docs/en/news/llm-material-1.1.2.md && echo DATE_OK
grep -q '^tag: Fix$' docs/en/news/llm-material-1.1.2.md && echo TAG_OK
grep -q 'emoji: 🐛' docs/en/news/llm-material-1.1.2.md && echo EMOJI_OK
grep -q '^slug: llm-material-1.1.2$' docs/en/news/llm-material-1.1.2.md && echo SLUG_OK
diff <(grep '^slug:' docs/news/llm-material-1.1.2.md) \
     <(grep '^slug:' docs/en/news/llm-material-1.1.2.md) && echo SLUG_PARITY_OK
grep -q 'PRAGMA_DISABLE_DEPRECATION_WARNINGS' docs/en/news/llm-material-1.1.2.md && echo CODE_OK
grep -q 'UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)' docs/en/news/llm-material-1.1.2.md && echo CODE_OK
grep -q 'RunUAT.bat BuildPlugin ... -rocket' docs/en/news/llm-material-1.1.2.md && echo CODE_OK
grep -q 'UE 5.5 / 5.6 / 5.7 / 5.8' docs/en/news/llm-material-1.1.2.md && echo VERSION_OK
grep -q '\.llmmat' docs/en/news/llm-material-1.1.2.md && echo EXT_OK
grep -q 'tool-fix-274' docs/en/news/llm-material-1.1.2.md && echo TOOL_OK
grep -q 'tool-fix-260' docs/en/news/llm-material-1.1.2.md && echo TOOL_OK
```
Expected: every `*_OK` line printed, no errors. If any check fails, fix the file and re-run.

- [ ] **Step 4: Stage but do not commit yet**

Run:
```bash
git add docs/en/news/llm-material-1.1.2.md
git status --short
```
Expected: `A  docs/en/news/llm-material-1.1.2.md` in the output. (Single final commit at end of Task 3 per spec §5.)

---

## Task 2: Translate LLMStateTree v1.1.2 news entry

**Files:**
- Create: `docs/en/news/llm-statetree-1.1.2.md`

- [ ] **Step 1: Verify Chinese source still exists and is unchanged**

Run (from repo root):
```bash
test -f docs/news/llm-statetree-1.1.2.md && echo OK || echo MISSING
```
Expected: `OK`. If `MISSING`, abort.

- [ ] **Step 2: Create `docs/en/news/llm-statetree-1.1.2.md` with full translated content**

Write the following file verbatim:

```markdown
---
layout: doc
title: LLMStateTree v1.1.2 — UE 5.5/5.6/5.7/5.8 C4996 Fix
date: 2026-07-02
tag: Plugin
summary: |
  LLMStateTree v1.1.2 patch release. Fixes two C4996 deprecation warnings on UE 5.8 build (Fab marketplace scanner treats C4996 as an error), routed through a multi-UE compat shim bridging old and new APIs. Also corrects the "UE 5.7+" doc-fossil in README / Documentation.md / VERSION-NOTES.md.
emoji: 🌲
slug: llm-statetree-1.1.2
---

# LLMStateTree v1.1.2

> Patch bump. Zero user-facing API changes — only fixes UE 5.8 compile warnings + doc fossil.

## 🐛 Bug Fixes

- **2 × C4996 deprecation warnings on UE 5.8** —
  `UE::StateTree::Delegates::OnRequestCompile` is marked deprecated on UE 5.8,
  triggering a C4996 warning that Fab marketplace scanner treats as an error.
  The `statetree compile` command now goes through `LLMStateTreeCompat::RecompileStateTree`:
  - UE 5.5-5.7: uses the old delegate (non-deprecated)
  - UE 5.8+: uses `UStateTreeEditingSubsystem::CompileStateTree` (canonical API)
- **doc-fossil "UE 5.7+"** corrected to "UE 5.5+ (5.5/5.6/5.7/5.8 multi-UE build)",
  touching `README.md` / `Documentation.md` / `VERSION-NOTES.md`

## ⚡ Improvements

- `LLMStateTreeCompatShim.h` adds a `LLMSTATETREE_UE_5_8_PLUS` compile-time detection macro
  and a `RecompileStateTree(UStateTree*)` bridge function; call sites no longer
  scatter `#ifdef` blocks.

## 💥 Breaking Changes

- None

## 🔧 Internal Refactors

- Multi-UE compat shim gains a 4th bridge (compile API), matching the style of the
  existing 3 bridges (`MakeBinding` / `AddBindingToEditor` / `GetRootParametersBag` /
  `AddPropertyToBag`).

---

**Engine support**: UE 5.5 (tested), UE 5.6 (tested), UE 5.7 (tested), UE 5.8 (tested)
— `.uplugin` `EngineVersion: "5.8.0"`, per-UE independent zip + Project Version.

**File format**: `.llmstate` (JSON), `.llmstateschema` (Schema), `UStateTree` (UAsset).

**Source**: 4 files changed — `LLMStateTreeCompatShim.h` (+50/-0 net),
`LLMStateTreeCommandHandler.cpp` (+12/-6 net),
`Documentation.md` (+3/-3 net), `README.md` (+1/-1 net),
`VERSION-NOTES.md` (+1/-1 net).
```

- [ ] **Step 3: Run structural checks on the new file**

Run (from repo root):
```bash
test -f docs/en/news/llm-statetree-1.1.2.md && echo FILE_OK
grep -q '^layout: doc$' docs/en/news/llm-statetree-1.1.2.md && echo LAYOUT_OK
grep -q '^title: LLMStateTree v1.1.2' docs/en/news/llm-statetree-1.1.2.md && echo TITLE_OK
grep -q '^date: 2026-07-02$' docs/en/news/llm-statetree-1.1.2.md && echo DATE_OK
grep -q '^tag: Plugin$' docs/en/news/llm-statetree-1.1.2.md && echo TAG_OK
grep -q 'emoji: 🌲' docs/en/news/llm-statetree-1.1.2.md && echo EMOJI_OK
grep -q '^slug: llm-statetree-1.1.2$' docs/en/news/llm-statetree-1.1.2.md && echo SLUG_OK
diff <(grep '^slug:' docs/news/llm-statetree-1.1.2.md) \
     <(grep '^slug:' docs/en/news/llm-statetree-1.1.2.md) && echo SLUG_PARITY_OK
grep -q 'LLMStateTreeCompat::RecompileStateTree' docs/en/news/llm-statetree-1.1.2.md && echo CODE_OK
grep -q 'UStateTreeEditingSubsystem::CompileStateTree' docs/en/news/llm-statetree-1.1.2.md && echo CODE_OK
grep -q 'LLMStateTreeCompatShim.h' docs/en/news/llm-statetree-1.1.2.md && echo CODE_OK
grep -q 'LLMSTATETREE_UE_5_8_PLUS' docs/en/news/llm-statetree-1.1.2.md && echo CODE_OK
grep -q 'UE 5.5 / 5.6 / 5.7 / 5.8' docs/en/news/llm-statetree-1.1.2.md && echo VERSION_OK
grep -q '\.llmstate' docs/en/news/llm-statetree-1.1.2.md && echo EXT_OK
```
Expected: every `*_OK` line printed, no errors.

- [ ] **Step 4: Stage but do not commit yet**

Run:
```bash
git add docs/en/news/llm-statetree-1.1.2.md
git status --short
```
Expected: both new files staged:
```
A  docs/en/news/llm-material-1.1.2.md
A  docs/en/news/llm-statetree-1.1.2.md
```

---

## Task 3: Build-verify, commit, and finalize

**Files:** no new files; this task verifies and commits.

- [ ] **Step 1: Run VitePress production build to confirm the new entries compile**

Run (from repo root):
```bash
cd docs && npm run docs:build 2>&1 | tail -30
```
Expected: build completes without errors. The build output should reference the new entries in the prerendered route list (e.g. `/en/news/llm-material-1.1.2/` and `/en/news/llm-statetree-1.1.2/`). If the build fails, abort and investigate — most common cause is malformed front-matter.

- [ ] **Step 2: Run VitePress dev server briefly and confirm sidebar has 8 entries**

Run:
```bash
cd docs && timeout 20 npm run docs:dev &
DEV_PID=$!
sleep 12
curl -s http://localhost:5173/en/news/ | grep -oE 'news/[a-z0-9.-]+/' | sort -u | wc -l
kill $DEV_PID 2>/dev/null || true
wait 2>/dev/null
```
Expected output of `wc -l`: `8` (was 6 before, +2 from this plan).

If `wc -l` returns something other than 8:
- 7: one entry didn't get picked up — check front-matter (likely missing `slug` or `date`).
- 9 or more: an extra entry slipped in — check no test/debug file is in `docs/en/news/`.
- 6: build cache — delete `docs/.vitepress/cache/` and `docs/.vitepress/dist/` and retry.

- [ ] **Step 3: Commit both files in a single commit**

Run (from repo root):
```bash
git -c user.email=yiming.wang@local -c user.name="Yiming Wang" commit -m "docs(i18n): translate material & statetree v1.1.2 news to en

- Add docs/en/news/llm-material-1.1.2.md (translated from docs/news/llm-material-1.1.2.md)
- Add docs/en/news/llm-statetree-1.1.2.md (translated from docs/news/llm-statetree-1.1.2.md)

VitePress config auto-discovers the new entries; no config.ts changes.
Slug matches the zh version so locale-switch URL parity holds."
```
Expected: single commit created on `main` with 2 new files. Confirm with:
```bash
git log --oneline -3
git show --stat HEAD | head -20
```

- [ ] **Step 4: Push only if user explicitly requests**

Per `CLAUDE.md`, do not push without explicit user instruction. Stop here and report results to the user.

---

## Self-Review

**1. Spec coverage:**

| Spec section | Covered by |
|--------------|------------|
| §1 File layout (2 new files) | Task 1, Task 2 |
| §2 Front-matter 7 fields | Task 1 Step 3, Task 2 Step 3 (structural checks) |
| §3 Translation rules (preserve code/versions, translate prose) | Task 1 Step 2 + Step 3 (CODE_OK/VERSION_OK/EXT_OK grep), Task 2 Step 2 + Step 3 |
| §4 Verification (file existence, front-matter, sidebar, build) | Task 1 Step 3, Task 2 Step 3, Task 3 Steps 1-2 |
| §5 Single commit with specific message | Task 3 Step 3 (exact commit message reproduced) |
| Out of scope: no config.ts change | Confirmed — no task touches config.ts |
| Out of scope: no other edits | Confirmed — only two files created |

**2. Placeholder scan:** no `TBD`, `TODO`, "fill in", "add appropriate error handling", or "similar to Task N". All code blocks contain complete content.

**3. Type / name consistency:**
- `slug` values `llm-material-1.1.2` and `llm-statetree-1.1.2` match across Tasks 1, 2, 3.
- `date: 2026-07-02` consistent.
- `tag` values `Fix` (Material) / `Plugin` (StateTree) match spec §2 table.
- `emoji` values 🐛 (Material) / 🌲 (StateTree) match spec §2 table.
- File paths `docs/en/news/llm-material-1.1.2.md` and `docs/en/news/llm-statetree-1.1.2.md` consistent across all three tasks.