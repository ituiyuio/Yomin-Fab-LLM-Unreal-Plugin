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

**Context**:提取自 SKILL.md `### 硅胶材质模板` 段尾部,原本是 inline blockquote 描述 tool-fix-170 闭合 M_SiliconeDoll 模板 fossil cluster 的 detailed rootCause + 3 重 lock。本 §N 保留 forensic 历史记录;SKILL.md 当前 live 段只保留 actionable warning、参数表和"先核实再引用"的查看命令(资产路径与 USH 文件名已随 de-projectify 改成范本占位符,见本节末尾 Amendment)。

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

### Amendment — de-projectify (2026-10-25)

本 skill 随插件公开发布(`github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin`),读者是**任意工程**,不是本仓库。原 live 段把本仓库私有资产当"生产可用资产"写死,外部用户照抄路径必然 file-not-found —— 正是 tool-fix-170 当初要消灭的那类 doc-fossil,只是换了个方向重演。故 SKILL.md live 段做 de-projectify:

| 原 live 段 | 现在 |
|---|---|
| `Content/Materials/M_SiliconeDoll.llmmat` + 3 个硅胶资产真实路径 | 范本占位符 + "先核实再引用"的 `find` / `ls` 命令 |
| `Content/Shaders/SiliconeFresnel.ush`(当时唯一真实 USH) | `<ProjectContentDir>/Shaders/`(插件真实落盘目录,见 `USHGenerator::Initialize()`) |
| 参数表标注"参考 M_SiliconeSkin_v3 实际值" | 标注"硅胶基底典型值"(数值不变) |
| `.ush` 输出目录写成 `/Game/Shaders/`(UE content path) | 改成 `<ProjectContentDir>/Shaders/`(文件系统路径)——原写法**连本仓库都是错的**,`references/llmmat-connection-fix.md` 已记录该 bug |

