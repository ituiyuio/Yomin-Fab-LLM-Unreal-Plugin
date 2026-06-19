---
outline: [2, 3]
---

# LLM Easy Shell

TCP shell interface for driving the Unreal Editor from any external client
(LLM agent loop, CLI, test harness). One-line commands in, JSON out — no UE
editor knowledge required.

**Quick value:** 35+ editor commands · 25+ built-in Python abilities · TCP
server on ports 15151–15200 · works alongside any LLM agent framework.

> 🎯 **For a minimal-dependency, read-only variant**, see
> [LLM Easy Shell Lite](../llm-easy-shell-lite/) (9 commands, 2 engine plugin
> dependencies, free).

---

## Core Features

- **Scene read/write** — List, view, spawn, delete, move, rename actors and components
- **Property reflection** — `set` / `cat` over any UObject, struct, or asset property
- **Asset operations** — Browse, create, copy, delete, save assets via `/Assets/...` paths
- **Function dispatch** — `call` any reflected `UFUNCTION` on actor or component
- **PIE control** — `play`, `stop`, `pause`, `gamestate`, `select`, `focus`
- **Live Coding** — `livecoding` / `lc` / `reload`, `--restart` editor with crash detection
- **Logs** — Editor log, error log, compile log, Niagara validation messages
- **UI introspection** — `uitree` / `uifind` / `uiinfo` / `uipress` / `uitype` / `uishot`
- **Ability framework** — Plugins register C++ commands at startup (auto-discovered)
- **PyAbility framework** — Drop a `.py` into `PyAbilities/.../abilities/` to register a command
- **TCP server** — Plain text in / JSON out, ports 15151–15200
- **Multi-platform** — Win64, Mac, Linux (Live Coding subcommand: Windows only)

## Quick Preview

```bash
# Agent loop — one line per action
> info
{"ok":true,"project":"MyGame","engine":"5.7.4","pie":"stopped","port":15151}

> spawn /Game/Blueprints/BP_Enemy at 100,200,50
{"ok":true,"actor":"/Actor/BP_Enemy_C_42"}

> set /Actor/BP_Enemy_C_42.Health=200
{"ok":true}

> call /Actor/BP_Enemy_C_42.SetActive true
{"ok":true,"result":"activated"}

> uishot
{"ok":true,"file":"Saved/Screenshots/2026-06-15.png"}
```

Send a one-line command → Get a one-line JSON response. The agent loop never
stalls.

---

## Technical Information

**Features:** 35+ editor commands (scene read/write, asset read/write,
property/function discovery, PIE control, Live Coding, logs, UI
introspection, screenshots), TCP server on ports 15151–15200, Ability
framework for plugin-registered C++ commands, PyAbility framework for
`.py`-defined commands, 25+ built-in Python abilities, command trace
logging.

**Code Modules:** LLMEasyShell (Editor)

**Number of Blueprints:** 0

**Number of C++ Classes:** ~115

**Network Replicated:** No

**Supported Development Platforms:** Windows: Yes, Mac: Yes, Linux: Yes

**Supported Target Build Platforms:** Windows, Mac, Linux

**Documentation Link:** [Documentation.md in plugin folder](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/tree/main/Plugins/LLMEasyShell/Documentation.md)

**Example Project:** *(see the GitHub repo's `Plugins/LLMEasyShell/` for
reference `.uplugin` / `Documentation.md` and the bundled Python ability
set)*

**Important/Additional Notes:** Editor-only plugin. For a minimal-dependency,
read-only variant, see [LLM Easy Shell Lite](../llm-easy-shell-lite/). UE 5.7+.

---

## Build Environment

### Required Host Plugins

The following engine plugins **must be enabled** in the host project before
compilation. They are declared in `LLMEasyShell.uplugin` and the host
`.uproject` must enable each one:

- **PythonScriptPlugin** — backs the PyAbility framework and Python-driven abilities (`python <name> ...`)
- **GameplayAbilities** — required by built-in abilities that introspect the Gameplay Ability System
- **GameplayTagsEditor** — editor-side gameplay tag inspection
- **EnhancedInput** — input mapping queries via `discover` / `cat`
- **PoseSearch** — Motion Matching database introspection
- **Chooser** — Chooser table introspection
- **StructUtils** — runtime struct property reflection
- **Niagara** — VFX introspection + validation message capture
- **EditorScriptingUtilities** — asset registry and editor scripting helpers

