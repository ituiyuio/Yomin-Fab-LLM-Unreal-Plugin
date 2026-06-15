---
outline: [2, 3]
---

# LLM Easy Shell

Drive a **running UE editor** from the command line. 27 native commands + 25+ Python sub-commands — query scenes, modify actor properties, call blueprint functions, trigger Live Coding, take screenshots, all from your AI agent.

> **Skill file:** [`skills/llm-easy-shell/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-easy-shell/SKILL.md)

This is the **full read/write** version. For a read-only safety subset, see [LLM Easy Shell Lite →](./llm-easy-shell-lite).

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Inspect or modify a running editor session (actors, components, assets, properties)
- Spawn / move / delete actors in the level
- Read or write a blueprint / material / data table / curve
- Call a blueprint function on an actor or asset
- Trigger a Live Coding rebuild, restart the editor, undo / redo
- Take a PIE screenshot or capture the editor window
- Read editor logs, output log, message log

**Triggers:** `ls`, `cat`, `set`, `spawn`, `rm`, `cp`, `mv`, `call`, `save`, `new`, `addcomp`, `play`, `stop`, `pause`, `select`, `focus`, `undo`, `redo`, `find`, `info`, `help`, `livecoding`, `reload`, `lc`, `log`, `mkdir`, `discover`, `actor`, `editor`, `/Actor/`, `/Assets/`, `/Game/`, `/Level/`, `restart`, `msglog`, `gamestate`, `simulated`.

**Does NOT trigger** for: pure C++ coding (use `cpp-developer`), AngelScript scripting (use `unreal-as`), full project builds (use `builder`).

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM Easy Shell** plugin | Install from Fab or copy from this repo to `Plugins/` |
| **Editor must be running** | Commands are RPC over a TCP socket to a live editor process |
| `llm-shell` CLI | Build artifact: `skills/llm-easy-shell/llm-shell/llm-shell.exe` (Windows) / `llm-shell` (Linux/Mac) |
| LLMEasyShell plugin enabled | Edit → Plugins → AI → **LLM Easy Shell** → restart editor |

The skill body documents the full command set. The CLI binary is shipped inside the skill folder for convenience — the agent invokes it directly.

---

## CLI Quick Reference

```bash
LLM_SHELL=skills/llm-easy-shell/llm-shell/llm-shell

# Core commands
$LLM_SHELL -c "ls /Level/Actors"                  # List all actors
$LLM_SHELL -c "cat /Actor/MyPawn"                  # Inspect an actor
$LLM_SHELL -c "discover /Actor/MyPawn"             # List functions + properties
$LLM_SHELL -c "spawn PointLight at (0,0,100)"      # Spawn an actor
$LLM_SHELL -c "set /Actor/MyPawn Location (0,0,0)" # Set a property
$LLM_SHELL -c "call /Actor/MyPawn Jump"            # Call a function
$LLM_SHELL -c "save"                               # Save the level / project
$LLM_SHELL -c "info"                               # Editor state snapshot

# Editor control
$LLM_SHELL -c "play"
$LLM_SHELL -c "stop"
$LLM_SHELL -c "livecoding"                         # Trigger Live Coding rebuild
$LLM_SHELL -c "restart"                            # Full editor restart
```

### Flags for LLM Context Efficiency

| Flag | Effect |
|------|--------|
| `-q` / `--quiet` | Redirects stderr noise (connect / path warnings) to `llm-shell-quiet.log`. LLM stdout stays clean. |
| `-j` / `--json-only` | Unwraps the `output` / `result` field of the server response and emits pure JSON. LLM can parse directly. |

**Recommended combination** for almost all calls: `-q -j`. It turns a 17-line noisy response into 7 lines of pure JSON.

```bash
# Before: 17 lines, nested JSON, port warnings
./llm-shell.exe -c "gamestate"
# After: 7 lines of pure JSON, ready to parse
./llm-shell.exe -q -j -c "gamestate"
```

> `-j` only activates when the response has an `output` / `result` field. The `info` command emits top-level JSON directly and does not need `-j`. REPL mode is unaffected by `-q` (stderr stays human-readable).

---

## Path Conventions

| Path | Meaning |
|------|---------|
| `/Actor/{label}`         | An actor in the current level |
| `/Actor/{label}/{comp}`  | A component on that actor (alias-matched) |
| `/Game/{path}`           | An asset under `/Game/` (cat-able) |
| `/Assets/{path}`         | Alias of `/Game/{path}` |
| `/Class/{name}`          | A UClass (cat-able) |

```bash
find /Game *Glass*       # Search assets by glob
find Actor BP_Liquid*    # Search actors by name pattern
find Asset *Liquid*      # Alias
```

---

## Live Coding vs Restart

The skill includes a full decision tree. The short version:

| Scenario | Command | Why |
|----------|---------|-----|
| Modified a function body | `livecoding` | Hot-patches function instructions, no re-instantiation |
| Added / removed a UPROPERTY or UFUNCTION | usually `livecoding` | Live Coding handles most reflection-light changes |
| **Added a new C++ class** | `restart` | Live Coding cannot register new types |
| Modified UENUM / USTRUCT | `restart` | Reflection metadata changed |
| Changed inheritance hierarchy | `restart` | Re-instantiation needed |
| Uncertain | `restart` | The safe default |

`livecoding` triggers a compile and waits up to 120s. `restart` runs `save → shutdown → MSBuild → launch engine`.

---

## Python Sub-Commands

The `python` ability is special — its sub-commands come from the filesystem, not C++ registration. Any `.py` file in `Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/` (not prefixed with `_`) becomes a `python <name>` command.

The full version ships with **25+ sub-commands**:

| Command | Purpose |
|---------|---------|
| `python material`        | Material parameter get / set |
| `python blueprint`       | Blueprint structure analysis (variables / functions / components / inheritance) |
| `python asset`           | Asset management and dependency audit |
| `python vfx`             | Parse `.llmvfx` DSL files |
| `python scene`           | Scene actor queries (stats / lights / proximity / tags) |
| `python level`           | Level operations and spatial queries |
| `python umg`             | UMG / Widget Blueprint structure and properties |
| `python curve`           | Curve asset creation and keyframe editing |
| `python datatable`       | DataTable row read/write, CSV/JSON export |
| `python editor`          | Editor session control (viewport / PIE / CVars / **screenshot**) |
| `python gameplay`        | PIE game control and debug drawing |
| `python gameplaytag`     | GameplayTag trace and dependency query |
| `python gameplayability` | GameplayAbility / Effect / AttributeSet metadata |
| `python navigation`      | NavMesh OBJ export |
| `python posesearch`      | PoseSearch Schema / Database query |
| `python chooser`         | Unreal Chooser table debugging |
| `python property`        | UPROPERTY read/write (bypasses Python access restrictions) |
| `python bpcomp`          | Blueprint CDO component property read/write |
| `python bpprop`          | Blueprint CDO property read/write |
| `python reparent`        | Blueprint parent redefinition |
| `python perf`            | Performance metrics (frame timing / memory / UObject stats) |
| `python anim`            | Animation asset inspection and editing |
| `python reactive`        | Reactive event subscription and management |
| `python hd3d*`           | HD3D / post-process / scene setup |

The agent can also **author new Python abilities** by dropping a `.py` file into the abilities directory. No C++ rebuild required.

---

## Screenshot — Two Paths

| What you want to see | Path | Command |
|----------------------|------|---------|
| **Editor application window** (Outliner / Details / toolbars) | **Win32 path** (recommended) | `powershell -File scripts/editor_shot.ps1` |
| **PIE 3D render** (HUD / animations / dynamic lighting)        | PIE path             | `play` → `sleep 5` → `python editor screenshot source=pie` |
| Unsure | **Win32 path** (always works) | `powershell -File scripts/editor_shot.ps1` |

**Win32 path advantages:** works regardless of editor state (Idle / PIE / Compiling), no PIE required, captures full editor UI.

**PIE path advantages:** exact pixel path, deterministic, can show HUD / UMG / WebBrowser with `show_ui=true`.

Full reference: `skills/llm-easy-shell/references/llm-screenshot.md` and `skills/llm-easy-shell/references/editor-shot-win32.md`.

---

## Before Any Write — Run `info`

```bash
$LLM_SHELL -c "info"
```

Returns:

```json
{
  "project": "YourProject",
  "engineVersion": "5.7.0-xxx",
  "level": { "name": "MainLevel", "actorCount": 42 },
  "pieState": "Stopped",
  "livecoding": { "compiling": false, "phase": "idle", "elapsed": 0.0 },
  "hint": "editor idle"
}
```

**Rule:** Before `set` / `spawn` / `rm` / `cp` / `mv` / `call` / `save` / `new` / `addcomp`, confirm `livecoding.compiling == false`. If a compile is in progress, wait or call `livecoding --status` to check.

---

## Port

LLMEasyShell uses TCP port range **15151–15200** (50 ports). The default is 15151. **Lite** uses 15201–15250. They never overlap — you can have both running side by side.

Port file: `llm-shell/.current_port`.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Actor not found` | `ls /Level/Actors` to see what's there |
| `Asset not found` | `ls /Assets` or `find /Game *` |
| `Function not found` | `discover <path> --funcs` to list available functions |
| Connection refused | The UE editor is not running — start it |
| Command timed out | After the timeout, call `info` — the response includes `editorState` for diagnosis |
| `find` returns "Unknown type: /X" | Use `find /Game <pattern>` path form |
| `cat` does not show property values | Already fixed: shows all `BlueprintVisible` properties including struct values |

The skill ships with a deep troubleshooting index under `skills/llm-easy-shell/experience/` covering 21 lessons learned (path parsing, Python output quirks, `bpprop` ClassProperty traps, build/restart decision tree, screenshot pitfalls, etc.).

---

## Related Skills

- [**llm-easy-shell-lite** →](./llm-easy-shell-lite) — read-only subset for safe exploration.
- All four asset-authoring skills ([dynamic-ui](./llm-dynamic-ui), [material](./llm-material), [statetree](./llm-statetree), [metasound](./llm-metasound)) — LLMEasyShell is the runtime engine that can also *generate* those assets via the `ui` / `material` / `statetree` / `metasound` plugin abilities.
