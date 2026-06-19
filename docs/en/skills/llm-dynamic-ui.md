---
outline: [2, 3]
---

# LLM Dynamic UI

DSL-driven UMG Widget generation for Unreal Engine 5. The agent writes `.llmui` JSON, the editor turns it into a real `UWidgetBlueprint` — full UMG + CommonUI, layout, animations, and SDF effects.

> **Skill file:** [`skills/llm-dynamic-ui/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-dynamic-ui/SKILL.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Create or design a UE5 UMG interface (login page, menu, HUD, dialog, settings, etc.)
- Convert an interface description into a `.llmui` file
- Inspect or modify an existing `.llmui` file
- Look up a UMG widget type, layout container, or animatable property
- Add an animation track (position, color, opacity, scale) to a widget

**Triggers:** `.llmui`, UMG, UMG widget, Widget Blueprint, UI, HUD, menu, login, dialog, animation, fade, slide, SDF, CommonUI, CommonButton, CommonText.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM Dynamic UI** plugin | Install from Fab or copy from this repo to `Plugins/` |
| Enabled in editor | Edit → Plugins → AI → **LLM Dynamic UI** → restart editor |

The agent does not need the editor running to *write* the JSON — it just writes the file. You open the editor and click **Generate** to compile it into a Widget Blueprint.

---

## Quick Example

Ask the agent:

> "Make me a login screen with a title and a CommonUI login button."

The agent produces a `.llmui` file:

```json
{
  "version": "2.0",
  "name": "LoginScreen",
  "parentClass": "CommonActivatableWidget",
  "rootWidget": {
    "id": "root",
    "type": "VerticalBox",
    "children": [
      {
        "id": "title",
        "type": "Text",
        "style": { "fontSize": 28, "fontWeight": "Bold", "color": "#FFD84D" },
        "content": { "text": "Welcome Back" }
      },
      {
        "id": "loginBtn",
        "type": "Button",
        "style": {
          "normalColor": "#1a66cc",
          "hoveredColor": "#3388ff",
          "cornerRadius": 8
        },
        "content": { "text": "Login" },
        "events": { "onClick": "OnLoginClicked" }
      }
    ]
  }
}
```

Save it, open the LLM Dynamic UI panel in the editor, click **Generate UMG Widget** — done.

---

## What the Skill Knows

The full skill body contains:

- **Color formats** — hex, rgb(), rgba(), named
- **All widget types** — VerticalBox, HorizontalBox, Canvas, Overlay, ScrollBox, Text, Image, Button, ProgressBar, Slider, CheckBox, etc.
- **CommonUI types** — CommonButton, CommonText, CommonActivatableWidget
- **Layout system** — anchors, alignment, padding, slot properties
- **Animation system** — 15+ easing functions, loops, ping-pong, autoplay
- **SDF effects** — shadows, glows, borders, gradients (single-pass)
- **Property schema** — points to `PropertySchema.llmschema` for full reference

You do not need to memorize any of it. The agent reads the skill, then writes the file.

---

## Compiling the JSON into an Asset

The agent writes the file. To turn the file into a Widget Blueprint, you (or the agent, if you also have **llm-easy-shell** installed) run:

```
# Option A — manual: editor panel
Tools → LLM Dynamic UI Panel → select .llmui file → Generate UMG Widget

# Option B — CLI: via the running editor
ui generate /Game/UI/LoginScreen --from LoginScreen.llmui
```

The Widget Blueprint is created at the path you specified and opens in the UMG editor, where you can make further adjustments by hand.

---

## Round-Trip

Already have a Widget Blueprint you want to author against with the agent? Use the editor panel's **Export to JSON** button to dump the current state back to a `.llmui` file. The agent can then edit that file and you re-generate.

---

## Related Skills

- [**llm-easy-shell** →](./llm-easy-shell) — drive the editor from the CLI: run `ui generate` for you, take a screenshot of the result, etc.
- [**llm-easy-shell-lite** →](./llm-easy-shell-lite) — read-only subset; safe for "show me what the UI looks like right now" without risking writes.
