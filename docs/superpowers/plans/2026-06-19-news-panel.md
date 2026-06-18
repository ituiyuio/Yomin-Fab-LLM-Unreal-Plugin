# News Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/news/` index page and a home-page "Latest News" section to the YominUnreal docs site, surfacing "Agent Online" as the headline update.

**Architecture:** One Markdown file per news entry under `docs/news/`, with front-matter metadata. A single `useNews()` composable (uses Vite's `import.meta.glob`) aggregates them at build time and feeds two presentational Vue components (`LatestNews` for the home page, `NewsList` for `/news/`) and one custom layout (`news-entry.vue`) for entry-detail pages. Tag color palette mirrors the existing 5 brand CSS variables in `theme/style.css`.

**Tech Stack:** VitePress 1.6, Vue 3 (`<script setup>`), TypeScript for the composable, plain CSS (no preprocessor).

---

## File Structure

```
docs/
├── .vitepress/
│   ├── config.ts                        # MODIFY  — nav "News", sidebar under /news/
│   └── theme/
│       ├── index.ts                     # MODIFY  — register LatestNews, NewsList
│       ├── style.css                    # MODIFY  — tag pills, banner gradient, timeline rail, nav divider
│       ├── composables/
│       │   └── useNews.ts               # CREATE  — single source of truth, glob → sorted list
│       ├── components/
│       │   ├── LatestNews.vue           # CREATE  — home page section (banner + compact grid)
│       │   ├── NewsList.vue             # CREATE  — /news page (vertical timeline)
│       │   └── NewsEntryHeader.vue      # CREATE  — tag pill + h1 + date header strip
│       └── layouts/
│           └── news-entry.vue           # CREATE  — custom layout: header + content + prev/next
├── news/
│   ├── README.md                        # CREATE  — maintainer guide (tag vocabulary)
│   ├── index.md                         # CREATE  — /news page body (intro + <NewsList />)
│   ├── 2026-06-19-agent-online.md       # CREATE  — seed 1 (headline)
│   ├── 2026-06-10-lite-shell.md         # CREATE  — seed 2
│   └── 2026-05-30-metasound.md          # CREATE  — seed 3
└── index.md                             # MODIFY  — append <LatestNews :count="3" />
```

**Why this decomposition:** each file has one clear responsibility. The composable owns data; components own visual presentation of *lists*; the layout owns the visual presentation of a *single entry*. Theme `index.ts` owns global registration. CSS stays flat in `style.css` to match the existing pattern.

---

## Task 1: Seed news entries

**Files:**
- Create: `docs/news/README.md`
- Create: `docs/news/2026-06-19-agent-online.md`
- Create: `docs/news/2026-06-10-lite-shell.md`
- Create: `docs/news/2026-05-30-metasound.md`

- [ ] **Step 1: Create the `docs/news/` directory**

Run: `mkdir -p docs/news`

- [ ] **Step 2: Create `docs/news/README.md` — maintainer guide for tag vocabulary**

```markdown
# News — Maintainer Guide

This directory holds news entries. Each entry is one `.md` file named
`YYYY-MM-DD-<slug>.md` (date is the publish date; the `slug` is purely
human-friendly, the URL segment is driven by the `slug` front-matter).

## Required front-matter

```yaml
---
title: Agent Online                          # required
date: 2026-06-19                             # required, YYYY-MM-DD, drives sort
tag: Release                                 # required, see table below
summary: |                                   # required, 1-3 line teaser
  AI 代理现可通过 LLM Easy Shell 直连 UE 编辑器…
emoji: ⚡                                    # optional, large icon on home banner
slug: agent-online                           # required, URL segment, kebab-case
---
```

## Tag vocabulary (controlled)

| Tag      | Meaning                  | Color (hex) |
|----------|--------------------------|-------------|
| Release  | Major release            | `#e06c75`   |
| Plugin   | New plugin / sub-module  | `#c678dd`   |
| Skill    | AI skill related         | `#61afef`   |
| Update   | General feature update   | `#e5c07b`   |
| Fix      | Bug fix                  | `#98c379`   |

Don't introduce new tags without updating this table.
```

- [ ] **Step 3: Create `docs/news/2026-06-19-agent-online.md`**

```markdown
---
title: Agent Online
date: 2026-06-19
tag: Release
summary: |
  AI 代理现可通过 LLM Easy Shell 直连 Unreal Editor — 27 个原生指令 + 25 个 Python 子指令，覆盖 actor 操作、属性编辑、Live Coding、截图。
emoji: ⚡
slug: agent-online
---

# Agent Online

我们刚刚把 **LLM Easy Shell** 升级到了"Agent Online"阶段 —— AI 代理现在可以直接驱动一个正在运行的 Unreal Editor。

## 这次能做什么

- **27 个原生指令** 覆盖 actor 增删改查、属性编辑、关卡管理
- **25 个 Python 子指令** 调用任何 `unreal` 模块 API
- **Live Coding** 触发：让 agent 改完 C++ 自动热重载
- **截图拉回**：agent 可以"看到"编辑器画面（PNG via TCP）

## 为什么是"Online"

之前的 Easy Shell 是离线管线（agent 写 JSON → 编译资产）。这次升级后，agent
和 Editor 之间有一条 **TCP 长连接**（端口 15151–15200），agent 可以在 loop
里反复"探查 → 编辑 → 截图验证"，形成真正的反馈环。

## 怎么开始

```bash
# 在 Editor 里
Edit → Plugins → LLM Easy Shell → Enable → Restart
# TCP 端口会自动分配，状态写到 .current_port
```

接着让你的 agent 读 `skills/llm-easy-shell/SKILL.md` 即可上手。
```

- [ ] **Step 4: Create `docs/news/2026-06-10-lite-shell.md`**

```markdown
---
title: Lite Shell 发布
date: 2026-06-10
tag: Skill
summary: |
  LLM Easy Shell 的只读子集 —— 9 个安全指令，适合让 agent 浏览场景和资产而不会有副作用。
emoji: 🔍
slug: lite-shell
---

# Lite Shell 发布

我们发布了 **LLM Easy Shell Lite**：Easy Shell 的只读子集，专为"安全浏览"设计。

## 9 个指令，全部只读

- `list_actors` / `inspect_actor` —— 浏览场景中的 actor
- `list_assets` / `inspect_asset` —— 浏览 `/Game/` 下的资产
- `get_property` —— 读取任意属性
- `screenshot` —— 截图当前视口
- `evaluate_python` —— 在受限沙箱里跑只读 Python

## 和完整版的关系

- Lite Shell 使用端口段 **15201–15250**（完整版是 15151–15200）
- 只依赖 2 个 engine plugin（`PythonScriptPlugin` + `EditorScriptingUtilities`）
- 完全免费，可直接装在只读工作流里

## 适用场景

- 文档 agent：让 AI 读懂工程现状
- 教学 agent：让 AI 演示但不修改
- CI agent：让 AI 在 PR 阶段做资产盘点
```

- [ ] **Step 5: Create `docs/news/2026-05-30-metasound.md`**

```markdown
---
title: MetaSound 插件上线
date: 2026-05-30
tag: Plugin
summary: |
  第四个插件 —— LLM MetaSound —— 上线。从 JSON 编译 UMetaSoundSource 和 UMetaSoundPatch。
emoji: 🔊
slug: metasound
---

# MetaSound 插件上线

我们发布了 **LLM MetaSound** 插件：第四个"JSON → 资产"家族的成员。

## 能生成什么

- `UMetaSoundSource` —— 完整 MetaSound 资产
- `UMetaSoundPatch` —— 子图 / patch
- 支持 **generators / filters / envelopes / mixers / bus IO** 全节点类型
- 节点自动连接 —— 写 JSON 时不需要画线

## 一个例子

```json
{
  "version": "1.0",
  "name": "Kick",
  "type": "Source",
  "graph": {
    "nodes": [
      { "id": "osc", "type": "SineOscillator", "params": { "frequency": 60 } },
      { "id": "env", "type": "ADEnvelope",     "params": { "attack": 0.001, "decay": 0.12 } },
      { "id": "out", "type": "Output" }
    ],
    "connections": [
      { "from": "osc", "to": "env" },
      { "from": "env", "to": "out" }
    ]
  }
}
```

## 上哪里

- 仓库：`skills/llm-metasound/SKILL.md`
- Wiki：`/llm-metasound/`
- Fab 列表：准备中
```

- [ ] **Step 6: Commit**

```bash
git add docs/news/README.md docs/news/2026-06-19-agent-online.md \
        docs/news/2026-06-10-lite-shell.md docs/news/2026-05-30-metasound.md
git commit -m "feat(news): add tag vocabulary README and 3 seed entries"
```

---

## Task 2: `useNews()` composable

**Files:**
- Create: `docs/.vitepress/theme/composables/useNews.ts`

- [ ] **Step 1: Create the composable file with full implementation**

```ts
// docs/.vitepress/theme/composables/useNews.ts
//
// Single source of truth for news entries. Reads front-matter from every
// *.md under /news/ at build time via Vite's import.meta.glob, filters
// index.md, validates required fields, sorts by date desc, returns
// { latest, list }.
//
// Consumed by:
//   - LatestNews.vue  (home page)
//   - NewsList.vue    (/news/ index page)
//   - config.ts       (auto-generates /news/ sidebar)

export interface NewsEntry {
  title: string
  date: string
  tag: string
  summary: string
  emoji?: string
  slug: string
}

export interface UseNewsResult {
  latest: NewsEntry | null
  list: NewsEntry[]
}

interface NewsModule {
  frontmatter: NewsEntry
}

export function useNews(): UseNewsResult {
  const modules = import.meta.glob<NewsModule>('/news/*.md', {
    eager: true
  })

  const entries: NewsEntry[] = []
  const seenSlugs = new Set<string>()

  for (const [path, mod] of Object.entries(modules)) {
    const filename = path.split('/').pop() ?? path

    // Skip the index page — it's the list page, not an entry.
    if (filename === 'index.md') continue

    const fm = mod.frontmatter

    if (!fm?.date) {
      console.warn(`[news] ${filename}: missing front-matter "date" — skipping`)
      continue
    }
    if (!fm?.tag) {
      console.warn(`[news] ${filename}: missing front-matter "tag" — skipping`)
      continue
    }
    if (!fm?.slug) {
      console.warn(`[news] ${filename}: missing front-matter "slug" — skipping`)
      continue
    }
    if (seenSlugs.has(fm.slug)) {
      throw new Error(
        `[news] duplicate slug "${fm.slug}" in ${filename} — slugs must be unique`
      )
    }
    seenSlugs.add(fm.slug)

    entries.push(fm)
  }

  // Sort by date desc. Invalid dates sink to the end.
  entries.sort((a, b) => {
    const ta = Date.parse(a.date)
    const tb = Date.parse(b.date)
    if (Number.isNaN(ta) && Number.isNaN(tb)) return 0
    if (Number.isNaN(ta)) return 1
    if (Number.isNaN(tb)) return -1
    return tb - ta
  })

  return {
    latest: entries[0] ?? null,
    list: entries
  }
}
```

- [ ] **Step 2: Sanity-check the composable via the dev server**

Run: `cd docs && npm run dev` (in another terminal)
Expected: server starts on http://localhost:5173, no `[news]` warnings in the
console (we haven't wired it anywhere yet, but `import.meta.glob` is module-
loaded as soon as any file imports it — so the warnings will surface once we
import it in a component in the next task; this step is just to confirm the
dev server boots cleanly with the new file present).

Stop the dev server before continuing.

- [ ] **Step 3: Commit**

```bash
git add docs/.vitepress/theme/composables/useNews.ts
git commit -m "feat(news): add useNews composable with validation"
```

---

## Task 3: `LatestNews.vue` component

**Files:**
- Create: `docs/.vitepress/theme/components/LatestNews.vue`

- [ ] **Step 1: Create the component**

```vue
<script setup lang="ts">
import { useNews } from '../composables/useNews'

const props = withDefaults(
  defineProps<{ count?: number }>(),
  { count: 3 }
)

const { list } = useNews()
const featured = list[0] ?? null
const rest = list.slice(1, props.count)

function hrefFor(slug: string): string {
  return `/news/${slug}/`
}
</script>

<template>
  <section v-if="featured" class="news-section">
    <h2 class="news-section-title">Latest News</h2>

    <!-- Featured banner: the most recent entry -->
    <a :href="hrefFor(featured.slug)" class="news-banner">
      <span v-if="featured.emoji" class="news-banner-emoji">{{ featured.emoji }}</span>
      <div class="news-banner-meta">
        <span class="news-banner-badge">LATEST</span>
        <span class="news-banner-date">{{ featured.date }}</span>
      </div>
      <h3 class="news-banner-title">{{ featured.title }}</h3>
      <p class="news-banner-summary">{{ featured.summary }}</p>
      <span class="news-banner-cta">Read more →</span>
    </a>

    <!-- Compact cards: entries 2..N -->
    <div v-if="rest.length" class="news-compact-grid">
      <a
        v-for="entry in rest"
        :key="entry.slug"
        :href="hrefFor(entry.slug)"
        class="news-compact-card"
      >
        <span class="news-compact-date">{{ entry.date }}</span>
        <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
          {{ entry.tag.toUpperCase() }}
        </span>
        <span class="news-compact-title">{{ entry.title }}</span>
        <span class="news-compact-arrow">→</span>
      </a>
    </div>
  </section>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add docs/.vitepress/theme/components/LatestNews.vue
git commit -m "feat(news): add LatestNews home page section component"
```

---

## Task 4: Register `LatestNews` and wire into home page

**Files:**
- Modify: `docs/.vitepress/theme/index.ts`
- Modify: `docs/index.md`

- [ ] **Step 1: Update `docs/.vitepress/theme/index.ts` to register `LatestNews`**

Replace the entire file contents with:

```ts
import DefaultTheme from 'vitepress/theme'
import LatestNews from './components/LatestNews.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('LatestNews', LatestNews)
  }
}
```

- [ ] **Step 2: Append the section to `docs/index.md`**

Read the current file (`docs/index.md`). After the closing `---` of the
front-matter and after the existing `<div style="text-align: center; ...">`
paragraph, append a blank line and then:

```markdown

