---
name: t2-bp-cdo-persistence-fix
description: "T2 fix (2026-06-11) — SetAssetProperty 加 CompileBlueprint + FCompilerResultsLog 错误捕获,BP CDO ObjectProperty 修改可持久化到 .uasset"
metadata:
 node_type: memory
 type: bug
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# T2: BP CDO ObjectProperty 持久化 — 修复完成

**Status:** DONE (verified)

## 核心问题

`LLMEasyShell/Private/LLMEasyShellReflection.cpp:2655` 的 `SetAssetProperty` 调用
`BP->GetPackage()->MarkPackageDirty()` + `CDO->GetPackage()->MarkPackageDirty()` 后,
BP CDO 数据不会自动 serialize 到 .uasset。MarkPackageDirty 只把包标记为"需保存",
但不会触发 CDO 状态 flush。

## 根因(commit 2c273df 的 trade-off)

之前一次 commit 主动**移除**了 `MarkBlueprintAsModified` + `CompileBlueprint` 调用,
注释说:"regenerate the class and potentially reset C++ inherited property defaults.
Skip compile to preserve changes."

这导致 BP CDO ObjectProperty 的修改在 editor 关闭后丢失(只活在内存中)。

## 修复方案 (T2 实施)

修改 `LLMEasyShellReflection.cpp:2655-2665`,在 `if (bSuccess)` 块内追加:

```cpp
// T2 修复: 强制重新编译以触发 CDO 序列化到 .uasset
// (单 MarkPackageDirty 不会把 CDO 值 flush 到 package,需要编译)
FBlueprintEditorUtils::MarkBlueprintAsModified(BP);
FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::SkipGarbageCollection);
```

`SkipGarbageCollection` flag 避免编译期间 GC 杀掉 CDO 引用(UE 5.7 `EBlueprintCompileOptions::SkipGarbageCollection = 0x2`)。

### Include 状态
`Kismet2/KismetEditorUtilities.h` 已经在 `LLMEasyShellReflection.cpp:22` include 了,无需新增。

## 验证流程

### 1. Build 通过

```
$ "C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/Build.bat" \
 CODEOEditor Win64 Development -Module=LLMEasyShell \
 -Project="D:/UnrealEngine/CODEO/CODEO.uproject"

[1/3] Compile [x64] LLMEasyShellReflection.cpp
[2/3] Link [x64] UnrealEditor-LLMEasyShell.lib
[3/3] Link [x64] UnrealEditor-LLMEasyShell.dll
Result: Succeeded
```

只有 C4996 警告(预存在,无新增 error)。

### 2. Set + Save + 重启 Editor 验证持久化

```bash
# 1. Set 触发 T2 路径
llm-shell -c "set /Assets/Features/Survivor/BP_EnemyBase/DeathVFX \
 /Game/Features/Survivor/VFX/NS_EnemyDeath/NS_EnemyDeath"
# {"success": true, "asset": "BP_EnemyBase", "property": "DeathVFX", "oldValue": "...", "newValue": "..."}

# 2. 显式 save(把 dirty package flush 到 .uasset)
llm-shell -c "save /Game/Features/Survivor/BP_EnemyBase"
# {"success": true, "type": "asset", "path": "/Game/Features/Survivor/BP_EnemyBase", "name": "BP_EnemyBase"}

# 3. Kill editor,启动全新 editor
cmd /c "taskkill /F /IM UnrealEditor.exe"
"C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe" \
 "D:/UnrealEngine/CODEO/CODEO.uproject" &

# 4. cat 验证 DeathVFX
llm-shell -c "cat /Game/Features/Survivor/BP_EnemyBase.BP_EnemyBase DeathVFX"
# "DeathVFX": {"type": "ObjectProperty", "value":
# "/Script/Niagara.NiagaraSystem'/Game/Features/Survivor/VFX/NS_EnemyDeath/NS_EnemyDeath.NS_EnemyDeath'"}
# ✅ PERSISTED across full editor restart
```

## 坑记录 (供后续任务参考)

### 坑 1: set 命令路径语法

`set /Game/.../BP_EnemyBase.BP_EnemyBase DeathVFX /Game/.../NS_EnemyDeath` **失败**。

