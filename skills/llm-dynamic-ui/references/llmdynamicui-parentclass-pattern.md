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
LLMDynamicUI 的 LLMUMGGenerator 在 .llmui 文件缺少 `parentClass` 字段时，默认使用 `UUserWidget` 作为父类。插件**不自带任何基类** —— 不存在"必须继承插件提供的基类"的前提。

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

生产代码：`Plugins/LLMDynamicUI/Source/LLMDynamicUIEditor/Private/Parser/LLMUMGGenerator.cpp`（`ResolveParentClass`）。解析顺序：

1. **默认** — `UUserWidget::StaticClass()`（兜底）
2. **优先级** — `Doc->ParentClass` > `CurrentConfig.bUseCommonUI`（Config 开关在 .llmui 缺 `parentClass` 字段时启用 CommonUI 路径）
3. **空 / "UserWidget"（大小写不敏感）** — 直接返回 UUserWidget 默认，不进 lookup
4. **CommonUI 类型**（StaticClass 直接映射，无需 FindObject 全局搜）：
   - `CommonActivatableWidget` → `UCommonActivatableWidget::StaticClass()`
   - `CommonUserWidget` → `FindObject<UClass>(nullptr, FLLMScriptPaths::CommonUserWidget)`（模块找不到时 fallback 到 UUserWidget + warning）
5. **完整路径** — `LoadObject<UClass>` + **`IsChildOf(UUserWidget)` 验证**（非 UUserWidget 子类 fallback warning，避免把非 widget 类当 parent）：
   - `/Game/...` — 蓝图资产路径
   - `/Script/<Module>.<Class>` — **任意模块**的 C++ 类，通用形式（与具体项目无关）
6. **简单类名**（内存查找 + `IsChildOf(UUserWidget)` 验证）：
   - 先查**运行时父类注册表** `ULLMParentClassRegistry::ResolveClass`（`Source/LLMDynamicUI/Public/Core/LLMParentClassRegistry.h`），注册表内部顺序是：
     1. 精确别名表（`RegisterAlias("ShopWidgetBase", "/Script/<Module>.ShopWidgetBase")`）
     2. 已注册的脚本模块，逐个拼成 `/Script/<Module>.<Name>` 查找
   - 再回退 `ClassName_C`（Blueprint 生成类后缀）
   - 再回退 `ClassName`（`FindObject<UClass>` 直接查找）
   - 全部需通过 `IsChildOf(UUserWidget)` 验证，否则 fallback
7. **未找到** — `UE_LOG(Warning, "Could not resolve parent class '%s', using UserWidget")` + 返回 UUserWidget

**通用插件 vs 项目专属**：简单名 → 模块的映射走**运行时注册表**，不是通用插件里的硬编码路径。注册由宿主项目插件（`Plugins/LLMSurvivorShell/`，**项目专属、不随 Fab 分发**）在启动时完成 —— 通过反射调用 `/Script/LLMDynamicUI.LLMParentClassRegistry` 的 `RegisterScriptModule("CODEO")` / `RegisterAlias(...)`，因此项目插件对通用插件**没有编译期依赖**。通用插件 `Plugins/LLMDynamicUI/` 只提供**解析机制**，**不含任何项目专属映射**。当插件尚未提供该注册时，简单名回退到 `ClassName_C` / `ClassName` 的内存查找（蓝图生成类 / 已加载的 C++ 类）。

**跨项目用法（Fab 包买家）**：自己的 C++ 基类建议写完整路径 `/Script/<你的模块名>.<ClassName>`，与任何项目注册表无关；简单名只在注册过的项目里可靠。

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