<LatestNews :count="3" />
```

The final `docs/index.md` should end like this:

```markdown
  - icon: 🔍
    title: LLM Easy Shell Lite
    details: Read-only TCP bridge between any LLM agent and the Unreal Editor. 9 commands, ports 15201–15250, 2 engine plugin deps, free.
    link: /llm-easy-shell-lite/
    linkText: Explore
---

<div style="text-align: center; padding: 2rem 0; color: #888;">
All plugins share the same paradigm: <strong>define your intent in JSON</strong>, and let the plugin handle the rest.
</div>

<LatestNews :count="3" />
```

- [ ] **Step 3: Boot dev server and verify section renders**

Run: `cd docs && npm run dev`
Expected: home page (http://localhost:5173/) loads without errors. Scroll to
bottom; a "Latest News" section is visible with a gradient banner ("Agent
Online", dated 2026-06-19) and 2 compact cards below (Lite Shell, MetaSound).

If a `[news]` warning appears in the dev console, fix the corresponding
entry's front-matter before continuing.

- [ ] **Step 4: Commit**

```bash
git add docs/.vitepress/theme/index.ts docs/index.md
git commit -m "feat(news): wire LatestNews into home page"
```

---

## Task 5: `NewsList.vue` component

**Files:**
- Create: `docs/.vitepress/theme/components/NewsList.vue`

- [ ] **Step 1: Create the component**

```vue
<script setup lang="ts">
import { useNews } from '../composables/useNews'

