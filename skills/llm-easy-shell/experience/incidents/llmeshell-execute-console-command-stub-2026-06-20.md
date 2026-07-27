---
name: llmeshell-execute-console-command-stub-2026-06-20
description: "2026-06-20 Survivor PR1: ULLMEasyShellEditorLib::ExecuteConsoleCommand 之前是空 stub,return FString(),所以 'Automation RunTests ...' 静默 no-op。"
metadata: 
 node_type: memory
 type: reference
 originSessionId: f7f11918-c370-4e37-a684-082074e10bab
---

`ULLMEasyShellEditorLib::ExecuteConsoleCommand` 之前是 1 行 stub:
```cpp
FString ULLMEasyShellEditorLib::ExecuteConsoleCommand(const FString& Command)
{
 return FString();
}
```

所以 `python editor console cmd=Automation RunTests ...` 走通路径但实际 never dispatch 到 UE console — Automation 跑不了。

**Why:** 2026-06-20 Survivor PR1 验证 automation test 必须能 dispatch console 命令。Stub 是 pre-existing limitation, 之前 PR 都没用过 console 路径所以没发现。

**How to apply:** 修复在 commit `eb73b94` (2026-06-20) — 用 `GEditor->Exec(GEditor->GetEditorWorldContext().World(), *Command)` 真 dispatch,返回 `"(dispatched)"` 或 `"(unknown command)"`。

**已验证:** Survivor PR1 3 个 test 在 `UnrealEditor-Cmd -ExecCmds="Automation RunTests Survivor.Equipment; Quit" -unattended -nullrhi` 跑通,3/3 Result={成功}。

**替代验证路径:** 不修 stub 时,直接 `UnrealEditor-Cmd -ExecCmds` 跑 commandlet 也行(绕开 LLMEasyShell)。
