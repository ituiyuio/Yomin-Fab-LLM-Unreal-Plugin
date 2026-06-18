import { defineConfig } from 'vitepress'
import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

// -----------------------------------------------------------------------------
// Read news entries' front-matter for the /news/ sidebar.
//
// We can't use Vite's import.meta.glob here (config.ts runs outside Vite's
// transform context). We don't have a YAML lib, so we parse just the few
// fields we need: `title`, `date`, `slug`. Anything that breaks parsing
// makes the entry fall out of the sidebar — silent but safe.
//
// i18n: each locale has its own news directory (root → /news/, en → /en/news/).
// The slug is shared across locales so the URL segments line up
// (/news/agent-online/ vs /en/news/agent-online/).
// -----------------------------------------------------------------------------

interface NewsEntryMeta {
  title: string
  date: string
  slug: string
}

function parseFrontmatter(source: string): Record<string, string> {
  const out: Record<string, string> = {}
  const m = source.match(/^---\n([\s\S]*?)\n---/)
  if (!m) return out
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([A-Za-z_]+):\s*(.*)$/)
    if (!kv) continue
    let value = kv[2].trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }
    out[kv[1]] = value
  }
  return out
}

function loadNewsEntries(subdir: 'news' | 'en/news'): NewsEntryMeta[] {
  const dir = join(__dirname, '..', subdir)
  let files: string[]
  try {
    files = readdirSync(dir).filter(
      (f) => f.endsWith('.md') && f !== 'index.md' && f !== 'README.md'
    )
  } catch {
    return []
  }
  const entries: NewsEntryMeta[] = []
  for (const f of files) {
    const fm = parseFrontmatter(readFileSync(join(dir, f), 'utf-8'))
    if (!fm.title || !fm.date || !fm.slug) continue
    entries.push({ title: fm.title, date: fm.date, slug: fm.slug })
  }
  // Newest first
  entries.sort((a, b) => b.date.localeCompare(a.date))
  return entries
}

const zhNews = loadNewsEntries('news')
const enNews = loadNewsEntries('en/news')

// -----------------------------------------------------------------------------
// VitePress config
// -----------------------------------------------------------------------------

// Sidebar entries for plugin doc sections (only zh-CN has these today; en
// users on those paths will 404 until those docs are translated — out of
// scope for the /news/ pilot).
const pluginSidebars = {
  '/llm-dynamic-ui/': [
    {
      text: 'LLM Dynamic UI',
      items: [
        { text: 'Overview', link: '/llm-dynamic-ui/' },
        { text: 'Getting Started', link: '/llm-dynamic-ui/getting-started' },
        { text: 'Widget Types', link: '/llm-dynamic-ui/widget-types' },
        { text: 'Animation', link: '/llm-dynamic-ui/animation' },
        { text: 'SDF Effects', link: '/llm-dynamic-ui/sdf-effects' }
      ]
    }
  ],
  '/llm-material/': [
    {
      text: 'LLM Material',
      items: [
        { text: 'Overview', link: '/llm-material/' },
        { text: 'Getting Started', link: '/llm-material/getting-started' },
        { text: 'Node Types', link: '/llm-material/node-types' },
        { text: 'Substrate', link: '/llm-material/substrate' },
        { text: 'Layout', link: '/llm-material/layout' },
        { text: 'USH', link: '/llm-material/ush' },
        { text: 'Examples', link: '/llm-material/examples' }
      ]
    }
  ],
  '/llm-statetree/': [
    {
      text: 'LLM StateTree',
      items: [
        { text: 'Overview', link: '/llm-statetree/' },
        { text: 'Getting Started', link: '/llm-statetree/getting-started' },
        { text: 'Node Types', link: '/llm-statetree/node-types' },
        { text: 'Examples', link: '/llm-statetree/examples' }
      ]
    }
  ],
  '/llm-metasound/': [
    {
      text: 'LLM MetaSound',
      items: [
        { text: 'Overview', link: '/llm-metasound/' },
        { text: 'Getting Started', link: '/llm-metasound/getting-started' },
        { text: 'Node Types', link: '/llm-metasound/node-types' },
        { text: 'Examples', link: '/llm-metasound/examples' }
      ]
    }
  ],
  '/llm-easy-shell/': [
    {
      text: 'LLM Easy Shell',
      items: [
        { text: 'Overview', link: '/llm-easy-shell/' },
        { text: 'LLM Easy Shell Lite', link: '/llm-easy-shell-lite/' }
      ]
    }
  ],
  '/llm-easy-shell-lite/': [
    {
      text: 'LLM Easy Shell Lite',
      items: [
        { text: 'Overview', link: '/llm-easy-shell-lite/' },
        { text: 'LLM Easy Shell (full)', link: '/llm-easy-shell/' }
      ]
    }
  ],
  '/skills/': [
    {
      text: 'AI Agent Skills',
      items: [
        { text: 'Overview', link: '/skills/' },
        { text: 'Installation', link: '/skills/installation' },
        { text: 'LLM Dynamic UI', link: '/skills/llm-dynamic-ui' },
        { text: 'LLM Material', link: '/skills/llm-material' },
        { text: 'LLM StateTree', link: '/skills/llm-statetree' },
        { text: 'LLM MetaSound', link: '/skills/llm-metasound' },
        { text: 'LLM Easy Shell', link: '/skills/llm-easy-shell' },
        { text: 'LLM Easy Shell Lite', link: '/skills/llm-easy-shell-lite' }
      ]
    }
  ]
}

