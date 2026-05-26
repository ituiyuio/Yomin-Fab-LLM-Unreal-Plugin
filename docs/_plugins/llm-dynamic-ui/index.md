---
layout: default
title: LLM Dynamic UI
has_children: true
nav_order: 1
---

# LLM Dynamic UI

DSL-Driven UMG Widget Generation System for Unreal Engine 5.

Generate complete UMG Widget Blueprints from JSON (`.llmui` files) with layout, animations, and SDF visual effects — no manual editor work required.

---

## Features

- **One JSON, Complete UI** — Layout, widgets, and animations generated from a single `.llmui` file
- **LLM-First Design** — AI outputs JSON directly, no UE editor knowledge required
- **Bidirectional Conversion** — JSON → UMG Blueprint, UMG Blueprint → JSON, perfect roundtrip
- **CommonUI Deep Integration** — Auto-generates style assets (CommonTextStyle, CommonButtonStyle)
- **Animation System** — Property animations with 15+ easing functions (Linear, Quad, Cubic, Elastic, Bounce, Back)
- **Loop & AutoPlay** — Infinite loops, ping-pong (yoyo) mode, auto-start on spawn
- **24 Widget Types** — VerticalBox, HorizontalBox, Canvas, Overlay, ScrollBox, Text, Image, Button, and more
- **JSON Schema Driven** — Recursive property discovery, 50+ properties auto-parsed
- **Editor Panel** — Import `.llmui` files, preview widget tree, batch generate
- **Full Compatibility** — Works with CommonActivatableWidget, CommonUserWidget, UserWidget

---

## Quick Start

1. Menu → Tools → **LLM Dynamic UI Panel**
2. Paste `.llmui` JSON or import a `.llmui` file
3. Click **Generate UMG Widget**
4. The generated Widget Blueprint opens automatically

```json
{
  "version": "2.0",
  "name": "LoginScreen",
  "rootWidget": {
    "id": "root",
    "type": "VerticalBox",
    "children": [
      {
        "type": "Text",
        "style": { "fontSize": 28, "fontWeight": "Bold", "color": "#FFD84D" },
        "content": { "text": "Welcome Back" }
      },
      {
        "type": "Button",
        "style": { "normalColor": "#1a66cc", "cornerRadius": 8 },
        "content": { "text": "Login" },
        "events": { "onClick": "OnLoginClicked" }
      }
    ]
  }
}
```

---

## Version Info

| Item | Value |
|------|-------|
| Plugin Version | 1.0.0 |
| Engine | UE 5.7+ |
| Modules | LLMDynamicUI (Runtime), LLMDynamicUIEditor (Editor) |
| Publisher | YominUnreal |
