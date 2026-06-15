---
outline: [2, 3]
---

# LLM Easy Shell Lite

> Read-only TCP bridge between any LLM agent and the Unreal Editor.
> Co-exists with **LLM Easy Shell** (full read + write + automation, separate
> TCP port range `15151–15200`).

**Quick value:** 9 read-only commands · open PyAbility framework · ports
15201–15250 · 2 engine plugin dependencies · zero third-party libraries.

> 🎯 **For full read + write + automation**, see
> [LLM Easy Shell](../llm-easy-shell/) (35+ commands, 25+ Python abilities).

---

## Core Features

- **Read-only TCP server** — port range 15201–15250 (disjoint from full
  Easy Shell's 15151–15200)
- **9 built-in read-only commands** — `ls` / `cat` / `find` / `discover` /
  `info` / `help` / `gamestate` / `log` / `msglog`
- **Open PyAbility framework** — full UE Python access via `python <name>`
- **Niagara message-log capture** — pull validation messages for VFX work
- **Multi-plugin C++ ability auto-registration** — `LLMMaterial`, `LLMVFX`,
  `LLMStateTree` etc. register their abilities here at startup
- **AI-agent-first JSON protocol** — single-line request in, single-line
  JSON response out

## Quick Preview

```bash
# Agent loop — one line per action
> info
{"project":"MyGame","engine":"5.7.4","pie":"stopped","port":15201}

> ls /Level/Actors
{"ok":true,"items":["BP_Player_C_1","BP_PlayerStart_1"],"count":2}

> cat /Actor/BP_Player_C_1
{"ok":true,"name":"BP_Player_C_1","class":"BP_Player_C","location":[0,0,200],"health":100}

> gamestate
{"ok":true,"wave":3,"health":85,"gold":120}
```

Send a one-line command → Get a one-line JSON response. **No write access**:
every command is read-only by design, so it's safe to leave running in
exploratory pipelines.

---

## Technical Information

**Features:** Read-only TCP server (port 15201–15250), 9 built-in read-only
commands (`ls` / `cat` / `find` / `discover` / `info` / `help` / `gamestate`
/ `log` / `msglog`), open PyAbility framework (full UE Python access),
Niagara message-log capture, multi-plugin C++ ability auto-registration,
AI-agent-first JSON protocol.

**Code Modules:** LLMEasyShellLite (Editor)

**Number of Blueprints:** 0

**Number of C++ Classes:** ~20

**Network Replicated:** No

**Supported Development Platforms:** Windows: Yes, Mac: Yes, Linux: Yes

**Supported Target Build Platforms:** Windows, Mac, Linux

**Documentation Link:** [Documentation.md in plugin folder](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/tree/main/Plugins/LLMEasyShellLite/Documentation.md)

**Example Project:** Any UE 5.7+ project — connect a TCP client to
`localhost:15201` (first free port in `15201–15250`).

**Important/Additional Notes:** Requires `PythonScriptPlugin` and
`EditorScriptingUtilities` (both bundled with UE 5.7+). Plugin is Editor-only
(`Type: Editor` in `.uplugin`). No third-party C++ or Python libraries are
shipped.

---

## Build Environment

### Required Host Plugins

This plugin depends on two engine plugins that **must be enabled** in the
host project before compilation. They are included with UE 5.7+ and do not
need to be downloaded separately:

- **PythonScriptPlugin** — Required to execute `.py` PyAbilities. Enable via
  `Edit → Plugins → Python Editor Script Plugin`, or add to your `.uproject`:
  ```json
  "Plugins": [{ "Name": "PythonScriptPlugin", "Enabled": true }]
  ```
- **EditorScriptingUtilities** — Required for asset / level introspection
  helpers. Enable via `Edit → Plugins → Editor Scripting Utilities`, or add
  to your `.uproject`:
  ```json
  "Plugins": [{ "Name": "EditorScriptingUtilities", "Enabled": true }]
  ```

### Verifying a Clean Build

```bash
cd "/c/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles"
./RunUAT.bat BuildPlugin \
  -plugin="D:/path/to/LLMEasyShellLite.uplugin" \
  -package="D:/Temp/LLMEasyShellLite" \
  -platform=Win64 \
  -configuration=Development \
  -rocket
```

The `-rocket` flag enables Epic's IWYU + ABI-strict build configuration,
matching the Fab submission environment. Confirm zero errors and zero
consequential warnings (deprecation warnings such as `C4996` are treated as
errors by many marketplace scanners).

### UE Version Compatibility

- **Minimum:** UE 5.7 (`EngineVersion: "5.7.0"` in `.uplugin`)
- **Tested:** UE 5.7

---

## Architecture

### Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│  LLM Agent (any TCP client)                                         │
└──────────────────────────┬─────────────────────────────────────────┘
                           │  one-line command + \n
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│  FLLMEasyShellLiteTcpServer  (Editor module, main thread)            │
│  • Bind first free port in 15201–15250                               │
│  • Per-connection line buffer                                        │
└──────────────────────────┬─────────────────────────────────────────┘
                           │  line
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│  FCommandDispatcher  (CommandDispatcher.cpp)                         │
│  • 9 built-in C++ commands  (ShellCommand_*.cpp)                     │
│  • 1 dispatch to PythonAbilityRegistryLite                          │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
┌──────────────────────┐           ┌─────────────────────────────────┐
│  C++ Commands         │           │  UPythonAbilityRegistryLite    │
│  (ShellCommand_*.cpp) │           │  • Scan PyAbilities/.../abilities │
│  ls/cat/find/discover │           │  • Dispatch to user .py        │
│  info/help/gamestate/ │           │  • Inject UWorld auto          │
│  log/msglog            │           └─────────────────────────────────┘
└──────────┬────────────┘
           │  FLLMEasyShellReflectionLite / FPropertyRouter
           ▼
┌────────────────────────────────────────────────────────────────────┐
│  Unreal Editor (UClass / UFunction / UProperty / AssetRegistry)     │
└────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              JSON line back to the agent
```

### Threading Model

- **TCP listener**: main thread; non-blocking `FSocket` accept loop driven by the `UEditorSubsystem` tick.
- **Command execution**: synchronous on the game thread. All 9 built-in commands and PyAbility dispatches complete before the next TCP line is read.
- **Python execution**: routed through `PythonScriptPlugin`'s `FPythonScriptExecution` (game thread, same as C++).
- **Side-effect guarantee**: built-in commands are read-only by design; PyAbilities can do whatever the UE Python API allows.

---

## Command Reference

All commands return a single JSON line terminated by `\n`. Errors are
reported as `{"ok": false, "error": "..."}`.

### `info`

- **Args:** none
- **Returns:** `{"project": str, "engine": str, "pie": "stopped"|"playing"|"paused", "port": int}`

```bash
> info
{"project":"MyGame","engine":"5.7.4","pie":"stopped","port":15201}
```

### `ls`

- **Args:** `<path>` where path ∈ {`/Level/Actors`, `/Assets/...`}
- **Returns:** `{"ok": true, "items": [str, ...], "count": int}`

```bash
> ls /Level/Actors
{"ok":true,"items":["BP_Player_C_1","BP_PlayerStart_1"],"count":2}
```

### `cat`

- **Args:** `/Actor/{name}` or `/Assets/.../Asset.Asset`
- **Returns:** JSON representation of the UObject (properties + values,
  snake_case keys via `FProperty` reflection)

```bash
> cat /Actor/BP_Player_C_1
{"ok":true,"name":"BP_Player_C_1","class":"BP_Player_C","location":[0,0,200],"health":100}
```

### `find`

- **Args:** `Actor` | `Asset` | `/Game` `[name_filter]`
- **Returns:** `{"ok": true, "items": [str, ...], "count": int}`
- **Notes:** `Actor` walks the current world; `Asset` queries
  `AssetRegistry`; `/Game` does a path-prefix search.

### `discover`

- **Args:** `--funcs` | `--props` `[<ClassName>]`
- **Returns:** List of `UFunction` / `FProperty` entries (name, type, flags)
  for the given `UClass`. Default class is the currently selected actor's
  class.

### `gamestate`

- **Args:** none
- **Returns:** `{"ok": true, "wave": int, "health": int, "gold": int}`
  (project-defined; defaults to zeros if no PIE session is active)
- **Note:** Field set is project-specific. The bundled `gamestate` returns
  project-specific keys; this contract is intended for **read** by agents,
  **write** by the game code.

### `log`

- **Args:** `--errors` | `--warnings` | `--all` `[N]`
- **Returns:** Last `N` entries from the Output Log filtered by severity
  (default `N=20`).

### `msglog`

- **Args:** `--niagara` `[N]`
- **Returns:** Last `N` entries from the Niagara message-log category
  (default `N=20`).

### `help`

- **Args:** `[<command_name>]`
- **Returns:** List of all commands (or detailed help for one command).

### `python`

- **Args:** `<ability_name> [arg1 arg2 ...]` | `reload`
- **Returns:** Whatever the ability's `main()` returns (must be
  JSON-serialisable).
- **Notes:** the bundled `simple` ability echoes args; `reload` re-scans
  `PyAbilities/.../abilities/`. See [PyAbility Extension API](#pyability-extension-api)
  below.

---

## PyAbility Extension API

Lite exposes three Python base classes (re-exported from
`LLMShellAbilitiesLite.registry`) and a discovery convention.

### Discovery Convention

- A file in `PyAbilities/LLMShellAbilitiesLite/abilities/` whose name
  **does not** start with `_` is auto-registered.
- The file must define either:
  - A module-level
    `def main(args: list[str], world: UWorld|None) -> dict` function
    (recommended for single-command abilities), or
  - A class deriving from `Ability` (recommended for multi-subcommand
    abilities).

### `class Context`

Provided as the second argument to `main()` or as the `context` argument to
`Ability.execute`. Exposes the current `UWorld` and editor helpers.

```python
class Context:
    @property
    def world(self) -> UWorld | None:
        """Lazily resolves the current editor world (None if no PIE session)."""
```

### `class Command`

```python
class Command:
    def __init__(self, name: str, description: str, params: list[str] | None = None):
        self.name        # subcommand name
        self.description # one-line help text
        self.params      # positional arg names
```

### `class Ability`

```python
class Ability:
    name: str                  # class attribute, ability namespace
    version: str               # class attribute, free-form

    def get_commands(self) -> list[Command]: ...
    def execute(self, command: str, args: list[str], context: Context) -> dict: ...
    def get_description(self) -> str: ...
```

### Lifecycle

- `python reload` triggers a `sys.modules` clear of
  `LLMShellAbilitiesLite*` + `LLMEasyShellLite*`, then re-imports and
  re-registers all discovered abilities.
- The C++ side does not cache function pointers — each call re-resolves
  `main` / `get_commands` / `execute` through `PythonScriptPlugin`'s `eval`
  interface. **No editor restart needed** for adding / removing / renaming
  abilities.

### Multi-Plugin Ability Registration

Other plugins (e.g. `LLMMaterial`, `LLMVFX`, `LLMStateTree`) can register
C++ abilities directly with `UPythonAbilityRegistryLite` at module startup;
those abilities then appear alongside the PyAbilities under the same
dispatcher.

---

## C++ Class Reference

| Class / Struct | Header | Purpose |
|----------------|--------|---------|
| `ULLMEasyShellLite` | `Public/LLMEasyShellLite.h` | `IModuleInterface`; module startup/shutdown, installs the C++ ability hook. |
| `ULLMEasyShellLiteSubsystem` | `Public/LLMEasyShellLiteSubsystem.h` | `UEditorSubsystem` that owns the TCP server, command dispatcher, and Python ability registry. |
| `FLLMEasyShellLiteTcpServer` | `Public/LLMEasyShellLiteTcpServer.h` | TCP listener (binds first free port in 15201–15250) + per-connection line buffer. |
| `FCommandDispatcher` | `Private/CommandDispatcher.cpp` | Routes a command line to a `ShellCommand_*` handler or to `UPythonAbilityRegistryLite`. |
| `FLLMEasyShellReflectionLite` | `Public/LLMEasyShellReflectionLite.h` | UClass / UFunction / UProperty reflection helpers for `discover` / `cat`. |
| `FPropertyRouter` | `Public/PropertyRouter.h` | Property get/set routing for `cat` + `discover --props`. |
| `UPythonAbilityRegistryLite` | `Public/PythonAbilityRegistryLite.h` | Scans `PyAbilities/.../abilities/`, dispatches Python `main()` / `Ability.execute()`. |
| `FCommandTraceLoggerLite` | `Public/CommandTraceLoggerLite.h` | In-memory ring buffer of recent commands + their JSON responses (for `log` / replay). |
| `ShellCommand_Ls` … `ShellCommand_MessageLog` | `Private/ShellCommand_*.cpp` | One class per built-in command. |
| `FLLMEasyShellLiteTypes` | `Public/LLMEasyShellLiteTypes.h` | Shared structs (`FCommandRequest`, `FCommandResponse`, `FPythonAbilityRecord`, JSON helpers). |

---

## File Layout

```
LLMEasyShellLite/
├── LLMEasyShellLite.uplugin         Plugin descriptor (EngineVersion, Modules, PlatformAllowList)
├── README.md                        Quickstart + tutorial (marketing + teaching)
├── Documentation.md                 Technical reference
├── VERSION-NOTES.md                 Version history
├── Config/
│   └── FilterPlugin.ini             Fab-packaged-file manifest
├── PyAbilities/
│   └── LLMShellAbilitiesLite/
│       ├── __init__.py
│       ├── registry.py
│       └── abilities/
│           ├── _base.py             Internal helpers
│           ├── _unreal_helpers.py   Internal helpers
│           ├── _example.py          Reference template
│           └── simple.py            Demo ability (publisher code)
├── Source/
│   ├── ThirdParty/
│   │   ├── README.md                "No third-party C++" declaration
│   │   └── NOTICE.txt               Fab scanner-friendly declaration
│   └── LLMEasyShellLite/
│       ├── LLMEasyShellLite.Build.cs
│       ├── Public/                  C++ headers (Subsystem, TCP server, types, registry)
│       └── Private/                 C++ implementation (one file per command + dispatcher)
```

---

## Third-Party Software

This plugin **uses no third-party C++ or Python libraries**. All C++ source
under `Source/LLMEasyShellLite/` is original work by the publisher
(YominUnreal). All Python under
`PyAbilities/LLMShellAbilitiesLite/abilities/` is also original publisher
code shipped as part of the plugin's open PyAbility framework — it is not a
third-party dependency and is not redistributed from any external source.

The only engine-level dependencies are:

- **PythonScriptPlugin** — Epic-shipped, bundled with UE 5.7+
- **EditorScriptingUtilities** — Epic-shipped, bundled with UE 5.7+

These are engine plugins, not third-party software under Fab's definition.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Plugin doesn't appear in Plugins Browser | `Plugins/` folder in wrong location | Verify folder is at `<ProjectRoot>/Plugins/LLMEasyShellLite/` |
| Editor complains about missing PythonScriptPlugin | Engine plugin not enabled | Enable in `.uproject` Plugins array, restart editor |
| TCP client can't connect | Firewall blocking loopback | Allow `UnrealEditor.exe` on `127.0.0.1:15201–15250` |
| Port already in use | Another tool (or Advanced) bound it | See port in Output Log; the listener skips occupied ports |
| `python reload` doesn't pick up new ability | Cache or syntax error in `.py` | Check Output Log for `PythonAbilityRegistryLite` errors |
| All commands return `"ok": false` | Subsystem not initialized | Restart editor; check that `LLMEasyShellLite` module is in `Modules` array of `.uplugin` |
| `cat` returns empty for valid Actor | Actor not in current world | Verify with `ls /Level/Actors` first; start PIE if needed |

---

*LLMEasyShellLite v1.0.0-lite | YominUnreal | Free*
