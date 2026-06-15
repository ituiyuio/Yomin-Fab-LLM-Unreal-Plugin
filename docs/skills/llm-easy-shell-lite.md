---
outline: [2, 3]
---

# LLM Easy Shell Lite

Read-only subset of [LLM Easy Shell →](./llm-easy-shell). 9 safe exploration commands, no writes, no PIE control, no Live Coding. The minimum you need to **look** at a running UE editor without risk.

> **Skill file:** [`skills/llm-easy-shell-lite/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-easy-shell-lite/SKILL.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- List actors in the current level
- Inspect an actor / component / asset (read-only)
- Search for actors or assets by name pattern
- Discover an actor's available functions and properties (before calling)
- Check editor state (`info`, `pieState`, `livecoding`)
- Read editor error log or Niagara validation messages
- Query PIE runtime state (`gamestate`)

**Triggers:** `ls`, `cat`, `find`, `discover`, `info`, `help`, `gamestate`, `log`, `msglog`, `/Actor/`, `/Assets/`, `/Game/`, `/Level/`.

**Does NOT trigger** for: any write operation (`set` / `spawn` / `rm` / `cp` / `mv` / `call` / `save` / `new` / `addcomp` / `play` / `stop` / `pause` / `undo` / `redo` / `reload`), screenshots, C++ coding, AngelScript scripting.

For any of the above, the agent should load the full [LLM Easy Shell →](./llm-easy-shell) skill.

---

## When to Use Lite vs Full

| Scenario | Use |
|----------|-----|
| "What actors are in this level?" | **Lite** ✅ |
| "What does this actor's material look like in PIE?" | **Lite** + screenshot path on **Full** (Lite has no screenshot) |
| "Move this light to the corner" | **Full** |
| "Discover the function signature before I decide whether to call it" | **Lite** ✅ |
| "I want a safe read-only sandbox" | **Lite** ✅ |
| "I need the full Python sub-command suite" | **Full** |

**Rule of thumb:** default to Lite for *exploration*; switch to Full when the user requests a *change*.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.7+ | Engine version |
| **LLM Easy Shell Lite** plugin | Install from Fab or copy from this repo to `Plugins/` |
| **Editor must be running** | Same as Full — commands RPC to a live editor process |
| `llm-shell` CLI | Build artifact: `skills/llm-easy-shell-lite/llm-shell/llm-shell.exe` (Windows) / `llm-shell` (Linux/Mac) |
| LLMEasyShellLite plugin enabled | Edit → Plugins → AI → **LLM Easy Shell Lite** → restart editor |

---

## The 9 Read-Only Commands

```bash
LITE=skills/llm-easy-shell-lite/llm-shell/llm-shell

# Browsing
$LITE -c "ls /Level/Actors"                    # List actors
$LITE -c "ls /Assets"                          # List asset directories
$LITE -c "cat /Actor/MyPawn"                   # Inspect an actor
$LITE -c "cat /Actor/MyPawn/MyComponent"       # Inspect a component

# Search
$LITE -c "find Actor BP_Liquid*"               # Search actors by name
$LITE -c "find Asset *Liquid*"                 # Search assets by name
$LITE -c "find /Game *Glass*"                  # Search by path glob
$LITE -c "find /Assets *Glass*"                # Same, /Assets alias

# Discover (call these BEFORE you switch to Full to set/call)
$LITE -c "discover /Actor/MyPawn --funcs"      # Available functions
$LITE -c "discover /Actor/MyPawn --props"      # Available properties

# Status
$LITE -c "info"                                # Project + editor + PIE state
$LITE -c "help"                                # List all commands
$LITE -c "gamestate"                           # PIE wave / health / gold / enemies
$LITE -c "log --errors"                        # Editor error log
$LITE -c "msglog --niagara"                    # Niagara validation messages
```

> **Convention:** the recommended workflow is — *discover* with Lite, then *act* with Full. Lite gives the agent a "dry run" view that prevents typos in the eventual `set` / `call`.

---

## Path Conventions

| Path | Meaning |
|------|---------|
| `/Actor/{label}`         | An actor in the current level |
| `/Actor/{label}/{comp}`  | A component on that actor (alias-matched) |
| `/Game/{path}`           | An asset under `/Game/` |
| `/Assets/{path}`         | Alias of `/Game/{path}` |
| `/Class/{name}`          | A UClass |

---

## Plugin Abilities (Limited Subset)

The four LLM series plugins also register read-only sub-commands that Lite can see via `help`:

| Ability | Source plugin | Read-only sub-commands |
|---------|---------------|------------------------|
| `llmstatetree` | LLMStateTree    | `inspect`, `list-types`, `describe-type`, `export-schema`, `export` |
| `ui`           | LLMDynamicUI    | `inspect`, `list-types`, `export-schema`, `export` |
| `material`     | LLMMaterial     | `inspect`, `list-types`, `describe-type`, `export-schema`, `export` |

These are safe to use with Lite. Sub-commands that *write* (`generate`, `copy`, `delete`, `compile`) technically work because Lite shares the handler instance with those plugins — **use them with caution and accept the risk** that they violate the read-only contract.

---

## What Lite Does NOT Have

- ❌ Any write operation (`set` / `spawn` / `rm` / `cp` / `mv` / `call` / `save` / `new` / `addcomp`)
- ❌ Any PIE control (`play` / `stop` / `pause`)
- ❌ `livecoding` / `restart` compile cycle
- ❌ `log --compile` (compile log capture — needs Full or an Advanced skill)
- ❌ Screenshots (PIE path or Win32 path)
- ❌ `-q` / `-j` CLI flags (Lite does not implement them — read stdout directly)
- ❌ `python <name>` 25+ sub-commands

For any of these, switch to [LLM Easy Shell →](./llm-easy-shell).

---

## Port

Lite uses TCP port range **15201–15250** (50 ports). The default is 15201.

Full uses 15151–15200. **The two ranges never overlap** — you can run Lite and Full side by side on the same machine without coordinating ports.

Port file: `llm-shell/.current_port`.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | UE editor is not running — start it |
| `Command not found: <X>` | `<X>` is a write command Lite does not implement. Use Full. |
| Output is noisier than expected | Lite does not implement `-q` / `-j`. Pipe through `jq` or read stdout directly. |
| A plugin's write sub-command worked anyway | Lite shares the handler with the plugin; Lite's "read-only" is enforced at the skill's command list, not at the C++ level. Treat it as advisory. |

---

## Related Skills

- [**llm-easy-shell** →](./llm-easy-shell) — full read/write version.
- All four asset-authoring skills ([dynamic-ui](./llm-dynamic-ui), [material](./llm-material), [statetree](./llm-statetree), [metasound](./llm-metasound)) — use Lite to inspect existing assets, then the asset-authoring skill to author new ones.
