---
name: llm-easy-shell
description: |
  操作运行中的 Unreal Engine 编辑器。当用户需要在 UE 编辑器中执行实时操作时使用此 skill。

  **触发场景**：
  - 场景操作：查看/创建/删除/选择 Actor，搜索对象
  - 属性修改：移动/旋转/缩放，修改任意属性值
  - 函数调用：调用 Actor 或组件上的蓝图函数（**先用 discover 确认函数名**）
  - 资产操作：浏览/创建/复制/删除蓝图、材质、数据表，**添加组件到蓝图**
  - 编辑器控制：PIE 播放/停止/暂停、热重载、保存、撤销重做
  - 日志查看：编辑器日志、编译日志

  **触发关键词**：ls, cat, set, spawn, rm, cp, mv, call, save, new, addcomp, play, stop, pause, select, focus, undo, redo, find, info, help, livecoding, reload, lc, log, mkdir, discover, actor, editor, /Actor/, /Assets/, /Game/, /Level/, restart, msglog, gamestate, simulated

  **不触发**：纯 C++ 代码编写(cpp-developer)、AngelScript 脚本(unreal-as)、完整项目编译(builder)
---

## 核心命令

```bash
ls /Level/Actors                    # 看场景
cat /Actor/{name}                   # 看详情
discover /Actor/{name}/LiquidGlass  # 查看可用函数和属性
set /Actor/{name}/Location (x,y,z)  # 改属性
call /Actor/{name}/LiquidGlass ApplyPreset --Preset Default  # 调用函数
spawn PointLight at (0,0,100)       # 创建
rm /Actor/{name}                    # 删除
```

**discover 是最重要的命令** — 调用函数前先用它确认函数名和参数！

## CLI 旗标（LLM 上下文优化）

| 旗标 | 等价 | 效果 |
|------|------|------|
| `-q` | `--quiet` | 把 stderr 噪音(连接/路径/端口警告)重定向到 `llm-shell-quiet.log`,LLM stdout 只剩有效输出 |
| `-j` | `--json-only` | 解包 server 响应里的 `output`/`result` 字段,做 JSON 反转义后原样输出 — LLM 直接 parse 不必二次解字符串 |

**推荐组合**:几乎所有调用都加 `-q -j`,把 17 行 noise 压成 7 行纯 JSON。

```bash
# 之前(17 行,嵌套 JSON)
./llm-shell.exe -c "gamestate"
# 输出:
# [llm-shell] Engine path found via fallback: C:\Program Files\Epic Games\UE_5.7
# { "success": true, "output": "{\"wave\":{...}}" }
# 
# 之后(7 行,纯 JSON,LLM 可直接 parse)
./llm-shell.exe -q -j -c "gamestate"
# {"wave":{"currentWave":"1",...},"player":{...},"enemyCount":2}
```

> 注意:`-j` 只在响应有 `output`/`result` 字段时生效;`info` 命令直接返回顶层 JSON,无需 `-j`。REPL 模式不受 `-q` 影响(保留人类可读 stderr)。

## 路径规则

| 路径 | 含义 |
|------|------|
| `/Actor/{label}` | 场景对象 |
| `/Actor/{label}/{component}` | 组件（支持别名匹配） |
| `/Game/{path}` | 资产（cat 支持） |
| `/Assets/{path}` | 资产（别名，cat 支持） |
| `/Class/{name}` | 类信息（cat 支持） |

**find 命令**：
```bash
find /Game *Glass*     # 在 /Game 下搜索资产（支持 * 通配符）
find /Assets *          # 在 /Assets 下搜索
find Actor BP_Liquid*   # 搜索场景中的 Actor
find Asset *Liquid*     # 搜索资产
```

## livecoding vs restart

| 场景 | 命令 | 说明 |
|------|------|------|
| 修改现有类函数体 | `livecoding` | 函数体、算法、局部变量 |
| 修改现有类 UPROPERTY/UFUNCTION | `livecoding` | 多数情况下可以 |
| **新增 C++ 类** | `restart` | LiveCoding 无法处理，必须重启编辑器 |
| UENUM/USTRUCT 变更 | `restart` | 反射系统元数据变更 |
| 继承层次变化 | `restart` | 需要重新实例化对象 |
| 不确定 | `restart` | 安全选择 |

