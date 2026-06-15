import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'YominUnreal Plugins',
  description: 'AI-powered Unreal Engine development tools — UI, Material, VFX, AI',
  lang: 'zh-CN',
  cleanUrls: true,
  srcDir: '.',
  base: '/Yomin-Fab-LLM-Unreal-Plugin/',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ],

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'YominUnreal Plugins',

    nav: [
      { text: 'LLM Dynamic UI', link: '/llm-dynamic-ui/' },
      { text: 'LLM Material', link: '/llm-material/' },
      { text: 'LLM StateTree', link: '/llm-statetree/' },
      { text: 'LLM MetaSound', link: '/llm-metasound/' },
      { text: 'AI Agent Skills', link: '/skills/' }
    ],

    sidebar: {
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
    },

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
  }
})
