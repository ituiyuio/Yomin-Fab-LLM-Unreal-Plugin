---
layout: default
title: Animation System
parent: LLM Dynamic UI
nav_order: 3
---

# Animation System

## Basic Format

Animations are defined directly in the `.llmui` widget definition:

```json
"animations": [
  {
    "name": "fadeIn",
    "property": "RenderOpacity",
    "fromValue": 0,
    "toValue": 1,
    "duration": 0.5,
    "easing": "EaseOut",
    "autoPlay": true
  }
]
```

---

## Animation Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Unique name for this animation |
| `property` | string | Property to animate |
| `fromValue` / `toValue` | float | Start and end values |
| `fromVector` / `toVector` | Vector2D | For 2D properties |
| `fromColor` / `toColor` | Color | For color properties |
| `duration` | float | Duration in seconds |
| `delay` | float | Delay before starting |
| `easing` | string | Easing function name |
| `loop` | int | Number of loops (-1 = infinite, 1 = once) |
| `autoPlay` | bool | Start automatically on spawn |
| `keyframes` | array | Keyframe array (overrides from/to) |

### Keyframe Format

```json
{
  "name": "bounce",
  "property": "RenderScale",
  "keyframes": [
    { "time": 0,   "value": { "x": 1.0, "y": 1.0 } },
    { "time": 0.1, "value": { "x": 1.2, "y": 1.2 } },
    { "time": 0.2, "value": { "x": 0.9, "y": 0.9 } },
    { "time": 0.4, "value": { "x": 1.0, "y": 1.0 } }
  ],
  "duration": 0.4,
  "easing": "OutBack"
}
```

---

## Animatable Properties

| Property Name | Value Type | Description |
|---------------|------------|-------------|
| `RenderOpacity` | Float (0-1) | Transparency |
| `RenderTranslation` | Vector2D | Position offset (X, Y) |
| `RenderScale` | Vector2D | Scale factor (X, Y) |
| `RenderRotation` | Float | Rotation angle in degrees |
| `BackgroundColor` | Color | Background tint (Border/Button) |
| `TintColor` / `ColorAndOpacity` | Color | Tint for Image widgets |
| `WidgetWidth` | Float | Width in pixels |
| `WidgetHeight` | Float | Height in pixels |
| `FillColorAndOpacity` | Color | Fill color for ProgressBar |
| `Percent` | Float | Progress value (0-1) for ProgressBar |
| `SliderValue` | Float | Slider position (0-1) |

---

## Easing Functions

| Category | Functions |
|----------|-----------|
| Basic | `Linear`, `EaseIn`, `EaseOut`, `EaseInOut` |
| Quadratic | `InQuad`, `OutQuad`, `InOutQuad` |
| Cubic | `InCubic`, `OutCubic`, `InOutCubic` |
| Sine | `InSine`, `OutSine`, `InOutSine` |
| Exponential | `InExpo`, `OutExpo`, `InOutExpo` |
| Elastic | `InElastic`, `OutElastic` |
| Bounce | `InBounce`, `OutBounce` |
| Back | `InBack`, `OutBack` |

---

## Examples

### Fade In

```json
{ "name": "fadeIn", "property": "RenderOpacity", "fromValue": 0, "toValue": 1, "duration": 0.5, "easing": "EaseOut", "autoPlay": true }
```

### Slide In from Left

```json
{ "name": "slideIn", "property": "RenderTranslation", "fromVector": { "x": -100, "y": 0 }, "toVector": { "x": 0, "y": 0 }, "duration": 0.3, "easing": "OutQuad" }
```

### Color Pulse (infinite loop)

```json
{ "name": "colorPulse", "property": "BackgroundColor", "fromColor": { "R": 0.2, "G": 0.5, "B": 0.8, "A": 1 }, "toColor": { "R": 0.4, "G": 0.7, "B": 1.0, "A": 1 }, "duration": 1.5, "easing": "InOutSine", "loop": -1, "autoPlay": true }
```

### Infinite Bounce Scale

```json
{ "name": "bounceScale", "property": "RenderScale", "fromVector": { "x": 1.0, "y": 1.0 }, "toVector": { "x": 1.05, "y": 1.05 }, "duration": 0.8, "easing": "InOutSine", "loop": -1 }
```
