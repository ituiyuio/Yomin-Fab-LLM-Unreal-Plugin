---
name: llm-statetree
description: |
  LLMStateTree is a DSL-driven UE5 StateTree asset generation system. Use this skill when users need to:
  (1) Create or design UE5 StateTree AI behavior trees (idle, patrol, chase, attack, etc.)
  (2) Convert AI behavior descriptions into generatable DSL format (.llmstate JSON)
  (3) Understand or modify existing StateTree DSL definitions
  (4) Learn about supported node types (State, Group, Selector, Sequencer, Tasks, Conditions, Considerations)
  (5) Query binding expression syntax and context data references
---

# LLM StateTree - DSL Schema Guide

### **Composition Over Inheritance**

## File Format

StateTree definition files use the `.llmstate` extension (LLM StateTree DSL), formatted as JSON.

## Reference Files

**Schema File**: `Config/Schemas/StateTreeNodeSchema.llmstateschema` - Contains complete node type definitions discovered from UE reflection

**Examples Directory**: `Config/Examples/` - Contains complete AI behavior example `.llmstate` files

**Samples**:
- `SimpleAI.llmstate` - Basic AI with Idle, Patrol, Chase, Attack states
- `GuardAI.llmstate` - Guard NPC with patrol, investigate, chase, return home
- `UtilityAI.llmstate` - Utility AI with considerations for action selection
- `StealthAI.llmstate` - Stealth AI with hide, sneak, detect, escape states
- `BossAI.llmstate` - Boss AI with multiple phases based on health thresholds

## Quick Start

```json
{
  "name": "MyAI",
  "version": "1.0",
  "parameters": [
    { "name": "PatrolRadius", "type": "float", "default": 500.0 },
    { "name": "ChaseSpeed", "type": "float", "default": 600.0 }
  ],
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
    },
    {
      "name": "Patrol",
      "type": "Group",
      "selectionBehavior": "TrySelectChildrenInOrder",
      "children": [
        {
          "name": "Patrol_Move",
          "type": "State",
          "tasks": [
            { "type": "StateTreeDelayTask", "properties": { "Duration": 0.0 } }
          ]
        }
      ]
    }
  ]
}
```

## State Types

### State

Basic state that executes tasks and transitions to other states.

```json
{
  "name": "Idle",
  "type": "State",
  "tasks": [...],
  "transitions": [...]
}
```

### Group

Container state that manages child states with a selection behavior.

```json
{
  "name": "Patrol",
  "type": "Group",
  "selectionBehavior": "TrySelectChildrenInOrder",
  "children": [...]
}
```

### Selector

Utility AI selector - evaluates children and selects highest utility.

```json
{
  "name": "SelectAction",
  "type": "Selector",
  "selectionBehavior": "UtilityMax",
  "children": [...]
}
```

### Sequencer

Executes children in sequence, succeeds when all complete.

```json
{
  "name": "AttackSequence",
  "type": "Sequencer",
  "children": [...]
}
```

## Tasks

Tasks are behaviors executed within a state.

### StateTreeDelayTask

Wait for a specified duration before succeeding.

| Property | Type | Description |
|----------|------|-------------|
| `Duration` | float | Time to wait in seconds |
| `RandomDeviation` | float | Random deviation range |
| `bRunForever` | bool | Run indefinitely |

### StateTreeMoveToTask

Move to a target location (from GameplayStateTree module).

| Property | Type | Description |
|----------|------|-------------|
| `AcceptableRadius` | float | Distance to consider arrival |

### StateTreeRunParallelStateTreeTask

Run another StateTree in parallel.

| Property | Type | Description |
|----------|------|-------------|
| `StateTree` | object | Reference to another StateTree asset |
| `PropertyOverrides` | array | Property override bindings |

### StateTreeDebugTextTask

Draw debug text on HUD.

| Property | Type | Description |
|----------|------|-------------|
| `Text` | string | Debug text to display |
| `TextColor` | color | Text color |
| `FontScale` | float | Font scale |
| `Offset` | vector | Screen offset |
| `ReferenceActor` | object | Actor to attach text to |

## Conditions

Conditions are boolean checks for transitions.

### StateTreeCompareIntCondition

Compare two integers.

