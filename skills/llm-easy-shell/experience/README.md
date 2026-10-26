# LLMEasyShell 经验库

基于实战踩坑凝练的 **40 个教训/规则**，分 7 个主题 (01-07) + 1 个速查 (debugging.md) + 3 个一次结案（本轮把 restart 持锁/超时判读蒸馏进 04 的规则 7，39→40）。

**72 个一次性 incident / PR work product** 在 [`incidents/`](incidents/) 子目录，按日期 / 主题归档为历史档案。


> (2026-10-26 发行仓订正：本仓 incidents/ 现读 72 = `ls skills/llm-easy-shell/experience/incidents/*.md | wc -l` = 73 枚文件 − 1 枚本 README（本目录计数惯例**不含 README.md**，见子目录 README 的 find 命令）。本轮入库 7 枚新档：`llmeshell-first-boot-asset-build-outlasts-restart-readiness-window-2026-09-29` / `llmeshell-port-handshake-and-stale-pch-2026-09-27` / `llmeshell-restart-misses-booting-editor-then-burns-a-link-2026-09-29` / `llmeshell-restart-unattended-kills-own-channel-2026-09-28` / `llmshell-restart-intercept-and-automation-framerate-2026-09-04` / `orphaned-unattended-editor-holds-dll-2026-09-29` / `ue58-python-material-graph-edit-api-defects-2026-09-05`。
> ⚠ 下方 r1920/r1923 两条历史注的算术（65→69→70→71→73）是**源项目仓**的读数链，在本仓不可复现（本仓 HEAD = 65），照录为史实、勿当本仓审计依据 —— 这正是 2026-10-26 订正它们的理由。)

