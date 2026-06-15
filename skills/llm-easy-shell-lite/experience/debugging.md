# LLMEasyShellLite Debugging Guide

> 基于 2026-04-19 实战经验凝练：Lite 只读命令的 bug 根因分析和修复模式。
> Lite 共享 full 的 CommandDispatcher / 反射实现，所以 full 的踩坑经验同样适用。

---

## 关键教训

### 教训 1：Shell 命令的路径前缀与类型标识容易混淆

**场景**：`find /Game LiquidGlass` → `"Unknown type: /Game"`

**根因**：LLM 倾向于使用类 shell 的路径格式（如 `/Game`、`/Assets`）作为类型前缀，但命令解析器期望的是纯文本类型名（如 `Asset`）。ExecuteNative() 的参数数组中，Args[0] 被当作 "Type"，当值为 `/Game` 时：

1. 不匹配 `Type == "/"`（旧兼容逻辑）
2. 也不是 `Actor` 或 `Asset`
3. 进入 else 分支报错

**修复模式**：
```cpp
// 在所有类型判断之前，对以 "/" 开头的 Args[0] 做兜底处理
if (Type.StartsWith(TEXT("/")) && Args.Num() >= 2)
{
    return FindAssetsInPath(Type, Args[1]);  // Type=路径，Args[1]=pattern
}
```

**经验**：任何接受 `find <type> <pattern>` 格式的命令，都应对以 `/` 开头的第一个参数做路径解析兜底。

---

### 教训 2：Reflection UI 层必须显式调用 SerializeProperty

**场景**：`cat /Actor/LG_Static/LiquidGlass` 只显示属性名/类型，不显示 Config struct 的值

**根因**：ShowComponent() 遍历了所有 BlueprintVisible 属性，但只打印了名称和类型，没有调用 `GetPropertyValue()`。而 `ExportTextItem_InContainer` 已经在 SerializeProperty 中正确处理了 struct 序列化（输出格式为 `(field1=val1,field2=val2)`），只是没有调用它。

**修复模式**：
```cpp
// 对每个 BlueprintVisible 属性，调用 Reflection 系统获取值
TArray<FProperty*> Properties;
for (TFieldIterator<FProperty> It(Component->GetClass()); It; ++It)
{
    FProperty* Prop = *It;
    if (Prop && (Prop->HasAnyPropertyFlags(CPF_Edit | CPF_BlueprintVisible)))
    {
        Properties.Add(Prop);
    }
}

for (FProperty* Prop : Properties)
{
    // 获取当前值
    FString PropValue = FLLMEasyShellReflection::GetPropertyValue(Component, PropName);

    // struct 属性输出格式为 "(...)"，可直接作为 JSON 值嵌入
    // 普通值需要加引号
    if (PropValue.StartsWith(TEXT("(")) || PropValue.StartsWith(TEXT("{")))
    {
        SerializedValue = PropValue;  // 结构体，不加引号
    }
    else
    {
        SerializedValue = FString::Printf(TEXT("\"%s\""), *PropValue);
    }
}
```

**经验**：Reflection 系统的 `SerializeProperty → ExportTextItem_InContainer` 已经能正确处理所有 UPROPERTY 类型，包括嵌套 struct。UI 层只需调用 `GetPropertyValue()` 即可获得完整值。

---

## 调试流程

### 1. 症状观察
- 命令返回意外结果（如错误消息、空白输出）
- 与预期行为不符

### 2. 信息收集
```bash
# 先确认编辑器状态
info

# 查看可用函数/属性
discover /Actor/{name}/Component --funcs

# 查看组件完整属性（含值）
cat /Actor/{name}/Component

# 查看日志
log --lines 50
```

### 3. 源码定位
关键文件：
- 命令实现：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/ShellCommand_*.cpp`
- Reflection 系统：`Plugins/LLMEasyShell/Source/LLMEasyShell/Private/LLMEasyShellReflection.cpp`
- 类型定义：`Plugins/LLMEasyShell/Source/LLMEasyShell/Public/LLMEasyShellTypes.h`

### 4. 修复策略
| 问题类型 | 修复位置 | 热重载 |
|---------|---------|--------|
| 命令解析逻辑错误 | ShellCommand_*.cpp | `livecoding` |
| Reflection 值获取/序列化 | LLMEasyShellReflection.cpp | `livecoding` |
| 新增函数声明 | LLMEasyShellTypes.h | `restart` |

### 5. 验证
```bash
# 修复后重新执行命令
livecoding  # 等待编译完成
cat /Actor/LG_Static/LiquidGlass  # 验证输出
```

---

## 代码模式

### 模式 1：支持路径前缀的参数解析
```cpp
// 在 ExecuteNative() 中，所有类型判断之前插入
FString Type = Args[0];
FString Pattern = Args[1];

