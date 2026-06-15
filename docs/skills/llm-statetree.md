---
outline: [2, 3]
---

# LLM StateTree

DSL-driven StateTree AI generation for Unreal Engine 5. The agent writes `.llmstate` JSON, the editor turns it into a real `UStateTree` asset — tasks, conditions, Utility-AI considerations, parameter binding, all round-trippable.

> **Skill file:** [`skills/llm-statetree/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-statetree/SKILL.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Create an AI behavior tree / state machine from a description (idle, patrol, chase, attack, etc.)
- Convert a behavior description into a `.llmstate` file
- Inspect or modify an existing `.llmstate` file
- Look up a StateTree node type (Task, Condition, Evaluator, Consideration)
- Bind parameters and references between nodes
- Use Utility-AI (scored action selection) instead of pure FSM

**Triggers:** `.llmstate`, StateTree, AI, behavior tree, FSM, utility AI, NPC, patrol, chase, attack, condition, task, evaluator, consideration.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM StateTree** plugin | Install from Fab or copy from this repo to `Plugins/` |
| Enabled in editor | Edit → Plugins → AI → **LLM StateTree** → restart editor |
| StateTree engine plugin | Built into UE 5.7; no extra install |

The schema file (`StateTreeNodeSchema.llmstateschema`) is generated from UE reflection at editor startup — the agent reads the latest one to know what tasks/conditions/evaluators are available in *your* project.

---

## Quick Example

Ask the agent:

> "Make me a basic enemy AI: idle for 2 seconds, then chase the player, then attack when in range."

The agent produces a `.llmstate` file:

```json
{
  "name": "SimpleAI",
  "version": "1.0",
  "parameters": [
    { "name": "IdleDuration", "type": "float", "default": 2.0 },
    { "name": "ChaseSpeed",   "type": "float", "default": 600.0 }
  ],
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "Wait",
          "properties": { "Duration": "${Param.IdleDuration}" } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [
        { "type": "StateTreeMoveToTask", "name": "MoveToTarget",
          "properties": { "AcceptableRadius": 50.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Attack" }
      ]
    },
    {
      "name": "Attack",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "AttackCD",
          "properties": { "Duration": 0.5 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Idle" }
      ]
    }
  ]
}
```

Save it, open the LLM StateTree panel, click **Generate** — the StateTree asset is on disk.

---

## What the Skill Knows

The full skill body contains:

- **All node types** — `State`, `Group`, `Selector`, `Sequencer`, plus all registered Tasks / Conditions / Evaluators
- **Selection behaviors** — `TrySelectChildrenInOrder`, `TrySelectChildrenAtRandom`, `TrySelectChildrenByUtilityScore`
- **Transitions** — trigger types (`OnStateCompleted`, `OnCondition`, `OnEvent`), Goto targets
- **Parameters and bindings** — `${Param.Name}` reference syntax, context data binding
- **Utility AI** — `Consideration` node with scoring functions
- **5 example files** — `SimpleAI`, `GuardAI`, `UtilityAI`, `StealthAI`, `BossAI`
- **Auto-generated schema** — points to the editor's "Generate Schema" button for the latest reflection data

---

## Compiling the JSON into an Asset

```
# Manual: editor panel
Tools → LLM StateTree Panel → select .llmstate file → Generate

# CLI (with llm-easy-shell installed)
statetree generate /Game/AI/SimpleAI --from SimpleAI.llmstate
```

The StateTree asset opens in the StateTree editor.

---

## Round-Trip

Already have a StateTree? Use **Export to JSON** in the editor panel to dump it to a `.llmstate` file. The agent edits it, you re-generate.

---

## Related Skills

- [**llm-easy-shell** →](./llm-easy-shell) — drive the editor from the CLI: `statetree generate`, `statetree inspect`, etc.
- [**llm-easy-shell-lite** →](./llm-easy-shell-lite) — read-only `statetree inspect` / `list-types` / `export-schema`.
