# 命令参考

## 命令分类总览

| 分类 | 来源 | 说明 |
|------|------|------|
| **原生命令** | `CommandDispatcher` 直接注册 | 内核自带，37 个 |
| **内置 Ability** | `RegisterAbilityJson` 注册 | actor、editor 两个 Ability |
| **插件 Ability** | 外部插件注册 | LLMVFX (`vfx`)、LLMMaterial (`material`)、LLMDynamicUI (`ui`)、LLMPCG (`pcg`)、LLMMetaSound (`llmms`)、LLMStateTree (`llmstatetree`)、LLMQuixel (`quixel`) 等 |

---

## 原生命令（Core）

共 37 个，直接通过 `CommandDispatcher` 注册，不依赖 Ability 系统。
（详见 `LLMEasyShellSubsystem.cpp::RegisterBuiltInCommands` 的 37 个 `RegisterCommand` 调用 —— 行号会漂，**锚符号名**）

> [tool-fix-149 2026-06-29] rootCause: 锚定 L1457-1492 是 tool-fix-146 (commit d43280d) 修了 cpp 注释 28→36 但漏扫 commands.md 的 sub-fossil。Source-of-truth 4 重 lock: cpp `grep -n 'RegisterCommand' Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp` 第一个 hit = L1474 (`ShellCommand_Ls`), 最后一个 hit = L1509 (`ShellCommand_Mcp`), 中间 36 行 1:1 对齐 36 个 RegisterCommand 跟 filesystem `find Plugins/LLMEasyShell/Source/LLMEasyShell/Private -name 'ShellCommand_*.cpp' | wc -l` = 36 同源 double lock, 跟 SKILL.md L207 '36 个原生命令' 一致。
> [tool-fix-07 session25 2026-07-09] cross-cpp-cleanup: tool-fix-149 (本 blockquote 上方 'future session' follow-up) 把 cpp L1469/1470 错位锚点 (L1458-1493 fossil + [tool-fix-141] 误标) 闭合到 (L1474-1509 + [tool-fix-146]),跟 `awk '/RegisterCommand/ {print}'` 1:1 锁定。本行 (commands.md L16) 也从 'L1460-1495' → 'L1474-1509' 跟 cpp 同步。
>
> [r2294 Ship F 2026-10-23 · 2026-10-26 复核] **基准数漂移订正**: 上面两条 tool-fix blockquote 记的是 **2026-06-29 当时**的数（36）—— 它们作为**史实**不改写。基准值沿革（三段）：
>   · **36**（06-29）→ **38**（r2294 10-23 复核时读数, 含 `ui state`）→ **37**（2026-10-25 `ui state` 因依赖 USurvivorUIManager/UGameFlowSubsystem 项目专属内容外迁 LLMSurvivorShell 宿主插件; `RegisterBuiltInCommands` 里该槽位已成注释, cpp 自注「本插件内置命令数: 38 → 37 (装 LLMSurvivorShell 时 runtime 总数仍为 38)」）；
>   · 源：`LLMEasyShellSubsystem.cpp::RegisterBuiltInCommands` 存活 `RegisterCommand` 调用 = **37**；
>   · filesystem 同源：`find Plugins/LLMEasyShell/Source/LLMEasyShell/Private -name 'ShellCommand_*.cpp' | wc -l` = **37**；
>   · **运行时**读数：装 LLMSurvivorShell 时 38（37 + 外迁的 `ui state` 回注）, 不装 = 37 —— 文档锚**发行体**的 37；
>   · 文档声称：本文件 L7/L15/L16 + `llm-easy-shell/SKILL.md` = **37**（2026-10-23 曾短暂写成 38, 10-25 外迁后归正）。
>   ⇒ 同源 lock 成立。⚠ 锚**符号名**不锚行号（行号会随无关编辑上漂）。

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
| `mcp` | **UE 5.8 官方 ModelContextProtocol 桥接** | `mcp status` / `mcp tools` / `mcp start` / `mcp stop` / `mcp call <name> [json]` / `mcp config [client]` |

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
| `material` | LLMMaterial 插件 | Material 生成/编辑 |
| `ui` | LLMDynamicUI 插件 | UMG Widget 生成/编辑（**仅当无 `ui <subcmd>` 命中**；见下方 UI 交互段） |
| `pcg` | LLMPCG 插件 | PCG 图生成/编辑 |
| `llmms` | LLMMetaSound 插件 | MetaSound 音频生成/编辑 |
| `llmstatetree` | LLMStateTree 插件 | StateTree 状态机生成/编辑。9 个子命令: `generate` / `preview` / `nodes` / `schema` / `inspect` / `export` / `copy` / `delete` / `compile`（`preview` 只解析不写资产，`nodes` 列出当前工程的节点类型，`schema` 导出 schema 快照） |
| `quixel` | LLMQuixel 插件 | Quixel Megascans 资产桥接 |
| `python` | LLMEasyShell 内置 | Python 脚本能力，命令来自**所有插件**的 `<Plugin>/Content/Python/<Pkg>/abilities/*.py`（含平台宿主 46 个内置）+ `Content/Features/<Feature>/Scripts/*.py` 项目脚本 |

