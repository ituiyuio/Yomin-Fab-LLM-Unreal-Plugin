# News Bilingual — Material & StateTree v1.1.2 — Design Spec

**Date:** 2026-07-02
**Status:** Approved (pending implementation)
**Author:** Brainstorming session with user

## Goal

Bring the two most recent plugin release notes — `LLMMaterial v1.1.2` and
`LLMStateTree v1.1.2` — into parity with the rest of `/news/`, so the
English locale of the docs site surfaces them too.

Both entries already ship in Chinese under `docs/news/` (dated 2026-07-02)
but have **no English counterpart** under `docs/en/news/`. This was
uncovered by `diff`-ing the two news directories:

```
$ diff <(ls docs/news/    | grep -vE '^(README|index)\.md$' | sort) \
       <(ls docs/en/news/ | grep -vE '^(README|index)\.md$' | sort)
< llm-material-1.1.2.md
< llm-statetree-1.1.2.md
```

The English `/news/` sidebar therefore lists 6 entries while the Chinese
one lists 8.

## Scope (in / out)

**In scope**

- Translate `docs/news/llm-material-1.1.2.md` → `docs/en/news/llm-material-1.1.2.md`.
- Translate `docs/news/llm-statetree-1.1.2.md` → `docs/en/news/llm-statetree-1.1.2.md`.
- Verify the new entries appear in the English sidebar via local VitePress
  dev / build (`cd docs && npm run docs:dev`).
- One commit, message: `docs(i18n): translate material & statetree v1.1.2 news to en`.

**Out of scope (YAGNI)**

- Any change to `docs/.vitepress/config.ts` — `loadNewsEntries('en/news')`
  auto-discovers new files (see §1).
- Any change to the existing 6 English news entries.
- Any change to `docs/news/README.md` (maintainer guide).
- Bilingual side-by-side / tab-switch UI — would require touching the
  VitePress i18n contract used by the rest of the docs site.
- New English translations for the (older) Chinese-only entries — none
  exist beyond Material/StateTree v1.1.2; older entries are already
  bilingual.

## Decisions captured during brainstorming

| # | Question | Decision |
|---|----------|----------|
| 1 | Scope of "做双语" | **News dir, specific entries** — the two Chinese-only files |
| 2 | Which entries | **Both** — Material **and** StateTree v1.1.2 |
| 3 | Translation source | **A** — translate the existing Chinese entries verbatim, do not rewrite from git log |
| 4 | Commit granularity | **A1** — single commit covering both (same release wave, same theme) |
| 5 | Local verification | **B** — `npm run docs:dev` and/or `npm run docs:build` to confirm sidebar picks them up |
| 6 | Front-matter / style template | **C1** — mirror `docs/en/news/llm-dynamic-ui-1.1.2.md` and `metasound-1.1.1.md` exactly |

---

## §1 — File Layout & VitePress integration

Two new files. Nothing else moves.

```
docs/en/news/
├── llm-material-1.1.2.md        ← NEW (translate from docs/news/llm-material-1.1.2.md)
└── llm-statetree-1.1.2.md       ← NEW (translate from docs/news/llm-statetree-1.1.2.md)
```

**Why `config.ts` needs zero edits** — `docs/.vitepress/config.ts:43-65`
defines:

```ts
function loadNewsEntries(subdir: 'news' | 'en/news'): NewsEntryMeta[] {
  const dir = join(__dirname, '..', subdir)
  let files = readdirSync(dir).filter(
    (f) => f.endsWith('.md') && f !== 'index.md' && f !== 'README.md'
  )
  // …parse front-matter, sort by date desc…
}
const enNews = loadNewsEntries('en/news')
```

Adding the two `.md` files is enough for `enNews` to grow from 6 → 8
entries, and `newsSidebar('/en/news/', enNews)` (config.ts:276) wires
them into the English locale sidebar on next build. No code change, no
restart, no manual sidebar entry.

**Slug parity** — `slug` front-matter is identical between the zh and
en versions, so the locale-switch button maps:
- `/news/llm-material-1.1.2/`  ↔  `/en/news/llm-material-1.1.2/`
- `/news/llm-statetree-1.1.2/` ↔  `/en/news/llm-statetree-1.1.2/`

## §2 — Front-matter (per entry)

Mirror the existing English template (`docs/en/news/llm-dynamic-ui-1.1.2.md`,
`docs/en/news/metasound-1.1.1.md`). Seven fields, all required:

