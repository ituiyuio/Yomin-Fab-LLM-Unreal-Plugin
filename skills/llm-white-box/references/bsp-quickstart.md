# UE 5.5-5.8 BSP Quickstart for LLM Agents

## What is BSP?

Binary Space Partitioning (BSP) is UE's level geometry system from the Unreal 1 era. In UE 5.5-5.8 it's still functional but **deprecated for new content** (Epic recommends Static Mesh assets or GeometryScripting instead). LLMWhitebox uses BSP for **whitebox/blockout** only — quick rough level layouts before being replaced by production art.

## How brushes work in UE 5.5-5.8

- **`ABrush`**: a level actor (not a separate `.uasset`). Lives in the .umap.
- **`UBrushBuilder`**: describes the geometry (Box, Cylinder, Sphere, Cone). Subclass per shape. The engine ships `UCubeBuilder` / `UCylinderBuilder` / `UConeBuilder` in `Engine/Source/Editor/UnrealEd/Classes/Builders/`; **no sphere builder exists** — LLMWhitebox ships its own `USphereBrushBuilder`.
- **`UModel`**: the compiled BSP geometry (used internally for collision + rendering).
- **`BrushType`**: `Brush_Add` (additive) or `Brush_Subtract` (subtractive).

## Workflow

1. Spawn `ABrush` via `World->SpawnActor<ABrush>()`.
2. Create the right `UBrushBuilder` subclass (`UCubeBuilder`, `UCylinderBuilder`, etc.).
3. Set builder parameters (size, radius, sides, etc.).
4. Call `Builder->Build(World, Brush)` — this generates the polygons.
5. Assign `Brush->BrushBuilder = Builder` and `Brush->BrushType = BrushType`.
6. **Set per-polygon material** — `Brush->Brush->Polys->Element[i].Material = <UMaterialInterface>`. Without this, BSP renders wireframe only. UI-built brushes inherit a default from the editor; programmatic brushes must set it explicitly.
7. **Compile BSP tree** — call `GEditor->RebuildLevel(*Level)`. This converts the `UModel` data into the renderer's compiled geometry and populates `BrushComponent->Bounds`. Without this step, brushes have `Bounds=(0,0,0)` and the renderer skips them entirely.

## What LLMWhitebox does

- Wraps steps 1-5 in `ULLMWhiteboxBspLib` (15 static methods).
- Adds JSON parsing + dispatch in `ULLMWhiteboxCommandHandler`.
- Registers as a `llmwhitebox` ability in both LLMEasyShell + LLMEasyShellLite.
- **Step 6 (material)** is auto-applied inside `SpawnBrushWithBuilder` for brushes created post-commit `2d49edf` (2026-06-30). Pre-`2d49edf` brushes AND brushes loaded from a saved `.umap` need retroactive material via `ULLMWhiteboxBspLib::ApplyDefaultMaterial` (exposed as `whitebox apply-default-material`).
- **Step 7 (compile)** is NOT automatic. UE does NOT rebuild the BSP tree on level save/load for programmatic brushes — you must call `ULLMWhiteboxBspLib::RebuildBSPLighting` (exposed as `whitebox rebuild-bsp-lighting`) explicitly. The shader-compile-on-save hook that the editor UI uses is NOT triggered when brushes are created/loaded via API.

### Pair-with-creation rule

After any `create-*` / `build-room` / `build-wall-segment` batch, run **both**:
```bash
whitebox apply-default-material   # writes material to all polys
whitebox rebuild-bsp-lighting      # compiles the BSP tree
```

`apply-default-material` without `rebuild-bsp-lighting` = wireframe.
`rebuild-bsp-lighting` without `apply-default-material` = invisible.

## When to use BSP vs other tools

| Task | Use this | Why |
|---|---|---|
| Rough blockout of a room | LLMWhitebox `build-room` | 6 brushes, 1 command, fast |
| Decorative prop placement | Static Mesh actor (existing LLMEasyShell) | BSP for props is silly |
| Organic terrain | UE Landscape tool or GeometryScripting | BSP can't do curves |
| Production-ready mesh | GeometryScripting `bake-to-static-mesh` (future) | BSP is deprecated for shipping |
| Modify an imported .uasset | UE Modeling Mode (interactive) or GeometryScripting | BSP can't edit existing meshes |
