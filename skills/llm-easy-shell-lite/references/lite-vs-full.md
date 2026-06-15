# LLMEasyShell Lite vs Full 能力对照表

Lite 是 LLMEasyShell 的**最精简只读子集**，只暴露查询类能力。Full 版提供完整 27 命令 + Python ability 25+ 子命令 + 写操作能力 + 截图能力。

---

## 命令对比

| 命令类别 | Full | Lite | Lite 说明 |
|----------|------|------|-----------|
| `ls` / `cat` / `find` / `discover` / `info` / `help` | ✅ | ✅ | 完全相同 |
| `gamestate` | ✅ | ✅ | 完全相同 |
| `log --errors` | ✅ | ✅ | 完全相同 |
| `log --compile` | ✅ | ❌ | Lite 不支持编译日志捕获，要 Advanced skill |
| `msglog --niagara` | ✅ | ✅ | 完全相同 |
| `set` / `spawn` / `rm` / `cp` / `mv` / `call` | ✅ | ❌ | Lite 无写操作 |
| `save` / `new` / `mkdir` / `addcomp` | ✅ | ❌ | Lite 无资产管理 |
| `play` / `stop` / `pause` | ✅ | ❌ | Lite 无 PIE 控制 |
| `undo` / `redo` / `reload` | ✅ | ❌ | Lite 无编辑历史 |
| `livecoding` / `lc` | ✅ | ❌ | Lite 无编译周期管理 |

---

## Ability 对比

| Ability | 来源 | Full | Lite |
|---------|------|------|------|
| `llmstatetree` | LLMStateTree plugin | ✅ | ✅ |
| `ui` | LLMDynamicUI plugin | ✅ | ✅ |
| `material` | LLMMaterial plugin | ✅ | ✅ |
| `python <name>` | LLMEasyShell PyAbility | ✅ 25+ 子命令 | ❌ 无 |

`python <name>` Full 包含：`material` / `blueprint` / `asset` / `vfx` / `scene` / `level` / `umg` / `curve` / `datatable` / `editor` / `gameplay` / `gameplaytag` / `gameplayability` / `navigation` / `poseseach` / `chooser` / `property` / `bpcomp` / `bpprop` / `reparent` / `perf` / `anim` / `reactive` / `hd3d` / `hd3dpostprocess` / `hd3dscene` 等

---

## 截图能力对比

| 截图路径 | Full | Lite |
|----------|------|------|
| `python editor screenshot` (PIE 视口) | ✅ | ❌ |
| `editor_shot.ps1` (Win32 窗口) | ✅ `scripts/editor_shot.ps1` | ❌ |

**Lite 需要截图怎么办**：用 full skill [llm-easy-shell](../../llm-easy-shell/SKILL.md)。

---

## CLI 旗标对比

| 旗标 | Full | Lite |
|------|------|------|
| `-q` / `--quiet` | ✅ 重定向 stderr noise 到 quiet log | ❌ 未实现 |
| `-j` / `--json-only` | ✅ 解包嵌套 JSON output | ❌ 未实现 |

**Lite 跑命令直接看 stdout**（带 stderr noise 是预期行为）。

---

## 端口对比

| 范围 | 用途 |
|------|------|
| 15151–15200 | Full LLMEasyShell |
| 15201–15250 | Lite LLMEasyShell |

两个 CLI 端口段**严格不重叠**，可同时运行。

---

## 何时用哪个

**用 Lite**：
- 只需要查询（看场景、看资产、看日志、看 game state）
- 不确定要不要改东西（安全探索）
- 想最小依赖

**用 Full**：
- 需要写操作（改属性、生成资产、PIE 控制）
- 需要截图
- 需要 `python <name>` 25+ 子命令
- 需要 `-q` / `-j` 旗标（让 LLM parse 更简单）
- 需要 `log --compile`

**两者切换**：在不同目录运行不同二进制，不冲突。