---
name: llm-dynamic-ui
description: |
  LLM Dynamic UI 是一个 DSL 驱动的 UE5 UMG 界面生成系统。当用户需要：
  (1) 创建或设计 UE5 UMG 界面（登录页、菜单、HUD、对话框等）
  (2) 将界面描述转换为可生成的 DSL 格式
  (3) 理解或修改现有的 UI DSL 定义
  (4) 需要了解支持的 Widget 类型、布局系统、动画系统
  (5) 查询可动画属性列表和动画创建方式
  请使用此技能。
---

# LLM Dynamic UI - DSL Schema Guide

### **组合优于继承**

## File Format

UI 定义文件使用 `.llmui` 扩展名（LLM UI DSL），格式为 JSON。

## Reference Files

**UMG 属性字典**: `Plugins/LLMDynamicUI/Content/Schemas/PropertySchema.llmschema` - 包含所有 UMG Widget 的完整属性定义

**CommonUI Schema**: `Plugins/LLMDynamicUI/Content/Schemas/CommonUISchema.llmschema` - CommonUI 控件定义，支持游戏菜单、手柄导航、InputAction 绑定

**动画属性字典**: `Plugins/LLMDynamicUI/Content/Schemas/AnimPropertySchema.llmschema` - 包含所有可动画属性的定义（Track类型、值类型、使用示例）

**SDF 效果字典**: `Plugins/LLMDynamicUI/Content/Schemas/SDFSchema.llmschema` - 包含 SDF 视觉效果（阴影、发光、边框、渐变）的完整定义

**示例目录**: `Plugins/LLMDynamicUI/Content/Samples/` - 包含完整的 UI 示例 `.llmui` 文件

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

## Color Formats (颜色格式)

支持多种颜色格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| Hex 6位 | `"#FF8800"` | RRGGBB |
| Hex 8位 | `"#FF880088"` | RRGGBBAA (带透明度) |
| Hex 3位 | `"#F80"` | RGB 短格式 |
| RGB | `"rgb(255, 136, 0)"` | 0-255 范围 |
| RGBA | `"rgba(255, 136, 0, 0.8)"` | 带透明度 |
| Named | `"white"`, `"cyan"`, `"transparent"` | 命名颜色 |

