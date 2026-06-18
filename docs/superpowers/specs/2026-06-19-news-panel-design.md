# News Panel — Design Spec

**Date:** 2026-06-19
**Status:** Approved (pending implementation plan)
**Author:** Brainstorming session with user

## Goal

Add a "News" surface to the YominUnreal docs site (`docs/`) that surfaces
project updates — most importantly the current headline update "Agent
Online" — to first-time visitors on the home page and to returning
visitors via a dedicated index page.

## Scope (in / out)

**In scope**

- A new `/news/` index page listing all news entries (newest first).
- A "Latest News" section on the home page showing the top 3 entries
  (1 featured + 2 compact cards).
- An entry-detail page per news item, rendered by VitePress's default
  markdown pipeline with a custom header and footer.
- A top-nav "News" link and an auto-generated `/news/` sidebar.
- 3 seed entries (1 about "Agent Online", 2 about recent plugin /
  skill launches).

**Out of scope (YAGNI)**

- Comments, RSS feed, tag-filtering, pagination, search-by-tag.
- A unit / e2e test suite.
- CI workflow.
- Custom domain, image hosting, or any infrastructure beyond the
  current GitHub Pages deploy.
- Any changes to the existing 6 plugin docs.

## Decisions captured during brainstorming

| # | Question | Decision |
|---|----------|----------|
| 1 | Form of the news panel | **C** — both `/news/` index page AND home page cards |
| 2 | Content scope | **B** — 3 seed entries, latest is "Agent Online" |
| 3 | Per-entry structure | **B** — medium blog style (title, date, tag, summary, 1–3 sections of body markdown) |
| 4 | Home page visual | **C + E hybrid** — gradient banner for the latest entry + 2 compact list rows below |
| 5 | Tag color palette | Brand-matched: Release (rose), Plugin (purple), Skill (blue), Update (yellow), Fix (green) |
| 6 | Top-nav placement | Append "News" to the right end of the existing top nav |
| 7 | Sidebar | Auto-generated from `useNews()` so adding a new entry requires zero config changes |

---

## §1 — Architecture & File Layout

Each news entry is a standalone Markdown file. VitePress (via Vite's
`import.meta.glob`) reads all of them at build time and feeds them to
two Vue components: `<LatestNews>` (home page) and `<NewsList>` (`/news/`
index page).

```
docs/
├── .vitepress/
│   ├── config.ts                        # ① nav: append "News"   ② sidebar: wire /news/
│   └── theme/
│       ├── style.css                    # news-specific styles (banner gradient, tag pills)
│       ├── composables/
│       │   └── useNews.ts               # single source of truth for entries
│       └── components/
│           ├── LatestNews.vue           # home page block (banner + 2 compact cards)
│           ├── NewsList.vue             # /news index page list (vertical timeline)
│           └── NewsEntryHeader.vue      # per-entry page header (tag / title / date)
├── news/
│   ├── index.md                         # /news page body: intro + <NewsList />
│   ├── 2026-06-19-agent-online.md       # seed: headline entry
│   ├── 2026-06-10-lite-shell.md         # seed
│   └── 2026-05-30-metasound.md          # seed
└── index.md                             # home: append <LatestNews :count="3" /> after features
```

**Why one `.md` per entry (not JSON):**

- Markdown files participate in VitePress's full-text search, sitemap,
  and "Edit this page on GitHub" link for free.
- Writing a long body in JSON is painful.
- Trade-off: ~3–4 extra lines of front-matter per entry — acceptable.

**Why `import.meta.glob` (not a VitePress custom data loader):**

- Zero config, no registration in `config.ts`.
- Adequate for a handful of entries; can migrate to a data loader later
  if the count grows past ~50.

---

## §2 — Front-matter & Data Aggregation

### Front-matter schema (per entry)

