---
name: llm-easy-shell
description: |
  操作运行中的 Unreal Engine 编辑器。当用户需要在 UE 编辑器中执行实时操作时使用此 skill。

  **触发场景**：
  - 场景操作：查看/创建/删除/选择 Actor，搜索对象
  - 属性修改：移动/旋转/缩放，修改任意属性值
  - 函数调用：调用 Actor 或组件上的蓝图函数（**先用 discover 确认函数名**）
  - 资产操作：浏览/创建/复制/删除蓝图、材质、数据表，**添加组件到蓝图**
  - 编辑器控制：PIE 播放/停止/暂停、热重载、保存、撤销重做
  - 日志查看：编辑器日志、编译日志

  **触发关键词**：ls, cat, set, spawn, rm, cp, mv, call, save, new, addcomp, play, stop, pause, select, focus, undo, redo, find, info, help, livecoding, reload, lc, log, mkdir, discover, actor, editor, /Actor/, /Assets/, /Game/, /Level/, restart, msglog, gamestate, simulated, **mcp**

  **不触发**：纯 C++ 代码编写(cpp-developer)、AngelScript 脚本(unreal-as)、完整项目编译(builder)
---

## 使用规范：每个工具调用前必须说清为什么选用在这个工具

**核心原则**:调用任何 llm-shell 命令之前,**先**输出一段说明,然后**再**发命令。

**完整示例**:

> 用 `ls /Level/Actors` 列场景所有 Actor。任务开始,需要先知道场景里有什么(灯光 / 敌人 / 玩家)才能决定下一步操作。看到 1 个 BP_PlayerCharacter + 3 个 BP_Goblin + 2 盏 PointLight。
> ```bash
> ./llm-shell.exe -q -j -c "ls /Level/Actors"
> ```

**例外**(允许省略):
- 用户明确说"快速看一下"、"先列一下"、"探索"等探索性请求时,可以做"轻量提示"而不是完整三段式,但仍要至少说明 **What**
- `help`(纯查命令清单)、`info`(环境状态查询)如果只是在响应前一条命令的延伸查询,可以简短

**这条规范的目的**:
- 用户能在 LLM "动手前"介入或纠正,避免无效操作累积
- 多步骤工作流产生可追溯的决策日志(事后回看能知道"为什么当时选这条路")
- 与本仓库 CLAUDE.md "优先挖掘问题根源,不急于实现" 的精神一致 — 写命令前先想清楚

**反例(禁止)**:
- ❌ 直接发 `set /Actor/X/Rotation (0,0,0)`,不解释 — 改之前先说为什么改
- ❌ 发完命令再补理由 — 必须"先解释,后执行"
- ❌ 用 5 个字打发 "改了 X" — 至少给 1 句 What + 1 句 Why

---

## 核心命令

```bash
ls /Level/Actors                    # 看场景
cat /Actor/{name}                   # 看详情
discover /Actor/{name}/LiquidGlass  # 查看可用函数和属性
set /Actor/{name}/Location (x,y,z)  # 改属性
call /Actor/{name}/LiquidGlass ApplyPreset --Preset Default  # 调用函数
spawn PointLight at (0,0,100)       # 创建
rm /Actor/{name}                    # 删除
```

**discover 是最重要的命令** — 调用函数前先用它确认函数名和参数！

## CLI 旗标（LLM 上下文优化）

| 旗标 | 等价 | 效果 |
|------|------|------|
| `-q` | `--quiet` | 把 stderr 噪音(连接/路径/端口警告)重定向到 `llm-shell-quiet.log`,LLM stdout 只剩有效输出 |
| `-j` | `--json-only` | 解包 server 响应里的 `output`/`result` 字段,做 JSON 反转义后原样输出 — LLM 直接 parse 不必二次解字符串 |

**推荐组合**:几乎所有调用都加 `-q -j`,把 17 行 noise 压成 7 行纯 JSON。

```bash
# 之前(17 行,嵌套 JSON)
./llm-shell.exe -c "gamestate"
# 输出:
# [llm-shell] Engine path found via fallback: C:\Program Files\Epic Games\UE_5.8
# { "success": true, "output": "{\"wave\":{...}}" }
# 
# 之后(7 行,纯 JSON,LLM 可直接 parse)
./llm-shell.exe -q -j -c "gamestate"
# {"wave":{"currentWave":"1",...},"player":{...},"enemyCount":2}
```

