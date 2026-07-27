---
name: t1-llmshell-args-dropped-fix
description: "T1 fix (2026-06-11) — shell main.cpp JoinArgsToCommand helper lets `llm-shell find Actor Player` run without -c wrapper"
metadata: 
 node_type: memory
 type: bug
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# 修复

`.claude/skills/llm-easy-shell/llm-shell/main.cpp:3399-3409` 加 `JoinArgsToCommand` static helper;
line 3446 改用 helper 拼接所有非 flag token。

同步改 `.claude/skills/llm-easy-shell-lite/llmshelllite/main.cpp` 同款两处。

# Why
原代码 `command = arg;` 只存第一个非 flag token,后续全丢。所有 LLM 工作流必须用 `-c "..."` 才能跑 args。
任何裸调用 `llm-shell find Actor Player*` / `ls /Level/Actors` / `set /Actor/X Loc (1,2,3)` 都返回
"Usage: <cmd> <args>" 错或只跑首 token。

# How to apply
改 shell CLI argv 解析时,务必用 helper 拼全所有非 flag token,不要只存第一个。
- 思路:`command = JoinArgsToCommand(argc, argv, i);` 在第一个非 flag token 出现时把后面所有 token 全部 join
- `i` 是 for-loop 变量,要求 `for (int i = 1; i < argc; i++)` 在 scope 内;本项目就是
- 注意:helper 必须放在 main() 之前(本项目放在 PrintUsage 之后,main 之前)
- 改完**不要**在注释里写中文(MSVC 默认 codepage 936 GBK,UTF-8 中文会让 parser 把行号搞乱,即使 file 本身是 UTF-8 也会触发 C4819 警告 + 误报语法错)

# 验证结果 (2026-06-11)
- `llm-shell -c "find Actor Player*"` -> success (baseline)
- `llm-shell find Actor Player*` -> success (T1 修复目标,以前返 Usage 错)
- `llm-shell ls /Level/Actors` -> success, 27 actors
- `llm-shell -- find Actor Player*` -> success (-- 分隔符也 work,被当 unknown flag 跳过不影响非 flag 部分)

# 顺手发现: lite main.cpp:641 pre-existing build break (历史 — 已被 W28 fix)
- 症状:`MAX_PORT` / `BASE_PORT` 在 lite main.cpp:641 undeclared
- 根因:commit 22da25a 引入,BASE_PORT/MAX_PORT 在 `AllocatePortForInstance()` 内是 local const,
 但 `ScanForAvailablePorts()` 用了同样的名字
- **不是 T1 范围**,建议下个 task 单独修(把 BASE_PORT/MAX_PORT hoist 到 file-scope constexpr)
- 本次 stash 验证:git stash 把 lite main.cpp 临时还原,compile.ps1 同样 fail at line 641
 → 确认 pre-existing, T1 lite 代码改动正确

# Lite main.cpp 编译失败 — W28 fix 2026-06-12 已完成
- 修复 = hoisted to file-scope `constexpr` in `.claude/skills/llm-easy-shell-lite/llmshelllite/main.cpp:53-63`
- 3 个 file-scope constexpr:
 - `LITE_PORT_BASE = 15201` (Lite 独占端口段,避开 full 15151-15200)
 - `LITE_PORT_MAX = 15250`
 - `LITE_PORT_COUNT = LITE_PORT_MAX - LITE_PORT_BASE + 1` (50)
- `kScanPortCount = LITE_PORT_COUNT` 在 line 663 现在是合法 constexpr context
 (ScanForAvailablePorts 函数内,以前因名字冲突 + 局部 const 不可用于 constexpr 求值 → C2065 undeclared)
- T1 lite diff (JoinArgsToCommand helper) 留着没动, 编译现在过
 → `llmshelllite.exe` 可正常 build + 启动
- Hoist 到 file-scope constexpr 是 idiomatic 模式:
 - 单一 source of truth (BASE/MAX 不会再被多次定义或名字冲突)
 - 编译期可算 (constexpr 让 LITE_PORT_COUNT inline 求值,无运行时 cost)
 - 跨函数可见 (AllocatePortForInstance + ScanForAvailablePorts + 任何未来的 helper 都共享)
 - 修这种 "名字被局部变量遮蔽" 的 undeclared 错误的最快路径

# 不要重复犯
- lite main.cpp compile 失败 → **不要**改 ScanForAvailablePorts 绕过 T1 (会污染 T1 范围)
- 把 T1 lite JoinArgsToCommand 改回 commit HEAD 等"放弃 lite" → 也不是,因为 lite T1 代码本身正确
- 正解:commit T1 (full + lite main.cpp) 时**只 exclude lite build** (lite T1 diff 留着,等下个 task 修 641)
 - **W28 fix 已处理**: 641 行 build break 通过 W28 单独 PR 修了, 跟 T1 不需要互斥; T1 lite diff 现在能干净 build

> [tool-fix-07 session86 2026-07-10] 闭合 tool-fix-169 (commit c832707 2026-06-29) directory rename 时遗漏的 stale 路径引用 (本文件 L15 + L44 `llm-shell/main.cpp` → `llmshelllite/main.cpp` 1:1 同步) + 同 session 闭合 `.claude/skills/llm-easy-shell-lite/llm-shell/.current_port` orphan fossil (5 字节 runtime state 阻止了原计划的 rmdir,35 天残留)。来源 forward-defense: doc-audit.py 新 pattern `stale-lite-path-drift` + .gitignore 新 entry `.claude/skills/llm-easy-shell-lite/llm-shell/`。详见 `.lrh/ultimate-task/tasks/tool-fix-07.json` evolutionHistory session86。
