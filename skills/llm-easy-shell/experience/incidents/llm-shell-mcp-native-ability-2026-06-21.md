---
name: llm-shell-mcp-native-ability-2026-06-21
description: 2026-06-21 UE 5.8 官方 ModelContextProtocol 插件包成 LLMEasyShell 原生 mcp 命令（status/start/stop/tools/call/config），6 子命令，C++ API 同步直调避免 HTTP 死锁
metadata: 
 node_type: memory
 type: project
 originSessionId: d5bb06cc-f398-45a1-bc61-5e3fb823d173
---

# UE 5.8 ModelContextProtocol → LLMEasyShell 原生 mcp 命令

## 改了什么（2026-06-21）

- `Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellTypes.h` — 加 `UShellCommand_Mcp` 声明（6 子命令：status / start / stop / tools / call / config）
- `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Mcp.cpp` — 新文件，直接调 `IModelContextProtocolModule` 同步 C++ API（不用 HTTP，避免 game-thread 死锁）
- `Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp` — 注册到 Dispatcher（`RegisterCommand(NewObject<UShellCommand_Mcp>(this))`）
- `Plugins/LLMEasyShell/Source/LLMEasyShell/LLMEasyShell.Build.cs` — 加 2 个 PrivateDependency（`ModelContextProtocol` + `ModelContextProtocolEngine`）+ `WITH_LLMEASYSHELL_MCP=1`，全部在 `bBuildEditor` 块内
- `Plugins/LLMEasyShell/LLMEasyShell.aiac` — 加 `hostDependencies` 条目 + `fixHistory` 条目

## 设计关键决策

**为什么不用 HTTP 走 JSON-RPC**：`FHttpRequest` 是异步的，shell dispatcher 同步路径上 `FEvent::Wait` 会阻 game thread → `FHttpManager` 无法 tick → completion 永远不 fire → 死锁。

**改用同步 C++ API**：
- `IModelContextProtocolModule::StartServer/StopServer/GetServer/GetTools/FindTool` 全同步
- `IModelContextProtocolTool::Run(Params)` 同步返回 `FModelContextProtocolToolResult`
- `FModelContextProtocolToolResult` 继承 `FJsonObjectWrapper`，有 `JsonObject` 字段

**为什么不走 `ToolsSearch=true` 暴露所有 tool**：5.8 默认 3 个工具（`list_toolsets` / `describe_toolset` / `call_tool`）作为统一入口；LLM 客户端（Claude）首次 `list_tools` 拿到这 3 个，再通过 `describe_toolset` 发现子 tool，然后 `call_tool` 间接调。`mcp tools` 直接列这 3 个；`mcp call` 也能直接调任何名字（包括 `ToolsetRegistry.AgentSkillToolset.CreateSkill` 这种 long-name 子 tool）。

## 关键踩坑

### 1. `ModelContextProtocolSettings.h` 在 `ModelContextProtocolEngine` 不在 `ModelContextProtocol`

第一次 Build.cs 只加了 `ModelContextProtocol`，UBT 报 `fatal error C1083: ModelContextProtocolSettings.h: No such file or directory`。

UE 5.8 MCP 插件的 6 个 module:
- `ModelContextProtocol` (Runtime) — server / tool 接口 / 协议常量
- `ModelContextProtocolEngine` (Runtime) — **Settings / ClientConfig / ToolLibrary / EngineMetaData** ← Settings 在这
- `ModelContextProtocolEditor` (Editor) — EditorToolLibrary / AssetDefinitions / ToolsetRegistryAdapter
- `ModelContextProtocol{Engine,Editor}Tests` — test 模块

**修法**：Build.cs 两个都要加。

### 2. LiveCoding 报 success 但 restart 失败

第一次 `livecoding` 返回 `compileSuccess:true, errorCount:0`，但 `llm-shell --restart` 走 UBT 全量构建报 fatal error。原因：LiveCoding 的 PCH cache 对新增 module dep 不敏感，会 patch 成功但全量 UBT 不行。所以加新 module dep 后**必须 UBT 全量构建**验证。

### 3. `WITH_LLMEASYSHELL_MCP` 宏设计

为避免强加 host dep 给非 UE 5.8 / 不想 enable MCP 的项目，整个 cpp 实现用 `#if WITH_LLMEASYSHELL_MCP` 包住，host 不 enable 时：
- Build.cs `PrivateDefinitions.Add("WITH_LLMEASYSHELL_MCP=1")` 不执行（`bBuildEditor` 块是死代码 if 不加 dep）
- 不加 dep → 头文件找不到 → link 失败

所以**必须 host 在 .uproject enable `ModelContextProtocol`** 才能 link，否则 Build.cs dep 块找不到头文件直接挂。这是为什么 aiac `hostDependencies` 条目要写清楚。

## 实测结果（UE 5.8.1-CL-55116800）

```
mcp status → Running:no, Port:8000, Path:/mcp, Tools Loaded:3 ✅
mcp start → Started MCP server on port 8000 ✅
mcp status → Running:yes ✅
mcp tools → list_toolsets / describe_toolset / call_tool (3 top-level) ✅
mcp call list_toolsets {} → 1 toolset: ToolsetRegistry.AgentSkillToolset ✅
mcp call describe_toolset {"toolset_name":"ToolsetRegistry.AgentSkillToolset"} → 4 sub-tools (UpdateSkill/ListSkills/GetSkills/CreateSkill) ✅
mcp config claude → 写 D:/UnrealEngine/CODEO/.mcp.json (110 bytes) ✅
mcp stop → Stopped MCP server ✅
curl http://localhost:8000/mcp -X POST '{"jsonrpc":"2.0","id":1,"method":"ping"}' → {"jsonrpc":"2.0","id":1,"result":{}} ✅
```

## 配置写盘注意事项

- 默认路径 `D:/<ProjectDir>/.mcp.json`（Claude Code 标准）
- 传 `/tmp/foo` 这种 Git Bash 假路径会写盘失败（C++ `FFileHelper::SaveStringToFile` 当成绝对路径处理，Windows 上不存在 `/tmp/` 目录）。**正确用法**：传 Windows 路径（`C:/...`）或不传（用默认 project 根）
- Cursor → `.cursor/mcp.json`，VSCode → `.vscode/mcp.json`，Gemini → `.gemini/settings.json`

## LLM 客户端接入

Claude Code（HTTP transport）：
```json
{
 "mcpServers": {
 "unreal": {
 "type": "http",
 "url": "http://localhost:8000/mcp"
 }
 }
}
```

启动 Claude Code 前要先 `mcp start`（或者 UE editor 用 `-ModelContextProtocolStartServer` flag 启动让 server 自动起）。

## Why

用户升级 UE 5.7.4 → 5.8 后，`.uproject` 已经加了 `ModelContextProtocol` plugin（Experimental 引擎插件），但只是个 HTTP server，没有 UI / 命令行入口。让 llmshell 能直接调 MCP tools 是连接 Claude Code 自动化 ↔ UE editor 的桥。

## How to apply

- 加新 UE 引擎 Experimental plugin 作为 dep 时，**先查该 plugin 有几个 module**（UE 5.8 MCP 有 6 个），Settings 通常在 `*Engine` 模块，Tool/Server API 在基础模块
- 加 C++ dep 后**必须 UBT 全量构建**（`--restart`），不能只信 `livecoding` success
- 想用同步 HTTP client 调用 async HTTP server 时，几乎一定要绕开 HTTP 直接调 C++ API，否则 game-thread 同步路径必死锁