**命名颜色列表**: `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `orange`, `gray`, `transparent`

## Simplified Style (简化样式) - 推荐

**直接在 Widget 上使用内联样式，系统自动哈希去重，生成复用的 Style 资产：**

### CommonButton 内联样式
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

### CommonText 内联样式
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

### 普通 Widget 样式
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

**文本样式属性**:
- `fontSize` - 字体大小
- `fontWeight` - 字重: `"Light"`, `"Regular"`, `"Medium"`, `"Bold"`
- `fontFamily` - 字体路径
- `color` - 文字颜色

**按钮样式属性**:
- `normalColor` - 正常状态颜色
- `hoveredColor` - 悬停状态颜色
- `pressedColor` - 按下状态颜色
- `textColor` - 文字颜色
- `cornerRadius` - 圆角半径
- `minWidth` / `minHeight` - 最小尺寸

**自动去重机制**: 相同的样式定义会自动生成同一个 Style 资产，无需手动管理。

## Widget Types

### Layout Containers
| Type | UE Class | Description |
|------|----------|-------------|
| `VerticalBox` | UVerticalBox | 垂直排列子元素 |
| `HorizontalBox` | UHorizontalBox | 水平排列子元素 |
| `Canvas` | UCanvasPanel | 绝对定位，支持锚点 (别名: `CanvasPanel`) |
| `Overlay` | UOverlay | 层叠布局 |
| `Border` | UBorder | 带背景的容器 |
| `ScrollBox` | UScrollBox | 可滚动容器 |
| `SizeBox` | USizeBox | 固定尺寸容器 |
| `ScaleBox` | UScaleBox | 缩放容器 |
| `WrapBox` | UWrapBox | 自动换行布局 |
| `GridPanel` | UGridPanel | 网格布局 |
| `UniformGridPanel` | UUniformGridPanel | 均匀网格 |
| `WidgetSwitcher` | UWidgetSwitcher | 切换显示子控件 |

### Leaf Widgets
| Type | UE Class | Description |
|------|----------|-------------|
| `Text` | UTextBlock | 文本显示 |
| `Button` | UButton | 按钮 |
| `Image` | UImage | 图片 |
| `InputField` | UEditableText | 输入框 (别名: `EditableText`) |
| `ProgressBar` | UProgressBar | 进度条 |
| `Slider` | USlider | 滑动条 |
| `CheckBox` | UCheckBox | 复选框 |
| `ComboBox` | UComboBoxString | 下拉框 |
| `Spacer` | USpacer | 占位空间 |

### Effects Widgets
| Type | UE Class | Description |
|------|----------|-------------|
| `SDFBox` | USDFBoxWidgetPure | SDF 效果容器，支持阴影/发光/边框/渐变，可包含单个子控件 |

### CommonUI Widgets (需要 CommonUI 插件)
| Type | UE Class | Description |
|------|----------|-------------|
| `CommonButton` | UCommonButton | CommonUI 按钮，支持输入动作 |
| `CommonText` | UCommonText | CommonUI 文本，支持样式资源 |
| `CommonBorder` | UCommonBorder | CommonUI 边框，支持样式资源 |
| `CommonImage` | UCommonImage | CommonUI 图片 |

## styleRef (专家模式)

> **注意**: 推荐 使用内联样式 `buttonStyle`/`textStyle`。以下仅用于引用人工预先创建的 Style 资产。

如果需要在多个 UI 文件间共享同一个手动创建的 Style 资产：

```json
{
  "id": "loginPanel",
  "type": "Border",
  "styleRef": "/Game/UI/Styles/PanelStyle",
  "children": [...]
}
```

**适用场景:**
- 引用美术/设计师手动创建的 Style Blueprint
- 需要在多个独立 UI 文件间共享样式

**不适用:**
- LLM 生成的 UI（使用内联样式即可）
- 同一文件内复用样式（自动去重机制已处理）

## Configuration (配置选项)

在文档根级别设置生成配置：

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

**配置项说明:**
- `bUseCommonUI`: 是否使用 `UCommonActivatableWidget` 作为父类 (默认: false)
- `commonUILayer`: CommonUI 层级，可选值: `Game`, `Menu`, `Popup`, `Dialog`, `Modal`
- `commonUIInputMode`: 输入模式，可选值: `Game`, `UI`, `All`

## Slot Properties (布局属性)

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

- `padding`: 内边距 (FMargin)
- `fill`: 填充权重，0=自动大小，>0=按比例填充
- `size.width`: 固定宽度 (px)，与 fill 互斥
- `size.height`: 固定高度 (px)，与 fill 互斥
- `size.fill`: 等同于 fill，用于复杂尺寸定义
- `hAlignment`: "Left" | "Center" | "Right" | "Fill"
- `vAlignment`: "Top" | "Center" | "Bottom" | "Fill"

**尺寸优先级:**
1. `size.width/height` → 固定尺寸
2. `fill` 或 `size.fill` → 按权重填充
3. 默认 → 自动大小

### Canvas Slot (绝对定位)
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

**锚点系统:**
- `minimum/maximum`: 0-1 归一化坐标，(0,0)=左上, (1,1)=右下
- **Point Anchor**: minimum=maximum，widget 相对于单个锚点定位
- **Stretch Anchor**: minimum≠maximum，widget 在锚点矩形间拉伸

**Point Anchor (minimum=maximum):**
- `offsets.left, offsets.top` = widget 左上角相对于锚点的位置 (position)
- widget 尺寸 = `(right - left, bottom - top)`
- 例：锚点(0.5,0.5)，offsets(-100,-50,100,50) = 居中200×100的widget

**Stretch Anchor (minimum≠maximum):**
- `offsets` 定义相对于锚点矩形的边距
- 正值=向内缩进，负值=向外扩展

## Editor Workflow

### JSON → UMG (生成)
1. 在编辑器面板输入 JSON
2. 点击 "Generate UMG Widget"
3. 生成的 Widget Blueprint 会自动打开

### UMG → JSON (导出)
1. 点击 "Export UMG to JSON"
2. 选择要导出的 Widget Blueprint
3. JSON 会显示在编辑器面板中，可用于修改和重新生成

### Overlay Slot
```json
"slot": {
  "padding": { "left": 0, "top": 0, "right": 0, "bottom": 0 },
  "hAlignment": "Center",
  "vAlignment": "Center"
}
```

## Content Properties (内容属性)

```json
"content": {
  "text": "显示文本",
  "placeholder": "输入提示",
  "isPassword": false,
  "progress": 0.75,
  "sliderValue": 0.5,
  "isChecked": false,
  "wrapping": 2,
  "justification": "Center"
}
```

- `text`: Text/Button 的文本内容
- `placeholder`: InputField 的提示文本
- `isPassword`: 是否为密码输入框
- `progress`: ProgressBar 进度 (0-1)
- `sliderValue`: Slider 值 (0-1)
- `isChecked`: CheckBox 是否选中
- `wrapping`: 文本换行模式: 0=NoWrap, 1=Wrap, 2=AutoWrap (默认)
- `justification`: 文本对齐: "Left", "Center", "Right"

**注意**: 字体样式（fontSize, color, fontWeight）应放在 `style` 字段中，不在 `content` 中。

## CommonUI Properties (CommonUI 属性)

当使用 CommonUI Widget 时，设置 `parentClass` 即可自动启用 CommonUI 模式：

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

**parentClass 选项:**
- `"CommonActivatableWidget"` - 游戏菜单/弹窗（推荐）
- `"CommonUserWidget"` - 嵌入式 UI 组件

**自动类型推断:**
- `parentClass` 为 CommonUI 时，`Text` → `CommonText`，`Button` → `CommonButton`
- 样式自动应用到对应 CommonUI 控件

## Style Properties (样式属性)

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

**布局样式**:
- `width` / `height` - 固定尺寸
- `padding` - 内边距
- `margin` - 外边距

**视觉样式**:
- `backgroundColor` - 背景颜色（容器类控件）
- `borderColor` / `borderWidth` / `borderRadius` - 边框
- `opacity` - 透明度 (0-1)
- `visibility` - 可见性: `"Visible"`, `"Hidden"`, `"Collapsed"`

**文本样式** (Text 控件):
- `fontSize` - 字体大小
- `fontWeight` - 字重: `"Light"`, `"Regular"`, `"Medium"`, `"Bold"`
- `fontFamily` - 字体资源路径
- `color` - 文字颜色

**按钮样式** (Button 控件):
- `normalColor` / `hoveredColor` / `pressedColor` - 状态颜色
- `textColor` - 文字颜色
- `cornerRadius` - 圆角
- `minWidth` / `minHeight` - 最小尺寸

## Animation System (动画系统)

### 基础动画格式

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

### 支持的动画属性

| 属性名 | 值类型 | 说明 |
|--------|--------|------|
| `RenderOpacity` | Float (0-1) | 透明度 |
| `RenderTranslation` | Vector2D | 位移 (X, Y) |
| `RenderScale` | Vector2D | 缩放 (X, Y) |
| `RenderRotation` | Float | 旋转角度 |
| `BackgroundColor` | Color | 背景颜色 (Border/Button) |
| `TintColor` / `ColorAndOpacity` | Color | 着色 (Image) |
| `WidgetWidth` | Float | 宽度 |
| `WidgetHeight` | Float | 高度 |

### Vector2D 动画

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

### 颜色动画

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

### 关键帧动画

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

- `Linear` - 线性
- `EaseIn`, `EaseOut`, `EaseInOut` - 基础缓动
- `InQuad`, `OutQuad`, `InOutQuad` - 二次方
- `InCubic`, `OutCubic`, `InOutCubic` - 三次方
- `InElastic`, `OutElastic` - 弹性
- `InBounce`, `OutBounce` - 弹跳
- `InBack`, `OutBack` - 回弹

### 扩展动画属性

系统使用**动画属性注册表**，支持动态扩展新的可动画属性。查看完整属性列表：

```
Plugins/LLMDynamicUI/Content/Schemas/AnimPropertySchema.llmschema
```

或在编辑器中点击 **"Export Anim Props"** 按钮导出最新字典。

## Events (事件绑定)

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

### SDFBox 效果容器
SDFBox 是一个支持 SDF 效果的容器控件，可包含单个子控件：

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

**SDFBox 特性:**
- 支持 `children` 数组（最多一个子控件）
- `padding` 属性控制子控件内边距
- 自动尺寸：SDF 尺寸会扩展以容纳子控件 + padding
- 可替代 `Overlay + SDFBox` 组合，结构更简洁

### visionOS Liquid Glass 风格 (BackdropBlur)
SDFBox 支持 `backdropBlur` 属性实现背景模糊效果，系统自动组合 `BackgroundBlur` 控件：

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

**BackdropBlur 参数:**
- `enabled`: 是否启用背景模糊
- `strength`: 模糊强度 (0-100, 默认64)
- `saturation`: 饱和度增强 (1.0=原始, 2.0=CSS saturate(200%))

**预设值:**
- `Glass(64)`: visionOS 默认玻璃效果
- `Subtle(32)`: 轻微模糊
- `Frosted(80)`: 强磨砂效果

详细属性参考: `Plugins/LLMDynamicUI/Content/Schemas/SDFSchema.llmschema`

### 固定高度行 (输入框/按钮)
```json
{
  "id": "inputRow",
  "type": "HorizontalBox",
  "slot": { "size": { "height": 45 }, "hAlignment": "Fill" },
  "children": [...]
}
```

### 填充剩余空间
```json
{
  "id": "spacer",
  "type": "Spacer",
  "slot": { "fill": 1.0 }
}
```

### 居中弹窗
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

### 全屏拉伸背景
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

### 等宽按钮行
```json
{
  "type": "HorizontalBox",
  "children": [
    { "type": "Button", "content": { "text": "OK" }, "slot": { "fill": 1 } },
    { "type": "Button", "content": { "text": "Cancel" }, "slot": { "fill": 1 } }
  ]
}
```

### 带动画的进度条
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

## LLMEasyShellLite Support (Parallel Registration)

`LLMDynamicUI` registers **two parallel abilities** named `ui` — one per shell — with **identical command set** (LLM-series plugins are allowed to register write operations in Lite, only the generic helper commands in LLMEasyShell itself are read-only by design):

| Shell | CLI Binary | Ability | Commands Available |
|-------|-----------|---------|--------------------|
| `LLMEasyShell` (full) | `llmshell` | `ui` (full) | `generate` · `export` · `list-types` · `export-schema` |
| `LLMEasyShellLite` | `llmshelllite` | `ui` (lite, full feature set) | `generate` · `export` · `list-types` · `export-schema` |

### Lite Discovery Mechanism

LLMDynamicUI does **not** use the Python Ability framework (`LLMShellAbilitiesLite`) — that path is exclusive to LLMEasyShell's own PyAbility runtime. Instead, it mirrors the same `RegisterAbilityJson` + `RegisterAbilityCommandHandler` C++ API that the full shell uses:

```cpp
// Compile-time: detected via CheckModuleExists("LLMEasyShellLite")
#if WITH_LLMEASYSHELL_LITE
    FCoreDelegates::OnAllModuleLoadingPhasesComplete.AddRaw(
        this, &FLLMDynamicUIEditorModule::RegisterWithLLMEasyShellLite);
