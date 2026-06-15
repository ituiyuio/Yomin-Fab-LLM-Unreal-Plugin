# Editor window screenshot via Win32 PrintWindow.
# Bypasses UE FViewport 0×0 limitation by grabbing the OS-level window pixels
# directly with GDI. Works regardless of editor state (Idle/PIE/Compiling/etc.)
# as long as the editor window is visible on the desktop.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .lrh/temp/editor_shot.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File .lrh/temp/editor_shot.ps1 -OutPath D:/x.png
#   powershell -NoProfile -ExecutionPolicy Bypass -File .lrh/temp/editor_shot.ps1 -ProcessName UnrealEditor

param(
    [string]$OutPath = "D:/UnrealEngine/CODEO/Saved/Screenshots/editor_win32.png",
    [string]$ProcessName = "UnrealEditor",
    # HWND is a pointer-width handle on x64 Windows; use [long] (Int64) not [int]
    # so high-32-bit handles don't truncate to a different (potentially valid)
    # window of another process.
    [long]$Hwnd = 0
)

$ErrorActionPreference = "Stop"
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
}
"@ -ReferencedAssemblies System.Drawing
}

# Auto-find editor hwnd — prefer LARGEST visible top-level window of the process.
# This avoids accidentally picking a smaller embedded PIE window when PIE is running.
if ($Hwnd -eq 0) {
    $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $proc) {
        Write-Error "Process $ProcessName not found"
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
                $script:winCandidates += [pscustomobject]@{
                    Hwnd = $h
                    Width = $w
                    Height = $hh
                    Area = $w * $hh
                }
            }
        }
        return $true
    }
    [void][Win]::EnumWindows($cb, [IntPtr]::Zero)

    if ($script:winCandidates.Count -eq 0) {
        Write-Error "No visible window found for $ProcessName"
        exit 3
    }
    $best = $script:winCandidates | Sort-Object -Property Area -Descending | Select-Object -First 1
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
    Write-Error "Window not visible or has zero size (hwnd=$hwnd, visible=$visible, ${W}x${H})"
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
    Write-Error "PrintWindow returned false"
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
