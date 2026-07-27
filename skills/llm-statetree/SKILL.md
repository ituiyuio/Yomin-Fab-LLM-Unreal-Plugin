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
  "parameters": {
    "IdleDuration": { "type": "float", "default": 2.0 },
    "ChaseSpeed": { "type": "float", "default": 600.0 }
  },
  "states": [
    {
      "name": "Idle",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "Wait", "properties": { "Duration": "${Parameters.IdleDuration}" } }
      ],
      "transitions": [
        { "trigger": "OnStateCompleted", "type": "GotoState", "target": "Chase" }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [
        { "type": "StateTreeDelayTask", "name": "ChaseWait", "properties": { "Duration": 0.5 } }
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

StateTree 全局参数，可在 Task 中通过 `${Parameters.Name}` 绑定：

```json
"parameters": {
  "PatrolRadius": { "type": "float", "default": 500.0 },
  "ChaseSpeed": { "type": "float", "default": 600.0 },
  "CanAttack": { "type": "bool", "default": true }
}
```

**Types:** `float`, `int`, `bool`, `string`

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

> **⚠️ Schema 状态**: `StateTreeNodeSchema.llmstateschema` 的 `Evaluator` category 当前为 **0 个具体节点**（仅 `Task` 3 / `Condition` 13 / `Consideration` 3）。
> `StateTreeEvaluatorBase` 是 UE 抽象基类，不能直接实例化；需要 AIModule / 项目内具体子类才能 resolve。
> 在 LLMStateTree plugin 补全 Evaluator 节点前，建议用 `parameters` 配合 Task 内读取替代。

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
| `TrySelectChildrenWithHighestUtility` | 选择效用最高的子状态 |

## Node Types

### Tasks

在状态下执行的 Actions：

| Type | Description |
|------|-------------|
| `StateTreeDelayTask` | 延迟等待 |
| `StateTreeDebugTextTask` | 绘制调试文本 |
| `StateTreeRunParallelStateTreeTask` | 并行运行另一个 StateTree |

> **⚠️ 注**: `StateTreeMoveToTask` 不在 `StateTreeNodeSchema.llmstateschema` 的 Task 列表中（AIModule plugin 提供但需显式 enable）。Schema 默认只暴露上表 3 个。

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
| `StateTreeCompareEnumCondition` | 枚举比较 |
| `StateTreeCompareNameCondition` | FName 比较 |
| `StateTreeCompareDistanceCondition` | 距离比较 |
| `GameplayTagMatchCondition` | GameplayTag 匹配 |
| `GameplayTagContainerMatchCondition` | Tag 容器匹配 |
| `GameplayTagQueryCondition` | Tag Query 容器匹配 |
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
    "conditions": [
      {
        "type": "StateTreeCompareDistanceCondition",
        "properties": { "Operator": "Less", "Distance": 500.0 }
      }
    ]
  }
]
```

> **⚠️ 注**: transition 字段是 **`conditions`**（复数数组），不是 `condition`。Parser 在 `LLMStateTreeParser.cpp:442/718` 用 `GetArrayField("conditions")`，单数 `condition` 会被静默丢弃。

<!-- Forensic: see SKILL_CHANGELOG.md §1 (tool-fix-172 2026-06-29 line drift closure) -->

**Transition Triggers:**
| Trigger | Description |
|---------|-------------|
| `OnStateCompleted` | 状态完成时 |
| `OnCondition` | 条件满足时 |
| `OnStateSucceeded` | Task 成功时 |
| `OnStateFailed` | Task 失败时 |

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
  "Duration": "${Parameters.IdleDuration}",
  "MovementSpeed": "${Parameters.ChaseSpeed}"
}
```

