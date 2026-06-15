# PIE 截图（Viewport Capture）完整指南

> **状态**：✅ 已实现（2026-06-01）
> **位置**：`python editor screenshot [args...]`
> **后端**：`ULLMEasyShellEditorLib::CaptureActiveViewport` (C++)

## 快速开始

```bash
# PIE 中截 PIE 视口（默认行为：auto source）
python editor screenshot

# 指定路径（不指定时用 Saved/Screenshots/Auto_<timestamp>.png）
python editor screenshot path=D:/shot.png

# 强制 PIE 视口（PIE 没运行则失败）
python editor screenshot source=pie

# 强制编辑器视口（headless 模式下 0×0 失败）
python editor screenshot source=editor

# 自定义尺寸（基于视口最近邻缩放）
python editor screenshot width=1280 height=720
```

## 完整参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `path` | `Saved/Screenshots/Auto_<timestamp>.png` | 输出 PNG 路径 |
| `width` | 视口宽度 | 缩放目标宽度（0=不缩放） |
| `height` | 视口高度 | 缩放目标高度（0=不缩放） |
| `source` | `auto` | `pie` / `editor` / `auto` |
| `async` | `false` | `true` 走 `FScreenshotRequest` 异步引擎路径 |
| `show_ui` | `false` | async 模式下是否包含 Slate UI |
| `base64` | `false` | （预留）base64 内嵌返回 |

返回值（同步，输出文本多行，机器可读字段在 data 字典）：

```
Screenshot saved
  Mode:     sync (FViewport::ReadPixels → SaveImageByExtension)
  Captures: 3D scene only (Slate widgets NOT included — UMG/HUD/WebBrowser invisible)
  Source:   PIE
  Path:     D:/UnrealEngine/CODEO/Saved/Screenshots/Auto_20260601.png
  Size:     853x482
  Tip:      pass async=true show_ui=true to also capture Slate UI
```

```json
{
  "success": true,
  "output": "<上方的多行文本>",
  "data": {
    "file_path": "D:/.../Auto_20260601.png",
    "width": 853,
    "height": 482,
    "source": "PIE",
    "mode": "sync",
    "scope": "3d-only",
    "show_ui": false
  }
}
```

返回值（异步请求已接受）：

```
Screenshot request accepted
  Mode:     async (FScreenshotRequest, engine writes on next frame)
  Captures: 3D scene + Slate UI (UMG widgets, WebBrowser, HUD)
  Source:   PIE
  Base path: D:/UnrealEngine/CODEO/Saved/Screenshots/Auto_20260601.png
  Note:     engine appends numeric suffix; actual file is the newest .png in the same directory
  Size:     853x482
```

**关键字段语义**：

- `Mode`：用的是哪条 C++ 路径（sync 立即读 / async 引擎下一帧写）
- `Captures`：截的内容范围，**3D-only** 还是 **3d+ui**。这是最容易踩的坑：sync 模式固定 3D only，HTML/UMG/HUD widget 一律截不到
- `Source`：PIE 视口还是 Editor 视口
- `Path / Base path`：sync 是写到的精确文件；async 是 base 路径，引擎会加数字后缀
- `scope` 字段：机器可读版（`3d-only` / `3d+ui`），脚本可以依赖它

## 双路径实现

### 路径 A：同步（默认）— `FViewport::ReadPixels` + `FImageUtils::SaveImageByExtension`

```cpp
// 1. 解析视口
FString Source, Detail;
FViewport* VP = LLEELInternal::ResolveCaptureViewport(bUsePIE, Source, Detail);

// 2. 同步读取像素（必须在游戏线程）
FIntPoint ViewportSize = VP->GetSizeXY();
TArray<FColor> Pixels;
VP->ReadPixels(Pixels, FReadSurfaceDataFlags(RCM_UNorm, CubeFace_MAX), FIntRect(0, 0, ViewportSize.X, ViewportSize.Y));

// 3. 缩放（最近邻）
if (Width != ViewportSize.X || Height != ViewportSize.Y) { ... }

// 4. 保存为 PNG
FImageView View(Pixels.GetData(), Width, Height);
FImageUtils::SaveImageByExtension(*FilePath, View);
```

**优点**：瞬时完成，不依赖下一帧渲染。
**缺点**：必须在视口有数据时调用（PIE 暂停时仍可，headless 时 0×0 失败）。

### 路径 B：异步 — `FScreenshotRequest::RequestScreenshot`

```cpp
FScreenshotRequest::RequestScreenshot(FilePath, bShowUI, bAddSuffix, bHdr);
```

**优点**：捕获引擎下一帧的完整渲染结果（含 PIE 动态光照/动画）。
**缺点**：文件由引擎写，文件名会自动追加后缀（如 `Auto_xxx0000.png`）。

## 视口选择策略

PIE 模式下，有 **两个** viewport 候选：
- `GEditor->PlayWorld->GetGameViewport()->Viewport` — PIE 视口（推荐）
- `GEditor->GetLevelViewportClients()[0]->Viewport` — Editor 视口

`ResolveCaptureViewport(bUsePIE, ...)` 实现：

| bUsePIE | GEditor->PlayWorld | 行为 |
|---------|---------------------|------|
| `-1` (auto) | 存在 | 返回 PIE 视口 |
| `-1` (auto) | null | 返回 Editor 视口 |
| `1` (force) | 存在 | 返回 PIE 视口 |
| `1` (force) | null | 返回 nullptr（错误） |
| `0` (force) | any | 返回 Editor 视口 |

