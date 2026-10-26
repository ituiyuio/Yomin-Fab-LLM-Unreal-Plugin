---
name: llmeshell-first-boot-asset-build-outlasts-restart-readiness-window
description: "--restart 报 hung：端口在听但无人 accept——全量重建后首启的资产构建时长超出 300s readiness 窗，编辑器其实活着，正确处置是按小时等"
metadata:
  node_type: memory
  type: feedback
---

# `--restart` 报 `hung`：端口在听但无人 accept——首启资产构建超出 300s readiness 窗（编辑器活着；「控制通道双起」假说已被证伪）（2026-09-29）

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


## 症状

`llm-shell --restart` 打成这样：

```json
{"success":false,"stage":"hung",
 "message":"Push signal arrived but 'info' never round-tripped within the 300s readiness window (process still alive)"}
```

链路上前半段全绿：UBT 全量 `exit 0`、编辑器起来了（PID 10780）、readiness 推送事件 40s 就到了。
只有最后那枚 `info` 往返始终不通 ⇒ 载荷 `stage:"hung"` ⇒ 本轮据此下了「**PIE unusable**」。

**这个结论是错的。** `hung` 只说「300s 内没谈拢」，不说「编辑器死了」，更不说「PIE 跑不了」。
同族误判 r1921 已经整轮死过一次（账在 `.lrh/ultimate-loop/rounds/r1922-spec.md` §2.5 与
`docs/survivor/0-vision/DECISION-2026-09-29-r1922-pocket-capacity.md`）。r1923 把手工分诊固化成
`tools/compile/ue_editor_shell_health.py`，四条读数 + 一个判定，见文末。

## 四读数怎么取（本轮实测的原始动作）

### R1 listener 在不在、归谁

```bash
cat .claude/skills/llm-easy-shell/llm-shell/.current_port        # 15157
netstat -ano | grep "127.0.0.1:15157"
#   TCP    127.0.0.1:15157        0.0.0.0:0              LISTENING       10780
```

端口有三个来源，能找到几源点几源，**在场的一致**才算干净（缺源不算分歧 —— `llm-shell-quiet.log`
会被下一次运行截断）：`.current_port`（权威，插件写的）、`CODEO.log` 里
`LLMEasyShell: Wrote port 15157 to .../.current_port`、`llm-shell-quiet.log` 里
`Failed to connect to 127.0.0.1:15157 (cached port for ...)`。
三源不一致是本仓记过账的真故障形态（多实例抢写，见 `llmeshell-port-handshake-and-stale-pch-2026-09-27.md`）。

**只认 `127.0.0.1:<port>` 那一行**：同一枚进程里还有第二套 server（`LogLLMEasyShellLite: ... started on
port 15201`，`0.0.0.0` 绑定），本机测量期间另有并发的 `UnrealEditor-Cmd.exe` 也绑在 `0.0.0.0:15201`
上 —— 按端口号在 netstat 里捞 PID 会捞到**别人家的进程**。

### R2 tickable 心跳

服务端 accept 循环挂在 tickable 上：`FLLMEasyShellTickable`（`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp:63-160`）
每 tick 调 `Server->Tick()`，后者每 ~5s 打一行（`LLMEasyShellTcpServer.cpp:243-266`）：

```
LogTemp: LLMEasyShell: Tick #<n> (port <p>, running YES)
```

```bash
grep -ac "LLMEasyShell: Tick #" Saved/Logs/CODEO.log      # 本轮读数: 0 —— 一条都没有
```

0 条 ⇒ 没有任何人 `accept()` ⇒ 客户端连上去是 **Connection refused**（`curl -v` / `socket.connect`
都实测 `WinError 10061`）。这跟「超时」不是一回事：超时是握上了没人回，refused 是根本没进 backlog。

> 别去找另一枚心跳：`FLLMEasyShellTickable alive, port=%d, PIE=%d` 是 `LogLLMEasyShell **Verbose**`
> 且 `GFrameCounter % 600 == 0` 才打（同文件 :88-96），默认日志里恒 0 条，拿它判活会得到假阴性。

### R3 游戏线程死活 —— 只看**非 LogHttp** 的行的时间戳

```bash
grep -v "LogHttp" Saved/Logs/CODEO.log | tail -3
```