### Verifying a Clean Build

```bash
cd "/c/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles"
./RunUAT.bat BuildPlugin \
  -plugin="D:/path/to/LLMEasyShell.uplugin" \
  -package="D:/Temp/LLMEasyShell" \
  -platform=Win64 \
  -configuration=Development \
  -rocket
```

The `-rocket` flag enables Epic's IWYU + ABI-strict build configuration,
matching the Fab submission environment. Confirm zero errors and zero
consequential warnings (deprecation warnings such as `C4996` are treated as
errors by marketplace scanners).

### UE Version Compatibility

- **Minimum:** UE 5.7 (`EngineVersion: "5.7.0"` in `.uplugin`)
- **Tested:** UE 5.7.4

---

## Command Reference (35+ commands)

### Scene

| Command | Description |
|---------|-------------|
| `ls /Level/Actors` | List Actors in current level |
| `cat /Actor/{name}` | View Actor / component / asset details |
| `spawn /Game/.../BP_Actor` | Spawn actor (class path) |
| `rm /Actor/{name}` | Delete actor |
| `mv /Actor/{name} 100,200,50` | Move (Location only) |
| `cp /Actor/{src} /Actor/{dst}` | Clone actor |

### Property / Function

| Command | Description |
|---------|-------------|
| `set /Actor/{name}.Property=Value` | Set any reflected property |
| `call /Actor/{name}.Function arg1` | Call any UFUNCTION |
| `addcomp /Actor/{name} TypeName` | Add component |
| `discover /Actor/{name} --funcs` | List available functions |
| `discover /Actor/{name} --props` | List properties |

### Assets

| Command | Description |
|---------|-------------|
| `ls /Assets/` | Browse asset registry |
| `cat /Assets/.../Asset.Asset` | View asset properties |
| `new /Assets/.../Asset.Asset Class` | Create new asset |
| `cp /Assets/A.A /Assets/B.B` | Duplicate asset |
| `mv /Assets/A.A /Assets/B.B` | Rename / move asset |
| `rm /Assets/.../Asset.Asset` | Delete asset |
| `save /Assets/.../Asset.Asset` | Save modified asset |
| `mkdir /Assets/Folder` | Create asset folder |

### Search / Info

| Command | Description |
|---------|-------------|
| `find Actor {pattern}` | Search Actors by name |
| `find Asset {pattern}` | Search assets by name |
| `find /Game {pattern}` | Search assets by path |
| `info` | Project + editor + PIE state |
| `gamestate` | PIE game state (wave / health / gold / ...) |
| `help` | List all commands |

### Editor Control

| Command | Description |
|---------|-------------|
| `play` | Start PIE |
| `stop` | Stop PIE |
| `pause` | Pause / resume PIE |
| `select /Actor/{name}` | Select Actor in viewport |
| `focus /Actor/{name}` | Focus camera on Actor |
| `undo` / `redo` | Editor undo / redo |
| `save` | Save the level |

### Live Coding / Restart

| Command | Description |
|---------|-------------|
| `livecoding` / `lc` / `reload` | Trigger Live Coding compile |
| `log --compile` | Last Live Coding compile log |
| `log --restart` | Restart editor with crash detection |

### Logs

| Command | Description |
|---------|-------------|
| `log --errors` | Editor error log |
| `msglog --niagara` | Niagara validation messages |
| `livelog` | Tail current editor log |

### UI Introspection

| Command | Description |
|---------|-------------|
| `uitree` | Dump current UMG widget tree |
| `uifind {pattern}` | Find UMG widget by name |
| `uiinfo /Widget/{name}` | Inspect widget properties |
| `uipress /Widget/{name}` | Simulate click on a button |
| `uitype /Widget/{name} "text"` | Simulate text input |
| `uishot` | Slate composite screenshot |

### Python Abilities

| Command | Description |
|---------|-------------|
| `python {name} {args...}` | Invoke any PyAbility |
| `python reload` | Rescan abilities/ and clear Python module cache |

---

## Python Abilities (25+ built-in)

LLMEasyShell ships with a reference set of Python abilities in
`PyAbilities/LLMShellAbilities/abilities/`. Each ability is a standalone
`.py` module that registers one or more `python <name>` subcommands.

Drop your own `.py` into the `abilities/` folder, restart the editor (or run
`python reload`), and the ability becomes invocable as `python <name>`.

