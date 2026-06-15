# Editor Window Screenshot（Win32 PrintWindow 路径）

> **状态**：✅ 已实现（2026-06-14）
> **位置**：`scripts/editor_shot.ps1`
> **后端**：Win32 GDI（`PrintWindow` + `System.Drawing`）
> **场景**：截**编辑器应用窗口**（含菜单/工具栏/视口/Outliner/状态栏）

## 为什么需要这个

UE 自带的 `python editor screenshot source=editor` 在 headless 模式下永远 0×0
（详见 [experience/05-screenshot.md](../experience/05-screenshot.md) 教训 5）：
- 编辑器的 D3D swap chain 窗口（`UnrealWindow` 类）一直 invisible
- `FViewport::GetSizeXY()` 反映这个 0×0
- `SetForegroundWindow` / `ShowWindow` 都救不回来

**Win32 PrintWindow 绕开 UE 全部 API**，直接 GDI 拷贝**编辑器应用窗口**的桌面像素。
跟 UE 状态完全无关（Idle / PIE / Compiling 都能截）。

## 快速开始

```bash
# 默认输出 Saved/Screenshots/editor_win32.png
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/editor_shot.ps1

# 自定义输出路径
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/editor_shot.ps1 -OutPath D:/x.png
```

实际验证（2026-06-14）：
- Editor Idle: 1609×1103 PNG，1.6MB，完整 UE 编辑器（菜单/工具栏/视口/Outliner/状态栏）
- PIE 运行中: 1609×1103 PNG，红停止按钮 + Outliner 包含 PIE 动态生成的 `EnemyBase0-5`

## 完整参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `OutPath` | `D:/UnrealEngine/CODEO/Saved/Screenshots/editor_win32.png` | 输出 PNG 路径 |
| `ProcessName` | `UnrealEditor` | 目标进程名 |
| `Hwnd` | `0` | 指定窗口句柄；0=auto-detect |

## Auto-detect 策略

- 枚举 `UnrealEditor` 进程的所有可见 top-level 窗口
- 过滤宽高都 > 100 的窗口
- **选面积最大的窗口**（避免 PIE 嵌入小窗口抢选 — PIE 嵌入窗口约 1020×660，editor 主窗口 1609×1103）
- 如果编辑器最小化 → 自动 `SW_RESTORE`（避免 PrintWindow 拿到黑屏）

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 2 | 进程未找到（`UnrealEditor` 不在跑） |
| 3 | 没找到可见窗口 |
| 4 | 窗口不可见或尺寸 ≤ 0 |
| 5 | PrintWindow 返回 false |

## 输出格式

```
hwnd=3476832  size=1609x1103  visible=True  iconic=False
saved: D:/UnrealEngine/CODEO/Saved/Screenshots/editor_win32.png  (1587640 bytes)
```

## 关键技术点

### PW_RENDERFULLCONTENT (0x00000002)

DWM 合成窗口（DWM-composited）用普通 BitBlt / PrintWindow 拿不到内容（拿到黑屏）。
`PW_RENDERFULLCONTENT` 告诉 DWM 把合成后的内容渲染到位图，是必须的 flag。

### 不依赖 FViewport / Slate

PrintWindow 拿到的是 OS-level 窗口的最终像素，包括：
- 标题栏、菜单栏
- 工具栏按钮
- Slate widgets（包括 Outliner / Details Panel / 主视口）
- 状态栏

### 限制

- **需要桌面会话**（headless server 没有 DWM/合成时，PrintWindow 拿黑屏）
- 不在主显示器上可能被截到部分内容
- 多显示器/不同 DPI 时，截到的是窗口自身的坐标系，不是物理像素

## 对比 PIE 截图（路径 B）

| 维度 | Win32 PrintWindow（路径 A） | UE PIE screenshot（路径 B） |
|------|--------------------------|---------------------------|
| 看 editor UI（菜单/Outliner） | ✅ | ❌（PIE 视口没有 editor UI） |
| 看 3D 场景内容 | ✅（视口是 editor 视口） | ✅（PIE 视口，可能与 editor 不同） |
| 看 PIE 动态（HUD/动画/光照） | ⚠️ 只能看到 PIE 嵌入窗 | ✅（PIE 视口准确） |
| 跟 UE 状态耦合 | ❌ 完全无关 | ⚠️ 需要 PIE 运行 + 等 5s |
| 失败模式 | 进程未跑 / 桌面不可见 | FViewport 0×0 / PreparingPatch 死锁 |
| 速度 | ~500ms | ~500ms（不含 sleep） |

**推荐组合**：
- 看 editor 状态（关卡内容、actor 列表、UI 布局）→ **路径 A**
- 看 PIE 实时（HUD、动态效果）→ **路径 B**
- 不知道选哪个 → 路径 A（永远能跑）

## 调试技巧

### 看 editor 进程的所有窗口

```bash
powershell -NoProfile -Command "
Get-Process -Name 'UnrealEditor' | ForEach-Object {
    Write-Host \"PID=\$(\$_.Id) MainWindowHandle=\$(\$_.MainWindowHandle)\"
}"
```

### PrintWindow 失败排查

- 桌面会话断开（headless server 无 DWM）→ 拿到黑屏 → 用 RDP/VNC 登入
- 窗口 minimize → 自动 SW_RESTORE，应能恢复
- 权限不够 → PowerShell 进程权限低 → 用 admin 跑

## 相关文件

- 脚本: `scripts/editor_shot.ps1`
- 经验: `experience/05-screenshot.md` — UE 双路径截图经验
- 文档: `references/llm-screenshot.md` — UE 路径 PIE 截图 API
- Memory: `claude-see-editor-screenshots-2026-06-14.md` — 完整工作流

## Why / How to apply

**Why**: UE 在 headless 模式下 FViewport 0×0 不可截图，但 OS-level 窗口 visible +
桌面画着 → Win32 GDI PrintWindow 拷像素即可，跟 UE 状态完全无关。

**How to apply**:
- **看 editor 窗口**（含 UI/Outliner/视口）→ 路径 A: `powershell ... editor_shot.ps1`
- **看 PIE 3D 渲染** → 路径 B: `play` → `sleep 5` → `python editor screenshot` → `Read`
- Read 工具读 PNG 视觉显示
- 失败时按退出码排查
