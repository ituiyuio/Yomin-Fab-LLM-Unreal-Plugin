---
name: llmshelllite-exe-rename
description: "llm-easy-shell-lite skill 的 CLI 二进制从 llm-shell.exe 改名为 llmshelllite.exe；用户偏好用 skill 名前缀 + \"shelllite\" 而非短 \"lite\""
metadata: 
 node_type: memory
 type: project
 originSessionId: 86b7dbae-620d-4667-9e85-c26bc533aa49
---

2026-06-06 把 Lite CLI 二进制从 `llm-shell.exe` 改名为 `llmshelllite.exe`（旧目录同步在 2026-06-29 tool-fix-169 重命名为 `llmshelllite/`）。

**改动文件**：
- `llmshelllite/CMakeLists.txt` — project / add_executable / target_link_libraries / install 全改为 `llmshelllite` (tool-fix-169 2026-06-29 directory rename 同步)
- `llmshelllite/compile.ps1` — `/Fe:llmshelllite.exe`（同时修了 `$srcDir` 之前误指向 `llm-easy-shell` 应该是 `llm-easy-shell-lite` 的隐藏 bug，tool-fix-169 同步更新为 `llmshelllite` 路径）
- `llmshelllite/_compile.ps1` — outPath 改 `llmshelllite.exe`（同样修了 srcPath 的路径 bug，tool-fix-169 同步更新路径）
- `llmshelllite/main.cpp` — header 注释 / help banner / 60+ 处 `[llm-shell]` 日志标签 → `[llmshelllite]` / `--restart` 错误消息 / stdin 注释全部更新，tool-fix-169 同步更新 g_ShellDir 3 处路径 (L77/L212/L251)
- `experience/*.md` — 4 个文档里命令示例 `llm-shell.exe` → `llmshelllite.exe`，tool-fix-169 同步更新目录路径引用

**保留**：skill 名 `llm-easy-shell-lite`、mode 名 "Lite / read-only"、状态文件 `.llmshell_crash_state` / `.current_port`（运行时文件，binary 内部 g_CrashStatePath 仍指向新路径，plugin 端不变）

> [tool-fix-169 2026-06-29] 闭合 2026-06-06 binary rename 时有意保留的 '目录名 `llm-shell/`'（跟 binary name `llmshelllite.exe` mismatch）。本日 audit 9 files + 4 doc + 7 gitignore pattern 1:1 同步 `llm-shell/` → `llmshelllite/`，跟 binary name 完全对齐。'保留 → 闭环 完整 cleanup' 2-step pattern 跟 tool-fix-130~168 partial-fix 同期 pattern 1:1 平行。

**Why**：用户偏好"完整 skill 名前缀"作为 CLI 命名 — 当初问"改名 lite"我直接叫 `lite.exe`，用户立刻纠正为 `llmshelllite.exe`（更明确不会和 `llm-easy-shell` 冲突）。
**How to apply**：未来给 lite skill 或其他 skill 命名 CLI 时，**先和用户确认短名/全名** — 不要凭直觉省略前缀。Lite 后续调用方式：`llmshelllite.exe --help` / `llmshelllite.exe -c "info"` / `llmshelllite.exe --restart`。