const { list } = useNews()

function hrefFor(slug: string): string {
  return `/news/${slug}/`
}
</script>

<template>
  <div v-if="list.length" class="news-timeline">
    <article
      v-for="(entry, idx) in list"
      :key="entry.slug"
      class="news-timeline-row"
    >
      <div class="news-timeline-rail">
        <span class="news-timeline-dot" />
        <span v-if="idx < list.length - 1" class="news-timeline-line" />
      </div>
      <a :href="hrefFor(entry.slug)" class="news-timeline-card">
        <div class="news-timeline-meta">
          <span :class="['news-tag', `news-tag-${entry.tag.toLowerCase()}`]">
            {{ entry.tag.toUpperCase() }}
          </span>
          <span class="news-timeline-date">{{ entry.date }}</span>
        </div>
        <h3 class="news-timeline-title">{{ entry.title }}</h3>
        <p class="news-timeline-summary">{{ entry.summary }}</p>
        <span class="news-timeline-cta">Read more →</span>
      </a>
    </article>
  </div>
  <p v-else class="news-empty">暂无更新</p>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add docs/.vitepress/theme/components/NewsList.vue
git commit -m "feat(news): add NewsList timeline component"
```

---

## Task 6: Wire `NewsList` into `/news/` page

**Files:**
- Modify: `docs/.vitepress/theme/index.ts`
- Create: `docs/news/index.md`

- [ ] **Step 1: Update `docs/.vitepress/theme/index.ts` to also register `NewsList`**

Replace the file with:

```ts
import DefaultTheme from 'vitepress/theme'
import LatestNews from './components/LatestNews.vue'
import NewsList from './components/NewsList.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('LatestNews', LatestNews)
    app.component('NewsList', NewsList)
  }
}
```

- [ ] **Step 2: Create `docs/news/index.md`**

```markdown
# News

