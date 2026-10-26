---
name: orphaned-unattended-editor-holds-dll
description: "两枚孤悬 -unattended 编辑器攥着 UnrealEditor-CODEO.dll 导致整仓建不了——拒建后如何判读持有者进程是可收的尸还是活会话"
metadata:
  node_type: memory
  type: feedback
---

# 两枚孤悬的 `-unattended` 编辑器攥着 `UnrealEditor-CODEO.dll` ⇒ 整仓建不了（2026-09-29 04:20）

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


一条**工具层**缺陷，不是玩法代码缺陷。带可重放命令 —— 复述结论没用，跑一遍才有用。
同族前传：`llmeshell-port-handshake-and-stale-pch-2026-09-27.md`（端口握手 + 陈旧 PCH）、
`llmeshell-restart-misses-booting-editor-then-burns-a-link-2026-09-29.md`（识别不出启动中的编辑器）。
本轮那一条已经把「动作面」补到 llm-shell 里（Step 4 前 `EnsureTargetModuleNotHeld()`）；
**这篇补的是「持有者判读面」** —— 拒建之后，凭什么判定这枚进程是可收的尸而不是活会话。

---

## 现场

```bash
python tools/compile/lc_build_gate.py
# ... LINK : fatal error LNK1104: cannot open file 'C:\Users\<user>\CODEO\Binaries\Win64\UnrealEditor-CODEO.dll'
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe --restart
# [llm-shell] Editor not running. Skipping save/shutdown steps.
# ... 然后照常去 Link ⇒ 撞同一枚锁 (它给的两条自救都要进程答 IPC，见下)
```

三条独立复核，共同指认「这两枚是尸不是会话」：

```bash
tasklist //FI "IMAGENAME eq UnrealEditor.exe" /V          # 两枚 UnrealEditor* 在，窗口标题为空 (windowless)
wmic process where "name='UnrealEditor.exe'" get ProcessId,ParentProcessId,CommandLine
#   父 PID 9400 / 10568 都不在 tasklist 里 ⇒ 拉起它们的 harness 早已散场
netstat -ano -p TCP | grep LISTENING | grep <PID>          # 它们在听的端口 (每枚若干)
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -q -j --port <上面每一个端口> -c "info"
#   ⇒ 每一个端口都没有 JSON 应答
tail -3 Saved/Logs/CODEO.log
# [..04:2x..]LogExit: Exiting.      ← 引擎自己已经走完退出流程，只是进程没散
```

代价：一整轮的 C++ 交付没能入库。

---

## 为什么 `--restart` **结构上**救不了这一形

`--restart` 的整条链都建立在「能跟编辑器说上话」上：

1. 它先按 IPC 找编辑器（缓存端口 / 项目匹配 / `EnumWindows`）。孤悬尸端口不开或端口上的服务已随
   引擎退出而拆掉 ⇒ 扫描返回空集 ⇒ 直接打 `Editor not running. Skipping save/shutdown steps.`
2. 跳过关闭之后它**照常去 Link** ⇒ 同一枚 DLL 同一个 LNK1104。
3. 它给出的两条自救 —— `-c "quit"` 与 `--restart --port N` —— 也都是 IPC 动作。

也就是说：**它认得出「活的编辑器」和「压根没有编辑器」，认不出「有进程但没有会话」**，
而后一形的唯一特征恰恰是「问它，它不答」。判据面必须由**进程侧**（父进程存在性、进程年龄、
日志收场证据）提供，不能挂在 IPC 上。

---

## 五判据（AND 链，全中才算可回收候选）

实现见 `tools/compile/lc_build_gate.py`：`dll_holder_criteria()` + `is_reclaimable_candidate()`，
默认**只打印读数**，动手要显式 `--reclaim-dll-holders`。

| 判据 | 读数来源 | 单独用的漏洞 |
|---|---|---|
| (a) 命令行含本项目 `.uproject` 且是 `UnrealEditor*` | `Get-CimInstance Win32_Process` | 只认 exe 名会把别的项目/别的引擎版本的编辑器算进来 |
| (b) 它在听的所有端口都不应答 `info` | `netstat -ano` 归属到该 PID + 逐端口 `-c "info"` | 启动期的编辑器同样端口未开 ⇒ 单用这一条会误判活的进程 |
| (c) 父进程已不存在 | `ParentProcessId` + `tasklist` | 手工双击启动的编辑器父进程是 explorer（永远在）；harness 散场才成立 |
| (d) 存活 > 600s | `CreationDate` | 挡住「刚拉起来 30 秒」的那一格，但挡不住「编完 13 分钟才拉起、正在启动」 |
| (e) 项目日志已 `LogExit: Exiting` 或最新一枚 `Saved/Logs/CODEO*.log` 静默 > 600s | 最新日志尾巴 512KB | — |

