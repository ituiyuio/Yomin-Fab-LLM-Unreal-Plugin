---
name: llmmat-constant3vector-value-vs-constant
description: "LLMMaterial .llmmat Constant3Vector 节点属性名必须用 \"Constant\" (UE UMaterialExpressionConstant3Vector::Constant)，不能写 \"Value\"；错误名字会 silently default to (0,0,0,0) 让 BaseColor 永远 = 纯黑"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 7e4ae561-f531-411d-9f46-68ec5c12571b
---

# LLMMaterial Constant3Vector 属性名 Value vs Constant (2026-06-07)

**Why**：`MaterialGraphBuilder.cpp:476-491` 在应用 .llmmat 节点属性时，对 Value 做了 fallback variants: `R`, `X`，但没 `Constant` (实际 L476-480 是 Value 变体映射块（5 行），L481-484 是 Constant 变体映射块（4 行）；L486-493 是 for 循环尝试变体，L496 是 `if (!Property)` 守卫，**L498 才是 AddWarning**——doc 之前写 L476-485/L487-490/L496 都是 fossil 误标) — UE 的 `UMaterialExpressionConstant3Vector::Constant` 字段不是 Value 也不是 R，是 **Constant**。错误的属性名 (Value) → "Property not found" warning + 字段不应用 + **节点默认 = (0,0,0,0)**。如果该常量被 `Multiply(white_const, vertex_color)` 用作 BaseColor，BaseColor 永远 = (0,0,0) × 任何 = 纯黑。

**StylizedPBR_Voxel.llmmat** 的 `white_const` 写的是 `"Value": [1.0, 1.0, 1.0]`，导致白色常量 = (0,0,0)，`M_StylizedPBR_Voxel` 渲染的所有 voxel mesh 永远 = 纯黑。同目录 `StylizedPBR.llmmat` 写的是 `"Constant"` (正确)，所以 PBR 材质的 mesh 正常。

**诊断信号**：
- `material generate` 输出含 `Property not found: Value on Constant3Vector` + `Some properties failed to apply on node: white_const`
- 材质 shader 编译成功（无 error），但渲染结果异常（黑/零值）
- `cat /Game/<MaterialFolder>/<mat>` 看 ScalarParameter 列表里没有 `Constant`/其他常量的 value（被默认了）

**修复**：
- 改 .llmmat: `properties.Value` → `properties.Constant` (array 格式不变)
- 重新 `material generate` 一次即可

**How to apply**：
- 写 .llmmat Constant3Vector 节点时**只**用 `Constant` (不是 `Value`)
- 写 .llmmat Constant (单 float) 节点时用 `R` (per builder.cpp:476-491 变体映射) 或 `Value` (被 R 覆盖)
- 写 ScalarParameter 节点用 `ParameterName` + `DefaultValue`
- 写 TextureSample 节点用 `Texture` (ObjectProperty) + 单独的 TexturePath 在 graph definition 里
- 跨材质的 .llmmat 应保持属性名一致：参考 `StylizedPBR.llmmat` 作为 canonical example
- 修复 commit: `fix(llmmat): StylizedPBR_Voxel.llmmat white_const 属性名 Value → Constant`
- 验证方法：`material generate` 无 "Property not found" 警告 + `ShaderCompiled: true` + 截图确认非黑

**关联**: [[llmmat-output-section-fix.md]] (类似 silent fallthrough 模式) [[llmmat-connection-fix.md]]
