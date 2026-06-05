---
name: llm-dynamic-ui
description: |
  LLM Dynamic UI is a DSL-driven UE5 UMG interface generation system. Use this skill when users need to:
  (1) Create or design UE5 UMG interfaces (login pages, menus, HUDs, dialogs, etc.)
  (2) Convert interface descriptions into generatable DSL format
  (3) Understand or modify existing UI DSL definitions
  (4) Learn about supported Widget types, layout systems, and animation systems
  (5) Query animatable property lists and animation creation methods
---

# LLM Dynamic UI - DSL Schema Guide

### **Composition Over Inheritance**

## File Format

UI definition files use the `.llmui` extension (LLM UI DSL), formatted as JSON.

## Reference Files

**UMG Property Dictionary**: `Plugins/LLMDynamicUI/Content/Schemas/PropertySchema.llmschema` - Contains complete property definitions for all UMG Widgets

**CommonUI Schema**: `Plugins/LLMDynamicUI/Content/Schemas/CommonUISchema.llmschema` - CommonUI control definitions, supporting game menus, gamepad navigation, and InputAction binding

**Animation Property Dictionary**: `Plugins/LLMDynamicUI/Content/Schemas/AnimPropertySchema.llmschema` - Contains definitions for all animatable properties (Track types, value types, usage examples)

**SDF Effect Dictionary**: `Plugins/LLMDynamicUI/Content/Schemas/SDFSchema.llmschema` - Contains complete definitions for SDF visual effects (shadows, glows, borders, gradients)

**Samples Directory**: `Plugins/LLMDynamicUI/Content/Samples/` - Contains complete UI example `.llmui` files

## Quick Start

```json
{
  "version": "2.0",
  "name": "MyUI",
  "rootWidget": {
    "id": "root",
    "type": "VerticalBox",
    "children": [
      {
        "id": "titleText",
        "type": "Text",
        "style": {
          "fontSize": 24,
          "color": "white"
        },
        "content": { "text": "Hello World" }
      },
      {
        "id": "submitBtn",
        "type": "Button",
        "style": {
          "normalColor": "#1a66cc",
          "cornerRadius": 8
        },
        "content": { "text": "Submit" },
        "events": { "onClick": "OnSubmitClicked" }
      }
    ]
  }
}
```

## Color Formats

Multiple color formats are supported:

| Format | Example | Description |
|--------|---------|-------------|
| Hex 6-digit | `"#FF8800"` | RRGGBB |
| Hex 8-digit | `"#FF880088"` | RRGGBBAA (with alpha) |
| Hex 3-digit | `"#F80"` | RGB short format |
| RGB | `"rgb(255, 136, 0)"` | 0-255 range |
| RGBA | `"rgba(255, 136, 0, 0.8)"` | With alpha |
| Named | `"white"`, `"cyan"`, `"transparent"` | Named colors |