Latest updates from YominUnreal.

<NewsList />
```

- [ ] **Step 3: Verify the page renders**

Run: `cd docs && npm run dev` (if not already running)
Open: http://localhost:5173/news/
Expected: a "News" h1, a one-line subtitle, then 3 timeline rows
(2026-06-19, 2026-06-10, 2026-05-30) with dots and connecting lines.

- [ ] **Step 4: Commit**

```bash
git add docs/.vitepress/theme/index.ts docs/news/index.md
git commit -m "feat(news): create /news/ page with NewsList"
```

---

## Task 7: Entry header component + custom layout

**Files:**
- Create: `docs/.vitepress/theme/components/NewsEntryHeader.vue`
- Create: `docs/.vitepress/theme/layouts/news-entry.vue`
- Modify: `docs/news/2026-06-19-agent-online.md`
- Modify: `docs/news/2026-06-10-lite-shell.md`
- Modify: `docs/news/2026-05-30-metasound.md`

- [ ] **Step 1: Create the header component**

```vue
<script setup lang="ts">
interface Props {
  tag: string
  title: string
  date: string
}
defineProps<Props>()
</script>

<template>
  <header class="news-entry-header">
    <span :class="['news-tag', `news-tag-${tag.toLowerCase()}`]">
      {{ tag.toUpperCase() }}
    </span>
    <h1 class="news-entry-title">{{ title }}</h1>
    <span class="news-entry-date">{{ date }}</span>
  </header>
