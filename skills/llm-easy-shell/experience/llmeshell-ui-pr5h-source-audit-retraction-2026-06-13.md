---
name: llmeshell-ui-pr5h-source-audit-retraction-2026-06-13
description: "2026-06-13 凌晨用户挑战 \"确定吗\" 触发 UE 5.7 源码深挖,**收回 PR5.E \"真闭环 verified\" 假声明** + 加 PR5.H 真严格 gate + dispatch check"
metadata: 
 node_type: memory
 type: project
 originSessionId: 0cb751d5-ed36-45c0-8c8f-88328bb712d7
---

# llmeshell-ui PR5.H: source-audit retraction + 真严格修复 (2026-06-13)

接 [[llmeshell-ui-pr5-end-to-end-2026-06-13]] 之后,**用户挑战"确定吗,要不要调查一下源码"** 触发 3 并行 Explore agent 深挖 UE 5.7 引擎源,发现 PR5.D-E 链条上至少 4 个深层 bug + 之前"95% verified"实际是假阳性。

## 用户挑战的核心价值

**没用户那一句"确定吗",我会一直把"PIE press 闭环 verified"当真**。这次得到的教训:
> `success: true` 不证明"点中了",只证明"没 crash + 路径解析完成"。LLM-friendly success 必须基于**真实 dispatch 后状态**,不是 cosmetic 设的。

## Explore agent 揭示的源码真相

### 1. `FSlateApplication::ProcessMouseButtonDownEvent` 重做 hit test,我传的 args 失效
- `SlateApplication.cpp:5283` 硬覆盖 `bIgnoreEnabledStatus=false` 且自己 `LocateWindowUnderMouse(Center, GetInteractiveTopLevelWindows(), false, ...)` —— 我传的 `{Window}` arg **完全没用**
- 真 hit test 跨**所有** interactive top-level window (PIE SWindow + editor LevelEditor SWindow + outliner + details + content browser + tool windows),按 z-order 找第一个匹配
- → 我的 `ui press` 实际可能点中 editor 主窗口的某个 widget,不是 PIE 的 WebBrowserHUDWidget

### 2. ESlateVisibility hit-test 真规则(UE 5.7 头文件 + paint + grid 三层证据链)
| 名称 | bit | IsHitTestVisible | AreChildrenHitTestVisible | 在 hit-test grid 里? |
|---|---|---|---|---|
| Visible | 25 | yes | yes | self + children 都进 |
| Collapsed | 2 | **no** | **no** | self 跳 + children 全跳 |
| Hidden | 4 | **no** | **no** | self 跳 + children 全跳 |
| **HitTestInvisible** | 1 | **no** | **no** | **self 跳 + children 全跳** (关键!) |
| SelfHitTestInvisible | 17 | **no** | yes | self 跳但 children 仍可进 |

源码: `SWidget.cpp:1449-1508` (Paint 阶段 `bOutgoingHittestability = bInheritedHittestability && AreChildrenHitTestVisible()`,false 后**所有 descendants 同样 false**) + `HittestGrid.cpp:814-820` (`!IsHitTestVisible()` 早 return)

WebBrowserHUDWidget 是 `HitTestInvisible`(从 dump 看到)→ self + children 全部不在 hit-test grid → Slate 在 (1923, 1046) 找不到任何 UMG widget → **click 静默 drop**,但我返回 success。

### 3. (1923, 1046) 是 desktop-absolute,PIE viewport 只有 1521×933
- `LocalToAbsolute` 把 widget 局部坐标变换到 root SWindow 空间(desktop-absolute,Geometry.h:439-449 注释)
- `GetCachedWidget()` 对 UUserWidget **优先返回 MyGCWidget (SObjectWidget 包整个 widget)**,不是子 leaf widget
- `LocalToAbsolute(Size*0.5)` 算的是**整个 root UserWidget 的中心**,1761×1080 中心 = (1162.5+880, 579.5+540) ≈ (2043, 1119) — 跟 (1923, 1046) 大致一致但**已超出 PIE viewport 1521×933 边界**
- 该坐标可能在 PIE SWindow chrome (title bar / border) 上,或在桌面上 PIE 窗口之外区域

### 4. `ui tick` GT sleep 死锁 verified
- `FPlatformProcess::Sleep` (`WindowsPlatformProcess.cpp:1855-1873`) → Win32 `::Sleep(ms)`,只挂当前线程
- 但当前线程是 game thread,`FEngineLoop::Tick`(`LaunchEngineLoop.cpp:5822`) 完全停摆 → `UWorld::Tick`(`LevelTick.cpp:1477`) 不 run → 任何 actor `Tick` 里 `CreateWidget+AddToViewport` 的 widget 永远不出现
- `UWidget::SetVisibility`(`Widget.cpp:417-441`)/`UUserWidget::AddToViewport`(`UserWidget.cpp:1355-1367`)**都是同步**(没 deferred / next-tick queue),所以 `BeginPlay`/构造期就 spawn 的 widget OK,但需要游戏推进才出现的 widget 100% timeout

