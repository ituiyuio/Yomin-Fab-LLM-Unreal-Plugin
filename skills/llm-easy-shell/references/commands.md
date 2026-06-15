# 命令参考

## 命令分类总览

| 分类 | 来源 | 说明 |
|------|------|------|
| **原生命令** | `CommandDispatcher` 直接注册 | 内核自带，27 个 |
| **内置 Ability** | `RegisterAbilityJson` 注册 | actor、editor 两个 Ability |
| **插件 Ability** | 外部插件注册 | LLMVFX、LLMMat 等（`statetree` 未注册） |

---

## 原生命令（Core）

共 27 个，直接通过 `CommandDispatcher` 注册，不依赖 Ability 系统。

### 资产操作

| 命令 | 功能 | 示例 |
|------|------|------|
| `ls` | 列出 Actor/资产 | `ls /Level/Actors` |
| `cat` | 查看详情 | `cat /Actor/Cube` |
| `find` | 搜索 | `find Actor Enemy*` |
| `new` | 新建资产 | `new Blueprint MyBP --parent ACharacter` |
| `addcomp` | 添加组件到蓝图 | `addcomp /Assets/BP_MyActor WidgetComponent as BackgroundWidget` |
| `mkdir` | 创建目录 | `mkdir /Assets/NewFolder` |
| `cp` | 复制 | `cp /Actor/Cube Cube_Copy` |
| `mv` | 重命名/移动 | `mv /Actor/Cube NewCube` |
| `rm` | 删除 Actor/资产 | `rm /Actor/Cube` |

### Actor 操作

| 命令 | 功能 | 示例 |
|------|------|------|
| `spawn` | 创建 Actor | `spawn PointLight at (0,0,100) as Light` |
| `set` | 修改属性 | `set /Actor/Cube/Location (0,0,0)` |
| `call` | 调用函数 | `call /Actor/Door Open` |
| `discover` | 查看函数/属性 | `discover /Actor/Cube --funcs` |
| `select` | 选择 | `select /Actor/Cube` |
| `focus` | 聚焦 | `focus /Actor/Cube` |

### 编辑器控制

| 命令 | 功能 | 示例 |
|------|------|------|
| `play` | 开始 PIE | `play` / `play --simulated`（Simulate-in-Editor） |
| `stop` | 停止 PIE | `stop` |
| `pause` | 暂停/恢复 | `pause` |
| `save` | 保存 | `save` / `save /Assets/BP` |
| `undo` | 撤销 | `undo` / `undo 3` |
| `redo` | 重做 | `redo` / `redo 2` |
| `livecoding` | 热重载 | `livecoding` |

### 信息查询

| 命令 | 功能 | 示例 |
|------|------|------|
| `info` | 项目信息 + 编辑器状态 | `info` |
| `help` | 帮助 | `help` / `help spawn` |
| `log` | 日志 | `log --compile --errors` |
| `msglog` | MessageLog 查询 | `msglog` |
| `gamestate` | 游戏状态查询（wave/health/gold/exp/enemies） | `gamestate` |

> `livelog` 已弃用，用 `log --compile` 代替。

---

## 内置 Ability

通过 `RegisterAbilityJson` 注册的命令组，需要加前缀调用。

### actor Ability

```bash
actor spawn/rm/cp/mv/select/focus/call/set
actor spawn PointLight at (0,0,100) as Light
```

等价于直接调用 `spawn`/`rm` 等。

### editor Ability

```bash
editor play/stop/pause/undo/redo/info/log/livecoding
editor play
```

等价于直接调用 `play` 等。

---

## 插件 Ability（外部）

通过 `help` 命令查看所有已注册的插件 Ability。已知：

| 命令 | 来源 | 说明 |
|------|------|------|
| `vfx` | LLMVFX 插件 | Niagara VFX 生成/编辑 |
| `mat` | LLMMat 插件 | Material 生成/编辑 |
| `python` | LLMEasyShell 内置 | Python 脚本能力，命令来自 `Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/*.py` |