> (r1923 2026-09-29：源项目仓现读 73 = HEAD 已计的 71 + 未入库新增 2 枚（`llmeshell-first-boot-asset-build-outlasts-restart-readiness-window-2026-09-29.md` 与 `llmeshell-port-handshake-and-stale-pch-2026-09-27.md`）。first-boot 那枚的技术要点：`--restart` 起来那台编辑器端口在听、`LLMEasyShell: Tick #` 心跳 0 条、`GFrameCounter` 列持续推进、无模态窗，而 `TCP Server started on port 15157` 出现两枚 —— **两条假说都被盘上证伪**：①「一次性构建饿死游戏线程」（`GFrameCounter` 那列持续推进）；②「控制通道双起」（一次成功 start 本就有两处发射点 `LLMEasyShellTcpServer.cpp:207` + `LLMEasyShellSubsystem.cpp:346`，健康会话同样两枚 ⇒ 无鉴别力）。**现行结论** = 那台 boot 从未进入常态 tick/serve 阶段：健康基准 `CODEO-backup-2026.09.28-15.04.21.log` 里心跳自 boot 后 ~2.5min 起、2.7h 累计 **130,070** 条，而 `--restart` 的 readiness cap 只有 300s ≪ 本机（4 核 VM）全量重建后首启的资产构建时长（本轮 >2h 未落定）⇒ 正确处置是**等，预算按小时**。方法账：判「0 命中 = 坏」之前必须先取一份**被服务过的**同类日志当健康基准 —— 本席头三次抽的 backup 全是从未服务过命令的短会话，那才是「健康会话也 0 条」这个错判的来源。判据在源项目固化成 `tools/compile/ue_editor_shell_health.py`（**源项目内部工具，本发行仓未发布**；四读数 / 六态 / `--selftest` 带鉴别与迁移归属检查，默认 0 副作用）。复算：`grep -ac "LLMEasyShell: Tick #" Saved/Logs/CODEO.log`（本轮 0 / 基准 130,070）与 `grep -acE "survivor\.[A-Z]" <候选基准>`（挑 >0 的那份当健康样本）。）

> (r1920 2026-09-28: 本行原写 65，`ls experience/incidents/*.md | wc -l` 现读 69（+ 本轮新增 1 = 70）⇒ 按实测改口。
> 新增那枚 = `incidents/llmeshell-restart-unattended-kills-own-channel-2026-09-28.md`：`--restart` 在 VMware 分支
> 给交互式编辑器追加 `-unattended`，而 `ShouldSuppressControlChannel()` 见 `FApp::IsUnattended()` 即不绑控制端口
> ⇒ restart 自己交付一个连不上的编辑器，表象是「本机 PIE 不可用」。复算：`netstat -ano | grep 15157`。）

> (r1920 同轮 09-29 收盘：现读 70 + 新增 1 = **71**。新增那枚 =
> `incidents/llmeshell-restart-misses-booting-editor-then-burns-a-link-2026-09-29.md`：`--restart` 把
> 启动期的活编辑器判成「Editor not running」⇒ 拿被映射占住的 DLL 照常 Link，20 分钟后报出与真编译错误
> 同形的失败。修 = Step 4 之前 `CreateFileA(GENERIC_WRITE, share=0)` 测锁，测到就点名 PID 并拒建。
> 两枚弯路值得记：模块名取**项目名**不是 target 名；探测面必须用写权限（`DELETE/share=0` 对加载中的
> 镜像**放行**）。复算：`python -c` 那条自检，见该档「判据 / 复现」。)

> (2026-10-26 本仓核对：canonical 表教训数列 6+4+5+**7**+5+1+4+7+1 = **40**（04 含本轮新增规则 7），与 `skills/llm-easy-shell/SKILL.md` 的「40 个教训」1:1 一致。本轮另闭合 2 处同族 fossil：06-cli-flags.md 表值 3→1、debugging.md 2→7（按各文件 `^## 教训` 实际标题数归正）。原 tool-fix-135/session14/session35 三条注描述的是源项目仓的修复史（commit id 与行号在本仓均不存在），已收拢为本条本仓事实。)

## 文档清单（canonical 教训库）

| 文件 | 主题 | 教训数 |
|------|------|--------|
| [01-builtin-commands.md](01-builtin-commands.md) | 内置 shell 命令（rm/cp/mv/new/set 路径与参数） | 6 |
| [02-python-abilities.md](02-python-abilities.md) | Python ability 系统（执行模式 / 输出 / 参数 / 字段名） | 4 |
| [03-blueprint-property.md](03-blueprint-property.md) | Blueprint / Property 操作（bpprop/bpprop/ClassProperty/嵌套路径） | 5 |
| [04-build-and-restart.md](04-build-and-restart.md) | 编译 / 重启周期（LiveCoding vs restart 决策树，7 规则） | 7 |
| [05-screenshot.md](05-screenshot.md) | 截图（UE PIE 双路径 / CEF 延迟 / 新输出格式） | 5 |
| [06-cli-flags.md](06-cli-flags.md) | -q/--quiet stderr 重定向 + -j/--json-only 反转义,LLM 上下文降噪 70% | 1 |
| [07-editor-shot-win32.md](07-editor-shot-win32.md) | Editor 窗口截图（Win32 PrintWindow 路径，绕开 FViewport 0×0） | 4 |
| [debugging.md](debugging.md) | 早期路径解析 + 反射 UI + Python ability 教训 | 7 |
| [2026-06-12-slate-ui-inspector-summary.md](2026-06-12-slate-ui-inspector-summary.md) | ui 命令族 4-PR 实施总览 (SKILL.md 引用) | — |
| [llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md](llmeshell-ui-pr5h-source-audit-retraction-2026-06-13.md) | `success: true` 不证明 "点中了" 教训 (SKILL.md 引用) | — |
| [t3-bpcomp-tobjectptr-reflection-fix.md](t3-bpcomp-tobjectptr-reflection-fix.md) | T3 修复 (2026-06-11) bpcomp ability 访问 C++ TObjectPtr 字段 | 1 |

> **不要**直接读 `incidents/` 找根因诊断路径 — 那是历史 commit 快照，所有可复用模式已蒸馏到上表 11 个 canonical 文件

## 速查决策树

### 改完代码怎么验证？

```
改动类型？
├── 改 .py 文件 → python reload
├── 改 .cpp 函数体（不动 USTRUCT）→ livecoding
├── 改 .h 函数签名（不动 USTRUCT 布局）→ livecoding
├── 新增 UCLASS → restart
├── 改 USTRUCT 字段 → restart
├── 改 UENUM → restart
├── Build.cs 加新 PrivateDependencyModuleName → restart（livecoding 假绿灯）
└── 不确定 → restart（5-10 分钟但安全）
```

详见 [04-build-and-restart.md](04-build-and-restart.md)

### 命令返回异常？

| 症状 | 跳到 |
|------|------|
| Actor 找不到 / 路径解析失败 | [01-builtin-commands.md](01-builtin-commands.md) 教训 1 |
| `SyntaxError` 或空 output | [02-python-abilities.md](02-python-abilities.md) 教训 1, 2 |
| `unexpected keyword 'world'` | [02-python-abilities.md](02-python-abilities.md) 教训 3 |
| bIsAsync / bIsPIE 永远 default | [02-python-abilities.md](02-python-abilities.md) 教训 4 |
| `set ClassProperty` 断言崩溃 | [03-blueprint-property.md](03-blueprint-property.md) 教训 1c / 2 Fix 1 |
| `set` 报 success 但 `cat` 读 0 | [03-blueprint-property.md](03-blueprint-property.md) 教训 1e |
| `Component.Property` 路径失败 | [03-blueprint-property.md](03-blueprint-property.md) 教训 2 Fix 3 |
| livecoding 报 success 但 UBT 挂 | [04-build-and-restart.md](04-build-and-restart.md) 规则 3（Build.cs 改必 restart） |
| `--restart` 报 `cannot link, target module is held...` | [04-build-and-restart.md](04-build-and-restart.md) 规则 7（DLL 被孤悬编辑器攥住，按 PID 收尸） |
| `--restart` 报 `Build cap reached ... NOT a compile failure` / `hung` | [04-build-and-restart.md](04-build-and-restart.md) 规则 7（树杀超时/首启资产构建超窗，预算按小时） |
| Python 改完 reload 仍跑旧逻辑 | [04-build-and-restart.md](04-build-and-restart.md) 规则 4（用 `python reload` 不是 `reload`） |
| 截图截不到 HUD / 全白 | [05-screenshot.md](05-screenshot.md) 教训 1, 3, 4 |
| 截图文件名带 5 个 0 | [05-screenshot.md](05-screenshot.md) 教训 2 |
| `source=editor` 永远 0×0 | [07-editor-shot-win32.md](07-editor-shot-win32.md) 教训 1（用 Win32 路径） |
| Win32 PrintWindow 截到黑屏 | [07-editor-shot-win32.md](07-editor-shot-win32.md) 教训 4（缺 PW_RENDERFULLCONTENT） |

### 加新能力

- **C++ 新能力**：参考 [04-build-and-restart.md](04-build-and-restart.md) 决定 livecoding / restart
- **Python 新 ability**：
  - 函数签名 `def main(args, context=None):`（与 dispatcher 期望一致）
  - 双输出：`unreal.log()` + `output` 键
  - 字段读取用 `_uh.get_field()`（支持 snake_case + 去 b 前缀）
  - 改完必跑 `python reload`

## 写作约定

每个文件用相同格式：

```
### 教训 N：[一句话]
**场景**：[具体症状]
**根因**：[代码层原因 + 文件:行号]
**修复模式**：[代码示例]
**经验**：[通用规则，下次怎么避]
```

- 场景要可识别（用户能 match 上）
- 根因要精确（文件:行号）
- 修复模式要可复用（不只解决当前问题）
- 经验要通用（不是"加 try/except"这种 ad hoc）
