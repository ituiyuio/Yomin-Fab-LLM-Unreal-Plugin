# LLMEasyShellLite Experience Index

Lite 是 LLMEasyShell 的最精简只读子集，经验文档比 full 少很多。

---

## 当前文档

| 文件 | 主题 |
|------|------|
| [debugging.md](debugging.md) | Lite 只读命令的调试经验（与 full 共享 C++ 实现） |
| [02-pyability-framework.md](02-pyability-framework.md) | Lite PyAbility 执行框架（无内置内容） |
| [llmeasyshell-lite-parsecommand-clobber.md](llmeasyshell-lite-parsecommand-clobber.md) | ParseCommand 参数覆盖修复记录 |
| [llmeasyshell-lite-phase6-fixes-2026-06-01.md](llmeasyshell-lite-phase6-fixes-2026-06-01.md) | Phase 6 物理目录重命名 + plugin 路径同步 |
| [llmeasyshell-lite-plugin-paths.md](llmeasyshell-lite-plugin-paths.md) | 插件路径冲突排查（已修复，详见 phase6） |
| [llmshelllite-actual-capabilities-2026-06-14.md](llmshelllite-actual-capabilities-2026-06-14.md) | 2026-06-14 baseline 9 命令 + 3 ability；[tool-fix-133 2026-06-29] 重新验证 5 ability（+ python framework + llmms 2026-06-21+ 接入）；[tool-fix-07 session36 2026-07-09] 加 `llmwhitebox` 6 ability；[tool-fix-07 session76 2026-07-10] 加 `uireactionbus` (UIWebBridge) 7 ability + 15201-15250 端口（runtime source-of-truth = `./llmshelllite.exe help`） |
| [llmshelllite-exe-rename.md](llmshelllite-exe-rename.md) | llmshelllite.exe 改名历史记录 |
| [llmshelllite-port-segmentation.md](llmshelllite-port-segmentation.md) | Lite 15201-15250 端口段独立历史 |

---

## 不在 Lite 范围（参考 full）

以下主题 Lite 不涉及，需要时看 [full skill](../../llm-easy-shell/experience/)：

- 写命令经验（rm / cp / mv / new / set / spawn / save）
- Python ability 系统踩坑（full 数百个 `.py` ability，2026-10-25 runtime 读数 370；早期 271 读数已化石）
- Blueprint CDO / property 操作经验
- LiveCoding / restart 编译周期

---

## Lite 踩坑（待补充）

Lite 实际跑出来的已知问题（2026-06-14 验证）：

1. ~~**Preflight 不识别 plugin ability**：`material` / `ui` / `llmstatetree` 这些 plugin ability 名字在 preflight 阶段被当成 unknown command，输出红色 warning，但子命令直接调用能跑（噪音警告不影响功能）。~~ [tool-fix-07 2026-07-09 **ROOT-CAUSE 闭合**] 真正根因不是客户端，是**服务端 recv over-read**：`LLMEasyShellLiteTcpServer.cpp` / `LLMEasyShellTcpServer.cpp` 用 `FString(ANSI_TO_TCHAR(Buffer), BytesRead)` 从**未 null-terminate** 的 recv buffer 构造命令字符串，而 `FString(const TCHAR*, int32)` 的第二参是 **ExtraSlack（容量）不是长度上限**，导致 `ANSI_TO_TCHAR` 越界读 buffer 后面的 stale 堆内存（上一条响应的尾字节 / 未初始化字节 = 那个 `0x01`），拼到命令后面。单命令 `-c` 连接不触发（没有"下一条命令"被污染）；`FetchServerCommands`（help + 真命令 = 一条连接两命令）才暴露。**先前 disable `FetchServerCommands` + 硬编码 7 个 ability 是绕过症状**。本次修复：两个 server 的 recv 块都改成 `SetNumUninitialized(size+1)` + `Recv(Buffer.Num()-1)` + `Buffer[BytesRead]=0` 后再 `FString(ANSI_TO_TCHAR(...))`（无 ExtraSlack）→ 越界消失。随后 lite + full 客户端 `FetchServerCommands(sock)` **重新启用**，`KNOWN_COMMANDS` 硬编码 7 ability seed **删除**（改由 help 动态填充，不再漂移）。Runtime e2e：raw-socket `help→info`/`gamestate→info`/`material→info` 两端口全 `(OK)` 无残留字节；`llmshelllite -c info` 返回干净 success（原 `'info'`）；`material list-types` preflight 不再误报（`material` 未 seed，纯靠 fetch 识别）；`foobar` 控制组仍报 unknown。
2. ~~**`-q` / `-j` 旗标在 Lite 没实现**：SKILL.md 早期版本宣传过，但实际 Lite 编译没带这两个 flag 处理。~~ [tool-fix-285 2026-07-09] 闭合：从 full `llm-shell/main.cpp` 1:1 port `g_QuietMode` + `g_JsonOnlyMode` 全局 + 顶置 pre-parse `-q`/stderr-redirect + argument-loop 接收 `-q`/`--quiet`/`-j`/`--json-only` + `ExtractInnerOutputJson` helper + `PrintUsage` 增 2 行 + `.gitignore` 加 `llmshelllite-quiet.log`。Runtime e2e (15201 端口 + Lvl_SurvivorTest PIE-Idle) 控制组对比通过: `info` baseline 显示整个 envelope → `-j info` 抽出内层 `output` JSON → `-q info` 把 stderr 重定向到 `llmshelllite-quiet.log` → `-q -j foobar` 同根因验证 `[preflight] Unknown command: 'foobar'` 进入 quiet log。Semantic 跟 full `llm-shell/main.cpp:4446/4495/4498/949-1013` 1:1 对齐。
3. **`log --compile` Lite 不支持**：必须用 full 或 Advanced skill。
4. ~~**`<ability> --help` 不工作**~~：[tool-fix-07 2026-07-09] 随 #1 root-cause 闭合。`FetchServerCommands` 重新启用后 preflight 从 live `help` 动态获取全部 ability 名，`material` / `llmstatetree` / `llmms` / `llmwhitebox` 等都被识别（不再靠硬编码；server 端实际没注册的如 `vfx`/`pcg`/`ui` 也不会假装认识）。