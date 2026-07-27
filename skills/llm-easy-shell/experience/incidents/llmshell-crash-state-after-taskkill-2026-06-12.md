---
name: llmshell-crash-state-after-taskkill-2026-06-12
description: "手动 taskkill UnrealEditor.exe 后 LLMEasyShell 缓存 crash 标志,导致后续 play 命令返回 crashed:true — 解决=用 llm-shell --restart 替代 taskkill"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 67d12361-0643-4190-ad5b-fd0124907bc5
---

**症状**:
- 手动 `taskkill /F /IM UnrealEditor.exe` 后,LLMEasyShell 缓存的 "editor has crashed" 标志不清空
- 后续 `llm-shell -c "play"` 返回 `crashed:true`,即使新 editor 进程已经成功启动
- Crash log 显示是历史 PID(如 59832)的 PlayLevel.cpp:546 断言残留

**Why**:
- LLMEasyShell 在 C++ 端维护 `g_LastEditorPid` + crash detection state
- 手动 taskkill 没有经过 LLMEasyShell 的 `WaitForExit` graceful shutdown path
- editor 死时如果有未清理的 PIE stage,PlayLevel.cpp:546 触发 "GameInstance still referenced" 断言,LLMEasyShell 收到 crash 报告 → 永久设 `crashed=true`
- 后续任何 `info`/`play` 等命令都先检查 crash 标志,直到有重启成功的 signal

**正确流程**:
1. **永远用 `llm-shell --restart` 替代手动 taskkill**
2. `--restart` 内部:`save → shutdown → Build.bat → 启动新 editor → WaitForEditorResult 检测 port 15251 connect`
3. 启动成功后自动清 crash 标志
4. 完成后再 `play`/`info` 正常工作

**What NOT to do**:
- ❌ `taskkill /F /IM UnrealEditor.exe` 然后期望 `play` 立刻 work
- ❌ `taskkill` 后直接 `play`(crashed:true 拦死)
- ❌ `taskkill` 后用 `start ... UnrealEditor.exe` 启新 editor(LLMEasyShell 不知道)
- ❌ 删 Saved/Crashes/* 文件以为能清标志(LLMEasyShell 在内存维护)

**Why `--restart` work 而手动 taskkill 不 work**:
- `--restart` 走 `EmRestartResult` 单 JSON 契约
- 用 `CreateEvent` 等待 editor 启动 + port connect + 状态 healthy
- 成功才 emit success JSON,清 crash 标志

**遇到 crashed:true 但 editor 实际活着的诊断**:
```bash
# 1. 看 editor 进程
tasklist 2>&1 | grep -i UnrealEditor

# 2. 看 LLMEasyShell 进程(端口 15151)
"D:/UnrealEngine/CODEO/.claude/skills/llm-easy-shell/llm-shell/llm-shell.exe" -c "info"
# 如果返回 crashed:true 但有 livecoding 字段 = editor 活着但 LLMEasyShell 缓存了旧 crash

# 3. 修复:llm-shell --restart (清状态 + 启)
```

相关:
- [[llm-shell-w26-restart-fixes]] — W26.1-4 多轮 restart 修复
- [[llm-shell-push-model-ready-signal-2026-06-05]] — push-model ready event 架构
- [[llm-shell-w27-tick-resetevent-fix]] — W27 race 修复
