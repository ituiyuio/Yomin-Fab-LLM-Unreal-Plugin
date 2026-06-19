# Node Types

LLMStateTree supports the following StateTree node types. All node types are automatically discovered from UE reflection via the schema system.

**Schema File:** `Config/Schemas/StateTreeNodeSchema.llmstateschema`

---

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

---

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

---

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

---

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

---

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

---

## Binding Expressions

Use `${}` syntax to reference parameters and context data:

- `${Param.Speed}` - Reference a parameter
- `${Context.Target.Location}` - Reference context property
- `${Param.IdleDuration * 2}` - Expressions supported
