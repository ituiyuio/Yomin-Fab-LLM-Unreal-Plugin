---
name: llmshell-multiengine-debug
description: LLMEasyShell 多引擎链接调试发现
type: reference
originSessionId: fb34f12f-8ede-49c7-ace3-8697f1490ce2
---
# LLMEasyShell 多引擎链接调试发现

## 核心问题

**`.current_port` 文件被写入错误值 `1` 而非正确端口**

### 根因分析

引擎启动时：
1. 插件尝试读取 `.current_port`
2. 如果读取失败或值无效，使用默认值 `15151`
3. 端口被占用时自动扫描下一个可用端口
4. **但在写入 `.current_port` 时出错** → 写入了 `1`

### 端口分配机制

```
LLMEasyShellSubsystem::Initialize()
├── 读取 .current_port → 失败时默认 15151
├── TcpServer->Start(ListenPort)
│ └── 失败时扫描 BasePort+i 直到成功
└── 写入当前端口到 .current_port
 └── 如果写入失败，文件保持为空或旧值
```

## 调试方法

### 1. 检查端口监听状态
```powershell
Get-NetTCPConnection -LocalPort 15151,15152 -ErrorAction SilentlyContinue
```

### 2. 检查引擎实例对应的项目和 PID
```powershell
Get-CimInstance Win32_Process -Filter 'ProcessId=<PID>'
```

### 3. 测试连接
```bash
llm-shell.exe -h 127.0.0.1 -p <PORT> -c "info"
```

## 已知问题

**15152 端口 (PID 48732) 连接超时**

- 现象：TCP 连接成功建立，但命令执行超时 (70 秒)
- 可能原因：
 1. `ProcessCommand` 中 `Subsystem` 指针为 null
 2. `Tick()` 函数未被正确调用 → 命令从未被处理
 3. 命令处理死锁

### `Tickable` 注册关键点

```cpp
// 必须同时满足：
// 1. FLLMEasyShellTickable::IsTickable() 返回 true
// 2. FLLMEasyShellTickable::IsTickableInEditor() 返回 true
// 3. ULLMEasyShellSubsystem 被正确初始化
// 4. TcpServer->IsRunning() 在 Tick 期间保持 true
```

## 2026-04-26 补充发现

### 问题 1：引擎路径检测错误
CODEO 项目的 `EngineAssociation` 是 `5.7`，应该使用 `C:\Program Files\Epic Games\UE_5.7`。
但 `llm-shell.exe` 的 `GetEnginePathFromRegistry` 找不到注册表条目，回退到 `D:\UnrealEngine\UnrealEngine-Angelscript`。

**影响**：`--restart` 命令会尝试用错误的引擎路径构建项目。

### 问题 2：15152 端口无响应
- 端口监听成功（PID 48732）
- TCP 连接建立成功
- 但命令超时（70 秒）无响应

**可能根因**：
1. `Subsystem` 指针为 null（`ProcessCommand` 静默失败）
2. `Tickable` 未被正确注册或未被调用
3. 插件初始化时 `CurrentPort` 为无效值 `1`，导致后续行为异常

### 已应用的修复
1. `ProcessCommand` 中 `Subsystem` 为空时发送错误响应（而非静默失败）
2. `.current_port` 文件已手动写入 `15152`

### 修复建议
1. **引擎路径注册表**：确保 `HKCU\Software\Epic Games\Unreal Engine\Builds` 包含 `5.7` 的正确路径
2. **端口分配验证**：写入 `.current_port` 后验证
3. **Tickable 健康检查**：添加日志确认 `FLLMEasyShellTickable::Tick()` 被调用

## Why: 多引擎同时运行时 LLMEasyShell 需要正确路由到目标引擎实例

## How to apply: 调试多引擎连接问题时，首先验证 `.current_port` 文件内容是否与目标端口匹配
