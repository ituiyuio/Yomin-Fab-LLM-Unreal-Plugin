---
name: llmshell-info-poll-ready-impl-2026-06-20
description: "2026-06-20 llm-shell --restart info-poll ready signal 实施总结: setvbuf _IONBF + Step 6 重写 + 测试结果"
metadata: 
 node_type: memory
 type: project
 originSessionId: 8cad053b-e597-4d5b-b2d4-b85264ea80f9
---

# llm-shell `--restart` info-poll ready signal 实施总结 (2026-06-20)

**Why**:
原始 push-model Win32 Event 等待机制在 Bash pipe `| tail -50` 下用户感受"4.5 分钟卡死"。问题不是 CLI 卡住，是 stdio 全缓冲 + tail 不立即输出。本任务用"info-poll + push-model 兜底"替代长 wait，并修 _IOLBF CRT crash。

**核心改动** (commit ad073c9 + 285e1af):
1. `main()` 入口加 `setvbuf(stdout, NULL, _IONBF, 0)` 行缓冲
2. `ExecuteRestart()` Step 6 重写: info-poll 主循环 (5min, 2s tick) + push-model non-blocking fast-path check + 30s-interval stderr 进度
3. 成功路径 `EmitRestartResult` 后加 `fflush(stdout)` 兜底
4. **`_IOLBF` 在 MSVC 14.44 CRT 崩溃** (STATUS_STACK_BUFFER_OVERRUN 0xC0000409) → 改 `_IONBF` (无缓冲, syscall 每次)

**实测结果** (2026-06-20 21:00 测试):
- cold start + `--skip-build`: 5 分钟内 CLI exit (push-signal hit 后 info 通)
- cold start + full UBT build: 7-10 分钟 wall clock (Step 4 UBT ~3-5 min + Step 6 5 min cap)
- **5 分钟 cap 工作正常** (CLI 5 分钟内 emit timeout JSON)
- stderr 进度行 (`Still waiting for editor (Xs elapsed)...`) 在 tail 输出可见
- 用户之前感受的"卡死"实为 `| tail -50` 等 stdin EOF (CLI 已 exit, tail 仍 hold)

**已知 limitation** (未修):
- `tail -N` 在 stdin close 后**不立即**输出最后 N 行,要内部 buffer flush 才输出 (Windows pipe 行为)
- 解决: 让用户用 `--skip-build` (10s 完成) 或不用 `| tail`
- Workaround: `kill <tail-pid>` 后 bash 立即结束, 输出可见

**未改 LLMEasyShellSubsystem.cpp** (现有 TCP serve `info` 已够用)。

**commit 链**:
```
285e1af fix(llmshell): _IONBF instead of _IOLBF — _IOLBF crashes MSVC 14.44 CRT
ad073c9 fix(llmshell): info-poll main + push-model fast-path for --restart
```

**相关文件**:
- Spec: `docs/superpowers/specs/2026-06-20-llmshell-info-poll-ready-design.md`
- Plan: `docs/superpowers/plans/2026-06-20-llmshell-info-poll-ready.md`
- 修改: `.claude/skills/llm-easy-shell/llm-shell/main.cpp`
 - line 3768-3784: `main()` setvbuf _IONBF
 - line 3491-3587: Step 6 info-poll loop
 - line 3585: `fflush(stdout)` success path

**How to apply** (后续维护):
1. 改 Step 6 任何代码必须保持 push-model fast-path (instant wake) + info-poll ground truth
2. `setvbuf` 必须在 main() 第一行 (任何 printf 之前)
3. 不要回退到 `_IOLBF` (CRT crash)
4. 5 分钟 cap 改成 10 分钟前先排查 UBT build 是不是冷启动 (vs 增量)
