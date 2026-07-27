---
name: ue-userwidget-rebuildwidget-timing
description: UUserWidget::RebuildWidget runs BEFORE NativeConstruct during AddToViewport — building widget tree in NativeConstruct causes SObjectWidget to wrap SSpacer and the widget renders at 0×0
metadata: 
 node_type: memory
 type: feedback
 originSessionId: f720a8ba-e3d4-452f-9d12-10c0d8e2f169
---

UUserWidget 的 widget tree 必须在 `RebuildWidget` 中构建（idempotent），**不能**放在 `NativeConstruct` 中。

**Why:** 调用链是 `CreateWidget → Initialize → AddToViewport → UGameViewportSubsystem::AddWidget → Widget->TakeWidget → UWidget::TakeWidget_Private → UUserWidget::RebuildWidget → WidgetTree->RootWidget->TakeWidget()`。如果此时 `RootWidget == null`，`UUserWidget::RebuildWidget` 会回退到 `SNew(SSpacer)`（UserWidget.cpp:1203），然后用 SObjectWidget 包装这个 SSpacer。`NativeConstruct` 之后才被调用（OnWidgetRebuilt 路径，UserWidget.cpp:1223），但此时 SObjectWidget 已经定型，**在 NativeConstruct 里改 WidgetTree 不会被 Slate 看到**——整个 widget chain 永远渲染为 0×0。这是 WebBrowser HUD、Shop、GameOver 一律不显示的根因。

**How to apply:** 程序化构建 UUserWidget（无 Blueprint 默认 RootWidget）时，重写 `RebuildWidget()` 并在 `Super::RebuildWidget()` 之前调用 `EnsureWidgetTreeBuilt()`，并保证 idempotent（用 `if (WidgetTree->RootWidget) return;` 短路）。`NativeConstruct` 只做不需要在 Slate 创建前发生的逻辑（绑定事件、LoadHtmlFile 等）。同样的模式适用于所有 C++ only 的 UUserWidget 子类。
