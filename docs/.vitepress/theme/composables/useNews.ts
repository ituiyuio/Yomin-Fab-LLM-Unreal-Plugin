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
  date: string   // YYYY-MM-DD
  tag: string
  summary: string
  emoji?: string
  slug: string
}

export interface UseNewsResult {
  latest: NewsEntry | null
  list: NewsEntry[]
}

interface NewsPageData {
  title: string
  description: string
  frontmatter: NewsEntry
  headers: unknown[]
  relativePath: string
  filePath: string
}

interface NewsModule {
  __pageData?: NewsPageData
  frontmatter?: NewsEntry
}

/** Normalize a date value to YYYY-MM-DD string. */
function normalizeDate(value: unknown): string {
  if (value instanceof Date) {
    // VitePress parses YYYY-MM-DD YAML dates into Date objects; restore the
    // local-date string. toISOString would shift to UTC and possibly
    // land on the previous day for users east of UTC.
    const y = value.getFullYear()
    const m = String(value.getMonth() + 1).padStart(2, '0')
    const d = String(value.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }
  if (typeof value === 'string') {
    // Accept either "2026-06-19" or "2026-06-19T00:00:00.000Z" (already ISO).
    return value.slice(0, 10)
  }
  return ''
}

function readEntry(mod: NewsModule): NewsEntry | null {
  // VitePress 1.6 ships frontmatter on __pageData.frontmatter; some versions
  // also expose a top-level `frontmatter` named export. Try both.
  const fm = mod.frontmatter ?? mod.__pageData?.frontmatter
  if (!fm) return null
  return { ...fm, date: normalizeDate(fm.date) }
}

export function useNews(): UseNewsResult {
  const modules = import.meta.glob<NewsModule>('/news/*.md', {
    eager: true
  })

  const entries: NewsEntry[] = []
  const seenSlugs = new Set<string>()

  for (const [path, mod] of Object.entries(modules)) {
    const filename = path.split('/').pop() ?? path

    // Skip the index page (list page) and the maintainer guide.
    if (filename === 'index.md' || filename === 'README.md') continue

    const entry = readEntry(mod)

    if (!entry?.date) {
      console.warn(`[news] ${filename}: missing front-matter "date" — skipping`)
      continue
    }
    if (!entry.tag) {
      console.warn(`[news] ${filename}: missing front-matter "tag" — skipping`)
      continue
    }
    if (!entry.slug) {
      console.warn(`[news] ${filename}: missing front-matter "slug" — skipping`)
      continue
    }
    if (seenSlugs.has(entry.slug)) {
      throw new Error(
        `[news] duplicate slug "${entry.slug}" in ${filename} — slugs must be unique`
      )
    }
    seenSlugs.add(entry.slug)

    entries.push(entry)
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
