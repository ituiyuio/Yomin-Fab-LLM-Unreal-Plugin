---
name: llmshell-args-dropped-bug-2026-06-11
description: "LLMEasyShell 2026-06-11 发现: 有参命令(find/ls/set/discover/python)全部返回 Usage 无参错误,只有无参命令(info/play/stop/save/log/gamestate)正常工作,根因疑是 ParseCommand/Args 解析层在某种状态下丢失"
metadata: 
 node_type: memory
 type: bug
 originSessionId: 1a2de1ad-8a01-4953-b887-6ad108e3e820
---

# 现象

2026-06-11 CODEO 项目,UE 5.7.4,LLMEasyShell 编辑器在 port 15151 + Lite 在 15201 双端口监听(同一 PID 9888)。

**工作命令(无参)**: `info`、`play`、`stop`、`save`、`log`、`gamestate`、`help` 返回正常 JSON。

**全部失败命令(有参)**: `find`、`ls`、`set`、`discover`、`python` 全部返回 `"Usage: <cmd> <args>..."` 错误,好像 Args 列表是空的。

# 复现

```bash
llm-shell.exe find Actor Player # → "Usage: find <type> <pattern>" Usage 错
llm-shell.exe ls /Level/Actors # → "Usage: ls <path> [options]" Usage 错
llm-shell.exe set /Actor/X Location (1,2,3) # → "Usage: set <path> <value>" Usage 错
llm-shell.exe python scene scene_stats # → "Unknown command: python"
```

# 真正根因 (2026-06-11 验证)

**不是引擎端 bug,是 shell main.cpp 参数解析 bug!**

看 `.claude/skills/llm-easy-shell/llm-shell/main.cpp:3392-3398`:
```cpp
else if (arg[0] != '-') {
 // Treat as command if no -c flag
 if (!singleCommand) {
 singleCommand = true;
 command = arg; // <-- 只存第一个 arg,后续被丢弃
 }
}
```

Shell 收到 `find Actor Player` 时:
- arg[0]="find" → `command="find"`,其他都丢
- 服务端 `ParseCommand` 解析出 Args=["find"] → 弹出后 Args=[] → 失败

**修复**: 必须用 `-c` 一次性传完整命令字符串:
```bash
llm-shell.exe -c "find Actor Player" # ✅ 工作
llm-shell.exe -c "ls /Level/Actors" # ✅ 工作 (27 actors)
llm-shell.exe -c "python scene scene_stats" # ✅ 工作
```

# `python` 不可用的真正原因

Crash log 显示: `Python is not available - skipping ability scan`
- Python 插件在当前 editor 实例没启用
- `python` 能力就不会注册
- 但 `-c "python scene scene_stats"` 仍能 dispatch(可能 C++ 路径有 fallback)

# 状态
- FIX 在调用端,不需要 C++ rebuild
- 所有之前标"坏"的命令(`find`/`ls`/`python`/`discover`/`set`)用 `-c` 都能跑
- `python scene scene_stats` 当前因为 Python 插件未启用,只能跑不依赖 Python 反射的部分(拿 0 个 actor)

# 结论

**所有工作流程都用 `-c "command"` 模式,不要用空格分隔的 argv 模式。**


# 临时 workaround

- 用 `info` / `play` / `stop` / `gamestate` / `log` 走 PIE 流程
- 直接读源文件 `Source/CODEO/...` 来做修改
- 改完后用 `--restart` 触发 build + restart(注意 build 仍可能因 engine 三方库 include 失败)
- **不要**依赖 `find` / `ls` / `discover` 来发现 actor,直接用 source + BP 文件搜索

# 验证信号

- 修 WaveManager UPROPERTY 后看 `gamestate` 的 `wave.currentWave` 是否从 "null" 变数字
- 修 EnemyBase 伤害后看 `gamestate` 的 `player.currentHealth` 衰减速率
