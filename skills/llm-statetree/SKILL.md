---
name: llm-statetree
description: |
  StateTree DSL 生成技能。当用户需要：
  (1) 创建 AI 行为树、状态机的 DSL 定义（.llmstate 文件）
  (2) 将行为逻辑描述转换为 llmstate JSON 格式
  (3) 理解 StateTree 节点类型（Task、Condition、Evaluator、Consideration）
  (4) 需要 StateTree 代码示例（巡逻、追逐、攻击、技能等）
  (5) 修改或扩展现有 llmstate 文件
  请使用此技能。
---

# LLM StateTree - DSL Schema Guide

### **组合优于继承**

## File Format

StateTree 定义使用 `.llmstate` 扩展名，格式为 JSON。

## Reference Files

**Node Schema**: `Plugins/LLMStateTree/Config/Schemas/StateTreeNodeSchema.llmstateschema` - 包含所有 StateTree 节点类型的完整定义、属性类型、默认值

**Examples**: `Plugins/LLMStateTree/Config/Examples/` - 包含完整的 AI 示例文件

**导出 Schema**: 在编辑器中点击 "Generate Schema" 按钮生成最新节点定义

## Quick Start

```json
{
  "name": "SimpleAI",
  "version": "1.0",
  "parameters": [
    { "name": "IdleDuration", "type": "float", "default": 2.0 },
    { "name": "ChaseSpeed", "type": "float", "default": 600.0 }
  ],
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "Wait", "properties": { "Duration": "${Param.IdleDuration}" } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [
        { "type": "StateTreeMoveToTask", "name": "MoveToTarget", "properties": { "AcceptableRadius": 50.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Attack" }
      ]
    },
    {
      "name": "Attack",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "AttackCD", "properties": { "Duration": 0.5 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
      ]
    }
  ]
}
```

## Core Concepts

### Parameters

StateTree 全局参数，可在 Task 中通过 `${Param.Name}` 绑定：

```json
"parameters": [
  { "name": "PatrolRadius", "type": "float", "default": 500.0 },
  { "name": "ChaseSpeed", "type": "float", "default": 600.0 },
  { "name": "CanAttack", "type": "bool", "default": true }
]
```

**Types:** `float`, `int`, `bool`, `string`, `vector`, `rotator`

### Evaluators

在 StateTree 启动时评估的节点，每帧提供上下文数据：

```json
"evaluators": [
  {
    "type": "StateTreeEvaluatorBase",
    "name": "DistanceToTarget",
    "properties": { "TargetKey": "TargetActor" }
  }
]
```

### States

StateTree 的核心，定义 AI 状态和转换：

```json
{
  "name": "Idle",
  "type": "State",
  "tasks": [...],
  "transitions": [...]
}
```

**State Types:**
| Type | Description |
|------|-------------|
| `State` | 普通状态，可包含 Tasks |
| `Group` | 状态组，可包含子状态，用于选择行为 |
| `Linked` | 链接到外部 StateTree |

**Selection Behaviors (用于 Group):**
| Behavior | Description |
|----------|-------------|
| `TrySelectChildrenInOrder` | 按顺序尝试选择子状态 |
| `SelectBehaviorChildWithHighestUtility` | 选择效用最高的子状态 |

## Node Types

### Tasks

在状态下执行的 Actions：

| Type | Description |
|------|-------------|
| `StateTreeDelayTask` | 延迟等待 |
| `StateTreeMoveToTask` | 移动到目标/位置 |
| `StateTreeDebugTextTask` | 绘制调试文本 |
| `StateTreeRunParallelStateTreeTask` | 并行运行另一个 StateTree |

**Common Task Properties:**
```json
{
  "type": "StateTreeDelayTask",
  "name": "Wait",
  "properties": {
    "Duration": 2.0,
    "RandomDeviation": 0.5
  }
}
```

### Conditions

状态转换条件判断：

