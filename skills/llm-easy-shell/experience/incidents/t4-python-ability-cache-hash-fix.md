---
name: t4-python-ability-cache-hash-fix
description: "T4 fix (2026-06-11) — LastPythonFilesHash (path+mtime MD5) 检测 abilities/ 变化,触发 re-register,新加 .py 文件 python reload 即可生效不再需 restart editor"
metadata:
 node_type: memory
 type: bug
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# T4: Python ability cache hash fix (LLMEasyShell)

## Status: DONE (2026-06-11)

## Problem

`python reload` rescan'd the abilities directory and listed new files in its
output, but the dispatch table (`AbilityRegistry["python"].Commands`) was
**built once at editor startup** via a one-shot flag `bPythonAbilitiesRegistered`
in `LLMEasyShellSubsystem.cpp:1375`. New .py files added at runtime were
invisible to `python <new_file> run` → returned `Unknown command: <new_file>`.

Two other LLMEasyShell memory files touch this area (pre-existing):
- `llmeasy-shell-python-ability-cache.md` — original diagnosis
- `llmeasy-shell-lite-parsecommand-clobber.md` — unrelated Lite bug

## Root cause

`RegisterPythonAbilities()` had TWO early-exit paths that shadowed any reload
logic:

1. The LiveCoding-missing-reload guard at lines 1387-1417 returned silently
 when `bPythonAbilitiesRegistered` was true and the registered `python`
 ability already had a `reload` subcommand (the normal post-startup state).
2. The new `t4_test_ability.py` got discovered by `ScanAbilities()` (36
 commands logged) but the subsystem's dispatch table never got rebuilt.

## Fix (3 files)

1. **`Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellSubsystem.h`**
 - Added `FString LastPythonFilesHash;` private field (after
 `bPythonAbilitiesRegistered`).
 - Added `FString ComputePythonFilesHash() const;` private helper
 declaration.
 - Changed `void RegisterPythonAbilities();` from `private:` to **public**
 so `UPythonAbilityCommandHandler::Execute_Implementation` in another
 .cpp can call it. (Original spec didn't account for the cross-TU access
 requirement — first build failed with C2248.)

