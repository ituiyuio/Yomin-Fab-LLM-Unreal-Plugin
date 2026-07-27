---
name: llmeasyshell-lite-parsecommand-clobber
description: "LLMEasyShellLite 两条串行 bug 全部已修: ExecuteSingle 删 Command clobber + GetPIEWorld 加 null-safe; 引入 commit a85f5548"
metadata: 
 node_type: memory
 type: bug
 originSessionId: 86b7dbae-620d-4667-9e85-c26bc533aa49
---

> **[tool-fix-121 2026-06-28]** 跨 2026-06-06 修复 commit a85f5548 后续多次 .cpp edit 后,本 forensic record 中 line refs 已 drift（ExecuteSingle 274-285 → 现 274 起 + clobber 已删 / ParseCommand 633-643 → 现 660 / GetPIEWorld 676 → 现 690 / GetWorld 663 → 现 681 / ExecuteSingle 298 → 现 274). 因本记录保留 2026-06-06 bug 历史 snapshot intentional,line refs 保留原值不修改,实际跳读请 grep 函数名 + commit ref a85f5548。

# LLMEasyShellLite ParseCommand 后 Command 被覆盖（2026-06-06 修）

## 现象
编辑器收到任何 ≥2 词命令（例如 `cat /Actor/Foo`、`find Asset *x*`、`quixel search wooden table`、`ls /Level/Actors --limit 5`）都返回：
```
{"success": false, "error": "Unknown command: '<第二个token>'. Use 'help' to list available commands."}
```
单 token 命令返回 `"No command provided"`。所有 `ls / cat / find / quixel` 都死。

## 根因（两层，串行触发 crash）

### 第一层：ExecuteSingle 274-285 行的 Command clobber
`Plugins/LLMEasyShellLite/Source/.../Private/LLMEasyShellLiteSubsystem.cpp` 第 274-285 行：
```cpp
if (Args.Num() == 0) { ... return "No command provided"; } // 太严，挡了 info/help
TracedCommandName = Args[0];
Command = Args[0]; // 覆盖 ParseCommand 的输出
Args.RemoveAt(0);
```
而 `ParseCommand`（633-643 行）已经正确把 `OutCommand = first token`、`OutArgs = rest`。`ExecuteSingle` 在拿到正确的 `Command` 后又无条件用 `Args[0]` 覆盖 → `Command` 变成第二个 token，ability prefix 探测全 miss。

### 第二层：GetPIEWorld() null-deref (parser 修好后暴露)
`LLMEasyShellLiteSubsystem::GetPIEWorld()` 第 676 行（原）：
```cpp
return GEditor->GetPIEWorldContext()->World(); // 不在 PIE 时 GetPIEWorldContext() 返回 null
```
Parser bug 掩盖了它（clobber 后 CommandDispatcher 路径不执行，GetWorld 不被调用）。修好 parser 后第一发 `info` 立刻崩：
```
EXCEPTION_ACCESS_VIOLATION reading address 0x00000000000002c8
 ULLMEasyShellLiteSubsystem::GetWorld() [line 663]
 ULLMEasyShellLiteSubsystem::ExecuteSingle() [line 298]
```

## 引入 commit
`a85f5548 feat(llm-easy-shell-lite): 新独立只读子项目` (2026-06-05)

## 修复（2026-06-06）

### 第一层（ExecuteSingle）
删除 283-285 三行，把 274 的 `if (Args.Num() == 0)` 改为 `if (Command.IsEmpty())`，加注释解释：
- ParseCommand 已经正确解析，trust 它
- 单字命令（`info`/`help`）Command 非空，必须能进 dispatcher
- 空字符串才拦截（返回 "No command provided"）

### 第二层（GetPIEWorld）
照搬 full LLMEasyShell 插件的 null-safe 模式：
- 检查 `GEditor->IsPlayingSessionInEditor()` 提前返回 nullptr
- 用 `for (FWorldContext : GEngine->GetWorldContexts())` 找 `EWorldType::PIE` 而非 `GetPIEWorldContext()->World()`（后者在非 PIE 时返回 null 解引用）

## 验证
1. `llmshelllite --restart` 触发 plugin 重编（~5s）
2. 跑 `info` 返回完整 editor state JSON
3. 跑 `ls /Level/Actors --limit 3` 返回 actor 列表
4. 跑 `cat /Actor/SunLight` 返回 properties + components
5. 跑 `find Actor BP_*` / `discover /Actor/SunLight --props` 返回真数据

## Why
LLMEasyShellLite 是 v2 只读简化版（不能 spawn / set / call / save），但代码复用 main 模板时把 main 版本 `if (!bIsAbilityPrefix) { Command = Args[0]; ... }` 的 *条件* 改成了 *无条件*，破坏 ability 路由。
**Why: 修复时一定要保留 `bIsAbilityPrefix` 检查 + 不变量 `Command == ParseCommand.OutCommand`。**

## How to apply
任何时候发现编辑器 ≥2 词命令都返回 "Unknown command: X"（X 是第二个 token）或单字命令都返回 "No command provided"，先检查 ExecuteSingle 的 clobber 3 行。
如果之后还看到 access violation 0x2c8 + GetPIEWorld callstack，就是 GetPIEWorldContext() null 路径。Log 关键字：`LogLLMEasyShellLite: Processing command: <原始一行>`。