> `python vfx` 仅解析 .llmvfx DSL 文件。Niagara 系统生成/编辑用 C++ `vfx` 命令。
> StateTree 用 `llmstatetree`（**带 `llm` 前缀**）；裸 `statetree` 会被 LLMEasyShellSubsystem 的 `CommandToAbilityMap` 判为 unknown ability，返回 `"Unknown command: statetree"`（`LLMEasyShellSubsystem.cpp` 的 `EShellErrorCode::NotFound` 分支 —— 2026-10-26 锚符号名, 原 `:977` 行号化石已漂至 ~:1056）。详见 `llm-statetree/SKILL.md` 的 tool-fix-156 修订注。

---

### UI 交互（本机 LLMEasyShell 原生）

7 个 `ui <subcmd>` 命名空间命令，**优先级高于** LLMDynamicUI 插件的 `ui` ability（`LLMEasyShellSubsystem.cpp` 的复合名 dispatcher —— 先把 `Command` 按空格拼复合名查一遍, 再走 single-token `ui` ability 匹配; 锚符号名, 原 `:623-630` 化石已漂）。仅当 `ui` 后不带这 7 个子命令之一时，才 fallback 到 LLMDynamicUI 的 `ui` ability。

| 子命令 | 功能 | 示例 |
|--------|------|------|
| `ui dump` | 导出 PIE 主 UUserWidget 的 UMG 树为 JSON | `ui dump --depth 3 --include-hidden` |
| `ui find` | 按 text/class/path 查找匹配条件的 widget | `ui find --text "Build"` / `ui find --class UWebShopWidget` |
| `ui info` | 按 path 获取单个 widget 详情（WebBrowser widget 额外带 `cef_state`） | `ui info --path HUD.BuildMenu.Card[0]` |
| `ui shot` | HighResShot 截图 PIE viewport（默认 `<ProjectSaved>/Screenshots/ui_shot_<ts>.png`） | `ui shot --out C:/temp/hud.png` |
| `ui press` | 注入鼠标点击或按键（`mouse`/`key` 子命令） | `ui press mouse --path HUD.Card[0] --button L` / `ui press key --path HUD.ChatInput --key Escape` |
| `ui type` | 聚焦 widget 后通过 FSlateApplication 注入文本字符 | `ui type --path HUD.ChatInput --text "hello"` |
| `ui tick` | 轮询直到出现匹配的 widget 或超时 | `ui tick --text "Wave 5" --timeout 30` |

> 这 7 个命令的 C++ 类在 `LLMEasyShellTypes.h` 声明（`UShellCommand_UITree`/`UIFind`/`UIInfo`/`UIShot`/`UIPress`/`UIType`/`UITick`，首 declarations 自 ~L1954 起 —— 2026-10-26 复核; 原 `:1900-2055` 区间截尾三个类），所有 `GetCommandName()` 返回 `"ui <subcmd>"` 带空格，复合 dispatcher 优先匹配。源码 `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_UI*.cpp`。

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
livecoding            # 触发热重载（等待最多 180s — r2175 由 60s 改；180s 只由一次增量实测推导，全量 UNVERIFIED）
livecoding --status  # 查看 LiveCoding 状态和报错信息
livecoding --enable  # 启用 LiveCoding
livecoding --disable # 禁用 LiveCoding
reload               # livecoding 的别名
lc                   # livecoding 的别名

