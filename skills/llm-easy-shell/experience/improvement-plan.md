# LLMEasyShell 体验改进计划

## 痛点分析

### 1. 路径格式容易混淆
**现状:**
- `/Actor/Name` - 场景中Actor
- `/Game/Path` - 资产（UE标准路径）
- `/Assets/Path` - 资产（别名）
- `find Actor xxx` vs `find Asset xxx`

**问题:** 每次都要查文档确认格式

**改进方案:**
```
# 智能路径解析 - 自动推断类型
ls Actor Cube          # 自动转为 /Actor/Cube
ls Game BP_Player      # 自动转为 /Game/BP_Player
cat BP_Player          # 智能识别：场景中有就用Actor，资产中有就用Asset
```

### 2. find 命令 type 参数反直觉
**现状:**
```bash
find Actor Enemy*      # 搜索场景Actor
find Asset *Enemy*     # 搜索资产
```

**问题:** "Asset" 不是复数 "Actors"，容易搞混；类型参数没有帮助提示

**改进方案:**
```bash
find enemy            # 智能：同时搜 Actor 和 Asset，返回合并结果 + 来源标注
find Actor Enemy*     # 明确指定类型，保留原有用法
find --help          # 显示所有类型及说明
```

### 3. discover 输出信息不足
**现状:**
```bash
discover /Actor/Player --funcs
# 只返回函数名和参数，无法看到：
# - BlueprintImplementableEvent vs cpp 函数
# - 函数功能描述
# - 调用示例
```

**改进方案:**
```bash
discover /Actor/Player --funcs --verbose
# 返回：
# {
#   "name": "Attack",
#   "params": "Damage:float",
#   "type": "BlueprintImplementableEvent",  # 新增
#   "description": "Trigger attack animation and apply damage",  # 新增
#   "example": "call /Actor/Player Attack --Damage 10.0"  # 新增
# }
```

### 4. 连接不稳定
**现状:** 引擎负载高时 `Failed to connect to 127.0.0.1:15153`

**改进方案:**
```bash
# 自动重试 + 状态缓存
llm-shell -c "info" --retry 3 --retry-delay 1

# info 命令显示上次已知状态（不依赖连接）
info --cached  # 返回 {"source": "cache", "level": "Lvl_Test", "cached_at": "..."}
```

### 5. Blueprint 内部逻辑不可见
**现状:** `discover` 只能看到函数签名，无法看到 EventGraph

**改进方案:**
```bash
# 查看 Blueprint 事件流
blueprint events /Game/BP_Player
# 返回 Blueprint 中所有 Event 和它们连接的节点

# 查看特定事件的实现
blueprint trace /Game/BP_Player OnTakeDamage
# 返回完整的 Event Graph 链路
```

### 6. 错误信息不够友好
**现状:**
```
Actor not found
Asset not found
Unknown type: /X
```

**改进方案:**
```
# 自动纠错 + 建议
> cat /Actor/Player
Actor 'Player' not found. Did you mean:
  - /Actor/Player0 (exact match in current session)
  - /Actor/PlayerStart (partial match)
  - /Game/Features/Survivor/BP_Player (similar name in assets)

> find Actor Enemy
Unknown type 'Actor'. Valid types: Actor, Asset, Class
Tip: Use 'ls --types' to see all available types
```

---

## 优先级排序

| 优先级 | 改进项 | 工作量 | 价值 | 状态 |
|--------|--------|--------|------|------|
| P0 | 路径智能解析 | 中 | 高 | 长期 |
| P0 | find --help 和智能搜索 | 小 | 高 | ✅ DONE |
| P1 | discover --verbose 增强输出 | 小 | 高 | TODO |
| P1 | 连接自动重试 | 小 | 中 | TODO |
| P2 | Blueprint 事件流 | 大 | 中 | TODO |
| P2 | 错误信息优化 + info --cached | 小 | 中 | ✅ DONE |
| P2 | Blueprint 组件子属性导航 | 小 | 高 | ✅ DONE |

---

## 实施步骤

### Phase 1: 小改动，大收益（可立即做）
1. `find` 命令添加 `--help` 显示所有类型 ✅
2. 错误信息增加" Did you mean:"建议 ✅
3. `info --cached` 缓存最后状态 ✅

### Phase 2: 智能解析
1. `ls` / `cat` 自动识别路径类型
2. `find` 智能同时搜 Actor + Asset

### Phase 3: Blueprint 可视化
1. 添加 `blueprint` Python ability
2. 实现 `blueprint events` 和 `blueprint trace`

---

## 负责 Agent
- LLMEasyShell Core 改进 → 需要修改 C++ CommandDispatcher
- Blueprint 可视化 → Python ability 实现

---

## 已完成实现细节 (2026-05-05)

### P0.2 错误信息优化 ✅
**文件**: `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/CommandDispatcher.cpp`
- 新增 `FindSimilarCommand()` 方法 - 使用 Levenshtein 距离查找相似命令
- 新增 `EditDistance()` 方法 - 计算两个字符串的编辑距离
- 阈值: 命令名距离≤3，别名距离≤2
- 当命令不存在时，自动建议相似命令

**文件**: `Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellTypes.h`
- 新增 `FindSimilarCommand()` 和 `EditDistance()` 方法声明

### P0.3 info --cached ✅
**文件**: `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Info.cpp`
- 新增 `--cached` / `-c` 标志检测
- 缓存 info 输出到 subsystem
- 返回时自动添加 `source: "cache"` 和 `cached_at` 字段

**文件**: `Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellSubsystem.h`
- 新增 `CachedInfo` 成员变量存储缓存
- 新增 `GetCachedInfo()` 和 `SetCachedInfo()` 方法

### 改进的错误提示
**文件**: `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Find.cpp`
- 未知类型错误增加 `Tip: Use 'find --help' to see all types` 提示