```yaml
---
title: Agent Online                          # required, main heading
date: 2026-06-19                             # required, YYYY-MM-DD, drives sort order
tag: Release                                 # required, controlled vocabulary
summary: |                                   # required, 1–3 line teaser
  AI 代理现可通过 LLM Easy Shell 直连 UE 编辑器…
  27 个原生指令 + 25 个 Python 子指令。
emoji: ⚡                                    # optional, large icon on featured banner
slug: agent-online                           # required, URL segment, kebab-case
---
```

### Controlled tag vocabulary

Documented in `docs/news/README.md` for future maintainers:

| Tag      | Meaning                  | Color (hex) |
|----------|--------------------------|-------------|
| Release  | Major release            | `#e06c75`   |
| Plugin   | New plugin / sub-module  | `#c678dd`   |
| Skill    | AI skill related         | `#61afef`   |
| Update   | General feature update   | `#e5c07b`   |
| Fix      | Bug fix                  | `#98c379`   |

### `composables/useNews.ts` — single source of truth

Exports `useNews()` which:

1. `import.meta.glob('/news/*.md', { eager: true })` — grab all entries.
2. Filter out `index.md`.
3. Read each module's `frontmatter` (Vite has already parsed it).
4. Sort by `date` descending.
5. Return `{ latest, list }` where `latest === list[0]`.

Both `<LatestNews>` and `<NewsList>` consume `useNews()` — no
duplication, no second glob.

### Why `slug` is in front-matter (not derived from filename)

Filename is human-friendly (`2026-06-19-agent-online.md`) but the URL
must be stable across renames. Decoupling slug from filename means we
can rename / reorganize files without breaking inbound links.

---

## §3 — Home Page "Latest News" Section

Inserted in `docs/index.md` after the existing `features` block. Two
sub-blocks:

### Featured banner (latest entry only)

- Full-width card, 12px corner radius, gradient
  `linear-gradient(135deg, #e06c75 0%, #c678dd 100%)`.
- Top-left: large `emoji` (if present) at 48px.
- Top-right: `LATEST` badge + `date` (small, semi-transparent white).
- Title: 20px, weight 700, white.
- Summary: max 2 lines, `line-clamp: 2`, opacity 0.9.
- Bottom-right: "Read more →".
- Whole card is one `<a>` link.

### Compact cards (entries 2..N)

- 2-column grid (desktop), 1-column stack (mobile, ≤ 768px).
- Each card: background `#1f1f23`, 1px border `#2e2e35`, 8px radius.
  ```
  ┌────────────────────────────────────────────┐
  │ 2026-06-10  [SKILL]   Lite Shell 发布   →  │
  └────────────────────────────────────────────┘
  ```
- Hover: border shifts to brand-1, card translates up 2px.
- Whole card is one `<a>` link.

### Placement

- `index.md` already defines `layout: home` with a `hero` and a
  `features` block.
- The new section appears in the markdown body, after the `features`
  YAML and before the closing `---` block.

### Mobile breakpoint

- ≤ 768px: banner full-width, compact cards stack to 1 column.

---

## §4 — `/news/` Index Page

`docs/news/index.md` body contains only:

```md
# News

Latest updates from YominUnreal.

<NewsList />
```

The `<NewsList>` component renders a vertical timeline:

- One column, max-width 720px, centered.
- Each row:
  - Left rail: a 10px dot + 2px vertical line connecting to the next row.
  - Right card:
    - Top row: `tag` pill (left) + `date` (right, small grey).
    - Title: 18px, weight 600, hover shifts to brand-1.
    - Summary: max 3 lines, `line-clamp: 3`.
    - Bottom: "Read more →".
- Sorted by `date` descending.

### Empty state

If `list` is empty, render: "暂无更新" (centered, muted) instead of
the timeline. Defensive — won't fire in practice once seeded.

---

## §5 — Entry Detail Page

URL: `/news/<slug>/` — auto-generated by VitePress from
`docs/news/<slug>.md`. Body is plain markdown rendered by VitePress's
default pipeline (code highlighting, custom containers, TOC, edit link
all work for free).

### `<NewsEntryHeader />` (above body)

- Tag pill (left) + `title` as `<h1>` (center, large) + `date` (right,
  small grey).
