---
name: llm-easy-shell-lite
description: |
  只读模式操作运行中的 Unreal Engine 编辑器。Lite 是 LLMEasyShell 的最精简只读子集，
  只暴露 9 个查询类命令和已注册的 plugin ability，绝不修改任何资产/场景/编辑器状态。
  适合在不确定时进行安全探索，或在需要最小依赖时使用。

  **触发场景**：
  - 场景浏览：列出 Actor、查看详情、发现函数和属性
  - 资产浏览：搜索资产、查看资产内容（不修改）
  - 日志查看：编辑器错误日志、Niagara 验证消息
  - 状态查询：项目信息、PIE 状态、game state

  **触发关键词**：ls, cat, find, discover, info, help, gamestate, log, msglog, /Actor/, /Assets/, /Game/, /Level/

  **不触发**：任何需要写入的操作（set/spawn/rm/cp/mv/call/save/new/addcomp/play/stop/pause/undo/redo/reload）、
  截图、C++ 代码编写、AngelScript 脚本。

  **完整写操作 / 截图 / Python ability 25+ 子命令**：用 full 版本 [llm-easy-shell](../llm-easy-shell/SKILL.md)。
---

## 能力范围（Lite 实际能跑什么）

### 1. 9 个只读命令（核心）

```bash
ls /Level/Actors                    # 看场景 Actor 列表
ls /Assets                          # 看资产目录（cat 支持详情）
cat /Actor/{name}                   # 看 Actor / Component / Asset 详情
cat /Actor/{name}/{component}       # 看 Component 详情（支持别名匹配）
find Actor {pattern}                # 按名称 pattern 搜索场景 Actor
find Asset {pattern}                # 按名称 pattern 搜索资产
find /Game {pattern}                # 按路径搜索（* 通配符）
find /Assets {pattern}              # 按路径搜索（别名）
discover /Actor/{name} --funcs      # 查看可用函数（call 前必看）
discover /Actor/{name} --props      # 查看属性（set 前必看）
info                                # 项目 + 编辑器 + PIE 状态（livecoding 字段判断）
help                                # 列出所有可用命令和注册的 ability
gamestate                           # 查询 PIE 中 wave/health/gold/enemies
log --errors                        # 查看编辑器错误日志
msglog --niagara                    # 查看 Niagara 验证消息
```

**路径规则**：

| 路径 | 含义 |
|------|------|
| `/Actor/{label}` | 场景 Actor |
| `/Actor/{label}/{component}` | Actor 上的 Component |
| `/Game/{path}` | 资产（UE 标准路径，cat 支持） |
| `/Assets/{path}` | 资产（`/Game` 的别名，cat 支持） |
| `/Class/{name}` | 类信息（cat 支持） |

### 2. Plugin Ability（由 LLM 系列插件注册）

`help` 输出里的 `abilities` 段列出当前已注册的 ability。当前 Lite 配套的常见 ability：

| Ability | 来源插件 | 主要能力 |
|---------|----------|----------|
| `llmstatetree` | LLMStateTree | generate / inspect / export / copy / delete / compile |
| `ui` | LLMDynamicUI | generate / export / list-types / export-schema |
| `material` | LLMMaterial | generate / export / list-types / describe-type / export-schema |

这些是 **只读相关的子命令**（inspect / list-types / describe-type / export-schema / export），可以放心使用。
**任何会写资产/场景的子命令**（generate / copy / delete / compile）属于"写操作"，理论上不在 Lite 范围，
但因为 Lite 与这些插件共享 handler 实例，实际能用——使用时自行评估风险。

### 3. PyAbility 执行框架（无内置内容）

Lite 注册了 PyAbility 执行框架，但**没有内置任何 `.py` 文件**。
如需注册自定义只读命令，在 `Plugins/LLMEasyShellLite/PyAbilities/LLMShellAbilitiesLite/abilities/` 下放 `.py` 文件即可。

> **⚠️ 注意**：full 版本的 `python <name>` 25+ 子命令（material / blueprint / asset / vfx / scene / level / umg /
> curve / datatable / editor / gameplay / reactive / hd3d...）**Lite 没有**。需要它们请用 full skill。

---

## 端口

Lite 独占 TCP 端口段 **15201–15250**（50 端口）。Full LLMEasyShell 占用 15151–15200，
**完全互不重叠**——CLI 无需协商，各扫各的段。Lite 默认 15201。

端口文件：`llm-shell/.current_port`

---

## Lite 不做什么（避免误用）

Lite 是**只读精简版**，以下能力**没有**（需要请用 full skill [llm-easy-shell](../llm-easy-shell/SKILL.md)）：

- ❌ 任何写操作（`set` / `spawn` / `rm` / `cp` / `mv` / `call` / `save` / `new` / `addcomp`）
- ❌ 任何 PIE 控制（`play` / `stop` / `pause`）
- ❌ `livecoding` / `restart` 编译周期管理
- ❌ `log --compile`（编译日志捕获，要 full 或 Advanced skill）
- ❌ 截图（PIE 截图、Win32 窗口截图）
- ❌ `-q` / `-j` CLI 旗标（Lite 没实现，直接看 stdout）
- ❌ `python <name>` 25+ 子命令

---

## 完整文档

- [experience/README.md](experience/README.md) — Lite 经验索引
- [references/lite-vs-full.md](references/lite-vs-full.md) — Lite vs Full 能力对照表