| Property | Type | Description |
|----------|------|-------------|
| `Operator` | enum | Less, LessOrEqual, Equal, NotEqual, GreaterOrEqual, Greater, IsTrue |
| `Left` | int | Left operand |
| `Right` | int | Right operand |

### StateTreeCompareFloatCondition

Compare two floats.

| Property | Type | Description |
|----------|------|-------------|
| `Operator` | enum | Less, LessOrEqual, Equal, NotEqual, GreaterOrEqual, Greater, IsTrue |
| `Left` | float | Left operand |
| `Right` | float | Right operand |

### StateTreeCompareBoolCondition

Compare two booleans.

| Property | Type | Description |
|----------|------|-------------|
| `bLeft` | bool | Left operand |
| `bRight` | bool | Right operand |

### StateTreeCompareEnumCondition

Compare two enum values.

| Property | Type | Description |
|----------|------|-------------|
| `Value` | enum | Enum value to compare |
| `Enum` | object | Enum type reference |

### StateTreeCompareNameCondition

Compare two FName values.

| Property | Type | Description |
|----------|------|-------------|
| `Left` | name | Left operand |
| `Right` | name | Right operand |

### StateTreeCompareDistanceCondition

Compare distance between two vectors.

| Property | Type | Description |
|----------|------|-------------|
| `Operator` | enum | Less, LessOrEqual, Equal, NotEqual, GreaterOrEqual, Greater |
| `Source` | vector | Source location |
| `Target` | vector | Target location |
| `Distance` | float | Distance to compare against |

### StateTreeRandomCondition

Random chance condition.

| Property | Type | Description |
|----------|------|-------------|
| `Threshold` | float | Probability threshold (0-1) |

### GameplayTagMatchCondition

Check if actor has a gameplay tag.

| Property | Type | Description |
|----------|------|-------------|
| `Tag` | gameplaytag | Tag to check |
| `GameplayTags` | array | Tag container |
| `bExactMatch` | bool | Require exact match |

### GameplayTagContainerMatchCondition

Check tag container against another container.

| Property | Type | Description |
|----------|------|-------------|
| `MatchType` | enum | Any or All |
| `GameplayTags` | array | Tags to match against |

### GameplayTagQueryCondition

Check against a Tag Query expression.

### StateTreeObjectIsValidCondition

Check if an object is valid.

| Property | Type | Description |
|----------|------|-------------|
| `Object` | object | Object to check |

### StateTreeObjectEqualsCondition

Check if two objects are the same.

| Property | Type | Description |
|----------|------|-------------|
| `Left` | object | Left object |
| `Right` | object | Right object |

### StateTreeObjectIsChildOfClassCondition

Check if object is of a specific class.

| Property | Type | Description |
|----------|------|-------------|
| `Object` | object | Object to check |
| `Class` | object | Class to check against |

## Considerations

Considerations are utility AI factors that produce a score.

### StateTreeConstantConsideration

Constant score.

| Property | Type | Description |
|----------|------|-------------|
| `Constant` | float | Fixed score value |

### StateTreeFloatInputConsideration

Score based on float input with response curve.

| Property | Type | Description |
|----------|------|-------------|
| `Input` | float | Raw input value |
| `Min` | float | Minimum input |
| `Max` | float | Maximum input |
| `DefaultValue` | float | Default when out of range |
| `Keys` | array | Response curve keys |

### StateTreeEnumInputConsideration

Enum-based consideration for Utility AI.

## Transitions

Transitions define how the AI moves between states.

```json
{
  "trigger": "OnStateCompleted",
  "type": "GotoState",
  "target": "Patrol"
}
```

### Trigger Types

- `OnStateCompleted` - State finished executing
- `OnStateFailed` - State reported failure
- `OnEvent` - Custom event received

### Transition Types

- `GotoState` - Move to specified state
- `EvaluateConditions` - Evaluate conditions before transition

## Binding Expressions

Use `${}` syntax to reference parameters and context data:

- `${Param.Speed}` - Reference a parameter
- `${Context.Target.Location}` - Reference context property
- `${Param.IdleDuration * 2}` - Expressions supported

## Parameters

Define parameters that can be set when assigning the StateTree to an AI character:

```json
{
  "parameters": [
    { "name": "PatrolRadius", "type": "float", "default": 500.0 },
    { "name": "ChaseSpeed", "type": "float", "default": 600.0 },
    { "name": "AlertRadius", "type": "float", "default": 1000.0 }
  ]
}
```