## PR5.H 实施

UIInteractor.cpp:
1. **visibility gate 收紧**: `Visible | SelfHitTestInvisible only`,拒 `HitTestInvisible | Hidden | Collapsed`。HitTestInvisible 错误带 engine 源引用 hint: "Widget AND all descendants skip Slate hit-test grid (UE 5.7 HittestGrid.cpp:814)"
2. **GlobalHit dispatch check**: 在 `ProcessMouseButton*Event` 调用**之前**,自己 mirror `SlateApplication.cpp:5283` 的 `LocateWindowUnderMouse(Center, GetInteractiveTopLevelWindows(), false)`,扫描 GlobalHit.Widgets 看 target SW 是否在 path 里
3. **Success JSON 加 `hit_leaf_type` + `hit_path_depth`**: LLM 看到 click 真实命中的 widget type / hit-test path 深度
4. **Fail with concrete reason** when leaf 不匹配: `"click at (X, Y) would land on '<leaf>', not the requested widget"`

UI.aia 修订:
- PR5.E **明确标 [RETRACTED]** + 解释为什么之前 verified 是错的
- PR5.G 死锁状态从 "未 verified 潜在 bug" 改成 "verified by source audit"
- PR5.H 新增,记录真严格版

## PIE verify (2026-06-13 01:14)

```
ui press mouse --path / # WebBrowserHUDWidget (HitTestInvisible)
→ {
 "success": false,
 "error_obj": {
 "error": "not_visible",
 "message": "widget '/' not hit-testable (vis=3, HitTestInvisible)",
 "hint": "Widget AND all descendants skip Slate hit-test grid (UE 5.7 HittestGrid.cpp:814). 
 Click is silently dropped. Use a child path that resolves under a 
 Visible/SelfHitTestInvisible ancestor."
 }
}
```

之前(PR5.E): false success 不报错
现在(PR5.H): false 报真错误 + engine 源码引用 + 教育性 hint

## 启示

1. **"成功"判定必须基于真 dispatch state,不能 cosmetic**。LLM 一拿 success 就不会再 query,假 success 浪费整条 reasoning chain
2. **用户的"确定吗"是无价的**。我倾向 over-claim verified,源码挖才能暴露盲区
3. **UE Slate hit-test rule 是非平凡的** — `HitTestInvisible` 跟 `SelfHitTestInvisible` 一字之差但后果天壤(self+children 全跳 vs 只 self 跳)
4. **ESlateVisibility 5 态是 bool 信息丢失的根本原因**,LLM 需要 enum 字符串才能正确推理

## 相关 memory + 引用源行号

- [[llmeshell-ui-pr5-end-to-end-2026-06-13]] — 被本文件收回的"假 verified" 上一版
- [[llmeshell-ui-pr5-runtime-verification-2026-06-12]] — PR5 之前 PR1-4 runtime verify
- [[feedback-question-tools-and-have-agency]] — 用户偏好"质疑工具,多做独立思考";本次"确定吗"是经典示例
- [[ue-webbrowser-pause-timer-deadlock]] — WebBrowser HUD PIE 早期渲染

UE 5.7 源码定位:
- `Runtime/Slate/Private/Framework/Application/SlateApplication.cpp:5283` — ProcessMouseButtonDownEvent 重做 LocateWindowUnderMouse
- `Runtime/SlateCore/Private/Widgets/SWidget.cpp:1449-1508` — Paint 阶段 bOutgoingHittestability 传播
- `Runtime/SlateCore/Private/Input/HittestGrid.cpp:814-820` — AddWidget early-out on !IsHitTestVisible()
- `Runtime/UMG/Public/Components/SlateWrapperTypes.h:21-33` — ESlateVisibility 5 个值
- `Runtime/SlateCore/Public/Layout/Visibility.h:56-64,80-108` — IsHitTestVisible/AreChildrenHitTestVisible bit 实现
- `Runtime/Core/Private/Windows/WindowsPlatformProcess.cpp:1855-1873` — FPlatformProcess::Sleep
- `Runtime/Launch/Private/LaunchEngineLoop.cpp:5822` — FEngineLoop::Tick 调用 GEngine->Tick
- `Runtime/UMG/Private/Components/Widget.cpp:417-441` — UWidget::SetVisibility 同步
- `Runtime/UMG/Private/UserWidget.cpp:1355-1367` — UUserWidget::AddToViewport 同步
