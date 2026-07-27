---
name: llm-shell-w27-tick-resetevent-fix
description: "W27 修复 llm-shell --restart 在 editor 已运行时 + llm-shell CreateEvent+ResetEvent 之后没人再 SetEvent 的 60s+60s 死等: editor 的 FLLMEasyShellTickable 在 Tick() 里每 ~1s 重新 SetEvent ReadyEventHandle"
metadata: 
 node_type: memory
 type: project
 originSessionId: c33e0873-f44c-4020-8c92-7adb7e888041
---

# W27 llm-shell --restart push-model race 修复 (2026-06-06)

## 触发场景
用户报告"restart命令还是收不到引擎已经就绪的消息"。editor PID 61096 已运行 7+ 分钟,editor 在 00:26:19 SetEvent 过一次后没人再 SetEvent,事件保持 signaled。llm-shell --restart 跑到 Step 6 时 CreateEventA 拿到旧 handle signaled → ResetEvent 清掉 → WaitForSingleObject 永久阻塞(60s 超时) → 落到 port-poll fallback 又 60s。总共 120s 才看到 complete。

## 根因
W26.4 加的 ResetEvent 初衷是清 force-kill 旧 editor 后的 stale signaled state(假信号问题),**但把真信号也清了**。editor SetEvent 是 one-shot(只在 Initialize() 末尾),不会再来第二次。

## 修复
`FLLMEasyShellTickable::Tick(DeltaTime)` 拿到 `HANDLE* ReadyEventHandlePtr`(指向 subsystem 的 HANDLE 字段)。每 ~1s 检查一次 elapsed,到了就 `::SetEvent(*ReadyEventHandlePtr)`。SetEvent on already-signaled manual-reset event 是 kernel no-op(状态保持 signaled),成本可忽略。

任何后来的 llm-shell 等待者(比如刚 ResetEvent 过的)最多等一个 tick 间隔(~1s)就能拿到信号。

## 改动文件
| 文件 | 改动 |
|------|------|
| `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp` | `FLLMEasyShellTickable` 加 `HANDLE* ReadyEventHandlePtr` + `TimeSinceLastSetEvent` 成员;`Tick()` 每 1s SetEvent;两处 `MakeShareable(new FLLMEasyShellTickable(...))` 传 `&ReadyEventHandle` |
| `Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellSubsystem.h` | H 字段注释加 W27 说明 |
| `Plugins/LLMEasyShell/LLMEasyShell.aiac` | ready-signal module description 加 W27 描述 + tcp-server link |

## 验证
- 单独构建 plugin dll:`Build.bat CODEOEditor Win64 Development -Module=LLMEasyShell` (32.9s, 全工程 build 因 LLMDynamicUI pre-existing link 失败但与本 fix 无关)
- 启动 editor (PID 63984),`LogLLMEasyShell: Ready signal SET on 'Local\LLMEasyShell_Ready_15151'`
- PowerShell 模拟 llm-shell 行为: CreateEventA → ResetEvent → WaitForSingleObject(5000ms) → **86ms 内收到信号** ✓

## Why
- 用户原话:"restart命令还是收不到引擎已经就绪的消息"
- 误诊:W26.4 之前以为纯 port-poll 慢,实际是 W26.4 引入的 race。editor SetEvent 是一次性,无法应对"已有 editor 跑着 + llm-shell 后来 CreateEvent+ResetEvent" 场景
- 6 次 restart 修复(W26 / W26.1 / W26.2 / W26.3 / W26.3.1 / W26.3.2 / W26.4 / push-model / W27)说明 push-model 跨进程 handshake 复杂度高

## How to apply
- 任何用 Win32 Named Event 做 ready signal 的代码,创建端必须 **周期性 re-set** 而非 one-shot。one-shot 在跨进程场景下脆弱(对方可能 ResetEvent 清掉)
- 设计 ready signal 时优先考虑:周期性 push(event) > request/reply 文件 > pull(port-poll)
- Deinitialize 顺序要保证: 先 `TickableObject.Reset()`(让 tick 停),再 `CloseHandle(ReadyEventHandle)`(关闭 handle)。否则 tick 会 dereference 已 close 的 handle

[[llm-shell-push-model-ready-signal-2026-06-05]] [[llm-shell-w26-4-stale-event-reset]] [[llmshell-restart-hang-fix-2026-06-04]]
