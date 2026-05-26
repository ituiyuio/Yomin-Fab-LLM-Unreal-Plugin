---
layout: default
title: Getting Started
parent: LLM Dynamic UI
nav_order: 1
---

# Getting Started

## Prerequisites

- Unreal Engine 5.7+
- Two engine plugins must be enabled in your project:

| Plugin | Purpose | How to Enable |
|--------|---------|---------------|
| **CommonUI** | CommonButton, CommonText, CommonBorder widgets | Edit → Plugins → CommonUI, or add to `.uproject` |
| **EditorScriptingUtilities** | UMG Blueprint generation at edit time | Edit → Plugins → Editor Scripting Utilities, or add to `.uproject` |

Both are included with UE5 and marked as required dependencies in `LLMDynamicUI.uplugin`.

---

## Installation

1. Copy the `LLMDynamicUI` plugin folder to your project's `Plugins/` directory
2. Open your project in Unreal Editor
3. Enable the two engine plugins above when prompted
4. The plugin is ready — no additional setup needed

---

## Basic Example

Create a `.llmui` file (or paste directly into the editor panel):

```json
{
  "version": "2.0",
  "name": "LoginScreen",
  "rootWidget": {
    "id": "root",
    "type": "VerticalBox",
    "children": [
      {
        "id": "titleText",
        "type": "Text",
        "style": { "fontSize": 28, "fontWeight": "Bold", "color": "#FFD84D" },
        "content": { "text": "Welcome Back" }
      },
      {
        "id": "loginBtn",
        "type": "Button",
        "style": { "normalColor": "#1a66cc", "hoveredColor": "#3388ff", "cornerRadius": 8 },
        "content": { "text": "Login" },
        "events": { "onClick": "OnLoginClicked" }
      }
    ]
  }
}
```

---

## Workflow

1. **LLM generates `.llmui`** — AI outputs JSON with your UI definition
2. **Import in Editor** — Window → LLMDynamicUI Panel → paste or import file
3. **Generate UMG** — One click creates the Widget Blueprint
4. **Iterate** — Modify JSON, regenerate, or export back to JSON for roundtrip editing

---

## Build Verification

Before distributing or submitting to a marketplace:

1. Delete `Intermediate/`, `Binaries/`, `Build/`, `Saved/` folders inside the plugin directory
2. Run a full rebuild from a clean Intermediate state:

   ```
   UnrealBuildTool BuildPlugin -Plugin="path/to/LLMDynamicUI.uplugin" -Platform=Win64 -Configuration=Development
   ```

3. Confirm zero errors and zero consequential warnings
