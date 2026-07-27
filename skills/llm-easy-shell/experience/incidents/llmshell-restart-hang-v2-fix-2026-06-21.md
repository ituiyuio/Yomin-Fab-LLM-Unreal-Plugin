---
name: llmshell-restart-hang-v2-fix-2026-06-21
description: llm-shell --restart 在 piped context 卡死永不退出 (2026-06-21):4 层防御修复 — CreateProcessW 替换 system / 8min buildWatcher / 10min 全局 hard cap / 10s heartbeat
metadata: 
 node_type: memory
 type: feedback
 originSessionId: bba897c9-241d-4ec4-bf92-700306e7ef98
---

# llm-shell --restart 在 piped context (2>&1 | tail -3) 卡死永不退出

**Why**:
用户 2026-06-21 报告:`llm-shell --restart 2>&1 | tail -3` 在 editor 已启动就绪时,llm-shell.exe 进程永不退出.重启流程的 shutdown/build/start 都已完成,engine.exe 启动了,但 llm-shell 进程卡住.

排查发现真根因不是 Step 6 的 5min cap,而是 Step 5 的 `system(startCmd)` 在 piped context 下 hang:cmd /c start 启动 engine.exe 后,cmd.exe 在 piped stdout/stderr 环境下等子进程 detach 才退出,system() 永久阻塞.

**修复 (4 层防御)**:

1. **替换 system(startCmd) → CreateProcessW** (main.cpp Step 5):`bInheritHandles=FALSE` + 立即 CloseHandle(pi.hProcess/pi.hThread),不走 cmd.exe 中介,完全消除 piped context hang.保留 system() 作为 CreateProcessW 失败时的 fallback.

2. **buildWatcher 线程** (Step 4 build block):用 CreateProcessW 启动 PowerShell+UBT (bInheritHandles=TRUE 必须,因为需要继承 stdout/stderr pipes 重定向到 tempPath).WaitForSingleObject(8min hard cap).超时主动 TerminateProcess.主线程每 30s emit stderr heartbeat.

3. **全局 10min hard cap** (`checkHardCap` lambda):ExecuteRestart 开头设 wall-clock timer,在 buildWatcher 循环 + Step 6 while 循环调.即使别的路径 hang 也保证 process 退出 + emit failure JSON.

4. **Step 6 heartbeat** (每 10s stderr):格式 `[llm-shell-heartbeat] elapsed=Xs readyEvent=set|null pushSignal=0|1 lastInfoProbe=empty|received allocatedPort=N`.让 LLM/用户在 restart running 时看到 liveness,未来 hang 能精确定位子路径.

**How to apply**:
- 改 main.cpp 时保持所有 4 层防御
- 改 build timeout 时联动改全局 hard cap(留 buffer)
- 新增 restart 相关代码必须经过 checkHardCap()

**Verify** (2026-06-21 端到端):
- Scenario 3 (piped `2>&1 | tail -3`): **51 秒内 exit**,emit `{"success":true,"stage":"complete"}` (修复前: 永不退出)
- Scenario 2 (editor 已就绪 + restart): 54 秒内 exit
- Heartbeat 在 10s 时正确 emit
- 两次都用 push-model fast-path (~12s 内 editor ready)

**相关 commit 模式**:
5 个 commit:
- `c87aae9 feat(llm-shell): add ToWide() helper for CreateProcessW paths`
- `200aa08 fix(llm-shell): replace system(startCmd) with CreateProcessW to fix piped-context hang`
- `220cbe0 fix(llm-shell): wrap UBT build in watcher thread with 8min hard cap`
- `a50a3b8 fix(llm-shell): add 10-minute global hard cap for --restart workflow`
- `f3f5d2a feat(llm-shell): add 10s heartbeat to Step 6 wait-for-ready for diagnostic visibility`
- `178f0b2 verify(llm-shell): restart hang v2 fix end-to-end manual verification`

参考 [[llmshell-restart-hang-fix-2026-06-04]] 上一轮 (崩溃场景) 修复.

**Spec**: docs/superpowers/specs/2026-06-21-llmshell-restart-hang-v2-design.md
**Plan**: docs/superpowers/plans/2026-06-21-llmshell-restart-hang-v2.md