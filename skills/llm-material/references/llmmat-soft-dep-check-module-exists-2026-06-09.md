---
name: llmmat-soft-dep-check-module-exists-2026-06-09
description: LLMMaterial LLMEasyShell 软依赖完整修复 — 5 步踩坑后发现真正根因是 Build.cs 缺 CheckModuleExists(2026-06-09)
metadata:
 type: project
 originSessionId: ea4e334c-2fa4-4f78-a577-12c9b7a9fdf4
---

# LLMMaterial 软依赖 (CheckModuleExists) 完整修复 — 5 步踩坑

## Why

LLMMaterial 想通过软依赖注册 `material` ability 到 LLMEasyShell / LLMEasyShellLite,实测发现:
**裸反射 (无 link) 100% 崩,只有 LLMStateTree 同样代码稳**。5 步排查后才发现真正根因:

> **Build.cs 必须 `CheckModuleExists` 条件 link LLMEasyShell / Lite 才能用反射 FindObject<UClass> 调 UFUNCTION**。
> 不 link,GUObjectArray 里 `ULLMEasyShellSubsystem` UClass metadata 没注册,`FindObject<UClass>(...)` 返回看似 non-null 的 invalid 指针 → `FindFunctionByName` 内部 deref 触发 EXCEPTION_ACCESS_VIOLATION。

5 步踩坑(已全部记录):
1. 裸反射 + `OnAllModuleLoadingPhasesComplete` → 崩 (Lite)
2. 改 `OnPostEngineInit` → 崩 (Full)
3. 改 `FTSTicker` next frame → 崩 (Full,栈底显示 ticker lambda 跑起来了)
4. 改成硬依赖 + 直调 C++ API → 稳(但 user 拒绝硬依赖)
5. 改成 LLMStateTree `CheckModuleExists` 条件 link + 完全反射 → 稳

## 真正根因

UE 5.7 GUObjectArray 的 UClass 注册是 build-time 行为:
- LLMEasyShell 的 UClass metadata 由 LLMEasyShell module 的 StaticInit 链注册
- 没 link LLMEasyShell module → LLMEasyShellSubsystem UClass 永远不在 GUObjectArray
- `FindObject<UClass>("/Script/LLMEasyShell.LLMEasyShellSubsystem")` 返回看似 non-null 的 stale 指针
- `GetEditorSubsystemBase` 返回 nullptr 但我们 check 了
- `UClass* ShellSubsystemClass = ...` 这个 raw pointer 实际指向一个 partial / stale class object
- `FindFunctionByName` 内部 TFieldIterator 解 `Children` 链表,read invalid 内存 → 0xffffffffffffffff / 0x00000005ba7424fa 之类地址 deref 失败

**只有 `CheckModuleExists` 加 `PrivateDependencyModuleNames` 才能触发 LLMEasyShell module 的 StaticInit 链 → UClass 才真正注册**。

LLMStateTree 稳是因为它 Build.cs 早用了这个模式(不是 timing 也不是 GC)。

## 完整修复(2026-06-09 commit)

### 1. LLMMaterial.uplugin — 删硬依赖

```json
"Plugins": [
 { "Name": "EditorScriptingUtilities", "Enabled": true }
 // 不写 LLMEasyShell / LLMEasyShellLite
]
```

### 2. LLMMaterial.Build.cs — CheckModuleExists 条件 link

```csharp
using System.IO;
public class LLMMaterial : ModuleRules {
 public LLMMaterial(ReadOnlyTargetRules Target) : base(Target) {
 if (Target.bBuildEditor) {
 PrivateDependencyModuleNames.AddRange(new[] { "UnrealEd", /* ... */ });
 // Optional: LLMEasyShell — CheckModuleExists + PublicDefinitions
 bool bHasLLMEasyShell = CheckModuleExists("LLMEasyShell");
 if (bHasLLMEasyShell) {
 PrivateDependencyModuleNames.Add("LLMEasyShell");
 }
 PublicDefinitions.Add("WITH_LLMEASYSHELL=" + (bHasLLMEasyShell ? "1" : "0"));
 // Optional: LLMEasyShellLite — 同样模式
 bool bHasLLMEasyShellLite = CheckModuleExists("LLMEasyShellLite");
 if (bHasLLMEasyShellLite) {
 PrivateDependencyModuleNames.Add("LLMEasyShellLite");
 }
 PublicDefinitions.Add("WITH_LLMEASYSHELL_LITE=" + (bHasLLMEasyShellLite ? "1" : "0"));
 }
 }
 private bool CheckModuleExists(string ModuleName) {
 foreach (string AvailableModule in Target.ExtraModuleNames) {
 if (AvailableModule == ModuleName) return true;
 }
 string ProjectRoot = Path.Combine(ModuleDirectory, "..", "..", "..", "..");
 string ModulePath = Path.Combine(ProjectRoot, "Plugins", ModuleName, "Source", ModuleName);
 return Directory.Exists(ModulePath);
 }
}
```

