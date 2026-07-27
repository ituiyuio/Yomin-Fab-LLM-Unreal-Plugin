---
name: llmdynamicui-parentclass-pattern
description: LLMDynamicUI .llmui文件使用C++ WidgetBase类作为父类的正确方法
type: reference
originSessionId: 86448bd0-54c7-4ad6-a568-df049ba83e41
---
# LLMDynamicUI parentClass 模式

## 问题
WBP_Shop.llmui 生成 Blueprint 时未正确继承 `ShopWidgetBase`，导致按钮事件无法通过 C++ NativeConstruct 绑定。

## 原因
LLMDynamicUI 的 LLMUMGGenerator 在 .llmui 文件缺少 `parentClass` 字段时，默认使用 `UUserWidget` 作为父类。

## 解决方法
在 .llmui 文件根级别添加：
```json
{
 "version": "2.0",
 "name": "WBP_Shop",
 "parentClass": "ShopWidgetBase",
 "rootWidget": { ... }
}
```

## parentClass 解析机制（LLMUMGGenerator::ResolveParentClass）

实际生产代码 `Plugins/LLMDynamicUI/Source/LLMDynamicUIEditor/Private/Parser/LLMUMGGenerator.cpp:534-629`（**当前实现**，可能比早期版本多了 CommonUI + Config 路径 + IsChildOf 验证三层）：

1. **默认** — `UUserWidget::StaticClass()`（兜底）
2. **优先级** — `Doc->ParentClass` > `CurrentConfig.bUseCommonUI`（Config 开关在 .llmui 缺 `parentClass` 字段时启用 CommonUI 路径）
3. **空 / "UserWidget"（大小写不敏感）** — 直接返回 UUserWidget 默认，不进 lookup
4. **CommonUI 类型**（StaticClass 直接映射，无需 FindObject 全局搜）：
 - `CommonActivatableWidget` → `UCommonActivatableWidget::StaticClass()`
 - `CommonUserWidget` → `FindObject<UClass>(nullptr, FLLMScriptPaths::CommonUserWidget)`（模块找不到时 fallback 到 UUserWidget + warning）
5. **完整路径** (`/Game/...` 或 `FLLMScriptPaths::GamePath` 开头) — `LoadObject<UClass>` + **`IsChildOf(UUserWidget)` 验证**（非 UUserWidget 子类 fallback warning，避免把非 widget 类当 parent）
6. **简单名查找**（3 策略 + IsChildOf 验证）：
 - `/Script/CODEO.ClassName`（CODEO 模块 C++ 类）
 - `ClassName_C`（Blueprint 生成类后缀）
 - `ClassName`（`FindObject<UClass>` 直接查找）
 - 全部需通过 `IsChildOf(UUserWidget)` 验证，否则 fallback
7. **未找到** — `UE_LOG(Warning, "Could not resolve parent class '%s', using UserWidget")` + 返回 UUserWidget

**note:** 当前实现里只有 `/Script/CODEO.` 路径会查 CODEO 模块 C++ 类（跟早期版本默认所有 C++ 都查的"通用 lib path"不同）。如果自定义 widget 基类不在 CODEO 模块，用 `/Game/...` 完整路径而不是 `ShopWidgetBase` 简单名。

## C++ WidgetBase 设计要点
- 使用 `FindButton(FName)` 在 `NativeConstruct()` 中动态查找按钮（无需 BindWidget）
- 使用 `BlueprintImplementableEvent` 定义事件（可被子类 Override）
- 按钮 OnClicked 绑定到 HandleItemNClicked()
- HandleItemNClicked() 调用 PurchaseItem(N) 和 OnBuyN()

## 验证方法
```
discover /Game/Features/Survivor/HUD/WBP_Shop
# classHierarchy 应包含 ShopWidgetBase
```
