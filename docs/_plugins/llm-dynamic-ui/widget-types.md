---
layout: default
title: Widget Types
parent: LLM Dynamic UI
nav_order: 2
---

# Widget Types

## Layout Containers

| DSL Type | UE Class | Description |
|----------|----------|-------------|
| `VerticalBox` | UVerticalBox | Vertical stacking of children |
| `HorizontalBox` | UHorizontalBox | Horizontal arrangement of children |
| `Canvas` / `CanvasPanel` | UCanvasPanel | Absolute positioning with anchors |
| `Overlay` | UOverlay | Layered stacking (z-order) |
| `Border` | UBorder | Container with background/border |
| `ScrollBox` | UScrollBox | Scrollable container |
| `SizeBox` | USizeBox | Fixed-size container |
| `ScaleBox` | UScaleBox | Scaled-to-fit container |
| `WrapBox` | UWrapBox | Auto-wrapping layout |
| `GridPanel` | UGridPanel | Grid-based layout |
| `UniformGridPanel` | UUniformGridPanel | Uniform grid |
| `WidgetSwitcher` | UWidgetSwitcher | Tab-style child switching |

## Leaf Widgets

| DSL Type | UE Class | Description |
|----------|----------|-------------|
| `Text` | UTextBlock | Text display |
| `Button` | UButton | Clickable button |
| `Image` | UImage | Image display |
| `InputField` / `EditableText` | UEditableText | Text input |
| `ProgressBar` | UProgressBar | Progress indicator |
| `Slider` | USlider | Value slider |
| `CheckBox` | UCheckBox | Checkbox toggle |
| `ComboBox` | UComboBoxString | Dropdown selector |
| `Spacer` | USpacer | Empty space |
| `ListView` | UListView | Scrollable list |
| `TreeView` | UTreeView | Hierarchical tree |

## Effects Widgets

| DSL Type | UE Class | Description |
|----------|----------|-------------|
| `SDFBox` | USDFBoxWidgetPure | SDF visual effects container |
| `BackgroundBlur` | UBackgroundBlur | Gaussian blur backdrop |

## CommonUI Widgets

| DSL Type | UE Class | Description |
|----------|----------|-------------|
| `CommonButton` | UCommonButton | CommonUI button with input actions |
| `CommonText` | UCommonText | CommonUI styled text |
| `CommonBorder` | UCommonBorder | CommonUI styled border |
| `CommonImage` | UCommonImage | CommonUI styled image |

> CommonUI widgets are automatically used when `parentClass` is set to a CommonUI class (e.g., `CommonActivatableWidget`).

---

## Color Formats

| Format | Example |
|--------|---------|
| Hex 6-digit | `"#FF8800"` |
| Hex 8-digit (alpha) | `"#FF880088"` |
| Hex 3-digit short | `"#F80"` |
| RGB | `"rgb(255, 136, 0)"` |
| RGBA | `"rgba(255, 136, 0, 0.8)"` |
| Named colors | `"white"`, `"black"`, `"red"`, `"green"`, `"blue"`, `"yellow"`, `"cyan"`, `"magenta"`, `"orange"`, `"gray"`, `"transparent"` |

---

## Slot Properties

### Box Slots (VerticalBox / HorizontalBox)

```json
"slot": {
  "padding": { "left": 10, "top": 5, "right": 10, "bottom": 5 },
  "fill": 1.0,
  "size": { "width": 100, "height": 45 },
  "hAlignment": "Center",
  "vAlignment": "Center"
}
```

- **padding** — Inner margin (FMargin)
- **fill** — Fill weight (0 = auto, >0 = proportional)
- **size** — Fixed pixel dimensions (mutually exclusive with fill)
- **hAlignment** — `"Left"` | `"Center"` | `"Right"` | `"Fill"`
- **vAlignment** — `"Top"` | `"Center"` | `"Bottom"` | `"Fill"`

### Canvas Slot (absolute positioning)

```json
"slot": {
  "anchors": {
    "minimum": { "x": 0.5, "y": 0.5 },
    "maximum": { "x": 0.5, "y": 0.5 }
  },
  "offsets": { "left": -100, "top": -50, "right": 100, "bottom": 50 },
  "alignment": { "x": 0.5, "y": 0.5 },
  "zOrder": 0
}
```

- **Point Anchor** (`minimum = maximum`) — Position relative to a single anchor point
- **Stretch Anchor** (`minimum ≠ maximum`) — Widget stretches between two anchor corners
