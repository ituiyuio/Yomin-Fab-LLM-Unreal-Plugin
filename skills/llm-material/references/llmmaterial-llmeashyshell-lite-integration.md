---
name: llmmaterial-llmeashyshell-lite-integration
description: LLMMaterial 注册到 LLMEasyShell Lite + full 双通道:**双注册**(两个都装时同时进 Lite 和 full 的 ability 表),ClassPath/JSON key 差异,handler 接口共用
metadata:
 node_type: memory
 type: project
 originSessionId: 2003556a-d100-4277-bcae-80fe8e188578
---

LLMMaterial 插件通过 `RegisterAsLLMEasyShellAbility()` (LLMMaterialModule.cpp:268-274) + `RegisterAsLLMEasyShellLiteAbility()` (LLMMaterialModule.cpp:286-292) 双注册到 LLMEasyShell 家族。**双注册策略**:Lite 与 full 是两个独立 .exe、两条独立端口、各自 ability 表,**两个都装时同时注册到两边**(2026-06-07 升级,之前是 Lite 优先 + full fallback);只装一个就只注册那一个;都不装就只 log 一行,GUI 仍工作。

**Why dual-register safe(为什么不会混淆)**:Lite 与 full 跑在不同 `.exe`(`llmshelllite.exe` vs `llm-shell.exe`)+ 不同端口段(15201-15250 vs 15151-15200)+ 各自独立的 `RegisterAbilityCommandHandler` 表。单个 LLM agent 只连一边,看不到另一边,不存在重复 ability 干扰。

**How to apply:** 任何新增的 LLMMaterial/LLMVFX/LLMDynamicUI 等插件,都该复用这个双注册模式 — 不是 Lite 优先,是 Lite 和 full 都注册。`FindShellSubsystem(ClassPath, ...)` helper 提取出来共享。完整 pattern + 跨工程行为表 → **车床技能 llm-ue-asset-generator-methodology 的阶段五 5.3**(source of truth);快速参考表 → `.claude/skills/llm-easy-shell-lite/SKILL.md` 方式三。链接:[[fab-cli-cleanup-skill]]、[[llmshelllite-port-segmentation]]。

**关键 API 差异**(Lite vs full,都要支持):

| API | LLMEasyShell (full) | LLMEasyShellLite |
|---|---|---|
| Class path | `/Script/LLMEasyShell.LLMEasyShellSubsystem` | `/Script/LLMEasyShellLite.LLMEasyShellLiteSubsystem` |
| TCP 端口段 | 15151-15200 | 15201-15250 |
| CLI 二进制 | `llm-shell.exe` | `llmshelllite.exe` |
| `RegisterAbilityJson` 签名 | `void(FString, FString)` | `bool(FString, FString)` (反射调,返回 bool 忽略) |
| `RegisterAbilityCommandHandler` 签名 | `(FString, UObject*)` | `(FString, UObject*)` ← 完全一样 |
| `UnregisterAbility` 签名 | `(FString)` | `(FString)` ← 完全一样 |
| JSON key for plugin name | `"pluginName"` | `"plugin"` |
| Handler contract | `ExecuteWithResult(Command, ArgsJson) -> FString` | 同(也 fallback `Execute` 函数) |

**JSON 输出必须双写 `plugin` + `pluginName`** —— 一个 key 都不能漏,否则 Lite 或 full 拿不到 plugin 字段。BuildAbilityInfoJson 已经是这样了。

**模块依赖**:Build.cs **不加** `LLMEasyShell` / `LLMEasyShellLite`,`.uplugin` 也**不在 `Plugins[]` 列**Shell — 完全靠运行时反射。这样 LLMMaterial 在任何 host project 都能编译,Shell 装不装都不影响。**这是关键的"软依赖"实现,任何后续插件参考时要复制这个模式,不要硬加 PrivateDependency**。

**关键文件**:
- `Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterialModule.cpp:268-292` — `RegisterAsLLMEasyShellAbility()` (L268-274) + `RegisterAsLLMEasyShellLiteAbility()` (L286-292) 双注册主入口(active working sample;旧 fossil `RegisterAbilityHandlers()` 是 **phantom function**(grep `Plugins/` 0 hit,源代码根本不存在 — 跟 tool-fix-112/120 同 rootCause family,容易让 LLM 误以为有这函数),`RegisterCommandHandlers()` 实际是 L82-85 的空 stub,2026-06-07 迁移到 Ability 系统后已废弃)
- `Plugins/LLMMaterial/LLMMaterial.uplugin` — Plugins[] 只列 EditorScriptingUtilities,不列 Shell
- `Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterial.Build.cs` — 不依赖 Shell 模块
- `.claude/skills/llm-ue-asset-generator-methodology/SKILL.md` — **车床技能** 阶段五 5.3,canonical pattern + 跨工程行为表
- `.claude/skills/llm-easy-shell-lite/SKILL.md` — 方式三,快速参考表(指向车床技能)

**陷阱**:FindObject<UClass> 找 ClassPath 时,如果 host project 没装,会返回 nullptr;此时 helper early return false,跳过那一边的注册,不报错。
