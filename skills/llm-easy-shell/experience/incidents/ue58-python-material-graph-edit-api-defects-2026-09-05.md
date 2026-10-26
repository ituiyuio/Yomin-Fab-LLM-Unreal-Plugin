---
name: ue58-python-material-graph-edit-api-defects
description: "UE 5.8 python 材质图编辑 API 缺陷：connect_material_expressions 对新建节点恒 False 且无报错，原地改图不可行，走 material generate 重建"
metadata:
  node_type: memory
  type: feedback
---

# UE 5.8 python 材质图编辑 API 缺陷 — 原地改图不可行, 走 material generate 重建 (2026-09-05)

**场景**: 给 M_HD3D_TiltShift 加深度剔除 (v10.3), 用 `unreal.MaterialEditingLibrary` 原地补图
(create 节点 + connect + 改 Custom code)。**create 全部成功, connect 27/27 全部静默失败**
(返回 False, 无异常), 最终改走「删资产 → LLMMaterial `material generate` → add_v10_chain 重绑」管线闭环。

## 实测 5.8 API 面 (Engine/Source/Editor/MaterialEditor/Private/MaterialEditingLibrary.cpp)

| API | 5.8 状态 |
|---|---|
| `connect_material_expressions(from, outPin, to, inPin)` | **对新建节点恒 False** — 引擎按 `Expression->Outputs` 数组按名查输出 (cpp:928, `GetExpressionOutputIndexByName`), 新建表达式 Outputs 未填充即 INDEX_NONE; input 侧同样按名查。**无任何报错** |
| `connect_material_property(expr, outPin, property)` | **3 参签名** (没有 material 参数) — 与 C++ 4 参不同 |
| `MaterialCustomInput` (FCustomInput) | **noexport USTRUCT, python 拿不到** → Custom 节点无法加动态输入 |
| `MaterialExpressionConstant` 标量属性 | 是 `r` 不是 `value` |
| `MaterialExpressionClamp` Min/Max | **protected, set_editor_property 报错** → 走 Min/Max 输入引脚接 Constant |
| 坐标属性 | `material_expression_editor_x/y` (不是 desc_x) |
| `EditorAssetLibrary.reload_asset / is_asset_dirty` | **5.8 无**; 有 `save_asset/save_loaded_asset` |
| `MaterialEditingLibrary.delete_material_expression` | 存在可用 (按 (类名, editor坐标) 精确识别孤儿清理) |
| `delete_unused_expressions` | 存在 — 孤儿批量清理备选 |
| `EditorLoadingAndSavingUtils.reload_packages` | 存在 (EditorAssetLibrary 没有 reload 时的替代) |

## llm-shell python ability 的执行语义 (实测)

- ability 内**未捕获异常** → 之前的 create/delete 等 mutation 的回滚行为**不一致** (有的运行残留孤儿、有的被回滚), 不能依赖异常路径的状态语义
- **正常 return (哪怕 success:false) 一定提交状态** — 失败运行里的 `save_loaded_asset` 会把半成品孤儿落盘
- 幂等门不要只看"参数/节点存在" — 要看**最终接线证据** (如 `get_material_property_input_node(mat, MP_EMISSIVE_COLOR)` 是否已是目标节点)
- json.dumps 返回值: `get_editor_property` 某些返回值是非序列化对象 (Array 等), 全部 `str()` 化再返回

## 结论 / 正确路径

**原地补图 (python MaterialEditingLibrary) 在 5.8 不可行** (create 行、connect 不行)。
生成/改材质图一律走 LLMMaterial C++ 管线 (它自己处理 pin 名/Outputs, 见 MaterialGraphBuilder.cpp:798 的 "UE5.8 单输出节点真实输出 pin 名是空串" 回退):

1. 更新 `.llmmat` DSL 源 (Plugins/HD3D/Config/)
2. `rm` 旧资产 (`unreal.EditorAssetLibrary.delete_asset`)
3. `material generate /Game/... --from <llmmat>` (0 errors)
4. 重绑引用: `python hd3dpostprocess add_v10_chain` (clear + 重挂 4 阶 + save level)
5. export 回读 + census 对账 (注意 exporter 用自己的 node id 命名空间, 且 connection 数与 DSL 不等 — 用类型分布 + 输出链 upstream trace 验证)

案例: r-tiltshift-v10.3 (107 节点 1:1, shader 0 errors, A/B 截图实证焦深处恢复清晰)。
