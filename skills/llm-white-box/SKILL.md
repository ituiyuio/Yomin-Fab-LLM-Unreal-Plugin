---
name: llm-white-box
description: |
  BSP-driven level whiteboxing for UE 5.5-5.8 via LLMEasyShell. When user needs:
  (1) Build rough level blockouts (rooms, walls, doorways) via shell commands
  (2) LLM-driven BSP brush creation in the editor
  (3) Compose composite structures (rooms, wall segments) from primitives
  (4) Query and manipulate existing ABrush actors in the persistent level
  (5) Fix BSP brushes that show wireframe-only or no bounds (=0) — apply-default-material + rebuild-bsp-lighting + build-bsp

  IMPORTANT: After programmatic brush creation OR loading brushes from a saved .umap, brushes have UModel data but NO compiled BSP tree — `Bounds=(0,0,0)` and the renderer skips them. You MUST pair `create-*` / `build-room` / `build-wall-segment` with `apply-default-material` (sets per-poly material — without it surfaces render as wireframe) AND `rebuild-bsp-lighting` (calls `GEditor->RebuildLevel` — without it brushes don't render at all). Don't ship a whitebox session that skips either of these.

  Use this skill.
---

# LLM White Box - BSP Level Whiteboxing

## What This Is

A 15-command shell ability for UE 5.5-5.8 level whiteboxing via BSP brushes. Builds on the engine's `ABrush` + `UBrushBuilder` family (Box / Cylinder / Sphere / Cone / Stairs) plus material-application and BSP-recompile commands. All commands are write operations on the persistent editor level.

## Reference Files

**Schema**: `Plugins/LLMWhitebox/Config/Schemas/BrushSchema.llmwhiteboxschema` — brush types, builder params, command list.

**BSP quickstart**: `.claude/skills/llm-white-box/references/bsp-quickstart.md` — UE 5.5-5.8 BSP concepts primer. Read this before first session — it documents the non-obvious two-step render path (material + compile) that distinguishes programmatic BSP from UI-built BSP.

## Quick Start

```bash
# 15 commands, all prefixed `whitebox`
# Create
whitebox create-box --name=Wall_01 --location=0,0,0 --size=1000,500,300
whitebox build-room --name=Room_01 --corner=0,0,0 --dimensions=2000,2000,500
whitebox move-rotate --name=Wall_01 --yaw=45
# Material + BSP compile (REQUIRED pair after creation/load — see "Render Pipeline")
whitebox apply-default-material
whitebox rebuild-bsp-lighting
# Query / delete
whitebox list-brushes
whitebox get-brush --name=Wall_01
whitebox delete-brush --name=Wall_01 --confirm=true
```

## Render Pipeline — The Two Non-Obvious Steps

Programmatic BSP brushes need **both** a material AND a compile to render. Skipping either = invisible or wireframe-only.

| Step | Command | What it does | When to skip |
|---|---|---|---|
| 1. Set material | `whitebox apply-default-material` | Writes `DefaultMaterial` to every `Brush->Brush->Polys->Element[i].Material` (per-poly, authoritative for BSP rendering). Also calls `BrushComponent->SetMaterial(0, mat)`. | New brushes already carry the material — `SpawnBrushWithBuilder` writes it **after** `Builder->Build()` (writing it before Build lands in an empty poly array and is silently lost). Still needed for brushes loaded from disk. |
| 2. Compile BSP | `whitebox rebuild-bsp-lighting` | Calls `GEditor->RebuildLevel(*Level)` — compiles the BSP tree from `UModel` data into the renderer's compiled geometry. Populates `BrushComponent->Bounds` (was `(0,0,0)` before). | Never — even loaded brushes from disk need this once after load. |
| 3. (Optional, stronger) | `whitebox build-bsp` | Re-runs each brush's `BrushBuilder->Build` then calls `RebuildLevel`. Use when `UModel` diverged from `BrushBuilder` spec across save/load cycles. | Skip if `rebuild-bsp-lighting` worked. |

> **Pair-with-creation rule**: after any `create-*` / `build-room` / `build-wall-segment` batch, run **both** `apply-default-material` AND `rebuild-bsp-lighting` before the user looks at the viewport. `apply-default-material` without `rebuild-bsp-lighting` = wireframe; `rebuild-bsp-lighting` without `apply-default-material` = invisible (no material to render).

## Core Concepts

### Brush types

| Type | Meaning | Use case |
|---|---|---|
| `additive` | Adds volume (BrushType=Brush_Add) | Walls, floors, pillars, room shells |
| `subtractive` | Removes volume (BrushType=Brush_Subtract) | Doorways, windows, holes in existing geometry |

### Builders

| Builder | Command | Notes |
|---|---|---|
| Box | `create-box`, `create-subtract-box` | Most common; rectangular volumes |
| Cylinder | `create-cylinder` | Pillars, columns; `sides >= 3` (8 = octagonal, 16 = round-ish, 32 = smooth) |
| Sphere | `create-sphere` | Orbs, decorative geometry |
| Cone | `create-cone` | Tents, funnels; `sides >= 3` |
| Stairs | `create-stairs` | A **solid flight** ascending along +Y. `--step-size` = (width X, tread depth Y, rise Z); step *i* is (i+1) rises tall, so every tread sits one rise above the previous one. |

### Composite commands

| Command | What it does |
|---|---|
| `build-room` | 4 walls (N/S/E/W) + optional floor + optional ceiling. 6 brushes by default. |
| `build-wall-segment` | Single wall spanning `start`→`end` with given `wall_size` (thickness, height). The brush is authored along +X and then **rotated to match the line**, so a diagonal wall really is diagonal. |

### Render-pipeline commands

| Command | What it does |
|---|---|
| `apply-default-material` | Writes a material (default `/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial`) to the brushes of the level. Without `--name` → every whitebox brush; with `--name=NAME` → the brush labelled `NAME` **plus every brush in the `NAME_*` group** (one call re-materializes a whole class of building). Targets per-poly (`Brush->Brush->Polys->Element[i].Material`) — the authoritative source for BSP rendering. |
| `rebuild-bsp-lighting` | Calls `GEditor->RebuildLevel(*Level)` to compile the BSP tree. Without it, brushes have `UModel` data but `Bounds=(0,0,0)` and the renderer skips them. Pairs with `apply-default-material`. |
| `build-bsp` | Stronger than `rebuild-bsp-lighting` — re-runs each brush's `BrushBuilder->Build` first, then `RebuildLevel`. Use when `UModel` diverged from `BrushBuilder` spec. |

### Safety gates

- `delete-brush` requires `--confirm=true`. Without it, returns `success: false, error: "delete-brush requires --confirm=true (safety gate)"`.
- **Volume brushes are refused.** UE derives `AVolume` from `ABrush` (`Engine/Classes/GameFramework/Volume.h`), so a raw `TActorIterator<ABrush>` sweep also yields `NavMeshBoundsVolume` / `DefaultPhysicsVolume` / `PostProcessVolume`. Those are *not* whitebox geometry — `get-brush` / `delete-brush` / `move-rotate` / `apply-default-material` now reject them with an explanatory error instead of silently treating them as brushes (deleting a navmesh volume is not a recoverable mistake). The engine's own predicate is `ABrush::CanEverAffectBSP()` (`Engine/Private/Brush.cpp:198`).
- `list-brushes` default filter `Brush` = **geometry only**. Pass `--class-filter=Volume` for volume brushes, or an empty filter for both.

### Coordinate system

- All `location` and `size` args are in UE world units (cm)
- Vectors are space- or comma-separated: `0,0,0` or `0 0 0`
- Z is up (gravity is -Z)

## Examples

### Build a 4x4m room with door

```bash
whitebox build-room --name=LivingRoom --corner=0,0,0 --dimensions=400,400,300 --wall-thickness=20
whitebox create-subtract-box --name=LivingRoom_Door --location=190,0,0 --size=80,40,200
```

### Round pillar

```bash
whitebox create-cylinder --name=Pillar_NE --location=380,380,0 --radius=15 --height=300 --sides=16
```

### Spiral of spheres

```python
# via python ability in LLMEasyShell
import unreal
for i in range(8):
    angle = i * 3.14159 / 4
    x = 100 * unreal.Math.cosine(angle)
    y = 100 * unreal.Math.sine(angle)
    unreal.LLMWhiteboxBspLib.create_sphere(
        unreal.Vector(x, y, 50), 50.0, f'Spiral_{i}')
```

## Out of Scope

- **GeometryScripting / `UDynamicMesh` / `UCSGMeshesTool`** — modern mesh operations. Future work (see spec §10).
- **Baking BSP to StaticMesh asset** — use UE's built-in "Convert Brush to Static Mesh" menu.
- **Modeling Mode interactive brushes** — UE built-in, just press `2` in the editor viewport.
- **Streaming levels** — only the persistent level is targeted.
- **Runtime (PIE) operations** — whitebox is editor-only.

## CLI Commands

> **Note**: 注册名是 **`llmwhitebox`**（不是 `whitebox` 或 `llm-white-box`）。`Plugins/LLMWhitebox/Source/LLMWhitebox/Private/LLMWhiteboxModule.cpp` 通过 `Info.AbilityName = TEXT("llmwhitebox")` 注册 — `LLMEasyShell` dispatcher 看到 `whitebox` 会返回 `"Unknown command"` (但 LLM 调用时仍可写 `whitebox <cmd>` — dispatcher 把 prefix 去掉)。

llmwhitebox ability 注册 **15 个 sub-cmd**，runtime `llm-shell -q -j -c help llmwhitebox` 1:1 锁定。Source-of-truth：`LLMWhiteboxCommandHandler.cpp:266-462` `ULLMWhiteboxCommandHandler::ExecuteWithResult` 内的 `if (Command == TEXT(\"...\"))` 15 个 dispatcher cascade（每个分支调 `ULLMWhiteboxBspLib` 对应 helper），加上 `LLMWhiteboxModule.cpp:54/56` 两条 `OnAllModuleLoadingPhasesComplete.AddRaw`（分别注册 `RegisterAsLLMEasyShellAbility` 走 full 路径 + `RegisterAsLLMEasyShellLiteAbility` 走 lite 路径）：

| subcommand | usage | description |
|---|---|---|
| `create-box` | `whitebox create-box [--name=NAME] --location=X,Y,Z --size=X,Y,Z [--brush-type=additive\|subtractive]` | 在指定位置/大小生成 ABrush (UCubeBuilder) |
| `create-subtract-box` | `whitebox create-subtract-box --name=NAME --location=X,Y,Z --size=X,Y,Z` | 同 create-box 但 BrushType=Subtractive (挖洞) |
| `create-cylinder` | `whitebox create-cylinder --name=NAME --location=X,Y,Z --radius=F --height=F --sides=N` | 生成圆柱形 brush |
| `create-sphere` | `whitebox create-sphere --name=NAME --location=X,Y,Z --radius=F` | 生成球形 brush |
| `create-cone` | `whitebox create-cone --name=NAME --location=X,Y,Z --radius=F --height=F --sides=N` | 生成圆锥 brush |
| `create-stairs` | `whitebox create-stairs --name=NAME --location=X,Y,Z --steps=N --step-size=width,tread,rise` | 实心楼梯，沿 +Y 升；第 i 级高 (i+1) 个 rise |
| `list-brushes` | `whitebox list-brushes [--class-filter=Brush\|Volume\|<substring>]` | 列出 persistent level 的 brush（默认只列白盒几何；`Volume` 列体积 brush；空 = 全列） |
| `get-brush` | `whitebox get-brush --name=NAME` | 获取单个 brush 完整详情 (location/size/brush_type/builder)；体积 brush 被拒绝 |
| `delete-brush` | `whitebox delete-brush --name=NAME --confirm=true` | 删除 brush (--confirm=true safety gate 必需)；体积 brush 被拒绝 |
| `move-rotate` | `whitebox move-rotate --name=NAME --location=X,Y,Z [--pitch=F] [--yaw=F] [--roll=F] [--scale=X,Y,Z]` | 更新 brush transform |
| `build-room` | `whitebox build-room --name=NAME --corner=X,Y,Z --dimensions=X,Y,Z [--wall-thickness=F] [--include-floor=true] [--include-ceiling=true]` | 一键生成 6 brush 房间 (4 墙 + 地 + 天花板) |
| `build-wall-segment` | `whitebox build-wall-segment --start=X,Y,Z --end=X,Y,Z --wall-size=thickness,height [--name=NAME]` | 沿直线生成单面墙（会按 start→end 方向旋转，斜墙真的是斜的） |
| `apply-default-material` | `whitebox apply-default-material [--material=/Game/Path/M_Foo.M_Foo] [--name=BrushName]` | 回填材质；无 `--name` = 全部 brush；`--name=NAME` = NAME 精确 + `NAME_*` 整组 |
| `rebuild-bsp-lighting` | `whitebox rebuild-bsp-lighting` | 调用 GEditor->RebuildLevel 编译 BSP tree → renderable geometry (Bounds=(0,0,0) → 修复) |
| `build-bsp` | `whitebox build-bsp` | 对每个 brush 重新跑 BrushBuilder + RebuildLevel (比 rebuild-bsp-lighting 更强: 修复 UModel drift) |

```bash
# 典型工作流: 建房间 → 补材质 → 编译 BSP
whitebox build-room --name=MainCity --corner=0,0,0 --dimensions=4000,4000,3000 --wall-thickness=200
whitebox apply-default-material
whitebox rebuild-bsp-lighting
```

## Sample Level — 山谷 + 欧洲中世纪城堡

插件自带一份示例关卡 `Plugins/LLMWhitebox/Content/Maps/Lvl_Sample_Castle.umap`（挂载点 `/LLMWhitebox/Maps/Lvl_Sample_Castle`）：一条**蜿蜒河道**在谷底穿过，两岸是阶梯化的岩壁台地，西岸肩部立着一座**欧洲中世纪城堡** —— 城墙 + 四角八边形鼓塔 + 门楼 + 主楼（keep）+ 大厅 + 礼拜堂 + 外郭马厩/水井 + 崖阶 + 石桥 + 道路 + 针叶林 + 巨石。地形 180 m × 180 m，谷底 72 m 宽，城堡台地比谷底高 14 m。

它同时是**能力面覆盖度的证明**：盒体（墙/台/塔）· 圆柱（鼓塔，正八边形）· 台阶（崖阶与屋顶山墙）· 减法盒（门洞/窗洞）—— 以及一件 BSP 插件特有的事：**用规则栅格铺地形**。

### 这份关卡里最容易踩的六个坑（照抄即可）

| 坑 | 现象 | 做法 |
|---|---|---|
| **共面相遇安全，部分嵌入致命** | 两支刷子**共面**相接是安全的；一旦**部分嵌入**，BSP 编译出来的接缝是一片薄片（sliver），整段墙可能整圈消失 | 鼓塔与城墙的接缝：墙的端面**埋进鼓塔内部**，由鼓塔自己的平面把墙的两个长面切齐。绝不让圆柱去切墙 |
| **斜面预算** | BSP 节点超过 255 个顶点会**静默丢面**（编译器的警告被注释掉了） | 斜面笔刷限量：八边形鼓塔 8 个面 × 4，大厅/礼拜堂双坡屋顶各 8 个面，山墙用**阶梯盒**（零额外斜面） |
| **阶梯山墙而非实体三角墙** | 实体三角墙的顶面会在檐口留下一道水平"盖子"，屋檐看起来像被削平 | 山墙做成阶梯盒，被屋面下表面精确裁切，且不增加任何斜面 |
| **地形用规则栅格** | 不规则三角网会把栅格平面切进自己的单元面，产生一堆斜面和薄片 | 900 cm 栅格 ⇒ 栅格平面永远切不到自己的单元面；地形高度只取整格（谷底 0 / 河床 −400 / 台地 1400） |
| **天空不能靠引擎 SkyAtmosphere** | 那张 LUT 在部分机器上算出来是**黑**的 ⇒ 天空纯黑 ⇒ 自动曝光把受光面打到过曝 | 自建 **unlit + two-sided + IsSky** 的渐变穹顶，跨机一致；**并且必须把引擎的 `SkyAtmosphere` actor 删掉**，否则两套天空打架（天上会出现一条深蓝色"海"带） |
| **天光要显式指定 cubemap** | 默认天光源是"捕获天空"，而天空在本机是黑的 ⇒ 只剩直射光，暗面全黑 | 天光 `source_type` 选 "cubemap" 语义的成员 + `DefaultTextureCube`，跨机一致 |

地表平面用 `StaticMeshActor` 而不是 BSP 刷子：一个那么大的平面在 BSP 里是一张巨大的面，而 BSP 编译会把**每一张穿过它的面**切开 —— 世界中间会被挖出一个洞。

材质组与配色沿用上一代思路：每支 brush 标签形如 `<材质组>_<构件名>`，用 `apply-default-material` 的**组过滤**按组上色 —— **19 个材质组**（`Ground`/`Rock`/`Water`/`Stone`/`Masonry`/`Slate`/`Thatch`/`Timber`/`Wood`/`Iron`/`Road`/`Forest`/`Banner`/`Lamp` + `Window`/`Haze`/`Field`/`Grove`/`Brass`）19 次调用换掉整座城堡的配色。后 5 组是第二轮"加细节"时开的口：窗洞内衬（Window）、远山空气透视（Haze）、麦田（Field）、阔叶树冠（Grove）、黄铜件（Brass）。母材质 `M_Master_Whitebox`（Surface 域 + Default Lit，世界坐标三平面两级网格：10 m 粗线 + 1 m 细线）保留，实例换成了 `MI_Castle_*`。

可复现生成器随插件走（`python castle build`），源码 `Plugins/LLMWhitebox/Content/Python/LLMWhiteboxAbilities/abilities/castle.py`（通用母材质与天穹材质拆在同目录的 `_wb_material.py`，下划线前缀 = 不注册成命令）。它直接调 `unreal.LLMWhiteboxBspLib`（一次编辑器调用建完整座关卡；逐条 shell 调用建 1040 支 brush 不可接受）。

```bash
python castle open        # 创建/载入示例关卡（走引擎模板，见下）
python castle build       # 生成/重建示例关卡（先清后建，幂等）
python castle stats       # 看当前关卡的 brush 清单（按材质组聚合）
python castle clear       # 清掉当前关卡所有 brush
python castle camera      # 把视口摆到英雄机位（也可 `camera <preset>` 选 hero/aerial/gate/keep/flank/dusk/river）
python castle verify      # 从磁盘重载并报告关卡里实际有什么
python castle atmosphere  # 只重建大气（天穹/日光/天光），不碰几何
python castle save        # 强制存盘当前关卡（shell 的 save 只写"脏"包，旋转太阳不一定会把关卡标脏）
python castle skydebug    # 只读探针：读回天穹材质的常量与相机节点可用性
```

> **两步走**：切图与建几何必须分成两次编辑器调用。一次调用里做两次 `load_map` 是已知崩溃模式。`castle open` 只切图，`castle build` 建几何。

### 造关卡时踩过的坑（血泪，直接照抄）

| 坑 | 真相 | 做法 |
|---|---|---|
| `LevelEditorSubsystem.new_level()` 造出来的关卡永远是黑的 | 它走 `GEditor->NewMap()`，产出**没有 WorldSettings、没有 builder brush** 的空壳世界（0 个 actor）。没有 builder brush ⇒ BSP tree 永不编译成可渲染面 ⇒ 再多次 `RebuildLevel` 也白搭，而且因为 .umap 存的是 brush 而不是编译面，**存盘重载后依然是坏的** | 用 `new_level_from_template(path, "/Engine/Maps/Templates/Template_Default")`——模板自带太阳/天空/雾/云/地板 |
| 视口全黑 ≠ 几何没渲染 | 引擎的 **SkyAtmosphere / M_SimpleSkyDome / VolumetricCloud 全部依赖大气 LUT**，某些机器（虚拟 GPU）LUT 回来是黑的 ⇒ 背景 = 引擎默认 clear color 纯黑。**新 spawn 一个 SkyAtmosphere 也照样黑**（LUT 才是缺的那块）；而且它与自建穹顶共存时会在地平线上方压出一条硬边深蓝带，读起来像"海" | 生成器**把引擎的 `SkyAtmosphere` + `VolumetricCloud` 一起删掉**，只留自建的 unlit 渐变穹顶（不依赖任何渲染目标，跨机一致）；模板自带的 `SM_SkySphere` 也要清掉（黑穹顶会罩在自家天空外面） |
| 自建天穹在**刚加载关卡的那一帧**是纯黑的，视口上还平铺着一句黄字 "YOUR SCENE CONTAINS A SKYDOME MESH WITH A SKY MATERIAL BUT IT DOES NOT COVER THAT PART OF THE SCREEN…" | **既不是几何错，也不是穹顶太大**：编辑器加载关卡时会**异步编译材质 shader**，那一帧天穹的 shader 还没就绪 ⇒ 穹顶**不进主 pass** ⇒ 背景直接露 clear color（纯黑）。引擎侧机制：`FSkyMeshBatch::bVisibleInMainPass = ViewRelevance.bRenderInMainPass`（SceneVisibility.cpp）；场景里有 sky material 而主 pass 里没有 sky mesh 时，引擎就在视口上画警告（ReflectionEnvironmentRealTimeCapture.cpp:313）。**实测与穹顶半径无关**：1 km 穹顶（scale 2000）在 shader 就绪后天空渲染完全正常（像素 156,175,193 / 171,188,204 / 160,184,204，与 400 m 同档）⇒ "1 km 太大所以渲染器不盖满屏幕"是误判 | **等 shader 编译完，再出一个新帧**：重新加载关卡（`python castle reload`）天空立刻恢复（天空像素 (0,0,0) → (170,188,204)）。**别因为黑屏去改几何、缩穹顶** —— 那是把无关的关卡改坏。另外：**别每次运行都重建材质**：重建会作废材质的 shader 缓存，凭空制造一段黑屏窗口（`ensure_sky_material()` 用 metadata tag `WB_SkyBuild` 做幂等，已建过就直接复用） |
| 材质整体一色、组配色全部不可见（整关呈暗剪影） | **Custom node 网格 HLSL 的线项写反**：minor 线项写成 `((0.5-wN)-d)/wN` 时在整个格子里饱和到 1，`lerp(PaintCol, GridCol, mask)` 恒出 GridCol——每张缩略图看着正常，上到几何就只剩网格色 | 线项必须是**以线为中心的 ramp**（`saturate((wN - d) / wN)` 形）；改完先看材质缩略图**之外**的实拍——缩略图无法暴露 mask 饱和 |
| 分级网格的淡出距离错乱 | 淡出若挂在**每级线自己的宽度**上：细线过早消失，且粗线（半宽大）反而比细线死得早——层级倒挂 | 淡出用**共享的世界尺寸判据**（`fwidth(WPos)` 与 FadeSize 比，默认 10 cm/像素），线宽只负责画分级 |
| 相机指哪儿完全不对 | **`unreal.Rotator` 的位置参数顺序是 (roll, pitch, yaw)**，不是编辑器 UI 的 (pitch, yaw, roll)。`unreal.Rotator(-18, 49, 0)` = roll=-18 / pitch=49（朝天）/ yaw=0（正北）——关卡直接飞出画面 | 一律用关键字：`unreal.Rotator(roll=0.0, pitch=-18.0, yaw=49.0)` |
| `python editor screenshot` 恒返回纯白 | 编辑器重启后离屏 `FViewport::ReadPixels` 路径不可信（连已知正常的关卡也是白的）—— 同步路径读的是裸 backbuffer | 改走**异步**路径：`unreal.LLMEasyShellEditorLib.capture_active_viewport(path, w, h, 0, True, False)`（`bAsync=True` ⇒ 引擎用 `FScreenshotRequest` 落盘）。注意它**会给文件名加 `00000` 后缀**，所以传的是**不带扩展名的基名** |
| 窗口捕获拿到的是**陈旧帧** | `PrintWindow` 取的是 DWM 上一次合成的内容；视口没有 pending 重绘时，相机改了画面也不变 —— 会把"改完没效果"误读成"改错了" | 用 `FScreenshotRequest`（`Saved/Screenshots/`）。**它要等下一次真实渲染才会 flush**：相机不变 ⇒ 视口不自刷新 ⇒ 不出图 |
| 截图拍到的是**上一个机位** | `FScreenshotRequest` 在视口的下一个 DRAW 里 flush，而 ticker 跑在**渲染之前** ⇒ 同一次调用里"改相机 + 请求截图"拍到的是旧帧。更狠的一层：`set_level_viewport_camera_info` 改的是**会被存进 .umap 的那份相机**，视口当前渲染的那台并不跟着动 —— 新相机要**重载地图**才生效 | 拆成多步：① 设相机（`python castle camera hero`）→ ② 存盘（`save`）→ ③ **从磁盘重载地图**（`python castle reload`）→ ④ 逼出新帧（`python editor set_realtime value=true`，视口转持续渲染）→ ⑤ 抓图（`editor_shot.ps1` + `crop.ps1`）。少任何一步都会拍到上一帧。**`console viewmode unlit` 这条路是死的**：它是 editor exec 不是 CVar —— shell 的 `console` 回 "not a known CVar and no console command consumed it"，`python editor console viewmode unlit` 回 "unknown command"，`set_viewport_view_mode` 也返回 False。**另外新加载的关卡要等材质 shader 编译完**，否则天空那一块是纯黑 (0,0,0)（见上面那条坑），拍到的是假天 —— 抓完必须用像素采样核对 |
| 抓到的图"变了一点点"（选中框变了、几何没变） | 视口的 3D 场景与它的 overlay 是两套：overlay 随输入立刻重画，3D 只在**有重绘理由**时才出新帧。所以"看得见选中高亮"并不等于 3D 重渲染过 —— 很容易据此误判成"改对了" | 强制出新帧：`python editor set_realtime value=true`（视口转持续渲染，最稳），或改一次 showflag，或最小化再还原窗口。判据仍是"两次截图字节完全一样 = 没重绘"，抓完用像素采样对比关键位置颜色（天空像素是不是 (0,0,0)） |
| 截图请求**已受理**（返回 "Async screenshot requested … on next frame"）却**永远不落盘** | 视口**失焦/不出帧**时，请求就一直挂在队列里。相机**没变**时更不触发重绘（视口没有重绘理由） | 两条路：① 引擎自己的 `unreal.AutomationLibrary.take_high_res_screenshot()`（按当前视口相机渲染），**先发请求、再 `RedrawAllViewports`** —— 顺序反了请求就永远排不上队（每个 `RedrawAllViewports` 要单独一次编辑器调用，才会多走一帧）；② Win32 直接抓窗口像素：`powershell -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1`。两条路都要求 UE 窗口在前台可见，否则 DWM 交回的是上一帧 |
| 抓到的图**看着没变**，其实是陈旧帧 | `PrintWindow` 交回的是 DWM 缓存的**最后一帧**；视口没出新帧 ⇒ 截图与上一次逐字节相同 | 判据：两次截图的字节数完全一样 = 没重绘，不是场景没变。抓帧前把 UE 窗口拉回前台（`ShowWindow(SW_RESTORE)` + `SetForegroundWindow`），抓完用像素采样对比关键位置的颜色 |
| 一条长廊/长墙**看着是镂空的栅栏** | 墙、屋顶、柱列三者的**跨度不一致**：柱列 7000 长，墙和顶只有 4400 ⇒ 北半截只剩一排无遮无挡的独立柱子，从庭院一眼望穿到护城河 | 同一构件的基座/墙/顶/柱**必须覆盖同一段**（用同一个 `length` 变量，别各写各的数字）。廊庑另加一道**槛墙**填住柱列下半段，空中看才是一堵墙 |
| 屋顶从檐角**飞出一堆木板** | 翼角条的长度用**水平距离**乘系数算（`hypot(dx,dy) * 1.42`），真实三维跨度只有 60–66% ⇒ 每根条**两头各多伸出 110–170 cm**；再叠上"翼角刷成金色"，就成了金色板片乱飞 | 长度取**三维**跨度 `hypot(hd, dz)`；且翼角属于**屋面**的一部分，必须穿屋顶本色（金色只留给正脊/垂脊/鸱吻） |
| 屋顶塌成**一摞平板** | 每层水平收进是线性 ⇒ 坡面读成金字塔；而且调用方给的 `height` 直接决定起脊高度，一个偏小的值就把屋顶压平 | 收进走**举折** `t**1.7`；起脊高度带**坡度下限** `rise = max(height, 长跨 × tan(26°))`，`height` 只是下限 |
| 某些构件**永远拿不到材质**（一直是默认灰） | 材质组表 `GROUPS` 漏了这个组名，但代码里已经在刷 `Gold_*` 标签 ⇒ `apply-default-material --name=Gold` 从来没跑过 | `GROUPS` 表与代码里的组名前缀**逐一对齐**（每加一个组前缀就往表里加一行）。组名之间不能互为前缀（`Gold` 与 `Gold2` 会串色；`Tile` 与 `TileY` 安全） |
| 刷子**在关卡里、材质也对、射线也打得到，屏幕上却没有**；大片地坪变成一个洞 | 不是破面、不是反向、也不是"预算用完"（实测：1759 支刷子照样完整渲染，差别只在**平面朝向**）。真相是 **BSP 节点的顶点数上限**：`FBspNode::MAX_NODE_VERTICES = 255`。一个面每被一个平面切穿一次，它所属节点里就多一个顶点；超限时 `FBSPUtils::AddPoint` **直接拒绝加点**，而那条警告在引擎 `BSPUtils.cpp` 里是**注释掉的** ⇒ 面被静默丢弃，日志一声不吭 | 把大面切小：**长墙按 ≤300 拆段**、**大地坪按 ≤1200 铺瓦片**。碎片是轴对齐的，BSP 会合并共面，代价几乎为零 |
| 同一关卡里有的墙没了、有的墙好好的 | **斜面笔刷**（垂脊/翼角）是旋转的：6 个面是 6 个没有同伴的斜平面，而 **BSP 平面是无限的** ⇒ 每一根都会切穿全关卡的每一张大面，切在哪里取决于**局部几何密度** ⇒ **轴线附近（午门/三大殿/后三宫最密的地方）最先死**，离得远的墙段反而好好的 | 斜面笔刷是最贵的平面来源：要么砍数量（次要建筑不挂垂脊），要么把被切的面切小。实测：删掉全部 644 支斜面笔刷 ⇒ 宫墙整条贯通 |
| 墙上凭空缺一段，缺口**正好在某个构件的位置** | **实体互相穿插** ⇒ CSG 相减 ⇒ 被减的那个面被啃掉。2026-11-11 实测：16 个墩台每个咬进墙厚 100（墙厚只有 200）⇒ 墙在每个墩台背后各缺一块，缺口的世界坐标与墩台坐标完全吻合；删掉这 16 个墩台，缺口当场消失 | 骑在墙上的构件要么**正好贴在墙面上**（共面接触），要么**整个跨过墙厚**（全跨骑：把墙那一段**替换**掉，而不是咬进去）。**半跨骑最毒**：它既没替换也没贴上，切出来的是薄片 |
| 墙上缺一段，缺口位置**压在某个构件的投影上**（构件本身好好的） | 真正的机理不是"共面"，而是**薄片**：两个实体**部分**重叠时，重叠边界变成一条切割平面把双方切开，切出来的**碎片（sliver）**正是 `AddPointToNode` 在节点顶点数达到 `MAX_NODE_VERTICES-1`（=254）时**静默拒收**的东西。2026-11-11 实测：压顶线**嵌入墙顶 10 cm** ⇒ 墙的外立面被切成 990 cm 的大面 + **10 cm 的薄片**，沿 178 m 整圈 ⇒ **整圈宫墙从屏幕上消失**，而门楼、地面、所有屋顶都好好的；把压顶线改成**恰好压在墙顶 z=900**（共面接触），墙立刻完整回来 | **共面接触是安全的**（宫墙自己的 60 段就是面对面贴合的，渲染完美）；**部分嵌入才致命**。跨在别人身上的构件：要么共面贴上，要么全跨骑替换，**绝不半咬** |
| 把"共面"全部改成"嵌入"之后，**墙和地面反而全没了** | 嵌入式接触不是免费的：它给大面新增 CSG 切割，切割又变成**薄片**，而薄片正是那个会耗尽的预算。2026-11-11 一次性把铺装/墙帽/城门/三台/河槽全改成嵌入式 ⇒ 南墙整段消失，整个广场地面变成一个**能看见天空的洞** | 见上一条的修正规则：**共面接触安全，半嵌入致命**。改完**一次只改一族**，重建 + 截图对比，别一把梭 |
| 想判定"某个构件族是不是元凶"，但每次干净重建要 4 分钟、增量重建又复现不出故障 | 增量实验态与干净构建态的笔刷数差 ~80（重名被拒），且 BSP 编译顺序不同 ⇒ 增量态怎么加都正常，干净构建就是坏的 | 用**可自动判定的像素指标**代替人眼看图：截图后按颜色统计某类像素占比（如"砖红""城堡石白"），指标用阈值一分为二，再**分组二分**：每轮 `delete` 一族刷子 + `rebuild_bsp_lighting` + 拍一张，指标从 0 跳到 0.6 就说明这族是元凶。**先记基线数值**再动手，否则"跳变"没有参照 |
| **分段链（长墙 / 铺地）在接缝处漏光、或者两段重叠** | 编辑器把 brush 的**原点**吸附到 10 cm 栅格（`Floor((v+5)/10)*10`），但**尺寸不吸附**。段长是小数（`span/count`）时，两端落在**不同的栅格偏移**上，链就既不严丝合缝也不共面 | 段长取 `2*GRID` 的倍数（中心才落在栅格上），起点落在栅格上，用精确算术逐段推进 ⇒ 接缝**零缝隙、零重叠**。这条规则要**离线校验**（脚本按同样规则重算一遍每段的两端坐标），不要靠肉眼看接缝 |
| **塔楼圆角把墙切出裂缝** | 圆柱/八棱柱**穿进**墙里，两支刷子**部分嵌入** ⇒ 接缝是一片薄片，整段墙可能消失 | 墙的端面**埋进鼓塔内部**，让鼓塔自己的平面把墙的两个长面切齐；实测正八边形关于顶点轴对称 ⇒ 城墙两侧面被同一个 x 切齐，无需探测八边形的朝向 |
| 想查"面还在不在"，却看到每支 brush 的 `umodel_polys=6` | `umodel_polys` 是笔刷的**源面数**——盒子永远是 6，跟 BSP 编译成什么样毫无关系。真正进渲染的是编译后的 BSP 节点 | 可靠量法只有两个：**判决实验**（一次只动一个变量，重建 + 截图对比）和**材质组判别**（把某组临时换成醒目颜色重截一张，颜色不变 ⇒ 那片区域根本不是该组的表面。2026-11-11 用它证明了"深蓝地面"其实是透过地面看到的天空） |
| 一半雉堞/墩台**根本没生成** | 用 `abs(x)` 造名字 ⇒ 镜像两侧塌成同名，插件以"名字已占用"拒绝第二支，**静默丢弃**（实测 17 支：8 墩台 + 9 雉堞） | 名字用**带符号**的 `n2700` / `2700`；并加**重复标签守卫**，把重名记成 `create_failure` 而不是静默丢弃 |
| 巨型地坪（120000×48950）拖垮整关 | 一个 1200 m 的单面 quad 会让 BSP 树围着它细分，其它面全被切碎 | 地平线不是建筑：改用 4 个 **StaticMeshActor 平面**（`/Engine/BasicShapes/Plane`），不进 BSP |
| 新建的材质立刻按路径 load 会失败 | 刚 `create_asset` 的资产还没进 AssetRegistry，`EditorAssetLibrary.load_asset(path)` 返回 None | 构造函数直接返回**材质对象**，别返回路径 |
| 模板的 Floor 是黑的 | `SM_Template_Map_Floor` 挂的是 `MI_ProcGrid`——**Landscape 材质实例**，挂在普通 StaticMeshActor 上渲染成黑 | 覆盖成草皮材质（生成器 `_build_atmosphere` 已自动做） |
| `delete_asset` 报成功但文件还在磁盘 | 内存里的包还在 | 磁盘 `rm -- "<path>"` + 重启编辑器清内存包 |
| 天空是一整片**灰白**，颜色全被洗掉 | 天空材质的**绝对值比受光面还亮**。实测 2026-11-11：旧配色（地平线 0.95 / 天顶 0.11-0.44）渲染成 0.77,0.73,0.73 的平片，而石墙只有 0.26-0.47 —— 天空亮一倍以上，自动曝光把它推进 tonemap 去饱和高光的区段，颜色全没了 | 天穹的配色要**低于**受光面（地平线 0.42 / 天顶 0.045-0.20），云层同理。判据不是"参数好不好看"，而是**在视口里采样天空与石墙的像素比**：天空应当明显低于墙面 |
| 太阳盘**怎么都不出现**，而且云的受光**不随方位变化** | `MaterialExpressionConstant3Vector` 的 `constant` **静默没写进去**（在裸 `try/except` 里）。实测：天空左右两半的云亮度 0.724 / 0.719 —— 太阳项根本没生效；`normalize((0,0,0))` 是 NaN，于是太阳盘、辉光、洗光、云受光**全死**，而渐变和噪声不依赖 `sun`，所以天空"看着还行" | 用 **`VectorParameter`**（HorizonCol/ZenithCol/SunCol 这条路实测有效），并且**写完立刻读回校验**；Custom node 的输入没接上**不报 shader 错**，只是保持 (0,0,0) —— 所以每个 `connect_material_expressions` 都要打 warning，不能 `except: pass` |
| 减法盒（门洞/拱券）**把路基和铁栏一起吃掉了** | 减法刷会切掉**一切**与它重叠的实体。城门拱券的减法体宽出 400 cm，把门前路基切掉 500 cm（只剩 100 cm 悬空短桩）；闸门 7 根铁栏整根落在减法体内 ⇒ 等于不存在 | 减法体的尺寸必须**正好等于**要留空的净空（门楼净深 600），并且**减法体里不能放任何可见几何** —— 闸门铁栏改到门楼外表面平面 |
| 装饰构件（浮雕窗/铁箍/旗杆/烟囱）**把墙面啃出缺口** | 装饰件**部分嵌入**被贴面 ⇒ 接缝变薄片 ⇒ 节点顶点数超限后被静默丢弃 ⇒ 整段墙可能消失（见上面两条薄片的坑） | 装饰件一律**站出去 40 cm、与墙面共面接触**。共面安全、半嵌入致命 |
| 远山/天际线**把 BSP 预算吃光** | 一张 400 m 的面在 BSP 里会被所有穿过它的面切开 | 远山走 **StaticMeshActor**（压扁球 / 锥体 + 肩丘），不进 BSP；近山脊与远山用不同材质做空气透视 |
| 七个机位拍出来**是同一张图**（逐字节相同） | 编辑器**没有拿到前台**：后台进程直接 `SetForegroundWindow` 会被 Windows 拒绝（只有拥有前台输入队列的调用方才可抢焦点），编辑器于是不 tick、视口不出新帧，`PrintWindow` 交回的 DWM 缓存永远是上一帧。实测：偷焦点前前台 hwnd=0x855868、编辑器=0x657212 | 抓帧前用 **AttachThreadInput 挂到前台线程的输入队列**再 `SetForegroundWindow`（附 `SwitchToThisWindow` 兜底），之后 `GetForegroundWindow` 必须等于编辑器 hwnd。**判据：两两像素差全为 0 = 没重绘**，不是"场景没变" |
| 机位算好了，画面却不对 | 视口 FOV 实测 **≈112° 水平 / ±38.6° 垂直**（不是 90°）。用 90° 去算构图，机位会偏 10° 以上 | 实测标定法：同一机位偏 20° yaw 拍两张，**互相关**求水平位移 → px/deg = 位移/20 → FOV = 宽/px每度。再用它反推物体的画面位置 |
| 相机 yaw 转了，画面里的东西**往左跑** | UE 是左手系：yaw 0=+X、yaw 90=**+Y（右）**，所以**加大 yaw = 相机右转 = 画面内容左移**。按"右手系逆时针"去推算会整体搞反 | 记住这条方向律，再用"yaw 差 20° 拍两张看东西往哪边跑"自证一遍，别靠直觉 |

<!-- Forensic: see SKILL_CHANGELOG.md §1 (tool-fix-07 session61+93+98 closure: 0→15 sub-cmd silent-missing + L141 stale breakdown + cascade-end anchor off-by-15 fix) -->

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `bSuccess=false, error="Editor world is null"` | Editor not fully loaded | Wait for `Idle` state, retry |
| `error="Invalid size: ..."` | Size component <= 0 | All size components must be > 0 |
| `error="Brush not found: NAME"` | Label mismatch | Use `list-brushes` to see actual labels |
| `error="delete-brush requires --confirm=true"` | Forgot flag | Add `--confirm=true` |
| Build fails on some UE version | BSP builder headers may have moved | Check `Engine/Source/Editor/UnrealEd/Classes/Builders/` (CubeBuilder.h / CylinderBuilder.h / ConeBuilder.h) and `Engine/Source/Runtime/Engine/Public/Model.h` for the current paths |
| **Brushes render as wireframe only (no surfaces)** | `Brush->Brush->Polys->Element[i].Material == NULL` — UModelComponent requires per-poly material to render filled surfaces | `whitebox apply-default-material` (writes DefaultMaterial to every polygon) |
| **Brushes don't render at all (invisible) even with material set** | `Bounds=(0,0,0)` — BSP tree not compiled into renderer | `whitebox rebuild-bsp-lighting` (calls `GEditor->RebuildLevel`) |
| **A long wall is in the level, has its material, passes a raycast — and is still not on screen** | 两支 brush **共面重叠**（segment 之间多出几厘米）被 BSP builder 拆成 sliver 后**静默丢弃**：`FBSPUtils::AddPoint` 拒绝加 sliver，而那句 warning 在 `BSPUtils.cpp` 里是注释掉的 | 把分段改成**严格贴合**（下一条）。`rebuild-bsp-lighting`、重刷材质、重新 build 都救不回来 —— 丢的是面，不是状态 |
| **分段链（长墙 / 铺地）在接缝处漏光、或者两段重叠** | 编辑器把 brush 的**原点**吸附到 10 cm 栅格（`Floor((v+5)/10)*10`），但**尺寸不吸附**。段长是小数（`span/count`）时，两端落在**不同的栅格偏移**上，链就既不严丝合缝也不共面 | 段长取 `2*GRID` 的倍数（中心才落在栅格上），起点落在栅格上，用精确算术逐段推进 ⇒ 接缝**零缝隙、零重叠**。这条规则要**离线校验**（脚本按同样规则重算一遍每段的两端坐标），不要靠肉眼看接缝 |
| **压顶 / 女儿墙之类压在墙顶上的构件，看着像浮空 5 cm** | 高度 70 的构件中心落在 935 这种**非栅格值**上 → 被吸附到 940 → 整体抬高 5 | 高度取 `2*GRID` 的倍数，让中心落在栅格上。**并且让它与被承载物在同一个栅格平面上"恰好接触"**（压顶底面 = 墙顶面），**不要嵌进去**：嵌入 10 cm 会在墙的外立面上切出一条 10 cm 的薄片，薄片耗尽 BSP 节点顶点预算 ⇒ **整面墙静默消失**。2026-11-11 实测：一整圈围墙不上屏，二分定位到的元凶就是这圈墙帽（`Wall_Cap`）；把它从 z=890 抬到 z=900，墙立刻回来 |
| **Python `bc.get_material(0)` returns NULL after `apply-default-material`** | Known quirk — UModelComponent's Python binding for `GetMaterial` differs from C++. Per-poly material is the authoritative source for BSP rendering; the BrushComponent slot is a fallback. | Verify via per-poly check (Python ability `whitebox_inspect_bounds*`); if per-poly non-NULL, trust the render. |
| **New shell command returns `Unknown command: whitebox` after live coding reload** | Live Coding recompiles the binary but does NOT re-register the ability info JSON. The cached ability info (in `LLMEasyShellSubsystem` / `LLMEasyShellLiteSubsystem`) keeps the old command list. | Run the command via Python ability wrapper (`python whitebox_apply_mat2`, `python whitebox_rebuild_bsp`, etc. in `Content/Features/Survivor/Scripts/`), OR full editor restart (`llm-shell --restart`). |
| **Editor becomes unresponsive after live coding** | Live Coding failed on an unrelated module's shader compile (e.g., PostProcessMaterial) — the editor's connection state may diverge from the shell | `llm-shell --restart` (saves → shutdown → UBT rebuild → restart) |
| **`error="A brush named 'X' already exists in this level (it may still be pending deletion)"`** | 名字被占了：要么同名 brush 还活着，要么上一支同名 brush 已 destroy 但还没被 GC（引擎的 `StaticFindObjectFast` 仍然能查到） | **换个 `--name`**，或先 `delete-brush --name=X --confirm=true`（delete 会立刻把 actor 改名成 `__deleted_X` 释放名字槽位） |
| **编辑器在 `delete-brush` 时 fatal：`Renaming an object (...) on top of an existing object (...) is not allowed`** | 回收名 `__deleted_<name>` 不幂等：第二次删同名 brush 时改名撞上第一次留下的垃圾名 | 已修（回收名加唯一后缀）。若在旧二进制上遇到，`llm-shell --restart` 拿新编译 |
| **`create-*` 重名把编辑器整个弄崩** | 引擎默认的 `FActorSpawnParameters::NameMode` **随版本变**: UE 5.8 默认 `Required_Fatal` → `LevelActor.cpp:586` 直接 `appError()`; UE 5.5 默认 `Requested` → 悄悄改名成 `Foo_2`（重名但不报错，agent 会以为建成功）。旧版预检只扫**活着的 actor**，漏掉"已 destroy 未 GC"的 pending-kill 对象 | 已修：预检用 `FindObject<UObject>(Level, ...)` 复刻引擎查找 + 显式 `NameMode = Required_ErrorAndReturnNull`（锁死行为，四个版本一致），重名一律**明确报错**而不是崩 |

---

<!-- canonical audit count: doc-audit.py --summary runtime; single source of truth (no paired-sync needed) -->
