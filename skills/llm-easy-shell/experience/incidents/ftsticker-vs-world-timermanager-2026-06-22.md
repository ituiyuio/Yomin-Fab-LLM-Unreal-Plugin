---
name: ftsticker-vs-world-timermanager-2026-06-22
description: 2026-06-22 升级 WebUIBase/LevelUp timer 改用 FTSTicker — 解决 PIE + GamePause 边界 World TimerManager 不 fire 问题
metadata: 
 node_type: memory
 type: feedback
 originSessionId: aecc241e-eeaa-4b7c-9a34-a02822517353
---

# 2026-06-22 FTSTicker 替代 World TimerManager

## 问题
在 PIE 中通过 editor Python 调用 `Player->LevelUp()`,内部用 `World->GetTimerManager().SetTimer(...)` 设了 4s 延迟回调。
- `WorldType` = 3 (PIE) ✓
- `SetTimer` 返回 valid FTimerHandle ✓
- 但 4s 后 lambda 不 fire ✗
- 同样的 `World->GetTimerManager()` 在 `WebUIBase::NativeConstruct` 设的 1s/3.5s/6s timer 也不 fire

## 根因
World TimerManager 在某些 PIE 启动状态下(world 边界 + 异步 spawn 流程)timer 不会触发。具体是:
- 玩家由 `BP_SurvivorPlayer_C_0` 标识(PIE 副本)
- `GetWorld()` 返回的 world 是 PIE world(world_type=3 验证过)
- 但 timer manager 的 tick 似乎被卡死(可能跟 `BeginPlay spawning 4 enemies immediately (Tick fallback)` 有关 — GameMode 的 BeginPlay 流程没走完)
- 任何 `SetGamePaused(true)` 之后,world tick 完全冻结,包括已 set 但未 fire 的 timer

## 解决
改用 `FTSTicker::GetCoreTicker().AddTicker(...)`:
- **进程级 ticker**,不依赖 World 状态
- 暂停/世界切换/PIE 边界都稳定 fire
- 一次性 ticker:lambda 返回 `false` 自动注销
- `TWeakObjectPtr<UObject>` 防 GC

## 代码模式
```cpp
// ❌ 旧:World TimerManager — PIE 边界 fire 失败
FTimerHandle TimerHandle;
GetWorld()->GetTimerManager().SetTimer(TimerHandle, FTimerDelegate::CreateLambda([this]() { ... }), 1.0f, false);

// ✅ 新:FTSTicker — 进程级稳定
TWeakObjectPtr<UWebUIBase> WeakThis(this);
FTSTicker::GetCoreTicker().AddTicker(
 FTickerDelegate::CreateLambda([WeakThis](float DeltaTime) -> bool {
 if (UWebUIBase* Self = WeakThis.Get()) {
 Self->bJavaScriptReady = true;
 }
 return false; // 一次性
 }), 1.0f);
```

## 适用范围
- **WebUI/UMG widget 的延迟回调** — WebUIBase CEF 3.5s 初始化,SetVisibility/JS ready 全部 FTSTicker
- **跨 World 边界的临时延迟** — LevelUp 4s 弹卡,PIE world 边界 timer 不可靠
- **需要在 SetGamePaused 期间也 fire 的 timer** — 例如暂停时弹菜单的延迟
- **UI 一次性回调** — 任何"X 秒后调一次"场景

## 不适用
- **需要每帧 Tick 的组件** — 用 `UActorComponent::TickComponent` 或 `FTickableGameObject`
- **GameMode 内的 tick** — 用 World TimerManager(它跟 world tick 同步,GameMode 切关卡不影响)
- **跨多个 PIE 实例的同步** — FTSTicker 是进程级,多个 PIE 会共享

## 关联
- [[levelup-choice-v1-2026-06-22]] — LevelUp Choice v1.0 端到端用了这个 fix
- [[llmshell-restart-hang-v2-fix-2026-06-21]] — Editor 启动用 WaitForEditorResult 替代阻塞的 loop

**Why**:World TimerManager 在 PIE 启动异步流程下 timer 不 fire 是常见坑,FTSTicker 是更稳健的替代,任何"延迟 N 秒做 X" 的 UI 流程都该用 FTSTicker 而非 World TimerManager。
