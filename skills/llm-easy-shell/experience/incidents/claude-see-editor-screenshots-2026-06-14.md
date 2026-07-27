---
name: claude-see-editor-screenshots
description: Claude 视觉看 UE 编辑器/PIE 截图工作流 — 两条路: Win32 PrintWindow (editor 桌面窗口) + UE PIE viewport (3D 渲染)
metadata:
 node_type: memory
 type: reference
 originSessionId: 0fc62e5f-a680-4647-a670-9c345e868b47
---

# Claude 看 UE 编辑器 / PIE 截图（2026-06-14）

## 目标

让 Claude 视觉看到 UE 渲染画面，便于调试后处理、HD3D、cel-shading、
WebBrowser、UI 布局等"必须用眼睛看才知道对不对"的任务。

## 两条路径（已验证）

### 路径 A: Win32 PrintWindow — 截编辑器**应用窗口**（含 UI/视口/Outliner）

**适用场景**: 看 editor UI、outliner、details panel、菜单、工具栏、关卡视口内容
**绕开的问题**: UE FViewport::GetSizeXY() 在 headless 模式固定 0×0 的硬约束
**原理**: 编辑器窗口 visible=True 1607×1101 在桌面上画着，用 GDI 拷窗口像素

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .lrh/temp/editor_shot.ps1
# 或自定义路径
powershell -NoProfile -ExecutionPolicy Bypass -File .lrh/temp/editor_shot.ps1 -OutPath D:/x.png
```

**实测**: 1609×1103 PNG，1.6MB，完整 UE 编辑器（菜单/工具栏/视口/Outliner/状态栏）
**优点**:
- 跟 UE 状态完全无关（Idle/PIE/Compiling 都行）
- 不需要 PIE
- 看到的是用户实际看到的编辑器界面
**缺点**:
- 需要桌面会话（headless server 看不到桌面的无效）
- 截到的是 OS 级窗口，可能含 DWM 合成偏差
- 最小化窗口会自动 SW_RESTORE（避免黑屏）
- PrintWindow 在某些 DWM 合成窗口上偶尔失败

### 路径 B: UE PIE viewport — 截 3D 渲染

**适用场景**: 看 PIE 中的 3D 场景、动态光照、动画、HUD、WebBrowser、UMG

```bash
LLM_SHELL=./.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe
SHOT=D:/UnrealEngine/CODEO/Saved/Screenshots

# 1. 启动 PIE
$LLM_SHELL -q -j -c "play"

# 2. 等视口初始化
sleep 5 # 简单场景; 含 CEF/WebBrowser 8-10s

# 3. 截图
$LLM_SHELL -q -j -c "python editor screenshot path=$SHOT/x.png async=false source=pie"

# 4. Read 工具视觉读回
Read("D:/UnrealEngine/CODEO/Saved/Screenshots/x.png")
```

**实测**: 1521×933 PNG，3D 场景清晰，HD-3D cel-shading 效果可见

## 关键约束与陷阱

### 1. UE FViewport 0×0 硬约束

在 headless 模式下，`FViewport::GetSizeXY()` 固定 0×0（`UEditorEngine` 的
D3D swap chain window `UnrealWindow` 一直 invisible/0×0）：

- `python editor screenshot source=editor async=false` 报：
 `"Viewport has zero size (Editor, 0x0)"`
- `async=true` 报：请求接受但**永远不写盘**（engine tick 阻塞）
- `SetForegroundWindow` / `ShowWindow(SW_SHOW)` 救不回来（Slate widget layout 不会重排）

**走路径 A 解决（Win32 PrintWindow 不经 UE）**。

### 2. PreparingPatch 死锁

`editorState: PreparingPatch` 来自 `ShellCommand_Info.cpp:128-211` 三路判断：
- `LiveCoding.bIsDoingHotReloadPatch` CVar
- log device 关键词 ("Patch"/"Preparing"/"Shell")
- `ILiveCodingModule::IsCompiling()`

**症状**: 所有命令 block，async 截图不写盘
**修复**: `./llm-shell.exe --restart --skip-build` (~30s 恢复)

### 3. sync vs async

- **sync**（`async=false`）: 精确路径，3D only，确定性高
- **async**（`async=true`）: 引擎下一帧写盘，自动加 5 位数字后缀
 - 含 UI/HUD/WebBrowser 必须 `async=true show_ui=true`
 - 路径 B 优先 sync；路径 A 不需要这个（直接 GDI 拷）

### 4. PIE viewport 初始化延迟

- `play` 后立即截图 → 0×0 视口
- 简单场景: `sleep 5`
- CEF/WebBrowser: `sleep 8-10`
- 复杂关卡: `sleep 10+`

## 路径 A 脚本 — `.lrh/temp/editor_shot.ps1`

```powershell
# Auto-detect UnrealEditor process, find main visible window, PrintWindow to PNG
param(
 [string]$OutPath = "D:/UnrealEngine/CODEO/Saved/Screenshots/editor_win32.png",
 [string]$ProcessName = "UnrealEditor",
 [int]$Hwnd = 0 # 0 = auto-detect
)
# ... uses GetWindowRect, PrintWindow(PW_RENDERFULLCONTENT=2), System.Drawing.Bitmap
```

**特性**:
- Auto-detect UnrealEditor hwnd（兼容不同 PID）
- Minimize 自动 SW_RESTORE
- PW_RENDERFULLCONTENT flag for DWM composited windows
- Exit code: 0 成功 / 2 进程未找到 / 3 窗口未找到 / 4 不可见 / 5 PrintWindow 失败

## 一次性准备清单

| 工具 | 路径 | 状态 |
|------|------|------|
| `llm-shell.exe` | `.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe` | ✅ |
| `python editor screenshot` | `Plugins/LLMEasyShell/PyAbilities/.../editor.py` | ✅ |
| `python editor set_realtime` | 同上 | ✅ (2026-06-14 加，对 0×0 无效) |
| Win32 editor_shot.ps1 | `.lrh/temp/editor_shot.ps1` | ✅ (2026-06-14 加) |
| Read PNG 视觉 | Claude Read tool | ✅ |

## 相关文档

- `.claude/skills/llm-easy-shell/references/llm-screenshot.md` — PIE 截图完整 API
- `.claude/skills/llm-easy-shell/experience/05-screenshot.md` — 双路径/陷阱经验
- `Plugins/LLMEasyShell/Source/.../Private/ShellCommand_Info.cpp:128-211` —
 PreparingPatch 状态推断代码
- memory `ue5-webbrowser-pie-no-render.md` — UWebBrowser CEF 初始化延迟
- memory `ue-webbrowser-pause-timer-deadlock.md` — WebBrowser 暂停死锁
- memory `ue-editor-state.md` — 编辑器状态与阻塞场景

## Why / How to apply

**Why**: 图像/后处理/HUD/UI/Outliner 等任务纯 log 调不出来，必须视觉确认。
UE 编辑器在 Windows headless 模式下 FViewport 0×0，但 OS-level 窗口 visible +
桌面画着 → 用 Win32 GDI PrintWindow 拷像素即可，绕开 UE。

**How to apply**:
- **看 editor 窗口（含 UI/Outliner/视口内容）** → 路径 A: `powershell ... editor_shot.ps1`
- **看 PIE 3D 渲染（HUD/动画/光照）** → 路径 B: `play` → `sleep 5` → `screenshot` → `Read`
- 死锁时 `--restart --skip-build`
- **别再走 `source=editor async=true`** — 在 stuck 状态下永远不写盘