```yaml
---
layout: doc
title: <English title, "<Plugin> v<x.y.z> — <short topic>" format>
date: 2026-07-02
tag: Fix | Plugin
summary: |
  <English 1-3 line teaser, translated from zh>
emoji: 🐛 | 🌲
slug: <same as zh version>
---
```

Per-entry:

| Field | LLMMaterial v1.1.2 | LLMStateTree v1.1.2 |
|-------|---------------------|----------------------|
| `title` | `LLMMaterial v1.1.2 — Multi-UE 5.5/5.6/5.7/5.8 Build Regression Fix` | `LLMStateTree v1.1.2 — UE 5.5/5.6/5.7/5.8 C4996 Fix` |
| `date` | `2026-07-02` | `2026-07-02` |
| `tag` | `Fix` | `Plugin` |
| `emoji` | 🐛 | 🌲 |
| `slug` | `llm-material-1.1.2` | `llm-statetree-1.1.2` |

## §3 — Translation rules

**Preserve verbatim** (these are code, not prose):

- Compiler / preprocessor symbols: `PRAGMA_DISABLE_DEPRECATION_WARNINGS`,
  `PRAGMA_ENABLE_DEPRECATION_WARNINGS`, `ENGINE_MAJOR_VERSION`,
  `ENGINE_MINOR_VERSION`, `EGetObjectsFlags::None`,
  `UMaterial::SetUsageByFlag(MATUSAGE_Xxx, bool)`,
  `LLMStateTreeCompat::RecompileStateTree`,
  `UStateTreeEditingSubsystem::CompileStateTree`,
  `LLMStateTreeCompatShim.h`, `LLMSTATETREE_UE_5_8_PLUS`.
- Source file names: `MaterialBuilder.cpp`, `LLMUMGGenerator.cpp`,
  `LLMStateTreeCommandHandler.cpp`, `Documentation.md`, `VERSION-NOTES.md`,
  `.uplugin`.
- Version strings: `UE 5.5 / 5.6 / 5.7 / 5.8`, `5.5+`, `5.7+`,
  `EngineVersion: "5.8.0"`.
- Shell command: `RunUAT.bat BuildPlugin ... -rocket`.
- Tooling tokens: `tool-fix-274`, `tool-fix-260` (existing English entry
  `metasound-1.1.1.md` already keeps `tool-fix-128` — follow precedent).
- File extensions: `.llmui`, `.llmmat`, `.llmstate`, `.llmstateschema`,
  `.llmmetasound`, `.llmschema`.
- Closing footer lines (`**Engine support**: …`, `**File format**: …`)
  — translate the label, leave the technical content untouched.

**Translate** (prose and section titles):

- Body prose, list items.
- Section titles — keep the emoji prefix, translate only the text:
  - `## 🐛 Bug Fixes` / `## 🐛 修复`
  - `## ⚡ Improvements` / `## ⚡ 改进`
  - `## ✅ Verified` / `## ✅ 验证`
  - `## 🔧 Compatibility` / `## 🔧 兼容性`
  - `## 💥 Breaking Changes` / `## 💥 破坏性变更`
  - `## 🔧 Internal Refactors` / `## 🔧 内部重构`
  - `## ✨ New Features` (if present)

## §4 — Verification

1. File existence: `docs/en/news/llm-material-1.1.2.md`,
   `docs/en/news/llm-statetree-1.1.2.md`.
2. Front-matter parity: all 7 fields present; `slug` matches the
   Chinese version byte-for-byte.
3. Local dev server: `cd docs && npm run docs:dev`, open
   `http://localhost:5173/en/news/`, sidebar shows **8** entries
   (previously 6).
4. Local production build: `npm run docs:build` — zero errors / warnings.
5. Spot-check render: emoji section headers render; no code spans
   incorrectly highlighted; long URLs / version strings not line-broken.

## §5 — Commit

Single commit on `main`:

```
docs(i18n): translate material & statetree v1.1.2 news to en

- Add docs/en/news/llm-material-1.1.2.md (translated from docs/news/llm-material-1.1.2.md)
- Add docs/en/news/llm-statetree-1.1.2.md (translated from docs/news/llm-statetree-1.1.2.md)

VitePress config auto-discovers the new entries; no config.ts changes.
Slug matches the zh version so locale-switch URL parity holds.
```