---
name: ue-gamestate-derived-pause-state-gotcha-2026-06-14
description: "UE 5.7 LLMEasyShell gamestate 读 isActive 字段 — 只看 bWaveActive 不看 bPaused, 玩家死亡后误报 wave active. 修复 = 联合 bWaveActive && !bPaused 判断"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: 8a109965-0ab8-4220-bc75-cbe7753fcec9
---

# UE 5.7 gamestate 派生状态字段 gotcha

**问题症状**: PIE 中玩家死亡 4 秒后 (HP=0), `gamestate` 命令返回 `wave.isActive: true` (应为 false), `enemiesRemaining` 视觉不再减但 UI 误导。

**根因**: `ShellCommand_GameState.cpp:74` 读 `bWaveActive` 字段, 但 `EndGame()` 调 `WaveManager->PauseWave()` 只设 `bPaused=true`, `bWaveActive` 仍 true。**两个字段独立**:
- `bWaveActive`: master "wave 启动了" 标志
- `bPaused`: "游戏暂停但 wave 还在 active" 标志 (Shop/Death 时用)

**Why 容易踩**:
- 字段名相似 (bWaveActive/bPaused) 让人误以为 bPaused 是 bWaveActive 的暂停版本
- 实际是 2 个独立布尔, 4 种组合都有意义

**修复 (commit c1bc00f)**:

```cpp
// 之前
FString IsActive = FLLMEasyShellReflection::GetPropertyValue(WaveManagerActor, TEXT("bWaveActive"));
WaveObj->SetStringField(TEXT("isActive"), IsActive);

// 之后
FString IsActive = ...("bWaveActive");
FString IsPaused = ...("bPaused");
const bool bWaveReallyActive = (IsActive == "True" || IsActive == "1")
 && !(IsPaused == "True" || IsPaused == "1");
WaveObj->SetStringField(TEXT("isActive"), bWaveReallyActive ? TEXT("True") : TEXT("False"));
```

**Why 在 ShellCommand_GameState 修而非 WaveManager**:
- 修 WaveManager 需要加 `IsWaveActive()` UFUNCTION, 影响 BP 接口
- gamestate 是 LLM 诊断工具, 派生字段计算在诊断层更合适 (避免污染 core API)
- 唯一成本: 改 1 个 .cpp, 8 行

**How to apply**:
- 加新 gamestate 字段前, 检查是否需要联合其他字段 (避免类似 bPaused 误报)
- 类似情况: `isShopOpen` (ShopManager 字段) vs `bGameEnded` (GameMode 字段) — Shop 关闭但 game ended 时 isShopOpen 可能仍 true
- LLM agent 读 gamestate 做决策时, 派生字段优先自己组合, 不信单字段