| Type | Description |
|------|-------------|
| `StateTreeCompareFloatCondition` | 浮点数比较 |
| `StateTreeCompareIntCondition` | 整数比较 |
| `StateTreeCompareBoolCondition` | 布尔比较 |
| `StateTreeCompareDistanceCondition` | 距离比较 |
| `GameplayTagMatchCondition` | GameplayTag 匹配 |
| `GameplayTagContainerMatchCondition` | Tag 容器匹配 |
| `StateTreeObjectIsValidCondition` | 对象有效性检查 |
| `StateTreeObjectEqualsCondition` | 对象相等检查 |
| `StateTreeObjectIsChildOfClassCondition` | 类继承检查 |
| `StateTreeRandomCondition` | 随机条件 |

**Condition Operators:** `Less`, `LessOrEqual`, `Equal`, `NotEqual`, `GreaterOrEqual`, `Greater`, `IsTrue`

**Example:**
```json
{
  "type": "StateTreeCompareDistanceCondition",
  "properties": {
    "Distance": 500.0,
    "Operator": "Less"
  }
}
```

### Considerations

Utility AI 效用计算因子：

| Type | Description |
|------|-------------|
| `StateTreeConstantConsideration` | 常量考虑因素 |
| `StateTreeFloatInputConsideration` | 浮点数输入效用曲线 |
| `StateTreeEnumInputConsideration` | 枚举输入效用曲线 |

## Transitions

状态转换定义：

```json
"transitions": [
  {
    "trigger": "OnStateCompleted",
    "type": "GotoState",
    "target": "Patrol"
  },
  {
    "trigger": "OnCondition",
    "type": "GotoState",
    "target": "Chase",
    "condition": {
      "type": "StateTreeCompareDistanceCondition",
      "properties": { "Operator": "Less", "Distance": 500.0 }
    }
  }
]
```

**Transition Triggers:**
| Trigger | Description |
|---------|-------------|
| `OnStateCompleted` | 状态完成时 |
| `OnCondition` | 条件满足时 |
| `OnSucceeded` | Task 成功时 |
| `OnFailed` | Task 失败时 |

**Transition Types:**
| Type | Description |
|------|-------------|
| `GotoState` | 跳转到指定状态 |
| `SelectChildren` | 选择子状态（用于 Group） |
| `Restart` | 重新开始当前状态 |
| `Stop` | 停止 StateTree |

## Property Binding

使用 `${Scope.Name.Property}` 语法绑定属性：

```json
"properties": {
  "Duration": "${Param.IdleDuration}",
  "AcceptableRadius": 100.0,
  "MovementSpeed": "${Param.ChaseSpeed}"
}
```

**Binding Scopes:**
| Scope | Example |
|-------|---------|
| `${Param.Name}` | 全局参数 |
| `${Evaluators.Name.Property}` | Evaluator 属性 |
| `${Context.Name}` | Context 属性（由 Schema 定义） |

## Common Patterns

### 巡逻循环 (Patrol Loop)
```json
{
  "name": "Patrol",
  "type": "Group",
  "selectionBehavior": "TrySelectChildrenInOrder",
  "children": [
    {
      "name": "Patrol_Move",
      "type": "State",
      "tasks": [
        { "type": "StateTreeMoveToTask", "name": "Move", "properties": { "AcceptableRadius": 100.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Wait" }
      ]
    },
    {
      "name": "Patrol_Wait",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "Wait", "properties": { "Duration": 1.0 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Move" }
      ]
    }
  ]
}
```

### 追逐-攻击循环 (Chase-Attack Loop)
```json
{
  "name": "Chase",
  "type": "State",
  "tasks": [
    { "type": "StateTreeMoveToTask", "name": "ChaseTarget", "properties": { "AcceptableRadius": 50.0 } }
  ],
  "transitions": [
    { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Attack" }
  ]
},
{
  "name": "Attack",
  "type": "State",
  "tasks": [
    { "type": "StateTreeDelayTask", "name": "AttackCooldown", "properties": { "Duration": 0.5 } }
  ],
  "transitions": [
    { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
  ]
}
```

