---
name: llmeasyshell-ability-argsjson-format
description: LLMEasyShell C++ ability handler ArgsJson 是 JSON 数组（不是带 _args key 的 object），自定义 ability 必须按数组解析
metadata: 
 node_type: memory
 type: reference
 originSessionId: ef8b3fa8-6f82-4aa1-b284-c82358983b0a
---

# LLMEasyShell Ability ArgsJson Format

注册一个继承 `ULLMEasyShellAbilityCommandObject` 的自定义 C++ ability 时,`Execute_Implementation(Command, ArgsJson)` 接收的 `ArgsJson` **是 JSON 数组**,不是带 `_args` key 的 object。

**实际格式**:
```json
["positional1", "positional2", "--flag1", "value1", "--flag2", "value2"]
```

**错误写法** (会导致每个命令都返回 `E_BAD_ARGS`):
```cpp
TSharedPtr<FJsonObject> JsonObj;
auto Reader = TJsonReaderFactory<>::Create(ArgsJson);
FJsonSerializer::Deserialize(Reader, JsonObj); // ❌ 数组 token 被拒
```

**正确写法** (仿 `LLMMaterialCommandHandler`):
```cpp
TSharedPtr<FJsonValue> JsonValue;
auto Reader = TJsonReaderFactory<>::Create(ArgsJson);
FJsonSerializer::Deserialize(Reader, JsonValue); // ✅
if (JsonValue->Type != EJson::Array) return false;

const TArray<TSharedPtr<FJsonValue>>& Arr = JsonValue->AsArray();
// 走 Arr 拆 positional vs --key value 对
```

**Why**: 见 `LLMEasyShell/Private/LLMEasyShellSubsystem.cpp:617-624`,dispatcher 总是这样构造 ArgsJson:
```cpp
FString ArgsJson = TEXT("[");
for (int32 i = 0; i < ActualArgs.Num(); i++) {
 if (i > 0) ArgsJson += TEXT(", ");
 ArgsJson += FString::Printf(TEXT("\"%s\""), *ActualArgs[i].Replace(...));
}
ArgsJson += TEXT("]");
```

**基类位置**: `ULLMEasyShellAbilityCommandObject` 在 `LLMEasyShell/Public/LLMEasyShellTypes.h:628`,**没有独立** `LLMEasyShellAbilityCommandObject.h`。include 用 `LLMEasyShellTypes.h`。

**附**: `FQuixelError::FormatSuccess(Output)` 会把 `"` 替换成 `'`,所以 `output` 字段里看到 `'{...}'` 不是 bug,是设计。

LLMQuixel 的 PR2 踩过这个坑,commit `9b93f40` 修复。
