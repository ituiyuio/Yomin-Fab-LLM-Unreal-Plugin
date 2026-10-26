# LLMEasyShell 编译 / 重启周期经验

> 6 个核心规则：哪些改动 `livecoding` 足够，哪些必须 `restart`

---

## 规则总览

| 改动类型 | 命令 | 说明 |
|---------|------|------|
| 现有类函数体 | `livecoding` | 函数体、算法、局部变量 |
| 现有类 UPROPERTY/UFUNCTION | `livecoding` | 多数情况可以 |
| 私有 `.cpp` 函数体 | `livecoding` | OK |
| 私有 `.h` 函数签名（不动 USTRUCT 布局） | `livecoding` | 多数情况 OK |
| **新增 C++ 类（UCLASS）** | `restart` | LiveCoding 无法处理 |
| **USTRUCT 字段（加/删/改）** | `restart` | 触发 UHT 重生成 |
| **UENUM** | `restart` | 反射元数据变化 |
| **继承层次变化** | `restart` | 需重新实例化 |
| **Build.cs 加新 PrivateDependencyModuleName** | `restart` | `livecoding` 报 success 但 UBT 全量 build 仍会 fatal error |
| 不确定 | `restart` | 安全选择（5-10 分钟完整启动） |

---

## 规则 1：新增 C++ 类（UCLASS）必须 `restart`

**Why**：

- LiveCoding 走**增量编译 + 热替换**实现代码更新
- 但 UHT（Unreal Header Tool）生成的 `.generated.h` 和新类的反射注册需要**完整启动流程**
- 新增 C++ 类后即使 DLL 链接成功，反射系统里的 `UClass*` 仍为 `nullptr`
- 表现：Python 端 `unreal.load_class()` 找不到，CDO 创建失败

**判定信号**：

- 添加 `.h` 含 `UCLASS()` 宏
- 添加 `.cpp` 含 `IMPLEMENT_PRIMARY_GAME_MODULE` 或类似宏
- 任何需要 UHT 生成新 `.gen.cpp` 的内容

**How to apply**：

```bash
# ❌ 不行
livecoding  # 0 errors 但 UClass* 是 nullptr，运行时找不到类

# ✅ 必须
llm-shell.exe --restart  # save → shutdown → MSBuild → 启动引擎
```

---

## 规则 2：USTRUCT 字段变更必须 `restart`

**场景**：给 `LLMEasyShellEditorLib.h` 的 `FLLEScreenshotResult` 加字段（`Source` / `Base64`），Live Coding 失败：

```
compiling: false
result: "Failed"
errorCount: 0, warningCount: 0
```

UBT 日志显示**所有**引擎模块（MiMalloc、Core、Slate、Niagara…）触发完整重编译，找不到 `static.c` / `sse_mathfun_extension.h` 等头文件。

**Why**：

USTRUCT 字段变化 → UHT 重新生成反射元数据（`.gen.cpp`）→ Live Coding 的**二进制 ABI 补丁无法处理反射布局变化** → UBT 把工作集识别错误 → 触发完整 UBT 编译。在 worktree 模式下，UBT 工作目录被错误指向 worktree 路径，找不到引擎依赖头文件。

**判定信号**：

- 公共 header 里 `USTRUCT` 内部 `UPROPERTY` 加/删/改
- 任何触发 UHT 重生成的反射元数据变更

**How to apply**：

```bash
# 修改 LLMEasyShellEditorLib.h USTRUCT 字段
llm-shell.exe --restart
# 5 个源文件识别为已修改，触发完整 build
# 生成 UnrealEditor-CODEO.dll (3.3MB) + .pdb (88MB)
# 耗时 5-10 分钟
```

---

## 规则 3：Build.cs 加新 PrivateDependencyModuleName 必须 `restart`（2026-06-21 实测）

**场景**：给 `LLMEasyShell.Build.cs` 加 `PrivateDependencyModuleNames.Add("ModelContextProtocol")` 让 `ShellCommand_Mcp.cpp` 能 include `IModelContextProtocolModule.h`。

**症状**：

```
$ livecoding
{ "compileSuccess": true, "errorCount": 0, "warningCount": 0, ... }

$ llm-shell --restart
[15/50] Compile [x64] ShellCommand_Mcp.cpp
ShellCommand_Mcp.cpp(10,1): fatal error C1083: ModelContextProtocolSettings.h: No such file or directory
```

**Why**：

- LiveCoding 的 PCH / `.gen.cpp` 缓存对**新增 module dependency** 不敏感 — 它 patch 现有 DLL 时认为头文件依赖链没变（因为实际 include 路径是延迟解析的）
- `livecoding` 报 `compileSuccess:true` **只是 patch 现有函数指令**成功，不是真的把新 module link 进去
- 真正会暴露问题的是 `llm-shell --restart` 走 UBT 全量构建，此时 UBT 才扫到新 dep → 找不到 header → fatal error

**判定信号**：

- 编辑 `*.Build.cs` 加 `PrivateDependencyModuleNames.Add("...")` 或 `PublicDependencyModuleNames.Add("...")`
- 编辑 `*.uplugin` 加 Plugins 数组项
- 编辑 `PrivateDefinitions` / `PublicDefinitions`

**How to apply**：

```bash
# ❌ 不要只信 livecoding success
$ livecoding
{ "compileSuccess": true, ... }   # ← 假绿灯，restart 会挂

# ✅ 加新 dep 后必须 UBT 全量 build
$ llm-shell --restart
[Build log] Build succeeded.   # ← 这是真绿灯
```

**记忆口诀**：**Build.cs 改了必 restart，livecoding 不可信**。

