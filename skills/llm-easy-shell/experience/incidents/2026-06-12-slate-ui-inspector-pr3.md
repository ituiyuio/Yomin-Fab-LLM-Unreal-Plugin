---
name: 2026-06-12-slate-ui-inspector-pr3
description: "LLMEasyShell ui press/type/tick PR3 落地 (2 commits on top of PR2), FUIInteractor 走 FSlateApplication::Process*Event (5.7 实际签名用 FKeyEvent/FPointerEvent 构造器)"
metadata:
 node_type: memory
 type: project
 originSessionId: 7b661671-8cab-45c8-a837-84138c692c7e
---

# 落地

PR3 加 3 个操作命令:
- `ui press mouse|key` (调 FUIInteractor::PressMouse / PressKey, 走 FSlateApplication::ProcessMouseButtonDownEvent/Up 或 ProcessKeyDownEvent/Up)
- `ui type` (focus + 逐字符 ProcessKeyDownEvent/Up)
- `ui tick` (polling 调用 FUIInspector::Find 直到匹配或 timeout)

总计 7 spec 命令全部 wired (dump + find + info + shot + press + type + tick).

# Why
- PR1+PR2 给了"看"能力 (dump/find/info/shot), PR3 补"操作"能力 (press/type/tick)
- spec §1 整体目标是 "ui 7 命令族", 缺了 operate 这 3 个就不完整

# How to apply
- **5.7 FSlateApplication 实际签名** (PR3 实施验证):
 - `ProcessKeyDownEvent(const FKeyEvent&)` — 单参 FKeyEvent
 - `ProcessMouseButtonDownEvent(const TSharedPtr<FGenericWindow>&, const FPointerEvent&)` — 双参 (NativeWindow + PointerEvent)
 - **plan 写错了**, plan 写的是 `(Key, Char, Code, bIsRepeat, FWidgetPath)`, 实际是 FKeyEvent/FPointerEvent 构造器
 - 参考 `WidgetInteractionComponent.cpp:439-651` canonical pattern 验证
- **构造 FKeyEvent**: `FKeyEvent(Key, ModKeys, UserIndex, bIsRepeat, CharCode, KeyCode)` (Events.h:447)
- **构造 FPointerEvent**: `FPointerEvent(UserIndex, PointerIndex, ScreenPos, LastScreenPos, PressedKeys, EffectingKey, WheelDelta, ModKeys)` (Events.h:746)
- **副作用**: `SetCursorPos` 真移动 OS 光标 (visible), 但不调 `IAutomationDriverModule::Enable()` 所以不拦截真实输入
- **错误路径**: UIInteractor 返 raw `FUIServiceResult`, UIErrorMapping 共享 header (PR2 提取) 负责 `EUIErrorCode → EShellErrorCode` 映射

# Known limitations (PR3 末)
- `Modifiers` 字段在 FUIPressMouseOptions/KeyOptions 留了但未解析 (UIInteractor 不用, shell command 也不解析 — TODO future)
- `SetUserFocus(0, ...)` 硬编码 UserIndex 0 — 假设单用户 PIE (multi-user 场景 out of scope)
- 5.7 没有 LoadState UPROPERTY on UWebBrowser, `ui info --path ...WebBrowser` 只能暴露 url+title+page_loaded proxy
- Full `Build.bat` link 验证仍未跑 (editor + Live Coding 锁住, 需 user 手动关 editor 跑 build 链路收尾)
- 3 bug-regression scripts + PIE end-to-end 全都没真跑过 (env 阻塞, Step 1 实测 build failed at UBT stage)

# Verification (PR3 done)
- 24 commits on master (PR1 15 + PR2 7 + PR3 2)
- 7 shell 命令 wired + registered (dump/find/info/shot/press/type/tick)
- 4 service 类 (UIServiceErrors / UIErrorMapping / UIInspector / UIInteractor) 协议完整
- 3 真 bug 的可观测性: z-order (ui find), WebBrowser CEF (ui info cef_state), GameOver 风暴 (ui find count)
- 3 bug-regression scripts 准备就绪 (待 editor restart 实跑)
- L0 test (PathParser::Tokenize) 编译 + linked
- PIE smoke test 编译成功, runtime 待 user 验证