> 完整决策树 + LiveCoding 失败诊断 + `python reload` 行为见 [experience/04-build-and-restart.md](experience/04-build-and-restart.md)

`livecoding`：Live Coding 二进制补丁，替换函数指令，不重新实例化对象。  
`restart`：`save → shutdown → MSBuild → 启动引擎`

## livecoding 使用准则

**每次工具调用返回中都包含 `livecoding` 字段**，显示当前编译状态。

| 命令 | 用途 |
|------|------|
| `livecoding` | 触发编译 + 等待完成（最长 120s） |
| `livecoding --status` | 查看 LiveCoding 状态和报错信息 |
| `livecoding --enable` | 启用 LiveCoding |
| `livecoding --disable` | 禁用 LiveCoding |

**正确流程**：
1. `livecoding` → 触发编译，等待完成
2. 查看响应中 `livecoding` 和 `result` 字段
3. `compiling: false, result: Success` → 编译完成
4. `compiling: true` → 编译进行中
5. `result: Timeout` → 命令超时，查看返回的 `editorState` 了解编辑器状态
6. `result: Timeout, compiling: false` → 超时但编译实际成功（通过日志确认）
7. `result: Timeout, compiling: true` → 超时且仍在编译，用 `livecoding --status` 确认

## info 命令

`info` 是唯一的状态查询入口，返回项目信息 + 编辑器实时状态：

```json
{
  "project": "CODEO",
  "engineVersion": "...",
  "level": { "name": "...", "actorCount": 42 },
  "pieState": "Stopped",
  "livecoding": {
    "compiling": true,
    "phase": "compiling",
    "elapsed": 15.2
  },
  "hint": "editor is compiling, 15s elapsed"
}
```

**在执行任何修改操作（set/spawn/rm/cp/mv/call/save/new）前，先用 `info` 确认 `livecoding.compiling` 是否为 false。**

## Ability 架构

**内置（Core）**：27 个原生命令
- Actor：`spawn` `rm` `cp` `mv` `select` `focus` `call` `set`
- 资产：`new` `save` `mkdir` `addcomp`
- 编辑器：`play` `stop` `pause` `undo` `redo` `reload` `info` `log` `msglog` `gamestate`
- 查询：`ls` `cat` `find` `help` `discover`
- 热重载：`livecoding` `reload` `lc`（三者等价）

**内置 Ability**：`actor` `editor`（加前缀调用，与直接调用原生命令完全等价，无额外功能）

**插件（Extension）**：`help` 列出所有已注册 Skills，`vfx` `mat` `python`

> `actor spawn` = `spawn`，`editor play` = `play` — 前缀机制仅为兼容性保留，建议直接使用原生命令。

## Python Ability（可扩展的命令）

`python` 是一个特殊的 Ability，它的命令来自文件系统而非 C++ 注册。Agent 有完全的自主权来创建新的 Python 能力。

### 工作原理

```
Plugins/LLMEasyShell/PyAbilities/
├── __init__.py
├── registry.py       # Ability 基类（不可删除）
└── abilities/
    ├── __init__.py
    ├── _base.py          # 下划线开头 = 私有
    ├── _example.py       # 下划线开头 = 私有
    └── material.py       → python material 命令
```

每个非 `_` 开头的 `.py` 文件自动成为一个命令，通过 `python <文件名>` 调用。

### 调用方式

```bash
python material              # 调用 material.py
python <command> [args...]   # args 会以列表传给 Python 函数
```

### Agent 的自由度

**1. 创建新的 Python 能力（完全自主）**

不需要修改任何 C++ 代码。只需：
1. 在 `Plugins/LLMEasyShell/PyAbilities/abilities/` 创建 `.py` 文件
2. 实现 `main(args, context)` 或 `execute(args, context)` 函数
3. Python ability 自动被发现并注册

**2. Context API（在 Python 中使用）**

Python 文件内可通过 `context` 对象访问 LLMEasyShell 的反射能力：

```python
from registry import Ability, Command, Context

class MyAbility(Ability):
    name = "my"
    version = "1.0.0"

    def get_commands(self):
        return [
            Command("my_action", "Do something", ["param1", "param2"]),
        ]

    def execute(self, command, args, context):
        if command == "my_action":
            # 读取资产属性
            value = context.get_property("/Game/BP_Test", "Health")
            # 修改资产属性
            context.set_property("/Game/BP_Test", "Health", "100")
            # 调用资产函数
            result = context.call("/Game/BP_Test", "TakeDamage", {"Damage": 10})
            return {"success": True, "output": f"Health is now {value}"}

def register(reg):
    reg.register_ability(MyAbility())
```

