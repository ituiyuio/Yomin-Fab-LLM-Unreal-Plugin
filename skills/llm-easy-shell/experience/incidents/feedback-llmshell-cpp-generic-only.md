---
name: feedback-llmshell-cpp-generic-only
description: "LLMEasyShell C++ 保持纯通用,Survivor 子系统特定 helper 提取到独立 LLMSurvivorGameplayLib 模块"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: bbc9370f-a530-472b-a5bc-e1354088191a
---

LLMEasyShell C++ (LLMEasyShellGameplayLib.h/.cpp) 只允许通用功能(actor 反射/property setter/function call/log 等)。子系统特定 helper 提取到独立模块。

**Why:** LLMEasyShell 是通用 LLM 脚手架工具,作为其他项目的脚手架可复用,不应被单个游戏的子系统污染。提取后 LLMEasyShell 可单独发布且与游戏代码解耦。

**How to apply:**
- LLMEasyShell C++ 通用原语保持
- 子系统特定 helper 放独立模块(如 LLMSurvivorGameplayLib)
- 提取 143 个 Survivor 前缀 helper 到 LLMSurvivorGameplayLib(commit 865b73b)
- Python abilities 通过函数名字符串继续调用(UE 反射按 function name 查找,模块路径透明)
- Build.cs 依赖: LLMSurvivorGameplayLib 依赖 LLMEasyShell(复用 FindSurvivorPlayerByName / GetPIEWorld) + CODEO(访问 ASurvivorPlayerCharacter / 各种 Component)

**模块结构参考(LLMSurvivorGameplayLib):**
```
Plugins/LLMEasyShell/Source/LLMSurvivorGameplayLib/
 LLMSurvivorGameplayLib.Build.cs
 Public/LLMSurvivorGameplayLibFunctionLibrary.h
 Private/LLMSurvivorGameplayLibFunctionLibrary.cpp
```

**统计(commit 865b73b):**
- LLMEasyShellGameplayLib.h: 1166 → 578 行(-588)
- LLMEasyShellGameplayLib.cpp: 5103 → 1350 行(-3753)
- LLMSurvivorGameplayLib: 4 新文件 + 3971 行
- .uplugin: +1 module entry

**相关:** [[settings-v1-2026-06-25]]
