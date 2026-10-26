---
name: llmshell-automation-test-via-python-ability
description: "【根因已修 2026-10-04】LLMEasyShell CLI 曾无法把 'Automation RunTests X.Y' 整串传给 UE console（多词命令尾部参数被静默丢弃，且返回 success=true 的绿 no-op）。现直接用 python editor console 整串传参即可，无需写临时 ability。"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: f7f11918-c370-4e37-a684-082074e10bab
---

# LLMEasyShell CLI 跑 AutomationTest —— 根因已修（2026-10-04）

> ## ✅ RESOLVED · 下面「写临时 ability」那条 workaround **已作废，不要再照做**
>
> **原症状**：`llm-shell.exe -c "python editor console cmd=Automation RunTests X.Y"`
> 只把 `Automation` 一个词派发出去，`RunTests X.Y` 整段蒸发。
>
> **根因**（本条原记录只定位到第 3 层；2026-10-04 已确认并修复该层）：
> `editor.py` 的 `console()` 里 `cmd = d.get("command", d.get("cmd", ""))` **只取键值的首词**，
> 后面跟着的裸位置 token 因为「已经有 cmd 了」而**全部被丢弃**。
> UE console 命令普遍是多词（`Automation RunTests X` / `stat unit` / `ce Func a b`），
> 所以这条命令形对多词命令**系统性失效**。
> ⛔ 最毒的地方：它返回 `{"success": true, "output": "(dispatched)"}` ——
> **一个看起来是绿的 no-op**，照文档做必然静默跑空还自以为跑过了。
>
> **现在的正确路径（任选一，都已实跑确认）**：
> ```bash
> # A. 整串作为**一个**引号参数（最稳，bash/llm-shell 都不会拆它）
> llm-shell.exe -q -j -c 'python editor console "cmd=Automation RunTests Survivor.X.Y"'
>
> # B. 键值 + 位置混用（2026-10-04 修好后已支持尾部参数接回）
> llm-shell.exe -q -j -c "python editor console cmd=Automation RunTests Survivor.X.Y"
> ```
> 修后读数（同一份日志逐行对比）：
> 修前 `Cmd: Automation` → 修后 `Cmd: Automation RunTests Survivor.X.Y` → `Found 1 automation tests` → `Result={Success}`。
>
> **结果看哪**：仍看 `Saved/Logs/CODEO.log` 的
> `LogAutomationController: Display: Test Completed. Result={...} Name={...} Path={...}`。
> **不要**用 `run_automation` ability（尾巴带 `; Quit` 会杀编辑器，CI 专用）。
> **不要**用 `execute_console_command` 拼临时 ability（见下，历史 workaround）。

---

## 历史记录（2026-06-20 · 根因未定位时的排查过程，保留供追溯）

### 核心坑（当时的记录）
`llm-shell.exe -c "python editor console cmd=Automation RunTests X.Y"` **不会**把整个字符串传给 UE console。原因:
1. **bash 层**:单引号在 Windows bash 下被剥掉,空格分隔 argv
2. **llm-shell 层** (TokenizeCommand main.cpp:1195):尊重 `"` `'` quote,但前提是 quote 没被 bash 吃掉
3. **Python `_args_to_dict`** (editor.py:57):只把 `command=...` 单个 arg 串起成 cmd,后续 arg 被忽略 ← **← 这一层是真凶，2026-10-04 已修**
4. **UE console**:收到的是 `Automation` 单 token,需要 subcommand `RunTests X.Y` 但只能识别到 `Automation` 然后报错

试过的失败 escape:`%20` / `+` / `\\ ` / bash 双引号嵌套 / 单引号嵌套 / PowerShell wrapper — 全部失败。
（**现在知道这些 escape 本来也不需要** —— 只要把整串包成一个引号参数，或直接靠 2026-10-04 修复 的修复。）

### ⛔ 已作废的 workaround:写一个临时 Python ability

~~在 `Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/` 下放个文件 (非 `_` 前缀,自动注册)，
自己拼 `cmd = "Automation RunTests " + name` 再调 `execute_console_command`。~~ 历史代码**照录如下**（本目录是
forensic 档案，当年真实可用的 workaround 原样保留，勿再照做）：

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

~~调用: `llm-shell.exe -q -c "python run_xxx_tests run"`~~

**不要再这么做了** —— 根因已修，且这个 workaround 本身有害：它要求往插件目录**创建文件再删掉**、
每次 `python reload` 污染 registry，是纯粹的净负债。

### 仍然有效的注意事项（与本 bug 无关，但都是真话）
- **`Context` 对象没有 `log()` 方法**(registry.py:11),只能写 print 或 UE_LOG
- **新 ability 需要** `llm-shell.exe -c "python reload"`（或 `reload`）才能扫描到
- **`execute_console_command` 返回空字符串是常态**(Automation 命令异步执行)
- **编辑器内跑 automation 会卡在 `FWaitForInteractiveFrameRate`**：窗口失焦时 Slate 节流到 ~3 FPS，
  latent command 要求 ≥10 FPS 持续 5s 才开跑。前台化窗口（或 `t.IdleWhenNotForeground 0`）后立刻开跑。
  见 [llmshell-restart-intercept-and-automation-framerate-2026-09-04.md](llmshell-restart-intercept-and-automation-framerate-2026-09-04.md)

**Why:** 阻止后续 implementer 在 CLI 上死磕字符串 escape，**以及照着一份已经过时的 workaround 去建临时文件**。
**How to apply:** 任何 PR 涉及 `Automation RunTests` 验证时，用上面「现在的正确路径」的 A 或 B 两种引号形态之一。