<!-- [r2175 2026-10-05] 本行 source-of-truth 已翻面：`constexpr double MaxWaitSeconds` = **180.0**（不再是 60.0），客户端 `RECV_TIMEOUT_MS` = **210000ms**（不再是 70000ms）= 180s server cap + 30s buffer。
     理由：原 60s 预算 < 本机实测一次**成功的增量**构建 67.11s ⇒ 每次正常成功构建都落进 Timeout 分支报假红。
     ⚠ **180s 只由那一次增量实测推导，全量构建未被测过 —— UNVERIFIED。** 若全量超过 180s，本病会在更晚 3 分钟处复发。
     ⚠ 另有已知副作用未处理：main.cpp:538-539 把该常量同时用于 `SO_RCVTIMEO` 与 `SO_SNDTIMEO` ⇒ 发送超时也一并从 70s 抬到 210s；且空回包兜底（main.cpp:1613-1617，靠 2000ms 探 `info` 判编辑器已崩）现在约 212s 才触发 ⇒ **崩溃发现被推迟约 2.3 分钟**。下一席若要收这两条，从「按命令分级超时」入手，别再抬全局默认。
     下方 tool-fix-144 / tool-fix-07 两段 meta-NOTE 保留为历史（它们记的是 60s 那一版的由来），但其 `source-of-truth` 断言**已过期**，以本段为准。 -->
<!-- [tool-fix-144 2026-06-29] livecoding max wait 120s → 60s (跟 SKILL.md:155 + ShellCommand_Reload.cpp:404 comment 同步)。source-of-truth: ShellCommand_Reload.cpp:405 `constexpr double MaxWaitSeconds = 60.0;`，客户端 RECV_TIMEOUT_MS = 70000ms = 60s server-side + 10s buffer。Pattern 跟 tool-fix-130~143 doc-fossil fix 1:1 平行。 -->
<!-- [tool-fix-07 session31 2026-07-09] commands.md L252 stale line-anchor drift `ShellCommand_Reload.cpp:401/:402` → `:404/:405` 闭合 session25 partial-fix residue — session25 (b32a073) 修了 LLMEasyShellSubsystem.cpp L1469-1472 meta-NOTE 双 fossil 但漏了 commands.md L252 anchor (off-by-1 + off-by-3 跟 ShellCommand_Reload.cpp 实际行号漂移)。Source-of-truth: cpp L402-L404 是 `[tool-fix-144]` 起始 3 行 comment (跟 commands.md 之前 anchor 的 `:401` 漂移 1 行) + L405 `constexpr double MaxWaitSeconds = 60.0;` (跟之前 anchor 的 `:402` 漂移 3 行)。Invariant: 任何 `Source/<Plugin>/Source/<Plugin>/Private/ShellCommand_*.cpp:L###` 行号锚点必 paired verify `grep -n 'constexpr.*MaxWaitSeconds' Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Reload.cpp` 跟 meta-NOTE/HTML comment anchor 1:1 lock。 -->
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
  "engineVersion": "5.8...",
  "level": {
    "name": "Lvl_IntroRoom",
    "path": "/Game/...",
    "actorCount": 42
  },
  "pieState": "Stopped",
  "pieWorldTimeSeconds": -1.0,
  "pieRealTimeSeconds": -1.0,
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

---

## <a id="mcp"></a>`mcp` — UE 5.8 ModelContextProtocol 桥接

将 UE 5.8 自带的官方 ModelContextProtocol 引擎插件包成 llmshell 原生命令。**实现路径**：直接调 `IModelContextProtocolModule` 同步 C++ API（不用 HTTP，避免 game thread 同步 wait 死锁）。

### 子命令

| 子命令 | 功能 | 示例 |
|--------|------|------|
| `mcp status` | 看 server 状态（port/path/running/tools count） | `mcp status` |
| `mcp start [--port N]` | 启 HTTP server，端口可选 | `mcp start` / `mcp start --port 8001` |
| `mcp stop` | 停 server | `mcp stop` |
| `mcp tools` | 列已注册 MCP tools | `mcp tools` |
| `mcp call <name> [json]` | 同步调 tool，返回 JSON-RPC content array | `mcp call list_toolsets {}` |
| `mcp config [client] [--out P]` | 写 `.mcp.json` 给 Claude/Cursor/VSCode/Gemini | `mcp config claude` |

