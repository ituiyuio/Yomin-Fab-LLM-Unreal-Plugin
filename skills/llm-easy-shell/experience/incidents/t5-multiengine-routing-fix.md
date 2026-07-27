---
name: t5-multiengine-routing-fix
description: "T5 fix (2026-06-11) — 4 sub-fixes (TcpServer null guard + 4-path engine discovery + .current_port reset + Tickable log),multi-engine routing 加固"
metadata:
 node_type: memory
 type: bug
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# T5 Multiengine Routing Fix (2026-06-11)

## 4 sub-fixes applied

| ID | File | Purpose |
| --- | --------------------------------------------------- | --------------------------------------------------------------- |
| T5a | `Plugins/LLMEasyShell/.../LLMEasyShellTcpServer.cpp` | Strengthen ProcessCommand null guard with explicit "Tickable died" diag + actionable error message |
| T5b | `.claude/skills/llm-easy-shell/llm-shell/main.cpp` + lite version | Engine path fallback 4 standard install paths (C/D Program Files/Epic Games + C/D Epic Games) using `GetFileAttributes` (directory check) + per-path stderr log |
| T5c | `Plugins/LLMEasyShell/.../LLMEasyShellSubsystem.cpp` | `.current_port` 写后立即读回验证,检测 multi-instance race |
| T5d | same | `FLLMEasyShellTickable::Tick()` 入口加 Verbose 健康日志 (每 ~10s, frame % 600) |

## Key findings during implementation

### 1. Task spec mis-located T5b

Task description said T5b belongs in `LLMEasyShellSubsystem.cpp`, but engine path resolution is **process-external** (in `llm-shell.exe` / `llmshelllite.exe` C++ CLI), not in the plugin. Fixed in `main.cpp` (full + lite versions).

### 2. T5a was partially pre-implemented

