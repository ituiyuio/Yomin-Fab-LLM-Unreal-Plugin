---
name: bp-cdo-debug-pattern-2026-05-19
description: Blueprint CDO property debugging pattern via LLMEasyShell python abilities
metadata: 
 node_type: memory
 type: reference
 originSessionId: f23ad300-6ebb-451e-9c4a-4eed076cae6c
---

# Blueprint CDO Property Debug Pattern (2026-05-19)

## Core Pattern

Blueprint CDO values **override** C++ defaults. `cat` runtime instance shows Blueprint values.

## Key Commands

| Problem | Command |
|---------|---------|
| Property shows 0 but C++ has default | `python property list_props asset_path=/Game/.../BP_X` - check Protected |
| Set Protected float property | `python property set_prop asset_path=... property_path=AttackRange value=200.0` |
| Set ClassProperty (TSubclassOf) | `python property set_prop asset_path=... property_path=HUDWidgetClass value=/Game/.../WBP_C.WBP_C_C` |
| Verify change | `python property get_prop asset_path=... property_path=AttackRange` |
| Save blueprint | `save /Game/.../BP_X` |

## Key Insight

A property showing "None" in `cat` output means the Blueprint-visible value is null, not that it can't be resolved. Always use `python property list_props` to see Protected vs Public visibility.

## Related Memory
- [[llmeasy-shell-bpprop-classproperty-bugs.md]] - Previous bpprop bugs