本 §N 的历史记录(真实资产路径 + 3 重 lock 证据)**保持原样**:它是 tool-fix-170 当年的 forensics,引用当时仓库里的真实文件名才有审计价值;live 段对应的 `<!-- Forensic: see SKILL_CHANGELOG.md §1 -->` marker 仍在,1:1 lock 未破。

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
- **session(de-projectify) (2026-10-25)**: llm-material skill 去项目化 —— SKILL.md live 段的本仓库私有资产路径 / HD3D 插件名 / 绝对路径全部改成通用占位符;`/Game/Shaders/` UE-content-path 谬误修正为 `<ProjectContentDir>/Shaders/`(文件系统路径);references/ 8 个文件的项目资产名泛化(保留 lesson、泛化 path,未删文件)。§1 增补 Amendment(forensics 原文不动),§2 的 5 子命令契约未触碰。
- **session(command-surface-convergence) (2026-10-25)**: `material` ability 命令面收敛 —— §2 的 **5 子命令契约一字未改**(ability JSON 与收敛前逐字节等价,门禁 `verify-e2e.py` 的 `contains="generate, export, export-schema, list-types, describe-type"` + `not_contains="inspect"` 双锁仍成立)。变的是**这些命令从哪来**:命令面唯一真源从 `LLMMaterialModule.cpp::BuildAbilityInfoJson()` 的手写字面量搬进 `Commands/MaterialCommandRegistry.h` 的注册表(一条命令 = 一枚描述对象:名字 + 用法 + 描述 + 示例 + 实现函数),ability JSON 的 `commands[]` 与 `"Available commands: ..."` 错误串都从这张表派生 ⇒ 声明与实现结构上不可能漂移;一命令一文件(`Commands/Material<Name>Command.{h,cpp}`)。同时查清并删掉一条更隐蔽的病:**两个 shell(full 与 lite)的分发门禁都只放行 `commands[]` 里的子命令** ⇒ "实现了但没广告"的命令(create/set/export/inspect/apply)从来就不可达,是假成功桩 + 重复实现。通用层已覆盖等价能力(`new`/`rm`/`cp`/`mv`/`cat`/`set`、`python material material_get_info`/`material_get_graph`、`set /Actor/.../MeshComp/StaticMesh 0 /.../MyMaterial`),故不重复注册。SKILL.md `## Command Reference` 的 Source-of-truth 指针同步指向注册表并写明"注册表外的命令一律不可达"这条运行期事实。
- **session(gui-tool-list-reconciliation) (2026-10-25)**: GUI 与 ability 工具列表跟真实实现对齐 —— 核心是**导出侧与解析侧的枚举词表漂移**:`LLMMaterialSerializer::DomainToString` / `BlendModeToString` 是一份手写 switch,解析侧认的是 `FLLMEnumLookup::Build*Map()` 这另一张表 ⇒ serializer 导出得出 `RuntimeVirtualTexture` / `AlphaComposite` / `AlphaHoldout`,解析侧却不认识 ⇒ `material export` → `material generate` 往返时**静默降级**成 `Surface` / `Opaque`(材质建出来、shader 也过,设置没了)。现在两侧共用 `FLLMEnumLookup` 的规范表(加一个值 = 改一行,两侧一起动),并加 `LLMMaterial.Enums.RoundTrip` 钉住"每个引擎枚举值导出成 token 后必须解析得回自己"。同轮还修:`--domain DeferredDecal` 之类在 builder 的枚举分支里被静默降级成 Surface(三元链只认 3 个域 → 改成穷尽 switch,`ELLMMaterialDomain` / `ELLMBlendMode` 补齐缺失值);`"VirtualTexture"` 这个老词表写法被误报成 Unknown domain(现在是文档化的别名,判定改成查表而不是"结果是不是默认值");编辑器面板**从不显示构建 warning**(那些正是静默降级信号,现在跟 shell 的 `[warnings]` 段对齐)、**不报 substrate 不可往返的警告**、**把 schema 写进插件源码树**(`Plugins/LLMMaterial/Config/MaterialExpressionSchema.json` —— Fab 装到引擎目录时那路径压根不存在,写源码树又污染仓库;现在走 registry 的导出器,跟命令同形状同落点)、**跟 shell 导出到不同目录**(现在统一 `Saved/LLMMaterial/`)。GUI 新增 Domain / Blend 两个覆盖下拉(可选项与 shell 的 `--domain` / `--blending` 同源,留空 = 用 `.llmmat` 里的值);ability 工具列表的 `version` 从写死的 `"1.0"` 改成读插件描述符(结构上不可能再漂),`--domain` / `--blending` 的合法值列表也改成从真源派生。删掉编辑器模块那个**空工具栏 section**(按钮早没了,section 留着)与四个没人消费的 Subsystem 配置键(`ExamplesPath` 还在 Fab 安装时指错路径)。
- **session(substrate-round-trip) (2026-10-25)**: substrate 材质的 export → generate 往返修好 —— 以前 `material export` 把 substrate 拓扑**拍平**成普通表达式节点(slab / 组合 / ShadingModels 节点全当普通节点),而 DSL 的 `substrate` 块那条路只在 ".llmmat → .llmmat" 时才可达 ⇒ 导出的文件再 generate 会报 `Orphaned node` / `Dangling node`(substrate 根节点没有消费者)。现在导出侧**逆向重建拓扑**:slab 分组回 `substrate.slabs`、组合树回 `substrate.root`、substrate 专属节点从扁平节点表剔除(否则重新导入会重复建节点),常量内联回 slab 输入。顺带修掉构建侧一个更隐蔽的病:slab 输入接线是一串 17 个 pin 的 if/else 链、且每个分支都只 `Cast<UMaterialExpressionSubstrateSlabBSDF>` ⇒ Hair / Unlit / Eye / SingleLayerWater 的输入被**静默丢弃**;现在两侧都改成**按属性名反射读写**(DSL 的输入名 == UE 的 FExpressionInput 属性名),新引脚自动通吃。导出侧与构建侧的 slab/composition 词表收进 `Core/LLMMaterialSubstrateCodec` 一处,两侧共用。导出警告从"一律不可往返"改成**只报真正有损的部分**(嵌套组合 / Select 阈值 ≠ 0.5 / 没有 FrontMaterial)。新样本 `SubstrateHybrid.llmmat`(普通表达式节点驱动 slab 输入 = 混合模式)+ 自动化测试 `LLMMaterial.Substrate.ExportRoundTrip`。
- **session(sample-battery) (2026-10-25)**: 样本集升级 + 路上修的五个插件缺陷 —— 样本(12 个 .llmmat)从"1~2 节点小玩具"变成真实能力面(参数 / Fresnel / Panner+Time / 贴图通道 / 顶点色 / Masked+opacityMask / 两种 Substrate 组合算子),并加了 `LLMMaterial.Samples.AllSamplesParse` 当永久回归网(遍历 Config/Examples,正样本必须解析且图自洽,`Invalid*` 负样本必须干净失败)。样本电池(generate → shader 编译 → export 往返)逼出五个**静默降级**级缺陷,全修了:① `output` 段的**常量被静默丢弃**(metallic/roughness/specular/opacity/opacityMask 全部退回引擎默认值,命令照报 Success —— `MetalMaterial` 的 `"metallic": 1.0` 根本不是金属);② 每次 generate 都**空等满 60s** shader 闸门(等 game-thread map 回贴的那一步是 editor tick 做的,而命令正堵着那个 tick ⇒ 改调 `IsCompilationFinished()`,60.7s → 0.6s);③ **构建 warning 在成功路径上完全不可见**(属性名不存在 / 连不上引脚都只进日志 ⇒ 现在成功消息带 `[warnings]` 段);④ **类型别名表放错层**(Lerp→LinearInterpolate 在 builder 里,parser 先拒 ⇒ 那半张表是死代码 ⇒ 挪到 expression registry);⑤ **枚举按名字填不进去**(只硬编码了噪声函数的 NOISEFUNCTION_ 前缀 ⇒ 贴图的 `SamplerType: Normal` 填不进去,法线贴图按 Color 采样 ⇒ shader 编译失败)。SKILL.md 的表达式属性表同步更正(`Power` 的输入叫 `Exponent` 不是 `Exp`、`Desaturation.Fraction` 是输入不是属性、`StaticSwitchParameter` 两路是 A/B、Fresnel 在 5.8 只剩 `Exponent`、法线贴图必须显式 `SamplerType: Normal`)。**已知缺口**:substrate 材质的 export→generate 往返仍不可行(导出拍平成表达式节点),export 现在会如实输出 WARNING。