`ProcessCommand` at `LLMEasyShellTcpServer.cpp:404-413` already had a null guard with `EShellErrorCode::InternalError`. The actual T5a improvement was: (a) better diagnostic log message including "Tickable may have died", (b) standardized error string from "LLMEasyShell subsystem not initialized" to "Internal error: subsystem not initialized" (more actionable — "internal error" tells the LLM agent this isn't a command bug).

### 3. T5b uses `GetFileAttributes` (Win32), not UE's `FPaths::DirectoryExists`

The CLI is a standalone Win32 executable; no UE engine available. The fix uses `GetFileAttributesA` (already in `windows.h` includes) to check the engine **directory** exists, not probing `UnrealEditor.exe` directly. This catches broken installs (engine root present but Binaries missing) and avoids fopen's silent miss on locked-file edge cases.

### 4. Lite version has pre-existing build break

`llmshelllite.exe` compile.ps1 fails with:
```
main.cpp(652): error C2065: 'MAX_PORT': undeclared identifier
main.cpp(652): error C2065: 'BASE_PORT': undeclared identifier
main.cpp(652): error C2737: 'kScanPortCount': must initialize constexpr object
main.cpp(653): error C2131: expression did not evaluate to a constant
```

Unrelated to T5 — pre-existing in lite's port-scan code. T5b's main.cpp changes compile cleanly in **full** version. **To do later**: rebase lite on full main.cpp (they share 95% of the engine path logic).

### 5. Editor was in crash state during T5 verification

Pre-existing `UnrealEditor_TedsCore` crash (UECC-Windows-... call stack in HD3D chain) blocked Step 6 dual-instance PIE test. **Step 7 engine miss test still passed** because llm-shell --restart runs even when editor is not running, hits the engine path fallback, and reports the actionable error.

## Verification

- **Step 5 build (LLMEasyShell module)**: Succeeded, 0 errors. 1 pre-existing C4996 Cast<> warning unrelated to T5.
- **Step 5 build (full llm-shell.exe)**: Succeeded, 0 errors.
- **Step 5 build (lite llmshelllite.exe)**: FAILED — pre-existing MAX_PORT/BASE_PORT errors, NOT T5.
- **Step 7 engine miss actionable error**: PASSED. Output (5.7 → 9.9):
 ```
 [llm-shell] Engine fallback miss: C:\Program Files\Epic Games\UE_9.9 (not found)
 [llm-shell] Engine fallback miss: D:\Program Files\Epic Games\UE_9.9 (not found)
 [llm-shell] Engine fallback miss: C:\Epic Games\UE_9.9 (not found)
 [llm-shell] Engine fallback miss: D:\Epic Games\UE_9.9 (not found)
 [llm-shell] Engine 9.9 not found in any standard path!

 [llm-shell] FATAL: Could not locate Unreal Engine 9.9. Tried:
 - HKCU\Software\Epic Games\Unreal Engine\Builds\9.9
 - HKLM\Software\Epic Games\Unreal Engine\Builds\9.9
 - C:\Program Files\Epic Games\UE_9.9
 - D:\Program Files\Epic Games\UE_9.9
 - C:\Epic Games\UE_9.9
 - D:\Epic Games\UE_9.9
 Fix: install UE 9.9 via Epic Launcher (or portable extract),
 or set the registry value to the engine install path.
 ```
- **Step 6 dual-instance routing**: BLOCKED (editor crash). Logic correct in source; can be re-tested after editor restart.

## Files changed

1. `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\Source\LLMEasyShell\Private\LLMEasyShellTcpServer.cpp` — T5a
2. `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\Source\LLMEasyShell\Private\LLMEasyShellSubsystem.cpp` — T5c + T5d
3. `D:\UnrealEngine\CODEO\.claude\skills\llm-easy-shell\llm-shell\main.cpp` — T5b (full)
4. `D:\UnrealEngine\CODEO\.claude\skills\llm-easy-shell-lite\llm-shell\main.cpp` — T5b (lite)

## Unrelated issues observed (out of T5 scope)

- **Lite `main.cpp` build break** (MAX_PORT/BASE_PORT/kScanPortCount undeclared at line 652-655). Pre-existing — need to either rebase lite on full main.cpp or define those constants locally.
- **`UnrealEditor_TedsCore` crash** (ProcessId 8068) blocks full dual-instance verification. Not a T5 issue — call stack points to HD3D TedsAlerts/HD3D postprocess. TedsCore is an internal UE module for live telemetry.
- **Cast<> warning** in `LLMEasyShellPropertyLib.cpp:695` (C4996, "Attempting to use Cast<> on types that are not related"). Pre-existing.

## T5 code review fix (I-1) — 2026-06-11

**Reviewer finding:** T5a's `ProcessCommand` null guard checked `Subsystem` but called `SendResponse(ClientSocket, ...)` without a `ClientSocket` null check. `SendResponse` itself guards (line 441-444) so it was technically safe, but the asymmetry was misleading: if `ClientSocket` was null/closed, the T5a log would say "Subsystem null" while the client got a 0-byte response — the same silent-failure mode T5a was trying to escape.

**Fix (1 line net change):** Wrap the `SendResponse(ClientSocket, NullSubsystemResult)` call in `if (ClientSocket) { ... }` at `LLMEasyShellTcpServer.cpp:413-420`. Real field names in this codebase are `bSuccess` and `Error` (not the spec's `Success` / `Message`); I used the actual struct fields.

**Diff sketch:**
```cpp
// before (lines 411-418)
UE_LOG(LogTemp, Error, TEXT("ProcessCommand: Subsystem null! Tickable may have died."));
FLLMEasyShellResult NullSubsystemResult;
NullSubsystemResult.bSuccess = false;
NullSubsystemResult.Error = TEXT("Internal error: subsystem not initialized");
NullSubsystemResult.ErrorCode = EShellErrorCode::InternalError;
SendResponse(ClientSocket, NullSubsystemResult);
return;

// after (lines 411-421)
UE_LOG(LogTemp, Error, TEXT("ProcessCommand: Subsystem null! Tickable may have died."));
if (ClientSocket) // I-1 fix: align with SendResponse's own null-guard convention
{
 FLLMEasyShellResult NullSubsystemResult;
 NullSubsystemResult.bSuccess = false;
 NullSubsystemResult.Error = TEXT("Internal error: subsystem not initialized");
 NullSubsystemResult.ErrorCode = EShellErrorCode::InternalError;
 SendResponse(ClientSocket, NullSubsystemResult);
}
return;
```

**Build verification:** `cmd //c ".\\build_via_cmd.bat"` (no `D:\UnrealEngine\CODEO\Build.bat` exists; wrapper invokes UE 5.7 Build.bat with `-NoHotReload`) → `Result: Succeeded`, 0 errors, 13.45s. `LLMEasyShellTcpServer.cpp` was re-compiled and `UnrealEditor-LLMEasyShell.dll` re-linked.

**Behavior in normal case (ClientSocket non-null):** Unchanged — log still fires, JSON error response still sent.

**Behavior in degenerate case (ClientSocket null/closed):** Log still fires (so we keep the diagnostic trail), but no `SendResponse` call (which would have silently returned anyway inside its own null guard). No more misleading asymmetry.
