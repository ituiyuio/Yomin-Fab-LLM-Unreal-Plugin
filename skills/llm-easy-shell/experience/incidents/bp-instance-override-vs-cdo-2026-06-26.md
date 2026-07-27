---
name: bp-instance-override-vs-cdo-2026-06-26
description: "BP CDO wire 修了但 level instance override 显式 None — runtime PIE 仍 null,需 set + save level 持久化"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 86643813-6244-482a-bbf8-a4dde9d4cd70
---

# BP Instance Override vs CDO Wire (2026-06-26)

## Root Cause

UE BP instance 在 level 里的属性值跟 CDO 默认值是 **2 层覆盖** 关系:
1. **CDO** (Class Default Object) = BP 类级默认值 (commit `bc52755` 修的是这一层)
2. **Level Instance Override** = BP actor 放在 level 里时,level 可以显式 override 任何属性(actor saved-with-property 模式)

如果 BP actor 早于新属性落地前就放在 level + level saved 时该属性是 None,后续 CDO 改了也无法 propagate 到 instance — UE 不会自动 sync,instance 永远保持 saved 时的 None 显式值。

**关键 trace 证据 (Session 55 PIE runtime verify)**:
- `cat /Game/Features/Survivor/BP_SurvivorPlayer` (CDO): `CharacterVFXData = /Script/CODEO.CharacterVFXDataAsset'/Game/Features/Survivor/VFX/DA_CharacterVFX_Default.DA_CharacterVFX_Default'` ✓
- `cat /Actor/BP_SurvivorPlayer0` (PIE instance): `CharacterVFXData = None` ✗
- 修法: `llm-shell set /Actor/BP_SurvivorPlayer0/CharacterVFXData /Game/Features/Survivor/VFX/DA_CharacterVFX_Default` + `llm-shell save /Game/Features/Survivor/Maps/Lvl_SurvivorTest`
- Verify: `git ls-files -s Lvl_SurvivorTest.umap` hash 变了,binary 93933 bytes 但内容确实改

## Symptoms

`C++ runtime guard fire silently`:
- 业务代码 `if (!CharacterVFXData) { UE_LOG warning; return; }` 永远命中
- Feature "wired" 在 git/aiac 都 OK,但 PIE runtime 实际 no-op
- 之前的 verify 路径(grep binary + bpprop 反射)只查 CDO 不查 instance,**漏掉 instance override**

## Real Example (Session 55)

- CDO wire 修在 commit `bc52755` (Session 53 + 54 work)
- Session 55 PIE 端到端 verify:
 - `info -j` → `pieState: Playing` ✓ (M_HD3D_TiltShader weight=0 不再 crash)
 - `cat /Actor/BP_SurvivorPlayer0` → CharacterVFXData=None ✗
 - `call /Actor/BP_SurvivorPlayer0 SpawnCharacterVFX 0` → log: `[VFX] SpawnCharacterVFX(0): CharacterVFXData is null, skipping`
- Fix: `set .../CharacterVFXData /Game/Features/Survivor/VFX/DA_CharacterVFX_Default` + `save /Game/Features/Survivor/Maps/Lvl_SurvivorTest` + commit `9c6df4f`
- Post-fix PIE verify: `call SpawnCharacterVFX 0/1/2/3` 4 event 全部 success,无 null log

## Detection Pattern (Ponytail Rung 7 + 2-step verify)

**别只查 CDO**:
```bash
# 1. 查 CDO (commit bc52755 已 verify)
llm-shell cat /Game/Features/Survivor/BP_X | grep -i 'propertyName'

# 2. **关键**: 查 PIE instance (需 PIE Playing)
llm-shell play -j && sleep 4
llm-shell cat /Actor/BP_SurvivorPlayer0 | grep -i 'propertyName'

# 3. 如 instance 仍 None 但 CDO 有值 → level override 漏修
llm-shell set /Actor/BP_SurvivorPlayer0/PropertyName /Game/Path/To/Asset
llm-shell save /Game/Path/To/Map
```

## Why This Is Different From [[bp-cdo-commit-before-save-2026-06-26]]

- **CDO commit-before-save**: 改 CDO 之前没 save BP,committed binary 缺 wire
- **Instance override stale**: CDO 修对了,instance 显式 None 跟 CDO 不同步
- 两者都是 silent failure,但 root 在不同层 (CDO vs instance),verify 路径不一样
- CDO 用 `grep` 查 binary,instance 用 `cat /Actor/...` 查 PIE runtime 反射

## Prevention (Root-Cause Fix)

1. **每次新加 UPROPERTY → 同步改 CDO + level instance**:
 - 改完 CDO 立即在 editor 重新打开 level + 在 PIE 里跑一遍 verify
 - 跑完 verify 再 commit (跟 CDO commit-before-save 同模式但更严:还需 instance 同步)
2. **改完 BP 属性 → 强制重新打开 + 重新 save 所有引用该 BP 的 level**:
 - UE editor 有 "update level instances from CDO" 工具(Blueprint Editor → File → Update All Level Blueprints / Tools → Audit)
 - 或手动 `llm-shell save <每个引用 level>` 强制 sync
3. **Verify 永远 2-step**: CDO grep + Instance `cat /Actor/...` 双重 verify
4. **C++ 代码加 BeginPlay log** 显式提示 wire 是否生效(不靠 silent guard):
 - 例:`UE_LOG(LogTemp, Log, TEXT("[VFX] BeginPlay CharacterVFXData=%s"), CharacterVFXData ? *CharacterVFXData->GetName() : TEXT("None"))`

## Related Memory

- [[bp-cdo-commit-before-save-2026-06-26]] — 同 root pattern (silent wire fail) 但 root 在 CDO 层
- [[bp-cdo-debug-pattern-2026-05-19]] — BP CDO 调试命令
-— git_precommit stale state lesson
- [[ue58-teds-plugin-crash-workaround-2026-06-26]] — UE 5.8 editor crash + workarounds (PIE 端到端 verify 依赖 editor online)
