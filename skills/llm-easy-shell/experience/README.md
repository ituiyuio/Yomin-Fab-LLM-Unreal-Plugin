# LLMEasyShell 经验库

> 基于实战踩坑凝练的 22 个教训，分 7 个主题 + 1 个速查

## 文档清单

| 文件 | 主题 | 教训数 |
|------|------|--------|
| [01-builtin-commands.md](01-builtin-commands.md) | 内置 shell 命令（rm/cp/mv/new/set 路径与参数） | 6 |
| [02-python-abilities.md](02-python-abilities.md) | Python ability 系统（执行模式 / 输出 / 参数 / 字段名） | 4 |
| [03-blueprint-property.md](03-blueprint-property.md) | Blueprint / Property 操作（bpprop/bpprop/ClassProperty/嵌套路径） | 5 |
| [04-build-and-restart.md](04-build-and-restart.md) | 编译 / 重启周期（LiveCoding vs restart 决策树） | 5 |
| [05-screenshot.md](05-screenshot.md) | 截图（UE PIE 双路径 / CEF 延迟 / 新输出格式） | 5 |
| [06-cli-flags.md](06-cli-flags.md) | -q/--quiet stderr 重定向 + -j/--json-only 反转义,LLM 上下文降噪 70% | 3 |
| [07-editor-shot-win32.md](07-editor-shot-win32.md) | Editor 窗口截图（Win32 PrintWindow 路径，绕开 FViewport 0×0） | 4 |
| [debugging.md](debugging.md) | 早期路径解析 + 反射 UI 教训 | 2 |

## 速查决策树

### 改完代码怎么验证？

```
改动类型？
├── 改 .py 文件 → python reload
├── 改 .cpp 函数体（不动 USTRUCT）→ livecoding
├── 改 .h 函数签名（不动 USTRUCT 布局）→ livecoding
├── 新增 UCLASS → restart
├── 改 USTRUCT 字段 → restart
├── 改 UENUM → restart
└── 不确定 → restart（5-10 分钟但安全）
```

详见 [04-build-and-restart.md](04-build-and-restart.md)

### 命令返回异常？

| 症状 | 跳到 |
|------|------|
| Actor 找不到 / 路径解析失败 | [01-builtin-commands.md](01-builtin-commands.md) 教训 1 |
| `SyntaxError` 或空 output | [02-python-abilities.md](02-python-abilities.md) 教训 1, 2 |
| `unexpected keyword 'world'` | [02-python-abilities.md](02-python-abilities.md) 教训 3 |
| bIsAsync / bIsPIE 永远 default | [02-python-abilities.md](02-python-abilities.md) 教训 4 |
| `set ClassProperty` 断言崩溃 | [03-blueprint-property.md](03-blueprint-property.md) 教训 1c / 2 Fix 1 |
| `set` 报 success 但 `cat` 读 0 | [03-blueprint-property.md](03-blueprint-property.md) 教训 1e |
| `Component.Property` 路径失败 | [03-blueprint-property.md](03-blueprint-property.md) 教训 2 Fix 3 |
| 截图截不到 HUD / 全白 | [05-screenshot.md](05-screenshot.md) 教训 1, 3, 4 |
| 截图文件名带 5 个 0 | [05-screenshot.md](05-screenshot.md) 教训 2 |
| `source=editor` 永远 0×0 | [07-editor-shot-win32.md](07-editor-shot-win32.md) 教训 1（用 Win32 路径） |
| Win32 PrintWindow 截到黑屏 | [07-editor-shot-win32.md](07-editor-shot-win32.md) 教训 4（缺 PW_RENDERFULLCONTENT） |

### 加新能力

- **C++ 新能力**：参考 [04-build-and-restart.md](04-build-and-restart.md) 决定 livecoding / restart
- **Python 新 ability**：
  - 函数签名 `def main(args, context=None):`（与 dispatcher 期望一致）
  - 双输出：`unreal.log()` + `output` 键
  - 字段读取用 `_uh.get_field()`（支持 snake_case + 去 b 前缀）
  - 改完必跑 `python reload`

## 写作约定

每个文件用相同格式：

```
### 教训 N：[一句话]
**场景**：[具体症状]
**根因**：[代码层原因 + 文件:行号]
**修复模式**：[代码示例]
**经验**：[通用规则，下次怎么避]
```

- 场景要可识别（用户能 match 上）
- 根因要精确（文件:行号）
- 修复模式要可复用（不只解决当前问题）
- 经验要通用（不是"加 try/except"这种 ad hoc）