### 3. LLMMaterialModule.h — 每个 shell 单独 TObjectPtr slot

```cpp
class FLLMMaterialModule : public IModuleInterface {
public:
 virtual void StartupModule() override;
 virtual void ShutdownModule() override;
private:
 void RegisterAsLLMEasyShellAbilityAt(
 const TCHAR* SubsystemClassPath,
 const TCHAR* ShellName,
 TObjectPtr<ULLMMaterialCommandHandler>& OutHandlerSlot);
 void UnregisterFromLLMEasyShellAt(
 const TCHAR* SubsystemClassPath,
 const TCHAR* ShellName,
 TObjectPtr<ULLMMaterialCommandHandler>& InOutHandlerSlot);
#if WITH_LLMEASYSHELL
 void RegisterAsLLMEasyShellAbility();
 void UnregisterFromLLMEasyShell();
#endif
#if WITH_LLMEASYSHELL_LITE
 void RegisterAsLLMEasyShellLiteAbility();
 void UnregisterFromLLMEasyShellLite();
#endif
 FString BuildAbilityInfoJson() const;
 UPROPERTY()
 TObjectPtr<ULLMMaterialCommandHandler> LLMEasyShellCommandHandler; // 防 double-reg
 UPROPERTY()
 TObjectPtr<ULLMMaterialCommandHandler> LLMEasyShellLiteCommandHandler; // 防 double-reg
 FDelegateHandle LLMEasyShellRegHandle;
 FDelegateHandle LLMEasyShellLiteRegHandle;
};
```

### 4. LLMMaterialModule.cpp — OnAllModuleLoadingPhasesComplete + 完全反射

```cpp
#include "LLMMaterialModule.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/GCObject.h" // FGCScopeGuard
#include "EditorSubsystem.h" // UEditorSubsystem
#include "Misc/CoreDelegates.h"
// **不 include 任何 LLMEasyShell 头文件** — CheckModuleExists + macro 已经控制 link 关系

void FLLMMaterialModule::StartupModule() {
#if WITH_EDITOR
#if WITH_LLMEASYSHELL
 LLMEasyShellRegHandle = FCoreDelegates::OnAllModuleLoadingPhasesComplete.AddRaw(
 this, &FLLMMaterialModule::RegisterAsLLMEasyShellAbility);
#endif
#if WITH_LLMEASYSHELL_LITE
 LLMEasyShellLiteRegHandle = FCoreDelegates::OnAllModuleLoadingPhasesComplete.AddRaw(
 this, &FLLMMaterialModule::RegisterAsLLMEasyShellLiteAbility);
#endif
#endif
}

#if WITH_LLMEASYSHELL || WITH_LLMEASYSHELL_LITE
void FLLMMaterialModule::RegisterAsLLMEasyShellAbilityAt(
 const TCHAR* SubsystemClassPath,
 const TCHAR* ShellName,
 TObjectPtr<ULLMMaterialCommandHandler>& OutHandlerSlot) {
 if (!GEditor) return;
 if (OutHandlerSlot) return; // 防 double-registration

 UClass* ShellSubsystemClass = FindObject<UClass>(nullptr, SubsystemClassPath);
 if (!ShellSubsystemClass) { /* log warn */ return; }

 UEditorSubsystem* ShellSubsystem = GEditor->GetEditorSubsystemBase(ShellSubsystemClass);
 if (!ShellSubsystem) { /* log warn */ return; }

 // Step 1: RegisterAbilityJson (UHT 真实 layout: params + trailing return)
 static const FName RegisterAbilityJsonFuncName(TEXT("RegisterAbilityJson"));
 UFunction* RegisterAbilityJsonFunc = ShellSubsystemClass->FindFunctionByName(RegisterAbilityJsonFuncName);
 bool bRegistered = false;
 if (RegisterAbilityJsonFunc) {
 struct FRegisterAbilityJsonParamsWithReturn {
 FString AbilityName;
 FString AbilityJson;
 bool bReturnValue;
 };
 FRegisterAbilityJsonParamsWithReturn Params;
 FMemory::Memzero(&Params, sizeof(Params));
 Params.AbilityName = TEXT("material");
 Params.AbilityJson = BuildAbilityInfoJson();
 FGCScopeGuard GCGuard;
 ShellSubsystem->ProcessEvent(RegisterAbilityJsonFunc, &Params);
 bRegistered = Params.bReturnValue;
 if (!bRegistered) { /* log warn, return */ }
 }

 // Step 2: NewObject handler + AddToRoot + register
 UClass* HandlerClass = ULLMMaterialCommandHandler::StaticClass();
 ULLMMaterialCommandHandler* Handler = NewObject<ULLMMaterialCommandHandler>(GEditor, HandlerClass);
 if (!Handler) return;
 Handler->AddToRoot();
 OutHandlerSlot = Handler;

 static const FName RegisterHandlerFuncName(TEXT("RegisterAbilityCommandHandler"));
 UFunction* RegisterHandlerFunc = ShellSubsystemClass->FindFunctionByName(RegisterHandlerFuncName);
 if (RegisterHandlerFunc) {
 struct FRegisterHandlerParams {
 FString AbilityName;
 UObject* Handler;
 };
 FRegisterHandlerParams Params;
 FMemory::Memzero(&Params, sizeof(Params));
 Params.AbilityName = TEXT("material");
 Params.Handler = Handler;
 FGCScopeGuard GCGuard;
 ShellSubsystem->ProcessEvent(RegisterHandlerFunc, &Params);
 }
}
#endif
```

