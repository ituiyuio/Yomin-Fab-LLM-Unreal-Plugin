import { defineConfig, type SidebarItem } from 'vitepress'
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

// Sidebar entries for plugin doc sections.
//
// Two parallel maps: zhPluginSidebars for the root locale, enPluginSidebars
// for the English locale. Each is wired into the matching locale below.
// en entries are added incrementally as the matching English content ships.
const zhPluginSidebars: Record<string, SidebarItem[]> = {
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

// en locale plugin/skill sidebars.
//
// Filled in incrementally as English pages ship (mirrors zhPluginSidebars
// but with /en/... links). Each entry is a copy-paste of the zh entry with
// the link prefix swapped — keep them in sync.
const enPluginSidebars: Record<string, SidebarItem[]> = {
  '/en/llm-dynamic-ui/': [
    {
      text: 'LLM Dynamic UI',
      items: [
        { text: 'Overview', link: '/en/llm-dynamic-ui/' },
        { text: 'Getting Started', link: '/en/llm-dynamic-ui/getting-started' },
        { text: 'Widget Types', link: '/en/llm-dynamic-ui/widget-types' },
        { text: 'Animation', link: '/en/llm-dynamic-ui/animation' },
        { text: 'SDF Effects', link: '/en/llm-dynamic-ui/sdf-effects' }
      ]
    }
  ],
  '/en/llm-material/': [
    {
      text: 'LLM Material',
      items: [
        { text: 'Overview', link: '/en/llm-material/' },
        { text: 'Getting Started', link: '/en/llm-material/getting-started' },
        { text: 'Node Types', link: '/en/llm-material/node-types' },
        { text: 'Substrate', link: '/en/llm-material/substrate' },
        { text: 'Layout', link: '/en/llm-material/layout' },
        { text: 'USH', link: '/en/llm-material/ush' },
        { text: 'Examples', link: '/en/llm-material/examples' }
      ]
    }
  ],
  '/en/llm-statetree/': [
    {
      text: 'LLM StateTree',
      items: [
        { text: 'Overview', link: '/en/llm-statetree/' },
        { text: 'Getting Started', link: '/en/llm-statetree/getting-started' },
        { text: 'Node Types', link: '/en/llm-statetree/node-types' },
        { text: 'Examples', link: '/en/llm-statetree/examples' }
      ]
    }
  ],
  '/en/llm-metasound/': [
    {
      text: 'LLM MetaSound',
      items: [
        { text: 'Overview', link: '/en/llm-metasound/' },
        { text: 'Getting Started', link: '/en/llm-metasound/getting-started' },
        { text: 'Node Types', link: '/en/llm-metasound/node-types' },
        { text: 'Examples', link: '/en/llm-metasound/examples' }
      ]
    }
  ],
  '/en/llm-easy-shell/': [
    {
      text: 'LLM Easy Shell',
      items: [
        { text: 'Overview', link: '/en/llm-easy-shell/' },
        { text: 'LLM Easy Shell Lite', link: '/en/llm-easy-shell-lite/' }
      ]
    }
  ],
  '/en/llm-easy-shell-lite/': [
    {
      text: 'LLM Easy Shell Lite',
      items: [
        { text: 'Overview', link: '/en/llm-easy-shell-lite/' },
        { text: 'LLM Easy Shell (full)', link: '/en/llm-easy-shell/' }
      ]
    }
  ],
  '/en/skills/': [
    {
      text: 'AI Agent Skills',
      items: [
        { text: 'Overview', link: '/en/skills/' },
        { text: 'Installation', link: '/en/skills/installation' },
        { text: 'LLM Dynamic UI', link: '/en/skills/llm-dynamic-ui' },
        { text: 'LLM Material', link: '/en/skills/llm-material' },
        { text: 'LLM StateTree', link: '/en/skills/llm-statetree' },
        { text: 'LLM MetaSound', link: '/en/skills/llm-metasound' },
        { text: 'LLM Easy Shell', link: '/en/skills/llm-easy-shell' },
        { text: 'LLM Easy Shell Lite', link: '/en/skills/llm-easy-shell-lite' }
      ]
    }
  ]
}

// zh-CN nav (root locale): full set of links, all pointing to /<path>/.
const zhNav = [
  { text: 'LLM Dynamic UI', link: '/llm-dynamic-ui/' },
  { text: 'LLM Material', link: '/llm-material/' },
  { text: 'LLM StateTree', link: '/llm-statetree/' },
  { text: 'LLM MetaSound', link: '/llm-metasound/' },
  { text: 'LLM Easy Shell', link: '/llm-easy-shell/' },
  { text: 'AI Agent Skills', link: '/skills/' },
  { text: 'News', link: '/news/' }
]

// en nav: links point to /en/... counterparts that exist under docs/en/.
//
// The en pages are file-by-file copies of the root pages (same English
// content; zh home and nav are translated, but plugin/Skills docs are
// authored in English). Keep these in sync with zhNav.
const enNav = [
  { text: 'LLM Dynamic UI', link: '/en/llm-dynamic-ui/' },
  { text: 'LLM Material', link: '/en/llm-material/' },
  { text: 'LLM StateTree', link: '/en/llm-statetree/' },
  { text: 'LLM MetaSound', link: '/en/llm-metasound/' },
  { text: 'LLM Easy Shell', link: '/en/llm-easy-shell/' },
  { text: 'AI Agent Skills', link: '/en/skills/' },
  { text: 'News', link: '/en/news/' }
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
  // Per-locale descriptions are set inside the `locales` block below —
  // keeping a top-level `description` here would force both locales to
  // share an English string in their <meta name="description"> tag.
  cleanUrls: true,
  srcDir: '.',
  base: '/Yomin-Fab-LLM-Unreal-Plugin/',

  // Internal brainstorming / planning artifacts — not user-facing docs.
  // They contain example dev-server URLs and don't need to render as pages.
  // We also exclude any README.md so maintainer-only notes (e.g.
  // docs/news/README.md, the tag vocabulary guide) don't ship to users.
  srcExclude: ['**/superpowers/**', '**/README.md'],

  // -----------------------------------------------------------------------
  // Auto language preference. GitHub Pages is static — there's no server to
  // read Accept-Language and 302. So we run a tiny inline script in <head>
  // before Vue hydrates:
  //
  //   - On a locale ROOT (e.g. /repo/ or /repo/en/): redirect based on
  //     localStorage preference, falling back to navigator.language.
  //   - On any other page under a locale: silently record the current
  //     locale as the user's preference, but do not redirect (avoids
  //     stealing the user away from a deep link).
  //
  // Once the user clicks the in-page language switcher, the SPA router
  // does NOT trigger this script, so the saved preference is only updated
  // by full page loads. That's the desired behavior — first-time visitors
  // get the right language, returning visitors get what they last visited.
  // -----------------------------------------------------------------------
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    // Inline (no `src`) so it runs before any external JS / before Vue
    // hydrates — no flash of the wrong language. Wrapped in try/catch so
    // a broken browser / blocked localStorage never bricks the site.
    [
      'script',
      {},
      `(function(){try{var K='vp-locale-pref';var B=${JSON.stringify('/Yomin-Fab-LLM-Unreal-Plugin/')};var p=location.pathname;var isRoot=p===B||p===B.replace(/\\/$/,'');var isEnRoot=p===B+'en/'||p===B+'en';var here=isRoot?'root':(isEnRoot?'en':null);if(here){var saved=null;try{saved=localStorage.getItem(K)}catch(e){}var want=(saved==='root'||saved==='en')?saved:((navigator.language||'').toLowerCase().indexOf('en')===0?'en':'root');if(want!==here){location.replace(want==='en'?B+'en/':B)}else{try{localStorage.setItem(K,here)}catch(e){}}}else if(p.indexOf(B+'en')===0){try{localStorage.setItem(K,'en')}catch(e){}}else if(p.indexOf(B)===0){try{localStorage.setItem(K,'root')}catch(e){}}}catch(e){}})();`
    ]
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
      description: 'AI 驱动的 Unreal Engine 开发工具 — UI、Material、VFX、AI',
      themeConfig: {
        nav: zhNav,
        sidebar: {
          ...zhPluginSidebars,
          ...newsSidebar('/news/', zhNews)
        }
      }
    },
    en: {
      label: 'English',
      lang: 'en-US',
      description: 'AI-powered Unreal Engine development tools — UI, Material, VFX, AI',
      // No `link` override: the en home is /en/ (created as docs/en/index.md),
      // and that's where both the language switcher and the top-left logo
      // should land. Setting link to '/en/news/' would push the logo to
      // /en/news/, which is not what "back to home" means.
      themeConfig: {
        nav: enNav,
        sidebar: {
          ...enPluginSidebars,
          ...newsSidebar('/en/news/', enNews)
        }
      }
    }
  }
})
