---
name: know_how_create_cpp-abilitys
description: |
  LLMEasyShell Ability 注册接口。
  用于为 LLMEasyShell 添加新命令（C++ 或 Python）。
  触发词：注册 ability、新增命令、扩展 shell、注册 pyability
---

# LLMEasyShell Ability 注册

LLMEasyShell 支持两种 Ability 注册方式：

| 方式 | 语言 | 注册方式 | 适用场景 |
|------|------|----------|----------|
| C++ Ability | C++ | `RegisterAbility()` + 命令处理器 | 复杂逻辑、性能敏感、反射操作 |
| PyAbility | Python | 放置 `.py` 文件到 `abilities/` 目录 | 快速原型、脚本化逻辑、资产操作 |

---

## 方式一：C++ Ability

### 最小示例

```cpp
#include "LLMEasyShellSubsystem.h"

// 1. 定义 Ability
FLLMEasyShellAbilityInfo Info;
Info.Name = TEXT("mycmd");
Info.Commands = {{ TEXT("hello"), TEXT("mycmd hello <name>"), TEXT("Say hello") }};

// 2. 注册
void MyPlugin::Startup() {
    if (ULLMEasyShellSubsystem* Shell = GEditor->GetEditorSubsystem<ULLMEasyShellSubsystem>()) {
        Shell->RegisterAbility(TEXT("mycmd"), Info);
        // 注册处理器...
    }
}
```

### 命令处理器

```cpp
UCLASS()
class UMyCmdHandler : public ULLMEasyShellAbilityCommandObject {
    GENERATED_BODY()
public:
    FString Execute_Implementation(const FString& Cmd, const FString& ArgsJson) override {
        // ArgsJson: {"_args":["arg1"],"name":"value"}
        if (Cmd == TEXT("hello")) {
            return TEXT("{\"success\":true,\"output\":\"Hello!\"}");
        }
        return TEXT("{\"success\":false,\"error\":\"Unknown\"}");
    }
};

// 3. 注册处理器
Shell->RegisterAbilityCommandHandler(TEXT("mycmd"), NewObject<UMyCmdHandler>());
```

### 参数解析

`ArgsJson` 结构：
```json
{
    "_args": ["positional", "args"],
    "_command": "hello",
    "_subcommand": "hello",
    "named_param": "value"
}
```

### 返回格式

```json
{"success": true, "output": "..."}
{"success": false, "error": "..."}
```

---

## 方式二：Python Ability (PyAbility)

将 `.py` 文件放入 `Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/` 目录，框架自动发现并注册。

### 最小示例

```python
# abilities/my_ability.py
from registry import Ability, Command, Context

class MyAbility(Ability):
    """My custom ability."""

    name = "my_ability"
    version = "1.0.0"

    def get_commands(self):
        return [
            Command("hello", "Say hello", ["name"]),
        ]

    def execute(self, command, args, context):
        if command == "hello":
            name = args.get("name", "World")
            context.log(f"Saying hello to {name}")
            return {
                "success": True,
                "output": f"Hello, {name}!",
            }
        return {"success": False, "error": f"Unknown command: {command}"}

def register(reg):
    """Called by the framework to register this ability."""
    reg.register_ability(MyAbility())
```

### Context 对象

`execute()` 接收的 `context` 参数提供以下方法（`from registry import Context`
走的是 `LLMShellAbilities/registry.py` re-export shim,底层指向
`LLMShellAbilities/abilities/__init__.py` 的真 Context 9 个属性,2026-06-29
tool-fix-130 修复了原 stub `Context` 只有 4 方法的 phantom 化石）:

| 方法 | 说明 |
|------|------|
| `context.world` | 当前 UWorld |
| `context.ability_name` | 当前 ability 名称 |
| `context.command` | 当前命令名称 |
| `context.args` | 命令参数字典 |
| `context.log(msg)` | 记录日志 |
| `context.get_property(asset_path, property_name)` | 读取资产属性 |
| `context.set_property(asset_path, property_name, value)` | 写入资产属性 |
| `context.call_function(asset_path, func_name, **kwargs)` | 调用资产函数 |
| `context.load_asset(asset_path)` | 加载资产 |

### 关键文件