**3. 不需要知道实现细节**

Agent 调用 `python material` 时，不需要知道 `material.py` 的内部结构。Python 框架负责：
- 参数传递
- 错误处理
- 结果序列化

**4. 现有的 Python abilities**

| 命令 | 功能 |
|------|------|
| `python material` | Material 资产生成与参数操作 |
| `python blueprint` | Blueprint 结构分析（变量/函数/组件/继承） |
| `python asset` | 资产管理与依赖审计 |
| `python vfx` | 解析 .llmvfx DSL 文件（Niagara 系统生成用 C++ `vfx` 命令） |
| `python scene` | 场景 Actor 查询（统计/灯光/邻近搜索/标签） |
| `python level` | Level 操作与 actor 空间查询 |
| `python umg` | UMG/Widget Blueprint 结构与属性 |
| `python curve` | Curve 资产生成与键值操作 |
| `python datatable` | DataTable 行读写、列搜索、CSV/JSON 导出 |
| `python editor` | 编辑器会话控制（视口/PIE/CVar/**截图**） || `python gameplay` | PIE 游戏控制与调试绘制 |
| `python gameplaytag` | GameplayTag 溯源与依赖查询 |
| `python gameplayability` | GameplayAbility/Effect/AttributeSet 元数据 |
| `python navigation` | NavMesh OBJ 导出 |
| `python poseseach` | PoseSearch Schema/Database 查询 |
| `python chooser` | Unreal Chooser 表调试 |
| `python property` | UPROPERTY 读写（绕过 Python 访问限制） |
| `python bpcomp` | Blueprint CDO 组件属性读写（支持蓝图合成组件和 C++ 继承组件） |
| `python bpprop` | Blueprint CDO 属性读写 |
| `python reparent` | Blueprint 父类重定义 |
| `python perf` | 性能指标查询（帧时序/内存/UObject 统计） |
| `python anim` | Animation 资产检查与编辑 |
| `python reactive` | 响应式事件订阅与管理 |
| `python hd3d` | HD3D 相关 |
| `python hd3dpostprocess` | HD3D 后处理 |
| `python hd3dscene` | HD3D 场景设置（材质/标签/体素 Actor 配置） |

路径：`Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/`

**5. 描述规范（Docstring Guidelines）**

创建 Python ability 时，**docstring 第一行必须具有语义**——描述"做什么"而非"怎么实现"。

| 写法 | 评价 |
|------|------|
| `"""Access Material parameters."""` | 差 - 不说明能做什么 |
| `"""Read and write Material parameters (scalar, vector, texture) via Python binding layer."""` | 好 - 明确说明能力范围 |
| `"""Query scene actors: stats, lights, proximity search, tags, and class distribution."""` | 好 - 列出具体功能 |
| `"""Analyze Blueprint class structure: variables, functions, components, and inheritance."""` | 好 - 动词开头，清晰具体 |

**规范**：
- 第一行用动词开头（Read, Query, Analyze, Audit, Generate...）
- 包含具体的功能关键词（stats, lights, proximity, tags）
- 避免技术实现细节（Python binding layer、C++ reflection）
- `help` 命令会提取 docstring 第一行显示给用户

**错误示例**：
```python
"""Material ability implementation."""
"""Functions for getting and setting material params."""
```

**正确示例**：
```python
"""Read and write Material parameters (scalar, vector, texture) via Python binding layer."""
```

**6. 注册/注销 Python abilities**

Python abilities 在编辑器启动时自动扫描注册。修改 `abilities/` 目录后需要重启编辑器（或调用 `reload`）使更改生效。

## 调用方式

```bash
skills/llm-easy-shell/llm-shell/llm-shell.exe -c "ls /Level/Actors"
skills/llm-easy-shell/llm-shell/llm-shell.exe --restart
```

## 错误排查

| 问题 | 解决 |
|------|------|
| Actor not found | `ls /Level/Actors` |
| Asset not found | `ls /Assets` 或 `find /Game *` |
| Function not found | `discover <path> --funcs` 查看可用函数 |
| 连接失败 | 启动 UE 编辑器 |
| 命令超时 | 超时后自动查询 `info`，响应中含 `editorState` 查看编辑器状态 |
| find 返回 "Unknown type: /X" | 命令已支持 `find /Game <pattern>` 路径格式 |
| cat 不显示属性值 | 已修复：显示所有 BlueprintVisible 属性当前值（含 struct） |

**更深入的踩坑经验（按主题）**：

- [experience/01-builtin-commands.md](experience/01-builtin-commands.md) — Actor 路径 `/` 解析、`new --key=value` 崩溃、stdin 与 `-c` 冲突、set Blueprint 父类限制、FObjectProperty 崩溃
- [experience/02-python-abilities.md](experience/02-python-abilities.md) — Python `ExecuteFile` 模式、output 字段缺失、`_call_with_world` 死写 bug、b 前缀 bool 字段读不到
- [experience/03-blueprint-property.md](experience/03-blueprint-property.md) — bpprop 5 个 ClassProperty 坑、FClassProperty MetaClass 校验、`#` 路径 FObjectProperty fallback、嵌套路径 walk
- [experience/04-build-and-restart.md](experience/04-build-and-restart.md) — 何时 `livecoding` / 何时 `restart` 决策树、USTRUCT 改字段必 restart、`python reload` 不重 import 模块
- [experience/05-screenshot.md](experience/05-screenshot.md) — 截图双路径（sync vs async+ui）、CEF 初始化延迟、2026-06-01 新输出格式

> 详细语法见 `references/commands.md`
> 源码调试经验见 `references/debugging.md`
> PIE 截图完整指南见 `references/llm-screenshot.md`
> **Editor 窗口截图**（Win32 路径，绕开 FViewport 0×0 硬约束）见 [references/editor-shot-win32.md](references/editor-shot-win32.md)
> 完整经验库（21 个教训）见 [experience/README.md](experience/README.md)

## 截图 — 两条路径选对

| 场景 | 用哪条 | 命令 |
|------|--------|------|
| 看 **editor 应用窗口**（菜单/工具栏/**Outliner**/视口/状态栏） | **Win32 路径**（推荐） | `powershell -File scripts/editor_shot.ps1` |
| 看 **PIE 3D 渲染**（HUD/动画/动态光照） | PIE 路径 | `play` → `sleep 5` → `python editor screenshot path=X source=pie` |
| 不知道选哪个 | Win32 路径（永远能跑） | `powershell -File scripts/editor_shot.ps1` |

