---
name: llmeshell-restart-misses-booting-editor-then-burns-a-link
description: "--restart 把启动期活编辑器判成 not running，拿被占 DLL 照常 Link，20 分钟后报出与真编译错误同形的失败；修 = Link 前 CreateFileA 写锁探测"
metadata:
  node_type: memory
  type: feedback
---

# --restart 把「正在启动的编辑器」判成没在跑 ⇒ 照常用被占的 DLL 去 Link（2026-09-29，r1920）

> **路径口径（2026-10-26 发行仓注）**：本文引用的 `tools/compile/*`、`docs/survivor/*`、`.lrh/*`、`tmp/*`、`llm-shell/compile.ps1` 等路径属**源开发仓**，本发行仓不含这些文件；判据/复现请以文中可直接运行的 shell / python 单行为准。


## 症状

`llm-shell --restart --port 15157` 打成：

```
[llm-shell] Editor not running. Skipping save/shutdown steps.
[llm-shell] Step 4: Building project with UnrealBuildTool...
```

而**同一时刻**本项目编辑器 PID 活着、`netstat` 显示 `127.0.0.1:15157 LISTENING`。
Compile 一路 `[1/33]…[24/33]` 全过，20 分钟后才在 Link 撞锁；报出来的形状与真编译错误同形，
第一轮据此得出的结论是「本机编译被阻塞」—— 又是「健康的构建被误杀 / 误判」那一类（见
`llm-shell-w26-restart-fixes.md` Bug 2、r1005/r996 的看门狗账）。

## 根因

两半，缺一不可：

1. **识别面**：`RequestEditorClose()` 靠「exe 名 + 进程命令行里有本 .uproject」认项目，
   命令行读不到时退到 `EnumWindows` 找顶层窗口。启动期（Nanite 网格 / DDC 构建阶段）
   这两样**都不齐** ⇒ 扫描返回空集 ⇒ 上层直接宣布「Editor not running」并跳过关闭步骤。
2. **动作面**：跳过关闭之后没有任何东西回答「那这枚目标 DLL 现在能写吗」，UBT 照跑。
   加载中的镜像把文件挡的是**写**，识别失败只是没人去问。

## 修复（`llm-shell/main.cpp`）

Step 4 之前加 `EnsureTargetModuleNotHeld()`：以 `CreateFileA(GENERIC_WRITE, share=0)`
试开 `Binaries/Win64/UnrealEditor-<项目名>.dll`，测到占用就逐一点名 `UnrealEditor*` 进程并**不构建**
（`{"success":false,"stage":"build",…}` + exit 1）。函数就地返回，绝不开一条注定失败的 Link。

## 探测面怎么选（本机实测，别再猜第二次）

对着**正加载该 DLL 的编辑器**量三种组合：

| 请求的访问权 | share | 结果 |
|---|---|---|
| `DELETE` | 0 | **成功拿到句柄** ← 挡的是写，不是删；用它探测 = 闸门恒放行 |
| `GENERIC_WRITE` | 0 | 失败 `err=32 ERROR_SHARING_VIOLATION` ← 定稿用这个 |
| `READ\|WRITE\|DELETE` | 0 | 失败 `err=32` |

两次弯路都记在函数注释里：第一版按 `GetTargetName()` 拼出 `UnrealEditor-CODEOEditor.dll`
（盘上不存在——模块名 = **项目名** `CODEO`）⇒ 走「文件不存在 = 首次构建」豁免分支恒放行，
连跑两次都在编辑器活着时照常开建，才看出闸门装了等于没装。

## 判据 / 复现

- 复现「识别不出活编辑器」：`llm-shell --restart --port <一个不存在的端口>`（跳过项目匹配、按端口关不到东西），
  同时让一个本项目编辑器活着（启动期最省事）。
- 期望（修后）：`ERROR: cannot link, target module is held by another process` + `PID=…` 点名
  + `stage:"build"` + **exit=1，且 `Build.bat` 一次都没被启动**。
  实测读数：09-29 00:4x，点名 `PID=740` / `PID=10368`，未启动构建。
- 状态自检（不经 llm-shell）：

```bash
python -c "import ctypes;k=ctypes.windll.kernel32;k.CreateFileW.restype=ctypes.c_void_p;\
print(k.CreateFileW(r'<项目绝对路径>\\Binaries\\Win64\\UnrealEditor-<项目名>.dll',0x40000000,0,None,3,0,None),ctypes.GetLastError())"
# err 32 ⇒ 写锁被占（此时 --restart 应当拒建；拒建不是故障）
```

## 代价面（别把机器状态读成工具故障）

那两个被点名的 PID 正是 `--restart` 自己启动后被冻住的编辑器：内存数分钟不变，
`taskkill /F` 报「没有这样的权限」，`Stop-Process -Force` 返回「killed」而进程仍在，
WM_CLOSE 无处可发（还没建窗口）。它们退出之前本机建不了该项目 —— 这是闸门存在的理由，
不是闸门的缺陷。下一席读到「llm-shell 拒绝构建」先跑上面那条自检：`err 32` 就是同一状态，
处置是等/清僵死进程，而不是去改 llm-shell 或 Build.bat 参数。

## 同族读法纪律

`--restart` 后面接任何管道（`| tail`、后台任务的「exit code 0」通知）拿到的都不是 llm-shell 的退出码
—— `--help` 早写了。判 `--restart` 只认 JSON 的 `success` / `stage` / `exitCode` 三字段。
本轮在此误判过一次「它说成功了」。