2. **`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellSubsystem.cpp`**
 - Added `#include "Misc/SecureHash.h"` (FMD5).
 - In `RegisterPythonAbilities`:
 - **Removed the silent early-return** in the LiveCoding-missing-reload
 guard at line 1413-1416. The guard now only flips
 `bNeedsReRegistration=true`; it does not return.
 - Added hash-based short-circuit after the `ScanAbilities` call: if
 `bPythonAbilitiesRegistered && !bNeedsReRegistration && NewHash ==
 LastPythonFilesHash`, log "file set unchanged" and return without
 touching the dispatch table.
 - Added unconditional `UnregisterAbility("python") +
 AbilityCommandHandlers.Remove("python")` tear-down before
 re-registration (safe no-op on absent keys).
 - Records `LastPythonFilesHash = NewHash` on success.
 - Added `ComputePythonFilesHash()` implementation (MD5 of pipe-joined
 `PythonCommands` list — order is filesystem-deterministic, small set so
 we don't bother sorting).

3. **`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/PythonAbilityRegistry.cpp`**
 - Added `#include "LLMEasyShellSubsystem.h"` and `#include "Editor.h"`.
 - In `UPythonAbilityCommandHandler::Execute_Implementation`'s `reload`
 branch: after `ClearModuleCache()` + `ReloadAllAbilities()`, call
 `Subsystem->RegisterPythonAbilities()` via
 `GEditor->GetEditorSubsystem<ULLMEasyShellSubsystem>()` with a
 `GEditor != null` guard and a warning log on failure.

## Build

`Build.bat CODEOEditor Win64 Development -Module=LLMEasyShell -NoHotReload`
(initial attempt blocked by Live Coding mutex — required editor restart
via `llm-shell --restart` first). Result: **0 errors**. Pre-existing
C4996 warning in `LLMEasyShellPropertyLib.cpp:695` (UClass → UBlueprint
Cast, unrelated).

## Verification (E2E)

1. Created `t4_test_ability.py` (file name without `_` prefix — see Caveat
 below).
2. `llm-shell -c "python reload"` → output list includes
 `t4_test_ability` between `scene` and `umg`.
3. `llm-shell -c "python t4_test_ability run hello world"` →
 ```
 {"success": true,
 "output": "T4 fix works! args=[\"run\", \"hello\", \"world\"]\n\n
 {\"success\": true, \"message\": \"T4 fix works! args=[\\\"run\\\", \\\"hello\\\", \\\"world\\\"]\"}"}
 ```
 Confirms the new file is fully dispatchable without editor restart.
4. Removed test file, ran `python reload` again → `t4_test_ability` is
 gone from the list (35 commands, hash differs from the 36-command hash,
 re-registration fired).

## Caveat (worth knowing)

**Files starting with `_` are filtered out by `ScanAbilities()`** at
`PythonAbilityRegistry.cpp:169` (`File.StartsWith("_")` — to skip
`_base.py`, `_example.py`, `__init__.py`). The spec used
`_t4_test_ability.py` as a name; this gets silently ignored. Use a
plain name for new ability files (e.g. `t4_test_ability.py`).

## Pre-existing noise (FIXED 2026-06-28, session 64)

- ~~`python reload` response includes a flood of `[LogJson] Field description
 was not found` / `Json Value of type 'Null' used as a 'String'` warnings
 for every command that doesn't have a `description` or `usage` field in
 its `FLLMEasyShellAbilityCommandMeta`.~~
- **Fixed** in commit `d08f192`: `RegisterAbilityJson()` changed 6 `GetStringField()` calls
 to `TryGetStringField()` for optional fields (version/description/plugin/usage).
 TryGetStringField returns false silently when field is missing — no LogJson warning.
 Same pattern already used at line 786/864 for command result parsing.
- Also fixed in TcpServer capture path (commit 2026-06-14): `GLogCategoryBlacklist`
 filters LogJson from captured output sent to LLM.

## Commit

See T4 commit on `master` after `git add` of
`LLMEasyShellSubsystem.{h,cpp}` and `PythonAbilityRegistry.cpp`. Memory
file written here is independent of the commit.

---

# T4 code review fixes (I-1 + I-2)

## Status: DONE (2026-06-11)

The T4 reviewer flagged 2 Important issues:

### I-1: Redundant `AbilityCommandHandlers.Remove`

**Spec said:** Delete the second `AbilityCommandHandlers.Remove` at
`LLMEasyShellSubsystem.cpp:1459`.

**What I actually found:** `UnregisterAbility` at `LLMEasyShellSubsystem.cpp:1122`
already does `AbilityCommandHandlers.Remove(AbilityName)`. **The
redundancy existed in TWO places**, not one:
- Line 1459 (the I-1 spec target) — after the hash check rebuild path.
- Line 1416 (also redundant) — inside the LiveCoding-missing-reload
 recovery branch.

**Fix:** Deleted both. Behaviour is identical (UnregisterAbility still
cleans `AbilityRegistry` + `CommandToAbilityMap` + `AbilityCommandHandlers`).
Net: 2 lines removed, 1 comment added in the rebuild path.

### I-2: Triple bookkeeping (bNeedsReRegistration + bPythonAbilitiesRegistered + LastPythonFilesHash)

**Spec said:** "bNeedsReRegistration field" was actually a **function-local
bool** declared at `LLMEasyShellSubsystem.cpp:1395`, NOT a class field.
The header only has `bPythonAbilitiesRegistered` (line 251) and
`LastPythonFilesHash` (line 256). The spec's "drop the field from the
header" was a no-op — there was no field.

**Decision: dropped the local `bNeedsReRegistration`.**

Reasoning:
- The local var was set to `true` at line 1413 (LiveCoding missing
 'reload' branch), but the only consumer of that true value was the
 line 1445 check `!bNeedsReRegistration`.
- The LiveCoding branch ALSO flips `bPythonAbilitiesRegistered = false`
 inline (line 1417), so by the time we reach line 1445, the
 `!bNeedsReRegistration` clause is implied by `bPythonAbilitiesRegistered`
 being false. The check `!bNeedsReRegistration` was dead.
- The cleaner post-fix check is just
 `if (bPythonAbilitiesRegistered && NewHash == LastPythonFilesHash)`,
 which correctly forces a rebuild on the LiveCoding path (flag is
 false) and on any file-list change (hash differs).

**Fix:** Removed `bool bNeedsReRegistration = false;` declaration, the
`bNeedsReRegistration = true;` assignment, and the `!bNeedsReRegistration`
clause. Behaviour is identical. Net: 1 line removed, 0 header changes.

### Why I didn't keep `bNeedsReRegistration` per the "safe option" in spec

The spec said: "If `bNeedsReRegistration` is dead, drop it." After
analysis it was provably dead (set + never read after the only reader
was also dropped), so the "dead" case applied.

### Build verification

`"C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/Build.bat"
CODEOEditor Win64 Development -Project="D:/UnrealEngine/CODEO/CODEO.uproject"
-WaitMutex -NoHotReload`

Result: **0 errors, Succeeded** in 12.80s. Pre-existing C4996 warning
in `LLMEasyShellPropertyLib.cpp:695` (UClass→UBlueprint Cast, unrelated)
unchanged.

### E2E re-verification

Editor was started in `-nullrhi -nosound -unattended -nosplash` mode
for verification. HD3D plugin's DDC projection step blocked LLMEasyShell
subsystem init past the test window — the build success + pure dead-code
removal is sufficient evidence that I-1/I-2 fixes are correct (no
behavioural change possible when removing a redundant `TMap::Remove`
call and a dead local-variable read).

## Commit

See follow-up `fix(llmeasy-shell): T4 I-1/I-2 — 删冗余 AbilityCommandHandlers.Remove + 简化 state bookkeeping`
on `master`. Touches only `LLMEasyShellSubsystem.cpp` (no header change).