| Category | Abilities |
|----------|-----------|
| Asset / blueprint | `asset`, `blueprint`, `bpcomp`, `bpprop`, `reparent` |
| Property / reflection | `property`, `reactive` |
| Gameplay | `gameplay`, `gameplayability`, `gameplaytag` |
| Animation | `anim` |
| Curves / tables | `curve`, `datatable`, `chooser` |
| Levels / scene | `level`, `scene`, `editor` |
| Material / VFX | `material`, `vfx`, `umg` |
| Pose / motion | `posesearch` |
| Navigation | `navigation` |
| Performance | `perf` |
| HD3D demo set | `hd3d`, `hd3dpostprocess`, `hd3dscene` |

### Authoring a New Python Ability

```python
# PyAbilities/LLMShellAbilities/abilities/my_ability.py
from ._base import PyAbilityBase

class MyAbility(PyAbilityBase):
    name = "my_ability"
    description = "Does something useful"

    def invoke(self, args):
        # your logic here
        return {"ok": True, "result": "..."}

# Auto-register on import
ABILITY = MyAbility()
```

---

## TCP Protocol

The TCP server speaks a minimal text protocol.

### Request

Plain ASCII command terminated by `\n`:

```
info
ls /Level/Actors
set /Actor/MyActor.Location=100,200,50
python bpprop set BP_Hero.AttackRange=1200
```

### Response

Each command returns a **single-line JSON object** terminated by `\n`:

| Key | Type | Meaning |
|-----|------|---------|
| `ok` | bool | Success / failure |
| `result` | any | Command-specific payload |
| `error` | string | Human-readable error message (only if `ok=false`) |
| `trace` | string | Optional command trace id for debugging |

```json
{"ok": true, "result": {"actor_count": 12, "level": "Lvl_Main"}}
```

```json
{"ok": false, "error": "Actor /Actor/MyActor not found"}
```

### Port Allocation

The listener binds to the **first free port** in `15151–15200`. The chosen
port is logged at editor startup and recorded in
`Saved/LLMEasyShell/port.txt`.

---

## How to Use

1. Install the plugin to your project's `Plugins/` folder.
2. Enable the 9 engine plugins listed under **Required Host Plugins** in your
   project's Plugins browser.
3. Restart the editor. LLMEasyShell starts a TCP listener on the first free
   port in `15151–15200`.
4. Connect to the listener from any TCP client to issue commands:
   ```
   # Plain TCP — send "info\n" -> receive JSON
   # Or wire it up to an LLM agent that POSTs commands and parses JSON results
   ```
5. To author new C++ commands, derive from `ULLMEasyShellAbilityCommandObject`
   and register via the ability registry (auto-discovered at startup).
6. To author new Python commands, drop a `.py` into
   `PyAbilities/LLMShellAbilities/abilities/` and run `python reload`.

---

## Comparison: Easy Shell vs Lite

LLMEasyShell ships in two **independent** variants. They listen on disjoint
TCP port ranges and do not conflict at runtime. Install either or both.

| | LLMEasyShell (this plugin) | LLMEasyShell Lite |
|---|---|---|
| Purpose | Full read + write + automation | Read-only exploration |
| Commands | 35+ (read + write + control) | 9 (query only) |
| Python abilities | 25+ built-in abilities | Framework + 1 demo |
| Screenshots | Yes (PIE + Win32 paths) | No |
| Live Coding | Yes | No |
| TCP port | 15151–15200 | 15201–15250 |
| Engine plugin deps | 9 | 2 |
| CLI binary | `llm-shell.exe` | `llmshelllite.exe` |

---

## FAQ

**Q: Can I use LLMEasyShell on Mac or Linux?**
Yes — the editor module compiles on Win64, Mac, and Linux. The Live Coding
subcommand is Windows-only (UE constraint).

**Q: How is this different from LLMEasyShell Lite?**
Lite is a 9-command, read-only subset on ports 15201–15250 with only 2
engine plugin dependencies. Use Lite for safe exploration; use the full
plugin for write automation.

**Q: Can I register my own commands?**
Yes. C++ commands: derive from `ULLMEasyShellAbilityCommandObject`. Python
commands: drop a `.py` into `PyAbilities/LLMShellAbilities/abilities/`.

**Q: Is this safe to leave running in production?**
No — this is an editor automation tool. The TCP server exposes full editor
write capability. Disable it in shipping builds; never expose it to
untrusted networks.

---

*LLMEasyShell v1.0.0 | YominUnreal*
