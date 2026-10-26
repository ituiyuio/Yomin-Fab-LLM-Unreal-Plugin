---
name: llmeshell-restart-unattended-kills-own-channel
description: "--restart 在 VMware 分支给交互式编辑器追加 -unattended，ShouldSuppressControlChannel() 即不绑控制端口 ⇒ restart 交付一个自己连不上的编辑器"
metadata:
  node_type: memory
  type: feedback
---

# llm-shell `--restart` 在 VMware 分支上启动了一个它自己连不上的编辑器 (r1920 2026-09-28)

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


## 症状（本轮差点因此退化成「只写文档的一轮」）

`llm-shell.exe --restart` 走完 build → 启动编辑器 → 报成功。之后**任何**命令都回：

```
Failed to connect to Unreal Editor at 127.0.0.1:15157
recommendedAction: "run_llm_shell_restart"
```

而 `info` 的恢复建议正是 `llm-shell --restart` ⇒ 自我循环。本轮实测到的现场：

- `tasklist` 里 `UnrealEditor.exe` 活着、常驻内存 4.0-4.8 GB，`Saved/Logs/CODEO.log` 一路写到
  `LogSourceControl: Uncontrolled asset discovery started`（= 编辑器确实起来了）；
- `netstat -ano` 只有 `0.0.0.0:15201 LISTENING`（LLMEasyShell**Lite** 的端口），
  15157 **没有任何监听者**；
- 客户端对着 15201 发 `info` 只会拿到 Lite 的命令注册表，`play` / `python editor console` /
  截图这些本轮要用的能力在 Lite 面上都不存在。

⇒ 表象是「这台机器 PIE 不可用」。**实际是「引擎起来了，但它的控制通道被我们自己传的旗标关了」。**
这类误判在仓里有代价：`docs/survivor/wiki/PIE-CARRY-QUEUE.md` 里 P-3/P-6/P-7 好几条 DEFER 的
理由写着「本机看不到任何一帧 / 无活体编辑器」，而其中一部分真相只是连不上端口。

## 根因

`.claude/skills/llm-easy-shell/llm-shell/main.cpp:4632`（VMware SVGA 3D 分支）给交互式编辑器
追加的是：

```cpp
extraRhiFlags = L" -d3d11 -unattended";
```

而 `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp:283-297`
`ShouldSuppressControlChannel()` 里，`FApp::IsUnattended()` 为真 ⇒ **完整控制通道不绑端口，
连共享端口文件都不读写**（那是 r1494 S4 为了「commandlet 不许抢真编辑器的端口」写的，判据本身没错）。
`-unattended` 的原始目的只是压掉模态对话框，不是为了关通道。

两处各自合理，合起来 = `--restart` 在本机永远交付一个连不上的编辑器。

## 修法（已落，且是可验的）

沿用插件自己写的逃生门（`LLMEasyShellSubsystem.cpp:279-280` 明文的
`-LLMEasyShellEnableInUnattended=1`），在**同一条分支**上补这个旗标：

```cpp
extraRhiFlags = L" -d3d11 -unattended -LLMEasyShellEnableInUnattended=1";
```

改后实测（本机，同一台 VMware SVGA 3D）：

| 读数 | 改前 | 改后 |
|---|---|---|
| `netstat -ano \| grep 15157` | 无监听 | `127.0.0.1:15157 LISTENING <编辑器 PID>` |
| `llm-shell -q -j -c "info"` | `Failed to connect` | 完整 JSON（`level=Lvl_SurvivorTest`, `actorCount=84`, `editorState=Idle`） |
| `play` | 发不出去 | `{"success": true, "state": "Playing"}` |
| `python editor console survivor.SpawnEnemy 4 10` | — | 日志 `[survivor.SpawnEnemy] spawned 10/10` |

判据：`grep -c LLMEasyShellEnableInUnattended Saved/Logs/CODEO.log` 与
`netstat -ano | grep 15157`，两枚都非零才算这条修完。

