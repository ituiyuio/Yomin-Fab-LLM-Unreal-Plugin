---
name: llmeshell-port-handshake-and-stale-pch
description: "两枚烧掉整轮时间的 llm-shell/UBT 陷阱：端口握手误判与陈旧 PCH（r1912 实测）"
metadata:
  node_type: memory
  type: feedback
---

# 两枚把整轮时间烧光的 llm-shell / UBT 陷阱（r1912 实测，2026-09-27）

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


两条都是**工具层**缺陷，不是玩法代码缺陷。每条都带可重放命令 —— 复述结论没用，跑一遍才有用。

---

## 陷阱一：`--restart` 把「已经起来的编辑器」报成失败

**现场**（2026-09-26 22:0x，本机 `C:` 只剩 7.0GB 时也一样能复现，与磁盘无关）：

```bash
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe --restart
# [llm-shell] Allocated port 15157 for this instance
# [llm-shell-heartbeat] elapsed=170s readyEvent=set pushSignal=0 lastInfoProbe=empty allocatedPort=15157 attempt=2
# [llm-shell] --restart failed after 2 attempt(s), stage=start: Editor did not respond to 'info' within 180s
# {"success":false,"stage":"start","exitCode":1}
```

而同一时刻编辑器**好好的**，只是插件绑到了**另一个端口**：

```bash
tail -3 Saved/Logs/CODEO.log
# [..15.42.43..]LogLLMEasyShellLite: LLMEasyShell: Tick #292573 (port 15201, running YES)
./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe -q -j --port 15201 -c "info"
# {"project":"CODEO","port":15201,"editorState":"Idle","hint":"editor is idle"}
```

**判据口径**：`--restart` 的 `success:false` **不能**当作「编辑器没起来」。三条独立复核，任一成立即算起来：
1. `Saved/Logs/CODEO.log` 尾部有没有 `Tick #N (port <P>, running YES)` —— 那是插件自己报的端口；
2. 拿那个 `<P>` 直接 `llm-shell --port <P> -c "info"`；
3. `tasklist //FI "IMAGENAME eq UnrealEditor.exe"` 看进程在不在（心跳行的 `lastInfoProbe=empty` 只说明**CLI 轮错了端口**，不说明引擎死了）。

**为什么危险**：报假失败之后，agent 的既定动作是「再 `--restart` 一次」⇒ 同项目第二个编辑器并发 ⇒ **r1452 那一形 TEDS `ACCESS_VIOLATION`**（本席 attempt 1 的现场：`Editor died 22s after launch … module=UnrealEditor_TedsCore`）。也就是说这条假失败会**自己制造**它声称的那个故障。

**工具侧收口**：`tools/compile/lc_build_gate.py` 本轮已加 `project_editor_pids()` / `live_editor_ports()` / `probe_editor_any_port()`（扫 `netstat -ano` 找本进程树的 LISTENING 端口并逐个 `info` 复核），把「离线」与「活着但端口不匹配」拆成两种结论，并把发现的端口带给 `--restart --port N`。根因（客户端按缓存端口轮、插件自选端口）仍在 `llm-shell` 的 readiness 探针里，未修。

---

## 陷阱二：按 mtime 判「孤立的 obj 树」并删掉 = 全项目重编

**现场**：`Intermediate/Build/Win64/x64/` 下并存两棵树 ——

| 树 | 文件数 | 最新 mtime | 本席当时的判断 | 盘上真相 |
|---|---|---|---|---|
| `UnrealEditor/Development/CODEO/` | 3589（940 枚 ≥09-20） | 09-26 21:26 | 现役 | 现役 ✔ |
| `CODEOEditor/Development/` | 56，其中单枚 `SharedPCH…Cpp20.h.pch` **2437MB** | **09-10** | 「09-10 起废弃的孤立树，可回收 2.4GB」 | **现役 blob 共用的 SharedPCH** ✘ |

删掉之后，正在跑的 UBT 于 22:44 **原地重生成那枚 2.56GB PCH**，并重编 **全部 96 枚 `Module.CODEO.*.cpp.obj` unity blob**（约 2.5 分钟/枚 ⇒ 单这一件事 ≈ 3–4 小时机器时间，且整期间 `-WaitMutex` 把所有别的构建排在后面）。

**决定性证据**（一行就够，别猜）：

```bash
grep -o '/Yu"[^"]*"' Intermediate/Build/Win64/x64/UnrealEditor/Development/CODEO/Module.CODEO.13.cpp.obj.rsp
# /Yu"C:/Users/<user>/CODEO/Intermediate/Build/Win64/x64/CODEOEditor/Development/UnrealEd/SharedPCH.UnrealEd.Project.ValApi.ValExpApi.Cpp20.h"
```

`UnrealEditor` 树里的 blob 用 `/Yu` 指向 **`CODEOEditor` 树的 PCH**。所以「另一条目标名的树」不等于「死的树」：**SharedPCH 只在引擎头变更或被删时重生，平时无限期不动 ⇒ 陈旧 mtime 是它的常态，不是废弃的信号。**

**正确判据** = 引用数，不是 mtime：

```bash
# 现役 blob 有没有引用这棵树？引用数 > 0 就不是孤物
grep -l "x64/CODEOEditor/" Intermediate/Build/Win64/x64/UnrealEditor/Development/CODEO/*.rsp | wc -l
```

`tools/compile/lc_build_gate.py` 的可回收候选扫描已按这条实现（引用数非零就不提名，并打印「mtime 陈旧不等于死物」的注），本席实测该函数 26.7s 跑完、只提名真正的可再生小缓存（`Temp/lc_build_gate_dll_snap` + 老 `Saved/Crashes`，合计 0.05GB）。

---

## 顺带一条：磁盘门不是「建议」

`tools/compile/lc_build_gate.py:68` `MIN_FREE_GB = 8`，低于它就 `GATE UNKNOWN`（rc=2）且**什么都不编**。前一轮（r1911）4 枚测试文件 + 3 枚改动文件因此停在 index 里没入库，写的是「本席不绕门」—— 那个 rc=2 的真身就是 `df /c = 7.0G`。
**先量盘再排产**：`df -h /c` 一眼 30 秒，比撞一次 rc=2 后回头考古便宜得多。本轮解法 = `npm cache clean --force`（实测 944MB→2MB）+ 清 `Temp` 里工具自产的快照残留 + 删 `DerivedDataCache`（612MB，会重编着色器，代价如实）；**不要**从 `Intermediate/` 里找肉（见陷阱二）。