</template>
```

- [ ] **Step 2: Create the custom layout `docs/.vitepress/theme/layouts/news-entry.vue`**

```vue
<script setup lang="ts">
import { useData } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NewsEntryHeader from '../components/NewsEntryHeader.vue'

const { frontmatter } = useData()
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <NewsEntryHeader
        :tag="frontmatter.tag"
        :title="frontmatter.title"
        :date="frontmatter.date"
      />
    </template>
  </DefaultTheme.Layout>
</template>
```

- [ ] **Step 3: Add `layout: news-entry` to each seed entry's front-matter**

For each of the three seed `.md` files created in Task 1, add the line
`layout: news-entry` immediately under the `---` opening fence (above
`title:`). Example for `2026-06-19-agent-online.md`:

```markdown
---
layout: news-entry
title: Agent Online
date: 2026-06-19
tag: Release
summary: |
  AI 代理现可通过 LLM Easy Shell 直连 Unreal Editor…
emoji: ⚡
slug: agent-online
---
```

Repeat for the other two files (their front-matter is already correct
except for the missing `layout` line).

- [ ] **Step 4: Verify a detail page renders**

Run: `cd docs && npm run dev` (if not running)
Open: http://localhost:5173/news/agent-online/
Expected: tag pill + "Agent Online" h1 + date at the top, followed by
the markdown body (h1, paragraphs, code block). No errors in console.

- [ ] **Step 5: Commit**

```bash
git add docs/.vitepress/theme/components/NewsEntryHeader.vue \
        docs/.vitepress/theme/layouts/news-entry.vue \
        docs/news/2026-06-19-agent-online.md \
        docs/news/2026-06-10-lite-shell.md \
        docs/news/2026-05-30-metasound.md
