---
name: ue57-svgdistancefield-skia-missing-2026-06-15
description: 2026-06-15 UE5.7 InstalledBuild engine Editor/SVGDistanceField 缺 ThirdParty/skia/skia-simplify.cpp → livecoding fatal
metadata: 
 node_type: memory
 type: reference
 originSessionId: 8fc2b885-86b5-47bb-8216-3b30724af5a6
---

# UE 5.7 SVGDistanceField/Skia ThirdParty 缺失阻塞 LiveCoding

## 症状
任何 LiveCoding 触发 → `Compile [x64] Module.SVGDistanceField.cpp: fatal error C1083: 无法打开包括文件: "ThirdParty/skia/skia-simplify.cpp"` → fatal,整个 LiveCoding patch 失败,即便我们自己 module (CODEO / 任何 plugin) 改动也不会被 patch 进运行进程。

## 文件位置
- 失败模块: `C:\Program Files\Epic Games\UE_5.7\Engine\Source\Editor\SVGDistanceField\` (always-built editor module)
- 缺的文件: `C:\Program Files\Epic Games\UE_5.7\Engine\Source\ThirdParty\skia\skia-simplify.cpp`
- 现存: 只有 `ThirdParty/skia/skia.tps` (许可证),源码全删
- 引用位置: `SvgDistanceFieldGenerate.cpp:19`

## 根因
跟 [[ue57-installedbuild-thirdparty-missing]] 一致 — InstalledBuild 引擎缺 third-party 源文件 (AHEasing/Skia/int128 等)。Plugin Build.bat 走得通(因为不需要重 link engine),只 Live Coding 全 relink 失败。

## 影响
- ✅ Editor 启动正常(engine .obj 是 prebuilt)
- ✅ 单 plugin manual build OK
- ✅ Game runtime 正常
- ❌ **LiveCoding 完全不可用**: 任何 cpp 改动无法 hot-patch
- ❌ `llm-shell --restart` 走 UBT rebuild 同样失败(LLMPCG.uplugin JSON fix 后第二次 restart 验证)

## 已知 workaround
1. **改 BP/Python ability 而非 cpp**: 大多数 game balance / 数据配置 用 BP CDO + python ability(参考 [[survivor-ranged-0kill-rca-2026-06-15]] 的 force_weapon_melee.py)
2. **临时禁用 LiveCoding 然后只 build CODEO module**: `livecoding --disable` 然后 manually run `Engine/Build/BatchFiles/Build.bat CODEOEditor Win64 Development -SingleFile=...` (未验证)
3. **修 engine source**: 删 SvgDistanceFieldGenerate.cpp 的 `#include "ThirdParty/skia/skia-simplify.cpp"` + stub 实现(影响其它项目,需重装引擎恢复)
4. **重装 UE 5.7** (耗时但根治)

## 何时遇到
- 首次必看: livecoding 失败时 `log --filter` 看 Module.SVGDistanceField 是不是阻塞模块
- 这不是项目代码 bug,是 engine 工程环境问题
- 不要为此回退自己的代码改动 — 临时改 BP/Python 绕过即可

## 决策树
```
cpp 改动需要生效?
├── 是 → 必须修 SVGDistanceField 或重装 UE → 数小时
└── 否 → 走 BP CDO 修改 + Python ability → 分钟级
```

相关: [[ue57-installedbuild-thirdparty-missing]] [[llmvfx-build-broken-pre-existing-2026-06-03]]
