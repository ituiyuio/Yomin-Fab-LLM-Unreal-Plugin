# LLMEasyShell 内置 Shell 命令经验

> 6 个教训：路径解析 / 参数解析 / 输入格式 / Blueprint reparent / FObjectProperty 反射

---

## 教训 1：Actor 标签含 `/` 时 rm/cp/mv 必须用 `Parts.Last()` 而非 `Parts[1]`

**场景**：`rm /Actor/LG_VisionOS` 失败，找不到 Actor。

**根因**：原代码用 `Parts[1]` 提取 actor label（假定固定格式 `/Actor/{label}`）。当 label 本身含 `/` 时（如 `LG_VisionOS` 实际存储为 `LG/Glass/VisionOS`），`Parts[1]` 只能拿到 `LG`，label 截断。

**修复模式**：

```cpp
// ShellCommand_Rm/Cp/Mv.cpp
FString Label = Parts.Last();  // ✅ 不是 Parts[1]
// wild card 匹配从 StartsWith 改 Contains
// 单 actor 删除加 EndsWith 检查
```

**文件**：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_Rm.cpp` / `_Cp.cpp` / `_Mv.cpp`

**经验**：任何解析 `/Type/{rest}` 路径的命令，只要 `{rest}` 部分可能含 `/`（actor label、文件路径、nested struct key），必须用 `Parts.Last()` 而非固定下标。

---

## 教训 2：`new` 命令 `--key=value` 解析崩溃（**已修复** 2026-05-08 后）

**历史场景**：`new /Game/Features/Survivor/BP_SurvivorProjectile --class=SurvivorProjectile` 触发 `Assertion failed` 在 `UObjectGlobals.cpp`。

**历史根因**：`ShellCommand_New.cpp` 旧版解析 `--key=value` 参数失败，错误地把 `--class=...` 拼接到路径，生成双斜杠路径 `PackageName: /Game/ParentClass=SurvivorProjectile//Game/Features/.../BP_SurvivorProjectile`。

**当前实现**（`ShellCommand_New.cpp:140-180`，已支持 `--key value` 形式）：

```cpp
// Parse options - 支持 --parent / --path / --struct 等
for (int32 i = 2; i < Args.Num(); i++) {
    if (Args[i].StartsWith(TEXT("--"))) {
        FString OptionName = Args[i].RightChop(2);
        if (i + 1 < Args.Num() && !Args[i + 1].StartsWith(TEXT("--"))) {
            Options.Add(OptionName, Args[++i]);
        } else {
            Options.Add(OptionName, TEXT("true"));
        }
    }
    else if (AssetPath.IsEmpty()) {
        // Positional path argument - normalize same as --path
        ...
    }
}
```

**当前用法**（可直接用）：
```bash
new WidgetBlueprint MyWidget --parent UserWidget
new Blueprint MyActor /Game/Blueprints
new DataTable MyTable --struct MyRowStruct
```

**经验**：写新 `--key value` 解析时参考 `HandleCreateAsset` 的实现（i+1 提前消费 + StartsWith 双连字符判断）。这个教训作为反面教材保留，提醒未来不要写直接拼路径的解析器。

---

## 教训 3：Windows bash 下 stdin pipe 和 `-c` flag 同时存在时优先 stdin

**场景**：在 Windows bash 用 `echo 'info' | llm-shell.exe -c "ls /Level/Actors"` 只执行了 stdin 的命令。

**根因**：原 main.cpp 不检测 stdin，只看 `-c` 参数。在 Windows bash 下 `echo ... |` 会把 stdin 接到 handle，但 bash 自己又把 `-c` 参数传过去，行为不确定。

**修复模式**（`main.cpp`）：

```cpp
// Windows bash 兼容性：检测 stdin 是否有数据
DWORD stdinMode;
HANDLE stdinHandle = GetStdHandle(STD_INPUT_HANDLE);
bool hasStdinData = (stdinHandle != INVALID_HANDLE_VALUE) &&
                    (stdinHandle != NULL) &&
                    !GetConsoleMode(stdinHandle, &stdinMode);
if (hasStdinData && singleCommand) {
    singleCommand = false;  // 优先用 stdin
    command.clear();
}
```

