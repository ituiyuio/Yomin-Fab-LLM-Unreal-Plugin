---
outline: [2, 3]
---

# LLM StateTree

JSON-Driven StateTree Asset Generator for Unreal Engine 5.

Generate complete StateTree Blueprint assets from JSON (`.llmstate` files) with schema auto-inference and live preview — no manual StateTree editor work required.

---

## Features

- **One JSON, Complete AI** — Tasks, Conditions, Evaluators, and Considerations from a single `.llmstate` file
- **LLM-First Design** — AI outputs JSON directly, no StateTree editor knowledge required
- **Schema Auto-Inference** — Automatically discovers StateTree node types from UE reflection
- **Editor Panel** — Browse and preview generated StateTree structure
- **Parameter Binding** — Support for `${Parameters.Name}` and `${Context.Property}` binding expressions (legacy `${Param.Name}` alias supported)
- **Utility AI** — Considerations with response curves for action selection
- **9 Example Files** — SimpleAI, GuardAI, UtilityAI, StealthAI, BossAI + 4 NPC dialog examples (Reimu / Rumia / Patchouli / Rumia Merchant) included
- **14+ Node Types** — Tasks, Conditions, Considerations fully documented

---

## Quick Start

1. Menu → Tools → **LLM StateTree Panel**
2. Load a `.llmstate` file or paste JSON
3. Click **Generate StateTree**
4. The generated StateTree asset is created automatically

```json
{
  "name": "MyAI",
  "version": "1.0",
  "parameters": {
    "Speed": { "type": "float", "default": 500.0 }
  },
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "properties": { "Duration": 2.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol" }
      ]
    }
  ]
}
```

---

## Version Info

| Item | Value |
|------|-------|
| Plugin Version | 1.1.2 |
| Engine | UE 5.5+ (5.5/5.6/5.7/5.8 multi-UE build) |
| Modules | LLMStateTree (Runtime), LLMStateTreeEditor (Editor) |
| Publisher | YominUnreal |
| Required Plugins | StateTree, GameplayStateTree, EditorScriptingUtilities |
