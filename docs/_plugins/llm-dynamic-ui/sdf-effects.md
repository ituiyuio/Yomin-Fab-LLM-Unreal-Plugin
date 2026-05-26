---
layout: default
title: SDF Effects
parent: LLM Dynamic UI
nav_order: 4
---

# SDF Visual Effects

SDFBox is a special container widget that renders visual effects using Signed Distance Fields (SDF). It can contain a single child widget and applies effects like shadows, glow, borders, and gradients.

## Basic SDFBox

```json
{
  "id": "card",
  "type": "SDFBox",
  "sdf": {
    "shape": { "size": { "width": 300, "height": 200 }, "cornerRadius": 16 },
    "fill": { "type": "Solid", "color": { "r": 0.1, "g": 0.1, "b": 0.15, "a": 0.9 } },
    "border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.1 } }
  },
  "children": [
    {
      "type": "VerticalBox",
      "children": [
        { "type": "Text", "content": { "text": "Title" } },
        { "type": "Text", "content": { "text": "Description" } }
      ]
    }
  ]
}
```

---

## SDF Properties

### Shape

```json
"shape": { "size": { "width": 300, "height": 200 }, "cornerRadius": 16 }
```

- **size.width / size.height** — Pixel dimensions (auto-sized if omitted)
- **cornerRadius** — Rounded corner radius in pixels

### Fill

**Solid:**
```json
"fill": { "type": "Solid", "color": { "r": 0.1, "g": 0.1, "b": 0.15, "a": 0.9 } }
```

**Gradient:**
```json
"fill": {
  "type": "Gradient",
  "startColor": { "r": 0.1, "g": 0.1, "b": 0.2, "a": 1.0 },
  "endColor": { "r": 0.2, "g": 0.1, "b": 0.3, "a": 1.0 },
  "angle": 90
}
```

### Shadow

```json
"shadow": { "offset": { "x": 0, "y": 8 }, "blur": 20, "color": { "r": 0, "g": 0, "b": 0, "a": 0.4 } }
```

### Glow

```json
"glow": { "radius": 16, "intensity": 0.8, "color": { "r": 0.3, "g": 0.5, "b": 1.0, "a": 0.6 } }
```

### Border

```json
"border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.1 } }
```

### Padding

```json
"padding": { "left": 20, "top": 20, "right": 20, "bottom": 20 }
```

Inner padding for the child widget inside the SDF box.

---

## Backdrop Blur (Glassmorphism)

SDFBox supports `backdropBlur` to achieve visionOS Liquid Glass style effects:

```json
{
  "id": "glassPanel",
  "type": "SDFBox",
  "sdf": {
    "shape": { "size": { "width": 300, "height": 200 }, "cornerRadius": 16 },
    "fill": { "type": "Solid", "color": { "r": 1, "g": 1, "b": 1, "a": 0.08 } },
    "border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.18 } },
    "shadow": { "offset": { "x": 0, "y": 8 }, "blur": 32, "color": { "r": 0, "g": 0, "b": 0, "a": 0.18 } },
    "backdropBlur": { "enabled": true, "strength": 64, "saturation": 2.0 }
  }
}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | false | Enable/disable blur |
| `strength` | float | 64 | Blur radius (0-100) |
| `saturation` | float | 1.0 | Saturation multiplier |

### Presets

| Preset | Strength | Saturation | Use Case |
|--------|----------|------------|---------|
| `Glass(64)` | 64 | 1.0 | visionOS default glass |
| `Subtle(32)` | 32 | 1.0 | Subtle blur |
| `Frosted(80)` | 80 | 1.5 | Heavy frosted glass |

---

## Complete Example: Login Card

```json
{
  "name": "LoginCard",
  "rootWidget": {
    "type": "SDFBox",
    "sdf": {
      "shape": { "size": { "width": 360, "height": 280 }, "cornerRadius": 20 },
      "fill": { "type": "Solid", "color": { "r": 0.08, "g": 0.08, "b": 0.12, "a": 0.95 } },
      "shadow": { "offset": { "x": 0, "y": 12 }, "blur": 40, "color": { "r": 0, "g": 0, "b": 0, "a": 0.5 } },
      "border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.08 } },
      "backdropBlur": { "enabled": true, "strength": 48 },
      "padding": { "left": 30, "top": 30, "right": 30, "bottom": 30 }
    },
    "children": [
      {
        "type": "VerticalBox",
        "children": [
          { "type": "Text", "content": { "text": "Sign In", "justification": "Center" }, "style": { "fontSize": 24, "fontWeight": "Bold", "color": "#FFFFFF" } },
          { "slot": { "size": { "height": 20 } } },
          { "type": "InputField", "content": { "placeholder": "Email" }, "slot": { "size": { "height": 40 } } },
          { "slot": { "size": { "height": 12 } } },
          { "type": "InputField", "content": { "placeholder": "Password", "isPassword": true }, "slot": { "size": { "height": 40 } } },
          { "slot": { "size": { "height": 24 } } },
          { "type": "Button", "content": { "text": "Login" }, "style": { "normalColor": "#4A9EFF", "cornerRadius": 8 }, "slot": { "size": { "height": 44 } } }
        ]
      }
    ]
  }
}
```