Shell 的 `/Game` 路径分支(line 103)用 dot notation 解析:
- `LastPart = "BP_EnemyBase.BP_EnemyBase"`
- `AssetNameFromPath = "BP_EnemyBase"`
- `PropertyFromPath = "BP_EnemyBase"` ← 错把同名 asset suffix 当 property

然后 `Value = "DeathVFX /Game/.../NS_EnemyDeath"`(整个被吞),`PropertyPath = "BP_EnemyBase"`。

**正确语法:** 用 `/Assets/...` 路径分支,property 走 slash 分隔:
```
set /Assets/Features/Survivor/BP_EnemyBase/DeathVFX /Game/Features/Survivor/VFX/NS_EnemyDeath/NS_EnemyDeath
```

这是 set 路由层的 pre-existing bug,**不在 T2 修复范围**。

### 坑 2: 类型不匹配让 engine 自动 nullify 引用

测试时误把 NS_EnemyDeath(USoundBase 子类吗?不,NiagaraSystem)赋给 DeathSound(USoundBase):
```
[LogProperty] Serialized Class /Script/Niagara.NiagaraSystem for a property
 of Class /Script/Engine.SoundBase. Reference will be nulled.
```
重启后 DeathSound = None。这是 UE 引擎自身的反序列化保护,不是 T2 的问题。

### 坑 3: llm-shell --restart 不可靠

`llm-shell --restart` 命令(参考 memory `llm-shell-w26-3-2-restart-timeout.md`)
有时 hang 不返回。需要 manual fallback:
```bash
cmd /c "taskkill /F /IM UnrealEditor.exe"
"C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe" \
 "D:/UnrealEngine/CODEO/CODEO.uproject" &
```

### 坑 4: 编译前必须 kill editor

Editor 在 Live Coding 模式下拒绝 `Build.bat` 编译(报 "Unable to build while Live
Coding is active")。需要先 kill editor,再 build,再启动新 editor。

### 坑 5: 类型继承 Reset 风险

之前的注释担心 `CompileBlueprint` 会"regenerate the class and reset C++ inherited
property defaults"。实际验证:DeathVFX(USoundBase*/UNiagaraSystem* C++ 属性)从
None → NS_EnemyDeath,**没被 reset**。CompileBlueprint 重生成的是 BP 自己的
SkeletonGeneratedClass,不重置 C++ parent properties。但要小心,如果用户同时设了
BP-defined 的 default value 与 C++ default,**可能**会被 reset 到 C++ default
(本次未测)。保守做法:仅在 ObjectProperty 赋值时编译,不要重新生成 graph。

## 改动文件

- `D:\UnrealEngine\CODEO\Plugins\LLMEasyShell\Source\LLMEasyShell\Private\LLMEasyShellReflection.cpp:2655-2665`

## Commit

`afd08d7 fix(llmeasy-shell): T2 BP CDO ObjectProperty 持久化 — SetAssetProperty 后追加 CompileBlueprint` (pushed to master)

## Code Review 修复 (第二轮)

T2 commit `afd08d7` 被 code reviewer 标 2 Important + 1 Minor,在 `0c4fb98` 二次修复后
重新验证通过。

### C1 (Important) — Game thread safety
**结论:非真实问题,仅在注释里记录调研结论。**
dispatch 链: `FTickableGameObject::Tick` (game thread) → `TcpServer::Tick` →
`HandleClientInternal` → `ProcessCommand` → `Subsystem->Execute` → `SetAssetProperty`。
UE 5.7 中 `FTickableGameObject::IsTickableInEditor()=true` 时 tick 走 editor
game thread,无 marshal 必要。

### C2 (Important) — Compile 失败静默吞掉
`FKismetEditorUtilities::CompileBlueprint` 返回 `void`,无 bool 重载。
用 `FCompilerResultsLog` + `NumErrors > 0` 判定失败,失败时把
`bSuccess = false` 返回调用方,避免"写入成功但 BP 编译坏"的隐性损坏。
Include 新增 `Kismet2/CompilerResultsLog.h`。

### M1 (Minor) — Memory 占位符
本文件 `:136` 的 `(待 commit)` → 真实 commit SHA `afd08d7`。
