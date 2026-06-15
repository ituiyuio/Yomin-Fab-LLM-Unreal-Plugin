# LLMEasyShell 编译 / 重启周期经验

> 2 个核心规则：哪些改动 `livecoding` 足够，哪些必须 `restart`

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

## 规则 3：Python 模块缓存不自动清除

**Why**：

修改 `Plugins/LLMEasyShell/PyAbilities/LLMShellAbilities/abilities/*.py` 后：
- C++ DLL 已被 Live Coding 更新
- 但 Python `import` 的模块是缓存的（`sys.modules`）
- `importlib.reload()` 在同 session 内不生效
- 旧代码继续跑

**How to apply**：

```bash
# ✅ 正确
python reload     # 特殊命令：重扫 abilities/ + 清 sys.modules 缓存

# ❌ 不行
reload            # 只触发 Live Coding，不重载 Python 模块
```

**例外**：如果 `python reload` 之后行为仍异常，**重启编辑器**。

---

## 规则 4：Live Coding 失败诊断（2026-06-01 新增）

**位置**：`ShellCommand_Reload.cpp` 加 `ubtDiagnostics` 字段

**功能**：失败时自动扫描 `Engine/Programs/UnrealBuildTool/Log.txt`，抓 `error C` / `fatal error` / `Live coding failed` 等 marker + ±3 行上下文。

**触发**：
- 失败时（`!bSuccess || ErrorCount > 0`）自动附加
- 主动 `livecoding --ubt` 也行

**Why**：之前 `0 errors, 0 warnings, result: Failed` 完全无法诊断。改完直接能看到 `fatal error C1083: 无法打开包括文件: "static.c"` 等真实原因。

---

## 规则 5：UE_LOG 自动回传到 Python 响应（2026-06-01 新增）

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
├── 新增 UCLASS → restart
├── 改 USTRUCT 字段 → restart
├── 改 UENUM → restart
└── 不确定 → restart（5-10 分钟但安全）
```