const mainNav = [
  { text: 'LLM Dynamic UI', link: '/llm-dynamic-ui/' },
  { text: 'LLM Material', link: '/llm-material/' },
  { text: 'LLM StateTree', link: '/llm-statetree/' },
  { text: 'LLM MetaSound', link: '/llm-metasound/' },
  { text: 'LLM Easy Shell', link: '/llm-easy-shell/' },
  { text: 'AI Agent Skills', link: '/skills/' },
  { text: 'News', link: '/news/' }
]

// Per-locale news sidebar: dynamic list driven by loadNewsEntries().
function newsSidebar(prefix: '/news/' | '/en/news/', entries: NewsEntryMeta[]) {
  return {
    [prefix]: [
      {
        text: 'News',
        items: [
          { text: 'All updates', link: prefix },
          ...entries.map((entry) => ({
            text: entry.title,
            link: `${prefix}${entry.slug}/`
          }))
        ]
      }
    ]
  }
}

export default defineConfig({
  title: 'YominUnreal Plugins',
  description: 'AI-powered Unreal Engine development tools — UI, Material, VFX, AI',
  cleanUrls: true,
  srcDir: '.',
  base: '/Yomin-Fab-LLM-Unreal-Plugin/',

  // Internal brainstorming / planning artifacts — not user-facing docs.
  // They contain example dev-server URLs and don't need to render as pages.
  srcExclude: ['**/superpowers/**'],

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'YominUnreal Plugins',

    socialLinks: [
      { icon: 'github', link: 'https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin' }
    ],

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },

    footer: {
      message: 'Powered by VitePress',
      copyright: 'Copyright © 2026 Yiming Wang &lt;yomin_noahwang@foxmail.com&gt;. All rights reserved.'
    }
  },

  // i18n. Root locale (zh-CN) keeps every existing path; English lives
  // under /en/. The /news/ section is fully bilingual; plugin docs are
  // not yet translated and will 404 on the en site until they are.
  locales: {
    root: {
      label: '中文',
      lang: 'zh-CN',
      themeConfig: {
        nav: mainNav,
        sidebar: {
          ...pluginSidebars,
          ...newsSidebar('/news/', zhNews)
        }
      }
    },
    en: {
      label: 'English',
      lang: 'en-US',
      // No `link` override: the en home is /en/ (created as docs/en/index.md),
      // and that's where both the language switcher and the top-left logo
      // should land. Setting link to '/en/news/' would push the logo to
      // /en/news/, which is not what "back to home" means.
      themeConfig: {
        nav: mainNav,
        sidebar: {
          ...newsSidebar('/en/news/', enNews)
        }
      }
    }
  }
})
