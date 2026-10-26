# Editor Window Screenshot（Win32 PrintWindow 路径）

> **状态**：✅ 已实现（2026-06-14）
> **位置**：`.claude/skills/llm-easy-shell/scripts/editor_shot.ps1`（安装位；发行仓内为 `skills/llm-easy-shell/scripts/editor_shot.ps1`）
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
# ⭐ 抓 PIE 里玩家真正看到的画面（含 HUD / UMG / **CEF 壳面板**）—— 截图取证首选
# 前置: PIE 必须跑在**独立窗口**（llm-shell `play` 即是; 编辑器工具栏 Play 按钮把 PIE
# 嵌在主视口里, 没有 NetMode: 标题窗, -Pie 找不到目标, 以退出码 6 报错）
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -Pie

# 默认输出 Saved/Screenshots/editor_win32.png（抓编辑器主窗）
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1

# 自定义输出路径
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -OutPath D:/x.png

# 组合
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -Pie -OutPath D:/x.png
```

### `-Pie` 存在的理由（**别用 `-Pie` 缺失的截图去断言「PIE 不渲染 UI」**）

脚本按**面积**选窗。PIE 运行期编辑器主窗面积恒大于 PIE 预览窗，
所以**不带 `-Pie` 永远抓编辑器主窗** —— 那张图里**没有 PIE 的 UMG / CEF 图层**，
但它看起来完全合法，是一类**很难事后识破的假阴性**（2026-10-10 r2229 实测踩中：
据此误判「PIE 像素通道对战斗壳面板不可用」并立了票，下一轮试 `-Pie` 即取到真机证据）。

脚本检测到 PIE 窗而你没给 `-Pie` 时会发告警，**看到就照做**（前缀 `WARNING:` / `警告:`
随系统语言，认正文不认前缀）：

```
WARNING: PIE preview window detected (hwnd=..., 1000x567). Capturing the EDITOR
window instead -- re-run with -Pie to capture what the player actually sees.
```

`-Pie` 找不到 PIE 窗时以退出码 **6** 报错，报错信息会提示独立窗口前置条件。

> ⚠ 另一条路径 game-API 截图（`capture_active_viewport` / `python editor screenshot source=pie`）
> 的取舍见 [llm-screenshot.md 陷阱 0](llm-screenshot.md)：`show_ui=True` 的异步路径能拍
> PIE 3D + UMG HUD（文件晚一拍落盘），但 **CEF/WebBrowser 壳面板像素不可靠** ——
> 要 CEF 壳面板像素证据只能用本路径的 `-Pie`。
> 详见 SKILL.md「截图 — 三条路径选对」。

实际验证（2026-06-14）：
- Editor Idle: 1609×1103 PNG，1.6MB，完整 UE 编辑器（菜单/工具栏/视口/Outliner/状态栏）
- PIE 运行中: 1609×1103 PNG，红停止按钮 + Outliner 包含 PIE 动态生成的 `EnemyBase0-5`

## 完整参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `OutPath` | `<project>/Saved/Screenshots/editor_win32.png`（从 `$PSScriptRoot` 向上找 `*.uproject` 定位工程根；找不到回退 4 层上溯；不可写回退 `%TEMP%`） | 输出 PNG 路径 |
| `ProcessName` | `UnrealEditor` | 目标进程名 |
| `Hwnd` | `0` | 指定窗口句柄；0=auto-detect |
| `Pie` | （switch，默认关） | 抓 PIE 预览窗（标题含 `NetMode:`）；多客户端 PIE 取面积最大者，精确指定用 `-Hwnd`。找不到时退出码 6 |

## Auto-detect 策略

- 枚举 `UnrealEditor` 进程的所有可见 top-level 窗口（读窗口标题 `GetWindowTextW`）
- 过滤宽高都 > 100 的窗口
- **默认选面积最大的窗口** —— PIE 运行期那就是编辑器主窗（独立窗口 PIE 是独立 top-level 窗，但面积小于编辑器框）
- **给了 `-Pie` 则改选标题含 `NetMode:` 的窗口**（独立窗口 PIE 专属标记；多客户端取最大）
- 如果编辑器最小化 → 自动 `SW_RESTORE`（避免 PrintWindow 拿到黑屏）

## 退出码

> 脚本以 `$ErrorActionPreference=Stop` 运行 —— 报错点必须 `Write-Error ... -ErrorAction Continue`
> 再 `exit N`，否则一律以退出码 1 终止、下表永不触达（2026-10-26 勘误：本表曾整体死码）。

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 未捕获异常（含 Add-Type 失败）/ 表内路径失效时的兜底 |
| 2 | 进程未找到（`UnrealEditor` 不在跑） |
| 3 | 没找到可见窗口 |
| 4 | 目标窗口不可见或尺寸 ≤ 0 |
| 5 | PrintWindow 返回 false |
| 6 | `-Pie`：找不到 `NetMode:` PIE 预览窗（含独立窗口前置条件提示） |

## 输出格式

```
hwnd=3476832  size=1609x1103  visible=True  iconic=False
saved: D:/UnrealEngine/CODEO/Saved/Screenshots/editor_win32.png  (1587640 bytes)
```

（`saved:` 行是解析出的**绝对路径** —— 默认值不再硬编码，按机器/安装位解析。）

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
| 看 PIE 动态（HUD/动画/光照） | ✅（`-Pie` 抓独立 PIE 窗，含 UMG/CEF；嵌入模式 PIE 无独立窗） | ✅（PIE 视口准确） |
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

- 脚本: `.claude/skills/llm-easy-shell/scripts/editor_shot.ps1`
- 经验: `experience/05-screenshot.md` — UE 双路径截图经验
- 文档: `references/llm-screenshot.md` — UE 路径 PIE 截图 API
- Memory: `../experience/incidents/claude-see-editor-screenshots-2026-06-14.md` — 完整工作流

## Why / How to apply

**Why**: UE 在 headless 模式下 FViewport 0×0 不可截图，但 OS-level 窗口 visible +
桌面画着 → Win32 GDI PrintWindow 拷像素即可，跟 UE 状态完全无关。

**How to apply**:
- **看 editor 窗口**（含 UI/Outliner/视口）→ 路径 A: `powershell ... editor_shot.ps1`
- **看 PIE 3D 渲染** → 路径 B: `play` → `sleep 5` → `python editor screenshot` → `Read`
- Read 工具读 PNG 视觉显示
- 失败时按退出码排查
