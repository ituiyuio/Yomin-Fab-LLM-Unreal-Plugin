---
name: llm-shell-push-model-ready-signal-2026-06-05
description: "LLMEasyShell --restart push-model 架构 (2026-06-05)：Win32 Named Event 替代 port-poll 轮询,SetEvent 在 Initialize() 末尾触发,WaitForSingleObject kernel-level 阻塞,port 后缀命名 + 旧版 fallback"
metadata: 
 node_type: memory
 type: project
 originSessionId: 17e69197-8184-4911-b5f0-b859b5470b1e
---

# llm-shell --restart push-model ready signal (2026-06-05)

## 解决的问题
W26.3.2 修复后 llm-shell --restart 仍慢 (60-90s)。根因：**pull-model 架构** — llm-shell 被动轮询 TCP port + info probe，editor 侧没有"我 ready 了"的推送机制，导致 LLM 误判 hang。

## 新机制 (push-model)

**核心 idea**：editor Initialize() 完成（TCP bind + Tickable 注册 + .current_port 写入）那一刻**主动** SetEvent 通知 llm-shell。llm-shell 阻塞等 SetEvent 而不是轮询。

### 跨进程契约

```
Event name: Local\LLMEasyShell_Ready_<port>
llm-shell: CreateEventA(name, manualReset=TRUE, bInitialState=FALSE) // 先创建
editor: CreateEventW(name, ..., bInitialState=TRUE) // 参数被忽略
 SetEvent(ReadyEventHandle) // 显式触发
llm-shell: WaitForSingleObject(handle, 60s) // kernel-level 阻塞
```

### 命名约定: `<port>` 而不是 `<pid>`

llm-shell 自己分配 port（`AllocatePortForInstance`），editor PID 是 spawn 之后才有。
用 port 后缀 llm-shell 立即知道 event name，editor 从 `.current_port` 读出 port 后构造同名 event。

### Win32 Named Event 跨进程语义 (关键)

- 同一 name → 同一 kernel object
- 第一次 `CreateEvent` 决定 initial state
- 后续 `CreateEvent` **忽略** `bManualReset`/`bInitialState` 参数，只返回 handle
- **所以即使 editor 传 bInitialState=TRUE 也没用** — 状态由 llm-shell 第一次的 FALSE 决定
- editor `SetEvent` 后**所有** handle 都看到 signaled

## 改动文件

| 文件 | 改动 |
|------|------|
| `Plugins/LLMEasyShell/Public/LLMEasyShellSubsystem.h` | 加 `HANDLE ReadyEventHandle = nullptr` 字段 (PLATFORM_WINDOWS); 加 windows.h include (用 `Windows/AllowWindowsPlatformTypes.h` 包装) |
| `Plugins/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp` | `Initialize()` 末尾 (写 .current_port 之后) CreateEventW + SetEvent + 写 `.ready_event` debug 文件; `Deinitialize()` 末尾 CloseHandle |
| `.claude/skills/llm-easy-shell/llm-shell/main.cpp` | `ExecuteRestart` Step 5 后 CreateEventA 提前到 system() 之前; Step 6 优先 WaitForSingleObject(60s),失败 (CreateEvent 失败 / WAIT_TIMEOUT) fallback 到 60s port-poll; 5 个 return 路径都加 CloseHandle 兜底 |
| `Plugins/LLMEasyShell/LLMEasyShell.aiac` | 加 `ready-signal` module 描述 push-model 架构 |

## 容错 (双向兼容)

- **新 editor + 新 llm-shell**：走 push-model，editor SetEvent 后 ~0ms emit complete
- **旧 editor + 新 llm-shell**：editor 不 SetEvent，WaitForSingleObject 60s 后 timeout, fallback port-poll 60s → 总 120s
- **新 editor + 旧 llm-shell**：旧 llm-shell 走 port-poll,editor SetEvent 是无害的额外信号
- **CreateEventA 失败** (rare, e.g. 残留 handle)：直接跳到 port-poll fallback,不等 60s

## Why
用户原话："llmshell的restart命令基本每次都会超时, 引擎明明已经启动了但是不会给shell返回信息"
+ 用户提示："shell插件会正常返回信息吗, 我记得是worldsubsystem就绪之后就会通过TCP通知"

确认是 pull-model 架构缺陷，不是具体 bug。W26.3.2 的 5 个修复都是症状层（stdout 污染、嵌套 JSON 失败、port-poll 过长），没碰架构层。

## How to apply
- 改 LLMEasyShellSubsystem 的 ready signal 触发点:必须确保触发时 TCP server 已 bind, TickableObject 已注册, port 文件已写入 — 任何后续异步初始化都不应改这条契约
- 改 llm-shell 的 Step 6 等待逻辑:必须保留 fallback 路径(port-poll + crash detect)以兼容旧 editor
- Win32 named event 是按 port 命名,不是 PID:多实例下 port 唯一,event name 也唯一
- `.ready_event` 文件是 debug 工具,不是 IPC 通道 — llm-shell 不读它
- aiac 文档已记录 `ready-signal` module,改这块代码前看 aiac
- 编译:LLMEasyShell 是 editor plugin,需要 editor target 编译;llm-shell 是独立 .exe,用 `compile.ps1`

[[llmshell-restart-hang-fix-2026-06-04]] [[llm-shell-w26-restart-fixes]] [[llm-shell-w26-3-2-restart-timeout]]