### 输出形态

**`mcp status` 典型输出**：

```
MCP Server Status
  Running:      yes
  Port:         8000
  URL Path:     /mcp
  Full URL:     http://localhost:8000/mcp
  Auto-Start:   no
  Tool Search:  enabled
  Tools Loaded: 3
```

**`mcp tools` 典型输出**：

```
MCP Tools (3):
  - list_toolsets
      Desc:   List all available toolsets with names and descriptions.
      Schema: {"type":"object","properties":{}}
  - describe_toolset
      Desc:   Get detailed information about a toolset including all tool names, descriptions, and input schemas.
      Schema: {"type":"object","properties":{"toolset_name":{"type":"string",...}},"required":["toolset_name"]}
  - call_tool
      Desc:   Call a tool by name. ...
```

UE 5.8 默认 3 个 top-level tool（统一入口），通过 `describe_toolset` 发现 toolset 子 tool，再 `call_tool` 间接调。

**`mcp call list_toolsets {}` 典型输出**：

```json
{"content":[{"type":"text","text":"- ToolsetRegistry.AgentSkillToolset: 提供用于列出、读取和创建/更新技能的工具。\n"}]}
```

**`mcp config claude` 写入文件**（默认 `D:/<ProjectDir>/.mcp.json`）：

```json
{
  "mcpServers": {
    "unreal": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Claude Code / Cursor / VSCode / Gemini 都认这个 HTTP transport 格式。

### 客户端 → UE 端到端流程

```
1. UE editor 启动时:
   - 启用 ModelContextProtocol plugin (.uproject)
   - 启 MCP server（三种任选）:
     a) `mcp start` (运行时启)
     b) Project Settings > Plugins > Model Context Protocol > bAutoStartServer = true
     c) CLI: UnrealEditor.exe CODEO.uproject -ModelContextProtocolStartServer

2. Claude Code 启动:
   - 自动读 .mcp.json 连上 http://localhost:8000/mcp
   - 通过 tools/list 发现 3 个 top-level tool
   - 用 describe_toolset / call_tool 间接调子 tool
```

### 关键踩坑

**1. host 必须 enable ModelContextProtocol 插件**

`.uproject` 必须有：

```json
{ "Name": "ModelContextProtocol", "Enabled": true }
```

否则 LLMEasyShell link 失败（unresolved `IModelContextProtocolModule` symbols）。LLMEasyShell.Build.cs 把 `ModelContextProtocol` + `ModelContextProtocolEngine` 都列为 `bBuildEditor` 块的 PrivateDependency，并通过 `WITH_LLMEASYSHELL_MCP=1` 宏包住所有相关 include — host 不 enable 时整个 cpp 退化成 NotImplemented 错误。

**2. `ModelContextProtocolSettings.h` 在 `ModelContextProtocolEngine` 模块，不在 `ModelContextProtocol`**

UE 5.8 MCP 插件有 6 个 module（基础 / Engine / Editor / *Tests），Settings/ClientConfig 都在 `*Engine` 子模块。第一次只加 `ModelContextProtocol` dep 会 UBT fatal error，加 `ModelContextProtocolEngine` 才过。

**3. Build.cs 加新 PrivateDependency 必须 `restart` 不能只信 `livecoding`**

`livecoding` 报 `compileSuccess:true` 但 `--restart` 走 UBT 全量构建会挂 fatal error（这次踩坑）。详见 [experience/04-build-and-restart.md](../experience/04-build-and-restart.md)。

**4. `/tmp/foo` 这种 Git Bash 假路径写盘失败**

`mcp config claude --out /tmp/foo` 在 Windows 上 `FFileHelper::SaveStringToFile` 当成绝对路径处理，Windows 没 `/tmp/` 目录 → 写盘失败。要么传 Windows 路径（`C:/...`）要么不传 `--out`（默认 project 根）。

**5. UE 5.8 之前（5.7.4 / 5.6）没有这个插件**

升级到 5.8 后才能用，5.7.4 项目需要先升引擎。

### 实测参考

UE 5.8.1-CL-55116800 + LLMEasyShell 全部 6 子命令端到端跑通。详见 [`../experience/incidents/llm-shell-mcp-native-ability-2026-06-21.md`](../experience/incidents/llm-shell-mcp-native-ability-2026-06-21.md)。