本轮实测：`LogHttp: Warning: HTTP request timed out after 3.00 seconds` 每 30s 一行雷打不动
（它跑在 HTTP 自己的线程上），而游戏线程侧最后几行是
`LogStaticMesh: Clustering [130.30s]` / `Leaves [40.53s]`（09:45:45Z），之后静默 ~37min；
同期 `DerivedDataCache` 还在落盘 ⇒ 本席首判「全量重建后的首启一次性 Nanite/资产构建把编辑器 tickables 饿住了」。
**该推断的最后一环随后被自己的另一把尺推翻**（见下文「本席首判错在哪」）：日志方括号那列是 `GFrameCounter % 1000`（引擎 `OutputDeviceHelper.cpp:24`；`GFrameCounter++` 在 `LaunchEngineLoop.cpp:6131`，每次**完整引擎 tick** 末尾一次），沿 30s 那行 `LogHttp` 取差 ⇒ `[1]@08:48 → [701]@09:08 → [626]@09:28 → [546]@09:48 → [23]@10:08`，**「静默」那 1.5h 里引擎 tick 一直在推进，游戏线程没冻**。真读数形状是「监听在 / 心跳 0 / tick 照走 / `LogTemp: LLMEasyShell TCP Server started on port 15157` **同毫秒出现两枚**（`CODEO.log:9082-9083`）」⇒ **结论（含两条被盘上证伪的假说，都留着）**：真形状 = 「端口在听 / 心跳全程 **0 条** / `GFrameCounter` 那列持续推进 / 无模态窗 / 业务日志尾部一直是 `LogStaticMesh`+`LogDerivedDataCache` 类一次性构建行」。对照**健康基准会话** `CODEO-backup-2026.09.28-15.04.21.log`：心跳从 boot 后 **~2.5min** 出现首条，2.7h 累计 **130,070** 条 ⇒ 本轮那台 boot 从未进入常态 tick/serve 阶段，而 `--restart` 的 readiness cap 只有 **300s**，远小于一台 4 核 VM 全量重建后首启的资产构建时长（本轮 >2h 未落定）。①「一次性构建把游戏线程饿死」被帧号取差推翻；②「控制通道同毫秒起了两次」也被推翻 —— `TCP Server started on port` 一次成功 start 就有两处发射点（`LLMEasyShellTcpServer.cpp:207` + `LLMEasyShellSubsystem.cpp:346`），健康会话同样出现两枚 ⇒ 那个形状**没有鉴别力**。方法账：判「0 命中 = 坏」之前必须先拿一份已知健康的同类样本做基准，我头三次抽的 backup 恰好都是从未服务过命令的短会话（这才是「健康会话也 0 条」那个错判的来源）。

两条时序口径（都是本仓记过账的坑）：

* **日志时间戳是 UTC**（`[2026.09.29-09.49.07:525]`），本机 UTC+8。拿本地钟减它就恒负 ⇒ 「心跳永远新鲜」。
* **mtime 不能当新鲜度代理**：LogHttp 每 30s 从别的线程写一行，文件 mtime 一直在走，而游戏线程可以整段冻着。
  新鲜度只能从**带类别前缀的时间戳**算。（同一个坑在 `lc_build_gate.py` 的 (e) 判据上是另一副样子：
  那里是「只看最新一枚日志，否则 `CODEO-backup-*.log` 里上一次会话的 `LogExit` 会给当前进程定罪」。）

### R4 模态弹窗

`tmp/r1923_win_probe.py`（一次性 ctypes 探针，逻辑已搬进工具）：`EnumWindows` + `GetWindowThreadProcessId`
过滤本 PID + `IsWindowVisible` + `IsWindowEnabled`。

```
visible top-level windows for pid=10780: 1
  hwnd=0x8b03dc enabled=1 class='UnrealWindow' title='CODEO - …编辑器'
DISABLED top-level windows (game thread usually blocked behind a modal):   ← 空
```

⇒ 本轮**不是**弹窗卡的。「可见 + `enabled==False`」才是模态签名；隐藏窗口的 enabled 状态是噪声，别算。

## 判定表

| listener | 心跳 | 游戏线程 | 弹窗 | verdict | action | 处置 |
|---|---|---|---|---|---|---|
| up | 新鲜 | 任意 | 无 | `ok` | `use_shell` | 直接干活 |
| up | 陈旧/缺席 | 活 | 无 | `no-tick-heartbeat` | **`wait`** | **等**：不许 kill、不许 restart、不许下「PIE unusable」 |
| up | 陈旧/缺席 | 静默超一次性构建窗口 | 无 | `no-tick-heartbeat` | `human` | 状态名不下「饿/僵」因果（MF-10 的改口）；心跳断且线程静默超窗 = 僵，交人判读，loop 仍不擅自动手 |
| down | 任意 | 任意 | 无 | `no-listener` | `restart` | 这才是 `llm-shell --restart` 的正牌触发条件 |
| 任意 | 任意 | 任意 | 有 | `modal-dialog` | `human_click` | 只有人能点；restart/kill 都会丢未保存工作 |
| — | R1/R2 读不全 | — | — | `instrument-failure` | `fix_tool` | **exit 2**：仪器坏了不是「读出来没问题」 |

四枚读数各自决定不同的状态迁移（`--selftest` 逐条钉住：翻掉哪枚读数会落到哪一格，且四枚的迁移集两两不同），
所以「等 / restart / 交人」三条出口各自对应一枚独立证据，不存在两态共用一枚信号。

## 怎么跑

