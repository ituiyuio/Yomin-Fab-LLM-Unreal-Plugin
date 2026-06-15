# LLMEasyShell 截图经验

> 双路径机制 / CEF 初始化延迟 / 新输出格式（2026-06-01）

---

## 教训 1：双路径差异巨大 —— sync 截 3D，async+ui 截整窗口

| 模式 | C++ 调用栈 | 捕获内容 |
|------|-----------|----------|
| **sync（默认）** | `FViewport::ReadPixels → FImageUtils::SaveImageByExtension` | **仅 3D scene render target** |
| **async + show_ui=true** | `FScreenshotRequest::RequestScreenshot` → `FSlateApplication::TakeScreenshot(WindowRef, ...)` | **整个 Slate 窗口**（含 WebBrowser / UMG / HUD） |

**关键事实**：

- sync 路径**不传 bShowUI**（`LLMEasyShellEditorLib.cpp:419` vs `:449`）
- 所以 `python editor screenshot show_ui=true` 但默认 sync 时 `show_ui` 参数**不生效**
- 必须 `async=true show_ui=true` 同时设置
- 引擎代码 `GameViewportClient.cpp:2272-2300` 根据 `bShowUI` 决定走 `FSlateApplication::TakeScreenshot`（含 widget）还是 `InViewport->ReadPixels`（仅 3D）

**How to apply**：

```bash
# 截 3D 场景（默认 sync 即可）
python editor screenshot source=pie

# 截 HUD/UI（必须 async + show_ui 同步）
python editor screenshot source=pie async=true show_ui=true

# ❌ 无效组合
python editor screenshot show_ui=true   # sync 模式忽略
```

---

## 教训 2：async 模式文件名自动加数字后缀

引擎 `FScreenshotRequest::RequestScreenshot(FilePath, bShowUI, bAddSuffix=true, bHdr)` 会加后缀：

```bash
# 期望
python editor screenshot path=D:/shot.png async=true

# 实际写盘
D:/shot00000.png   # ← 5 个 0 后缀，引擎自动加
```

**auto timestamp 形式**：`Saved/Screenshots/Auto_20260601_18302800000.png`（5 个 0 也是引擎加的）。

**How to apply**：

- async 模式报告的 `path` 只是 base，告诉消费者去 `Saved/Screenshots/` 找最新 `.png`
- 或 `dir Saved/Screenshots` 找 `*00000.png` 形式

---

## 教训 3：CEF / WebBrowser 初始化需要 3-4s

`UWebBrowser` 首次初始化延迟 3-4s：
- 1.5s / 2.5s 时截图还是白屏
- 4.5s 才有 HTML 内容

**早截图永远得到**：
- 白屏（CEF 还在 init）
- 错误页（HTML 路径错误）
- 纯 widget 但无 HTML 内容

**How to apply**：

- `play` 后 `sleep 5` 再截图
- WebBrowser widget 自己会设 3.5s 后显示，6s 后 force-show
- async+show_ui 看到 Slate 标题栏但 HUD 区域全白 → CEF 渲染失败，检查 HTML 路径 / CEF 初始化

---

## 教训 4：2026-06-01 新输出格式（多行，机器可读）

旧的单行格式 `Screenshot saved [sync, PIE]: path (WxH)` 太简略，没标**截的内容范围**。

### 新 sync 成功输出

```
Screenshot saved
  Mode:     sync (FViewport::ReadPixels → SaveImageByExtension)
  Captures: 3D scene only (Slate widgets NOT included — UMG/HUD/WebBrowser invisible)
  Source:   PIE
  Path:     D:/UnrealEngine/CODEO/Saved/Screenshots/Auto_20260601.png
  Size:     853x482
  Tip:      pass async=true show_ui=true to also capture Slate UI
```

### 新 async 接受输出

```
Screenshot request accepted
  Mode:     async (FScreenshotRequest, engine writes on next frame)
  Captures: 3D scene + Slate UI (UMG widgets, WebBrowser, HUD)
  Source:   PIE
  Base path: D:/UnrealEngine/CODEO/Saved/Screenshots/Auto_20260601.png
  Note:     engine appends numeric suffix; actual file is the newest .png in the same directory
  Size:     853x482
```

### 关键字段语义

| 字段 | 含义 |
|------|------|
| `Mode` | 哪条 C++ 路径（sync 即时读 / async 引擎下一帧写） |
| `Captures` | **3D-only** vs **3d+ui** —— 截图能不能含 widget |
| `Source` | PIE 视口 vs Editor 视口 |
| `Path / Base path` | sync 是写到的精确文件；async 是 base 路径 |
| `data.scope` | 机器可读版（`3d-only` / `3d+ui`），脚本可依赖 |

**判定规则**：

- `success + mode=sync` → 永远 3D only（不管 show_ui）
- `success + mode=async + show_ui=true` → 3d+ui
- `success + mode=async + show_ui=false` → 3d only

---

## 教训 5：Editor 视口在 headless / 最小化时是 0×0

UE 编辑器如果是 headless（无人值守、窗口最小化），Editor 视口 `GetSizeXY()` 返回 `(0, 0)`。此时只能用 PIE 视口或根本不能截图。

**诊断**：`python editor viewport` 实时查看视口尺寸。

**How to apply**：

- 截图前用 `info` 看 PIE 状态
- 强制 PIE 视口：`source=pie`
- 强制 Editor 视口：`source=editor`（headless 下失败）
- **想要看 editor 窗口本身（含 Outliner / Details Panel / 工具栏）**：
  **用 Win32 PrintWindow 路径** [references/editor-shot-win32.md](../references/editor-shot-win32.md)，
  绕开 UE FViewport 0×0 硬约束

---

## 截图相关失败模式

| 症状 | 原因 | 解决 |
|------|------|------|
| 全白/全黑无内容 | sync 模式 + Widget | 改 `async=true show_ui=true` |
| "Failed to load URL" 错误页 | HTML 路径 / URL 编码错 | 查 `webui-cef-file-url-encoding-bug` |
| HUD 之间区域纯白 | UWebBrowser `bSupportsTransparency` 没开 | C++ 用 FProperty 反射写 |
| 0×0 视口错误 | headless / 最小化 | 走 PIE 视口或用 [Win32 路径](../references/editor-shot-win32.md) |
| 文件名带 5 个 0 | async 模式引擎加后缀 | 看 `Saved/Screenshots/` 最新 |
| bIsAsync 字段读不到 | `_candidates` 漏 snake_case | 见 `02-python-abilities.md` 教训 4 |
| Win32 PrintWindow 截到黑屏 | 缺 `PW_RENDERFULLCONTENT` | 见 [07-editor-shot-win32.md 教训 4](07-editor-shot-win32.md) |
