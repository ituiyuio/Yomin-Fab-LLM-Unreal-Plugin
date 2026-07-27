---
name: v3-pr4-enum-property-default-required-2026-06-14
description: "UE 5.7 USTRUCT 字段若用 UENUM 类型 (非 int32/默认) 必须显式给默认值,否则 LogClass Error \"EnumProperty XXX is not initialized properly\" + editor TedsCore crash"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: ffb87414-bb20-42ea-9341-b1d8d7892638
---

**症状**: UE 5.7 editor 启动后立即崩 `EXCEPTION_ACCESS_VIOLATION reading address 0xffffffffffffffff`, CallStack 全是 TedsCore/TedsAlerts。
**Log 关键**: `LogClass: Error: EnumProperty FUpgradeData::Id is not initialized properly. Module:CODEO File:Public/Survivor/StatUpgradeComponent.h`

**根因**: UE 5.7 USTRUCT(BlueprintType) 里如果某个 UPROPERTY 是 UENUM 类型 (非 int32/非内置类型), **必须**给默认值, 否则 UHT reflection 失败 + engine 启动 TedsCore 崩。

**错误**:
```cpp
USTRUCT(BlueprintType)
struct FUpgradeData {
 UPROPERTY(EditAnywhere, BlueprintReadWrite) EUpgradeId Id; // ❌ 编译过但启动崩
};
```

**正确**:
```cpp
USTRUCT(BlueprintType)
struct FUpgradeData {
 UPROPERTY(EditAnywhere, BlueprintReadWrite) EUpgradeId Id = EUpgradeId::Health; // ✅
};
```

**Why**: UE 5.7 UHT 反射时, enum property 没默认值会在 GenerateHeader 阶段标记为 "not initialized", CDO 构造时 try 写这个字段会触发断言, 但断言被 TedsCore 包了一层 catch 后变成 0xFFFFFFFFFFFFFFFF 访问违例 — 看起来像随机 TedsCore 崩, 实际是 upstream enum 反射初始化错误。

**How to apply**:
- 任何 USTRUCT(BlueprintType) 里 UENUM 字段必须有默认值 `= EMyEnum::Value`
- 之前 v2 / v3 早期 (LootItem, AchievementComponent) 我用 UENUM + 没默认值 + 没崩, 因为那些 enum 是 EAchievementId 在 UActorComponent 里直接用, USTRUCT 里没用过
- 写新 USTRUCT 时养成习惯: enum 字段加 `= EMyEnum::DefaultValue` 默认
- 诊断 "TedsCore 启动崩" 第一步: `grep "LogClass.*not initialized"` log 文件 (UE 5.7 reflection 错误有特殊模式)
- 修复走 Build.bat (skip livecoding 触发全 engine relink), 然后手动启动 editor, 不要 restart — restart 流程读 stale crash state 又崩
