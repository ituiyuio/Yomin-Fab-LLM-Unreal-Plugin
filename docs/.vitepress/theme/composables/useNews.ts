// docs/.vitepress/theme/composables/useNews.ts
//
// Single source of truth for news entries. Reads front-matter from every
// *.md under /news/ and /en/news/ at build time via Vite's import.meta.glob,
// filters index.md / README.md, validates required fields, sorts by date
// desc, and returns the slice for the *current* locale (so components
// never have to know which language they're rendering).
//
// Consumed by:
//   - LatestNews.vue  (home page)
//   - NewsList.vue    (/news/ index page)
//   - config.ts       (auto-generates /news/ sidebar)

import { useData } from 'vitepress'

export type NewsLocale = 'root' | 'en'

export interface NewsEntry {
  title: string
  date: string   // YYYY-MM-DD
  tag: string
  summary: string
  emoji?: string
  slug: string
  locale: NewsLocale
  url: string    // pre-computed, includes the locale path prefix
}

export interface UseNewsResult {
  latest: NewsEntry | null
  list: NewsEntry[]
}

interface NewsModule {
  __pageData?: { frontmatter?: Omit<NewsEntry, 'locale' | 'url'> }
  frontmatter?: Omit<NewsEntry, 'locale' | 'url'>
}

interface RawFrontmatter {
  title?: string
  date?: unknown
  tag?: string
  summary?: string
  emoji?: string
  slug?: string
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

function inferLocaleFromPath(modPath: string): NewsLocale {
  // modPath is something like "/news/agent-online.md" or
  // "/en/news/agent-online.md" (Vite glob keys, leading slash, srcDir-relative).
  const parts = modPath.split('/').filter(Boolean)
  return parts[0] === 'en' ? 'en' : 'root'
}

function readEntry(mod: NewsModule, modPath: string): NewsEntry | null {
  // VitePress 1.6 ships frontmatter on __pageData.frontmatter; some versions
  // also expose a top-level `frontmatter` named export. Try both.
  const fm = (mod.frontmatter ?? mod.__pageData?.frontmatter) as RawFrontmatter | undefined
  if (!fm) return null

  const locale = inferLocaleFromPath(modPath)
  const urlPrefix = locale === 'en' ? '/en/news/' : '/news/'

  return {
    title: fm.title ?? '',
    date: normalizeDate(fm.date),
    tag: fm.tag ?? '',
    summary: fm.summary ?? '',
    emoji: fm.emoji,
    slug: fm.slug ?? '',
    locale,
    url: fm.slug ? `${urlPrefix}${fm.slug}/` : ''
  }
}

export function useNews(): UseNewsResult {
  // VitePress 1.6: useData() returns `localeIndex` ("root" | "en"), not
  // `localePath`. localePath only exists in newer 2.x; using it here
  // crashes the build for the root locale.
  const { localeIndex } = useData()
  const currentLocale: NewsLocale =
    localeIndex.value === 'en' ? 'en' : 'root'

  // Two globs (relative to srcDir, which is `docs/`). The leading slash is
  // important — without it, Vite would resolve these relative to the
  // composable's own file location and miss everything.
  const modules = import.meta.glob<NewsModule>(
    ['/news/*.md', '/en/news/*.md'],
    { eager: true }
  )

  const entries: NewsEntry[] = []
  const seenSlugs = new Set<string>()

  for (const [modPath, mod] of Object.entries(modules)) {
    const filename = modPath.split('/').pop() ?? modPath

    // Skip the index page (list page) and the maintainer guide.
    if (filename === 'index.md' || filename === 'README.md') continue

    const entry = readEntry(mod, modPath)

    if (!entry?.date) {
      console.warn(`[news] ${modPath}: missing front-matter "date" — skipping`)
      continue
    }
    if (!entry.tag) {
      console.warn(`[news] ${modPath}: missing front-matter "tag" — skipping`)
      continue
    }
    if (!entry.slug) {
      console.warn(`[news] ${modPath}: missing front-matter "slug" — skipping`)
      continue
    }
    const dupKey = `${entry.locale}/${entry.slug}`
    if (seenSlugs.has(dupKey)) {
      throw new Error(
        `[news] duplicate slug "${entry.slug}" in ${modPath} — slugs must be unique per locale`
      )
    }
    seenSlugs.add(dupKey)

    entries.push(entry)
  }

  // Filter to the current locale. Sorting is global so dates line up
  // across locales if the same slug is used in both.
  const localEntries = entries.filter((e) => e.locale === currentLocale)

  localEntries.sort((a, b) => {
    const ta = Date.parse(a.date)
    const tb = Date.parse(b.date)
    if (Number.isNaN(ta) && Number.isNaN(tb)) return 0
    if (Number.isNaN(ta)) return 1
    if (Number.isNaN(tb)) return -1
    return tb - ta
  })

  return {
    latest: localEntries[0] ?? null,
    list: localEntries
  }
}
