---
name: llmshell-automation-test-via-python-ability
description: "2026-06-20 LLMEasyShell CLI 无法向 UE console 传带空格的字符串 (e.g. \"Automation RunTests Survivor.X\"),必须用 Python ability 调 execute_console_command 才能跑 AutomationTest"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: f7f11918-c370-4e37-a684-082074e10bab
---

# LLMEasyShell CLI 跑 AutomationTest 的正确路径

## 核心坑
`llm-shell.exe -c "python editor console cmd=Automation RunTests X.Y"` **不会**把整个字符串传给 UE console。原因:
1. **bash 层**:单引号在 Windows bash 下被剥掉,空格分隔 argv
2. **llm-shell 层** (TokenizeCommand main.cpp:1195):尊重 `"` `'` quote,但前提是 quote 没被 bash 吃掉
3. **Python `_args_to_dict`** (editor.py:57):只把 `command=...` 单个 arg 串起成 cmd,后续 arg 被忽略
4. **UE console**:收到的是 `Automation` 单 token,需要 subcommand `RunTests X.Y` 但只能识别到 `Automation` 然后报错 "Unknown Automation command 'Automation%20List'" (URL-decode 不做)

试过的失败 escape:`%20` / `+` / `\\ ` / bash 双引号嵌套 / 单引号嵌套 / PowerShell wrapper — 全部失败。

## 正确路径:写一个临时 Python ability

在 `Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/` 下放个文件 (非 `_` 前缀,自动注册):

```python
from ..registry import Ability, Command, Context

class RunXxxTestsAbility(Ability):
 name = "run_xxx_tests"
 def get_commands(self):
 return [Command("run", "Run all automation tests", [])]
 def execute(self, command, args, context):
 if command == "run":
 return self._run_tests(args, context)
 def _run_tests(self, args, context):
 import unreal
 # 直接在 Python 里拼完整的 cmd 字符串,绕开所有 tokenize 层
 for name in ["X.Y.A", "X.Y.B", "X.Y.C"]:
 cmd = "Automation RunTests " + name
 unreal.LLMEasyShellEditorLib.execute_console_command(cmd)
 return {"success": True, "output": "dispatched"}

def register(reg):
 reg.register_ability(RunXxxTestsAbility())
```

调用: `llm-shell.exe -q -c "python run_xxx_tests run"`

## 注意事项
- **`Context` 对象没有 `log()` 方法**(registry.py:11),只能写 print 或 UE_LOG
- **重新加载需要** `llm-shell.exe -c "python reload"` 才能扫描到新 ability
- **`execute_console_command` 返回空字符串是常态**(Automation 命令异步执行,stdout 走 Automation framework 而不是 console capture)
- **真正的 PASS/FAIL 看 `Automation: Run Started` / `Automation Test Failed` / `LogAutomationController` 输出**,不是 stdout
- **临时 ability 跑完一定要删掉 + `python reload` 清理**,否则污染 registry

**Why:** 阻止后续 PR 的 implementer 在 CLI 上死磕字符串 escape。
**How to apply:** 任何 PR 涉及 `Automation RunTests` 验证时,直接用这个 pattern 写临时 ability。
