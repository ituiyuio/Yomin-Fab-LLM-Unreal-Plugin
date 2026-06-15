# LLMEasyShell Python Ability 系统经验

> 4 个教训：执行模式 / 输出捕获 / 参数传递 / 字段名解析

---

## 教训 1：Python ability 必须用 `ExecuteFile` 模式 + 读 `LogOutput`

**场景**：所有 `python <name>` 调用都失败，返回 `SyntaxError: multiple statements found while compiling a single statement` 和空 result。

**根因**（2 个独立 bug）：

1. `ExecuteStatement` 模式只支持单语句（`1+1` 这种），多行 Python（try/except、函数定义）必须用 `ExecuteFile`
2. `ExecuteFile` 模式成功时 `CommandResult` 是 `None`，真正的输出在 `CommandEx.LogOutput[]` 数组里

**修复模式**（`PythonAbilityRegistry.cpp`）：

```cpp
// 1. 切到 ExecuteFile
CommandEx.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;

// 2. 从 LogOutput 提取输出（不是从 CommandResult）
FString CombinedOutput;
for (const FPythonLogOutputEntry& Entry : CommandEx.LogOutput) {
    if (!Entry.Output.IsEmpty()) {
        if (!CombinedOutput.IsEmpty()) CombinedOutput += TEXT("\n");
        CombinedOutput += Entry.Output;
    }
}
return CombinedOutput;
```

**配套**：旧 ability 缺 `LLMShellAbilities/registry.py`（Ability 基类）需要补上。

**经验**：写 `python <name>` 调用方时，如果能力返回 `success: true` 但 `output: ""`，**第一反应**是检查 LogOutput 而不是怀疑命令没跑。

---

## 教训 2：Python ability 返回 dict 必须含 `"output"` 键才能在 IPC 显示

**场景**：`hd3dpostprocess status` 返回 50 行数据但 IPC 的 `output` 字段是空字符串。

**根因**：LLMEasyShell 的 IPC 协议靠 `result["output"]` 键回传文本。`unreal.log(json.dumps(result))` 把 JSON 写入 `LogPython`，但 IPC 只解 `output` 字段。

**两种可靠修法（都做最稳）**：

```python
# 修法 1: 显式构造 output
lines = ["Total: 24", "Lights: 3", ...]
for line in lines:
    unreal.log(line)
return {"success": True, "output": "\n".join(lines), "data": {...}}

# 修法 2: 不依赖 return value 传数据，关键信息都 unreal.log
```

**经验**：所有 Python ability 都遵循"双输出"模式 —— `unreal.log()` + `output` 键。否则用户看到的 `output: ""` 调试起来要 grep log file。

**仍未升级的旧 ability**（需要批量迁移）：`asset.py` / `blueprint.py` / `datatable.py` / `property.py` —— 仍用旧 `_bool_val` helper，不带 `output` 构造。

---

## 教训 3：`_call_with_world` 必须 `inspect.signature` 动态判断 + 位置参数传递

**场景**（2026-05-28 commit 1039074 后所有 Python 能力失效）：

```
TypeError: main() got an unexpected keyword argument 'world'
```

**根因**（`PythonAbilityRegistry.cpp:294-295` 旧代码）：

```python
# 旧 bug：死写 world= 关键字
if len(params) >= 2 and params[1] in ('world', 'context'):
    return fn(args_str, world=_world)  # ❌ 死写 world
```

用户函数签名是 `def main(args, context=None):` 时（最常见），传 `world=` 就是未知 kwarg。

**第一代修复**（params[1] 动态 kw 名）：

```python
if len(params) >= 2 and params[1] in ('world', 'context'):
    return fn(args_str, **{params[1]: _world})  # ✅ 动态 kw 名
```

**当前实现**（`PythonAbilityRegistry.cpp:315-327`，2026-06-01 commit 50bc549）—— **更通用**：用 `inspect.signature` 检测函数签名，只要接受 2+ 位置参数就把 `_world` 作为第二参数传入，不再依赖参数名白名单。

```python
def _call_with_world(fn, args_str):
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
    except (TypeError, ValueError):
        return fn(args_str)
    # 任何接受 2+ 位置参数的 ability 都把 _world 作为第二参数传入。
    # 这比之前硬编码的 ('world', 'context') 白名单更通用——ability
    # 端可以自由命名第二参数（w、ctx、env 等）。
    positional = [p for p in params if p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)]
    if len(positional) >= 2:
        return fn(args_str, _world)
    return fn(args_str)
```

**经验**：写自定义 Python ability 时推荐 `def main(args, context=None):` 签名（位置参数 + context 默认值），跟 dispatcher 完全兼容，参数名可以自由（world / context / w / ctx 都行）。

**影响范围**：所有 Python 能力（editor / material / gameplay / scene / property / bpprop ...）

---

## 教训 4：`_candidates` 漏掉剥 b 后的 snake_case，所有 b 前缀 bool 字段读不到

**场景**：`python editor screenshot async=true` 走 `else` 分支，返回 C++ 的 Error 字符串而不是 Python 期望的 `is_async=True` 判定。`python editor state` 的 `pie` 永远是 `false`。

**根因**（`_unreal_helpers.py:_candidates`）：

旧代码剥 b 后的候选只有 `'IsAsync'` 和 `'isasync'`，**漏掉 `'is_async'`**（剥 b 后的 snake_case）。UE Python 实际暴露的是 `is_async`（snake_case + 去 b 前缀），所以候选列表里**永远没有正确形式**。

```python
# 旧代码
out.append('bIsAsync')     # 原名
out.append('b_is_async')   # 原始名 snake
out.append('bisasync')     # lowercase
out.append('IsAsync')      # strip b
out.append('isasync')      # lowercase of stripped
# ❌ 缺 'is_async' = snake_case of stripped
```

**修复**（`_unreal_helpers.py`）：

```python
def _candidates(name: str) -> list[str]:
    out: list[str] = [name]
    snake_str = _to_snake(name)
    if snake_str != name: out.append(snake_str)
    out.append(name.lower())
    if name.startswith('b') and len(name) > 1 and name[1].isupper():
        stripped = name[1:]
        out.append(stripped)
        out.append(stripped.lower())
        # ★ 关键：剥 b 后的名也要做 snake_case
        snake_stripped = _to_snake(stripped)
        if snake_stripped != stripped and snake_stripped not in out:
            out.append(snake_stripped)
    return _dedup(out)

def _to_snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append('_')
        out.append(ch.lower() if i == 0 or not name[i - 1].isupper() else ch)
    return ''.join(out)
```

**调试技巧**：临时加 `return {"success": False, "error": f"{err} || DEBUG fields: {_uh.field_diagnostic(result)}"}`，看 `Available fields on X: [...]` 列表里真实字段名跟 `_candidates(name)` 输出 diff。

**经验**：
- 改完 `_unreal_helpers.py` 必须 `python reload`（只清 Python sys.modules 缓存，C++ DLL 不变）
- 受影响字段：`bIsAsync` / `bIsPIE` / `bIsPaused` / `bSuccess` / `bIsCompiling`
- 字段读不到的**第一反应**就是 `_uh.field_diagnostic()` 打印

---

## 经验速查

| 症状 | 教训 |
|------|------|
| SyntaxError + 空 output | 教训 1：检查执行模式 / LogOutput |
| `output: ""` 但 log 有数据 | 教训 2：缺 `output` 键 |
| `unexpected keyword 'world'` | 教训 3：参数名死写 bug |
| bool 字段永远 default | 教训 4：`_candidates` 漏 snake_case |