git commit -m "feat(news): add entry header component and custom layout"
```

---

## Task 8: Entry footer with "Back to all news"

**Files:**
- Modify: `docs/.vitepress/theme/layouts/news-entry.vue`

- [ ] **Step 1: Extend the layout to render a footer after the content**

Replace `docs/.vitepress/theme/layouts/news-entry.vue` with:

```vue
<script setup lang="ts">
import { useData } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NewsEntryHeader from '../components/NewsEntryHeader.vue'

const { frontmatter } = useData()
</script>

<template>
  <DefaultTheme.Layout>
    <template #doc-before>
      <NewsEntryHeader
        :tag="frontmatter.tag"
        :title="frontmatter.title"
        :date="frontmatter.date"
      />
    </template>
    <template #doc-after>
      <footer class="news-entry-footer">
        <a href="/news/" class="news-back-link">← Back to all news</a>
      </footer>
    </template>
  </DefaultTheme.Layout>
</template>
```

- [ ] **Step 2: Verify footer renders**

Reload http://localhost:5173/news/agent-online/ in the dev server.
Expected: at the bottom of the article, a "← Back to all news" link,
clickable, takes you to /news/.

- [ ] **Step 3: Commit**

```bash
git add docs/.vitepress/theme/layouts/news-entry.vue
git commit -m "feat(news): add back-to-all-news footer on entry pages"
```

---

## Task 9: Top nav + sidebar

**Files:**
- Modify: `docs/.vitepress/config.ts`

- [ ] **Step 1: Append "News" to the nav and add a sidebar under `/news/`**

The current `themeConfig.nav` array ends with `{ text: 'AI Agent Skills', link: '/skills/' }`.
Add a 7th element after it:

```ts
{ text: 'News', link: '/news/' }
```

For the sidebar, add a new key to the `sidebar` object (after the
`/skills/` block, before the closing `}`):

```ts
'/news/': [
  {
    text: 'News',
    items: [
      { text: 'All updates', link: '/news/' }
    ]
  }
]
```

The full updated `themeConfig.nav` (for reference) reads:

```ts
nav: [
  { text: 'LLM Dynamic UI', link: '/llm-dynamic-ui/' },
  { text: 'LLM Material', link: '/llm-material/' },
  { text: 'LLM StateTree', link: '/llm-statetree/' },
  { text: 'LLM MetaSound', link: '/llm-metasound/' },
  { text: 'LLM Easy Shell', link: '/llm-easy-shell/' },
  { text: 'AI Agent Skills', link: '/skills/' },
  { text: 'News', link: '/news/' }
],
```

- [ ] **Step 2: Verify nav shows the new entry**

Reload the dev server. Top-right of the nav: "News" link is visible
(visual separator border will be added in the CSS task). Click it
→ navigates to /news/.

- [ ] **Step 3: Commit**

```bash
git add docs/.vitepress/config.ts
git commit -m "feat(news): add News to top nav"
```

---

## Task 10: News-specific CSS

**Files:**
- Modify: `docs/.vitepress/theme/style.css`

- [ ] **Step 1: Append all news styles to `docs/.vitepress/theme/style.css`**

The existing file holds brand CSS variables and a hero-text gradient.
Add the following block at the end of the file (do **not** touch the
existing `:root` block — we reuse the brand vars):

```css
/* ==========================================================================
   News Panel — home page section
   ========================================================================== */

.news-section {
  max-width: 1152px;
  margin: 64px auto 0;
  padding: 0 24px;
}

.news-section-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 24px;
  color: var(--vp-c-text-1);
}

/* Featured banner (latest entry) */
.news-banner {
  position: relative;
  display: block;
  padding: 32px 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #e06c75 0%, #c678dd 100%);
  color: #fff;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.news-banner:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(224, 108, 117, 0.25);
}

.news-banner-emoji {
  position: absolute;
  top: 28px;
  left: 36px;
  font-size: 48px;
  line-height: 1;
}

.news-banner-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 12px;
  opacity: 0.9;
}