**Supported Types**: `float`, `int`, `bool`, `vector`, `gameplaytag`

## Selection Behaviors

### Group Selection Behaviors

| Behavior | Description |
|----------|-------------|
| `TrySelectChildrenInOrder` | Evaluate children in order, select first eligible |
| `TrySelectChildrenInRandomOrder` | Evaluate children in random order |
| `SelectMostDesirableChild` | Select child with highest priority |

### Selector (Utility AI) Selection Behaviors

| Behavior | Description |
|----------|-------------|
| `UtilityMax` | Select child with highest utility score |
| `WeightedRandom` | Select child based on weighted random |

## Common Patterns

### Simple Patrol Loop
```json
{
  "name": "SimplePatrol",
  "parameters": [
    { "name": "PatrolRadius", "type": "float", "default": 500.0 }
  ],
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
    },
    {
      "name": "Patrol",
      "type": "Group",
      "selectionBehavior": "TrySelectChildrenInOrder",
      "children": [
        {
          "name": "Patrol_Move",
          "type": "State",
          "tasks": [
            { "type": "StateTreeDelayTask", "properties": { "Duration": 0.0 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Wait" }
          ]
        },
        {
          "name": "Patrol_Wait",
          "type": "State",
          "tasks": [
            { "type": "StateTreeDelayTask", "properties": { "Duration": 1.0, "RandomVariance": 0.3 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Move" }
          ]
        }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Idle" }
      ]
    }
  ]
}
```

### Utility AI with Considerations
```json
{
  "name": "UtilityAI",
  "parameters": [
    { "name": "MaxHealth", "type": "float", "default": 100.0 },
    { "name": "LowHealthThreshold", "type": "float", "default": 30.0 }
  ],
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "properties": { "Duration": 0.5 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "SelectAction" }
      ]
    },
    {
      "name": "SelectAction",
      "type": "Selector",
      "selectionBehavior": "UtilityMax",
      "children": [
        {
          "name": "Flee",
          "type": "State",
          "considerations": [
            {
              "type": "StateTreeFloatInputConsideration",
              "properties": {
                "Min": 0.0,
                "Max": 100.0,
                "DefaultValue": 50.0
              }
            }
          ],
          "tasks": [
            { "type": "StateTreeDelayTask", "properties": { "Duration": 2.0 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Idle" }
          ]
        },
        {
          "name": "Attack",
          "type": "State",
          "considerations": [
            { "type": "StateTreeConstantConsideration", "properties": { "Constant": 0.8 } }
          ],
          "tasks": [
            { "type": "StateTreeDelayTask", "properties": { "Duration": 0.5 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Idle" }
          ]
        }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Idle" }
      ]
    }
  ]
}
```

### Guard AI with Conditional Transitions
```json
{
  "name": "GuardAI",
  "parameters": [
    { "name": "AlertRadius", "type": "float", "default": 800.0 },
    { "name": "VisionAngle", "type": "float", "default": 90.0 }
  ],
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "properties": { "Duration": 3.0, "RandomVariance": 1.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol" }
      ]
    },
    {
      "name": "Patrol",
      "type": "Group",
      "selectionBehavior": "TrySelectChildrenInOrder",
      "children": [...]
    }
  ]
}
```

## Editor Workflow

1. Enable required engine plugins: StateTree, GameplayStateTree, EditorScriptingUtilities
2. Open the LLMStateTree Editor Panel: Window → LLMStateTree Panel
3. Click "Load File" and navigate to `.llmstate` file
4. Click "Generate StateTree" to create the StateTree Blueprint asset
5. Assign the generated StateTree to your AI Controller or Character

## File Location

Place `.llmstate` files in your project's `Config/Examples/` folder for easy access:

```
YourProject/
└── Config/
    └── Examples/
        ├── SimpleAI.llmstate
        ├── GuardAI.llmstate
        ├── UtilityAI.llmstate
        ├── StealthAI.llmstate
        ├── BossAI.llmstate
        └── MyAI.llmstate
```

## Dependencies

| Plugin | Type | Required |
|--------|------|----------|
| StateTree | Engine | Yes |
| GameplayStateTree | Engine | Yes |
| EditorScriptingUtilities | Engine | Yes (Editor only) |