**(e) 是「正在启动的编辑器」唯一的护身符**：启动期的形是端口还没开 ⇒ (b) 成立、
命令行带着 `.uproject` ⇒ (a) 成立、拉它的 shell/harness 外壳往往已退出 ⇒ (c) 成立，
而 (d) 在这种时间尺度上不算事（本域全量重编十几分钟，`--restart` 是**编完才拉起编辑器**，
从拉起到打开端口之间悬着的就是最长的一格）。四条全中，只剩 (e) 能把它跟
「引擎走完退出、进程没散」分开：启动中的日志在源源不断地写，既不出 `LogExit` 也不会静默十分钟。
配套口径：(e) **只看最新那一枚**日志 —— `CODEO-backup-*.log` 里的 `LogExit` 说的是上一次会话，
拿它给当前进程定罪 ⇒ 盘上留过一轮正常退出，(e) 就恒真，护身符当场失效。

---

## 收尸顺序（本机实测，别再按直觉排）

```bash
# ① 优雅关窗口 —— 对这类 windowless 进程**完全无效**
python -c "import psutil,sys; p=psutil.Process(N); p.close_main_window()"   # 或 PowerShell CloseMainWindow
# ② PowerShell 直接 Kill —— **一击即中**
powershell -NoProfile -Command "(Get-Process -Id <N>).Kill()"
# ③ taskkill /F —— **反而失败**，报一句乱码中文（大意「无法终止 … 没有此任务的实例正在运行」）
taskkill /F /PID <N>
```

`taskkill` 那句错**不是**「进程已经没了」的意思（它明明还在，DLL 还锁着）——
把 `taskkill` 当成「最后的大锤」会在这里停手，然后误判成「进程杀不掉 = 系统障碍」。
`lc_build_gate.py` 的 `terminate_dead_process()` 按 ①→②→③ 排，并打印到底是哪一步收掉的。

---

## 判读纪律（两条红线）

1. **会应答 `info` 的进程永远不可回收。** 哪怕它其余四条全像尸体：能答 IPC 就说明会话还在，
   `-c "quit"` / 让人保存都有效，杀它就是杀一次没保存的工作。所以 (b) 是**一票否决**：
   任一端口有应答 ⇒ 直接出局（selftest 的控 1 就是拿「其余四条全成立」的形状钉这一条）。
   探针本身不可用（llm-shell 缺失 / netstat 读不动）时 (b) 记**不成立**而不是「无应答」——
   否则探针一坏 (b) 恒真，等于把刀递给偶然。
2. **别靠再 `--restart` 一次来「救」它。** 这是本轮最容易走进去的坑，且它自己会制造故障：
   `--restart` 认不出活编辑器 ⇒ 判定「没在跑」⇒ 另起第二枚同项目编辑器 ⇒
   **r1452 那一形 TEDS `ACCESS_VIOLATION`**（见 09-27 篇陷阱一）。也就是说这条重试会
   **自己制造**它声称的那个故障，还会把「谁锁着 DLL」这件事彻底搅成两枚 PID。

拒建 ≠ 失败：`llm-shell` 报 `cannot link, target module is held by another process` 是闸门在正常工作。
先跑 `python tools/compile/lc_build_gate.py --diagnose-dll-holders`（只读，不构建不杀）拿到五条读数，
再决定「让活的让路」还是「确认后收尸」。

---

## 工具侧收口（本轮已落）

- `tools/compile/lc_build_gate.py`：`target_editor_dll()` / `dll_write_locked()` / `dll_holders()` /
  `_proc_info()` / `_pid_alive()` / `project_log_exit_evidence()` / `dll_holder_criteria()` /
  `is_reclaimable_candidate()` / `terminate_dead_process()` / `reclaim_dll_holders()`。
- 新 flag：`--diagnose-dll-holders`（只读判读）、`--reclaim-dll-holders`（红线授权）、
  `--selftest`（三控 + 逐条判据「抽掉必翻转」的棘轮，纯合成 dict 不碰进程）。
- 接线：离线 UBT 腿**开跑前**预检一次（锁着就把判读印出来，别用一趟全量换一条 LNK1104），
  `fail`/`unknown` 收场时再复量一次。**只回显不改判**，退出码语义一字未动。
- 顺带修：`_run_restart()` 一直没接 `port` 参数，而 `main()` 一直在传 ⇒ 在线路径必 TypeError；
  `live_editor_ports()` 拆出 `_listening_ports_for_pids()` 以便按 PID 归属端口（拿全局端口表
  去归属会张冠李戴：A 应答却给 B 记成活的）。
