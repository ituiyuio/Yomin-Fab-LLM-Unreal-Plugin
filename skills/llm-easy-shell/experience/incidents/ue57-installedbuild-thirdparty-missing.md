---
name: ue57-installedbuild-thirdparty-missing
description: "UE5.7 InstalledBuild 缺 third-party 库文件 (AHEasing-1.3.2/Skia/int128_no_intrinsic.inc) — .tps 描述符保留但实际 .h/.lib 物理缺失;关键: plugin-only build 走得通,只 Live Coding 全 editor relink 失败"
metadata: 
 node_type: memory
 type: project
 originSessionId: 8bc27ad3-8bf2-4feb-84a6-20dc0bf53549
---

# UE5.7 InstalledBuild third-party 物理缺失 + Build 走通路径 (2026-06-12)

## 根因 (纠正之前的误归因)

`llmeasyshell-lite-phase6-fixes-2026-06-01.md` 记 "路径重命名后 livecoding 触发全量编译失败（engine 三方库 includes 缺失，与 Lite 无关）" — 实际根因是 **Engine 是 InstalledBuild (binary install)**,第三方库文件 **从未安装**,跟 Lite phase 6 rename 无关 (只是时间巧合)。

## 物理证据 (2026-06-12 调查)

UE_5.7 `C:\Program Files\Epic Games\UE_5.7\Engine\Source\ThirdParty\` 下 30+ 目录只含 `.tps` 描述符 (1 file / dir),实际 .h/.lib/.inc 物理缺失:

| ThirdParty dir | .tps 有 | 真文件 (AHEasing-1.3.2 / skia-simplify.* / int128_no_intrinsic.inc 等) |
|---|---|---|
| `AHEasing/` | ✅ AHEasing.tps (544B) | ❌ `AHEasing-1.3.2/` 子目录整体缺失 |
| `skia/` | ✅ skia.tps (875B) | ❌ 0 个 skia-simplify.* |
| `abseil/20240722.0/` | ✅ abseil.tps (797B) | ⚠️ 有 450 个 .h,**但** 缺 `absl/numeric/int128_no_intrinsic.inc` |
| 其他 ~27 dir (ANGLE/AVXMathFun/Detours/DiaSdk/Distorm/FakeIt/FontConfig/GPUReshape/LivePlusPlus/OneSky/OpenAL/OpenAPV/RawPDB/Re2/SentryNative/Tencent/WiX/WinHttp/cares/flatbuffers/fmt/http_parser/libxml2/llvm/lmdb/msdfgen) | ✅ .tps | ❌ 0 真文件 |

UE_5.3/5.4/5.5/5.6/5.7.4 **同样状态** — 全部 InstalledBuild。

`Engine/Build/InstalledBuild.txt` 标志 = binary install (内容 "UE_5.7")。

## ⚠️ 关键: Plugin build **能走通**, Live coding **不能**

**全量 Build (Build.bat CODEOEditor Win64 Development ... -NoHotReload)** 走 UBT incremental compile,**只重新编译 8 commits 改动的 plugin .cpp + 直接 link 进现有 .dll**,不触发 engine modules 重新编译,5 min 内完成。Plugin .dll mtime 从 Jun 9-11 → Jun 11 23:18,新代码入 binary。

**Live coding (Ctrl+Alt+F11)** 想 relink 整个 editor 二进制,触发 engine modules (Slate/RigVM/SVGDistanceField/MetaHumanSDKEditor) 重编译,这些模块的源码 #include AHEasing/skia/abseil → **编译 fail**,Live coding 永远 stuck 5/3 起。

`llm-shell --restart` 内部用 Build.bat 走 plugin-only 路径,不是 Live coding,所以能成功。

## 触发 Live coding 失败的真实编译错 (UBT Log.txt 末次 5/3 17:54)

```
Module.Slate.1.cpp → fatal: AHEasing/easing.h
Module.SlateCore.2.cpp → fatal: ThirdParty/skia/skia-simplify.h
Module.SVGDistanceField → fatal: ThirdParty/skia/skia-simplify.cpp
Module.RigVM.3.cpp → fatal: AHEasing/easing.h
Module.MetaHumanSDKEditor → fatal: absl/numeric/int128_no_intrinsic.inc
Result: Failed (OtherCompilationError)
```

## 修复 third-party 路径 (3 选 1, 未在本次做)

1. **Epic Games Launcher → Library → UE 5.7 → ⋯ → Verify** (自动重下 third-party)
2. **Run GenerateProjectFiles** (`Engine/Build/BatchFiles/GenerateProjectFiles.bat`) 触发 TpsStub 下载
3. **全 reinstall UE 5.7** (重下 ~30GB)

## ⚠️ 另一个 pre-existing issue: Engine SM6 shader 验证收紧

post-process material SM6 compile 撞 `PostProcessMaterialShaders.dxil:5403: error: Instructions must be of an allowed type. note: at 'unreachable'`。影响 TiltShift/Bloom/PostQuantizeTemporal/FilmGrain 等所有 post-process。根因 = 引擎 prebuilt .dxil 跟当前 DXC/driver 不兼容,**跟 third-party 缺失同根**(都是 InstalledBuild 缺基础组件),但不是同一个文件,third-party 修复不一定能解 SM6 issue。

## 工具/sanity check 模式

诊断时用:
```bash
# 1. Engine 是否 InstalledBuild
ls "C:/Program Files/Epic Games/UE_5.7/Engine/Build/InstalledBuild.txt"