| 文件 | 用途 |
|------|------|
| `LLMEasyShellTypes.h` | `FLLMEasyShellAbilityInfo` / `FLLMEasyShellAbilityCommandMeta` |
| `LLMEasyShellSubsystem.h` | `RegisterAbility` / `RegisterAbilityCommandHandler` |
| `LLMEasyShellSubsystem.cpp` | 内置 Ability 注册实现参考 |
| `PythonAbilityRegistry.h` | PyAbility 自动发现和调度 |
| `Content/Python/LLMShellAbilities/registry.py` | Python Ability 基类的 re-export shim (2026-06-29 后;底层指向 `abilities/__init__.py`) |
| `Content/Python/LLMShellAbilities/abilities/__init__.py` | Python Ability 基类真正的 source-of-truth (`Ability`, `Command`, `Context` 9 属性) |
| `Content/Python/LLMShellAbilities/abilities/_example.py` | PyAbility 参考实现 |

---

## 方式三:Reflection-only 注册(跨工程兼容,Lite + full 双注册)

适用场景:**第三方插件想在 host project 装了 LLMEasyShell / LLMEasyShellLite 时自动暴露一个 ability,但 host 不装也要能编译/运行**。典型例子 `LLMMaterial`(material ability)、`LLMVFX`(vfx ability)。

> **完整代码模板与设计原则**见车床技能 [`llm-ue-asset-generator-methodology`](../../llm-ue-asset-generator-methodology/SKILL.md) 的「阶段五:Shell Ability 系统集成」步骤 1-4。本节只列**速查表**,不重复代码骨架。

### 跨工程行为速查表

| host project 装了… | 注册行为 | LLM 调用路径 |
|---|---|---|
| 只装 full | 注册到 full(15151-15200) | `llm-shell [ability] …` |
| 只装 Lite | 注册到 Lite(15201-15250) | `llmshelllite [ability] …` |
| **两个都装** | **双注册**:full 和 Lite **各自 ability 表里都有** | 两条 shell 都能调,LLM 选哪个都行 |
| 都不装 | 不注册,仅写一条 Log;**GUI 面板照常工作** | 仅缺 shell 命令,插件其他功能不受影响 |
| 编译期(任何组合) | host 不装任何 Shell 也能编译 | 反射调用,无符号依赖 |

> **为什么双注册安全**:Lite 与 full 跑在 **不同 .exe**(`llmshelllite.exe` vs `llm-shell.exe`)+ **不同端口段**(15201-15250 vs 15151-15200)+ **各自独立的 `RegisterAbilityCommandHandler` 表**。同一个 LLM agent 只连一条 shell,看不到对面,不存在"看到两份命令"的混淆。

### Lite vs full 关键差异速查

| 维度 | LLMEasyShell (full) | LLMEasyShellLite |
|---|---|---|
| Class path | `/Script/LLMEasyShell.LLMEasyShellSubsystem` | `/Script/LLMEasyShellLite.LLMEasyShellLiteSubsystem` |
| TCP 端口段 | 15151-15200 | 15201-15250 |
| CLI 二进制 | `llm-shell.exe` | `llmshelllite.exe` |
| JSON key for plugin name | `"pluginName"` | `"plugin"` |
| AbilityInfo JSON | **同一份必须双写**`plugin` + `pluginName`,两边才都能识别 | (同左) |

### 反射调用的三个 UFunction 名

| 用途 | 函数名 | 参数(struct) |
|---|---|---|
| 注册 ability JSON | `RegisterAbilityJson` | `{ FString AbilityName; FString AbilityJson; }` |
| 注册命令处理器 | `RegisterAbilityCommandHandler` | `{ FString AbilityName; UObject* Handler; }` |
| 注销 ability | `UnregisterAbility` | `FString AbilityName` |

### 反模式提醒

❌ **不要用"Lite 优先 + full fallback"** —— 找到 Lite 就 `return;` 看似避免重复,实际上让"full shell 也能用同一份 ability"成为不可能。**新代码一律双注册**。

❌ **不要在 `Build.cs` 加 `LLMEasyShell` / `LLMEasyShellLite` 依赖** —— host 没装会编译失败。

❌ **不要在 `.uplugin` 的 `Plugins[]` 列 Shell 插件** —— 同上,UBT 会去找它们。

✅ **完全靠运行时反射** + JSON 双 key 字段(`plugin` & `pluginName`)+ 双注册(Lite 和 full 都进)。

完整工作示例:`Plugins/LLMMaterial/Source/LLMMaterial/LLMMaterialModule.cpp` 的 `RegisterAsLLMEasyShellAbility()` (L268-274) + `RegisterAsLLMEasyShellLiteAbility()` (L286-292) 双注册主入口 (LLMMaterialModule.cpp:268-292)。`RegisterAbilityHandlers()` / `RegisterCommandHandlers()` 是 L82-85 的空 stub, 2026-06-07 迁移到 Ability 系统后已废弃 (跟 tool-fix-111/llmmaterial-llmeashyshell-lite-integration.md L34 fossil 闭环一致)。
