---
name: feedback-ue-uclass-getname-strips-prefix
description: UE 5 UClass::GetName() 自动去掉 U/A/F 前缀；分析带 prefix-strip 逻辑的 UE 插件代码时不要假设 GetName() 返回完整 C++ 类名
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 6b107901-4136-4321-9236-e2f1b9b8be84
---

# UE 5 UClass::GetName() 自动剥前缀

**关键事实**：UE 5 的 `UClass::GetName()` 返回的是**去掉 U/A/F 前缀的短名**。

```
C++ 声明: UCLASS() class UPCGCreatePointsGridSettings : public UPCGSettings
GetName(): "PCGCreatePointsGridSettings" ← UE 自动剥掉 U
GetPathName(): "/Script/PCG.PCGCreatePointsGridSettings"
```

**Why**：2026-06-06 审计 LLMPCG 插件时，我错误判断"9 个示例因 type 命名约定错误（带 PCG 前缀）全部失败"，把 `PCG<Name>` 标记为 P0 bug。

实际上：
- `LLMPCGNodeRegistry::ExtractNodeMeta` 里的 `if (TypeName.StartsWith("UPCG"))` 是**死代码**分支（GetName 不返回 `UPCG...`）
- 实际 TypeName 保留为 `PCGCreatePointsGridSettings`（首字符 P 不进 else 分支）
- 正好与示例 `sample_*.llmpcg` 里的 `"type": "PCG<Name>"` 匹配
- commit `6a00cf9` 的 diff 也证明 `PCG<Name>` 是正确约定（从 `PointFromSurface` 改成 `PCGPointFromMeshSettings`）

**How to apply**：
- 看到 UE 插件里有 `if (Name.StartsWith("UPCG"))` / `if (Name.StartsWith("UActor"))` 这类 prefix-strip 代码，先**怀疑它是防御性 dead code**，不要直接当成"作者预期 GetName 返回带前缀名"
- 真正判断 type 匹配：直接 grep 示例文件 + `git log -p` 看最近的 type 命名修复
- 想验证：写一个 minimal UE 命令（`UE_LOG(GetName())`）或者用 `python unreal.log(Class.GetName())` 调一下

**相关 UE 5 反射规则**：
- `UClass::GetName()` → 短名（去 U/A/F 前缀）
- `UClass::GetPrefixCPP()` → 单独拿前缀
- `UClass::GetPathName()` → 完整路径（同样去前缀）
- `FString::Printf("/Script/%s.%s", Module, Class->GetName())` → 正确路径格式

不要在路径中加 `U` 前缀（`/Script/PCG.UPCGCreatePointsGridSettings`）— 这是错的，正确是 `/Script/PCG.PCGCreatePointsGridSettings`。

相关审计报告教训：[[llmpcg-audit-2026-06-06]]（待建立）
