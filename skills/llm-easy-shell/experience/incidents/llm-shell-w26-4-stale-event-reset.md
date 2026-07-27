---
name: llm-shell-w26-4-stale-event-reset
description: W26.4 修复 llm-shell --restart 在旧 editor force-kill 后的 stale signaled event 假唤醒：CreateEventA 后 ResetEvent + WaitForSingleObject 返回后 500ms 端口 connect 验证
metadata: 
 node_type: memory
 type: project
 originSessionId: 260568b3-079a-4150-8bad-55bd0686c580
---

# W26.4 stale Win32 Event 修复 (2026-06-05)

## 触发场景

`llm-shell --restart` 之前一次跑得不对，旧 editor 被 force-kill（`taskkill /F` 或 crash 跳过 Deinitialize），Win32 named event 状态被遗留在 **signaled** —— 旧 editor 调过 SetEvent 但 CloseHandle 没人调，kernel 对象活着，状态保留。

下一次 --restart 时：
```
T0 旧 editor: SetEvent → signaled
T1 旧 editor: force-kill（Deinitialize 没跑） → handle 泄漏，kernel 对象活着
T2 llm-shell: CreateEventA(name, initial=FALSE)
 ⚠️ 对象已存在 → bInitialState 被忽略，状态仍 = signaled
T3 llm-shell: WaitForSingleObject → 立即返回 WAIT_OBJECT_0（假信号）
T4 llm-shell: portUp=true（"assumed up"）
T5 llm-shell: info probe 8×1.5s = 12s 连不上新 editor
T6 llm-shell: emit success + 空 infoJson
```

新 editor 实际还在 Initialize() 跑，但 llm-shell 已经"成功"走人。LLM 看到的 restart 状态跟真实状态对不上。

## 修复（双端 ResetEvent + 端口验证）

### `main.cpp`（**关键**，2 处）

1. **CreateEventA 之后立刻 ResetEvent**（line ~2820）：
 ```cpp
 readyEvent = CreateEventA(nullptr, TRUE, FALSE, name);
 if (readyEvent) {
 ResetEvent(readyEvent); // W26.4: 清 stale signaled state
 // ...
 }
 ```

2. **WaitForSingleObject 返回后做端口 connect 验证**（line ~2870）：
 ```cpp
 if (waitResult == WAIT_OBJECT_0) {
 SOCKET verifySock = ConnectWithTimeout(host, port, 500);
 if (verifySock != INVALID_SOCKET) {
 closesocket(verifySock);
 portUp = true;
 } else {
 // push signal fired 但 port 还没 listening → 落到 port-poll fallback
 }
 }
 ```
 解决另一类 race：editor SetEvent 时 listen socket 还没 accept 第一次 tick，connect 会失败。

### `LLMEasyShellSubsystem.cpp`（防御性 belt-and-suspenders）

CreateEventW 之后、SetEvent 之前 ResetEvent：
```cpp
if (ReadyEvent) {
 ReadyEventHandle = ReadyEvent;
 ResetEvent(ReadyEvent); // W26.4: 同 main.cpp 理由
 SetEvent(ReadyEvent);
}
```

正常 close 路径（Deinitialize 跑了 CloseHandle → kernel 对象释放 → 下次 CreateEvent 拿新对象）下，editor 侧 ResetEvent 是不必要的。但 force-kill 场景下它补一刀：即使 llm-shell 没 ResetEvent，editor 也能把 stale 状态清掉。

## 验证

`llm-shell --restart` 跑通，关键日志：
```
[llm-shell] Created + reset ready event 'Local\LLMEasyShell_Ready_15151' — waiting for editor push signal (60s cap).
[llm-shell] Ready signal received from editor (push-model).
[llm-shell] Port 15151 verified accepting connections. Push-model confirmed.
[llm-shell] Editor ready (push-model: event signaled, port 15151 up).
[llm-shell] Editor state captured (info probe succeeded).
[llm-shell] Restart complete!
```

最终 JSON: `{"success":true,"stage":"complete","output":{...full editor state...}}`

## Why

用户原话："现在的问题依然是引擎就绪之后挂起的restart没有知道引擎已经启动了"

误诊一轮：先以为是 close 阻塞 → 实际 close 没问题。改去查 start 路径，看到 `CreateEventA` 没用 ResetEvent，推断 stale event 假信号。

## How to apply

- 任何用 Win32 Named Event 做跨进程 ready signal 的代码，**CreateEvent 之后必须 ResetEvent** —— bInitialState 对已存在的命名对象是被忽略的（per Win32 docs）
- 拿到 ready signal 后**别假设 "signal = service ready"** —— 加一个 500ms 级别的 connect/readiness probe
- livecoding patch **只更新 in-memory**，on-disk dll 不动。下次 editor 重启会回退到旧 dll。所以 livecoding 后跑 --restart 验证修复时，要意识到 editor 侧 ResetEvent 在新 editor 中不生效（仍靠 llm-shell 侧 ResetEvent + 正常 close 释放 kernel 对象来保证）

[[llm-shell-push-model-ready-signal-2026-06-05]] [[llmshell-restart-hang-fix-2026-06-04]]
