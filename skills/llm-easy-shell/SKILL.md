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
`restart`：`save → shutdown → MSBuild → 启动引擎`（客户端工作流；`-c "restart"` 与 `--restart` 等价 — 2026-09-04 起 bare `restart` 命令在客户端拦截转 `--restart`，因为插件侧没有 restart handler，直接发只会收到 unknown command 且不会真正重建）

**2026-09-03 起 bare `reload` 同时热重载 Python ability 模块**：在触发 LiveCoding 编译前先执行
`python reload` 同款三步（`UPythonAbilityRegistry::ClearModuleCache` + 重扫描 + dispatch 表重注册，
`ShellCommand_Reload.cpp`）— 纯 `.py` 修改即使 LiveCoding 报 `NoChanges` 也会完成热重载，
返回 JSON 带 `pythonReloaded: true` / `pythonCommandCount` 字段。`--status/--enable/--disable/--ubt`
查询旗标不触发。

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

### ⚠️ `--restart` 报 failure 时，先自己发一条 `info` 再下结论（r982）

**别只信 `--restart` 的返回值。** r982 之前它有个 readiness 探针 bug：editor 回的是
pretty-print JSON（`"success": true`，**冒号后带空格**），而探针只匹配无空格的
`"success":true` —— 永远匹配不上。后果是 editor 明明已经起来、`info` 540ms 就回，
`--restart` 仍然空转满 5 分钟，然后返回 `success:false` + exit 1。

更坑的是失败载荷里会附 `priorCrashLog`（**上一次**运行的崩溃，PID 都对不上），
于是一个健康的启动看起来像刚 OOM 崩了。**loop 因此长期误判「PIE 不可用」，改去写文档。** 探针已修（`main.cpp:4186`，两种拼写都接受）：修前实测「editor 在跑且 `info` 正常，探针仍空转到 300s 上限并 exit 1」，修后同一命令返回 `success:true` / exit 0。

所以遇到 `--restart` 说失败：

```bash
./llm-shell.exe -q -j -c "info"   # ← editor 十有八九活得好好的
```

`info` 有正常 JSON 就直接继续干活，别重启第二次，更别得出「这台机器跑不了 PIE」。