# 2. 找缺失 third-party (.tps-only dirs)
for d in "C:/Program Files/Epic Games/UE_5.7/Engine/Source/ThirdParty/"*/; do
 count=$(find "$d" -type f 2>/dev/null | wc -l)
 [ $count -le 1 ] && echo "MISSING: $d (only $count files)"
done

# 3. Plugin .dll mtime vs commit time — 验证 C++ 改动是否在 running binary
git log --pretty=format:"%ad %s" --date=iso HEAD~8..HEAD
ls -la Plugins/LLMMaterial/Binaries/Win64/UnrealEditor-LLMMaterial.dll

# 4. UBT log 末次 mtime — 看 last build 何时
ls -la "C:/Program Files/Epic Games/UE_5.7/Engine/Programs/UnrealBuildTool/Log.txt"
```

## Why
本次 8 commits chain 验证卡住多周, 用户误以为是 Lite phase 6 path rename 副作用, 实际是 InstalledBuild 标准状态。LLMEasyShell 自身代码零第三方依赖 (HD3D Build.cs 只依赖 Core/Engine/RHI/Renderer/Geometry*; LLMMaterial Build.cs 只依赖 Core/Engine),所以 plugin-only build 走得通。

## How to apply
- 任何 8 commits 后做 PIE 验证,如果看到 shader compile fail 但 C++ 解析 OK,先查 plugin .dll mtime 是否在 commit 之后
- 任何 "Live coding 失败" 报告,先 grep 5 个第三方文件名 (AHEasing/skia-simplify/int128_no_intrinsic.inc/absl) 在 UBT log
- 改 HD3D/LLMMaterial plugin Build.cs 时,**不要**加 AHEasing/skia/abseil 引用 — 必踩 InstalledBuild 缺文件雷
- 重 Build 优先用 `llm-shell --restart` (走 Build.bat 路径, plugin-only),不要触发 Live coding

Related: [[llmeasyshell-lite-phase6-fixes-2026-06-01]] (Lite phase 6 fixes 总结, 此 memory 是其根因补充) [[hd3d-sm6-shader-regression-2026-06-10]] (pre-existing SM6 验证 issue, third-party 修复不一定解) [[hd3d-v6-chain-final-state-2026-06-10]] (v6 chain '全修' 实际未验证)