**Binding Scopes:**
| Scope | Example |
|-------|---------|
| `${Parameters.Name}` | 全局参数 |
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
        { "type": "StateTreeDelayTask", "name": "MoveWait", "properties": { "Duration": 0.5 } }
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
    { "type": "StateTreeDelayTask", "name": "ChaseCooldown", "properties": { "Duration": 0.5 } }
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
  "conditions": [
    {
      "type": "StateTreeCompareDistanceCondition",
      "properties": {
        "Distance": 500.0,
        "Operator": "Less"
      }
    }
  ]
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
  "selectionBehavior": "TrySelectChildrenWithHighestUtility",
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
      "tasks": [{ "type": "StateTreeDelayTask", "name": "MoveWait", "properties": { "Duration": 1.0 } }],
      "transitions": [
        { "trigger": "OnCondition", "type": "GotoState", "target": "Chase", "conditions": [{ ... }] }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [{ "type": "StateTreeDelayTask", "name": "ChaseWait", "properties": { "Duration": 0.5 } }],
      "transitions": [
        { "trigger": "OnCondition", "type": "GotoState", "target": "Patrol", "conditions": [{ ... }] }
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
  "parameters": {
    "PatrolRadius": { "type": "float", "default": 500.0 },
    "ChaseSpeed": { "type": "float", "default": 600.0 },
    "DetectionRange": { "type": "float", "default": 800.0 },
    "AttackRange": { "type": "float", "default": 150.0 }
  },
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
            { "type": "StateTreeDelayTask", "name": "MoveWait", "properties": { "Duration": 1.0 } }
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
          "conditions": [
            {
              "type": "StateTreeCompareDistanceCondition",
              "properties": { "Distance": "${Parameters.DetectionRange}", "Operator": "Less" }
            }
          ]
        }
      ]
    },
    {
      "name": "Chase",
      "type": "State",
      "tasks": [
        {
          "type": "StateTreeDelayTask",
          "name": "ChaseWait",
          "properties": { "Duration": 0.5 }
        }
      ],
      "transitions": [
        {
          "trigger": "OnCondition",
          "type": "GotoState",
          "target": "Attack",
          "conditions": [
            {
              "type": "StateTreeCompareDistanceCondition",
              "properties": { "Distance": "${Parameters.AttackRange}", "Operator": "Less" }
            }
          ]
        },
        {
          "trigger": "OnCondition",
          "type": "GotoState",
          "target": "Patrol",
          "conditions": [
            {
              "type": "StateTreeCompareDistanceCondition",
              "properties": { "Distance": "${Parameters.DetectionRange}", "Operator": "Greater" }
            }
          ]
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

> **Note**: 实际命令名是 **`llmstatetree`**（带 `llm` 前缀）。直接打 `statetree` 会被 LLMEasyShellSubsystem 的 `CommandToAbilityMap` 判为 unknown ability，返回 `"Unknown command: statetree"`（LLMEasyShellSubsystem.cpp:977 `EShellErrorCode::NotFound` 分支）。
>
<!-- Forensic: see SKILL_CHANGELOG.md §2 (tool-fix-156 2026-06-29 cross-subsystem misattribution) -->

生成 StateTree:
```bash
llmstatetree generate /Game/AI/GuardAI --from GuardAI.llmstate
```

检查 StateTree:
```bash
llmstatetree inspect /Game/AI/GuardAI --states
```

导出 StateTree:
```bash
llmstatetree export /Game/AI/GuardAI --output C:/Temp/AI.llmstate
```

复制 StateTree (序列化 → 重新生成到新路径):
```bash
llmstatetree copy /Game/AI/GuardAI /Game/AI/GuardAI_v2
```

删除 StateTree 资产 (`--force` 跳过脏数据确认):
```bash
llmstatetree delete /Game/AI/GuardAI --force
```

强制 StateTree 重新编译 (绕过 cached 空 state, PIE 之前必跑):
```bash
llmstatetree compile /Game/AI/GuardAI
```

<!-- Forensic: see SKILL_CHANGELOG.md §3 (tool-fix-07 session60 3→6 sub-cmd silent-missing closure) -->

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
