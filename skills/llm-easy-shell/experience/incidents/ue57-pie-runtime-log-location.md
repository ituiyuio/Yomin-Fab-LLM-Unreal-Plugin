---
name: ue57-pie-runtime-log-location
description: UE 5.7 PIE 运行时日志(自定义 UE_LOG)写入 Saved/Logs/CODEO.log 而非 llm-shell 的 log 命令 buffer;查 PIE 自定义日志必须 grep Saved/Logs/CODEO.log
metadata: 
 node_type: memory
 type: reference
 originSessionId: b5f9aa97-d6ab-4f4f-a2f9-cd5896d1e1c0
---

UE 5.7 PIE 运行时 `UE_LOG(LogTemp, Log, ...)` 写入项目日志文件,llm-shell `log` 命令只输出 editor 启动期日志 + LLMShell 自己的命令处理日志。

**Why**: editor log buffer 滚动窗口只有 ~7000 行,PIE 跑 30s 后自定义日志会被推出视野,LLM 看 `log --filter EliteAffix` 找不到任何匹配。

**How to apply**:
- PIE 跑完查自定义日志 → 直接 grep 文件: `grep "your_tag" Saved/Logs/CODEO.log`
- editor log 只用于查 engine 内部日志(PythonAbilityRegistry/livecoding/compile)
- 验证自己写的 UE_LOG 必须等 PIE 跑出事件后 grep Saved/Logs/CODEO.log

**坑**: llm-shell 的 `log --filter X` 适合查已知会进 editor log 的引擎事件,不查自定义 game log。

参考 [[survivor-elite-affix-design-2026-06-19]]