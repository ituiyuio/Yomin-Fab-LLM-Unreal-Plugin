# LLMEasyShellLite Python Ability 执行框架

> Lite 注册了 Python ability 框架，但**没有内置任何 `.py` 文件**。
> 本文档说明框架能力边界 + 如何放自定义只读 `.py` 文件。

---

## Lite Python Ability 框架 vs Full 区别

| 维度 | Full | Lite |
|------|------|------|
| 框架注册 | ✅ | ✅ |
| 内置 `.py` 文件 | ✅ 25+ 个（material / blueprint / asset / vfx / scene / level / umg / curve / datatable / editor / gameplay / reactive / hd3d...） | ❌ 无 |
| 自定义 `.py` 加载机制 | ✅ | ✅（同 full） |
| 加载路径 | `Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/` | `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/` |
| C++ 入口 | `PythonAbilityRegistry.cpp` | `PythonAbilityRegistryLite.cpp`（独立，不与 full 共享） |
| 调用方式 | `python <name>` | `python <name>` (Lite 暴露 `python` 入口，见 ShellCommand_Python.cpp) |

> **2026-06-16 路径变更**：所有插件的 Python 都搬到 `Content/Python/` 下，遵循 Fab 规范。

---

## 框架能做什么（Lite 适用部分）

Python ability 框架在 Lite 里提供**注册机制**：

1. **自动扫描** `Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/` 目录
2. **自动加载**非 `_` 开头的 `.py` 文件作为只读命令
3. **暴露 Context API**：让 `.py` 文件能读取 UE 编辑器状态（actor / asset / property）

---

## 如何添加自定义只读命令

```python
# 文件：Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/my_query.py
"""Query specific game state from the editor (read-only)."""

def main(args, world):
    # args: list[str] - 命令行参数
    # world: UWorld (or None if PIE 未运行)
    if world is None:
        return {"ok": False, "error": "no PIE session"}
    actors = [a.get_name() for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)]
    return {"ok": True, "actors": actors}
```

**注意**：
- Lite 的 `python <name>` 入口是暴露的（见 Documentation.md "Command Reference"）
- 文件名不要以下划线开头（`_xxx.py` = 私有，不注册）
- docstring 第一行写"做什么"（动词开头 + 具体功能），`help` 命令会展示
- `main` 第二个参数是 auto-injected `UWorld`（PIE 运行时）或 `None`

---

## 已知 Lite 限制

- ⚠️ Python ability 模块缓存不会自动清除（与 full 一致）
  - 修改 `.py` 后必须重启编辑器（Lite 没暴露 `python reload` 命令 — 是 full 版的命令）

---

## 相关文件

- C++ 注册（Lite）：`Plugins/LLMEasyShellLite/Source/LLMEasyShellLite/Private/PythonAbilityRegistryLite.cpp`
- Lite 框架入口：`Plugins/LLMEasyShellLite/Content/Python/LLMShellAbilitiesLite/abilities/`（Lite 加载路径）
- Full 框架入口：`Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/`（Full 加载路径，含 25+ 内置）

---

## 何时用 Lite Python Ability vs Full

**用 Lite**：
- 只想跑只读查询（如自定义 reflection walker、actor 统计）
- 不想拉进 full 插件的 9 个引擎依赖

**用 Full**：
- 需要 25+ 内置命令
- 写自定义能力 + 需要 `python <name>` 调度入口（Lite 也支持，但 Lite 没内置 ability）
- 需要 Live Coding / 写 / PIE 控制等 Lite 范围外能力
