# LLMEasyShellLite PyAbility 执行框架

> Lite 注册了 PyAbility 执行框架，但**没有内置任何 `.py` 文件**。
> 本文档说明框架能力边界 + 如何放自定义只读 `.py` 文件。

---

## Lite PyAbility 框架 vs Full 区别

| 维度 | Full | Lite |
|------|------|------|
| 框架注册 | ✅ | ✅ |
| 内置 `.py` 文件 | ✅ 25+ 个（material / blueprint / asset / vfx / scene / level / umg / curve / datatable / editor / gameplay / reactive / hd3d...） | ❌ 无 |
| 自定义 `.py` 加载机制 | ✅ | ✅（同 full） |
| 加载路径 | `Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/` | `Plugins/LLMEasyShellLite/PyAbilities/LLMShellAbilities/abilities/` |
| 调用方式 | `python <name>` | （Lite 没内置 `<ability> python` 子命令，需通过 plugin ability 形式注册） |

---

## 框架能做什么（Lite 适用部分）

PyAbility 框架在 Lite 里提供**注册机制**：

1. **自动扫描** `Plugins/LLMEasyShellLite/PyAbilities/LLMShellAbilities/abilities/` 目录
2. **自动加载**非 `_` 开头的 `.py` 文件作为只读命令
3. **暴露 Context API**：让 `.py` 文件能读取 UE 编辑器状态（actor / asset / property）

---

## 如何添加自定义只读命令

```python
# 文件：Plugins/LLMEasyShellLite/PyAbilities/LLMShellAbilities/abilities/my_query.py
"""Query specific game state from the editor (read-only)."""

def main(args, context):
    # args: list[str] - 命令行参数
    # context: 反射访问句柄
    level_name = context.get_current_level_name()  # 示例 API
    return {"level": level_name}

def register(reg):
    reg.register(main)  # 注册为只读命令
```

**注意**：
- Lite 没有内置 `python <name>` 调度入口，需要走 plugin ability 形式注册（参考 `llmstatetree` / `ui` / `material` 的 C++ handler）
- 文件名不要以下划线开头（`_xxx.py` = 私有，不注册）
- docstring 第一行写"做什么"（动词开头 + 具体功能），`help` 命令会展示

---

## 已知 Lite 限制

- ⚠️ PyAbility 模块缓存不会自动清除（与 full 一致）
  - 修改 `.py` 后必须重启编辑器（或调用 full 版的 `python reload`，Lite 没暴露这个命令）
- ⚠️ Lite 的 PyAbility 框架与 full 共享 `PythonAbilityRegistry` C++ 代码
  - 修改 Lite 的 PyAbility 代码 = 修改 full 的，**会触发全项目重新编译**

---

## 相关文件

- C++ 注册：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/PythonAbilityRegistry.cpp`
- Lite 框架入口：`Plugins/LLMEasyShellLite/PyAbilities/`（Lite 加载路径）
- Full 框架入口：`Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/`（Full 加载路径，含 25+ 内置）

---

## 何时用 Lite PyAbility vs Full

**用 Lite**：
- 只想跑只读查询（如自定义 reflection walker、actor 统计）
- 不想触发 full 插件编译

**用 Full**：
- 需要 25+ 内置命令
- 写自定义能力 + 需要 `python <name>` 调度入口
- 需要修改 PyAbility 代码