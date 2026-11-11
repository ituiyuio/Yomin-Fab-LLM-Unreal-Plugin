---
outline: [2, 3]
---

# LLM White Box

> BSP level whiteboxing for LLM agents — **15 JSON-returning commands** that lay
> out real BSP geometry in the persistent level, plus a reproducible
> **castle-in-a-valley** sample generator.
> Needs **LLM Easy Shell** (or Lite) in the same project to expose the command
> surface.

**Quick value:** `create-box` / `create-subtract-box` / `create-cylinder` /
`create-sphere` / `create-cone` / `create-stairs` · `build-room` ·
`build-wall-segment` · named-group material filtering · BSP recompile ·
`python castle build` regenerates a 1040-brush blockout in one editor call ·
UE 5.5 / 5.6 / 5.7 / 5.8.

---

## Core Features

- **Real BSP geometry** — the output is native `ABrush` built with the engine's
  own `UBrushBuilder` family, so it saves into your `.umap`, lights with the BSP
  compiler, and stays editable by hand afterwards.
- **One-line commands, JSON answers** — every command returns a single-line
  JSON object, so an agent loop can act on the result without parsing prose.
- **Composite builders** — `build-room` emits 4 walls + floor + ceiling in one
  call; `build-wall-segment` lays a wall along any line and actually rotates it.
- **Named-group material filtering** — `apply-default-material --name=Masonry`
  re-materializes the whole `Masonry_*` group in one call, so a blockout can be
  re-coloured by category instead of brush by brush.
- **The two-step rendering rule, automated** — a brush without a per-poly
  material renders as wireframe; a brush without a compiled BSP tree has zero
  bounds and does not render at all. `apply-default-material` +
  `rebuild-bsp-lighting` are the hard pair; `build-bsp` does the stronger
  variant (re-runs every builder, then recompiles).
- **Safe by default** — `delete-brush` requires `--confirm=true`, and volume
  brushes (`NavMeshBoundsVolume`, `DefaultPhysicsVolume`, `PostProcessVolume`,
  …) are refused with an explanation, because UE derives them from `ABrush`
  too.
- **Zero compile-time coupling** — the plugin registers itself into LLMEasyShell
  or LLMEasyShell Lite at runtime by reflection. It compiles standalone; the
  shell is only needed at runtime to reach the commands.

---

## Quick Preview

```bash
# a wall
> whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300
{ "success": true, "name": "Wall_01", "brush_type": "additive", "builder": "CubeBuilder" }

# a doorway cut out of it
> whitebox create-subtract-box --name=Door_01 --location=500,250,0 --size=200,100,300

# a whole room
> whitebox build-room --name=Room_01 --corner=0,0,0 --dimensions=2000,2000,500 --wall-thickness=50

# make it visible — BOTH steps are required
> whitebox apply-default-material --name=Stone
> whitebox rebuild-bsp-lighting
```

Regenerate the bundled reference blockout with one editor call:

```bash
> python castle build
{ "success": true, "brush_count": 1040, "create_failures": [], "phase_errors": [] }
```

---

## Technical Information

**Features:** BSP brush creation (box / subtract box / cylinder / sphere / cone
/ stairs), one-shot room and wall-segment builders, brush query / transform /
delete, material assignment with group filtering, BSP recompile, plus a
deterministic Python sample-level generator and its procedural sky material
builder.

**Code Modules:** LLMWhitebox (Editor)

**Number of Blueprints:** 0

**Number of C++ Classes:** ~4

**Network Replicated:** No

**Supported Development Platforms:** Windows: Yes, Mac: Yes, Linux: Yes

**Supported Target Build Platforms:** Windows, Mac, Linux

**Documentation Link:** [Documentation.md](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-white-box/SKILL.md) in plugin folder

**Example Project:** The plugin ships a complete example —
`Content/Maps/Lvl_Sample_Castle.umap` (a 180 m × 180 m valley with a castle,
1040 BSP brushes, 19 material groups) plus the generator that rebuilds it:
`python castle build`. The brush/builder contract is also published as a
machine-readable schema at `Config/Schemas/BrushSchema.llmwhiteboxschema`.

