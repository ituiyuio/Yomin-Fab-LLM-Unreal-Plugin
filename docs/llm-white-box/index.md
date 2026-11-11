---
outline: [2, 3]
---

# LLM White Box

> 给 LLM agent 用的 BSP 关卡白盒工具 —— **15 条返回 JSON 的命令**，直接在持久关卡里
> 铺出真正的 BSP 几何体，外加一份可复现的 **山谷 + 中世纪城堡** 示例生成器。
> 需要在同一工程里装 **LLM Easy Shell**（或 Lite）才能拿到命令面。

**一句话价值**：`create-box` / `create-subtract-box` / `create-cylinder` /
`create-sphere` / `create-cone` / `create-stairs` · `build-room` ·
`build-wall-segment` · 按命名组批量刷材质 · BSP 重编译 ·
`python castle build` 一次调用重建 1040 支刷子的白盒 · 支持 UE 5.5 / 5.6 / 5.7 / 5.8。

---

## 核心能力

- **真 BSP 几何体** —— 用引擎自带的 `UBrushBuilder` 系列在 `ABrush` 上搭出来的，
  存进你的 `.umap`、走 BSP 光照编译、之后还能手动改。
- **一行命令，JSON 回执** —— 每条命令回一行 JSON 对象，agent 循环可以直接拿结果
  继续决策，不用去解析自然语言。
- **复合构件一步到位** —— `build-room` 一次吐 4 面墙 + 地 + 顶；`build-wall-segment`
  沿任意方向拉一道墙，而且**真的会把它转过去**。
- **按命名组刷材质** —— `apply-default-material --name=Masonry` 一次重刷整组
  `Masonry_*`，白盒可以按类别换色，不用一支一支来。
- **两步渲染链已经自动化** —— 没写 per-poly 材质的刷子只出线框；没编译 BSP 树的刷子
  bounds 为 0、干脆不渲染。`apply-default-material` + `rebuild-bsp-lighting` 是硬性搭配，
  `build-bsp` 是加强版（先把每个 builder 重跑一遍再编译）。
- **默认安全** —— `delete-brush` 必须带 `--confirm=true`；体积刷
  （`NavMeshBoundsVolume` / `DefaultPhysicsVolume` / `PostProcessVolume` …）
  一律拒绝并给出解释，因为 UE 里它们也是从 `ABrush` 派生的。
- **零编译期耦合** —— 插件靠反射在运行时把自己注册进 LLMEasyShell 或 LLMEasyShell
  Lite。它能独立编译；shell 只在运行时用来接命令。

---

## 快速预览

```bash
# 一面墙
> whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300
{ "success": true, "name": "Wall_01", "brush_type": "additive", "builder": "CubeBuilder" }

# 在墙上开个门洞
> whitebox create-subtract-box --name=Door_01 --location=500,250,0 --size=200,100,300

# 一整个房间
> whitebox build-room --name=Room_01 --corner=0,0,0 --dimensions=2000,2000,500 --wall-thickness=50

# 让它显形 —— 两步都要
> whitebox apply-default-material --name=Stone
> whitebox rebuild-bsp-lighting
```

一次编辑器调用重建整份参考白盒：

```bash
> python castle build
{ "success": true, "brush_count": 1040, "create_failures": [], "phase_errors": [] }
```

---

## Technical Information

**Features:** BSP brush creation (box / subtract box / cylinder / sphere / cone
/ stairs), one-shot room and wall-segment builders, brush query / transform /
delete, material assignment with group filtering, BSP recompile, plus a
deterministic Python sample-level generator and its procedural sky material
builder.

**Code Modules:** LLMWhitebox (Editor)

**Number of Blueprints:** 0

**Number of C++ Classes:** ~4

**Network Replicated:** No

**Supported Development Platforms:** Windows: Yes, Mac: Yes, Linux: Yes

**Supported Target Build Platforms:** Windows, Mac, Linux

**Documentation Link:** [Documentation.md](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin/blob/main/skills/llm-white-box/SKILL.md) in plugin folder

**Example Project:** The plugin ships a complete example —
`Content/Maps/Lvl_Sample_Castle.umap` (a 180 m × 180 m valley with a castle,
1040 BSP brushes, 19 material groups) plus the generator that rebuilds it:
`python castle build`. The brush/builder contract is also published as a
machine-readable schema at `Config/Schemas/BrushSchema.llmwhiteboxschema`.