> 注意:`-j` 只在响应有 `output`/`result` 字段时生效;`info` 命令直接返回顶层 JSON,无需 `-j`。REPL 模式不受 `-q` 影响(保留人类可读 stderr)。

## 路径规则

| 路径 | 含义 |
|------|------|
| `/Actor/{label}` | 场景对象 |
| `/Actor/{label}/{component}` | 组件（支持别名匹配） |
| `/Game/{path}` | 资产（cat 支持） |
| `/Assets/{path}` | 资产（别名，cat 支持） |
| `/Class/{name}` | 类信息（cat 支持） |

**find 命令**：
```bash
find /Game *Glass*     # 在 /Game 下搜索资产（支持 * 通配符）
find /Assets *          # 在 /Assets 下搜索
find Actor BP_Liquid*   # 搜索场景中的 Actor
find Asset *Liquid*     # 搜索资产
```

## livecoding vs restart

| 场景 | 命令 | 说明 |
|------|------|------|
| 修改现有类函数体 | `livecoding` | 函数体、算法、局部变量 |
| 修改现有类 UPROPERTY/UFUNCTION | `livecoding` | 多数情况下可以 |
| **新增 C++ 类** | `restart` | LiveCoding 无法处理，必须重启编辑器 |
| UENUM/USTRUCT 变更 | `restart` | 反射系统元数据变更 |
| 继承层次变化 | `restart` | 需要重新实例化对象 |
| **Build.cs 加新 PrivateDependencyModuleName** | `restart` | `livecoding` 假绿灯 — patch 成功但 UBT 全量 build 会 fatal error |
| 不确定 | `restart` | 安全选择 |

> 完整决策树 + LiveCoding 失败诊断 + `python reload` 行为见 [experience/04-build-and-restart.md](experience/04-build-and-restart.md)

`livecoding`：Live Coding 二进制补丁，替换函数指令，不重新实例化对象。  
`restart`：`save → shutdown → MSBuild → 启动引擎`

## Editor 不在线？用 `--restart` 启动，不要等用户手动

任何命令（含 `info`）返回连接失败 → **直接 `--restart`**：

```bash
./llm-shell.exe --restart   # 前台阻塞等启动完成，5-10min；带 heartbeat 看进度
```

**`info` 离线响应约定**（2026-06-26）：返回的 JSON 顶部字段 `recommendedAction: "run_llm_shell_restart"` + `restartCommand: "llm-shell --restart"`。LLM 看到这两个字段就**直接跑 restart**，不要问用户、不要反复探测、不要等其他命令。

**不要**：
- ❌ "editor offline, 等用户手动启动" — 浪费一轮对话
- ❌ 反复 `info` 探测 — 一定 fail
- ❌ 假设 `livecoding` 能补救 offline editor — 不行，必须 editor 在跑
- ❌ 看到 `recommendedAction` 后问 "要不要 restart?" — 直接跑

**`--restart` 内部流程**：
1. 检测 editor 是否已跑（port scan / cached port）
2. 若已跑 → save dirty packages → graceful shutdown
3. 若未跑 → 跳过 save/shutdown，直接走 build
4. UBT 全量 build `CODEOEditor Win64 Development`（~60-120s）
5. 启动 `UnrealEditor-CODEO.exe`（push-model fast-path 约 10s ready，fallback TCP poll 60s）
6. emit 单 JSON 契约：`{"success":true,"stage":"complete"}` 或带 `crashLog` / `priorCrashLog`

**`--restart --port N`**（多编辑器精准关闭）：
- 用 netstat 找到端口 N 对应的 PID（必须 UnrealEditor），发 WM_CLOSE
- **跳过** project-match 校验、`RequestEditorClose` 项目级扫描、`KillAllProjectRelatedProcesses` 项目级 sweep
- 保留 save 步骤（仍连该端口发 save）
- 60s 超时后用 `taskkill /T /F /PID` 强杀单 PID 树
- 新编辑器仍启动在端口 N（不重新分配）
- 适用场景：同时跑多个项目编辑器，只想关其中一个

**何时用 `--restart` 而不是 `livecoding`**：
- editor 本来就没跑（offline session start）
- 加新 UCLASS / USTRUCT / UENUM
- Build.cs 加新 PrivateDependencyModuleName（livecoding 假绿灯 — 见 experience/04）
- 用户明确要求 restart

