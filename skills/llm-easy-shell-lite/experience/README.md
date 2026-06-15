# LLMEasyShellLite Experience Index

Lite 是 LLMEasyShell 的最精简只读子集，经验文档比 full 少很多。

---

## 当前文档

| 文件 | 主题 |
|------|------|
| [debugging.md](debugging.md) | Lite 只读命令的调试经验（与 full 共享 C++ 实现） |
| [02-pyability-framework.md](02-pyability-framework.md) | Lite PyAbility 执行框架（无内置内容） |

---

## 不在 Lite 范围（参考 full）

以下主题 Lite 不涉及，需要时看 [full skill](../../llm-easy-shell/experience/)：

- 写命令经验（rm / cp / mv / new / set / spawn / save）
- Python ability 系统踩坑（full 25+ `.py` 文件）
- Blueprint CDO / property 操作经验
- LiveCoding / restart 编译周期

---

## Lite 踩坑（待补充）

Lite 实际跑出来的已知问题（2026-06-14 验证）：

1. **Preflight 不识别 plugin ability**：`material` / `ui` / `llmstatetree` 这些 plugin ability 名字在 preflight 阶段被当成 unknown command，输出红色 warning，但子命令直接调用能跑（噪音警告不影响功能）。
2. **`-q` / `-j` 旗标在 Lite 没实现**：SKILL.md 早期版本宣传过，但实际 Lite 编译没带这两个 flag 处理。
3. **`log --compile` Lite 不支持**：必须用 full 或 Advanced skill。
4. **`<ability> --help` 不工作**：`material --help` / `ui --help` / `llmstatetree --help` 都报 unknown command，但子命令（如 `material list-types`）直接调用能跑。