**Important/Additional Notes:** Editor-only plugin. Uses UE 5.5/5.6/5.7/5.8
APIs — `ABrush` (`Engine/Brush.h`), `UBrushBuilder` and the `Builders/*` headers
from the engine's `UnrealEd` module. The shell commands are reached through
**LLM Easy Shell** or **LLM Easy Shell Lite** — the host project needs one of
them installed; this plugin itself has no compile-time dependency on either.
The engine plugins **EditorScriptingUtilities** and **PythonScriptPlugin** are
enabled automatically by this plugin.

---

## 编译环境

### Required Host Plugins

| 插件 | 为什么需要 | 谁来开 |
|------|-----------|--------|
| **LLM Easy Shell** *或* **LLM Easy Shell Lite** | `whitebox ...` 命令走 shell 的 ability registry。没有 shell 插件时本插件照样加载、C++ API 照样能用，但就没有命令面。 | **你** —— 在宿主工程里装其中之一。 |
| EditorScriptingUtilities | `unreal.EditorAssetLibrary` —— 插件的 Python 侧（资产 + 材质）。 | 本插件自动开。 |
| PythonScriptPlugin | 加载自带的 Python ability（城堡生成器）。 | 本插件自动开。 |

### Module Dependencies

- Public: `Core`, `CoreUObject`, `Engine`, `EditorSubsystem`, `Json`,
  `JsonUtilities`
- Private: `Slate`, `SlateCore`, `InputCore`, `ToolMenus`
- Private，仅编辑器（`if (Target.bBuildEditor)`）：`UnrealEd`、
  `EditorScriptingUtilities`

### Verifying a Clean Build

```bash
cd "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles"
./RunUAT.bat BuildPlugin -plugin="path/to/LLMWhitebox.uplugin" -package="path/to/output" -rocket
```

---

## 功能表

| 功能 | 说明 |
|------|------|
| Box / 减法 Box | `UCubeBuilder` 刷子，可加可减（`BrushType`） |
| 圆柱 / 圆锥 | `UCylinderBuilder` / `UConeBuilder`，边数可配 |
| 球 | 插件自带的 `USphereBrushBuilder`（引擎没有球体 builder） |
| 楼梯 | N 级阶梯盒沿 +Y 上升 |
| 房间生成器 | 一次 6 支刷子：4 墙 + 地 + 顶 |
| 墙段 | 沿任意连线拉一道墙，并按方向旋转到位 |
| 刷子查询 | `list-brushes` / `get-brush`，带体积感知的类过滤 |
| 变换 | `move-rotate` —— 位置、旋转、缩放 |
| 删除 | `delete-brush`，带 `--confirm=true` 安全闸 |
| 材质 | per-poly 材质写入，可按命名组过滤 |
| BSP 编译 | `rebuild-bsp-lighting` 与加强版 `build-bsp` |
| 示例关卡 | `python castle build` —— 1040 支刷子、19 个材质组、天空穹顶、24 座远山 |
| Schema | `Config/Schemas/BrushSchema.llmwhiteboxschema` —— 机器可读的刷子/builder 契约 |

---

## 命令参考（15 条）

### 创建

| 命令 | 说明 |
|------|------|
| `whitebox create-box` | 用 `UCubeBuilder` 生成 `ABrush`。`--name`、`--location=X,Y,Z`、`--size=X,Y,Z`、`--brush-type=additive\|subtractive` |
| `whitebox create-subtract-box` | 同 `create-box`，但 `BrushType=Subtractive` —— 挖洞 |
| `whitebox create-cylinder` | `--name`、`--location`、`--radius`、`--height`、`--sides` |
| `whitebox create-sphere` | `--name`、`--location`、`--radius` |
| `whitebox create-cone` | `--name`、`--location`、`--radius`、`--height`、`--sides` |
| `whitebox create-stairs` | `--name`、`--location`、`--steps=N`、`--step-size=width,tread,rise` |

### 复合

| 命令 | 说明 |
|------|------|
| `whitebox build-room` | 一次 6 支刷子：`--name`、`--corner=X,Y,Z`、`--dimensions=X,Y,Z`、`--wall-thickness`、`--include-floor`、`--include-ceiling` |
| `whitebox build-wall-segment` | 沿连线拉一道墙：`--start=X,Y,Z`、`--end=X,Y,Z`、`--wall-size=thickness,height`、`--name` |

