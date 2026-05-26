---
layout: default
title: Getting Started
parent: LLM StateTree
nav_order: 1
---

# Getting Started

## Prerequisites

- Unreal Engine 5.7+
- Three engine plugins must be enabled in your project:

| Plugin | Purpose | How to Enable |
|--------|---------|---------------|
| **StateTree** | StateTree module and core types | Edit → Plugins → StateTree, or add to `.uproject` |
| **GameplayStateTree** | StateTree tasks and conditions | Edit → Plugins → GameplayStateTree, or add to `.uproject` |
| **EditorScriptingUtilities** | Asset generation at edit time | Edit → Plugins → Editor Scripting Utilities, or add to `.uproject` |

All are included with UE5 and marked as required dependencies in `LLMStateTree.uplugin`.

---

## Installation

1. Copy the `LLMStateTree` plugin folder to your project's `Plugins/` directory
2. Open your project in Unreal Editor
3. Enable the three engine plugins above when prompted
4. The plugin is ready — no additional setup needed

---

## Basic Workflow

1. **LLM generates `.llmstate`** — AI outputs JSON with your AI behavior definition
2. **Load in Editor** — Window → LLMStateTree Panel → load or paste `.llmstate` file
3. **Generate StateTree** — One click creates the StateTree Blueprint asset
4. **Assign to AI** — Use the generated StateTree with your AIController or Character

---

## Build Verification

Before distributing or submitting to a marketplace:

1. Delete `Intermediate/`, `Binaries/`, `Build/`, `Saved/` folders inside the plugin directory
2. Run a full rebuild from a clean Intermediate state:

   ```
   UnrealBuildTool BuildPlugin -Plugin="path/to/LLMStateTree.uplugin" -Platform=Win64 -Configuration=Development
   ```

3. Confirm zero errors and zero consequential warnings

---

## File Location

Place `.llmstate` files in your project's `Config/Examples/` folder for easy access:

```
YourProject/
└── Config/
    └── Examples/
        ├── SimpleAI.llmstate
        ├── GuardAI.llmstate
        └── MyAI.llmstate
```
