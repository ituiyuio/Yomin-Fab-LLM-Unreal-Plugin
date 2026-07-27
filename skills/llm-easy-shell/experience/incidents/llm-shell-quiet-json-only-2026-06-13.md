---
name: llm-shell-quiet-json-only-2026-06-13
description: "2026-06-13 llm-shell 加 -q (quiet stderr) 和 -j (json-only inner) 旗标,大幅减少 LLM 上下文噪声"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: b60e322f-e48a-4ead-bbd7-1508bf141e5d
---

# llm-shell Quiet/JSON-Only 模式 (2026-06-13)

## 痛点
LLM 使用 llm-shell 时输出 70% 是噪声:
1. **stderr 噪声**:`[llm-shell] Engine path found...`, `Trying port...`,
 `Found instance...`, `[preflight] Unknown command...`, `[preflight] Warning...`
2. **stdout 嵌套 JSON**:`{"success":true,"output":"<stringified JSON>"}` — LLM
 还得再 parse 一次 output 字符串才能用

## 修复
- **`-q` / `--quiet`**:早解析 argv(在 DetectProjectPaths 前),把 stderr 重定向到
 `llm-shell-quiet.log`,LLM 看不到
- **`-j` / `--json-only`**:解析 server 响应,只取 `"output"`(或 `"result"`)字段,做 JSON
 反转义(`\n \t \" \\ \uXXXX`)后原样输出。LLM 直接拿纯 JSON
- **REPL 模式不受影响**:REPL 仍保留 stderr 给人类看
- **PrintUsage** 加新旗标的说明

## 关键决策
- stderr 重定向必须**早于** `DetectProjectPaths()`,否则启动期 fprintf 已经飞出去了
- REPL 模式保持原样,只在 -c 单次模式下静默 — 交互不应该静默
- JSON 反转义要处理 `\uXXXX`(4 位 hex),最简 UTF-8 编码就够用(BMP)

## 使用
```bash
# 之前
$ ./llm-shell.exe -c "gamestate"
[llm-shell] Engine path found via fallback: C:\Program Files\Epic Games\UE_5.7
{ "success": true, "output": "{\"wave\":{...}, ...}" }
```

```bash
# 之后
$ ./llm-shell.exe -q -j -c "gamestate"
{"wave":{"currentWave":"1",...},"player":{...},"enemyCount":2}
```

## Why this matters
- LLM 上下文是稀缺资源,70% 噪声 → 30% 真实信息,token 浪费巨大
- 嵌套 JSON 让 LLM 必须二次解析,出错率高
- 一个 `-q -j` 组合,2 个 flag 解决问题,胜过任何复杂输出处理

## commit
- `8db878b` — feat(llm-shell): -q (quiet stderr) + -j (json-only inner output)