### 查询 / 修改

| 命令 | 说明 |
|------|------|
| `whitebox list-brushes` | 列出持久关卡里的 BSP 刷子。`--class-filter=Brush\|Volume\|<子串>` |
| `whitebox get-brush` | 单支刷子的完整信息：`--name` |
| `whitebox delete-brush` | 销毁刷子。`--name`、`--confirm=true`（必填） |
| `whitebox move-rotate` | `--name`、`--location`、`--pitch`、`--yaw`、`--roll`、`--scale` |

### 渲染链

| 命令 | 说明 |
|------|------|
| `whitebox apply-default-material` | 赋材质。`--material=/Game/...`、`--name=BrushName`（传组名会命中 `NAME` 加上整组 `NAME_*`） |
| `whitebox rebuild-bsp-lighting` | `GEditor->RebuildLevel` —— 把 BSP 树编译成可渲染几何体 |
| `whitebox build-bsp` | 先把每支刷子的 `BrushBuilder` 重跑一遍（修复跨存读后 `UModel` 与 builder 状态分叉的刷子），再 `RebuildLevel` |

---

## 两步渲染铁律

代码创建的 BSP 刷子在两件事发生之前**不会显形**：

1. **材质** —— per-poly 材质为 `NULL` 的刷子只出线框，没有实面。
   `apply-default-material` 会把材质写进 `UModel` 的每一个多边形，**同时**写进
   `BrushComponent` 的槽位。
2. **BSP 编译** —— 代码建刷子不会触发编辑器的 BSP 编译。没编译时刷子有正确的
   `UModel` 数据，但 `Bounds=(0,0,0)`，压根不渲染。

`build-bsp` 是加强版：先把每个 builder 重跑一遍，再编译。

---

## 故障排查

### 刷子只出线框

`Brush->Brush->Polys->Element[i].Material == NULL`。用
`whitebox apply-default-material` 修。

### 刷子完全不渲染

`Bounds=(0,0,0)` —— BSP 树没编译进渲染器。用 `whitebox rebuild-bsp-lighting` 修。

### 一面墙在关卡里、有材质、射线能打中，却就是不在屏幕上

两支刷子**共面重叠**会被 BSP builder 拆成一片 sliver，而 sliver 会被**静默丢弃**
（`FBSPUtils::AddPoint` 拒绝它，`BSPUtils.cpp` 里那句 warning 是注释掉的）。
丢的是面，不是状态 —— 重刷材质或重新编译都救不回来。

### 刷子原点吸附

编辑器把刷子的**原点**吸附到 10 cm 栅格（`Floor((v+5)/10)*10`），但**尺寸不吸附**。
段长是小数时，相邻两段落在不同的栅格偏移上，链既不严丝合缝也不共面。段长取栅格
两倍的倍数、起点落在栅格上，然后**离线校验**接缝算术，别靠肉眼看。

### Live Coding 重编后 `whitebox` 报 "Unknown command"

Live Coding 只重编二进制，**不会**重新注册 ability info JSON，shell 子系统里缓存的
命令列表还是旧的。重启编辑器（`llm-shell --restart`）即可重新注册。

### 提示某个刷子名已被占用

要么同名刷子还活着，要么之前销毁的同名刷子还没被 GC。用别的 `--name`，或者先
`delete-brush` 掉旧的 —— delete 会立刻给 actor 改名，把名字槽位放出来。

---

## 怎么用

1. 把插件拷进工程的 `Plugins/` 目录并启用。引擎插件 `EditorScriptingUtilities` 和
   `PythonScriptPlugin` 会由插件描述文件自动开启。
2. 在同一工程里装 **LLM Easy Shell** 或 **LLM Easy Shell Lite**。
3. 重启编辑器。插件在 `OnAllModuleLoadingPhasesComplete` 阶段把自己注册进 shell。
4. 造几何体，然后让它显形（两步都要）：
   ```
   whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300
   whitebox apply-default-material --name=Stone
   whitebox rebuild-bsp-lighting
   ```

C++ API 也可以直接从 Blueprint / Python 调：

```python
import unreal
result = unreal.LLMWhiteboxBspLib.create_box(
    unreal.Vector(0, 0, 0), unreal.Vector(1000, 500, 300), "Wall_01")
```

---

*LLM White Box v1.0.0 | YominUnreal*
