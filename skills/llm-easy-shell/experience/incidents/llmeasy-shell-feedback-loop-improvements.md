---
name: llmeasy-shell-feedback-loop-improvements
description: "LLMEasyShell 全面加强反馈循环 + preflight 护栏 12 痛点修复 (2026-06-11),含 call 参数解析/livecoding 检测/play --wait/截图默认 show_ui/discover 过滤/find --type/编译 BOM strip/set PIE 提示/Material param 预检"
metadata: 
 node_type: memory
 type: project
 originSessionId: d5689e8b-a539-4f0c-b7ea-76a918a1cbcd
---

# LLMEasyShell 12 痛点全面修复 (2026-06-11)

针对 2026-06-11 用户报的所有痛点系统化修复,加强 LLM 反馈循环 + preflight 护栏:

## 修复一览(按文件)

### Plugins/LLMEasyShell/ 插件 C++ 端

| 文件 | 修复内容 |
|------|---------|
| ShellCommand_Call.cpp | 参数解析: 4 种格式统一(原只支持 --name value);Material param 预检(call SetVectorParameterValue 之前反射查 material 是否有该 param,无则输出 _preflight_hint) |
| ShellCommand_Find.cpp | --type <ClassName> 过滤(支持短名+全路径匹配) |
| ShellCommand_Discover.cpp | --writable (仅 EditAnywhere + BlueprintReadWrite) / --category (按 Category meta) / --limit N 截断 |
| ShellCommand_Play.cpp | --wait / --timeout / --post-wait (polling GEngine->GetWorldContexts() 直到 PIE world HasBegunPlay) |
| ShellCommand_Reload.cpp | --force-restart + 60s 内 .h 修改检测 + stderr warning 提示用 --restart |
| ShellCommand_Set.cpp | PIE-aware hint: 检测 PIE 跑时 set 改的是 editor instance,PIE 看不到,加 _preflight_hint 字段 |
| LLMEasyShellTypes.h | FindAssets/FindAssetsInPath/ShowObjectDetails 函数签名加 ClassTypeFilter/CategoryFilter/ResultLimit 参数 |

### .claude/skills/llm-easy-shell/ CLI 端

| 文件 | 修复内容 |
|------|---------|
| llm-shell/main.cpp | 编译输出 BOM strip (0xFF 0xFE 过滤 + 0x00 过滤 + 连续行去重);BASE_PORT/MAX_PORT 提升到 file-level constexpr;ScanForAvailablePorts VLA 换 std::vector;SUPPORTED_FLAGS 白名单加新 flag |
| llm-shell/llm-shell.exe | 重新编译 (462KB) |

### Plugins/LLMEasyShell/PyAbilities/ 端

| 文件 | 修复内容 |
|------|---------|
| abilities/editor.py | screenshot 默认 async=true, show_ui=true(原 false/false);解决 HUD/WebBrowser 截不到问题 |

## 关键设计原则

### 1. 反馈循环注入 JSON 字段,不进 stderr
所有 hint / 警告 / 修复建议注入到 JSON response 的 `_preflight_hint` / `_hint` 字段。
LLM 用 JSON parser 自动收到诊断,不会漏掉 stderr 字符串。

### 2. 错误返回带 fix hint
失败时不仅说"出了什么错",还说"怎么修":
```
"error": "PIE did not become ready within 30000 ms (poll 150 times).",
"Hint: Use 'info' to check PIE state, or pass --timeout 60000 for slow shaders."
```

### 3. preflight 在函数调用前反射检查
不在事后补救。例: call SetVectorParameterValue 之前,枚举 mesh 用的所有 material 的
Vector param 列表,目标 param 不存在时直接 _preflight_hint 提示"create material with
VectorParameter named 'X' first"。

### 4. 静默 no-op 检测
UE 引擎很多 API 失败不报错不警告(MID SetVectorParameterValue、SetActorLocation
越界、CreateAndSetMaterialInstanceDynamic material slot 还没填好等)。
LLM 以为成功了实际没效果 — 用反射 / 主动检查转化为"显式失败 + 修复建议"。

### 5. PIE-aware 命令
任何 set / call / discover 在 PIE 跑时加 hint: 改的是 editor instance,PIE 看不到。
提示 "stop → set → play" 或 "use 'bpprop set' to modify the BP asset CDO directly"。

## 解决的关键痛点(用户原文)

| 痛点 | 修复方式 |
|------|---------|
| livecoding 全量 958 actions 编译触发 include 找不到 | reload 加 header change detection,force restart 走 modular build path |
| SetVectorParameterValueOnMaterials UE 5.7 签名收紧 | 不再用该 API,改用 MID.SetVectorParameterValue(FLinearColor) |
| PIE 实例与 editor 实例数据不互通 | set PIE-aware hint |
| call 参数解析歧义 | 4 种格式统一(--name value/--name=value/name=value/{json}) |
| MID SetVectorParameterValue 静默 no-op | 反射预检 material param,无则报错+建议 |
| 截图不包含 HUD/WebBrowser | 默认 async=true, show_ui=true |
| 编译输出 BOM 乱码 | 0xFF/0xFE/0x00 字节过滤 + 连续行去重 |
| discover 输出 200+ 反射函数 | --writable / --category / --limit 截断 |
| set PIE 影响 | _preflight_hint 字段 |
| find type 过滤 | --type <ClassName> 走 AssetClassPath 匹配 |
| 启动后无 PIE 同步 | play --wait 阻塞 polling |
| restart 60s push-model 等不到 | (未完全解决,但 BOM strip 让 LLM 能看到真实错误) |

## UE 5.7 编译错误踩坑(已记在此 memory,复用)

1. **WaveManager.h**: UE 5.7 UHT 严格化,BlueprintReadOnly 不能在 private 字段,
 改 protected
2. **Play.cpp**: `UWorld::bBegunPlay` 公开访问 deprecated,改 `HasBegunPlay()`
3. **Call.cpp**: FString::Printf '{0}' 语法需要 FString 引用(不接受 *FString);
 复杂字符串拼接避免 `{0}` 占位符陷阱
4. **Call.cpp**: UE 5.7 FormatStringSan 严格化,%s 期望 dereferenced FString
5. **Discover.cpp**: 5 个新 filter 变量必须在 ShowObjectDetails 内部用,
 ShowBlueprintDetails 函数体内不能用(没透传)
6. **Reload.cpp**: TCHAR* fprintf 报错,改 TCHAR_TO_UTF8 转换
7. **main.cpp**: file-internal const int 跨函数访问不到,改 file-level constexpr

## 验证

- 全 LLMEasyShell plugin C++ build 通过(UBT 22s)
- llm-shell.exe 重新编译 (462KB,vs 旧版相同)
- editor 正常启动, info / ls / cat / discover / find / play / set / call / screen
 全部命令工作

## commit

`7b3e97d` feat(llmeasy-shell): 全面加强反馈循环 + preflight 护栏 (12 痛点修复)
9 files changed, 559 insertions(+), 61 deletions(-)