**Win32 路径优势**：跟 UE 状态完全无关（Idle/PIE/Compiling 都行），不需要 PIE，能看到 editor UI 全部内容（Outliner、Details Panel、工具栏）。
**PIE 路径优势**：精确路径、确定性高、能用 `show_ui=true` 截 HUD/UMG/WebBrowser。

完整 Win32 路径文档：[references/editor-shot-win32.md](references/editor-shot-win32.md)

## PIE 截图（核心能力）

```bash
# PIE 中截 PIE 视口（默认）
python editor screenshot

# 指定路径
python editor screenshot path=D:/shot.png

# 强制源
python editor screenshot source=pie       # PIE 视口
python editor screenshot source=editor    # Editor 视口
python editor screenshot source=auto      # 自动

# 自定义尺寸（最近邻缩放）
python editor screenshot width=1280 height=720

# 异步（走 FScreenshotRequest，捕获下一帧完整渲染）
python editor screenshot async=true
```

PIE 截图的两条路径：
- **同步（默认）**：`FViewport::ReadPixels` + `FImageUtils::SaveImageByExtension`
- **异步**：`FScreenshotRequest::RequestScreenshot` 引擎自带

**关键陷阱**：
- UE Python 访问 USTRUCT 用 snake_case：`result.bSuccess` ❌ → `result.success` ✅
- 修改 `editor.py` 后必须 `python reload` 重载 Python 模块
- 修改公共头 USTRUCT 加字段 → 必须 `restart`（Live Coding 失败）
- Editor 视口在 headless/最小化时是 0×0，需用 PIE 视口

完整文档：`references/llm-screenshot.md` + 实战踩坑见 [experience/05-screenshot.md](experience/05-screenshot.md)
