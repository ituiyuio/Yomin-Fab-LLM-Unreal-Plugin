---
name: llmshell-restart-tail-buffer-2026-06-20
description: llm-shell --restart 在 Bash pipe | tail -N 下输出被缓冲的实际根因（4.5min 实测 + tail EOF flush）
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 8cad053b-e597-4d5b-b2d4-b85264ea80f9
---

# llm-shell --restart 用户报"等待超时"根因（实测复现）

**Why**:
2026-06-20 用户报告：`Bash("...llm-shell.exe" --restart 2>&1 | tail -50)` 在引擎没启动时跑，**Bash 等到 10min timeout**，但编辑器页面已经打开。怀疑 CLI 死锁。

排查后**实测复现**（引擎真没启动场景）：
- `time (llm-shell.exe --restart 2>&1 | tail -50)` 实跑 **4m32.241s** real time, exit=0
- stdout **0 字节**直到 tail EOF 才输出（buf 缓冲）
- 编辑器 19:53:23 启动（CLI 9 秒后），CPU 70.2s
- tail.exe PID 14580 一直 hold 等 stdin EOF

**实际真相 — 不是 CLI 卡住，是这 3 个机制叠加**：

### 1. **真实流程耗时 ~4.5 分钟**
```
Step 1-3: 检测 + 关闭前 editor (~5s,本场景不触发)
Step 4: UBT Build (real 30-120s, 看代码增量)
Step 5: 启动 editor (real ~3-10s, system("cmd /c start") + system() fork)
Step 6: push-model 等 editor SetEvent (real 9s, 命中)
 + TCP verify connect (real 2s)
 + info probe 1-8 次 × 1.5s (real 3-6s)
```
UBT build + editor startup = 真实 4 分钟。**`--skip-build` 实测可压到 10s**。

### 2. **Git Bash `| tail -50` 全缓冲 (Windows 关键陷阱)**
- Git Bash on Windows 调 Windows .exe 时,**stdio buffering 是 FULL (4KB) 不是 LINE**
- llm-shell.exe stdout 输出 554 bytes JSON → buffer 不满 → 不 flush
- `tail -50` 收 stdin 但 stdio 不是 tty → 也 full-buffered
- **只有 stdin EOF 才一次性 flush 全部 buffer**
- 表现：CLI exit 后 30 秒里 Bash 还"卡住",其实 tail 在 print 50 行

### 3. **Bash subshell `()` + pipe 创建** 雪上加霜
- `time ( ... | tail -50 )` subshell 套娃
- subshell fork 后 pipe fd 复制,可能 1-2 秒延迟 exit 通知

**How to apply** (给 LLM 用的修复):

**用户用命令加旗标**:
```bash
# 推荐: 跳过 UBT (如果 build artifact 还在) + 显式 unbuffered
"D:/UnrealEngine/CODEO/.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe" -q --restart --skip-build 2>&1 | tail -50

# 或强制 stdout line-buffered (需要 main.cpp 加 setvbuf)
# 或用 stdbuf -oL 包装 (但 Windows Git Bash 不支持)
```

**开发侧修复 (未实施)**:
- main.cpp 第 3094 行 ExecuteRestart 入口加 `setvbuf(stdout, NULL, _IOLBF, 0)` 让 stdout line-buffered
- 或在 EmitRestartResult 后 `fflush(stdout)` + `_commit(1)` 强制 flush 到 OS

**实测快速命令 (10s 内完成)**:
```bash
"D:/UnrealEngine/CODEO/.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe" -q --restart --skip-build
```

**Verify**:
- 实测 4m32.241s real, exit=0, tail flush 时 output 完整 50 行
- 引擎 19:53:23 启动, CLI 在 ~9s 后收 push-model 事件
- `tail` 进程 PID 14580 hold 整个 4m32s, kill tail 后 bash 立即返回

**相关 commit**:
- d7f7b33 (Jun 14) `--skip-build` flag: 实测可压到 10s
- d2981b0 (Jun 5) push-model Win32 event
- d750317 (Jun 5) W26.4 ResetEvent + 端口 verify

**为什么前几次测试 10-40s 完成**:
前几次 editor **已经在跑**,所以 ExecuteRestart 走 Step 1-3 close editor 路径(快速),省去 UBT build。本次 engine 真没启动 → 走完整 Build → 4.5 分钟。

**LLM prompt 模板**:
> LLM: 跑 `llm-shell --restart` 之前,先问用户:
> 1. UBT build 是否需要?(默认 yes,慢) → 加 `--skip-build` 如果 build artifact 还 current
> 2. 用 `2>&1 | tail -N` 会缓冲 → 加 `-q` 或不用 pipe