**刻意没动的地方**：`main.cpp:4667` 的 `-nullrhi -unattended` 分支（Microsoft Basic / Hyper-V）保持
r1252 原样。理由不是漏了，是本机不走这条分支、无法在同一台机器上证伪，而那条分支自己的注释写明
「unverified hardware, behavior left exactly as shipped」。换机器跑到那条分支的席位，请按同一判据补。

## 同一条 restart 路径上另外两枚缺陷（一并修，同一台机器实测）

**① build 超时被说成「编译失败」。** `main.cpp` 的 build 看门狗到点时只做
`TerminateProcess(pi.hProcess)` —— 杀的是那层 PowerShell，**UBT(dotnet) 与 cl.exe 作为孤儿继续编**。
后果两条，本轮都撞上了：
- 调用方收到 `Build failed with code 1`，而同一份 UBT 日志里 **0 条编译错误**（只有 C4996
  deprecation warning）⇒ 本席差点去找一处不存在的编译错。这是 r1005 那条注释（「健康的编译被误杀成
  Build failed with code 1」）的**复发**，因为当年的处置是「把 25 min 加大」，没解决「超时≠失败」的口径。
- 下一个 `Build.bat` 会卡在一把**名义持有者已死**的互斥上，表现为
  `Build.bat is already running, waiting for existing script to terminate...` 长挂。

修法（已落）：超时分支改走仓内既成的 `KillProcessTreeByPid()`（`main.cpp:3294` 的
`taskkill /T /F` 树杀），并用 `buildTimedOut` 把 verdict 分成两句话 —— 超时那句明写
`NOT a compile failure` + 给出「直接重跑 --restart，增量会从断点续上」的下一步。

**② 两枚 cap 各写各的，全局 cap 可以小于 build cap。** 旧布局是 build cap 25 min / 全局 cap 35 min
（硬编码常量），改大任何一枚都可能让另一枚先砍。本轮改成派生 + 可 env 覆盖：

```
LLMSHELL_BUILD_TIMEOUT_MIN      默认 60
LLMSHELL_RESTART_HARD_CAP_MIN   默认 = build cap + 15（即 75）
```

判据（已复算）：`python -c "d=open('.../llm-shell.exe','rb').read();print(d.count(b'LLMSHELL_BUILD_TIMEOUT_MIN'))"` ⇒ 2；
宽字符串那枚 `LLMEasyShellEnableInUnattended` 是 UTF-16，`d.count('…'.encode('utf-16-le'))` ⇒ 1
（**注意**：二进制 grep 对 ASCII 命中 0 不等于没编进去，宽字符要按 UTF-16 数 —— 本席第一次就数错了，
差点得出「编译没生效」的假结论）。

**③ 本席自己的取证管道 bug（写进来免得下次再犯）**：观察并发拒绝时看到
`{"success":false, "exitCode":2}` 而外层 shell 退出码是 0，本席差点把它记成「契约不回非零码」。
回读 `main.cpp:4084-4094` 那条分支确实 `return 2` —— **0 是 `llm-shell … | tail -30` 造成的**：
管道的退出码属于 `tail`。⇒ 凡拿退出码当判据的命令，不许挂管道。

## 判据（下一位可复算）

```bash
netstat -ano | grep 15157                      # 改后：LISTENING <编辑器 PID>；改前：无行
python -c "import glob;print(open(sorted(glob.glob('Saved/Logs/CODEO.log'))[-1],'rb').read().decode('utf-8','replace').count('EnableInUnattended'))"
tasklist | grep -ciE "dotnet.exe|cl.exe"       # 超时后应为 0（树杀生效）；改前会留孤儿
```

## 状态

- 分支：本轮实测走的是 VMware SVGA 3D ⇒ `-d3d11` 那条（`main.cpp:4632`）。
- `-nullrhi` 那条分支（Microsoft Basic / Hyper-V）**未改**：本机不走它、无法在这台机器上证伪，
  且其注释自陈「unverified hardware, behavior left exactly as shipped」。换到那条分支的席位请同判据补。
- 端到端 `--restart`（含超时分支的树杀）在本轮**未跑到**：本轮验证的是「带不带这枚旗标，通道在不在」
  与「编译后的二进制里三串常量都在」。「超时后无孤儿」这条要到下一次真超时才能确证，别当成已确证。

