---
name: llm-bpprop-debug
description: Debug and fix Blueprint CDO (Class Default Object) property issues via LLMEasyShell Python abilities. Use when Blueprint default values seem wrong, properties show as "None" unexpectedly, or `cat` command shows different values than expected. Triggers on: "Blueprint property", "CDO", "set/get blueprint default", "AttackRange=0", "HUDWidgetClass=None", property shows None but shouldn't.
---

# Blueprint CDO Property Debug Skill

## Problem Statement

Blueprint properties can show unexpected values when:
1. The Blueprint CDO has a different value than the C++ default
2. `cat` on runtime instance shows "None" for a ClassProperty
3. A float/int property shows 0.0 or 0 when it shouldn't
4. `bpprop get/set` fails with "Property not found"

## Diagnostic Workflow

### Step 1: Identify the Property Category

Run `python property list_props asset_path=/Game/.../BP_YourBlueprint` to see property visibility:

```
AttackRange (float) Protected   ← Can use python property set_prop
HUDWidgetClass (...) Protected  ← Can use python property set_prop
Stats (FPlayerStats) Public     ← May need different approach
```

### Step 2: Choose the Right Tool

| Tool | Use Case | Example |
|------|----------|---------|
| `cat /Game/...BP_X` | View runtime instance values | See current state |
| `python bpprop list` | List all properties on CDO | Find property name |
| `python bpprop get` | Get single CDO property | `bpprop get /Game/... AttackRange` |
| `python bpprop set` | Set single CDO property | `bpprop set /Game/... AttackRange 200` |
| `python property list_props` | View property visibility (Public/Protected/Private) | See Protected properties |
| `python property set_prop` | Set Protected/Private properties | `set_prop asset_path=... property_path=AttackRange value=200.0` |

### Step 3: Common Issues and Fixes

#### Issue: `bpprop get` returns "Property not found"

**Cause**: The property is on the parent class, not visible on Blueprint's generated class.

**Fix**: Use `python property get_prop` instead:
```bash
python property get_prop asset_path=/Game/.../BP_SurvivorPlayer property_path=AttackRange
```

#### Issue: `bpprop set` fails for float property

**Cause**: `bpprop` uses `get_editor_property()` which may not work for all property types.

**Fix**: Use `python property set_prop`:
```bash
python property set_prop asset_path=/Game/Features/Survivor/BP_SurvivorPlayer property_path=AttackRange value=200.0
```

#### Issue: ClassProperty shows "None" but isn't actually None

**Example**: `HUDWidgetClass: None` in `cat` output but Blueprint has it set.

**Cause**: The `cat` command resolves class paths for display. "None" means the Blueprint-visible value is unset (null).

**Fix**: Set it explicitly:
```bash
python property set_prop asset_path=/Game/.../BP_SurvivorPlayer property_path=HUDWidgetClass value=/Game/Features/Survivor/HUD/WBP_SurvivorHUD.WBP_SurvivorHUD_C
```

#### Issue: Property value 0.0 when C++ default is 200.0

**Cause**: Blueprint CDO overrides the C++ default with a different value.

**Fix**: 
1. Check C++ header: `AttackRange = 200.0f` in `.h`
2. Check Blueprint defaults: someone set it to 0 in Blueprint editor
3. Fix via Python:
```bash
python property set_prop asset_path=/Game/.../BP_SurvivorPlayer property_path=AttackRange value=200.0
```

## ClassProperty Path Format for set_prop

When setting a TSubclassOf or UClass* property, use the full Blueprint path:

```
# Correct format for Blueprint class:
value=/Game/Features/Survivor/HUD/WBP_SurvivorHUD.WBP_SurvivorHUD_C

# Correct format for C++ class:
value=/Script/CODEO.EnemyBase
```

## Verification After Fix

1. **Blueprint**: `python property get_prop asset_path=/Game/... property_path=YourProperty`
2. **Runtime**: `cat /Actor/YourActor0` to see runtime instance value
3. **Save**: `save /Game/.../BP_YourBlueprint`

## Real-World Example from CODEO Survivor Game

**Problem**: BP_SurvivorPlayer had AttackRange=0 (overriding C++ default of 200)

**Diagnosis**:
```bash
# Check C++ default - found AttackRange = 200.0f in .h
# Check runtime instance - showed AttackRange=0
# Check Blueprint list_props - showed AttackRange (float) Protected
```

**Fix**:
```bash
python property set_prop asset_path=/Game/Features/Survivor/BP_SurvivorPlayer property_path=AttackRange value=200.0
save /Game/Features/Survivor/BP_SurvivorPlayer
```

## Key Insight

> Blueprint CDO values **override** C++ defaults. A property shows 0 in the Blueprint editor means the Blueprint explicitly set it to 0 — even if C++ has a different default. Always check both the C++ header AND the Blueprint defaults when debugging property values.
