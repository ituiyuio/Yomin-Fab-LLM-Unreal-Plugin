---
name: ue58-python-dataasset-creation-pitfalls
description: UE 5.8 Python DataAsset/FDataTableRow creation 5 real 踩坑 (DataAssetFactory + EPlayerCharacter + TMap EnumValue + set_editor_property PascalCase)
metadata: 
 node_type: memory
 type: reference
 originSessionId: 61d97c71-f67e-413a-894e-4c8dcea39be3
---

UE 5.8 Python DataAsset/asset creation 5 real 踩坑 (Task 1.5 commit 159e45c 实测, 跟 survivor-portrait-v1-2026-06-26 / hd2d-sorceress-commit-pattern 模式一致):

1. **DataAssetFactory.data_asset_class → set_editor_property("DataAssetClass", ...)**
 - `factory.data_asset_class = unreal.CharacterVFXDataAsset` ❌ AttributeError (no such Python attr)
 - `factory.set_editor_property("DataAssetClass", unreal.CharacterVFXDataAsset)` ✅ PascalCase editor property 名
 - Ponytail: factory Python attr 跟 editor property 名不一定一致, 走 set_editor_property 是更稳 path

2. **EPlayerCharacter exposed as unreal.PlayerCharacter (no E prefix)**
 - `unreal.EPlayerCharacter` ❌ AttributeError
 - `unreal.PlayerCharacter` ✅ (UE Python auto-strip E prefix from UENUM names)
 - Ponytail: enum class name (UE C++) → Python expose 是 strip E + lowercase first letter (standard convention)

3. **SCREAMING_SNAKE_CASE for enum values**
 - `unreal.PlayerCharacter.SakuraMiko` ❌
 - `unreal.PlayerCharacter.SAKURA_MIKO` ✅
 - Ponytail: UE UENUM UMETA DisplayName 是 human-readable, Python expose 走 UENUM identifier = SCREAMING_SNAKE_CASE

4. **TMap keys must be EnumValue objects (not int / str)**
 - `cfgs[0] = struct` ❌ silently fails
 - `cfgs["Warrior"] = struct` ❌ silently fails
 - `cfgs[unreal.PlayerCharacter.WARRIOR] = struct` ✅
 - Ponytail: UE TMap<EnumKey, V> 必须用 EnumValue object 当 key, int/str 不报错但 silently 不填

5. **`int(unreal.PlayerCharacter.X)` cast fails**
 - `int(unreal.PlayerCharacter.WARRIOR)` ❌ "Cannot create instances of enum types"
 - `unreal.PlayerCharacter.WARRIOR` 直接传 ✅ (跟 #4 同根: enum 是 type, 不是 instance)
 - Ponytail: UE enum value object 不可 int() cast, 必须用 Unreal 名

**Verify path (跟 portrait / sorceress 模式):**
- 1 个 use-once Python ability (e.g., `create_character_vfx_dataasset.py`) → 跑通 → self-delete (跟 import_character_portraits.py 模式一致)
- binary verify: `grep -aoE "NS_[A-Za-z]+_[A-Za-z]+" path/to/asset.uasset | sort -u` 找 24 ref 字符串

**Why:** UE 5.8 strict mode + Python reflection 的 5 个 corner case, 任何 DataAsset / FDataTableRow / TMap<EnumKey> 创建任务都会遇到。Memory 1 次写 + 多次复用 (跟 continuesg-session-loop-pattern 同样 rerun-safe pattern)。

**How to apply:** 任何 UE Python ability 创建 DataAsset / FDataTableRow / TMap<EnumKey> 资产前必读本 memory, 5 踩坑 0 时间浪费。

**Related:** [[gensokyo-characters-portrait-v12-2026-06-26]] (LLMDynamicUI overwrite + ForceDeleteObjects 模式) + [[survivor-portrait-v1-2026-06-26]] (Python ability 一次性 use-once 模式)