**Named Colors List**: `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `orange`, `gray`, `transparent`

## Simplified Style - Recommended

**Use inline styles directly on Widgets. The system automatically hashes and deduplicates to generate reusable Style assets:**

### CommonButton Inline Style
```json
{
  "type": "CommonButton",
  "buttonStyle": {
    "normalColor": "#1a66cc",
    "hoveredColor": "#3388ff",
    "pressedColor": "#0d4a99",
    "textColor": "#FFFFFF",
    "cornerRadius": 8
  },
  "content": { "text": "Click Me" }
}
```

### CommonText Inline Style
```json
{
  "type": "CommonText",
  "textStyle": {
    "fontSize": 32,
    "fontWeight": "Bold",
    "color": "#FF8800"
  },
  "content": { "text": "Title" }
}
```

### Standard Widget Style
```json
{
  "type": "Text",
  "style": {
    "fontSize": 32,
    "fontWeight": "Bold",
    "color": "#FF8800"
  }
}
```

**Text Style Properties**:
- `fontSize` - Font size
- `fontWeight` - Font weight: `"Light"`, `"Regular"`, `"Medium"`, `"Bold"`
- `fontFamily` - Font path
- `color` - Text color

**Button Style Properties**:
- `normalColor` - Normal state color
- `hoveredColor` - Hover state color
- `pressedColor` - Pressed state color
- `textColor` - Text color
- `cornerRadius` - Corner radius
- `minWidth` / `minHeight` - Minimum dimensions

**Auto-Deduplication Mechanism**: Identical style definitions automatically generate the same Style asset, no manual management needed.

## Widget Types

### Layout Containers
| Type | UE Class | Description |
|------|----------|-------------|
| `VerticalBox` | UVerticalBox | Arranges children vertically |
| `HorizontalBox` | UHorizontalBox | Arranges children horizontally |
| `Canvas` | UCanvasPanel | Absolute positioning with anchor support (alias: `CanvasPanel`) |
| `Overlay` | UOverlay | Stacked layout |
| `Border` | UBorder | Container with background |
| `ScrollBox` | UScrollBox | Scrollable container |
| `SizeBox` | USizeBox | Fixed-size container |
| `ScaleBox` | UScaleBox | Scaling container |
| `WrapBox` | UWrapBox | Auto-wrap layout |
| `GridPanel` | UGridPanel | Grid layout |
| `UniformGridPanel` | UUniformGridPanel | Uniform grid |
| `WidgetSwitcher` | UWidgetSwitcher | Switches between child widgets |

### Leaf Widgets
| Type | UE Class | Description |
|------|----------|-------------|
| `Text` | UTextBlock | Text display |
| `Button` | UButton | Button |
| `Image` | UImage | Image |
| `InputField` | UEditableText | Input field (alias: `EditableText`) |
| `ProgressBar` | UProgressBar | Progress bar |
| `Slider` | USlider | Slider |
| `CheckBox` | UCheckBox | Checkbox |
| `ComboBox` | UComboBoxString | Dropdown |
| `Spacer` | USpacer | Spacer |

### Effects Widgets
| Type | UE Class | Description |
|------|----------|-------------|
| `SDFBox` | USDFBoxWidgetPure | SDF effect container, supports shadow/glow/border/gradient, can contain a single child widget |

### CommonUI Widgets (requires CommonUI plugin)
| Type | UE Class | Description |
|------|----------|-------------|
| `CommonButton` | UCommonButton | CommonUI button, supports input actions |
| `CommonText` | UCommonText | CommonUI text, supports style assets |
| `CommonBorder` | UCommonBorder | CommonUI border, supports style assets |
| `CommonImage` | UCommonImage | CommonUI image |

## styleRef (Expert Mode)

> **Note**: Inline styles `buttonStyle`/`textStyle` are recommended. The following is only for referencing manually pre-created Style assets.

If you need to share a manually created Style asset across multiple UI files:

```json
{
  "id": "loginPanel",
  "type": "Border",
  "styleRef": "/Game/UI/Styles/PanelStyle",
  "children": [...]
}
```

**Applicable Scenarios:**
- Referencing manually created Style Blueprints by artists/designers
- Need to share styles across independent UI files

**Not Applicable:**
- LLM-generated UI (inline styles suffice)
- Reusing styles within the same file (auto-deduplication handles this)

## Configuration

Set generation configuration at the document root level:

```json
{
  "version": "2.0",
  "name": "MyUI",
  "config": {
    "bUseCommonUI": true,
    "commonUILayer": "Menu",
    "commonUIInputMode": "UI"
  },
  "rootWidget": { ... }
}
```

**Configuration Options:**
- `bUseCommonUI`: Whether to use `UCommonActivatableWidget` as parent class (default: false)
- `commonUILayer`: CommonUI layer, options: `Game`, `Menu`, `Popup`, `Dialog`, `Modal`
- `commonUIInputMode`: Input mode, options: `Game`, `UI`, `All`

## Slot Properties

### Box Slots (VerticalBox/HorizontalBox)
```json
"slot": {
  "padding": { "left": 10, "top": 5, "right": 10, "bottom": 5 },
  "fill": 1.0,
  "size": { "width": 100, "height": 45 },
  "hAlignment": "Center",
  "vAlignment": "Center"
}
```

- `padding`: Inner padding (FMargin)
- `fill`: Fill weight, 0=auto size, >0=proportional fill
- `size.width`: Fixed width (px), mutually exclusive with fill
- `size.height`: Fixed height (px), mutually exclusive with fill
- `size.fill`: Equivalent to fill, for complex size definitions
- `hAlignment`: "Left" | "Center" | "Right" | "Fill"
- `vAlignment`: "Top" | "Center" | "Bottom" | "Fill"

**Size Priority:**
1. `size.width/height` → Fixed size
2. `fill` or `size.fill` → Fill by weight
3. Default → Auto size

### Canvas Slot (Absolute Positioning)
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

**Anchor System:**
- `minimum/maximum`: 0-1 normalized coordinates, (0,0)=top-left, (1,1)=bottom-right
- **Point Anchor**: minimum=maximum, widget positioned relative to a single anchor point
- **Stretch Anchor**: minimum≠maximum, widget stretched between anchor rectangle

**Point Anchor (minimum=maximum):**
- `offsets.left, offsets.top` = position of widget's top-left corner relative to anchor point
- widget size = `(right - left, bottom - top)`
- Example: anchor(0.5,0.5), offsets(-100,-50,100,50) = centered 200×100 widget

**Stretch Anchor (minimum≠maximum):**
- `offsets` defines margins relative to anchor rectangle
- Positive values = inset, negative values = outset

## Editor Workflow

### JSON → UMG (Generation)
1. Enter JSON in the editor panel
2. Click "Generate UMG Widget"
3. The generated Widget Blueprint opens automatically

### UMG → JSON (Export)
1. Click "Export UMG to JSON"
2. Select the Widget Blueprint to export
3. JSON displays in the editor panel for modification and regeneration

### Overlay Slot
```json
"slot": {
  "padding": { "left": 0, "top": 0, "right": 0, "bottom": 0 },
  "hAlignment": "Center",
  "vAlignment": "Center"
}
```

## Content Properties

```json
"content": {
  "text": "Display Text",
  "placeholder": "Input Hint",
  "isPassword": false,
  "progress": 0.75,
  "sliderValue": 0.5,
  "isChecked": false,
  "wrapping": 2,
  "justification": "Center"
}
```

- `text`: Text content for Text/Button
- `placeholder`: Hint text for InputField
- `isPassword`: Whether it's a password input field
- `progress`: ProgressBar progress (0-1)
- `sliderValue`: Slider value (0-1)
- `isChecked`: Whether CheckBox is checked
- `wrapping`: Text wrap mode: 0=NoWrap, 1=Wrap, 2=AutoWrap (default)
- `justification`: Text alignment: "Left", "Center", "Right"

**Note**: Font styles (fontSize, color, fontWeight) should be in the `style` field, not in `content`.

## CommonUI Properties

When using CommonUI Widgets, setting `parentClass` automatically enables CommonUI mode:

```json
{
  "version": "2.0",
  "name": "MyMenu",
  "parentClass": "CommonActivatableWidget",
  "rootWidget": {
    "type": "VerticalBox",
    "children": [
      {
        "type": "Text",
        "style": { "fontSize": 24, "color": "white" }
      },
      {
        "type": "Button",
        "style": { "normalColor": "#1a66cc", "cornerRadius": 8 }
      }
    ]
  }
}
```

**parentClass Options:**
- `"CommonActivatableWidget"` - Game menus/popups (recommended)
- `"CommonUserWidget"` - Embedded UI components

**Auto Type Inference:**
- When `parentClass` is CommonUI, `Text` → `CommonText`, `Button` → `CommonButton`
- Styles automatically apply to corresponding CommonUI controls

## Style Properties

```json
"style": {
  "width": 200,
  "height": 50,
  "padding": { "left": 10, "top": 5, "right": 10, "bottom": 5 },
  "backgroundColor": "#1a1a1f",
  "borderColor": "#808080",
  "borderWidth": 2,
  "borderRadius": 8,
  "opacity": 0.9,
  "visibility": "Visible"
}
```

**Layout Styles**:
- `width` / `height` - Fixed dimensions
- `padding` - Inner padding
- `margin` - Outer margin

**Visual Styles**:
- `backgroundColor` - Background color (container widgets)
- `borderColor` / `borderWidth` / `borderRadius` - Border
- `opacity` - Opacity (0-1)
- `visibility` - Visibility: `"Visible"`, `"Hidden"`, `"Collapsed"`

**Text Styles** (Text widget):
- `fontSize` - Font size
- `fontWeight` - Font weight: `"Light"`, `"Regular"`, `"Medium"`, `"Bold"`
- `fontFamily` - Font resource path
- `color` - Text color

**Button Styles** (Button widget):
- `normalColor` / `hoveredColor` / `pressedColor` - State colors
- `textColor` - Text color
- `cornerRadius` - Corner radius
- `minWidth` / `minHeight` - Minimum dimensions

## Animation System

### Basic Animation Format

```json
"animations": [
  {
    "name": "fadeIn",
    "property": "RenderOpacity",
    "fromValue": 0,
    "toValue": 1,
    "duration": 0.5,
    "delay": 0,
    "easing": "EaseOut",
    "loop": 1,
    "autoPlay": true
  }
]
```

### Supported Animation Properties

| Property Name | Value Type | Description |
|---------------|------------|-------------|
| `RenderOpacity` | Float (0-1) | Opacity |
| `RenderTranslation` | Vector2D | Translation (X, Y) |
| `RenderScale` | Vector2D | Scale (X, Y) |
| `RenderRotation` | Float | Rotation angle |
| `BackgroundColor` | Color | Background color (Border/Button) |
| `TintColor` / `ColorAndOpacity` | Color | Tint (Image) |
| `WidgetWidth` | Float | Width |
| `WidgetHeight` | Float | Height |

### Vector2D Animation

```json
"animations": [
  {
    "name": "slideIn",
    "property": "RenderTranslation",
    "fromVector": { "x": -100, "y": 0 },
    "toVector": { "x": 0, "y": 0 },
    "duration": 0.3,
    "easing": "OutQuad"
  },
  {
    "name": "scaleUp",
    "property": "RenderScale",
    "fromVector": { "x": 0.5, "y": 0.5 },
    "toVector": { "x": 1.0, "y": 1.0 },
    "duration": 0.4,
    "easing": "OutBack"
  }
]
```

### Color Animation

```json
"animations": [
  {
    "name": "colorPulse",
    "property": "BackgroundColor",
    "fromColor": { "R": 0.2, "G": 0.5, "B": 0.8, "A": 1 },
    "toColor": { "R": 0.4, "G": 0.7, "B": 1.0, "A": 1 },
    "duration": 1.5,
    "easing": "InOutSine",
    "loop": -1,
    "autoPlay": true
  }
]
```

### Keyframe Animation

```json
"animations": [
  {
    "name": "bounce",
    "property": "RenderScale",
    "keyframes": [
      { "time": 0, "value": { "x": 1.0, "y": 1.0 } },
      { "time": 0.1, "value": { "x": 1.2, "y": 1.2 } },
      { "time": 0.2, "value": { "x": 0.9, "y": 0.9 } },
      { "time": 0.3, "value": { "x": 1.05, "y": 1.05 } },
      { "time": 0.4, "value": { "x": 1.0, "y": 1.0 } }
    ]
  }
]
```

### Easing Types

- `Linear` - Linear
- `EaseIn`, `EaseOut`, `EaseInOut` - Basic easing
- `InQuad`, `OutQuad`, `InOutQuad` - Quadratic
- `InCubic`, `OutCubic`, `InOutCubic` - Cubic
- `InElastic`, `OutElastic` - Elastic
- `InBounce`, `OutBounce` - Bounce
- `InBack`, `OutBack` - Back

### Extended Animation Properties

The system uses an **Animation Property Registry** that supports dynamic extension of new animatable properties. View the complete property list:

```
Plugins/LLMDynamicUI/Content/Schemas/AnimPropertySchema.llmschema
```

Or click **"Export Anim Props"** in the editor to export the latest dictionary.

## Events

```json
"events": {
  "onClick": "OnButtonClicked",
  "onHover": "OnMouseEnter",
  "onUnhover": "OnMouseLeave",
  "onPressed": "OnMouseDown",
  "onReleased": "OnMouseUp",
  "onValueChanged": "OnSliderChanged",
  "onTextChanged": "OnInputChanged"
}
```

## Common Patterns

### SDFBox Effect Container
SDFBox is a container widget supporting SDF effects, can contain a single child widget:

```json
{
  "id": "card",
  "type": "SDFBox",
  "sdf": {
    "shape": { "size": { "width": 300, "height": 200 }, "cornerRadius": 16 },
    "fill": { "type": "Solid", "color": { "r": 0.1, "g": 0.1, "b": 0.15, "a": 0.9 } },
    "shadow": { "offset": { "x": 0, "y": 8 }, "blur": 20, "color": { "r": 0, "g": 0, "b": 0, "a": 0.4 } },
    "border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.1 } },
    "padding": { "left": 20, "top": 20, "right": 20, "bottom": 20 }
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

**SDFBox Features:**
- Supports `children` array (maximum one child widget)
- `padding` property controls child widget padding
- Auto sizing: SDF size expands to accommodate child widget + padding
- Can replace `Overlay + SDFBox` combination, cleaner structure

### visionOS Liquid Glass Style (BackdropBlur)
SDFBox supports `backdropBlur` property for background blur effect, system automatically combines `BackgroundBlur` widget:

```json
{
  "id": "glassPanel",
  "type": "SDFBox",
  "sdf": {
    "shape": { "size": { "width": 300, "height": 200 }, "cornerRadius": 16 },
    "fill": { "type": "Solid", "color": { "r": 1, "g": 1, "b": 1, "a": 0.08 } },
    "border": { "width": 1, "color": { "r": 1, "g": 1, "b": 1, "a": 0.18 } },
    "shadow": { "offset": { "x": 0, "y": 8 }, "blur": 32, "color": { "r": 0, "g": 0, "b": 0, "a": 0.18 } },
    "backdropBlur": {
      "enabled": true,
      "strength": 64,
      "saturation": 2.0
    }
  }
}
```

**BackdropBlur Parameters:**
- `enabled`: Whether to enable background blur
- `strength`: Blur strength (0-100, default 64)
- `saturation`: Saturation boost (1.0=original, 2.0=CSS saturate(200%))

**Preset Values:**
- `Glass(64)`: visionOS default glass effect
- `Subtle(32)`: Subtle blur
- `Frosted(80)`: Strong frosted effect

Detailed property reference: `Plugins/LLMDynamicUI/Content/Schemas/SDFSchema.llmschema`

### Fixed Height Row (Input/Button)
```json
{
  "id": "inputRow",
  "type": "HorizontalBox",
  "slot": { "size": { "height": 45 }, "hAlignment": "Fill" },
  "children": [...]
}
```

### Fill Remaining Space
```json
{
  "id": "spacer",
  "type": "Spacer",
  "slot": { "fill": 1.0 }
}
```

### Centered Popup
```json
{
  "id": "dialog",
  "type": "Border",
  "content": { "color": { "R": 0.15, "G": 0.15, "B": 0.2, "A": 0.95 } },
  "slot": {
    "anchors": { "minimum": { "x": 0.5, "y": 0.5 }, "maximum": { "x": 0.5, "y": 0.5 } },
    "offsets": { "left": -200, "top": -150, "right": 200, "bottom": 150 }
  }
}
```

### Fullscreen Stretched Background
```json
{
  "id": "background",
  "type": "Image",
  "content": { "color": { "R": 0, "G": 0, "B": 0, "A": 0.5 } },
  "slot": {
    "anchors": { "minimum": { "x": 0, "y": 0 }, "maximum": { "x": 1, "y": 1 } },
    "offsets": { "left": 0, "top": 0, "right": 0, "bottom": 0 }
  }
}
```

### Equal Width Button Row
```json
{
  "type": "HorizontalBox",
  "children": [
    { "type": "Button", "content": { "text": "OK" }, "slot": { "fill": 1 } },
    { "type": "Button", "content": { "text": "Cancel" }, "slot": { "fill": 1 } }
  ]
}
```

### Animated Progress Bar
```json
{
  "type": "ProgressBar",
  "content": { "progress": 0 },
  "animations": [{
    "name": "fillProgress",
    "property": "progress",
    "fromValue": 0,
    "toValue": 1,
    "duration": 2.0,
    "easing": "OutQuad"
  }]
}
```

## Full Example: Login Screen

```json
{
  "version": "2.0",
  "name": "LoginScreen",
  "parentClass": "CommonActivatableWidget",
  "styles": {
    "titleText": {
      "type": "text",
      "fontSize": 28,
      "fontWeight": "Bold",
      "color": "#FFD84D"
    },
    "panelBackground": {
      "type": "border",
      "backgroundColor": "#1a1a26",
      "borderRadius": 12
    }
  },
  "rootWidget": {
    "id": "rootCanvas",
    "type": "Canvas",
    "children": [
      {
        "id": "background",
        "type": "Image",
        "style": { "backgroundColor": "#0d0d14" },
        "slot": {
          "anchors": { "minimum": { "x": 0, "y": 0 }, "maximum": { "x": 1, "y": 1 } },
          "offsets": { "left": 0, "top": 0, "right": 0, "bottom": 0 }
        }
      },
      {
        "id": "loginPanel",
        "type": "Border",
        "styleRef": "panelBackground",
        "slot": {
          "anchors": { "minimum": { "x": 0.5, "y": 0.5 }, "maximum": { "x": 0.5, "y": 0.5 } },
          "offsets": { "left": -180, "top": -200, "right": 180, "bottom": 200 }
        },
        "children": [
          {
            "id": "contentBox",
            "type": "VerticalBox",
            "slot": { "padding": { "left": 30, "top": 30, "right": 30, "bottom": 30 } },
            "children": [
              {
                "id": "titleText",
                "type": "Text",
                "styleRef": "titleText",
                "content": { "text": "Welcome Back" },
                "slot": { "padding": { "bottom": 30 }, "hAlignment": "Center" }
              },
              {
                "id": "usernameInput",
                "type": "InputField",
                "content": { "placeholder": "Username" },
                "slot": { "padding": { "bottom": 15 }, "size": { "height": 40 }, "hAlignment": "Fill" }
              },
              {
                "id": "passwordInput",
                "type": "InputField",
                "content": { "placeholder": "Password", "isPassword": true },
                "slot": { "padding": { "bottom": 25 }, "size": { "height": 40 }, "hAlignment": "Fill" }
              },
              {
                "id": "loginButton",
                "type": "Button",
                "style": {
                  "normalColor": "#1a66cc",
                  "hoveredColor": "#3388ff",
                  "textColor": "white",
                  "cornerRadius": 6
                },
                "content": { "text": "Login" },
                "slot": { "size": { "height": 45 }, "hAlignment": "Fill" },
                "events": { "onClick": "OnLoginClicked" }
              },
              {
                "id": "registerLink",
                "type": "Text",
                "style": { "color": "#80B3FF" },
                "content": { "text": "Create Account" },
                "slot": { "padding": { "top": 15 }, "hAlignment": "Center" }
              }
            ]
          }
        ]
      }
    ]
  }
}
```