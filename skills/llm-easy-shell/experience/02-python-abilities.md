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

**根因**（旧代码 @ `PythonAbilityRegistry.cpp:294-295`，2026-06-01 之前的提交；**当前已不在该处**，现行实现见下方 ：358-380）：

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

**当前实现**（`PythonAbilityRegistry.cpp:358-380`，2026-06-01 commit 50bc549）—— **更通用**：用 `inspect.signature` 检测函数签名，只要接受 2+ 位置参数就把 `_world` 作为第二参数传入，不再依赖参数名白名单。

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

<!-- [tool-fix-173 2026-06-29] line drift closure: PythonAbilityRegistry.cpp:294-295 旧代码 + :315-327 当前实现 → 统一 :358-380 (off-by-64 / off-by-31)。痛点: 原 doc 锚定 _call_with_world 函数位置在 PythonAbilityRegistry.cpp:294-295 (旧代码) + :315-327 (当前实现 2026-06-01 commit 50bc549), 但 2026-06 中段 2 次 refactor (commit 9c41a3d 2026-06-08 'refactor(python-registry): 把 _call_with_world + _FakeReg 移入 BuildFullScript 段 + 加 try/except 包裹' + commit 7e3a2b1 2026-06-22 'refactor(python-registry): 拆 ExecutePythonCommand 到 BuildFullScript + RunPythonCommand 分段'), 实际 _call_with_world 函数在 L358-380 (def L358 + 函数体 L359-378 + 收尾 L379-380)。Source-of-truth 4 重 lock 跟新 claim 1:1 锁定: (1) filesystem `grep -n "_call_with_world" Plugins/LLMEasyShell/Source/LLMEasyShell/Private/PythonAbilityRegistry.cpp` = L358 / L372 / L374 (3 处 L358 def + L372 _call_with_world(mod.main,...) + L374 _call_with_world(mod.execute,...), 跟新 doc claim L358-380 1:1); (2) `awk 'NR==294' PythonAbilityRegistry.cpp` = UE_LOG 跟 _call_with_world 无关 (跟原 doc claim L294 旧代码错位); (3) `awk 'NR==315' PythonAbilityRegistry.cpp` = `// Build Python script with newlines for try/except blocks` 注释 跟 _call_with_world 无关 (跟原 doc claim L315 当前实现错位); (4) `awk 'NR==358' PythonAbilityRegistry.cpp` = `FullScript += TEXT("    def _call_with_world(fn, args_str):\n");` 跟新 doc claim 1:1 锁定。Fix scope 2 行锚点 L71 :294-295 → :358-380 + L88 :315-327 → :358-380 (L88 隐含的 '2026-06-01 commit 50bc549' 仍然准确, _call_with_world 引入 commit 没变, 变的只是它在文件中的位置)。Paired completion 跟 tool-fix-173 experience/03 ShellCommand_Set.cpp 跟 LLMEasyShellReflection.cpp + LLMEasyShellPropertyLib.cpp 跟 tool-fix-173 SKILL.md MaxWaitSeconds 同 family 'doc line ref 跟 source 实际行号错位' 但 sub-pattern 不同 (本 fix 是 2 次连续 refactor 派生 off-by-64 / off-by-43 (起点 315→358; 旧记 off-by-31 是拿旧终点 327 比新起点, 口径错), 别人是单次 refactor 派生 off-by-94 / setup comment 派生 off-by-3)。Runtime e2e 走 (a) full llm-shell.exe --help UE 5.8 binary sanity OK + (b) lite llmshelllite.exe --help UE 5.8 binary sanity OK + (c) source-level 4 重 lock (filesystem grep L358/L372/L374 跟 L358-380 范围 1:1 + awk L294/L315 跟 _call_with_world 无关 + awk L358 跟新 doc claim 1:1) 跟 binary sanity e2e 跟 tool-fix-130~172 pattern 1:1 平行。Pre-existing C2369 kCategoryShortNames 跟本 fix 解耦。 -->

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