**自动检测（2026-07-18 引入；2026-09-03 r771/r771b 根修后才真正生效）**：`reload` preflight 扫描 `*.Build.cs` / `*.Target.cs`（`Source/` + `Plugins/` 两树）+ `*.uplugin`（`Plugins/`）+ `*.uproject`（项目根）+ `*.h`（`Source/`）最近 60s 修改（`ShellCommand_Reload.cpp` preflight 段，~L317-423），命中时：
- `reload --status` 与编译路径结果 JSON 的 `livecoding` 块带 `requiresRestart=true` +
  `reason="N restart-required file(s) modified in last 60s (X .h, Y .Build.cs/.Target.cs, Z .uplugin/.uproject)"`
  ——**这是主信号面**（服务端 stderr `[preflight]` 提示到不了 CLI quiet log，仅服务端本地可见）
- LLM caller 看到 requiresRestart=true 主动走 `--restart`

> **API 陷阱（r771b 勘误）**：`IFileManager::FindFilesRecursive` 第 6 参 `bClearFileNames` **默认
> true** ——对同一数组链式调用会"后一次清空前一次"，终态只剩末次调用。原实现 4 连调自 2026-07-18
> 起因此恒空（末次是 0 命中的 `Plugins/**/*.Target.cs`），检测从未生效；CountRecent 的时钟源 bug
> （QPC 秒减 unix mtime 恒负）同期叠加。多树累积必须显式传 `/*bClearFileNames=*/false`。非递归
> `FindFiles`（4 参重载）无此参数，链式安全。

详见 `verify-e2e.py` 的 "full reload preflight detects Build.cs" 检查（每树取基线 → touch Plugins 与 Source 各一个 `.Build.cs` → 跑 `reload --status` → 判据 = status JSON `livecoding.requiresRestart` **且 reason 里 `.Build.cs/.Target.cs` 计数相对基线 +1** —— 2026-10-26 勘误：旧判据"reason 含 Build.cs 子串"是恒真式，三类标签无条件打印、只改 `.h` 也能全绿；quiet-log 兜底同日删除，服务端 stderr 到不了 CLI）。

**额外注意**：加 dep 时还要看目标 module 有几个子 module 都要加。例：UE 5.8 的 ModelContextProtocol plugin 有 6 个 module，Settings 在 `ModelContextProtocolEngine` 而非 `ModelContextProtocol` — 加漏了 UBT 会报"找不到 header"。

---

## 规则 4：Python 模块缓存不自动清除

**Why**：

修改 `Plugins/LLMEasyShell/Content/Python/LLMShellAbilities/abilities/*.py` 后：
- C++ DLL 已被 Live Coding 更新
- 但 Python `import` 的模块是缓存的（`sys.modules`）
- `importlib.reload()` 在同 session 内不生效
- 旧代码继续跑

**How to apply**：

```bash
# ✅ 正确 (2026-09-03 起两个都行)
python reload     # 特殊命令：重扫 abilities/ + 清 sys.modules 缓存
reload            # 2026-09-03 修复: bare reload (及 lc/livecoding) 在 LiveCoding 编译前
                  # 也走 ClearModuleCache + 重扫描 + dispatch 重注册 (ShellCommand_Reload.cpp);
                  # 纯 .py 修改即使 LiveCoding 报 NoChanges 也完成重载 (JSON 带 pythonReloaded 字段)。
                  # 注意: LC 文件监视器偶发漏检后台期间的 .cpp 修改 (报 "no code changes") —
                  # touch 该 .cpp 后再 reload 即可恢复检测。

# ❌ 仍然不行
importlib.reload()   # ability 内部自行 reload 其它模块 (同 session 缓存规则不变)
```

**例外**：如果 `reload` 之后行为仍异常，**重启编辑器**。

---

## 规则 5：Live Coding 失败诊断（2026-06-01 新增）

**位置**：`ShellCommand_Reload.cpp` 加 `ubtDiagnostics` 字段

**功能**：失败时自动扫描 `Engine/Programs/UnrealBuildTool/Log.txt`，抓 `error C` / `fatal error` / `Live coding failed` 等 marker + ±3 行上下文。

**触发**：
- 失败时（`!bSuccess || ErrorCount > 0`）自动附加
- 主动 `livecoding --ubt` 也行

**Why**：之前 `0 errors, 0 warnings, result: Failed` 完全无法诊断。改完直接能看到 `fatal error C1083: 无法打开包括文件: "static.c"` 等真实原因。

---

## 规则 6：UE_LOG 自动回传到 Python 响应（2026-06-01 新增）

**位置**：`LLMEasyShellTcpServer.cpp` 加 `FCapturingLogDevice` + `AppendCapturedLogsToResult`

**功能**：每个命令用 `GLog->AddOutputDevice/RemoveOutputDevice` 包裹执行，捕获的 Warning+ 日志作为 `capturedLogs` JSON 字段附加到响应。

**Why**：Python 端 SyntaxError/异常本来要 grep log file 才能看到，现在直接出现在响应里。

---

## 速查决策树

```
改动类型？
├── 改 .py 文件 → python reload
├── 改 .cpp 函数体（不动 USTRUCT）→ livecoding
├── 改 .h 函数签名（不动 USTRUCT 布局）→ livecoding
├── 改 *.Build.cs / *.Target.cs / *.uplugin（加 dep、改模块定义）→ restart（规则 3，livecoding 假绿灯）
├── 新增 UCLASS → restart
├── 改 USTRUCT 字段 → restart
├── 改 UENUM → restart
└── 不确定 → restart（5-10 分钟但安全）
```