### 距离触发转换 (Distance-Triggered Transition)
```json
{
  "trigger": "OnCondition",
  "type": "GotoState",
  "target": "Chase",
  "condition": {
    "type": "StateTreeCompareDistanceCondition",
    "properties": {
      "Distance": 500.0,
      "Operator": "Less"
    }
  }
}
```

### 带随机变量的延迟 (Delay with Random Variance)
```json
{
  "type": "StateTreeDelayTask",
  "name": "Wait",
  "properties": {
    "Duration": 2.0,
    "RandomDeviation": 0.5
  }
}
```

### 待机-巡逻-追逐切换
```json
{
  "name": "Root",
  "type": "Group",
  "selectionBehavior": "SelectBehaviorChildWithHighestUtility",
  "children": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [{ "type": "StateTreeDelayTask", "name": "Wait", "properties": { "Duration": 1.0 } }],
      "transitions": [{ "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol" }]
    },
    {
      "name": "Patrol",
      "type": "State",
      "tasks": [{ "type": "StateTreeMoveToTask", "name": "Move", "properties": {} }],
      "transitions": [
        { "trigger": "OnCondition", "type": "GotoState", "target": "Chase", "condition": { ... } }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [{ "type": "StateTreeMoveToTask", "name": "Chase", "properties": {} }],
      "transitions": [
        { "trigger": "OnCondition", "type": "GotoState", "target": "Patrol", "condition": { ... } }
      ]
    }
  ]
}
```

## Full Example: Guard AI

```json
{
  "name": "GuardAI",
  "version": "1.0",
  "description": "Guard AI with patrol, chase, and attack states",
  "parameters": [
    { "name": "PatrolRadius", "type": "float", "default": 500.0 },
    { "name": "ChaseSpeed", "type": "float", "default": 600.0 },
    { "name": "DetectionRange", "type": "float", "default": 800.0 },
    { "name": "AttackRange", "type": "float", "default": 150.0 }
  ],
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "LookAround", "properties": { "Duration": 2.0, "RandomDeviation": 0.5 } }
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
            { "type": "StateTreeMoveToTask", "name": "MoveToPoint", "properties": { "AcceptableRadius": 100.0 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Wait" }
          ]
        },
        {
          "name": "Patrol_Wait",
          "type": "State",
          "tasks": [
            { "type": "StateTreeDelayTask", "name": "Wait", "properties": { "Duration": 1.0, "RandomDeviation": 0.3 } }
          ],
          "transitions": [
            { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Patrol_Move" }
          ]
        }
      ],
      "transitions": [
        {
          "trigger": "OnCondition",
          "type": "GotoState",
          "target": "Chase",
          "condition": {
            "type": "StateTreeCompareDistanceCondition",
            "properties": { "Distance": "${Param.DetectionRange}", "Operator": "Less" }
          }
        }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [
        {
          "type": "StateTreeMoveToTask",
          "name": "ChaseTarget",
          "properties": {
            "AcceptableRadius": 50.0,
            "MovementSpeed": "${Param.ChaseSpeed}"
          }
        }
      ],
      "transitions": [
        {
          "trigger": "OnCondition",
          "type": "GotoState",
          "target": "Attack",
          "condition": {
            "type": "StateTreeCompareDistanceCondition",
            "properties": { "Distance": "${Param.AttackRange}", "Operator": "Less" }
          }
        },
        {
          "trigger": "OnCondition",
          "type": "GotoState",
          "target": "Patrol",
          "condition": {
            "type": "StateTreeCompareDistanceCondition",
            "properties": { "Distance": "${Param.DetectionRange}", "Operator": "Greater" }
          }
        }
      ]
    },
    {
      "name": "Attack",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "AttackCooldown", "properties": { "Duration": 0.8 } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
      ]
    }
  ]
}
```

## CLI Commands

生成 StateTree:
```bash
statetree generate /Game/AI/GuardAI --from GuardAI.llmstate
```

检查 StateTree:
```bash
statetree inspect /Game/AI/GuardAI --states
```

导出 StateTree:
```bash
statetree export /Game/AI/GuardAI --output C:/Temp/AI.llmstate
```