> `python vfx` 仅解析 .llmvfx DSL 文件。Niagara 系统生成/编辑用 C++ `vfx` 命令。
> `statetree` 命令存在但**未注册到 LLMEasyShell**，不可用。

---

## 详细用法

### spawn

```bash
spawn <Class> [at (x,y,z)] [as <Name>]
spawn PointLight at (0,0,200) as Light_01
spawn PointLight at (0, 0, 200) as Light_01    # 空格逗号也支持
spawn BP_Enemy at (100, 0, 50)
```

### set

```bash
set <Path> <Value>
set /Actor/Cube/Location (100,200,50)
set /Actor/Cube/Rotation (0,90,0)
set /Actor/Light/PointLight/Intensity 5000
set /Assets/BP_Enemy/MaxHealth 100
```

**Blueprint 父类重定义**：
```bash
set <Blueprint>.ParentClass <NewParentClass>
set /Game/Features/Survivor/BP_WaveManager.ParentClass WaveManager
set /Game/Features/Survivor/BP_EnemyBase.ParentClass EnemyBase
```
注意：Blueprint 重定义父类必须使用 `.ParentClass` 语法（点号分隔），不能用空格传递 ParentClass 作为属性名。

### call

```bash
call <Path> <Function> [--arg value]
call /Actor/Door Open
call /Actor/Light SetIntensity --NewIntensity 5000
call /Actor/Light/PointLight SetLightColor --NewColor "(1,0,0)"
```

### rm

```bash
rm <Path>
rm /Actor/Cube           # 删除 Actor
rm /Actor/Enemy*         # 批量删除
rm /Game/VFX/NS_Test    # 删除资产
rm /Assets/Blueprints/BP_Old
```

### ls

```bash
ls /Level/Actors                    # 场景 Actor
ls /Level/Actors --class BP_Enemy   # 按类过滤
ls /Assets                          # 资产目录
ls /Assets --type Blueprint         # 按类型过滤（全项目搜索）
```

选项：`--limit N` `--offset N` `--class NAME` `--name PATTERN` `--type TYPE`

### discover

```bash
discover <path>                    # 查看所有函数和属性
discover <path> --funcs           # 仅函数
discover <path> --props           # 仅属性
discover /Actor/Door/LiquidGlass --funcs
discover /Game/BP_TestComp#WidgetComponent --funcs  # Blueprint 内部组件
```

**调用函数前必查** — 确认函数名和参数格式！

### log

```bash
log                    # 编辑器日志
log --errors           # 仅错误
log --tail 100         # 最后 100 行
log --compile          # 编译日志
log --compile --status # 编译状态
log --compile --errors # 编译错误
```

### new

```bash
new <Type> <Name> [--parent Class] [--path /Assets/Dir]
new Blueprint MyActor
new Blueprint MyChar --parent ACharacter
new Material M_Glow --path /Assets/Materials
new DataTable DT_Items --struct FItemData
```

类型：`Blueprint/BP` `Material/Mat` `DataTable/DT` `NiagaraSystem/NS` `WidgetBlueprint/WB`
别名不区分大小写：`Widget` → `WidgetBlueprint`

### addcomp

```bash
addcomp <BlueprintPath> <ComponentClass> [as <name>] [--attach <parent>]
addcomp /Assets/BP_MyActor WidgetComponent as BackgroundWidget
addcomp /Assets/BP_Player StaticMeshComponent --attach RootComponent
```

路径支持 `/Game/` 和 `/Assets/` 前缀。组件类名支持各种格式（`WidgetComponent`、`StaticMesh`、`PointLight` 等，自动追加 `Component` 后缀搜索）。

**查看已添加的组件**：使用 `discover /Game/BP_MyActor` 可列出所有 SCS 组件，格式为 `BP_Path#ComponentName`。