.news-banner-badge {
  background: rgba(255, 255, 255, 0.18);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.news-banner-date {
  font-variant-numeric: tabular-nums;
}

.news-banner-title {
  margin: 8px 0 8px;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  /* Reserve room for the emoji on the left */
  padding-left: 72px;
  min-height: 48px;
}

.news-banner-summary {
  margin: 0 0 16px;
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.9;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  padding-left: 72px;
}

.news-banner-cta {
  font-size: 13px;
  font-weight: 600;
  padding-left: 72px;
}

/* Compact cards (entries 2..N) */
.news-compact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.news-compact-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.news-compact-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.news-compact-date {
  font-size: 12px;
  color: var(--vp-c-text-3);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.news-compact-title {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.news-compact-arrow {
  color: var(--vp-c-brand-4);
  flex-shrink: 0;
}

/* ==========================================================================
   Tag pill — shared across all news surfaces
   ========================================================================== */

.news-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #fff;
  flex-shrink: 0;
}

.news-tag-release { background: #e06c75; }
.news-tag-plugin  { background: #c678dd; }
.news-tag-skill   { background: #61afef; }
.news-tag-update  { background: #e5c07b; }
.news-tag-fix     { background: #98c379; }
.news-tag-unknown { background: #666; }

/* ==========================================================================
   News list (/news/ index page) — vertical timeline
   ========================================================================== */

.news-timeline {
  max-width: 720px;
  margin: 32px auto 0;
  padding: 0 24px;
}

.news-timeline-row {
  display: flex;
  gap: 20px;
  padding-bottom: 24px;
}

.news-timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 18px;
  flex-shrink: 0;
}

.news-timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--vp-c-brand-1);
  margin-top: 14px;
  flex-shrink: 0;
}

.news-timeline-line {
  flex: 1;
  width: 2px;
  background: var(--vp-c-divider);
  margin-top: 8px;
}

.news-timeline-card {
  flex: 1;
  display: block;
  padding: 16px 20px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.news-timeline-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.news-timeline-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.news-timeline-date {
  margin-left: auto;
  font-size: 12px;
  color: var(--vp-c-text-3);
  font-variant-numeric: tabular-nums;
}

.news-timeline-title {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 600;
}

.news-timeline-title:hover {
  color: var(--vp-c-brand-1);
}

.news-timeline-summary {
  margin: 0 0 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-timeline-cta {
  font-size: 12px;
  font-weight: 600;
  color: var(--vp-c-brand-4);
}

.news-empty {
  text-align: center;
  color: var(--vp-c-text-3);
  padding: 48px 0;
}

/* ==========================================================================
   News entry detail page — header strip + footer
   ========================================================================== */

.news-entry-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
  border-bottom: 1px solid var(--vp-c-divider);
  margin-bottom: 24px;
}

.news-entry-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  flex: 1;
  line-height: 1.2;
}

.news-entry-date {
  font-size: 13px;
  color: var(--vp-c-text-3);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.news-entry-footer {
  display: flex;
  justify-content: flex-start;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}

.news-back-link {
  color: var(--vp-c-brand-1);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}

.news-back-link:hover {
  text-decoration: underline;
}

/* ==========================================================================
   Top nav — News item visual separator
   ========================================================================== */

.VPNavBarMenuLink[href="/news/"] {
  border-left: 1px solid var(--vp-c-divider);
  margin-left: 12px;
  padding-left: 16px;
}

/* ==========================================================================
   Mobile responsive (≤ 768px)
   ========================================================================== */

@media (max-width: 768px) {
  .news-section {
    padding: 0 16px;
  }

  .news-banner {
    padding: 24px 20px;
  }

  .news-banner-emoji {
    font-size: 36px;
    top: 20px;
    left: 20px;
  }

  .news-banner-title,
  .news-banner-summary,
  .news-banner-cta {
    padding-left: 56px;
  }

  .news-banner-title {
    font-size: 22px;
  }

  .news-compact-grid {
    grid-template-columns: 1fr;
  }

  .news-entry-header {
    flex-wrap: wrap;
  }

  .news-entry-title {
    flex-basis: 100%;
    order: 3;
  }

  .VPNavBarMenuLink[href="/news/"] {
    border-left: none;
    margin-left: 0;
    padding-left: 0;
  }
}
```

- [ ] **Step 2: Visual smoke-test all three surfaces**

Reload the dev server. Walk through:

1. Home page — banner gradient is visible, compact cards are 2-up on
   desktop, 1-up on mobile (resize the window).
2. `/news/` — timeline dots line up vertically, connecting lines render
   between rows.
3. `/news/agent-online/` — header has tag pill + h1 + date with a
   bottom border; body renders; "← Back to all news" footer is
   present.
4. Top nav — "News" has a thin left border separating it from the
   plugin cluster.
5. Hover any card or timeline row — border turns rose, card lifts 2px.
6. Toggle light/dark theme — colors still look right (banner gradient
   is fixed, but text/border use theme variables).

- [ ] **Step 3: Commit**

```bash
git add docs/.vitepress/theme/style.css
git commit -m "feat(news): add news panel CSS (banner, timeline, tags, responsive)"
```

---

## Task 11: Production build verification

**Files:** (none modified)

- [ ] **Step 1: Stop the dev server**

Kill any running `npm run dev` process (Ctrl+C in its terminal, or kill
its PID).

- [ ] **Step 2: Run the production build**

Run: `cd docs && npm run build`
Expected: exits 0 with no errors and no Vite warnings.

If `[news]` warnings appear, fix the corresponding entry's front-matter
in `docs/news/`.

- [ ] **Step 3: Spot-check the built output**

Run:
```bash
ls docs/.vitepress/dist/news/
ls docs/.vitepress/dist/news/agent-online/
test -f docs/.vitepress/dist/news/agent-online/index.html && echo OK
test -f docs/.vitepress/dist/news/index.html && echo OK
test -f docs/.vitepress/dist/index.html && echo OK
```
Expected: each `echo OK` prints.

- [ ] **Step 4: Smoke-test the built site**

Run: `cd docs && npm run preview` (serves the dist on a port)
Open the printed URL in a browser. Re-run the 6-item visual check
from Task 10's Step 2. Confirm everything still works in the built
artifact (sometimes build-only issues — like missing chunks — surface
here but not in dev).

Stop the preview server when done.

- [ ] **Step 5: Commit (only if you had to fix something)**

If Steps 2–4 surfaced no issues, there's nothing to commit. If you
fixed a CSS or front-matter issue, commit it:

```bash
git add <fixed files>
git commit -m "fix(news): address build warnings / preview smoke issues"
```

---

## Task 12: Final review and tag

**Files:** (none modified)

- [ ] **Step 1: Walk the original 10-item manual checklist from the spec**

Open `docs/superpowers/specs/2026-06-19-news-panel-design.md` §7 and
re-run the manual verification checklist. Tick each item mentally; if
any fail, open a fix-up task and run it.

- [ ] **Step 2: Final commit (if any) and log**

If Task 11 surfaced nothing, this is a no-op. If you made any further
fixes:

```bash
git add <fixed files>
git commit -m "fix(news): final spec checklist fixes"
```

- [ ] **Step 3: Update the spec status line**

Edit `docs/superpowers/specs/2026-06-19-news-panel-design.md` to
change the **Status** field from "Approved (pending implementation
plan)" to "Implemented".

- [ ] **Step 4: Commit the spec status update**

```bash
git add docs/superpowers/specs/2026-06-19-news-panel-design.md
git commit -m "docs(news): mark spec as implemented"
```

---

## Self-Review

After writing the plan, the following checks were performed:

**Spec coverage** — every requirement in the design spec is implemented:
- §1 architecture → Tasks 1, 2, 7
- §2 front-matter + useNews → Tasks 1, 2
- §3 home page visual → Tasks 3, 4, 10
- §4 /news list page → Tasks 5, 6, 10
- §5 entry detail page → Tasks 7, 8, 10
- §6 nav + sidebar → Task 9
- §7 edge cases → embedded in `useNews` (Task 2); build/manual verification in Task 11

**Placeholder scan** — no TBD/TODO/"implement later" remains. Every code block contains the actual content. No "similar to Task N" shortcuts — the seed files are inlined in Task 1, not referenced.

**Type consistency** — `useNews` returns `{ latest, list }` of `NewsEntry`; both Vue components destructure that exact shape; the layout reads `frontmatter.tag/title/date` which match the front-matter schema in Task 1; CSS class names (`news-banner`, `news-compact-card`, `news-timeline-card`, `news-entry-header`, `news-tag`, etc.) are used identically in templates and stylesheet.
