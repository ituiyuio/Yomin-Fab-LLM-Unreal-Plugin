---
name: bp-parentclass-mismatch-2026-06-12
description: UE5.7 蓝图父类错配的诊断与 C++ fallback 模式 + Python reparent 反射限制
metadata: 
 node_type: memory
 type: project
 originSessionId: 67d12361-0643-4190-ad5b-fd0124907bc5
---

UE 蓝图资产创建时如果用了默认父类(Actor),后续 C++ 父类改成 UPrimaryDataAsset 等,蓝图 reparent 经常失败(BP asset 不会自动同步)。结果:
- `Cast<UFixedParentClass>(BP.GetAsset())` 永远 nullptr
- 数据资产/组件的所有字段失效,代码走到 fallback 硬编码默认值

**诊断命令**:
```bash
python blueprint bp_summary <path> asset_path=<path>
# 输出: "Class: BP_X_C\nParent: Actor" ← bug 标志
```

**C++ 兜底模式**(USurvivorStatsConfig::Get 案例):
```cpp
if (USurvivorStatsConfig* TypedAsset = Cast<USurvivorStatsConfig>(AssetData.GetAsset()))
{
 return TypedAsset;
}
UE_LOG(LogTemp, Warning, TEXT("BP cast failed (likely wrong parent class). Falling back to transient default."));
return NewObject<USurvivorStatsConfig>(
 GetTransientPackage(), USurvivorStatsConfig::StaticClass(), NAME_None, RF_Transient);
```

**Why 双层**:
- 治本:让游戏可玩,涌现式数值/StatCalculator 不再 nullptr crash
- 兜底日志:让用户/AI 知道 "BP reparent 失败",指引手动修复
- RF_Transient 不污染磁盘,PIE 结束自动 GC

**Python reparent 反射限制(UE 5.7)**:
- `bp.ParentClass = new_class` → 报 `'Blueprint' object attribute 'ParentClass' is protected and cannot be set`
- `bp.set_editor_property('ParentClass', new_class)` → 同样 protected
- **`unreal.evaluate_on_external_editor_change` 在 UE 5.7 移除**(旧代码依赖)
- 结论:UE 5.7 Python 反射 API **无法程序化 reparent** 蓝图,必须在 UE 编辑器里手动改

**手动 reparent 步骤**:
1. 在 Content Browser 右击 BP 资产 → "Reparent" 蓝图
2. 选 `SurvivorStatsConfig` (USurvivorStatsConfig)
3. 重新编译 BP
4. 验证:`python blueprint bp_summary <path>` 看 `Parent: SurvivorStatsConfig`

**已有工具修复**:`Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/reparent.py` 已适配 UE 5.7:
- `hasattr(bp, 'ParentClass')` 守卫
- `_safe_class_name` 兼容 unreal.Class 无 `GetName()` (用 `get_name()` Python binding)
- 删 `unreal.evaluate_on_external_editor_change` 调用
- 明确报告 ParentClass 是 protected,Python 反射无法程序化改

相关:
- [[t3-bpcomp-tobjectptr-reflection-fix]] — TObjectPtr 反射修复(类似反射层穿透问题)
- [[llm-bpprop-debug]] — bpprop Python ability 调试
