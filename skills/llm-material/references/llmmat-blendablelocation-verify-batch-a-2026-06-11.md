---
name: llmmat-blendablelocation-verify-batch-a-2026-06-11
description: LLMMaterial Batch A fix (commit 41eb93c) 验证通过 — M_CustomTonemapper.BlendableLocation = BL_ReplacingTonemapper; 但 .llmmat 写入 BL_ReplacingTonemapper 不会自动同步到已存在的 .uasset (需要 re-generate)
metadata: 
 node_type: memory
 originSessionId: 3d4942af-682d-4e39-960d-b94ef72058c8
---

# LLMMaterial Batch A Fix Verification (2026-06-11)

**Commit**: `41eb93c fix(llmmaterial): P6 producer 端 — parser 读 blendableLocation 字段`

**验证方法**：`python property get_prop asset_path=/Game/<MaterialFolder>/<M> property_path=BlendableLocation`
（注：`python material material_get_info` 返回的 FLLEMaterialInfo struct 不含 BlendableLocation 字段，必须走 FProperty 反射）

**实测 12 个 PP 材质**（2026-06-11）：

| Material | BlendableLocation | .llmmat 源 |
|----------|-------------------|-----------|
| **M_CustomTonemapper** | `BL_ReplacingTonemapper` ✓ | `ReplacingTonemapper` ✓ |
| M_TiltShift | `BL_SceneColorAfterTonemapping` (默认) | `SceneColorAfterDOF` (working tree) ✗ |
| M_KawaseDOF | `BL_SceneColorAfterTonemapping` (默认) | `SceneColorAfterTonemapping` ✓ |
| M_SSAOMask | `BL_SceneColorAfterTonemapping` (默认) | `SceneColorAfterTonemapping` ✓ |
| M_CelShading, ChromaticAberration, FilmGrain, DOF, Bloom, CCDComposite, ColorGrading, Quantize12, PreQuantizeMedian, PostQuantizeTemporal | `BL_SceneColorAfterTonemapping` (默认) | (无 blendableLocation 字段) |

**关键发现**：
1. **Parser 修复 ✓** — CustomTonemapper 验证通过证明 commit 41eb93c 实际生效（live coding 231.5s 后 succeeded）
2. **TiltShift 数据漂移** — .llmmat 已加 `SceneColorAfterDOF` 字段（uncommitted diff），但 .uasset 仍为默认 → 需 `material generate` 重新 apply 才能把字段写入 asset
3. **LiveCoding 报告的 "Failed" 可能是 60s timeout 假象** — 等到 `livecoding --status` 或 `info` 看到 `phase: "succeeded"` 才是真状态

**适用场景**：每次修改 .llmmat 后必须 `material generate` 重新写入 .uasset，光改 .llmmat 不会同步到 asset