### livecoding

```bash
livecoding            # 触发热重载（等待最多 120s）
livecoding --status  # 查看 LiveCoding 状态和报错信息
livecoding --enable  # 启用 LiveCoding
livecoding --disable # 禁用 LiveCoding
reload               # livecoding 的别名
lc                   # livecoding 的别名
```

**每次返回都带 `livecoding` 字段**，包含 `compiling` 和 `hint`。

### info

```bash
info              # 项目信息 + 编辑器状态
```

返回 JSON，**包含编辑器状态**，是唯一的状态查询入口：

```json
{
  "project": "CODEO",
  "engineVersion": "5.4...",
  "level": {
    "name": "Lvl_IntroRoom",
    "path": "/Game/...",
    "actorCount": 42
  },
  "pieState": "Stopped",
  "selectedActors": 1,
  "livecoding": {
    "compiling": true,
    "phase": "compiling",
    "elapsed": 15.2
  },
  "hint": "editor is compiling, 15s elapsed"
}
```

`livecoding.compiling = true` 表示编辑器正在编译，此时大部分命令会超时。`hint` 字段直接告知当前状态和下一步建议。

### find

```bash
find <type> <pattern>   # type: Actor 或 Asset，pattern 支持 * 通配符
find Asset *Glass*      # 搜索包含 Glass 的资产
```

**注意**：
- 格式是 `find <type> <pattern>`（两个参数，**不用 `--pattern` flag**）
- 示例：`find Asset NS_LiquidGlass`（不是 `find --pattern NS_LiquidGlass`）
- `find Asset *` = `ls /Assets`，`find Asset *Blueprint*` ≈ `ls /Assets --type Blueprint`

### play

```bash
play                # 开始 PIE（Play-in-Editor）
play --simulated    # Simulate-in-Editor（仅模拟，不控制玩家）
play -s             # 同上（短标志）
```

`--simulated` 模式下，编辑器运行物理/AI 但不接管玩家输入，适合观察 NPC 行为和场景交互。

### undo / redo

```bash
undo      undo 5
redo      redo 3
```

### gamestate

```bash
gamestate [wave|health|gold|exp|enemies|all]
```
查询游戏运行时状态（仅 PIE）。

| 参数 | 说明 |
|------|------|
| `wave` | 当前波次 |
| `health` | 玩家生命值 |
| `gold` | 金币数量 |
| `exp` | 经验值 |
| `enemies` | 存活敌人数量 |
| `all` | 显示所有状态 |

### msglog

```bash
msglog
```
查询编辑器 MessageLog。

---

## Blueprint 内部组件路径 (`#` 分隔符)

使用 `#` 分隔符访问 Blueprint 内部组件（定义在 SimpleConstructionScript 中）：

```bash
cat /Game/BP_TestComp#MeshComp           # 查看组件详情
discover /Game/BP_TestComp#WidgetComponent --props  # 查看组件属性
```

**路径格式**：`/Game/{BlueprintPath}#{ComponentName}[/{property}]`

| 示例 | 说明 |
|------|------|
| `/Game/BP_TestComp#MeshComp` | 查看 MeshComp 组件详情 |
| `/Game/BP_TestComp#MeshComp/StaticMesh` | 查看 StaticMesh 属性值 |
| `/Game/BP_TestComp#MeshComp/CastShadow` | 查看 CastShadow 属性值 |
| `discover /Game/BP_TestComp#WidgetComponent --funcs` | 查看组件可用函数 |

**注意**：
- `#` 前是 Blueprint 路径（不含 `/Game/` 前缀），`#` 后是组件变量名
- 组件名支持变量名、类名模糊匹配（如 `WidgetComponent` 可匹配 `BackgroundWidget` 变量）
- `cat` 输出的 `owner` 字段为 `null` 是正常的（Blueprint 组件模板无 owner 实例）