**Important/Additional Notes:** Editor-only plugin. Uses UE 5.5/5.6/5.7/5.8
APIs — `ABrush` (`Engine/Brush.h`), `UBrushBuilder` and the `Builders/*` headers
from the engine's `UnrealEd` module. The shell commands are reached through
**LLM Easy Shell** or **LLM Easy Shell Lite** — the host project needs one of
them installed; this plugin itself has no compile-time dependency on either.
The engine plugins **EditorScriptingUtilities** and **PythonScriptPlugin** are
enabled automatically by this plugin.

---

## Build Environment

### Required Host Plugins

| Plugin | Why | Who enables it |
|--------|-----|----------------|
| **LLM Easy Shell** *or* **LLM Easy Shell Lite** | The `whitebox ...` commands are dispatched through the shell's ability registry. Without a shell installed the plugin still loads and the C++ API stays usable, but there is no command surface. | **You** — install one of the shell plugins in the host project. |
| EditorScriptingUtilities | `unreal.EditorAssetLibrary` — the Python side of the plugin (asset + material work). | This plugin, automatically. |
| PythonScriptPlugin | Loads the bundled Python abilities (the castle generator). | This plugin, automatically. |

### Module Dependencies

- Public: `Core`, `CoreUObject`, `Engine`, `EditorSubsystem`, `Json`,
  `JsonUtilities`
- Private: `Slate`, `SlateCore`, `InputCore`, `ToolMenus`
- Private, editor-only (`if (Target.bBuildEditor)`): `UnrealEd`,
  `EditorScriptingUtilities`

### Verifying a Clean Build

```bash
cd "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles"
./RunUAT.bat BuildPlugin -plugin="path/to/LLMWhitebox.uplugin" -package="path/to/output" -rocket
```

---

## Features

| Feature | Description |
|---------|-------------|
| Box / subtract box | `UCubeBuilder` brush, additive or subtractive (`BrushType`) |
| Cylinder / cone | `UCylinderBuilder` / `UConeBuilder` with a configurable side count |
| Sphere | Bundled `USphereBrushBuilder` (the engine ships no sphere builder) |
| Stairs | Composed flight of N stepped boxes, ascending along +Y |
| Room builder | One-shot 6-brush room: 4 walls + floor + ceiling |
| Wall segment | One wall along a line, rotated to match the start → end direction |
| Brush query | `list-brushes` / `get-brush` with a volume-aware class filter |
| Transform | `move-rotate` — location, rotation, scale |
| Delete | `delete-brush` behind a `--confirm=true` safety gate |
| Material | Per-poly material assignment, optionally filtered by a named group |
| BSP compile | `rebuild-bsp-lighting` and the stronger `build-bsp` |
| Sample level | `python castle build` — 1040 brushes, 19 material groups, sky dome, 24 far mountains |
| Schema | `Config/Schemas/BrushSchema.llmwhiteboxschema` — the machine-readable brush/builder contract |

---

## Command Reference (15 commands)

### Create

| Command | Description |
|---------|-------------|
| `whitebox create-box` | Spawn an `ABrush` built with `UCubeBuilder`. `--name`, `--location=X,Y,Z`, `--size=X,Y,Z`, `--brush-type=additive\|subtractive` |
| `whitebox create-subtract-box` | Same as `create-box` but `BrushType=Subtractive` — punches a hole |
| `whitebox create-cylinder` | `--name`, `--location`, `--radius`, `--height`, `--sides` |
| `whitebox create-sphere` | `--name`, `--location`, `--radius` |
| `whitebox create-cone` | `--name`, `--location`, `--radius`, `--height`, `--sides` |
| `whitebox create-stairs` | `--name`, `--location`, `--steps=N`, `--step-size=width,tread,rise` |

### Composite

| Command | Description |
|---------|-------------|
| `whitebox build-room` | 6 brushes in one call: `--name`, `--corner=X,Y,Z`, `--dimensions=X,Y,Z`, `--wall-thickness`, `--include-floor`, `--include-ceiling` |
| `whitebox build-wall-segment` | One wall along a line: `--start=X,Y,Z`, `--end=X,Y,Z`, `--wall-size=thickness,height`, `--name` |