- 1px separator line below.

### Footer (below body)

- Left: `← Back to all news` → `/news/`.
- Right: prev/next links based on date order
  (next = older entry; prev = newer entry; hide either side if at the
  boundary).

### What we explicitly do NOT do on detail pages

- Comments, reading-time estimate, share buttons, related-entries.
- Cover image rendering (the `emoji` field is home-page-only; detail
  pages use the header's tag pill for visual identity).

---

## §6 — Navigation & Sidebar

### Top nav

Append `"News"` to the right end of `themeConfig.nav` in
`docs/.vitepress/config.ts`, visually separated from the plugin
cluster by a `1px` left border on the News item.

```
[LLM Dynamic UI] [LLM Material] [LLM StateTree] [LLM MetaSound] [LLM Easy Shell] [AI Agent Skills] | [News]
```

**Implementation note:** VitePress's nav config doesn't have a
built-in "divider" field. The border is applied via a small CSS rule
in `docs/.vitepress/theme/style.css` that targets the News item by
its `text` content (e.g., `.VPNavBarMenuLink[href="/news/"]` with a
`border-left: 1px solid var(--vp-c-divider); margin-left: 12px;
padding-left: 12px;`).

### `/news/` sidebar

`config.ts` registers a sidebar under `'/news/'` with a single root
entry: "All updates" → `/news/`. The list of individual entries is
**injected at build time** by walking `useNews()` and appending one
sidebar item per entry. This means:

- Adding a new entry: drop a new `.md` in `docs/news/`. No `config.ts`
  edit required.
- The sidebar is automatically date-sorted (same sort as the list
  page).

### Home page sidebar

Unchanged — home page has no sidebar in the current theme.

---

## §7 — Edge Cases & Testing

### Edge case behavior

| Scenario                                          | Behavior                                                                 |
|---------------------------------------------------|--------------------------------------------------------------------------|
| `news/` directory empty                           | List page shows "暂无更新"; home page `<LatestNews>` renders nothing    |
| Entry missing `date`                              | `useNews()` filters it out and `console.warn`s with the file path; warning surfaces in dev server + build output |
| Entry missing `tag`                               | Same as above                                                            |
| `tag` not in controlled vocabulary                | Render with fallback grey pill + same `console.warn`                    |
| Duplicate `slug`                                  | `useNews()` throws on the first duplicate it encounters (build fails)  |
| `date` not in `YYYY-MM-DD` format                 | Same — `useNews()` throws (date parse failure visible as `NaN` ordering) |
| `count` > available entries                       | Render only what's available                                             |
| Mobile width (≤ 768px)                            | Banner full-width; compact cards stack to 1 column; timeline rail narrows |

### Manual verification checklist (after implementation)

1. `npm run dev` — site boots without warnings.
2. Home page: scroll to "Latest News" — banner + 2 compact cards render.
3. Click banner → `/news/agent-online/` — header / body / footer all
   render.
4. Click any "Read more" (banner, compact card, list row) — navigates
   correctly.
5. `/news/` index page — 3 entries in date-desc order, timeline dots
   line up.
6. Sidebar under `/news/` — lists 3 entries automatically.
7. Resize to ≤ 768px — banner full-width, compact cards stack.
8. Toggle light / dark theme — gradient banner colors still look right.
9. Search box — typing "agent" finds the headline entry.
10. Empty `news/` (temporary) — list page shows empty state; home page
    omits the section.

### Build verification

- `npm run build` exits 0 with no Vite warnings.
- `dist/news/agent-online/index.html` exists.
- `dist/news/index.html` exists with all 3 entries linked.
- `docs/news/2026-06-19-agent-online.md` is reachable via "Edit this
  page on GitHub" link.

### What we explicitly do NOT test

- No unit tests (would require vue-test-utils + happy-dom + a VitePress
  test harness; cost > value at this scale).
- No e2e (Playwright not installed; manual checklist above is enough).
- No CI.

---

## Open questions

None — all decisions captured in the table at the top.
