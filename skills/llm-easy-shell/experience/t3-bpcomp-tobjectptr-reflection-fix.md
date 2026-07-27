---
name: t3-bpcomp-tobjectptr-reflection-fix
description: "T3 fix (2026-06-11) — ULLMEasyShellPropertyLib::ResolveBlueprintObjectProperty UFUNCTION 让 bpcomp ability 访问 C++ TObjectPtr 字段 (BP 组件的非 scene C++ 属性)"
metadata:
 node_type: memory
 type: bug
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# T3: bpcomp C++ TObjectPtr 反射修复

## 问题
Survivor 游戏的 `BP_EnemyBase`/`BP_SurvivorPlayer` 有 `TObjectPtr<UWeaponBaseComponent> WeaponComponent` 这样的 C++ UPROPERTY。Python `bpcomp` ability 的 `_get_component_by_name` 走 `cdo.get_components()` 路径(只返 `USceneComponent` 子类)和 `getattr` fallback(返 TObjectPtr wrapper,无法 introspect/用于 property access),无法访问这些非 scene 的 C++ TObjectPtr 属性,卡在 "Component not found"。

## 修复

### 1. C++ 端 — `ULLMEasyShellPropertyLib::ResolveBlueprintObjectProperty`

**新加的 UFUNCTION** (file: `Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellPropertyLib.h` + `.cpp`):

```cpp
UFUNCTION(BlueprintCallable, Category = "LLMEasyShell|Property")
static UObject* ResolveBlueprintObjectProperty(const FString& BlueprintPath, const FString& PropertyName);
```

实现走 FProperty reflection:
1. `StaticLoadObject` 拿到 BP
2. `BP->GeneratedClass->GetDefaultObject()` 拿 CDO
3. `CDO->GetClass()->FindPropertyByName(FName(*PropertyName))` 找 property
4. `CastField<FObjectPropertyBase>(Prop)` 检查是不是 Object property
5. `ObjProp->GetObjectPropertyValue(ObjProp->ContainerPtrToValuePtr<void>(CDO))` 拿真实 UObject

### 2. 桥接 pattern 选择

`ULLMEasyShellPropertyLib` 是 `UBlueprintFunctionLibrary`,已经用 `UFUNCTION(BlueprintCallable) static` 模式暴露给 Python(`unreal.LLMEasyShellPropertyLib.xxx()`)。这是 codebase **idiomatic** 模式,优于在 `LLMEasyShellReflection.cpp`(普通 C++ class,不是 function library)加 UFUNCTION。

### 3. Python 端 — `bpcomp.py::_get_component_by_name`

**C++ 路径作 FIRST attempt**(不是 fallback)：

```python
def _get_component_by_name(cdo, comp_name, bp_path=None):
 if bp_path:
 try:
 lib = unreal.LLMEasyShellPropertyLib
 obj = lib.resolve_blueprint_object_property(bp_path, comp_name)
 if obj and obj != cdo:
 return obj
 except Exception:
 pass
 # ... 旧 get_components + getattr fallback
```

`bp_path` 在 `bpcomp_get` / `bpcomp_set` 里通过 `asset_path` 透传。

## 验证 (2026-06-11, real PIE test)

启动 editor `UnrealEditor.exe CODEO.uproject -unattended -nullrhi` 后跑:

```bash
$ llm-shell -c "python bpcomp get /Game/Features/Survivor/BP_SurvivorPlayer own WeaponComponent BaseDamage"
{
 "success": true,
 "output": "[Blueprint CDO] WeaponComponent.BaseDamage = None"
}

$ llm-shell -c "python bpcomp get /Game/Features/Survivor/BP_SurvivorPlayer ASurvivorPlayerCharacter WeaponComponent BaseDamage"
{
 "success": true,
 "output": "[parent class ASurvivorPlayerCharacter] WeaponComponent.BaseDamage = None"
}
```

**T3 之前**: `Component not found: WeaponComponent`(`get_components` 不返 UActorComponent 子类 + TObjectPtr wrapper)。
**T3 之后**: C++ reflection 拿到 UObject,`Component found`。`BaseDamage=None` 是因为 `find_property_by_name` 在 Python 这层调的是 component class 而非 UObject 的 UClass — 这是 T3 范围外的 issue(已在 `bpcomp_set` 测试里暴露,pre-existing)。

## Build

```bash
# kill editor first to avoid Live Coding block
taskkill //F //IM UnrealEditor.exe
# build
"C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/Build.bat" \
 CODEOEditor Win64 Development -Project=D:/UnrealEngine/CODEO/CODEO.uproject \
 -WaitMutex -FromMsBuild -Module=LLMEasyShell
# Result: Succeeded (6 actions, 11s)
# Pre-existing Cast<UBlueprint>(ParentClass) warning — not from T3.
```

## 关键文件

- `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\Source\LLMEasyShell\Public\LLMEasyShellPropertyLib.h` — UFUNCTION 声明
- `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\Source\LLMEasyShell\Private\LLMEasyShellPropertyLib.cpp:680` — `ResolveBlueprintObjectProperty` 实现
- `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\PyAbilities\LLMShellAbilities\abilities\bpcomp.py:172` — Python 修复
- `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\PyAbilities\LLMShellAbilities\abilities\bpcomp.py:325,366` — `bpcomp_get` / `bpcomp_set` 透传 `bp_path=asset_path`

## 教训

1. **Bridge pattern**: UE 暴露 C++ helper 给 Python 走 `UBlueprintFunctionLibrary` + `UFUNCTION(BlueprintCallable) static`,不是 `LLMEasyShellReflection.cpp`。`unreal.LLMEasyShellPropertyLib.xxx()` 已经是 codebase 既有约定,跟它对齐。
2. **FProperty vs Python `getattr`**: Python `getattr(bp_cdo, 'WeaponComponent')` 在 UE 5.x TObjectPtr<UClass> UPROPERTY 上返 wrapper object,`obj.get_class()` 等方法都没用。唯一可靠路径是 C++ 端 `FObjectPropertyBase::GetObjectPropertyValue`。
3. **bpcomp 的 SCS 组件限制**: SCS scene components 不在 BP CDO 的 `get_components()` 里,`bpcomp get` 对它们是 no-op(应该用 `set /Game/BP_X#SpringArm/Prop Val` C++ 路径)。T3 没动这个,只解决 TObjectPtr 问题。
4. **Build 前要 kill editor**: `Build.bat` 报 "Unable to build while Live Coding is active",必须 `taskkill //F //IM UnrealEditor.exe`。

## Code Review 修复 (第二轮) — I1 容器安全

第二次 code review 发现 `FObjectPropertyBase` cast 太宽,会接受 `FArrayProperty`/`FMapProperty`/`FSetProperty` (容器 of UObject) — `GetObjectPropertyValue` 对容器会返回 reinterpret 后的 array 内部指针而非 UObject,调用会 crash。

修法: cast 改 `FObjectProperty` (hard UObject* / TObjectPtr<T> only, 拒绝 soft/weak/lazy/class/interface/container 变体)。

Commit: f96aa30
