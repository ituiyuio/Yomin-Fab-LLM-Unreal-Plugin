# LLMEasyShell Editor 窗口截图（Win32 路径）

> Win32 PrintWindow 截编辑器应用窗口（2026-06-14 沉淀）

---

## 教训 1：UE FViewport 0×0 是 headless 模式硬约束 — 但 Win32 救场

**场景**：在 Windows headless 模式（无人值守 / 隐藏 DWM 窗口）下跑 UE 编辑器，
调用 `python editor screenshot source=editor`（sync 或 async）都拿不到 editor 视口截图。

**根因**：
- UE 编辑器启动时创建**两个 UnrealWindow**：
  - 主 UI chrome（1607×1101，visible=True）
  - **D3D swap chain 窗口**（`UnrealWindow` 类，**invisible**）
- `FViewport::GetSizeXY()` 反映 D3D swap chain 窗口的尺寸 → 0×0
- `SetForegroundWindow` / `ShowWindow(SW_SHOW)` / `RedrawWindow` 救不回来
  - Slate SViewport widget layout 不会因为外部 SetWindowPos 重排
  - Windows 10+ foreground 抢占限制
- 引擎 `async=true` 路径能接受请求但永远不写盘（因为 engine tick 阻塞 / 无 frame 触发）

**修复模式**：
**绕开 UE 全部 API，用 Win32 GDI PrintWindow 拷桌面像素**：

```powershell
# scripts/editor_shot.ps1
[Win]::PrintWindow($hwnd, $hdc, 2)  # PW_RENDERFULLCONTENT
```

**优点**：
- 跟 UE 状态完全无关（Idle / PIE / Compiling 都行）
- 不需要 PIE
- 截到的是用户实际看到的 editor 窗口（含 Outliner / Details Panel / 工具栏）
- 速度 ~500ms

**经验**：
- **看 editor UI/视口内容** → Win32 路径，永远能跑
- **看 PIE 3D 渲染（HUD/动画）** → UE PIE 路径
- **别再走 `source=editor`** — 在 headless 下永远失败

---

## 教训 2：PIE 状态会让 auto-detect 选错窗口

**场景**：PIE 运行时调 `editor_shot.ps1`，期望截完整 editor 窗口，结果截到 PIE 嵌入小窗（1020×660）。

**根因**：
- 启 PIE 后，UE 会把 PIE 窗口设为"最前"（foreground）
- `Get-Process MainWindowHandle` 返回的是最前窗口
- PIE 嵌入窗口 < editor 主窗口（1609×1103）

**修复模式**：
**枚举所有可见 top-level 窗口，选面积最大的那个**：

```powershell
$candidates = @()
$cb = {
    param($h, $l)
    $procId = 0
    [Win]::GetWindowThreadProcessId($h, [ref]$procId)
    if ($procId -eq $proc.Id -and [Win]::IsWindowVisible($h)) {
        $rect = New-Object Win+RECT
        [Win]::GetWindowRect($h, [ref]$rect)
        $area = ($rect.Right - $rect.Left) * ($rect.Bottom - $rect.Top)
        if ($area -gt 10000) {  # 过滤掉 < 100x100 的小窗口
            $script:candidates += [pscustomobject]@{ Hwnd = $h; Area = $area }
        }
    }
    return $true
}
[Win]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
$best = $candidates | Sort-Object -Property Area -Descending | Select-Object -First 1
```

**经验**：
- 截图前先枚举窗口，不要相信 `MainWindowHandle`
- 永远按面积排序选最大窗口（最可能是主应用窗口）

---

## 教训 3：PowerShell `$pid` 是 reserved 变量

**场景**：PowerShell 脚本里写 `$pid = 0; [Win]::GetWindowThreadProcessId($h, [ref]$pid)`，
结果 `$pid` 是 PowerShell 内部进程 ID，赋值失败。

**根因**：`$pid` 是 PowerShell 保留的自动变量（指向当前 PowerShell 进程 ID），不可写。

**修复模式**：
**用 `$procId` / `$processId` / `$ownerPid` 等非 reserved 名称**。

```powershell
# ❌ 错
$pid = 0
[Win]::GetWindowThreadProcessId($h, [ref]$pid)

# ✅ 对
$procId = 0
[Win]::GetWindowThreadProcessId($h, [ref]$procId)
```

其他常见 PowerShell reserved 变量：`$?` `$^` `$_` `$args` `$input` `$host` `$null` `$true` `$false`。

**经验**：PowerShell 写 P/Invoke 时，所有 `out` 参数的本地变量名都要避开 reserved 字。

---

## 教训 4：PW_RENDERFULLCONTENT 是 DWM 合成窗口必须的 flag

**场景**：用普通 `PrintWindow(hwnd, hdc, 0)` 截 UE 编辑器窗口，拿到的是黑屏。

**根因**：
- Windows 10+ 的窗口大多走 DWM（Desktop Window Manager）合成
- 普通 PrintWindow 拿不到合成后内容（只拿窗口的 GDI surface，合成内容是另一回事）
- 拿到的是窗口的"占位符"内容 = 黑屏

**修复模式**：
**`PrintWindow(hwnd, hdc, PW_RENDERFULLCONTENT)`**（flags = 0x00000002）：

```powershell
# ✅ 对：DWM 合成窗口也能拿到内容
$ok = [Win]::PrintWindow($hwnd, $hdcBmp, 2)
```

**经验**：所有 Win32 GDI 截屏 / PrintWindow 现代应用，**必须**加 `PW_RENDERFULLCONTENT`（0x2）flag，否则黑屏。
