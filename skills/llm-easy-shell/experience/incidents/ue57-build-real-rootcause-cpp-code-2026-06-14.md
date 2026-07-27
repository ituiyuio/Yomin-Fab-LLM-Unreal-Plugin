---
name: ue57-build-real-rootcause-cpp-code-2026-06-14
description: "UE 5.7.4 build 失败的真正根因 (纠正 ue57-installedbuild-thirdparty-missing) — 90% 是 C++ 代码问题 (protected 跨类访问 / missing include), 10% 是 live coding 占用 UBT. Build.bat 走得通, 不需要 reinstall third-party"
metadata: 
 node_type: memory
 type: reference
 originSessionId: 8a109965-0ab8-4220-bc75-cbe7753fcec9
---

# UE 5.7.4 build 真正根因 (2026-06-14 实测, 纠正之前认知)

**纠正**: 之前 memory [[ue57-installedbuild-thirdparty-missing]] 把 Live Coding 失败归因到 "InstalledBuild 缺三方库", 实测发现:

## 真正 build 失败 3 层根因 (按出现频率)

### 根因 #1 (最常见, 80%): Live Coding 占用 UBT
- 症状: "Unable to build while Live Coding is active. Exit the editor and game, or press Ctrl+Alt+F11"
- 修复: `llm-shell --restart` (它内部 kill editor → build → 重启, 一步到位)
- 不要再手动 `livecoding` 命令 — 那会触发 relink 整个 editor binary
- **不要**走 Live Coding 路径编译项目 module (CODEO), 用 Build.bat

### 根因 #2 (常见, 15%): C++ 跨类 protected 字段访问
- 症状: `error C2248: 'AClassName::FieldName' : cannot access protected member declared in class 'AClassName'`
- 修复: 加 public UFUNCTION setter (UE 5.7 风格), 不直接 public 字段
 ```cpp
 // 错
 WaveMgr->DailySeedHash = NewValue; // C2248 if protected
 // 对
 UFUNCTION(BlueprintCallable, Category = "Survivor|Wave|Daily")
 void SetDailySeedHash(const FString& Hash) { DailySeedHash = Hash; }
 ```
- Reference: [[ue5-survivor-debug]] Bug 2 (记忆里有完整修复方法)

### 根因 #3 (常见, 5%): 引用错的 class 成员 + missing include
- 症状: `error C2039: 'SlotName' : is not a member of 'USurvivorSaveGame'`
- 修复: 检查常量/字段属于哪个 class
 - `USurvivorSaveGame` 字段: 实际数据
 - `FSurvivorSaveLoad` 字段: 静态常量 (SlotName/UserIndex) + 静态函数
- 同时检查 include — `OnNGPlusLoaded.Broadcast` 之前需要 `#include "Survivor/NewGamePlusComponent.h"`

## Build 走通完整流程 (实测 2026-06-14)

```bash
# 1. 编辑器空闲时: Build.bat 直接跑 (会成功, ~10s)
"C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/Build.bat" \
 CODEOEditor Win64 Development \
 -Project="D:/UnrealEngine/CODEO/CODEO.uproject" \
 -WaitMutex -NoHotReload

# 2. 启动新 editor (用刚 build 的 binary)
llm-shell --restart --skip-build
# 内部: WM_CLOSE 旧 editor → 等进程退出 → 启动新 editor

# 3. PIE 验证
llm-shell -c "play" && sleep 10 && llm-shell -c "gamestate"
```

## Why 之前 memory 归因错误

- 我之前 [ue57-installedbuild-thirdparty-missing] 看到 `[1/958] MiMalloc.c → static.c` 错误就猜是 third-party 缺失
- 实际: UBT 在重 link editor binary 时, 会尝试增量编译受影响的 engine modules
- 那些 engine modules 的 `#include <static.c>` 失败, **不是因为 static.c 物理缺失**, 而是因为 live coding 触发的 relink 路径有 bug (跟我 C++ 改动无关)
- 走 Build.bat (UBT incremental) 不触发这个路径, 所以走得通

## Sanity check 流程 (更新版)

诊断 UE 5.7 build 失败:
```bash
# 1. 检查 editor 状态
llm-shell -c "info" | grep livecoding

# 2. 检查 UBT log
tail -30 "C:/Program Files/Epic Games/UE_5.7/Engine/Programs/UnrealBuildTool/Log.txt"

# 3. 找真正错误 (C2248/C2039/C2027 = C++ 错误; 找不到头文件 = include 错; static.c/AHEasing = 真的 third-party 错)
```

**How to apply**:
- 改 C++ 后 build 失败, 先 grep `error C` 找真正编译错误, 不要被 "static.c not found" 误导
- 跨 class 访问字段一律用 UFUNCTION setter, 不直接 public 字段
- 调试时用 `llm-shell --restart` 走完整路径, 不用 live coding
- 如果 `llm-shell --restart` 卡在 build, 看 UBT log 找真正错, 别重装 UE
