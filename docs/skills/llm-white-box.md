---
outline: [2, 3]
---

# LLM White Box

BSP level whiteboxing skill for LLM agents. Teaches the agent the **15
`whitebox ...` commands**, the **two-step rendering rule** that decides whether
a programmatically created brush is visible at all, and the **BSP pitfalls**
that silently produce wrong geometry (coplanar slivers, 10 cm origin snapping,
partial embedding).

> **Skill file:** [`skills/llm-white-box/SKILL.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-white-box/SKILL.md)
> · **Reference:** [`references/bsp-quickstart.md`](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-white-box/references/bsp-quickstart.md)

---

## When the Agent Loads It

The agent loads this skill when the user asks to:

- Block out a level: rooms, walls, doorways, stairs, platforms
- Create BSP brushes in the editor via shell commands
- Compose a composite structure (a room, a wall segment) out of primitives
- Query or transform existing `ABrush` actors in the persistent level
- Fix brushes that show **wireframe only** or have **no bounds (`=0`)**

**Triggers:** `whitebox`, `create-box`, `create-subtract-box`, `create-cylinder`,
`create-sphere`, `create-cone`, `create-stairs`, `build-room`,
`build-wall-segment`, `list-brushes`, `get-brush`, `delete-brush`,
`move-rotate`, `apply-default-material`, `rebuild-bsp-lighting`, `build-bsp`.

**Does NOT trigger** for: material / VFX / UI / StateTree / MetaSound work —
those have their own skills.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| UE 5.5 – 5.8 | Engine version (all four compile clean) |
| **LLM Easy Shell** or **LLM Easy Shell Lite** | The `whitebox ...` commands are dispatched through the shell's ability registry. Without one of them the plugin loads but there is no command surface. |
| **Editor must be running** | Commands RPC to a live editor process |
| `llm-shell` CLI | `skills/llm-easy-shell/llm-shell/llm-shell.exe` (Windows) / `llm-shell` (Linux/Mac) |

The engine plugins `EditorScriptingUtilities` and `PythonScriptPlugin` are
enabled automatically by the LLM White Box plugin descriptor.

---

## The Two-Step Rendering Rule

> ⚠️ **This is the single most important thing in the skill.** A brush created
> through code does **not** render until both steps have run.

| Step | Command | What breaks without it |
|------|---------|------------------------|
| 1. Material | `whitebox apply-default-material` | Per-poly material is `NULL` → the brush renders as **wireframe with no filled surfaces** |
| 2. BSP compile | `whitebox rebuild-bsp-lighting` | The BSP tree is never compiled → `Bounds=(0,0,0)` and the renderer **skips the brush entirely** |

Code-driven brush creation does **not** trigger the editor's BSP compile, and
the editor UI's shader-compile-on-save hook does **not** fire for API-created
brushes. `whitebox build-bsp` is the stronger variant: it re-runs every
brush's `BrushBuilder` first (repairing brushes whose `UModel` diverged from
the builder spec across a save/load cycle), then recompiles.

---

## The 15 Commands

```bash
LITE=skills/llm-easy-shell/llm-shell/llm-shell

# Create
$LITE -c "whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300"
$LITE -c "whitebox create-subtract-box --name=Door_01 --location=500,250,0 --size=200,100,300"
$LITE -c "whitebox create-cylinder --name=Pillar_01 --location=1000,1000,0 --radius=100 --height=500 --sides=12"
$LITE -c "whitebox create-sphere --name=Orb_01 --location=0,0,1000 --radius=300"
$LITE -c "whitebox create-cone --name=Tent_01 --location=0,0,0 --radius=400 --height=600 --sides=8"
$LITE -c "whitebox create-stairs --name=Stairs_01 --location=0,0,0 --steps=6 --step-size=600,400,60"

# Composite
$LITE -c "whitebox build-room --name=Room_01 --corner=0,0,0 --dimensions=2000,2000,500 --wall-thickness=50"
$LITE -c "whitebox build-wall-segment --start=0,0,0 --end=2000,0,0 --wall-size=50,300 --name=Fence_01"

# Query / Modify
$LITE -c "whitebox list-brushes"
$LITE -c "whitebox get-brush --name=Wall_01"
$LITE -c "whitebox move-rotate --name=Wall_01 --location=0,0,0 --yaw=45"
$LITE -c "whitebox delete-brush --name=Wall_01 --confirm=true"

# Render pipeline
$LITE -c "whitebox apply-default-material --name=Masonry"
$LITE -c "whitebox rebuild-bsp-lighting"
$LITE -c "whitebox build-bsp"
```

All arguments are `--key=value` flags; vectors are `X,Y,Z` in centimetres.
Every command returns a single-line JSON object.

---

## Python ability — the sample level

```bash
$LITE -c "python castle build"        # rebuild the whole sample level (idempotent)
$LITE -c "python castle stats"        # brush count, per-group breakdown
$LITE -c "python castle camera hero"  # hero / aerial / gate / keep / flank / dusk / river
$LITE -c "python castle atmosphere"   # rebuild only the sky dome, sun and skylight
$LITE -c "python castle save"         # force-save the level
```

`python castle build` regenerates a complete valley + medieval castle blockout
from source — terrain grid, curtain walls, corner towers, gatehouse with
portcullis, keep, hall, chapel, road, bridge, forest, wheat field, 24 far
mountains, a self-built gradient sky with a procedural cloud deck, and 7 camera
presets — deterministically, in one editor call.

---

## BSP Pitfalls (measured, not assumed)

| Pitfall | Rule |
|---------|------|
| **Coplanar contact is safe, partial embedding is fatal** | Two brushes meeting exactly on a face are fine. Once one is *partially embedded*, the BSP compiler cuts the seam into a sliver and the whole wall segment can silently vanish. Let the bigger volume's own planes trim the smaller one. |
| **Sliver faces are dropped without a warning** | `FBSPUtils::AddPoint` refuses slivers and the warning in `BSPUtils.cpp` is commented out. A wall can be in the level, have a material, pass a raycast — and not be on screen. Re-applying materials will not bring it back. |
| **Origins snap to a 10 cm grid, sizes do not** | `Floor((v+5)/10)*10`. A fractional segment length puts consecutive segments on different grid offsets, so the chain neither meets nor overlaps. Use segment lengths that are multiples of twice the grid size, start on the grid, and verify the seam arithmetic offline. |
| **Sloped-face budget** | BSP nodes past 255 vertices silently drop faces. Budget your sloped brushes; stair-stepped boxes cost zero extra sloped faces. |
| **Terrain on a regular grid** | An irregular triangle mesh slices grid planes into their own cells and produces a pile of slivers and slivers-on-slivers. |
| **Cap / parapet resting on a wall** | Let it touch exactly (cap bottom = wall top), do not sink it in. Embedding 10 cm cuts a 10 cm sliver out of the wall's outer face, and the sliver can exhaust the vertex budget — the entire wall face disappears. |
| **Never rely on the engine's SkyAtmosphere** | Its LUT renders black on some machines, which blows out auto-exposure. Build an unlit two-sided gradient dome instead, and delete any `SkyAtmosphere` actor so the two skies do not fight. |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Brushes render as wireframe only | `whitebox apply-default-material` |
| Brushes do not render at all (`Bounds=0`) | `whitebox rebuild-bsp-lighting` (or `build-bsp`) |
| A wall is invisible although it has a material and passes a raycast | Coplanar overlap → sliver dropped. Fix the geometry so the segments fit exactly. |
| `error="delete-brush requires --confirm=true"` | Add `--confirm=true` |
| `error="A brush named 'X' already exists in this level (it may still be pending deletion)"` | Use a different `--name`, or `delete-brush` the old one first — delete releases the name slot immediately. |
| `error="Editor world is null"` | Editor not fully loaded — wait for `Idle`, retry |
| `Unknown command: whitebox` after a Live Coding reload | Live Coding does not re-register the ability info JSON. Restart the editor (`llm-shell --restart`). |

---

*LLM White Box v1.0.0 | YominUnreal*