**`compile.ps1` 重建 `llm-shell.exe`**：已改成运行时探测（`$PSScriptRoot` + `vswhere` +
最新 MSVC/SDK），并且**必须带 `/utf-8`** —— 本文件是 UTF-8 中文注释，MSVC 默认按 cp936 读，
某些 UTF-8 尾字节是 `0x5C`(`\`)，会把注释变成续行吞掉下一行代码，报出
`error C2181: illegal else without matching if` 这种跟真实代码无关的假错。

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
| `livecoding` | 触发编译 + 等待完成（最长 180s；r2175 由 60s 改，客户端收包 210s = 180s + 30s buffer。**该值由一次增量实测推导，全量构建未测 = UNVERIFIED**） |
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

## 游戏状态诊断 — 先跑这两条,别用 `gamestate` 猜

`gamestate` 是**有损**读数,不足以定位 gameplay 故障。用游戏自带的 console dump 拿权威内部状态:

```bash
./llm-shell.exe -q -j -c "python editor console survivor.DumpWaveState"   # CurrentWave/bWaveActive/bPaused/EnemiesToSpawn/SpawnTimer
./llm-shell.exe -q -j -c "python editor console survivor.DumpFlowState"   # FSM CurrentState/StateStack/StatePayloads/CurrentHandler
# 两者都只返回 "(dispatched)",真正的输出写进 LogTemp — 必须去日志读:
grep -n "Survivor.DumpWaveState\|Survivor.DumpFlowState" -A 8 Saved/Logs/CODEO.log | tail -30
```

**为什么必须用它们**(2026-08-18 实测教训):

- `gamestate` 的 `isActive` = `bWaveActive && !bPaused` 的**与**,把「波次结束没续上」跟「波次被 pause 卡住」压成同一个 `False`。单凭它我把「WaveClockGate 正在按锚点表 defer 下一波」(完全正常的推进) 误判成「战斗循环死锁 P0」,两个子代理也各自据此编出了两套互相矛盾且都错误的根因。
- `gamestate` 的 `enemyCount` 是**类名子串扫描**,不读 WaveManager 权威列表。
- FSM 状态 (`UGameFlowSubsystem::StateStack`) 是 private 且非 UPROPERTY → **反射读不到**,`gamestate` 永远不会有 `flowState` 字段。`survivor.DumpFlowState` 是唯一入口。

### 怎么在 PIE 里真的把战斗跑起来（r982 实测）

`call /Actor/PortalActor_X TriggerCombat` **单独调不会开战**。它会成功返回、WFC 会生成地块、
biome 会设上，然后 GameMode 把事件丢掉：

```
[SurvivorGameMode] OnPortalCombatTriggered: fired outside PortalModal context
                   (FlowState=EGameFlowState::MainCity) — ignored
```

这是**故意的**（`SurvivorGameMode.cpp:6333` 守卫 + `:6325` 注释写明就是为了让这种
test-path 假象暴露出来）。真玩家路径是 portal overlap → `EnsurePortalModalPushed` →
PortalModal → `OnPortalCombatTriggered`，而 `EnsurePortalModalPushed` 没有 BlueprintCallable，
`call` 不到；直接把 pawn `set Location` 传送进 TriggerSphere 也**不会**触发 overlap。

要看真实战斗，走 designer console 最省事：

```bash
./llm-shell.exe -q -j -c "play"
./llm-shell.exe -q -j -c "python editor console survivor.SetWave 1"   # 直调 AWaveManager::StartWave(1) — fake-bridge, 跳 EnsurePortalModalPushed → OnPortalCombatTriggered → StartBattle → D1 SetSurvivalTime(0) + r1266 C1 SetIsFocusable 真修 都不会跑; 只验刷怪/计数, **不能验 tarot focus / run clock 锚点**
./llm-shell.exe -q -j -c "python editor console survivor.EnterPortal Forest"  # 走真玩家路径 (r1178 vR1178-ENTERPORTAL-CHEAT-DEV ship #227): EnsurePortalModalPushed → OnPortalCombatTriggered → StartBattle → SetSurvivalTime(0) + SetIsFocusable 完整触发; **biome (跟 SurvivorGameMode.cpp:19771 docstring 1:1 锁, r1269 A1 真修)**: Forest | Night | Hill | Water | ShrineRuins
```

**headless/后台驱动 PIE 前先 `survivor.FocusLossPause 0`**（cvar，r1017 起）：编辑器窗口失焦会触发失焦暂停闩锁（GameMode Tick 轮询，单向 latch），世界一停 World TimerManager 全停 — cinematic 卡 83s / WaveTime 冻结 90s 的实测教训。

实测能跑通完整循环：spawn → 玩家掉血 → 击杀 → XP/金币 → 波次清空 → **升级** → 下一波。
之后 W3+ 会被 `WaveClockGate` 按锚点表（W1@30s / W2@120s / W3@420s … W7@870s，
`SurvivorGameMode.cpp:2350`）defer —— **那是正常节奏，不是卡死**。

另注：`capturedLogs` 只回 Warning 及以上。`Display` 级的 dump 字段（如
`EventStingMap.Num=[0]`）必须去 `Saved/Logs/CODEO.log` 里读。

**日志时间戳是 UTC**,跟本地时间差 8 小时 — 判断某条日志是不是"本次会话"时按 UTC 换算,别因为日期看着像昨天就当成陈旧日志。

## info 命令

`info` 是唯一的状态查询入口，返回项目信息 + 编辑器实时状态：

```json
{
  "project": "CODEO",
  "engineVersion": "++UE5+Release-5.8-CL-...",
  "port": 15152,
  "level": { "name": "Lvl_SurvivorTest", "path": "/Game/...", "actorCount": 30 },
  "pieState": "Stopped",
  "pieWorldTimeSeconds": -1.0,              // PIE 世界时钟; -1 = PIE 未运行
  "pieRealTimeSeconds": -1.0,               // 墙钟, 永远前进; -1 = PIE 未运行
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
- `pieWorldTimeSeconds` / `pieRealTimeSeconds` — **活性读数**（2026-10-01 r2117 D3 新增）。`pieState` 是**状态**读数（"暂停条件此刻成不成立"），**不是**"世界在动"。同一字段连采两次：`pieWorld` 不动而 `pieReal` 在动 ⇒ **世界冻结**，此时读任何"事件没发生"都作废。判「某事件没发生」的三种同形读数（真不可达 / 没触发它 / 被别的缺陷挡住）只有活性读数能分开。已复发两轮（r2114 D2 / r2115 S1，第二次污染了整整 4 分钟实验）—— **先断言活性，再读"没有"**。
- `editorState` — 顶层状态机: `Idle` | `PIE` | `Compiling` | `PreparingPatch` | `Saving` | `Loading` | `Building`。在执行任何修改操作前先确认它不是 `Compiling`/`PreparingPatch`。
- `livecoding.compiling` — LiveCoding 自身的二进制状态,会滞后于 `editorState`。
- `livecoding.requiresRestart=true` — 头文件被改了,**只能 restart editor,继续用 `livecoding` 会编译失败**。
- `livecoding.reason` + `recommendation` — 跟 `requiresRestart` / `hasCompleted=true` 同时出现,告诉 LLM 下一步该做什么。
- `hint` — 综合 `editorState` + `livecoding` 的人类可读指令(LLM 直接转给用户即可)。

## Ability 架构

**内置（Core）**：37 个原生命令 = 29 核心 + 7 UI 调试子命令（见下方 §UI 调试）+ 1 已弃用 `livelog`（用 `log --compile` 代替；第 38 条 `ui state` 已迁 LLMSurvivorShell 宿主插件）
- Actor（8）：`spawn` `rm` `cp` `mv` `select` `focus` `call` `set`
- 资产（4）：`new` `save` `mkdir` `addcomp`
- 编辑器（9）：`play` `stop` `pause` `undo` `redo` `info` `log` `msglog` `gamestate`
- 查询（5）：`ls` `cat` `find` `help` `discover`
- **AI 集成（1）：`mcp`（UE 5.8 官方 ModelContextProtocol 桥接 — `mcp status|start|stop|tools|call|config`，详见 [references/commands.md](references/commands.md#mcp)）**
- 热重载（1）：`livecoding`（别名 `reload` / `lc` 三者等价）— 2026-09-03 起 bare `reload` 在 LiveCoding 编译前同时热重载 Python ability 模块（ClearModuleCache + 重扫描 + dispatch 重注册，等价 `python reload`；返回 JSON 带 `pythonReloaded`/`pythonCommandCount`）

**内置 Ability**：`actor` `editor`（加前缀调用，与直接调用原生命令完全等价，无额外功能）

**插件（Extension）**：`help` 列出所有已注册 Skills，已知：`vfx` (LLMVFX) `material` (LLMMaterial) `ui` (LLMDynamicUI) `pcg` (LLMPCG) `llmms` (LLMMetaSound) `llmstatetree` (LLMStateTree) `quixel` (LLMQuixel) `llmwhitebox` (LLMWhitebox) `uireactionbus` (UIWebBridge) `python` (LLMEasyShell 内置)

<!-- Forensic: see SKILL_CHANGELOG.md §3 -->

**UI 调试**（Slate/UMG 可观测性 + 模拟输入，8 命令族）：`ui dump|find|state|info|shot|press|type|tick`
- `dump` UMG widget tree JSON · `find` 按 text/class/path 搜节点 · `info` 单节点 detail (含 UWebBrowser→cef_state)
- `shot` 整 VP 或单 widget 截图 · `press mouse|key` + `type` 逐字符 + `tick` polling
- 真闭环: z-order bug / WebBrowser CEF 黑屏 / GameOver 风暴 3 个真 bug 的可观测性 + 模拟操作通道
- 详见 [experience/2026-06-12-slate-ui-inspector-summary.md](experience/2026-06-12-slate-ui-inspector-summary.md) (7 命令表 + 关键架构决策 + DoD 6/7)
- 教学 lesson: [experience/llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md](experience/llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md) — `success: true` 不证明 "点中了",只证明 "没 crash + 路径解析完成"

> `actor spawn` = `spawn`，`editor play` = `play` — 前缀机制仅为兼容性保留，建议直接使用原生命令。

## Python Ability（可扩展的命令）

`python` 是一个特殊的 Ability，它的命令来自文件系统而非 C++ 注册。Agent 有完全的自主权来创建新的 Python 能力。

### 工作原理

**约定**：任何插件都可以按下面这个布局托管自己的 python 能力 ——
`<Plugin>/Content/Python/<PackageName>/abilities/*.py`

```
Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/     ← 平台内置能力
├── __init__.py
├── registry.py       # Ability 基类（不可删除）
└── abilities/
    ├── __init__.py
    ├── _base.py          # 下划线开头 = 私有
    ├── _example.py       # 下划线开头 = 私有
    └── <name>.py         → python <name> 命令

Plugins/LLMMaterial/Content/Python/LLMMaterialAbilities/    ← 材质能力（通用）
└── abilities/
    └── material.py       → python material 命令

Plugins/LLMSurvivorShell/Content/Python/LLMSurvivorShellAbilities/  ← 项目专属
└── abilities/
    ├── survivor_material.py → python survivor_material 命令
    └── mat_sm6_check.py     → python mat_sm6_check 命令

Content/Features/Survivor/Scripts/   # 项目脚本权威路径
├── <your_script>.py         → python <your_script> 命令
└── ...                      # 项目拥有的 .py ability
```

> **注**：装载器（`PythonAbilityRegistry`）按**插件发现**扫描
> `<Plugin>/Content/Python/<PackageName>/abilities/` —— 不再写死某个插件的目录。
> 每个宿主的包名必须**因插件而异**（Python 的包是目录绑定的，一个包不能劈到两个插件目录下），
> 所以模块名是 `<PackageName>.abilities.<文件名>`。
>
> **顶层 helper 命名空间**（`_base` / `registry`）归平台宿主（LLMEasyShell）独占 ——
> 33 个项目脚本写的是 `from _base import ...`（顶层 import），别的宿主的同名模块会遮蔽它。
> 别的插件要复用 Ability 基类，用绝对导入 `from LLMShellAbilities.registry import Ability, Command`。
>
> **优先级**：插件宿主 > 项目脚本（同名时插件那份赢）。插件之间按插件名排序 —— 插件加载顺序不稳定，
> 而同名冲突必须确定性。历史上文档写的是 "Content 优先"，那与代码相反，已改正。

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
   - `Plugins/<PluginName>/Content/Python/<PackageName>/abilities/` (任何插件都可托管)
   - `Content/Features/Survivor/Scripts/` (项目脚本权威路径,避免双轨化石)
2. 实现 `main(args, context)` 或 `execute(args, context)` 函数
3. Python ability 自动被发现并注册 (插件宿主 + 项目目录双路径扫描去重, 插件优先)

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
| ~~`python scene`~~ (r164 DROP — 5 sub-cmds broken + 0 caller) | 场景 Actor 查询已由 builtin `ls /Level/Actors` 覆盖 |
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

> **注**：此表为精选示例，非完整注册表。完整 Python ability 列表见 `Plugins/<PluginName>/Content/Python/<PackageName>/abilities/`（每个非 `_` 开头的 `.py` 自动注册为 `python <文件名>` 命令）+ `Content/Features/Survivor/Scripts/`（项目脚本权威路径），或在编辑器会话中运行 `help` 查看所有已注册 Ability。

路径：
- 平台内置：`Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/`
- 插件托管：`Plugins/<PluginName>/Content/Python/<PackageName>/abilities/`（材质 → LLMMaterialAbilities；项目专属 → LLMSurvivorShellAbilities）
- 项目权威：`Content/Features/Survivor/Scripts/`

**5. 描述规范（Docstring Guidelines）**

创建 Python ability 时，**docstring 第一行必须具有语义**——描述"做什么"而非"怎么实现"。

| 写法 | 评价 |
|------|------|
| `"""Access Material parameters."""` | 差 - 不说明能做什么 |
| `"""Read and write Material parameters (scalar, vector, texture) via Python binding layer."""` | 好 - 明确说明能力范围 |
| `"""Query scene actors: stats, lights, proximity search, tags, and class distribution."""` ~~(r164 scene.py 已 DROP, 此示例 fossil)~~ | 好 - 列出具体功能 |
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

Python abilities 在编辑器启动时自动扫描注册。修改平台内置 abilities 目录或项目脚本路径后需要重启编辑器（或调用 `reload`）使更改生效。扫描面: 各插件 Content/Python/<PackageName>/abilities/ + Content/Features/<Feature>/Scripts/ 项目脚本 (插件宿主优先于项目脚本, 同 CommandName 先到先得去重)。

## 调用方式

```bash
.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -c "ls /Level/Actors"
.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe --restart
```

## 自检：扫描决策面（`--selftest-sweep`）

```bash
.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe --selftest-sweep
```

**不连编辑器、不杀任何进程**，跑 `KillAllProjectRelatedProcesses` 的决策面 10 例并打印
got/want 对照，全绿 exit 0。

覆盖的三条轴（r2229 D-SCAF-5 把决策抽成 `DecideSweepAction()` 纯函数后才有）：

| 情形 | 期望 |
|---|---|
| 孤儿 helper（父已死 / 父 PID=0） | `KILL` |
| **有活爹的 helper**（别席的在途通道） | `SKIP`（另打一行 SKIP 日志） |
| 本进程 / 祖先链（r2156 自排除） | `IGNORE` |
| `roots` 为空（**实测常见形态**） | `IGNORE`，整个清理块不执行 |

> **为什么需要它**：r2227 D-SCAF-4 加的 SKIP 分支（多 agent 并行时放过别席的活通道）
> 要求 `roots>0` 且该 helper 父进程在扫描瞬间还活着 —— 而正常单编辑器路径走不到
> （主编辑器优雅关闭后 `roots=0`，清理块整块跳过）。
> 想手工造这个场景得开第二个编辑器，会杀 `UnrealEditor-Cmd`、可能打断并行席正在跑的电池。
> ⇒ **把决策抽成纯函数就不必复现那个环境**：决策面照样能全跑一遍，且零风险。

---

## 错误排查

| 问题 | 解决 |
|------|------|
| Actor not found | `ls /Level/Actors` |
| Asset not found | `ls /Assets` 或 `find /Game *` |
| Function not found | `discover <path> --funcs` 查看可用函数 |
| 连接失败 | 启动 UE 编辑器 |
| `--restart` 报 `stage:"hung"`（`info` 死活不通） | **先分诊再动手**：`python tools/compile/ue_editor_shell_health.py` 取四条读数（listener / `LLMEasyShell: Tick #` 心跳 / 游戏线程日志推进 / 有无模态窗）⇒ 判定给出「等 / restart / 交人 / 通道没人 serve」。**`hung` ≠ 编辑器死了，也 ≠「PIE 不可用」**（r1921 曾据此空手一整轮）。本轮实测形状是「端口在听 + 心跳 0 条 + `GFrameCounter` 持续推进」。结论 = 那台 boot 从未进入常态 tick/serve 阶段：心跳全程 0 条，而**健康基准**（`CODEO-backup-2026.09.28-15.04.21.log`）里心跳自 boot 后 ~2.5min 起、2.7h 累计 130,070 条；`GFrameCounter` 持续推进（线程没冻）、无模态窗、日志尾部一直是 `LogStaticMesh`/`LogDerivedDataCache` 类一次性构建行 ⇒ `--restart` 的 300s readiness cap 远小于一台 4 核 VM 全量重建后首启的资产构建时长（本轮 >2h 未落定）⇒ **等，预算按小时，不是杀**。两条假说**均已被盘上证伪，别再引用**：①「一次性构建饿死游戏线程」（帧号取差推翻）；②「控制通道同毫秒起了两次」（一次成功 start 就有两处发射点：`LLMEasyShellTcpServer.cpp:207` + `LLMEasyShellSubsystem.cpp:346`，健康会话同样出现两枚 ⇒ 该形状无鉴别力）。 复算（三条各一命令）：`grep -ac 'LLMEasyShell: Tick #' Saved/Logs/CODEO.log`（本轮 0 / 健康基准 130,070）· `grep -a 'LogHttp: Warning' Saved/Logs/CODEO.log | sed -n '1p;40p;80p'`（看方括号那列**在推进**）· `ls -t Saved/Logs/CODEO-backup-*.log | head -3` 里挑一份**被服务过**的会话当基准（`grep -acE 'survivor\.[A-Z]'` > 0 的那份），别拿从没服务过命令的短会话当健康样本。全文见 [incidents/llmeshell-first-boot-asset-build-outlasts-restart-readiness-window-2026-09-29.md](experience/incidents/llmeshell-first-boot-asset-build-outlasts-restart-readiness-window-2026-09-29.md) |
| 分诊器判 `full-shell-down`（full 通道没起来，**但 Lite 通道活着**）| **不要 `--restart`、不要 kill**。一台编辑器同时开**两个** TCP 监听：full `LLMEasyShell`（本表其余各行说的那条，写 `.claude/skills/llm-easy-shell/llm-shell/.current_port`）与 `LLMEasyShellLite`（**另一个** `.current_port`，独立端口段 `[15201,15250]`，`LLMEasyShellLiteSubsystem.cpp:114/129`）。两枚插件的心跳是**字面量一样**的 `LLMEasyShell: Tick #`，只有 Log 类别前缀能分开 —— 分诊器据此分两路计数。`--restart` 内部是 save→shutdown→`KillAllProcess` 树（`llm-shell/main.cpp:4478/4490` 调 `KillAllProjectRelatedProcesses()`）⇒ **会把那台正干活的编辑器连同未保存工作一起杀掉**。改用只读的 [llm-easy-shell-lite](../llm-easy-shell-lite/SKILL.md)；要写操作/PIE 才需 restart，届时先确认 Lite 上的活已落盘。（r2155 新增的第 6 态；判据见 `tools/compile/ue_editor_shell_health.py` 模块 docstring） |
| 控制台 cheat 拿不到读数（`-c "survivor.X"` 回 `Unknown command`）| 引擎控制台命令必须带 **`console ` 前缀**：`llm-shell.exe -c "console survivor.DumpWorldTier"`。裸 `-c "survivor.DumpWorldTier"` 会被路由成 **llm-shell 自身**的命令取，回 `Unknown command: survivor.DumpWorldTier` —— 错误信息长得像「cheat 没注册」，实际是 shell 路由错了一格，排错方向完全相反。判据：`console <cmd>` 的返回带 `"kind":"command","world":"pie"`（已进引擎）；裸形形的返回带 `"error":"Unknown command"`。cheat 读数在 `Saved/Logs/CODEO.log` 里（`LogTemp: Warning: [survivor.X] ...`），不在 shell 的返回值里。（r2156 现场学：本轮要验 PIE 下的 designer cheat，在这一行上赶了一次） |
| 命令超时 | 超时后自动查询 `info`，响应中含 `editorState` 查看编辑器状态 |
| `cat`/`ls`/`discover` 回 `Unknown path: C:/Program`（或 `C:/Program Files/Git/...`）| **Git Bash 的 MSYS 路径转换把 `/` 开头的参数改写成了 Windows 路径** —— 而本工具的寻址命名空间整个是 `/` 前缀的（`/Game/` `/Actor/` `/Level/` `/Assets/`），两者正面相撞。服务端实收会变成 `cat C:/Program Files/Git/Game/...`（`Saved/Logs/CODEO.log` 的 `LLMEasyShell: Processing command:` 行可自证）。**已修**：`~/bin/llm-shell` wrapper 顶部加了 `export MSYS2_ARG_CONV_EXCL='*'`。它之所以活了很久：本文档记载的调用惯例是**带引号整串**（`-c "ls /Level/Actors"`），整串不以 `/` 开头 ⇒ 恰好免疫；仓内探针走 Python `subprocess` ⇒ 也免疫 —— **唯一会踩雷的裸形式从没被任何文档或测试覆盖**。临时绕过：`MSYS2_ARG_CONV_EXCL='*' llm-shell cat /Game/...`，或直接用带引号的 `-c "cat /Game/..."`。（r2166 D2 现场学） |
| find 返回 "Unknown type: /X" | 命令已支持 `find /Game <pattern>` 路径格式 |
| cat 不显示属性值 | 已修复：显示所有 BlueprintVisible 属性当前值（含 struct） |

**更深入的踩坑经验（按主题）**：

- [experience/01-builtin-commands.md](experience/01-builtin-commands.md) — Actor 路径 `/` 解析、`new --key=value` 崩溃、stdin 与 `-c` 冲突、set Blueprint 父类限制、FObjectProperty 崩溃
- [experience/02-python-abilities.md](experience/02-python-abilities.md) — Python `ExecuteFile` 模式、output 字段缺失、`_call_with_world` 死写 bug、b 前缀 bool 字段读不到
- [experience/03-blueprint-property.md](experience/03-blueprint-property.md) — bpprop 5 个 ClassProperty 坑、FClassProperty MetaClass 校验、`#` 路径 FObjectProperty fallback、嵌套路径 walk
- [experience/04-build-and-restart.md](experience/04-build-and-restart.md) — 何时 `livecoding` / 何时 `restart` 决策树、USTRUCT 改字段必 restart、`reload`/`python reload` 热重载 Python 模块（2026-09-03 起 bare reload 也走同路径）、**Build.cs 加新 PrivateDependencyModuleName 必须 restart（livecoding 报 success 但 UBT 全量 build 仍会挂）**
- [experience/05-screenshot.md](experience/05-screenshot.md) — 截图双路径（sync vs async+ui）、CEF 初始化延迟、2026-06-01 新输出格式

> 详细语法见 `references/commands.md`
> 源码调试经验见 [experience/debugging.md](experience/debugging.md)
> PIE 截图完整指南见 `references/llm-screenshot.md`
> **Editor 窗口截图**（Win32 路径，绕开 FViewport 0×0 硬约束）见 [references/editor-shot-win32.md](references/editor-shot-win32.md)
> 完整经验库（39 个教训）见 [experience/README.md](experience/README.md)
>
> (tool-fix-137 2026-06-29: SKILL.md L401 fossil '31 个教训' 跟实际 experience/ 9 canonical 文件 grep 1:1 验证的 39 个教训/规则 (6+4+5+6+5+1+4+7+1) 差 8; 9248b59 2026-06-27 当时 31 正确, 但 06-cli-flags.md (+1) + 07-editor-shot-win32.md (+4) + debugging.md 5 个新教训 (5→7 +2 实际是新增, 不是漂移, 累计 +7) + t3-bpcomp-tobjectptr-reflection-fix.md (+1) 累计 +8 加成后 31→39 SKILL.md L401 未同步, experience/README.md L3 也 fossil 38, 本 fix 闭合 2 surfaces 1 rootCause family)

## 截图 — 三条路径选对

| 场景 | 用哪条 | 命令 |
|------|--------|------|
| **看 PIE 里玩家真正看到的画面（含 HUD / UMG / CEF 壳面板）** | **Win32 + `-Pie`（唯一可靠路径）** | `powershell -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -Pie` |
| 看 **editor 应用窗口**（菜单/工具栏/**Outliner**/视口/状态栏） | Win32 路径（不带 `-Pie`） | `powershell -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1` |
| 看 **PIE 3D 场景**（纯 3D，不含任何 UMG/CEF 图层） | `python editor screenshot` | `play` → `sleep 5` → `python editor screenshot path=X source=pie` |
| 不知道选哪个 | 带 `-Pie` | 见第一行 |

> **必须带 `-ExecutionPolicy Bypass`**（2026-09-10 r1209 实测）：本机 PowerShell 执行策略默认禁止运行脚本，
> 不带该旗标时 `editor_shot.ps1` 直接报 `UnauthorizedAccess` / `SecurityError` 退出，一个像素也截不到。
> 带上后同���条命令正常输出 `hwnd=... size=1374x856` + `saved: Saved\Screenshots\editor_win32.png`。

**Win32 路径优势**：跟 UE 状态完全无关（Idle/PIE/Compiling 都行），不需要 PIE，能看到 editor UI 全部内容（Outliner、Details Panel、工具栏）。

### ⛔ `python editor screenshot` 截不到 UMG / CEF —— 这条曾被本文写反

**旧版本文在此处声称「PIE 路径能用 `show_ui=true` 截 HUD/UMG/WebBrowser」，那是错的**，2026-10-10 r2229 实测推翻：

- `python editor screenshot` 自陈 `Captures: 3D scene only (Slate widgets NOT included — UMG/HUD/WebBrowser invisible)`；
- 同步路径（`async=false`）**忽略 `show_ui`**（传了也照样输出 `3D scene only`）；
- 异步路径（`async=true show_ui=true`）在本机**接受请求但不落盘**；
- ⇒ **战斗壳那类 CEF 面板只能用 Win32 `-Pie` 取证。**

### ⛔ 不带 `-Pie` 截 PIE = 一个长得很像证据的假阴性

`editor_shot.ps1` 不带 `-Pie` 时按面积选窗，PIE 运行期**永远选到编辑器主窗**，
抓到的是**没有 PIE UMG/CEF 图层**的编辑器视口 —— 图像看着完全合法，
极易被读成「PIE 里这个面板不渲染」。

脚本会为此发一条告警，看到就要照做：

```
WARNING: PIE preview window detected (hwnd=..., 1000x567). Capturing the EDITOR
window instead -- re-run with -Pie to capture what the player actually sees.
```

**2026-10-10 r2229 实例**：本席据 `python editor screenshot` 的 3D-only 自陈，
断言「PIE 像素通道对壳面板不可用」并**据此立了一张票**；下一轮试 `-Pie` 即取到
主城飞行 HUD 的真机像素（`SkyGlideHud` 四读数清晰在屏）。
⇒ **纪律：「我没找到」与「它不存在」必须分开记账**，前者先穷举本仓已有通道再下结论。

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
- 修改 `editor.py` 等 .py 后跑 `reload` 重载 Python 模块（2026-09-03 起 bare `reload` 也热重载；`python reload` 依旧可用）
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

