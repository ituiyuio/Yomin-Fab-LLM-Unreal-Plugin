---
name: llmeasyshell-lite-phase6-fixes-2026-06-01
description: "LLMEasyShell Lite Phase 6 修复总结 (2026-06-01): 5 critical bug + 4 quality issue + 路径不一致"
metadata: 
 node_type: memory
 type: project
 originSessionId: 967ae0f0-0803-4aa9-94ce-cafc6386a200
---

LLMEasyShell Lite Phase 6 质量审查修复 (2026-06-01)。

**5 critical bug 全部修复：**
- Bug #1: ShellCommand_Info/Log 砍掉 FLiveCodingLogDevice，改用简化版 (CVar + ILiveCodingModule.IsCompiling)；log --compile 提示用户改用 Advanced
- Bug #2: PythonAbilityRegistry.cpp 硬编码 "Plugins/LLMEasyShell/PyAbilities/" 改为 GetPythonPyAbilitiesRoot() 动态路径
- Bug #3: ShellCommand_Help 裁剪到 9 个 Lite 命令 (ls/cat/find/info/help/discover/gamestate/log/msglog)
- Bug #4: LLMEasyShellLiteTypes.h 移除 19 个孤儿 UCLASS (1886→1197 行)
- Bug #5: Python 包 `LLMShellAbilities` 重命名为 `LLMShellAbilitiesLite`，避免与 Advanced 冲突

**4 quality issue 全部修复：**
- FLLEasyShellLiteTickable → FLLMEasyShellLiteTickable (LLMEasyShellLiteSubsystem.cpp:31,34,49,122,146)
- Build.cs 移除未用依赖 (SourceControl/ImageCore/ImageWrapper/RenderCore/RHI)
- 删除 PathResolverChain 死代码 (5 cpp + 6 UCLASS)
- 移除 IsLiveCodingActive 占位 + UE_LOG(LogTemp) → UE_LOG(LogLLMEasyShellLite)

**路径不一致修复 (重要)：**
- 物理目录 `Plugins/LLMEasyShell_Lite/` (带下划线) → `Plugins/LLMEasyShellLite/` (无下划线，与 .uproject 一致)
- 详见 [[llmeasyshell-lite-plugin-paths.md]]

**编译验证：**
- 触发 livecoding 编译，结果是 0 errors 但 UBT 报 958 actions 失败
- 失败原因：engine 三方库 includes 找不到 (static.c, sse_mathfun_extension.h, oodle2base.h) — 与 Lite 代码无关，是环境问题
- 目录重命名可能触发了 Live Coding 全量重建；建议下次先测试只改 .cpp 的增量编译

**Types.h 仍需观察：**
- 剩余 9 个 UShellCommand_ + UShellCommandBase = 10 类
- 1197 行，相对原 1886 行砍掉 ~37%

**没改但仍存的：**
- `MainFrame` 依赖：TcpServer.cpp 在 ProcessCommand 调 RequestCloseEditor
- PropertyRouter.cpp/h 存在但 Subsystem 不引用
- LLMEasyShellReflection.cpp 97KB — 大且未被 PythonAbilityRegistry 之外调用