// 路径前缀兜底（支持 /Game, /Assets 等）
if (Type.StartsWith(TEXT("/")) && Args.Num() >= 2)
{
    return FindAssetsInPath(Type, Pattern);
}
```

### 模式 2：显示组件完整属性值
```cpp
// 在 ShowComponent() 中，遍历所有 BlueprintVisible 属性并获取值
TArray<FProperty*> Properties;
for (TFieldIterator<FProperty> It(Component->GetClass()); It; ++It)
{
    FProperty* Prop = *It;
    if (Prop && (Prop->HasAnyPropertyFlags(CPF_Edit | CPF_BlueprintVisible)))
    {
        Properties.Add(Prop);
    }
}

for (FProperty* Prop : Properties)
{
    FString PropName = Prop->GetName();
    FString PropValue = FLLMEasyShellReflection::GetPropertyValue(Component, PropName);
    // PropValue 已由 ExportTextItem 处理
    // struct: "(...)" | 普通值: "value"
}
```

### 模式 3：UE Property 遍历过滤
```cpp
// 正确过滤 BlueprintVisible 属性
if (Prop && (Prop->HasAnyPropertyFlags(CPF_Edit | CPF_BlueprintVisible)))

// 排除内部生成的属性（_GEN_VAR 等）
FString CleanName = Prop->GetName().Replace(TEXT("_GEN__"), TEXT(""));
```

### 模式 4：JSON 序列化 struct 值
```cpp
// UE ExportTextItem 输出格式为 "(...)"，直接作为 JSON 值
if (PropValue.StartsWith(TEXT("(")) || PropValue.StartsWith(TEXT("{")))
{
    Output += FString::Printf(TEXT("    \"%s\": %s"), *PropName, *PropValue);
}
else
{
    Output += FString::Printf(TEXT("    \"%s\": \"%s\""), *PropName, *PropValue);
}
```

---

## 教训 3：Python Ability 命令分发与 `unreal` 模块属性名

**场景**：`python hd3d_pp add_all` 返回 `{"success": false, "error": ""}`，但 `python test_apply test` 正常返回结果

**根因分析**：
1. **类名大小写**：`unreal.ULLMEasyShellMaterialLibrary` 是错误的，应为 `unreal.LLMEasyShellMaterialLibrary`（无 `ULL` 前缀）
2. **Python Ability 命令分发机制**：Python abilities 使用类名作为命令名，但 `test_apply test` 能工作而 `hd3d_pp add_all` 不能，表现出"偶发性"——重启编辑器后行为一致，表明存在未清除的状态问题

**修复模式**：
```python
# 错误 ❌
unreal.ULLMEasyShellMaterialLibrary.apply_post_process_material(...)

# 正确 ✅
unreal.LLMEasyShellMaterialLibrary.apply_post_process_material(...)

# 或使用 getattr 方式（更安全）
func = getattr(unreal.LLMEasyShellMaterialLibrary, 'apply_post_process_material', None)
if func:
    func("PostProcessVolume0", mat_path, 1.0)
```

**调试方法**：
```bash
# TCP 直接测试（比 CLI 可靠）
# 1. 确认编辑器运行
info

# 2. 测试 Python ability（通过 TCP）
echo 'python test_apply test' | nc 127.0.0.1 15201

