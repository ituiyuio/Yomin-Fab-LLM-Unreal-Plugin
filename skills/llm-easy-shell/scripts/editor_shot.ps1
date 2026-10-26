# Editor window screenshot via Win32 PrintWindow.
# Bypasses UE FViewport 0×0 limitation by grabbing the OS-level window pixels
# directly with GDI. Works regardless of editor state (Idle/PIE/Compiling/etc.)
# as long as the editor window is visible on the desktop.
#
# Usage (-ExecutionPolicy Bypass is REQUIRED: default machine policy is Restricted
# and blocks this script with a SecurityError before it runs a single line):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -OutPath C:/x.png
#   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/llm-easy-shell/scripts/editor_shot.ps1 -ProcessName UnrealEditor
# (.claude/skills/... = installed location; inside the distribution repo itself the
#  script lives at skills/llm-easy-shell/scripts/editor_shot.ps1)
#
# Exit codes: 0 ok | 2 process not found | 3 no visible window | 4 target window
# not visible / zero size | 5 PrintWindow failed | 6 -Pie: no PIE preview window.

param(
    # Empty default -> resolved below from $PSScriptRoot. Do NOT hardcode a repo
    # path here: this script previously defaulted to "D:/UnrealEngine/CODEO/..."
    # (one dev's layout), so on every other machine it died with
    # "PermissionDenied: D:\UnrealEngine\CODEO\Saved" instead of taking a shot.
    [string]$OutPath = "",
    [string]$ProcessName = "UnrealEditor",
    # HWND is a pointer-width handle on x64 Windows; use [long] (Int64) not [int]
    # so high-32-bit handles don't truncate to a different (potentially valid)
    # window of another process.
    [long]$Hwnd = 0,
    # Capture the PIE preview window instead of the editor main window.
    # Without this switch the script picks the largest window by area, which while
    # PIE is running is always the editor frame. That capture shows the editor
    # viewport WITHOUT the PIE UMG/CEF layers and is easily misread as
    # "PIE renders no UI". To verify what the player actually sees, use -Pie.
    # PREREQUISITE: a "NetMode:"-titled window only exists when PIE runs in a
    # SEPARATE window — llm-shell `play` does this; the editor toolbar Play
    # button embeds PIE in the main viewport and -Pie cannot see it.
    # Multi-client PIE: picks the largest NetMode: window (titles differ per
    # client, e.g. "[NetMode: Client 1]"); pass -Hwnd to target one exactly.
    [switch]$Pie
)

$ErrorActionPreference = "Stop"

# Resolve the default output path: walk up from this script to the directory
# holding *.uproject (the UE project root — works for any install depth);
# if no .uproject is found (e.g. user-scope ~/.claude/skills install), fall
# back to 4 levels up = the layout <proj>/<agent-dir>/skills/llm-easy-shell/scripts.
# If the resolved dir is not writable, fall back to %TEMP% rather than dying.
if ([string]::IsNullOrWhiteSpace($OutPath)) {
    $repoRoot = $PSScriptRoot
    while ($true) {
        if (Get-ChildItem -Path $repoRoot -Filter *.uproject -File -ErrorAction SilentlyContinue) { break }
        $parent = Split-Path -Parent $repoRoot
        if (-not $parent -or $parent -eq $repoRoot) {
            $repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
            break
        }
        $repoRoot = $parent
    }
    $OutPath = Join-Path $repoRoot "Saved/Screenshots/editor_win32.png"
    $shotDir = Split-Path -Parent $OutPath
    try { New-Item -ItemType Directory -Path $shotDir -Force | Out-Null }
    catch {
        $OutPath = Join-Path $env:TEMP "editor_win32.png"
        Write-Warning "default dir not writable ($shotDir) - falling back to $OutPath"
    }
}

Add-Type -AssemblyName System.Drawing
# Type 'Win' is process-wide; guard re-import so a second invocation in the
# same PowerShell runspace (test harness / before-after wrapper) doesn't crash
# with 'type already exists' under ErrorActionPreference=Stop.
if (-not ('Win' -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win {
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndAfter, int x, int y, int cx, int cy, uint flags);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
  [DllImport("user32.dll", CharSet=CharSet.Unicode, EntryPoint="GetWindowTextW", ExactSpelling=true)] public static extern int GetWindowTextW(IntPtr hWnd, System.Text.StringBuilder s, int n);
}
"@ -ReferencedAssemblies System.Drawing
}