**超时**：`--restart` 全局 10min hard cap（即使中间 hang 也会 exit），buildWatcher 8min，stdout 每 10s heartbeat。详细 debug 见 [experience/04-build-and-restart.md](experience/04-build-and-restart.md)。

## livecoding 使用准则

**每次工具调用返回中都包含 `livecoding` 字段**，显示当前编译状态。

| 命令 | 用途 |
|------|------|
| `livecoding` | 触发编译 + 等待完成（最长 60s） |
| `livecoding --status` | 查看 LiveCoding 状态和报错信息 |
| `livecoding --enable` | 启用 LiveCoding |
| `livecoding --disable` | 禁用 LiveCoding |

<!-- Forensic: see SKILL_CHANGELOG.md §1 -->
<!-- Forensic: see SKILL_CHANGELOG.md §2 -->

**正确流程**：
1. `livecoding` → 触发编译，等待完成
2. 查看响应中 `livecoding` 和 `result` 字段
3. `compiling: false, result: Success` → 编译完成
4. `compiling: true` → 编译进行中
5. `result: Timeout` → 命令超时，查看返回的 `editorState` 了解编辑器状态
6. `result: Timeout, compiling: false` → 超时但编译实际成功（通过日志确认）
7. `result: Timeout, compiling: true` → 超时且仍在编译，用 `livecoding --status` 确认

## info 命令

`info` 是唯一的状态查询入口，返回项目信息 + 编辑器实时状态：

```json
{
  "project": "CODEO",
  "engineVersion": "++UE5+Release-5.8-CL-...",
  "port": 15152,
  "level": { "name": "Lvl_SurvivorTest", "path": "/Game/...", "actorCount": 30 },
  "pieState": "Stopped",
  "selectedActors": 0,
  "editorState": "Idle",
  "stateDetail": "LiveCoding engine flag is stale (no log activity for 35s) — treating as idle",
  "livecoding": {
    "compiling": false,
    "phase": "idle",                      // idle | compiling | succeeded | failed
    "elapsed": 0.0,                       // seconds since compile start
    "hasCompleted": false,
    "success": false,
    "requiresRestart": false,             // true when header files were modified
    "reason": "Modified 2 header file(s)", // present when hasCompleted=true
    "recommendation": "Restart editor to apply header changes"
  },
  "hint": "editor is idle",               // actionable instruction for LLM
  "capturedLogs": [ ... ]                 // recent log tail (optional)
}
```

**字段语义关键**:
- `editorState` — 顶层状态机: `Idle` | `PIE` | `Compiling` | `PreparingPatch` | `Saving` | `Loading` | `Building`。在执行任何修改操作前先确认它不是 `Compiling`/`PreparingPatch`。
- `livecoding.compiling` — LiveCoding 自身的二进制状态,会滞后于 `editorState`。
- `livecoding.requiresRestart=true` — 头文件被改了,**只能 restart editor,继续用 `livecoding` 会编译失败**。
- `livecoding.reason` + `recommendation` — 跟 `requiresRestart` / `hasCompleted=true` 同时出现,告诉 LLM 下一步该做什么。
- `hint` — 综合 `editorState` + `livecoding` 的人类可读指令(LLM 直接转给用户即可)。

## Ability 架构

