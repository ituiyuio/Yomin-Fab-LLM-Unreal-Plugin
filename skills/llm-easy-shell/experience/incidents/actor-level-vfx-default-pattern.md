---
name: actor-level-vfx-default-pattern
description: Actor-level NiagaraSystem TObjectPtr properties need ConstructorHelpers default in constructor to ensure runtime availability
type: reference
originSessionId: 1b8ff173-ede8-4108-a56f-493e9c415d60
---
# Actor-Level VFX ObjectPtr 需要 ConstructorHelpers 默认值后备

## 模式

当在 C++ Actor 类中定义 `TObjectPtr<UNiagaraSystem>` 级别的 VFX 属性（如 LevelUpVFX、DeathVFX）时，**必须在构造函数中使用 `ConstructorHelpers::FObjectFinder` 设置默认值后备**。

## 问题现象

- BlueprintDefault 中属性值正确设置（如 `LevelUpVFX=NS_LevelUp`）
- 但 PIE 运行时实例显示属性为 `None`
- VFX 不播放，但代码有 null 检查所以不崩溃

## 根因分析

Actor 在 Blueprint 中spawn时：
1. C++ 构造函数运行（此时属性为 nullptr）
2. Blueprint properties 从 CDO 加载
3. 如果 Blueprint 的 construction script 或其他逻辑重置了属性，值变为 None

对比两种情况：
- `EnemyBase.DeathVFX`: 有 ConstructorHelpers 默认后备 ✓
- `SurvivorPlayerCharacter.LevelUpVFX`: 无 ConstructorHelpers 后备 ✗

## 正确模式（参考 EnemyBase.cpp）

```cpp
// EnemyBase.cpp 构造函数
static ConstructorHelpers::FObjectFinder<UNiagaraSystem> DeathVFXAsset(
 TEXT("/Game/Features/Survivor/VFX/NS_EnemyDeath/NS_EnemyDeath.NS_EnemyDeath"));
if (DeathVFXAsset.Succeeded())
{
 DeathVFX = DeathVFXAsset.Object;
}
```

```cpp
// SurvivorPlayerCharacter.cpp 构造函数（修复后）
static ConstructorHelpers::FObjectFinder<UNiagaraSystem> LevelUpVFXAsset(
 TEXT("/Game/Features/Survivor/VFX/NS_LevelUp/NS_LevelUp.NS_LevelUp"));
if (LevelUpVFXAsset.Succeeded())
{
 LevelUpVFX = LevelUpVFXAsset.Object;
}
```

## 为什么组件属性（如 WeaponComponent.AttackVFX）不需要？

组件通过 `CreateDefaultSubobject` 创建，其属性在组件构造时固定。但 Actor 级别的属性更容易被 Blueprint 覆盖或重置。

## 相关文件

- `Source/CODEO/Private/Survivor/Combat/EnemyBase.cpp` - DeathVFX 后备（正确模式）
- `Source/CODEO/Private/Survivor/Player/SurvivorPlayerCharacter.cpp` - LevelUpVFX 后备（已修复）