#endif
```

At editor startup, the editor module checks for `/Script/LLMEasyShellLite.LLMEasyShellLiteSubsystem` and (if present) registers the `ui` ability with the **same 4 commands** as the full shell, reusing a single `ULLMDynamicUICommandHandler` instance whose `Execute` UFUNCTION bridges to `ExecuteWithResult`.

### Why the Same Handler Works for Both Shells

The two shells' command dispatchers look for different UFUNCTION names by default:
- **Full** (`ULLMEasyShellSubsystem`) prefers `ExecuteWithResult`, falls back to `Execute`
- **Lite** (`ULLMEasyShellLiteSubsystem`) only knows `Execute` (base class `ULLMEasyShellAbilityCommandObjectLite`)

LLMDynamicUI's `ULLMDynamicUICommandHandler` exposes **both** UFUNCTIONs:
```cpp
UFUNCTION() FString ExecuteWithResult(const FString& Cmd, const FString& ArgsJson);
UFUNCTION() FString Execute(const FString& Cmd, const FString& ArgsJson)
    { return ExecuteWithResult(Cmd, ArgsJson); }
```

Both shells end up routing to the same `ExecuteWithResult` body — there is exactly one command-dispatch path.

### Commands (identical in both shells)

```bash
# Generate a UMG Widget Blueprint from a .llmui file
llmshelllite ui generate /Game/UI/MyWidget --from C:/Temp/ui.json

# Export a UMG Widget Blueprint back to .llmui
llmshelllite ui export /Game/UI/MyWidget --output C:/Temp/export.llmui

# List available widget types grouped by category
llmshelllite ui list-types
llmshelllite ui list-types --category Layout

# Export the widget-type schema to a JSON file
llmshelllite ui export-schema --output C:/Temp/schema.json
```

### Compile-time Configuration

`LLMDynamicUIEditor.Build.cs` detects each shell independently and defines a macro:
- `WITH_LLMEASYSHELL=1` if `Plugins/LLMEasyShell/` exists
- `WITH_LLMEASYSHELL_LITE=1` if `Plugins/LLMEasyShellLite/` exists

Both can be 1 simultaneously (e.g. dev workstation with both shells installed). The two `ui` abilities are independent — each shell's CLI sees only its own registered commands.
