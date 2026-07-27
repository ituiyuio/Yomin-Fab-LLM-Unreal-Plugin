---
name: llm-shell-set-pie-preflight-2026-06-25
description: "LLMEasyShell `set` 命令加 PIE preflight 拦截 — PIE 中改 BP asset 触发 BP 全量重编,90+ component BP 在 UE 5.8 必 crash (EXCEPTION_ACCESS_VIOLATION in SetComponentProperty)"
metadata: 
 node_type: memory
 type: reference
 originSessionId: 9427fbbf-9fca-487d-80cc-f1cbf61e7c85
---

# LLMEasyShell `set` PIE preflight 拦截

## 背景

PIE 中改 BP asset (`/Game/...` 或 `/Assets/...` 路径) 走 BP 全量重编。BP_SurvivorPlayer 有 90+ component,UE 5.8 strict enum reroute 在重编中触发 `EXCEPTION_ACCESS_VIOLATION reading address 0xffffffffffffffff` in `UShellCommand_Set::SetComponentProperty()` line 620 → `ExecuteNative()` line 186。

**这跟 preflight 拦不拦无关** — `--allow-pie` 放行后仍 crash。结论:PIE 中改 BP asset 必崩,只能 stop PIE 再改。

## 改动 (2026-06-25 commit)

`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Set.cpp:53-99`

1. **ExecuteNative 入口加 PIE preflight**:
 ```cpp
 const bool bIsAssetPath = (Parts[0] == TEXT("Assets") || Parts[0] == TEXT("Game"));
 const bool bIsReadOnly = Value.StartsWith(TEXT("__READ"));
 if (bIsAssetPath && !bIsReadOnly && !bAllowPie && GEditor && GEditor->IsPlayingSessionInEditor())
 {
 return FLLMEasyShellResult::Failure(EShellErrorCode::ExecutionFailed,
 TEXT("[preflight] PIE is running. set on BP asset triggers full BP recompile, which can crash the editor on large BPs (90+ components).\n")
 TEXT("Recommended workflow: stop -> set -> play (PIE)\n")
 TEXT("Override: append '--allow-pie' to bypass this guard if you accept the risk."));
 }
 ```

2. **Args 解析时支持 `--allow-pie` flag**:
 - 在 Args 中检测 `--allow-pie` (任意位置)
 - Value 拼接循环里 skip 这个 flag (不污染 value)
 - bAllowPie=true 时跳过 preflight

3. **/Actor/... 路径放行** — 改 PIE 中 actor 实例(transform 等)不触发 BP 重编,安全

## 用法

```
# PIE 中改 BP asset → 被 preflight 拒绝,推荐 stop
set /Game/Features/Survivor/BP_SurvivorPlayer#PortraitWidget/Space Screen
→ {"success": false, "error": "[preflight] PIE is running..."}

# stop 后再 set → 通过
stop
set /Game/Features/Survivor/BP_SurvivorPlayer#PortraitWidget/Space Screen
→ {"success": true, ...}

# 显式旁路 (LLM 自负风险)
set /Game/.../Space Screen --allow-pie
→ 走完,但仍可能 crash BP 重编

# PIE 中改 actor 实例(安全,放行)
set /Actor/BP_SurvivorPlayer0/Location (100,200,300)
→ 立即生效,不触发 BP 重编

# Read-only 不拦
set /Game/.../Health __READ
→ 返回当前值,不写
```

## ponytail 教训

- LLM 写 set 时若看到"editor is busy" timeout + restart,优先怀疑 PIE 中改了 BP asset
- PIE 改 BP asset 是死亡路径,无论加不加 preflight 都必崩
- Workaround: 把 BP 改动移到 C++ (livecoding 增量编译不触发 BP 全量重编) 或 BeginPlay runtime 配置已存在 component
- 之前 Sorceress 看板就是这条路径:C++ .cpp BeginPlay 配 WidgetComponent (Space/DrawSize/WidgetClass) — 不触发 BP 重编
- `--allow-pie` 仅是显式 escape hatch,不应作为默认路径

## 关联

- [[ue58-pre-existing-build-error-batch-2026-06-23]] — UE 5.8 strict enum 累积错误
- [[ezue-survivor-session-summary-2026-06-22]] — UbaCli crash pattern
- [[survivor-llmeasy-shell-restart-2026-06-25]] — editor crash 后 restart 工作流