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
