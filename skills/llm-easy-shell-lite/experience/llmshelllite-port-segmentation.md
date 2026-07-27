---
name: llmshelllite-port-segmentation
description: LLMEasyShell Lite 端口段从 15161 (与 full 重叠 15162-15251) 改为独占 15201-15250；full 保持 15151-15200
metadata: 
 node_type: memory
 type: project
 originSessionId: 86b7dbae-620d-4667-9e85-c26bc533aa49
---

2026-06-06 把 LLMEasyShell Lite 端口从"和 full 共享 15151+ 然后用 stale-file guard 防 15151"改为**严格独占端口段**。

**新分段（无重叠）**：
- **LLMEasyShell (full)**: 15151-15200 (50 端口) — 不变
- **LLMEasyShellLite**: 15201-15250 (50 端口) — 新

**改的文件**：
- `Plugins/LLMEasyShellLite/Source/.../LLMEasyShellLiteSubsystem.cpp` — Initialize() 里 LITE_PORT_BASE=15201 / LITE_PORT_MAX=15250; scan loop 限制在段内; 删了 "never claim 15151" stale-file guard; 加了"cached port 越界 → 落回 default"逻辑
- `Plugins/LLMEasyShellLite/Source/.../Public/LLMEasyShellLiteSubsystem.h` — CurrentPort 默认 15151 → 15201
- `Plugins/LLMEasyShellLite/Source/.../Public/LLMEasyShellLiteTcpServer.h` — Start() 默认 / ListenPort 默认 / 注释 15151 → 15201
- `Plugins/LLMEasyShellLite/Source/.../Private/ShellCommand_Info.cpp` — 兜底 ListenPort 15151 → 15201
- `.claude/skills/llm-easy-shell-lite/llmshelllite/main.cpp` — DEFAULT_PORT 15151→15201, 端口扫描 15151-15160 改为 15201-15250 (50 个), `AllocatePortForInstance()` MAX_PORT 65535→15250, 加 cached port 越界 clamp (tool-fix-169 2026-06-29 directory rename 同步路径)
- `SKILL.md` — "Lite 默认 TCP 端口 15151" 改为 "Lite 独占 15201-15250, full 15151-15200"
- `experience/01-builtin-commands.md` / `debugging.md` / `improvement-plan.md` — 端口示例从 15151-15160 改到 15201-15250

**生效时机**：Lite CLI 二进制已重编完（llmshelllite.exe 19:33）；Lite **插件** C++ 改动需要 rebuild UnrealEditor 后才生效（plugin 会自动 detect 老 .current_port 越界 → 落回 15201）。

**Why**：用户指出旧设计混乱 — full 扫 15151-15251、lite 扫 15162-15261，重叠 90 端口必然冲突；CLI 端口扫描只到 15160 又够不到 lite 的 15161+。分段后 0 重叠，0 协商，0 补丁。
**How to apply**：未来加新的 LLMEasyShell 子插件时按同样规则分段（如 LLMVFX / LLMQuixel 各自占 50 端口段），CLI 端各自扫自己段。