```bash
python tools/compile/ue_editor_shell_health.py            # 人读四读数 + 判定
python tools/compile/ue_editor_shell_health.py --json     # 机读（loop 用；退出码 0=有判定，2=仪器坏）
python tools/compile/ue_editor_shell_health.py --selftest # 合成夹具 + 带牙齿/迁移归属检查，不需要引擎在跑
```

只读、零副作用：不 kill、不 restart、不写文件、**不向端口发起连接**（R1 只读 netstat）。
判定为 `wait` 时正确动作是隔 60-120s 复跑本工具直到 R2 新鲜，而不是改去 `--restart --skip-build`。

## 本轮盘上复核：`hung` 那一步的推理链有一环站不住（下一席必读）

前三条读数全部复核成立（listener=PID 10780 / 心跳 0 条 / 无模态窗 / connect refused）。
**「没人 accept ⇒ `FLLMEasyShellTickable::Tick` 没跑 ⇒ 游戏线程被饿」这条推断链的最后一环，在本机当下的状态里不成立**：

1. 日志行首第二列 `[NNN]` 是 `GFrameCounter % 1000`（`Engine/Source/Runtime/Core/Private/Misc/OutputDeviceHelper.cpp:24`），
   而 `GFrameCounter++` 在 **`FEngineLoop::Tick()` 的最末尾**
   （`Runtime/Launch/Private/LaunchEngineLoop.cpp:6131`，注释原文 "Once for each engine tick"）。
   它推进 = 游戏线程**完整走完**了引擎循环。按每 30s 一行 LogHttp 携带的帧号做 mod-1000 差分：
   `08:50Z→10:00Z` 全程持续推进（≈8-20fps，含「静默 37min」那段）。⇒ 游戏线程没冻。
2. 那为什么 tickable 不出声？`FTickableGameObject::TickObjects`
   （`Runtime/Engine/Private/Tickable.cpp:170-220`）除了 `IsTickable()` / `IsTickableInEditor()`，
   还钉着一条 `TickableObject->GetTickableGameObjectWorld() == World`。
   `FLLMEasyShellTickable` 没覆写它 ⇒ 默认 `GWorld`；而编辑器那条 `TickObjects(nullptr, LEVELTICK_All, …)`
   （`Runtime/Engine/Private/GameEngine.cpp:1973`）传的是 null world，**匹配不上** ⇒ 它只能从
   **世界 tick** 那条路被叫醒（`Runtime/Engine/Private/LevelTick.cpp:1821`）。
   所以「心跳缺席」的准确读法是「**这个 tickable 没被世界 tick 叫到**」，不是「游戏线程停了」。
3. 另一枚待查线索（本席只观测，未定论）：`CODEO.log` 里 `LogTemp: LLMEasyShell TCP Server started on
   port 15157` **连打两行**（:9082/:9083），且 15157 在 netstat 里只有一行 —— 同进程内
   `StartControlChannel()` 跑了两遍、两套 `TcpServer`+tickable（Windows `SO_REUSEADDR` 容许重复 bind）。
   「有 socket 在听但没人服务」跟这个形态是吻合的，下一席要往这里挖。
4. 进程命令行：`UnrealEditor.exe CODEO.uproject -LLMEasyShellPort=15157 -d3d11 -unattended
   -LLMEasyShellEnableInUnattended=1`。`-unattended` 本来会被 `ShouldSuppressControlChannel()`
   整段跳过控制通道（r1494 S4），本轮靠 `-LLMEasyShellEnableInUnattended=1` 才把 listener 拉起来 ——
   即「编辑器起来了但不该被驱动」这条既有红线在 push-model 路径上是被显式豁免的，判读时别忘。

**结论不变，动作要改一句**：`wait` 依然是 `--restart` 报 `hung` 时的**第一**动作（r1921/r1923 两轮的代价都是
在没有第二枚证据时动手杀进程）。但等待要有判别式：复跑本工具时若 **R2 心跳持续缺席、而 R3 的
`aux_last_frame_number_mod_1000` 一直在推进**，说明引擎早就恢复正常 tick 了、Shell 通道是自己回不来
（本轮 09:52Z 之后就是这一形）—— 那一刻的正确动作是**交人/报缺陷**，不是继续等，也不是把「PIE unusable」
写进账。R3 里那枚 `aux_last_frame_number_mod_1000` 字段就是为这一步留的（判定面不用它，只打进 JSON）。

## 相关账

* `SKILL.md` §「Editor 不在线？用 `--restart` 启动」+ §错误排查 —— 本文件的入口行
* `llmeshell-restart-misses-booting-editor-then-burns-a-link-2026-09-29.md`（r1920）—— 同为「把机器状态读成工具故障」
* `llmshell-restart-hang-v2-fix-2026-06-21.md` / `llm-shell-push-model-ready-signal-2026-06-05.md` —— readiness 探针史
* `tools/compile/lc_build_gate.py` 的「日志新鲜度只认最新一枚」注 —— 同一枚时序坑的另一副面孔