**经验**：CLI 入口检测要兼容 Unix-style pipe（stdin 检测）。三种方式都正常：
- `echo 'info' | shell.exe`
- `shell.exe -c "info"`
- `echo 'info' | shell.exe -c "info"` ← stdin 优先

---

## 教训 4：`set Blueprint.ParentClass` 之前 FindClassByName 过滤掉非 Actor 类

**场景**：`set /Game/Path/BP_Shop.ParentClass ShopWidgetBase` 失败，但 `ShopWidgetBase` 是合法的 `UUserWidget` 子类。

**根因**：`ShellCommand_Set::SetBlueprintParentClass()` 里的 `FindClassByName()` 只搜 Actor 类。

**修复模式**（`ShellCommand_Set.cpp`）：

```cpp
// 1. 先尝试直接类路径
UClass* NewParentClass = UClass::TryFindTypeSlow<UClass>(FullClassPath, EFindFirstObjectOptions::None);
// 2. 回退到 FindClassByName（只 Actor）
if (!NewParentClass) NewParentClass = FLLMEasyShellReflection::FindClassByName(ClassNameToFind);
// 3. 再回退到剥模块前缀的名字
if (!NewParentClass) NewParentClass = UClass::TryFindTypeSlow<UClass>(ClassNameToFind, EFindFirstObjectOptions::None);
```

**经验**：reparent 场景一定要支持 UMG、GameMode、Subsystem 等**非 Actor** 类。`TryFindTypeSlow` 是万能回退。

---

## 教训 5：FObjectProperty 设值前必须 `!IsA<UClass>()` 校验

**场景**：通过 `/Script/LiquidGlass3D.LiquidGlassComponent'...'` 路径反序列化 `FObjectProperty` 时编辑器崩溃，断言 `ObjectA == nullptr || ObjectA.IsA<UClass>()` 在 `PropertyClass.cpp:201`。

**根因**：`LLMEasyShellReflection::DeserializeProperty()` 用 `LoadAssetByPath` 加载资产时，路径带 `'...'` 外层引用语法时，**返回值可能是 `UClass*` 而不是 `UObject*` 实例**。然后 `SetObjectPropertyValue_InContainer(Container, UClass*)` 触发 UE 断言。

**修复模式**（`LLMEasyShellReflection.cpp:399-435`）：

```cpp
// 所有 SetObjectPropertyValue_InContainer 调用前
if (Asset && !Asset->IsA<UClass>()) {
    ObjProp->SetObjectPropertyValue_InContainer(Container, Asset);
}
// None / nullptr 走单独分支清空
if (!Asset) { /* clear */ }
```

**经验**：序列化 `FObjectProperty` 时，路径 `'Class'path'` 形式可能解析成 `UClass`（CDO）。永远要 `!IsA<UClass>()` 防御。

---

## 教训 6：连接失败时扫描端口显示可用编辑器

**场景**：连不上默认 15151 端口时，用户不知道有别的编辑器实例。

**根因**：LLMEasyShell 默认端口 15151，多编辑器（PIE/单独 editor 进程）会占用 15151-15160。

**修复模式**（`main.cpp`）：`ScanForAvailablePorts()` 扫描所有端口发 `info` 命令，输出：

```
Available instances:
  o Port 15154: JKP (Editor: Idle)
```

**经验**：连不上时 CLI 应该显示其他可用实例，而不是直接报错。

---

## 相关文件

- `ShellCommand_Rm.cpp` / `_Cp.cpp` / `_Mv.cpp` — 教训 1
- `ShellCommand_New.cpp` — 教训 2
- `main.cpp` — 教训 3, 6
- `ShellCommand_Set.cpp` — 教训 4, 5
- `LLMEasyShellReflection.cpp:399-435` — 教训 5
