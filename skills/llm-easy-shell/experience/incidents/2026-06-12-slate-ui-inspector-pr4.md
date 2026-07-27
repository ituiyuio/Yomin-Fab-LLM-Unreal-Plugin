---
name: 2026-06-12-slate-ui-inspector-pr4
description: "LLMEasyShell ui shot --widget PR4 落地 (DrawWidget via FWidgetRenderer, 2 commits on top of PR3), 5.7 GetGeometry→GetCachedGeometry deprecation 发现"
metadata:
 node_type: memory
 type: project
 originSessionId: 7b661671-8cab-45c8-a837-84138c692c7e
---

# 落地

PR4 扩展 `ui shot` 从 MVP 整 VP 截图 → 支持 `--path <UWidget-path>` 单 widget 截图, 通过 FUIInteractor::DrawWidget + FWidgetRenderer。Task 4.1。

# Why
- PR1+PR2+PR3 给了 dump/find/info/shot(MVP) + press/type/tick = 6 命令族
- 缺 "视觉证据" 拿单 widget 视觉验证 (对比 VP 整图)

# How to apply
- **`FWidgetRenderer` 用法** (5.7 verified): `FWidgetRenderer R(false, true); UTextureRenderTarget2D* RT = FWidgetRenderer::CreateTargetFor({Wd, Ht}, TF_Bilinear, false); R.DrawWidget(RT, SW, {Wd, Ht}, 0.0f);`
- **PNG 编码**: `IImageWrapperModule` + `EImageFormat::PNG` + `ERGBFormat::BGRA` (8bpp)
- **Width/Height=0 sentinel**: 用 widget 几何尺寸 fallback
- **5.7 重要 deprecation**: `SWidget::GetGeometry()` 已删, 5.7+ 用 `GetCachedGeometry()`. PR4 build 时发现 4 处 PR3 pre-existing call sites 也需要 fix, 已全部替换

# Known limitations (PR4 末)
- `ui shot --path` 工作但 PIE runtime 没真跑过 (env 阻塞, user 需关 editor + 跑 PIE 后才能验证 PNG 输出)
- 完整 Build.bat link 仍被 `UIInspector.cpp:12 WebBrowser.h` pre-existing 阻塞 (PR1.5 引入, 与 PR4 无关)

# Verification (PR4 done)
- 26 commits on master (PR1 15 + PR2 7 + PR3 2 + PR4 2)
- 7 shell 命令全部 wired + registered
- 5.7 GetGeometry deprecation 已修, PR3+PR4 在 5.7 编译通过
- L0 test 编译 + linked
- 3 regression scripts 准备就绪
- spec §13 DoD 6/7 met, 1 (PIE runtime) deferred
