---
name: llm-shell-set-assetpath-suffix
description: set ObjectProperty 必须用 /Game/.../Asset.Asset 后缀；无后缀形式静默失败（返回 OK 但引用没真写进）
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 3ac5e79b-e4ab-4b9b-bac9-d13cae0cb459
---

LLMEasyShell `set /Actor/.../Component/ObjectProperty <path>` 写 StaticMesh / Material 引用时，**必须用 `/Game/.../AssetName.AssetName` 全路径（带 .Asset 后缀）**。无后缀形式 `/Game/.../AssetName` 单独路径会**返回 success OK 但引用没真绑定**（ObjectProperty 仍是 NULL）。

**Why:** 2026-06-07 修 HD3D voxel scene 时排查 2 小时才发现。HD3D_VoxelDemo 设 mesh 用了某个带后缀的形式 OK；其它 3 个 Vox_* 用无后缀 `set` 静默失败。`voxel_diag` 跑 `get_editor_property("static_mesh")` 返回 NULL 才暴露。

**How to apply:**
- `set /Actor/.../StaticMeshComponent/StaticMesh /Game/HD3D/Voxelized/Megascans/Preview/SM_S_Wooden_Table_veigfjmaw_lod5_Var1_Voxel.SM_S_Wooden_Table_veigfjmaw_lod5_Var1_Voxel` ← **带后缀**
- 不要用：`/Game/HD3D/Voxelized/Megascans/Preview/SM_S_Wooden_Table_veigfjmaw_lod5_Var1_Voxel` ← **无后缀静默失败**
- 验证：写完后用 `voxel_diag` 或 `python property get_prop` 读回来确认引用非 NULL
- 同样的坑适用于 `Material` 引用、`OverrideMaterials[i]`、任何 UObject property
- 跟 memory `hd3d-megascans-bake-e2e-2026-06-07` 里的 `GetObjectPathString().RemoveFromEnd("." + AssetName)` 是同一根因的镜像 — UE 的 ObjectPath 全程带 `.Asset` 后缀，setter 写引用时也期望这个完整形式