### Query / Modify

| Command | Description |
|---------|-------------|
| `whitebox list-brushes` | List the BSP brushes of the persistent level. `--class-filter=Brush\|Volume\|<substring>` |
| `whitebox get-brush` | Full details of one brush: `--name` |
| `whitebox delete-brush` | Destroy a brush. `--name`, `--confirm=true` (required) |
| `whitebox move-rotate` | `--name`, `--location`, `--pitch`, `--yaw`, `--roll`, `--scale` |

### Render pipeline

| Command | Description |
|---------|-------------|
| `whitebox apply-default-material` | Assign a material. `--material=/Game/...`, `--name=BrushName` (a group name matches `NAME` plus every `NAME_*` brush) |
| `whitebox rebuild-bsp-lighting` | `GEditor->RebuildLevel` — compiles the BSP tree into renderable geometry |
| `whitebox build-bsp` | Re-runs every brush's `BrushBuilder` (repairing builders whose `UModel` diverged across a save/load cycle), then `RebuildLevel` |

---

## The Two-Step Rendering Rule

BSP brushes created through code do **not** render until two things have
happened:

1. **Material.** A brush whose per-poly material is `NULL` renders as a
   wireframe with no filled surfaces. `apply-default-material` writes the
   material to every polygon of the `UModel` *and* to the `BrushComponent` slot.
2. **BSP compile.** Code-driven brush creation does not trigger the editor's
   BSP compile. Without it the brush has correct `UModel` data but
   `Bounds=(0,0,0)` and does not render at all.

`build-bsp` does the stronger variant: it re-runs every brush's builder first,
then recompiles.

---

## Troubleshooting

### Brushes render as wireframe only

`Brush->Brush->Polys->Element[i].Material == NULL`. Fix with
`whitebox apply-default-material`.

### Brushes do not render at all

`Bounds=(0,0,0)` — the BSP tree has not been compiled into the renderer. Fix
with `whitebox rebuild-bsp-lighting`.

### A wall is in the level, has a material, passes a raycast, and is still invisible

Two brushes **coplanar and overlapping** are split by the BSP builder into a
sliver, and the sliver is silently dropped (`FBSPUtils::AddPoint` refuses it,
and the warning in `BSPUtils.cpp` is commented out). The face is gone, not the
state — re-applying materials or recompiling will not bring it back.

### Brush origin snapping

The editor snaps a brush's **origin** to a 10 cm grid
(`Floor((v+5)/10)*10`) but does **not** snap its size. When a segment length is
fractional, consecutive segments land on different grid offsets and the chain
neither meets nor overlaps. Pick segment lengths that are multiples of twice
the grid size and start on the grid, then verify the seam arithmetic offline
instead of by eye.

### `whitebox` returns "Unknown command" after a Live Coding reload

Live Coding recompiles the binary but does not re-register the ability info
JSON, so the cached command list in the shell subsystem stays stale. Restart
the editor (`llm-shell --restart`) to re-register.

### A brush name is reported as already in use

Either a brush with that name is still alive, or a previously destroyed brush
has not been garbage-collected yet. Use a different `--name`, or `delete-brush`
the old one first — delete renames the actor immediately, which releases the
name slot.

---

## How to Use

1. Copy the plugin into your project's `Plugins/` folder and enable it. The
   engine plugins `EditorScriptingUtilities` and `PythonScriptPlugin` are
   enabled automatically by the plugin descriptor.
2. Install **LLM Easy Shell** or **LLM Easy Shell Lite** in the same project.
3. Restart the editor. The plugin registers itself with the shell during
   `OnAllModuleLoadingPhasesComplete`.
4. Create geometry, then make it visible (both steps):
   ```
   whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300
   whitebox apply-default-material --name=Stone
   whitebox rebuild-bsp-lighting
   ```

The C++ API is also directly callable from Blueprint and Python:

```python
import unreal
result = unreal.LLMWhiteboxBspLib.create_box(
    unreal.Vector(0, 0, 0), unreal.Vector(1000, 500, 300), "Wall_01")
```

---

*LLM White Box v1.0.0 | YominUnreal*
