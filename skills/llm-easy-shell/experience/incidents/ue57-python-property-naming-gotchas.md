---
name: ue57-python-property-naming-gotchas
description: UE 5.7 Python API property name gotchas hit on Epic lighting preset (enable_volumetric_fog / bloom_tint FColor)
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 72fdc994-e247-4286-957b-7f45b3379f41
---

UE 5.7 Python `set_editor_property()` + `get_editor_property()` use a different naming than what's in the editor Details panel. Three traps hit during 2026-06-01 `apply_epic_volume`:

**Trap 1 — `b` prefix + snake_case mismatch**
- C++ property: `bEnableVolumetricFog` → editor "Enable Volumetric Fog"
- UE5.7 Python correct name: `enable_volumetric_fog` (NOT `volumetric_fog`, NOT `b_enable_volumetric_fog`)
- Failure mode: `Failed to find property 'volumetric_fog' for attribute 'volumetric_fog'`
- Fix: when name doesn't work, `dir(component)` to enumerate actual Python attribute names. Properties exist as `snake_case` with `b` prefix stripped.

**Trap 2 — FColor vs FLinearColor color fields**
- `DirectionalLightComponent.BloomTint` is `FColor` (0-255 ints), not `FLinearColor` (0-1 floats)
- Sending `unreal.LinearColor(1.0, 0.85, 0.6)` errors: `Cannot nativize 'LinearColor' as 'Color'`
- Fix: `unreal.Color(255, 217, 153, 255)` (8-bit ints, gold tint)
- Heuristic: if editor shows a "color picker" without HDR slider, it's FColor; if it has "Intensity" or HDR, it's FLinearColor. Light-related tints (BloomTint, etc.) are often FColor.

**Trap 3 — `MaterialInstanceDynamic.create()` removed in UE 5.7**
- Old: `unreal.MaterialInstanceDynamic.create(mat_asset, None)` — AttributeError in 5.7
- New: `unreal.MaterialEditingLibrary.create_material_instance(mat_asset)` works
- Workaround: `unreal.new_object(unreal.MaterialInstanceDynamic)` if MEL fails

**Why:** These trip the agent repeatedly because they're not in any single doc; only UE source + a working build reveals them. When a property set silently fails, ALWAYS `dir()` it first.

**How to apply:** Before writing property setters in `apply_*` style Python abilities, add a `_introspect_<component>` debug command that `dir()`s the component and `unreal.log()`s all relevant props. This saved 3 iterations on the epic_volume preset.