**内置（Core）**：36 个原生命令 = 28 核心 + 7 UI 调试子命令（见下方 §UI 调试）+ 1 已弃用 `livelog`（用 `log --compile` 代替）
- Actor（8）：`spawn` `rm` `cp` `mv` `select` `focus` `call` `set`
- 资产（4）：`new` `save` `mkdir` `addcomp`
- 编辑器（9）：`play` `stop` `pause` `undo` `redo` `info` `log` `msglog` `gamestate`
- 查询（5）：`ls` `cat` `find` `help` `discover`
- **AI 集成（1）：`mcp`（UE 5.8 官方 ModelContextProtocol 桥接 — `mcp status|start|stop|tools|call|config`，详见 [references/commands.md](references/commands.md#mcp)）**
- 热重载（1）：`livecoding`（别名 `reload` / `lc` 三者等价）

**内置 Ability**：`actor` `editor`（加前缀调用，与直接调用原生命令完全等价，无额外功能）

**插件（Extension）**：`help` 列出所有已注册 Skills，已知：`vfx` (LLMVFX) `material` (LLMMaterial) `ui` (LLMDynamicUI) `pcg` (LLMPCG) `llmms` (LLMMetaSound) `llmstatetree` (LLMStateTree) `quixel` (LLMQuixel) `llmwhitebox` (LLMWhitebox) `uireactionbus` (UIWebBridge) `python` (LLMEasyShell 内置)

<!-- Forensic: see SKILL_CHANGELOG.md §3 -->

**UI 调试**（Slate/UMG 可观测性 + 模拟输入，7 命令族）：`ui dump|find|info|shot|press|type|tick`
- `dump` UMG widget tree JSON · `find` 按 text/class/path 搜节点 · `info` 单节点 detail (含 UWebBrowser→cef_state)
- `shot` 整 VP 或单 widget 截图 · `press mouse|key` + `type` 逐字符 + `tick` polling
- 真闭环: z-order bug / WebBrowser CEF 黑屏 / GameOver 风暴 3 个真 bug 的可观测性 + 模拟操作通道
- 详见 [experience/2026-06-12-slate-ui-inspector-summary.md](experience/2026-06-12-slate-ui-inspector-summary.md) (7 命令表 + 关键架构决策 + DoD 6/7)
- 教学 lesson: [experience/llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md](experience/llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md) — `success: true` 不证明 "点中了",只证明 "没 crash + 路径解析完成"

> `actor spawn` = `spawn`，`editor play` = `play` — 前缀机制仅为兼容性保留，建议直接使用原生命令。

## Python Ability（可扩展的命令）

`python` 是一个特殊的 Ability，它的命令来自文件系统而非 C++ 注册。Agent 有完全的自主权来创建新的 Python 能力。

### 工作原理

```
Plugins/<PluginName>/Content/Python/LLMShellAbilities/
├── __init__.py
├── registry.py       # Ability 基类（不可删除）
└── abilities/
    ├── __init__.py
    ├── _base.py          # 下划线开头 = 私有
    ├── _example.py       # 下划线开头 = 私有
    └── material.py       → python material 命令

Content/Features/Survivor/Scripts/   # 项目脚本权威路径 (2026-06-27 起,优先于 Plugin 副本)
├── <your_script>.py         → python <your_script> 命令
└── ...                      # 项目拥有的 .py ability
```

> **注**：实际扫描路径由 `PythonAbilityRegistry::GetPythonAbilitiesRoot()` (Plugin) + hardcoded `Content/...` 路径 (项目) 决定。要改路径需修改 C++ 源码 + rebuild plugin。

每个非 `_` 开头的 `.py` 文件自动成为一个命令，通过 `python <文件名>` 调用。

### 调用方式

```bash
python material              # 调用 material.py
python <command> [args...]   # args 会以列表传给 Python 函数
```

### Agent 的自由度

**1. 创建新的 Python 能力（完全自主）**

不需要修改任何 C++ 代码。只需：
1. 在以下任一路径创建 `.py` 文件:
   - `Plugins/<PluginName>/Content/Python/LLMShellAbilities/abilities/` (平台内置能力)
   - `Content/Features/Survivor/Scripts/` (项目脚本权威路径,优先于 Plugin 副本,避免双轨化石)
2. 实现 `main(args, context)` 或 `execute(args, context)` 函数
3. Python ability 自动被发现并注册 (双路径扫描去重, Content 优先)

**2. Context API（在 Python 中使用）**

Python 文件内可通过 `context` 对象访问 LLMEasyShell 的反射能力：

```python
from registry import Ability, Command, Context

class MyAbility(Ability):
    name = "my"
    version = "1.0.0"

    def get_commands(self):
        return [
            Command("my_action", "Do something", ["param1", "param2"]),
        ]

    def execute(self, command, args, context):
        if command == "my_action":
            # 读取资产属性
            value = context.get_property("/Game/BP_Test", "Health")
            # 修改资产属性
            context.set_property("/Game/BP_Test", "Health", "100")
            # 调用资产函数
            result = context.call("/Game/BP_Test", "TakeDamage", {"Damage": 10})
            return {"success": True, "output": f"Health is now {value}"}

def register(reg):
    reg.register_ability(MyAbility())
```

**3. 不需要知道实现细节**

Agent 调用 `python material` 时，不需要知道 `material.py` 的内部结构。Python 框架负责：
- 参数传递
- 错误处理
- 结果序列化

**4. 现有的 Python abilities**

| 命令 | 功能 |
|------|------|
| `python material` | Material 资产生成与参数操作 |
| `python blueprint` | Blueprint 结构分析（变量/函数/组件/继承） |
| `python asset` | 资产管理与依赖审计 |
| `python vfx` | 解析 .llmvfx DSL 文件（Niagara 系统生成用 C++ `vfx` 命令） |
| `python scene` | 场景 Actor 查询（统计/灯光/邻近搜索/标签） |
| `python level` | Level 操作与 actor 空间查询 |
| `python umg` | UMG/Widget Blueprint 结构与属性 |
| `python datatable` | DataTable 行读写、列搜索、CSV/JSON 导出 |
| `python editor` | 编辑器会话控制（视口/PIE/CVar/**截图**） |
| `python gameplay` | PIE 游戏控制与调试绘制 |
| `python navigation` | NavMesh OBJ 导出 |
| `python poseseach` | PoseSearch Schema/Database 查询 |
| `python chooser` | Unreal Chooser 表调试 |
| `python property` | UPROPERTY 读写（绕过 Python 访问限制） |
| `python bpcomp` | Blueprint CDO 组件属性读写（支持蓝图合成组件和 C++ 继承组件） |
| `python bpprop` | Blueprint CDO 属性读写 |
| `python perf` | 性能指标查询（帧时序/内存/UObject 统计） |
| `python anim` | Animation 资产检查与编辑 |
| `python hd3dscene` | HD3D 场景设置（材质/标签/体素 Actor 配置） |

> **注**：此表为精选示例，非完整注册表。完整 Python ability 列表见 `Plugins/<PluginName>/Content/Python/LLMShellAbilities/abilities/`（每个非 `_` 开头的 `.py` 自动注册为 `python <文件名>` 命令）+ `Content/Features/Survivor/Scripts/`（项目脚本权威, 优先扫描），或在编辑器会话中运行 `help` 查看所有已注册 Ability。

路径：
- 平台内置：`Plugins/<PluginName>/Content/Python/LLMShellAbilities/abilities/`
- 项目权威：`Content/Features/Survivor/Scripts/`

**5. 描述规范（Docstring Guidelines）**

创建 Python ability 时，**docstring 第一行必须具有语义**——描述"做什么"而非"怎么实现"。

| 写法 | 评价 |
|------|------|
| `"""Access Material parameters."""` | 差 - 不说明能做什么 |
| `"""Read and write Material parameters (scalar, vector, texture) via Python binding layer."""` | 好 - 明确说明能力范围 |
| `"""Query scene actors: stats, lights, proximity search, tags, and class distribution."""` | 好 - 列出具体功能 |
| `"""Analyze Blueprint class structure: variables, functions, components, and inheritance."""` | 好 - 动词开头，清晰具体 |

**规范**：
- 第一行用动词开头（Read, Query, Analyze, Audit, Generate...）
- 包含具体的功能关键词（stats, lights, proximity, tags）
- 避免技术实现细节（Python binding layer、C++ reflection）
- `help` 命令会提取 docstring 第一行显示给用户

**错误示例**：
```python
"""Material ability implementation."""
"""Functions for getting and setting material params."""
```

**正确示例**：
```python
"""Read and write Material parameters (scalar, vector, texture) via Python binding layer."""
```

**6. 注册/注销 Python abilities**

Python abilities 在编辑器启动时自动扫描注册。修改平台内置 abilities 目录或项目脚本路径后需要重启编辑器（或调用 `reload`）使更改生效。双路径扫描: Plugin abilities + Content 项目脚本路径 (Content 优先, 同 CommandName 去重)。

## 调用方式

```bash
.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -c "ls /Level/Actors"
.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe --restart
```

## 错误排查

| 问题 | 解决 |
|------|------|
| Actor not found | `ls /Level/Actors` |
| Asset not found | `ls /Assets` 或 `find /Game *` |
| Function not found | `discover <path> --funcs` 查看可用函数 |
| 连接失败 | 启动 UE 编辑器 |
| 命令超时 | 超时后自动查询 `info`，响应中含 `editorState` 查看编辑器状态 |
| find 返回 "Unknown type: /X" | 命令已支持 `find /Game <pattern>` 路径格式 |
| cat 不显示属性值 | 已修复：显示所有 BlueprintVisible 属性当前值（含 struct） |

**更深入的踩坑经验（按主题）**：

- [experience/01-builtin-commands.md](experience/01-builtin-commands.md) — Actor 路径 `/` 解析、`new --key=value` 崩溃、stdin 与 `-c` 冲突、set Blueprint 父类限制、FObjectProperty 崩溃
- [experience/02-python-abilities.md](experience/02-python-abilities.md) — Python `ExecuteFile` 模式、output 字段缺失、`_call_with_world` 死写 bug、b 前缀 bool 字段读不到
- [experience/03-blueprint-property.md](experience/03-blueprint-property.md) — bpprop 5 个 ClassProperty 坑、FClassProperty MetaClass 校验、`#` 路径 FObjectProperty fallback、嵌套路径 walk
- [experience/04-build-and-restart.md](experience/04-build-and-restart.md) — 何时 `livecoding` / 何时 `restart` 决策树、USTRUCT 改字段必 restart、`python reload` 不重 import 模块、**Build.cs 加新 PrivateDependencyModuleName 必须 restart（livecoding 报 success 但 UBT 全量 build 仍会挂）**
- [experience/05-screenshot.md](experience/05-screenshot.md) — 截图双路径（sync vs async+ui）、CEF 初始化延迟、2026-06-01 新输出格式

> 详细语法见 `references/commands.md`
> 源码调试经验见 [experience/debugging.md](experience/debugging.md)
> PIE 截图完整指南见 `references/llm-screenshot.md`
> **Editor 窗口截图**（Win32 路径，绕开 FViewport 0×0 硬约束）见 [references/editor-shot-win32.md](references/editor-shot-win32.md)
> 完整经验库（39 个教训）见 [experience/README.md](experience/README.md)
>
> (tool-fix-137 2026-06-29: SKILL.md L401 fossil '31 个教训' 跟实际 experience/ 9 canonical 文件 grep 1:1 验证的 39 个教训/规则 (6+4+5+6+5+1+4+7+1) 差 8; 9248b59 2026-06-27 当时 31 正确, 但 06-cli-flags.md (+1) + 07-editor-shot-win32.md (+4) + debugging.md 5 个新教训 (5→7 +2 实际是新增, 不是漂移, 累计 +7) + t3-bpcomp-tobjectptr-reflection-fix.md (+1) 累计 +8 加成后 31→39 SKILL.md L401 未同步, experience/README.md L3 也 fossil 38, 本 fix 闭合 2 surfaces 1 rootCause family)

## 截图 — 两条路径选对

| 场景 | 用哪条 | 命令 |
|------|--------|------|
| 看 **editor 应用窗口**（菜单/工具栏/**Outliner**/视口/状态栏） | **Win32 路径**（推荐） | `powershell -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1` |
| 看 **PIE 3D 渲染**（HUD/动画/动态光照） | PIE 路径 | `play` → `sleep 5` → `python editor screenshot path=X source=pie` |
| 不知道选哪个 | Win32 路径（永远能跑） | `powershell -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1` |

**Win32 路径优势**：跟 UE 状态完全无关（Idle/PIE/Compiling 都行），不需要 PIE，能看到 editor UI 全部内容（Outliner、Details Panel、工具栏）。
**PIE 路径优势**：精确路径、确定性高、能用 `show_ui=true` 截 HUD/UMG/WebBrowser。

完整 Win32 路径文档：[references/editor-shot-win32.md](references/editor-shot-win32.md)

## PIE 截图（核心能力）

```bash
# PIE 中截 PIE 视口（默认）
python editor screenshot

# 指定路径
python editor screenshot path=D:/shot.png

# 强制源
python editor screenshot source=pie       # PIE 视口
python editor screenshot source=editor    # Editor 视口
python editor screenshot source=auto      # 自动

# 自定义尺寸（最近邻缩放）
python editor screenshot width=1280 height=720

# 异步（走 FScreenshotRequest，捕获下一帧完整渲染）
python editor screenshot async=true
```

PIE 截图的两条路径：
- **同步（默认）**：`FViewport::ReadPixels` + `FImageUtils::SaveImageByExtension`
- **异步**：`FScreenshotRequest::RequestScreenshot` 引擎自带

**关键陷阱**：
- UE Python 访问 USTRUCT 用 snake_case：`result.bSuccess` ❌ → `result.success` ✅
- 修改 `editor.py` 后必须 `python reload` 重载 Python 模块
- 修改公共头 USTRUCT 加字段 → 必须 `restart`（Live Coding 失败）
- Editor 视口在 headless/最小化时是 0×0，需用 PIE 视口

完整文档：`references/llm-screenshot.md` + 实战踩坑见 [experience/05-screenshot.md](experience/05-screenshot.md)

## e2e 验证一条龙 (tool-fix-07 用)

每个 tool-fix-07 session 默认跑 30 条验证命令 (doc-audit + check-broken-anchors + doc-audit self-check + 6 个 full runtime check (llm-shell info/help/gamestate + llm-shell pcg --help contains debug (session65 regression lock) + llm-shell vfx --help contains coverage (session66 regression lock) + llm-shell material --help generate error-path 包含 5 commands 不含 dead-route `inspect` (session75 regression lock)) + 5 个 uiwebbridge Task 4.2 sub-cmd check (uireactionbus send/subscribe/snapshot/replay/diff; bench 走 L3 Python bench_emit_throughput.py 不在此 e2e harness) + 6 个 lite check (llmshelllite info/help/help uireactionbus expects_json=True (session78 + session80 JSON-escape regression lock)/llm-shell help uireactionbus expects_json=True (session80 mirror — full-side per-ability help JSON validity) /python simple 含空 args regression) + 4 个 UIWebBridge DevTools help-text check (preview_server help contains start/stop + playwright_ui_test help contains run/list) + git diff + session86 fossil-cleanup lock + session88 ue-bridge coverage lock)。**Runtime regression lock (session55)**: `info` / `help` / `gamestate` 3 个 runtime check 各带 `not_contains="5.7"` 负向断言 — exit 0 + valid JSON 太 lax,runtime-side 0 防御不能 catch `engineVersion: "5.7"` 之类的 cpp 硬编码 fossil;doc-audit.py 23 个 engine-version pattern 只覆盖 doc surface,本 gate 镜像到 runtime side。**session65/66 LLM plugin help-text regression lock**: `pcg --help` 必须包含 "debug" 子命令 + `vfx --help` 必须包含 "coverage" 子命令 (静态 string-concat help text 跟 factory/dispatch 注册的子命令 1:1 lock — LLM agent 的实际发现路径)。**session75 LLMMaterial error-path 5cmds regression lock** (`material --help generate` 必须 error message 含 "generate, export, export-schema, list-types, describe-type" 五命令连续 substring + not_contains "inspect") — session65/66 同 class 跟进一步:不是 plugin-facing help text drift,而是 cpp error message drift(`LLMMaterialCommandHandler.cpp:101` 静态 string 跟 `LLMMaterialModule.cpp:303` 的 `BuildAbilityInfoJson` 不一致时 LLM 在 error path 仍能被引导到 dead route)。**session78 Lite ability count forward defense**: `lite help uireactionbus` 必须包含 "send" 子命令 — Lite runtime ability 注册 (UIWebBridge Phase 4 2026-07-10 加 uireactionbus) 跟 `lite help uireactionbus` JSON output 1:1 锁 + 配套 doc-audit.py `lite-ability-count-drift` pattern (78p / 31c 第 31 类) catch stale "Lite N abilities" doc claim。**session80 per-ability-help JSON-escape root-cause fix**: `ShellCommand_Help.cpp` (full + Lite) per-ability help path 从 raw `FString::Printf` 改 `FJsonSerializer::Serialize` — pre-fix plugin description 含 `"`/`\` 时输出 invalid JSON (e.g. UIWebBridge `replay` description 含 `{"name":"...","sequence_id":...}` 模板,内嵌 `"` 破坏外层 JSON),session78 `lite help uireactionbus` 只能用 `expects_json=False` + `contains` workaround;session80 后两 side 都用 `expects_json=True` 全 JSON parse,root-cause closure 不留化石口。已封装到一条命令:

```bash
python .claude/skills/llm-easy-shell/scripts/verify-e2e.py            # 31 checks (full pass)
python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --full-only # 25 checks (跳过 lite)
python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --lite-only # 19 checks (跳过 full)
python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --quiet     # 退出码 only
python .claude/skills/llm-easy-shell/scripts/verify-e2e.py --help      # 打印 usage
```

退出码: `0` 全 PASS, `1` 有 FAIL, `2` 缺 binary。脚本 ponytail-only 拼装现有审计 (doc-audit 118 patterns + check-broken-anchors 全 anchor map + doc-audit --self-check 防止 docstring count drift), 0 业务逻辑。

---

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->

