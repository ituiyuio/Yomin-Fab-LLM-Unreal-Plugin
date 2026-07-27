---
name: ui-generate-crash-2026-06-25
description: ⚠️ STALE/SUPERSEDED [tool-fix-152 2026-06-29]: 原文档 rootCause 引用了不存在的 JSON 字段 `imagePath`,实际 LLMDynamicUI Image widget 只用 style brush fields 不接受 imagePath;`--from` 是必需 flag 不是 warning。保留作为错误历史参考,新操作请看下方 [Current Correct Usage]
metadata:
 node_type: memory
 type: feedback
 originSessionId: 1aeb72a7-8c06-47c1-9da4-52ab517853e7
status: stale-superseded-by-tool-fix-152
---

# ⚠️ STALE — Superseded by tool-fix-152 (2026-06-29)

## 错误根因诊断(原文档 claim)

2026-06-25 调用 `ui generate /Game/.../WBP_SorceressPortrait --from json.json` 期间 UE 5.8 editor 崩溃. LLMEasyShell `Failed to connect to 127.0.0.1:15151` + editor 进程 . PNG Content/Features/.../Sorceress/ (绿底 alpha ), .uasset Texture2D UE . JSON `imagePath: /Game/.../sorceress_stand` texture .

**Why:** `ui generate` `imagePath` LoadObject null UE .

**How to apply:**
- `imagePath` **先** PNG → .uasset Texture2D `ui generate` .
- : `ui generate` WBP (无 Image brush) BP set Image brush. Image UE editor .
- JSON `rootWidget` `root` .
- `--from` preflight (`Warning: 'ui' doesn't support flag --from` , warning only).
- Crash : `llm-shell --restart` editor + build .
- WBP `new WidgetBlueprint` disk — restart .

## [Current Correct Usage] — tool-fix-152 source-of-truth

[tool-fix-152 2026-06-29] 验证后,此文档 rootCause 描述**不成立**:

1. **`imagePath` JSON 字段从未在 LLMDynamicUI schema 中实现** —
   `grep -i 'imagePath' Plugins/LLMDynamicUI/ -r` 返回 0 hits
   (LLMDynamicUI/Source/ + LLMDynamicUI/Config/ + LLMDynamicUI/Content/ 全 tree)。
   Image widget 仅接受标准 brush fields(`style.backgroundColor` / `style.brush` 等),
   不解析 `imagePath` 键。`/Game/.../sorceress_stand` 这条线索在当前 codebase 也 0 hits
   (`grep -i 'sorceress' Plugins/LLMDynamicUI/ -r` 返回 0)。

2. **`--from` flag 是必需 source-file 标记,不是 unsupported warning** —
   实际 `LLMDynamicUICommandHandler.cpp:66` 显式调用
   `FindArgValue(Args, TEXT("from"), SourceFile)`,L70/L75 在缺失时返回 error
   `"Missing required argument: --from <filePath>"`(不是 warning)。原文档
   "`Warning: 'ui' doesn't support flag --from`" 的描述**与实际代码相反**。

3. **`ui generate` 当前正确的 image 工作流** — Image widget 通过 `style`
   字段配置 brush,如需引用 Texture2D 资产,**先用 Content Browser import
   PNG → .uasset Texture2D**,然后在 JSON 里直接写 brush reference
   (`{ "type": "Image", "style": { "brush": "/Game/Textures/MyTexture" } }`
   或使用 `style.backgroundColor` 用纯色)。不需要 `imagePath` 中间字段。

**如何 apply(替代原文档):**
- PNG 素材 → UE Content Browser import → .uasset Texture2D
- JSON `Image` widget 用 `style.brush` 或 `style.backgroundColor` 引用
- `--from <filePath>` 是必需 flag,CLI 不接受 inline JSON
- 真实 editor crash 时 `llm-shell --restart` 拉起 editor + check editor log

[tool-fix-152 2026-06-29] meta-NOTE: 本 doc 保留作为错误历史 fossil,新操作请参考
SKILL.md "Common Patterns → Image widget" + "Editor Workflow" 章节
(`Plugins/LLMDynamicUI/Config/Schemas/PropertySchema.llmschema` brush schema)。
RootCause family: 早期 session 描述未验证的 API surface,导致 memory 文件 silent inconsistency。
Fix pattern 跟 tool-fix-130~151 meta-NOTE 链 1:1 平行 preservation > rewrite。
