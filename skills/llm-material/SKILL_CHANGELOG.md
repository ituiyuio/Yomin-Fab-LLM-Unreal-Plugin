---
name: llm-material-skill-changelog
description: llm-material/SKILL.md 历次 forensic 历史记录 — 提取自 SKILL.md 的 archived 历史修复 blockquote / HTML comment,doc-noise-reduction sub-class 34 (tool-fix-07 session129 2026-07-10) closure。2 markers in SKILL.md ↔ 2 §N in CHANGELOG.md 1:1 lock。
metadata:
  type: project
---

# llm-material SKILL.md Forensic Changelog

> 历史 forensic 记录归档。SKILL.md 当前内容只保留 live technical warning + 当前材质 DSL 使用说明;本文件保留 detailed commit archaeology + doc-fossil closure history + audit-trail 证据,供未来审计 / regression 调查参考。

**Architecture invariant**:`SKILL.md` ↔ `SKILL_CHANGELOG.md` 1:1 lock,每处 forensic blockquote / HTML comment 在 SKILL.md 都有对应 `<!-- Forensic: see SKILL_CHANGELOG.md §N (context) -->` marker。

---

## §1 — [tool-fix-170 2026-06-29] M_SiliconeDoll template asset/USH fossil closure

**Context**:提取自 SKILL.md `### 硅胶材质模板` 段尾部,原本是 inline blockquote 描述 tool-fix-170 闭合 M_SiliconeDoll 模板 fossil cluster 的 detailed rootCause + 3 重 lock。本 §N 保留 forensic 历史记录;SKILL.md 当前 live 段只保留 actionable warning、真实资产路径、唯一 USH 文件事实、参数表和查看命令。

### 痛点

tool-fix-151 (commit `5c5d0b6`, 2026-06-29) 修了 `llm-material/references/*.md` 5 处 line drift,但漏扫 `SKILL.md` 主体的 `M_SiliconeDoll` 模板 fossil cluster:

1. 1 个 asset-name doc-fossil: `Content/Materials/M_SiliconeDoll.llmmat` 并不存在
2. 3 个 USH-name doc-fossil: `SiliconeSSSApprox.ush` / `SiliconeRimGlow.ush` / `SiliconeComposite.ush` 并不存在
3. 1 个 directory-not-exist: `Content/Materials/` 整个目录不存在
4. 3 个参数默认值跟真实资产不匹配

LLM 据此按模板跑 `material generate` 会立刻陷入 file-not-found / wrong-reference 调试循环。

### Source-of-truth 3 重 lock

1. `find . -iname "*silicone*doll*"` = 0 hits 全工程 (`M_SiliconeDoll.llmmat` 不存在)
2. `ls Content/Materials/` = 0 files (整个目录不存在)
3. `find Content -iname "Silicone*.ush"` = 1 file (`Content/Shaders/SiliconeFresnel.ush`),模板列出的其他 3 个 USH 0 hits

### Fix scope

1 file `llm-material/SKILL.md` 原段改为:

- header 加 ⚠️ 警告,明确这是模板/教学示例,不是已存在资产
- 锚定 3 个真实硅胶资产:
  - `Content/Core/LLM/Materials/M_SiliconeSkin_v3.llmmat`
  - `Content/Core/LLM/Materials/M_TPESilicone_v7_NoSSS.llmmat`
  - `Content/Core/LLM/Materials/M_TPESilicone_v8_AiCup.llmmat`
- 改 USH 列表为唯一真实文件 `Content/Shaders/SiliconeFresnel.ush`
- 改 `basecolor` / `roughness` / `sss_mfp` 默认值跟 `M_SiliconeSkin_v3` 1:1 对齐
- 末尾加 `[tool-fix-170]` meta-NOTE 解释 rootCause + 3 重 lock + pattern

Pattern 跟 tool-fix-151/164/167 paired completion 1:1 平行: `doc-fossil count/asset claim drift` family。

---

## §2 — [tool-fix-07 session62 2026-07-09] material ability 5-subcommand count closure

**Context**:提取自 SKILL.md `## Command Reference` 段,原本是 inline blockquote 记录 session62 把 `material` ability 子命令数锁到 runtime truth 的 detailed forward-fossil defense。本 §N 保留 forensic 历史记录;SKILL.md 当前 live 段只保留 `Source of truth` 与 5 条命令列表。

### 痛点

`material` ability 的 runtime 注册表只有 5 个公开子命令,但历史文档容易把 deprecated factory / internal handler 分支混入公开 CLI,误写成 7 个或包含已移除的 `inspect` / `set`。这会让 LLM 选择 dispatcher 不放行的命令,进入 help/error-path 调试循环。

### Runtime truth

`llm-shell -q -j -c help material` 公开子命令 5 个:

1. `generate`
2. `export`
3. `export-schema`
4. `list-types`
5. `describe-type`

Source-of-truth 是 `Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterialModule.cpp::BuildAbilityInfoJson()`。通用资产操作(创建/删除/复制/移动/查看/设置参数)由 LLMEasyShell 主系统提供,不在 `material` ability 重复注册。

### Forward defense

`doc-audit count-llmmaterial-subcmd-drift` 模式作为前向化石防御:任何未来 LLM 误写 `material ability 注册 N 个子命令` (N≠5) 会触发 audit fail。

---

## Session history

- **session129 (2026-07-10)**: llm-material/SKILL.md forensic extraction — 29896B → 28570B (-1326B / 4.4% reduction),2 forensic blockquotes 提取 (`tool-fix-170` M_SiliconeDoll template asset/USH fossil closure + `tool-fix-07 session62` material 5-subcommand count closure) → 2 short markers。Mirrors session118 Lite (66%) + session119 full (16%) + session120 sakura-brass (72%) + session121 methodology (27%) + session122 llm-dynamic-ui (38.7%) + session123 llm-statetree (32.7%) + session124 llm-metasound (18.9%) + session124 final llm-quixel (57%) + session125 llm-white-box (14.6%) + session127 llm-vfx (7.7%) + session128 llm-pcg (11.8%) pattern (sub-class 34 doc-noise-reduction skill-main-doc forensic extraction extended to 11th skill)。`## Command Reference` live source-of-truth + 5 command table KEPT。
