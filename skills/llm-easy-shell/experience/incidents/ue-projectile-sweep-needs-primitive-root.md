---
name: ue-projectile-sweep-needs-primitive-root
description: UE Projectile 不命中真实根因 — Root 是 USceneComponent + SetActorLocation 默认 bSweep=false 双层 bug
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 7aed3dd6-b755-4164-96ef-ff884b20be22
---

UE 写自定义 Projectile actor 不用 ProjectileMovementComponent 时,两个隐性 bug 会让"100% 0 命中":

**Bug A**: `SetActorLocation(NewLoc)` 默认 `bSweep=false`, 引擎当作 teleport, 跨敌人不触发 `OnComponentBeginOverlap`。

**Bug B**: Root 是 `USceneComponent` (无碰撞)。即便 Bug A 修了改 `bSweep=true`, 引擎只 sweep root primitive, attached `UCapsuleComponent` 不参与 → 仍 0 命中。

**修复要双修**:
1. `CapsuleComp` 直接作为 Root: `SetRootComponent(CapsuleComp)`,Mesh attach 到 Capsule
2. Tick 中 `SetActorLocation(NewLoc, /*bSweep=*/true, &Hit)`
3. (额外) `CollisionObjectType = ECC_WorldDynamic`, 避免被自家 AutoAttack `SphereOverlapActors(ECC_Pawn)` 误识别为目标

**Why:** UE 文档没明说 sweep 只作用在 root primitive — 必须自己读 `PrimitiveComponent::MoveComponent` 源码才能发现。SetActorLocation 默认 sweep=false 也是反直觉。

**How to apply:** 写任何手动移动的 Actor (projectile/missile/grenade) 时, Root **必须**是带碰撞的 `UPrimitiveComponent` 子类 (Capsule/Sphere/Box), 移动调用必须 `bSweep=true`。直接用 `UProjectileMovementComponent` 更省事但要损失一些控制度。

**实战诊断**: 看到 [[survivor-game-state-2026-05-05]] 武器系统"看着对但 0 命中"+ `cat /Actor/BP_Projectile` 发现 projectile location 每帧不变 → 几乎 100% 是这两层 bug。

参考 commit: `5255fd6 fix(survivor): Projectile 0 命中根因 — SceneComponent-as-Root 让 sweep 失效`