## 关键模式总结(LLMStateTree 验证过的)

1. **Build.cs `CheckModuleExists` 条件 link** — 让 plugin 决定 link 关系而不是硬编码
2. **代码不 include 任何 LLMEasyShell 头** — 完全反射,同名 struct 冲突自然消失
3. **`OnAllModuleLoadingPhasesComplete` delegate** — LLMStateTree 验证过的时序,此时所有 plugin subsystem 都 Initialize 完
4. **每个 shell 单独 TObjectPtr slot** — 防 OnAllModuleLoadingPhasesComplete 二次触发 double-registration
5. **`#if WITH_LLMEASYSHELL` / `#if WITH_LLMEASYSHELL_LITE` macro 包裹** — 没装时整个函数体不参与编译
6. **ProcessEvent 期间 FGCScopeGuard** — 防 GC race(虽然这次根因不是 GC,但保留它做 defense-in-depth)
7. **UHT 真实 layout 模拟** — bool-return UFUNCTION 必须加 trailing `bool bReturnValue`,ProcessEvent 内部按 UFunction reflection 的完整结构读取

## How to apply

下次任何 UE 5.7 plugin 想"软依赖"调 LLMEasyShell / Lite / 任何其他 plugin:
- **必须**用 `CheckModuleExists` 模式,不能裸反射
- 即使代码不引用任何对方 plugin 头文件,`PrivateDependencyModuleNames` 也必须 link,这样对方 module 的 StaticInit 链跑,UClass 才真正注册
- 参考: `Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterial.Build.cs` + `LLMMaterialModule.cpp`
- 参考实现: `Plugins/LLMStateTree/Source/LLMStateTreeEditor/LLMStateTreeEditor.Build.cs` + `LLMStateTreeEditorModule.cpp:391-658`

如果"裸反射"崩 `EXCEPTION_ACCESS_VIOLATION reading address 0x...` 在 `FindFunctionByName` 内部,99% 是这个原因 — 不要再去试 GC scope / 时序 / next frame,直接 CheckModuleExists 走起。

## 验证

- Editor 启动不崩(无 crash log)
- `material list-types` (LLMEasyShell 端口 15151) → 340 MaterialExpression types ✓
- `material` ability 在 LLMEasyShellLite (端口 15201+) `help` 输出里 ✓
- 双 shell 各自独立注册,handler 实例独立,各 AddToRoot / RemoveFromRoot 平衡
