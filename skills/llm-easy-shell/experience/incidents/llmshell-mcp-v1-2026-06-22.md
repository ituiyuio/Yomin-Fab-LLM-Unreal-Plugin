---
name: llmshell-mcp-v1-2026-06-22
description: 2026-06-22 mcp command v1.0 落地 + 4 必修 review findings (WriteClientConfiguration / Target.cs V6 / schema dup pins)
metadata: 
 node_type: memory
 type: project
 originSessionId: 797432ec-2f6e-47b2-8ae8-062ab5fcd05a
---

2026-06-22 一次 /git_precommit 触发的 code-review,跑 10 个 finder 角度 + UE 5.8 源码验证,出 15 findings,落地 4 commits:

**Commits(顺序)**:
1. `4b7258c` feat(llmshell): mcp command v1.0 — UE 5.8 ModelContextProtocol plugin bridge
2. `eaa233b` fix(ue58): CODEOEditor.Target.cs — keep V6 + bOverrideBuildEnvironment
3. `17ef1b6` fix(llmvfx): NiagaraModuleSchema — DistributionCurveFloat pins + Abs_Float + defaults
4. `07e9e8f` docs(skills): mcp command + fab-submit-pipeline + LLMEasyShellLite updates

**5 必修 review findings(都在 commit 1 落地)**:
- `mcp config` 用 `UE::ModelContextProtocol::WriteClientConfiguration(EModelContextProtocolClient, uint32, FString, FString)` 公开 API(UE 5.8),不要手写 JSON。引擎 `ModelContextProtocolClientConfig.cpp:31-37` 已正确处理 VSCode 的 `"servers"(非 mcpServers)+type field` 和 Gemini 的 `"httpUrl"(非 url)` shape 差异,手写 4 套会让 VSCode + Gemini 配置被对方客户端静默忽略
- `mcp start` 必须验证 `Module.GetServer()->IsServerRunning()`,`StartServer` 返回 void,port-in-use / permission-denied 会 silent no-op,原版报告 "Started" 是误导
- `HandleConfig` 显式拒收 flag args(只接受 client name positional),避免位置/flag 消歧
- `Module.GetServer()` 缓存到 local,避免 2x 重复 call + 潜在 race window

**2 必修独立 commit**:
- `Target.cs` V7 + Unreal5_8 切换是回退 `e9ec507` 修复 — V7 在 UE 5.8 因 3 个 warning 升 Error 会触发 UBT abort,`BuildEnvironment=Unique` 是 Source Build only。注释里加"不要再切 V7 + Unreal5_8"防重蹈覆辙,后续切 V7 必须同时 `ModuleRules.WarningsOverride` + 清干净 unreachable code
- NiagaraModuleSchema 自动 regen 脚本 4 个 bug(已修):重复 `LoopCount` pin / 拼写错 `CurveParameterType:` / 3 个 color alpha 默认值变成 XMM 垃圾值(1.50589e+16, 5.52251e+19, 10267.3 → 0.0000) / 删 `Abs_Float` 模块

**Why**: review 主动挖掘根因能拦下至少 1 个会进 master 的回归(V7 切换)。CLAUDE.md "优先挖掘问题根源" 的实际案例。

**How to apply**: 后续加 LLMEasyShell 新 shell command 时:
1. 引擎有公开 API 就调 API,不要自己重写
2. void 返回值的引擎 API 必须有 ground-truth verification(本例 `IsServerRunning()`)
3. UE 5.8 V7 切换是高风险,必须 `ModuleRules.WarningsOverride` 配套
4. LLMVFXSchema regen 脚本要 fix XMM 读取 + pin 去重检查