# YominUnreal Plugins

> **AI-powered Unreal Engine development tools.**
> Define your intent in JSON — the plugin turns it into a real engine asset.

<p align="center">
  <img src="https://img.shields.io/badge/YominUnreal%20Plugins-UMG%20%C2%B7%20Material%20%C2%B7%20StateTree%20%C2%B7%20MetaSound-0d6efd?style=for-the-badge&logo=unrealengine&logoColor=white" alt="YominUnreal Plugins — UMG · Material · StateTree · MetaSound"/>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.7%2B-blue.svg)](https://www.unrealengine.com/)
[![Available on Fab](https://img.shields.io/badge/Available%20on-Epic%20Fab-8a3ffc.svg)](https://www.fab.com/listings/d84f1501-b45a-49c2-8069-40132482d0fd)
[![Docs](https://img.shields.io/badge/Docs-VitePress-success.svg)](https://ituiyuio.github.io/Yomin-Fab-LLM-Unreal-Plugin/)

YominUnreal is a suite of four **DSL-driven** Unreal Engine 5 editor plugins. Each one reads a focused JSON dialect and compiles it into a real engine asset — **UMG Widget, Material, StateTree, or MetaSound** — so you (or your LLM copilot) can author complex UE5 content from text instead of clicking through graph editors.

Built for **AI-assisted workflows** and **rapid iteration**. Compose, don't subclass. Round-trip from graph editor back to JSON anytime.

---

## 🎮 Get It On Fab

Three plugins are published on **Epic Fab** — the official Unreal Engine marketplace.

| Plugin | Fab Listing |
|--------|-------------|
| **LLM Dynamic UI** | [View on Fab →](https://www.fab.com/listings/d84f1501-b45a-49c2-8069-40132482d0fd) |
| **LLM Material**   | [View on Fab →](https://www.fab.com/listings/501c1599-bf89-4b61-8037-14ef2fab0728) |
| **LLM StateTree**  | [View on Fab →](https://www.fab.com/listings/0e19efd3-6898-4d0f-b7de-5e9fb9a32951) |

*LLM MetaSound is currently distributed through this repository only — Fab listing coming soon.*

---

## The Four Plugins

| | Plugin | What It Makes | Highlights |
|---|--------|---------------|------------|
| 🎨 | **LLM Dynamic UI** | UMG Widget Blueprints | Full UMG + CommonUI, layout / animation / SDF effects |
| 🎭 | **LLM Material**   | Material assets | Expression graph, UE5 **Substrate**, inline `.ush` HLSL |
| 🌲 | **LLM StateTree**  | StateTree AI assets | Tasks, conditions, Utility-AI considerations, parameter binding |
| 🔊 | **LLM MetaSound**  | `UMetaSoundSource` / `UMetaSoundPatch` | Generators, filters, envelopes, mixers, bus IO |

Every plugin ships with:
- A **documented DSL** (`.llmui` / `.llmmat` / `.llmstate` / `.llmmetasound`)
- A **JSON ↔ asset round-trip** in the editor panel
- A **schema file** for LLM tool-use and validation

---

## Why YominUnreal?

| | |
|---|---|
| 🤖 **LLM-Native**<br>Structured text is what models produce — no editor scraping | 🔀 **Diffable**<br>Your UMG, Material, AI, audio lives in version control |
| 🧩 **Composable**<br>Combine nodes, don't subclass | 🔄 **Round-Trip**<br>Export any asset back to JSON to iterate with an AI assistant |

---

## See It In Action

A `.llmui` login panel → a real UMG Widget Blueprint:

```json
{
  "version": "2.0",
  "name": "LoginScreen",
  "parentClass": "CommonActivatableWidget",
  "rootWidget": {
    "id": "root",
    "type": "VerticalBox",
    "children": [
      { "id": "title", "type": "Text",
        "style": { "fontSize": 28, "fontWeight": "Bold", "color": "#FFD84D" },
        "content": { "text": "Welcome Back" } },
      { "id": "loginBtn", "type": "Button",
        "style": { "normalColor": "#1a66cc", "hoveredColor": "#3388ff", "cornerRadius": 8 },
        "content": { "text": "Login" },
        "events": { "onClick": "OnLoginClicked" } }
    ]
  }
}
```

One click in the editor panel — and the Widget Blueprint is on disk. The other three plugins work exactly the same way.

---

## 📚 Documentation

Full guides, schema references and example projects:

**🌐 https://ituiyuio.github.io/Yomin-Fab-LLM-Unreal-Plugin/**

| | |
|---|---|
| 🎨 **LLM Dynamic UI**<br>UMG Widgets from JSON | 🎭 **LLM Material**<br>Materials from JSON |
| [Get Started →](./docs/llm-dynamic-ui/getting-started.md) | [Get Started →](./docs/llm-material/getting-started.md) |
| 🌲 **LLM StateTree**<br>AI behavior from JSON | 🔊 **LLM MetaSound**<br>Audio graphs from JSON |
| [Get Started →](./docs/llm-statetree/getting-started.md) | [Get Started →](./docs/llm-metasound/getting-started.md) |

---

## License

[MIT](./LICENSE) © 2026 Yiming Wang &lt;yomin_noahwang@foxmail.com&gt;