# Auto-find editor hwnd — prefer LARGEST visible top-level window of the process.
# This avoids accidentally picking a smaller embedded PIE window when PIE is running.
if ($Hwnd -eq 0) {
    $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $proc) {
        # -ErrorAction Continue is REQUIRED before exit N: the script runs with
        # ErrorActionPreference=Stop, where a bare Write-Error terminates the
        # script with exit 1 and the documented exit code never fires.
        Write-Error "Process $ProcessName not found" -ErrorAction Continue
        exit 2
    }
    # Enumerate all visible top-level windows of the process, pick the LARGEST
    $script:winCandidates = @()
    $cb = [Win+EnumWindowsProc]{
        param($h, $l)
        $procId = 0
        [void][Win]::GetWindowThreadProcessId($h, [ref]$procId)
        if ($procId -eq $proc.Id -and [Win]::IsWindowVisible($h)) {
            $rect = New-Object Win+RECT
            [void][Win]::GetWindowRect($h, [ref]$rect)
            $w = $rect.Right - $rect.Left
            $hh = $rect.Bottom - $rect.Top
            if ($w -gt 100 -and $hh -gt 100) {
                $sb = New-Object System.Text.StringBuilder 512
                [void][Win]::GetWindowTextW($h, $sb, 512)
                $script:winCandidates += [pscustomobject]@{
                    Hwnd = $h
                    Width = $w
                    Height = $hh
                    Area = $w * $hh
                    Title = $sb.ToString()
                }
            }
        }
        return $true
    }
    [void][Win]::EnumWindows($cb, [IntPtr]::Zero)

    if ($script:winCandidates.Count -eq 0) {
        Write-Error "No visible window found for $ProcessName" -ErrorAction Continue
        exit 3
    }
    # PIE preview window carries "NetMode:" in its title. Localization note:
    # stock UE ships no translation of the PlayInEditor_WindowTitleFormat key,
    # so the literal survives any editor UI language; it exists ONLY when PIE
    # runs in a separate window (PlayLevel.cpp GeneratePIEViewportWindow).
    $pieWin = $script:winCandidates | Where-Object { $_.Title -match 'NetMode:' } |
              Sort-Object -Property Area -Descending | Select-Object -First 1
    if ($Pie) {
        if (-not $pieWin) {
            Write-Error "-Pie requested but no 'NetMode:' PIE preview window found. PIE must run in a SEPARATE window (llm-shell 'play' does this; the editor toolbar Play button embeds PIE in the main viewport and has no such window)" -ErrorAction Continue
            exit 6
        }
        $best = $pieWin
    } else {
        $best = $script:winCandidates | Sort-Object -Property Area -Descending | Select-Object -First 1
        # Loud warning: without this, an agent screenshots the editor window, sees no
        # HUD, and concludes "PIE renders no UI" — a false negative that is very hard
        # to spot afterwards because the image looks like a legitimate PIE capture.
        if ($pieWin -and $pieWin.Hwnd -ne $best.Hwnd) {
            Write-Warning "PIE preview window detected (hwnd=$($pieWin.Hwnd), $($pieWin.Width)x$($pieWin.Height)). Capturing the EDITOR window instead -- re-run with -Pie to capture what the player actually sees."
        }
    }
    # Preserve full 64-bit handle width; [IntPtr] ctor below accepts Int64 directly.
    $Hwnd = [long]$best.Hwnd
}

$hwnd = [IntPtr]$Hwnd
$visible = [Win]::IsWindowVisible($hwnd)
$iconic = [Win]::IsIconic($hwnd)
$r = New-Object Win+RECT
[Win]::GetWindowRect($hwnd, [ref]$r) | Out-Null
$W = $r.Right - $r.Left
$H = $r.Bottom - $r.Top

# If window is iconic (minimized), try to restore it. PrintWindow on minimized
# windows usually returns black.
if ($iconic) {
    [Win]::ShowWindow($hwnd, 9) | Out-Null  # SW_RESTORE
    Start-Sleep -Milliseconds 500
    [Win]::GetWindowRect($hwnd, [ref]$r) | Out-Null
    $W = $r.Right - $r.Left
    $H = $r.Bottom - $r.Top
    Write-Host "(restored from minimized state)"
}

if (-not $visible -or $W -le 0 -or $H -le 0) {
    Write-Error "Window not visible or has zero size (hwnd=$hwnd, visible=$visible, ${W}x${H})" -ErrorAction Continue
    exit 4
}

$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()

# PW_RENDERFULLCONTENT = 0x00000002 — needed for DWM-composited windows
$ok = [Win]::PrintWindow($hwnd, $hdc, 2)
$g.ReleaseHdc($hdc)
$g.Dispose()

if (-not $ok) {
    $bmp.Dispose()
    Write-Error "PrintWindow returned false" -ErrorAction Continue
    exit 5
}

# Ensure output dir exists
$dir = Split-Path -Parent $OutPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

$bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

$bytes = (Get-Item $OutPath).Length
Write-Host "hwnd=$hwnd  size=${W}x${H}  visible=$visible  iconic=$iconic"
Write-Host "saved: $OutPath  ($bytes bytes)"
exit 0
