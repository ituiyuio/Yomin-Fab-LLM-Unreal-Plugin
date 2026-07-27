---
name: ue-python-ustruct-field-naming
description: "UE Python 端访问 USTRUCT BlueprintReadOnly UPROPERTY 时自动 snake_case + 去 b 前缀：bSuccess→success, FilePath→file_path"
metadata: 
 node_type: memory
 type: project
 originSessionId: f8614493-0e5f-4c8b-8e82-303049c4338b
---

**问题**: 在 LLMEasyShell 的 Python ability 中调用返回 USTRUCT 的 C++ 函数时，`getattr(result, 'bSuccess', None)` 永远返回 None。导致所有返回 USTRUCT 的 C++ 能力看似失败（实际是 Python 端读不到字段值）。

**UE 命名转换规则**：

C++ UPROPERTY 经 BlueprintReadOnly 暴露给 UE Python 时，遵循 PEP 8 自动转换：
- `bool bSuccess` → Python `result.success`（去 `b` 前缀）
- `FString FilePath` → Python `result.file_path`（snake_case）
- `int32 Width` → Python `result.width`
- `FString Source` → Python `result.source`
- `FString Error` → Python `result.error`

**诊断方法**:
```python
all_attrs = [a for a in dir(result) if not a.startswith('_')]
# 示例输出: ['success', 'file_path', 'width', 'height', 'source', 'error', 'base64', ...]
```

**安全写法**（兼容两种风格）:
```python
success = bool(getattr(result, 'bSuccess', getattr(result, 'success', False)))
file_path = str(getattr(result, 'FilePath', getattr(result, 'file_path', '')) or '')
```

**Why**: UE 5.x 的 PythonScriptPlugin 内部对 BlueprintReadOnly UPROPERTY 自动应用 camelCase → snake_case 转换，并剥离 bool 的 `b` 前缀（UE C++ 编码规范要求）。原始 C++ 名字仅在反射层（`UFunction::FindFunctionByName` 等）有效。

**How to apply**:
- 任何新写 LLMEasyShell Python ability 调用 C++ 返回 USTRUCT 的函数时，**必须**用 snake_case 字段名（或 fallback 写法）
- 调试时先 `print(dir(result))` 列出真实字段名
- 现有 `_bool_val` / `_str_val` / `_int_val` helper 用了 `getattr(obj, attr) or getattr(obj, attr.lower())` 兜底，但仍按 C++ 风格传 `'bIsPIE'`、`'CurrentLevelPath'`，可能误导
