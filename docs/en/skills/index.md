---
outline: [2, 3]
---

# AI Agent Skills

Each YominUnreal plugin ships with a dedicated **AI agent skill** — a `SKILL.md` file that teaches any LLM-powered coding assistant the full DSL of that plugin. Point your agent at the right skill and it can author `.llmui` / `.llmmat` / `.llmstate` / `.llmmetasound` files, or drive the running UE editor through the LLMEasyShell CLI, without ever opening the graph editor.

---

## The Six Skills

### 🎨 Asset Authoring Skills (DSL Generation)

These skills teach the agent how to **write JSON files** for a specific asset type. The plugin in the editor turns that JSON into a real engine asset.

| | Skill | What it teaches | Source file |
|---|-------|-----------------|-------------|
| 🎨 | **llm-dynamic-ui**   | UMG Widget Blueprints from `.llmui` | [`skills/llm-dynamic-ui/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-dynamic-ui/SKILL.md) |
| 🎭 | **llm-material**     | Material assets from `.llmmat`         | [`skills/llm-material/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-material/SKILL.md) |
| 🌲 | **llm-statetree**    | StateTree AI from `.llmstate`           | [`skills/llm-statetree/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-statetree/SKILL.md) |
| 🔊 | **llm-metasound**    | MetaSound audio from `.llmmetasound`    | [`skills/llm-metasound/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-metasound/SKILL.md) |

### 🛠️ Editor Control Skills (Runtime Operation)

These skills teach the agent how to **drive a running UE editor** through the LLMEasyShell CLI — query scenes, modify actor properties, call blueprint functions, trigger Live Coding, take screenshots.

| | Skill | What it teaches | Source file |
|---|-------|-----------------|-------------|
| 🛠️ | **llm-easy-shell**     | Full read/write access — 27 native commands + 25+ Python sub-commands | [`skills/llm-easy-shell/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-easy-shell/SKILL.md) |
| 🛠️ | **llm-easy-shell-lite** | Read-only subset — 9 safe exploration commands | [`skills/llm-easy-shell-lite/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-easy-shell-lite/SKILL.md) |

---

## How a Skill Works

A `SKILL.md` is plain Markdown with two parts:

1. **YAML frontmatter** — `name` + `description` that the AI agent uses to decide *when* to load the skill (matched against the user's request).
2. **Markdown body** — the full DSL schema, supported nodes / widgets, authoring patterns, and command references.

When you ask the agent a question, it scans the frontmatter of all installed skills. If a skill's `description` matches your request, the agent loads the body and follows it. **No code is scraped from the editor, no graph screenshots are sent to the LLM** — the skill is the only source of truth.

---

## Where to Put Skills

Each AI tool has its own convention. See [Installation](./installation) for the exact path used by Claude Code, OpenCode, Cursor, Codex, and others.

The short version:

```
<your UE project>/                     # The folder containing your .uproject
├── MyProject.uproject
└── .claude/
    └── skills/
        ├── llm-dynamic-ui/
        │   └── SKILL.md
        ├── llm-material/
        │   └── SKILL.md
        ├── llm-statetree/
        │   └── SKILL.md
        ├── llm-metasound/
        │   └── SKILL.md
        ├── llm-easy-shell/
        │   └── SKILL.md
        └── llm-easy-shell-lite/
            └── SKILL.md
```

That is — drop the skill folder next to your `.uproject` and most tools will pick it up automatically.

---

## Per-Skill Usage

Once installed, see the per-skill pages for triggers, examples, and the exact command set:

- [LLM Dynamic UI →](./llm-dynamic-ui)
- [LLM Material →](./llm-material)
- [LLM StateTree →](./llm-statetree)
- [LLM MetaSound →](./llm-metasound)
- [LLM Easy Shell →](./llm-easy-shell)
- [LLM Easy Shell Lite →](./llm-easy-shell-lite)
