---
name: ue57-livecoding-vs-cpp-vs-shader
description: "UE 5.7 LiveCoding 报\"失败\"未必是 C++ 错！可能是 (1) pre-existing shader 编译失败 (HD3D TiltShift 等) (2) Engine ThirdParty 头文件缺失 (MiMalloc/SSEMathFun/Skia/VHACD/oodle2base)。先 --restart 让 C++ 编译过，再用 PIE 实跑验证代码逻辑，不被 livecoding 报告阻塞。"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 946b702b-0b2d-46c6-aa01-9786de7d908a
---

# UE 5.7 LiveCoding 报告失败的判别

**重要**: LiveCoding 的 `result: Failed` ≠ 代码错误。它监控整个编译链路（C++ + shader + link），任何一个 fail 都报失败。

## 真实根因 (2026-06-12 实测)

### 1. Pre-existing Shader 编译失败
```
D3DCompileToDxil failed. Error code: 未指定的错误 (0x80004005).
BasePassPixelShader.dxil:4906:1: error: Instructions must be of an allowed type.
note: at 'unreachable' in block '#0' of function 'MainPS'.
```
- 来源: `/Game/HD3D/M_HD3D_TiltShift.M_HD3D_TiltShift` 在 PCD3D_SM6 平台
- 与 C++ 代码无关，材质 pre-existing
- 已用 `Default Material` fallback，不影响游戏运行

### 2. Engine ThirdParty 头文件缺失
```
MiMalloc.c(24,1): fatal error C1083: 无法打开包括文件: "static.c"
Module.Core.8.cpp: ThirdParty/SSEMathFun/sse_mathfun_extension.h
Module.TextureFormatOodle: oodle2base.h
Module.SVGDistanceField: ThirdParty/skia/skia-simplify.cpp
```
- 触发条件: `livecoding` 触发全量 relink（任何 .h 改动都触发）
- 根因: UE 5.7 InstalledBuild 缺 third-party 库
- 关联: `ue57-installedbuild-thirdparty-missing.md`

## 判别流程

1. **看 CODEO.log**：找 `[LogLinker] [ERROR]` 或 `[LogClass] [ERROR]`（C++ 错误）
 - **有** → 真的是 C++ 编译失败，要修代码
 - **无** → LiveCoding 失败是 shader / ThirdParty，**与代码无关**
2. **看 LiveCodingCapture.log 末尾**：shader 错误会显式说 `Shader FDistortionMeshPS / TBasePassPSFNoLightMapPolicy`
3. **看 ubtDiagnostics**：找 `fatal error C1083: 无法打开包括文件` 列表

## 正确动作

- **C++ 编译过 + LiveCoding 报失败**：
 - **不要**重试 livecoding（会再次触发全量 relink 同样失败）
 - 用 `--restart` 替代（已验证 Build.bat 走得通，UE editor 启动走完整 Build Tool 路径不会用 UBA relink）
 - 或直接跑 PIE（dll 实际是好的，PIE 能跑就证明 C++ 编译过了）
- **PIE 跑通新代码** → 代码 100% 正确，可放心 commit
- **Pre-existing shader / ThirdParty 问题** → 不在本次 commit 范围，单独 task 修

## Why

- 工具监控整个链路 ≠ 工具能区分错误类型
- 用户偏好"质疑工具"，不被表面错误信号阻塞
- 实际项目节奏：代码改 → 启动 PIE 看效果 → 没问题就 commit
- 修 pre-existing build 问题（Shader/ThirdParty）是另一个工作量级，独立评估
