---
name: llm-hd3dpostprocess-boverride-naming-bug
description: hd3dpostprocess.py 用 snake_case override_* 当 Python 属性名（错），UE 真实是 PascalCase bOverride_*；导致 epic_reset / apply_epic_volume / apply_epic_volume_v6 全部 no-op，v6 Manual EV=-1.0 永远卡在 Lvl_SurvivorTest umap 里 → 场景纯黑
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 21d58984-f537-441e-923a-8db465b33cc1
---

# LLM EasyShell HD3DPostProcess bOverride_* 属性名错配根因 (2026-06-05)

**Why**：`hd3dpostprocess.py` 三处（`epic_reset` / `apply_epic_volume` / `apply_epic_volume_v6`）所有 `set_editor_property("override_*", ...)` 调用都用 **snake_case + 去 b 前缀** 写 `bOverride_*` UPROPERTY。UE Python 真实属性名是 **`bOverride_X`**（PascalCase + 保留 b 前缀）— 错的名字让 `set_editor_property` 抛异常被 except 吞，**整个 v6 EPIC 写操作 no-op**。

具体连锁：
1. `apply_epic_volume_v6` 写 `bOverride_AutoExposureMethod=True` + `AutoExposureMethod=AEM_MANUAL` + `bOverride_AutoExposureBias=True` + `AutoExposureBias=-1.0` —— 全部用错名 → 全部 no-op → 没真写入 PostProcessVolume0
2. `epic_reset` 列表里**没有 `bOverride_AutoExposureBias` 项**（且所有项都用错名）→ reset 是 no-op
3. 但 `Lvl_SurvivorTest.umap` 里 PostProcessVolume0 **硬编码** 了 `bOverride_AutoExposureBias=True` + `AutoExposureBias=-1.0`（某次手改或之前 commit 写入）
4. v6 设计的 Manual EV=-1.0 依赖配套 `r.Lumen.ScreenProbeGather.DownsampleFactor 16` + `TracingOctahedronResolution 16`（CVar，aiac 明确说"do NOT persist across editor restart"）— 重启后 CVar 失效，GI 缺
5. 缺 Lumen GI + Manual EV=-1.0 调暗 → 3D 输出 ≈ 0 → **场景纯黑**

**How to apply**：
- 写 `FPostProcessSettings` 字段时：
 - **值字段**（如 `AutoExposureMethod`, `BloomIntensity`）→ Python 用 snake_case（`auto_exposure_method`, `bloom_intensity`）✓
 - **bOverride_* 标志** → Python 用 **`bOverride_X`**（PascalCase + 保留 b 前缀）— **不**是 `override_x`
- 验证方法：`set` C++ 命令（`/Actor/{label}/{path}`）传 `bOverride_AutoExposureBias` 成功 vs `override_auto_exposure_bias` 失败，可以快速 sanity check
- `epic_reset` 必须包含**所有** `apply_epic_volume_v6` 写的 bOverride flags —— 缺一个就漏一个
- `set` C++ 命令在 PP volume sub-property 上**连续 set 3+ 次可能 crash**（崩溃栈 `ShellCommand_Set.cpp:521 return Result;`，地址 `0x000077ff...` kernel 段）— 是 LLMEasyShell 已知 bug，绕开方法：用 Python `set_editor_property`（走 `epic_reset` 走的就是这条路径）

**诊断信号**：
- `python hd3dpostprocess epic_status` 报告 bOverride 字段全 True + 值是 v6 写入值 → 检查 umap
- `python hd3dpostprocess epic_reset` 返回空 success 但 epic_status 没变 → **reset 是 no-op**（snake_case 错名）
- 场景纯黑 + Unlit 模式仍黑 + 关 PP volume 恢复 → **PP volume bOverride flags 强覆盖** 渲染
- `set /Actor/PostProcessVolume0/Settings.bOverride_X false` 恢复 → 确认是 bOverride 标志强覆盖

**修复 commit 范围**：`hd3dpostprocess.py` line 416-465（`_apply_epic_volume` 内 19 处）+ line 710-721（`_epic_reset` overrides 列表）+ line 962-965（`_apply_epic_volume_v6` AutoExposure 段）