# 3. 验证结果
# 成功: {"success": true, "output": "{\"function_exists\": true, ...}"}
# 失败: {"success": false, "error": "..."} 或 {"success": true, "output": ""}
```

**经验**：`unreal` 模块中的 BlueprintFunctionLibrary 类名不带 `U` 前缀（那是 C++ 的命名约定）。`getattr(unreal, 'ClassName')` 比直接访问 `unreal.ClassName` 更安全。

---

## 教训 4：`call AddOrUpdateBlendable` 对 Blueprint 接口无效

**场景**：通过 `call /Actor/PostProcessVolume0/PostProcessComponent AddOrUpdateBlendable` 添加 post-process 材质失败，`WeightedBlendables` 保持为空

**根因**：`InterfaceProperty` 反射处理使用 `reinterpret_cast<IBlendableInterface*>(Asset)`，但 Blueprint 实现的接口没有原生表示（`ScriptInterface.h` 明确说明："For objects that only implement an interface in blueprint, only ObjectPointer will be set because there is no native representation"）

**解决方案**：使用 `ULLMEasyShellMaterialLibrary::ApplyPostProcessMaterial` 静态函数，它直接操作 `WeightedBlendables` 数组，绕过接口问题：
```cpp
// C++ 实现（已验证有效）
UMaterialInterface* Mat = LoadObject<UMaterialInterface>(nullptr, *MaterialPath);
Volume->Modify();
FWeightedBlendable NewWB;
NewWB.Object = Mat;  // 直接存储 UMaterialInterface*，不是接口指针！
Volume->Settings.WeightedBlendables.Array.Add(NewWB);
Volume->PostEditChange();
Volume->MarkPackageDirty();
```

**验证方法**：
```bash
# 查看 PostProcessVolume 的 WeightedBlendables
cat /Actor/PostProcessVolume0
# 搜索 "WeightedBlendables" 字段
```

**经验**：当 `TScriptInterface<IBlendableInterface>` 通过 Python/反射传递时，Blueprint 实现的接口无法正确序列化。需要绕过接口层，直接操作底层对象指针。

**2026-05-15 验证**：`call AddOrUpdateBlendable` 返回 `{"success": true}` 但实际无效（权重未改变）。`ApplyPostProcessMaterial` 工作正常。问题根因：Blueprint 类没有原生接口表示，`GetInterfaceAddress` 返回 nullptr。

---

## 教训 7：Python Ability 输出捕获与 unreal.log()

**场景**：`python test_apply add_all` 返回空输出，但材质实际已添加

**根因**：ExecuteFile 模式下，`unreal.log()` 输出到 LogOutput，但某些情况下 LogOutput 为空时输出丢失。添加 `unreal.log()` 调用到 ability 方法内部可以解决（原因不明，可能是 Unreal log 缓冲问题）。

**修复方式**：
```python
def _add_all(self, args, context):
    unreal.log("DEBUG _add_all: starting")  # 添加内部日志
    # ... 业务逻辑 ...
    unreal.log(f"DEBUG _add_all: returning {results}")  # 返回前日志
    return results
```

**验证**：添加内部 `unreal.log()` 后，`add_all` 返回完整 JSON 输出。

---

## 教训 5：Python Ability 绑定层 args 解析问题

**场景**：`python test_apply test` 返回正确结果，但 `python test_apply add_all` 返回空输出

**观察**：
- TCP 测试显示两个命令都能被识别
- `test_apply test` 总是返回 `{"success": true, "output": "{\"function_exists\": true, ...}"}`
- `test_apply add_all` 总是返回 `{"success": true, "output": ""}`
- debug 日志文件显示代码实际执行成功并返回正确的 dict

**可能根因**：`ExecutePythonCaptureStdout` 函数中，`print(json.dumps(result))` 的输出没有被 `LogOutput` 捕获。返回的 dict 中包含 list 时，JSON 序列化后的字符串可能被截断或丢失。

**验证方法**：
```python
# 在 ability 中添加文件日志来调试
DEBUG_LOG = "D:/UnrealEngine/CODEO/debug_log.txt"
def debug_write(msg):
    with open(DEBUG_LOG, "a") as f:
        f.write(msg + "\n")
# 在 execute() 开头调用
debug_write(f"execute called: command={command}, args={args}")
```

**经验**：使用 TCP 直接测试 Python ability 比 CLI 更可靠。CLI 的 stdout 捕获机制可能丢失部分输出。

---

## 教训 6：Python Ability 多子命令注册行为差异

**场景**：`python test_apply test` 正常，但 `python test_apply add_all` 返回空；`python simple small` 返回 "Unknown command: python"

**观察**：
- `test_apply` (2个子命令) vs `simple` (1个子命令) 行为不同
- `test_apply test` 工作，`test_apply add_all` 返回空输出（代码执行成功但输出丢失）
- `simple small` 返回 "Unknown command: python"

**调试发现**：
- CLI 的 `echo 'python X Y' | llmshelllite.exe` 方式对某些命令返回 "Unknown command: python"
- TCP 发送 `python test_apply test` 返回正确结果
- CLI 和 TCP 对同一命令的处理可能不同

**可能根因**：
1. CLI 的 stdin 解析对包含下划线的 ability name 处理不同
2. 或者 CLI 发送命令的格式与 TCP 不同

**经验**：
- 使用 TCP 测试 Python abilities 而非 CLI
- CLI 输出不可靠时，通过文件日志或 `cat /Actor/PostProcessVolume0` 验证实际效果