## 已知陷阱

### 1. Editor 视口在 headless 模式下是 0×0

UE 编辑器如果是 headless（无人值守、窗口最小化），Editor 视口 `GetSizeXY()` 返回 `(0, 0)`。这是预期的 — 此时只能用 PIE 视口或根本不能截图。

**诊断**：`python editor viewport` 实时查看视口尺寸。

### 2. UE Python 字段名转换（**最容易踩坑**）

USTRUCT 的 `BlueprintReadOnly` UPROPERTY 暴露给 Python 时，**自动 snake_case + 去 b 前缀**：

| C++ UPROPERTY | Python 访问名 |
|---------------|---------------|
| `bool bSuccess` | `result.success` |
| `FString FilePath` | `result.file_path` |
| `int32 Width` | `result.width` |
| `FString Source` | `result.source` |
| `FString Error` | `result.error` |
| `FString Base64` | `result.base64` |

**Why**: UE Python 端遵循 PEP 8 命名约定，对 BlueprintReadOnly UPROPERTY 进行转换。

**How to apply**:
- 永远不要用 `result.bSuccess`、`result.FilePath` — 会返回 `None`
- 安全的写法：`getattr(result, 'bSuccess', getattr(result, 'success', default))` 兼容两种风格
- LLMEasyShell 自带的 `_bool_val(st, 'bIsPIE', False)` 用 `getattr`+`getattr` 的 fallback 写法，值得参考

### 3. 修改公共头 USTRUCT 触发 LiveCoding 完全重编译

**现象**：编辑 `LLMEasyShellEditorLib.h`（public header）增加 USTRUCT 字段（`Source`、`Base64`）后：
- `livecoding` 显示 `0 errors, 0 warnings` 但 `result: Failed`
- UBT 日志显示触发所有引擎模块的完整重新编译

**Why**: USTRUCT 字段变化导致反射元数据（`.gen.cpp`）重生成，Live Coding 的二进制 ABI 补丁无法应用。

**How to apply**:
- 修改 public USTRUCT 后，**必须 `restart`**（完整重启编辑器）
- 纯函数体修改 + 私有字段 → 可以 `livecoding`
- 加 UFUNCTION/UPROPERTY → 通常可以 `livecoding`
- 加 USTRUCT 字段/UENUM → 触发 `restart`

### 4. Python 模块缓存不会自动清除

修改 `editor.py` 后，C++ DLL 已经 Live Coding 更新，**但 Python `import` 的模块是缓存的**。

**必须调用**：`python reload`（特殊命令）来重扫描 abilities/ 目录 + 清 sys.modules 缓存。

**How to apply**:
- 任何 Python ability 修改后，先 `python reload`，再调用命令
- `reload` shell 命令只触发 Live Coding，**不**重载 Python 模块

### 5. PIE viewport 在 PIE 启动后才有尺寸

PIE 启动后需要等 1-2 帧才能拿到 viewport。如果立即截图会得到 0×0 视口。

**How to apply**:
- `play` 后 `sleep 5-10` 再截图（取决于场景复杂度）
- 用 `python editor viewport` 检查尺寸

### 6. async 路径的文件名追加后缀

`FScreenshotRequest::RequestScreenshot(FilePath, ..., bAddSuffix=true, ...)` 引擎会自动在文件名后追加数字（`Auto_20260601_15011600000.png`），**不**是用户传的精确路径。

**How to apply**:
- async 模式只告诉用户"已请求"，实际文件名需要 `dir Saved/Screenshots/` 找最新
- 同步模式按用户传的精确路径写入

## UE5.7 截图 API 速查

| API | 用途 | 头文件 |
|-----|------|--------|
| `FViewport::ReadPixels(...)` | 同步读取当前视口像素 | `UnrealClient.h` |
| `FScreenshotRequest::RequestScreenshot(...)` | 异步请求截图 | `UnrealClient.h` |
| `FScreenshotRequest::OnScreenshotCaptured()` | 一次性回调 | `UnrealClient.h` |
| `FImageUtils::SaveImageByExtension(...)` | 存为 PNG/EXR/JPG | `ImageUtils.h` |
| `GetHighResScreenshotConfig().SetResolution(...)` | 高分辨率截图配置 | `HighResScreenshot.h` |
| `FSlateApplication::Get().TakeScreenshot(...)` | 整个应用窗口（含 UI） | `Framework/Application/SlateApplication.h` |

## 调试技巧

### 加 UE_LOG 验证 C++ 是否被调用

```cpp
UE_LOG(LogTemp, Log, TEXT("[LLMEasyShell] CaptureActiveViewport: path=%s, bUsePIE=%d, PlayWorld=%p"),
    *OutFilePath, bUsePIE, GEditor ? GEditor->PlayWorld.Get() : nullptr);
```

### Python 端诊断 struct 字段

```python
all_attrs = [a for a in dir(result) if not a.startswith('_')]
err = str(getattr(result, 'Error', getattr(result, 'error', '')) or '')
err_msg = err if err else f"Unknown error. Result type: {type(result).__name__}, attrs: {all_attrs}"
```

### 强制 Python 重新加载

```bash
python reload     # 重新扫描 abilities/ + 清 sys.modules 缓存
```

## 相关文件

- C++ 实现：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellEditorLib.cpp`
- C++ 接口：`Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellEditorLib.h`
- Python 包装：`Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/editor.py`
- Python 注册：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/PythonAbilityRegistry.cpp`
