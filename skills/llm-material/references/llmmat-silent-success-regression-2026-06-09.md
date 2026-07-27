---
name: llmmat-silent-success-regression-2026-06-09
description: "LLMMaterial SM6 编译错误返抛链 2026-04-15 被 14b5cfc 砍掉回归,2026-06-09 最小修复;科学架构(Shader Compile Gate)留待重构"
metadata: 
 node_type: memory
 type: project
 originSessionId: ab89b52f-89eb-4e8e-ab02-8aed304a4d33
---

# LLMMaterial SM6 编译错误返抛回归 + 最小修复(2026-06-09)

## 根因(已通过代码 + git 历史 100% 锁定)

`LLMMaterialCommandHandler.cpp:CmdGenerate` 在两个 commit 之间被退化:

- **`b772c0a` (2026-04-03)**:正确路径 — `Material->ForceRecompileForRendering()` + 60s 阻塞轮询 `IsCompilationFinished()` + 读 `GetCompileErrors()` + `IsCompilingOrHadCompileError` 兜底诊断
- **`14b5cfc` (2026-04-15)**:为避免 Substrate 上 `FAssetThumbnailPool crash` 把上面的逻辑全部砍掉,改为 `ProcessAsyncResults(0.0f, true)`(fire-and-forget)+ `pending` 即 `BuildSuccessResult` 静默成功

**症状**:任何带 SM6 编译错误的 `.llmmat`(典型如 `M_HD3D_KawaseDOF`)在 `material generate` 时返 `success=true` 但实际材质是坏的。

**根因(更深)**:14b5cfc 砍错位置了。`FAssetThumbnailPool crash` 是 `ForceRecompileForRendering` 的副作用(thumbnail 渲染 + render thread race),不是"等编译"的副作用。CLI 命令场景下没有 thumbnail 渲染,触发 + 等编译是安全的。

## 最小修复(已实施,2026-06-09)

`LLMMaterialCommandHandler.cpp` CmdGenerate 内:

1. **Substrate 路径**(避免 thumbnail crash):`Material->PreEditChange(nullptr) + PostEditChange()` + 60s 等编译
2. **非 Substrate 路径**:`Material->ForceRecompileForRendering()` + 60s 等编译(b772c0a 老路)
3. **三态报告**:
 - `GetCompileErrors().Num() > 0` → `BuildErrorResultWithDetails` 返具体 SM6 错
 - `IsCompilationFinished() == false` (timeout) → 报 timeout 错
 - 0 errors + 编译完成 → `BuildSuccessResult`

Substrate 判别条件:
```cpp
Material->MaterialDomain == MD_Surface
 && Material->GetShadingModels().HasShadingModel(EMaterialShadingModel::MSM_Strata)
```

## Why

LLMMaterial 的设计意图是"生成时同步返抛编译错误,LLM 可以迭代"。14b5cfc 把它退化成了"生成成功 = 实际不验证",完全违背了 LLM-first 工具的设计。`b772c0a` 已被 14b5cfc 完整覆盖 + 14b5cfc 多次 refactor(46895b9 / 76dc8f6 / 9e4116f)未恢复,成为长期 silent bug。

## How to apply

1. 任何"`.llmmat generate` 返 success 但材质不工作"的报告:先看是否走了 `ShaderStatus: pending`(意味着还是老 bug);新代码不会再返 pending,只会返具体错或编译成功
2. 任何 LLMMaterial 编译/触发相关代码改动:不要砍 `ForceRecompileForRendering` 调用,正确做法是用 `HasShadingModel(MSM_Strata)` 判别分流
3. 任何材质生成 pipeline 涉及"等待 shader 编译":**必须** 三态(success/errors/timeout),不能二态(success/pending)

## 待重构(科学架构)

当前最小修复是 pragmatic 补丁,科学架构是:
- **Shader Compile Gate** 单一函数 `WaitForShaderCompileAndCollectErrors(Material, Timeout)` 给所有材质用
- 触发动作选 Substrate-safe 的 `PostEditChange`(经实测)
- 等编译统一用 `FinishCompilation` 或轮询 `IsCompilationFinished`
- 错误收集统一用 `GetCompileErrors() + IsCompilingOrHadCompileError()`

关联:[[llmvfx-build-broken-pre-existing-2026-06-03]] (LLMVFX 类似问题:Lite phase 6 引擎三方库 includes 缺失导致 build 卡,完全独立于 LLMMaterial 修复)
