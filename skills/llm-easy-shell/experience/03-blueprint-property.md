# LLMEasyShell Blueprint / Property 操作经验

> 5 个教训：bpprop 5 bug / 2026-05-08 三大修复 / bpcomp 限制 / FObjectProperty 嵌套 / CompileBlueprint 重置

---

## 教训 1：bpprop 5 个 ClassProperty 坑

### 1a. `_args_to_dict` 把 subcommand 当位置参数

`python bpprop set <asset> <prop> <value>` 失败，`args[0]='set'` 被当作 `asset_path`，报 "Asset not found: set"。

**修复**（`bpprop.py`）：

```python
KNOWN_SUBCOMMANDS = {"set", "get", "list"}
def _args_to_dict(args):
    for arg in args:
        if isinstance(arg, str) and arg in KNOWN_SUBCOMMANDS:
            continue  # skip — 在 main() 里 dispatch
```

### 1b. `cdo.get_editor_property()` 找不到 C++ 继承属性

`SurvivorPlayerClass` 定义在 `ASurvivorGameMode`（C++ 基类），BP CDO 上 `get_editor_property` 找不到。**未解决**，BP CDO 对 C++ 继承字段暴露方式不同。

### 1c. `set` 命令在 ClassProperty 上崩溃

`set ... SurvivorPlayerClass /Game/BP_SurvivorPlayer` 触发 `ObjectA.IsA<UClass>()` 断言。**未解决**，见教训 4 修法（`FClassProperty` MetaClass 校验）部分缓解。

### 1d. `python reload` 不重 import 已加载模块

`importlib.reload()` 在同 session 内不生效，BP CDO 缓存问题。**Workaround**：重启编辑器。

### 1e. `set` 报 success 但 `cat` 读 C++ 继承值是旧的（**已修复**为条件分支）

**历史问题**：`set AttackRange 200` 报成功，但 `cat` 显示 `0.000000`（C++ 默认值）。

**历史根因**：`FKismetEditorUtilities::CompileBlueprint(BP)` 重新生成 BP class，**重置 C++ 继承的 CDO 默认值**到 C++ class 默认。

**当前实现**（`ShellCommand_Set.cpp:386-407`，条件分支 + 显式 skip）：

```cpp
// Check if this is a C++ inherited property vs Blueprint-defined property
// For C++ inherited properties, compiling would reset them to C++ defaults
bool bIsCPPProperty = (Prop->GetOwnerClass() != BP->GeneratedClass);

if (bIsCPPProperty) {
    // For C++ inherited properties, skip compile to preserve the runtime change
    // The change persists in memory and works at runtime, but won't persist to disk
    BP->GetPackage()->MarkPackageDirty();
    CDO->GetPackage()->MarkPackageDirty();
}
else {
    // For Blueprint-defined properties, notify Blueprint system so change persists
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
    FKismetEditorUtilities::CompileBlueprint(BP);
    BP->MarkPackageDirty();
}

return FLLMEasyShellResult::Success(FString::Printf(
    TEXT("{\"success\": true, \"property\": \"%s\", \"newValue\": \"%s\", \"compiled\": %s}"),
    *PropertyPath, *Value, bIsCPPProperty ? TEXT("false") : TEXT("true")));
```

**两代方案对比**：

| 代次 | 实现 | 限制 |
|------|------|------|
| 第 1 代（旧 memory） | 一律注释掉 `CompileBlueprint` | BP 定义字段也不 compile，可能没生效 |
| **当前（`ShellCommand_Set.cpp:386-407`）** | 按 `bIsCPPProperty` 条件分支 | BP 定义字段正常 compile，C++ 继承字段 skip |

**配套坑**：响应里加 `"compiled": false` 字段告知调用方，**C++ 继承字段的修改只在内存/runtime 生效，磁盘上不会持久化**（要持久化需要改 C++ 默认值或重新建 BP）。

---

## 教训 2：2026-05-08 三大修复（FClassProperty + bpprop args + 组件导航）

### Fix 1：FClassProperty 设值前 MetaClass 校验

**文件**：`LLMEasyShellReflection.cpp:538-570`

```cpp
if (ClassValue) {
    if (!ClassValue->IsChildOf(ClassProp->MetaClass)) {
        UE_LOG(LogTemp, Warning, TEXT("FClassProperty: '%s' not subclass of '%s'"),
            *ClassValue->GetName(), *ClassProp->MetaClass->GetName());
        return false;
    }
    if (!Container) {
        UE_LOG(LogTemp, Warning, TEXT("FClassProperty: Container null for '%s'"), *ClassProp->GetName());
        return false;
    }
    ClassProp->SetObjectPropertyValue_InContainer(Container, ClassValue);
    return true;
}
```

### Fix 2：bpprop args 解析加固

```python
# 2a: _args_to_dict 接受非 list
def _args_to_dict(args):
    if not isinstance(args, list):
        if isinstance(args, str) and "=" in args:
            k, v = args.split("=", 1); d[k.strip()] = v.strip()
        return d
    # ...

# 2b: main() 校验
def main(args, context=None):
    if not isinstance(args, list):
        return {"success": False, "error": f"Expected list, got {type(args).__name__}"}
    if len(args) == 0:
        return {"success": False, "error": "Empty args list"}
    # dispatch with debug_info

# 2c: bpprop_set 过滤
if isinstance(args, list):
    filtered = [a for a in args if not (
        isinstance(a, str) and (a in KNOWN_SUBCOMMANDS or a.startswith("_subcommand="))
    )]
    args = filtered
```

### Fix 3：Blueprint 组件点号路径（`Component.Property`）

`python property set_prop /Game/BP_SurvivorPlayer WeaponComponent.AttackVFX ...` 在 BP CDO 上原本解析失败。

**修复**（`LLMEasyShellReflection.cpp`）：在 `GetPropertyValue` / `SetPropertyValue` 检测 `Component.Property` 格式，先找 SCS 节点，递归调用 `GetPropertyValue(SCSNode->ComponentTemplate, RemainingPath)`。

**限制**：只支持 SCS 节点（Blueprint 编辑器拖入的组件）。C++ `CreateDefaultSubobject` 创建的组件需用 BP `#` 路径（见教训 3）。

---

## 教训 3：`/Game/BP_X#Component` 路径同时支持 SCS 和 C++ subobject

**场景**：`cat /Game/Features/Survivor/BP_SurvivorPlayer#WeaponComponent` 之前只能查 SCS 节点，C++ `CreateDefaultSubobject` 创建的组件（`WeaponComponent`）查不到。

**修复**（`ResolveBlueprintComponent` 在 `LLMEasyShellReflection.cpp`）：

```cpp
// 1. 先尝试 SCS 节点
USCS_Node* SCSNode = FindSCSNode(BP, ComponentName);
if (SCSNode) return SCSNode->ComponentTemplate;

// 2. C++ subobject fallback：在 CDO 上按名找 FObjectProperty
for (FProperty* Prop : TFieldRange<FObjectProperty>(BP->GeneratedClass->GetDefaultObject()->GetClass())) {
    if (Prop->GetName() == ComponentName) {
        if (auto* Comp = Cast<UActorComponent>(Prop->GetObjectPropertyValue(CDO))) {
            return Comp;
        }
    }
}
```

**配套改动**（`LLMEasyShellReflection.h`）：`FBlueprintComponentTarget` 加 `Component` 字段；`ShellCommand_Cat.cpp` / `ShellCommand_Discover.cpp` 支持 `Target.Component`。

**经验**：写自定义 ability 走 BP 组件时**优先 `#` 路径**（自动 fallback 链），不要硬编码 SCS lookup。

---

## 教训 4：`FObjectProperty` / `TObjectPtr` 嵌套路径必须解引用 + 继续 walk

**场景**：`python property set_prop /Game/BP_SurvivorPlayer WeaponComponent.WeaponType Range` 失败。

**根因**（`LLMEasyShellPropertyLib.cpp:143-152`）：`ResolvePath()` 只对 `FStructProperty` 继续 walk 嵌套路径，遇到 `FObjectProperty`（`TObjectPtr<WeaponBaseComponent>`）就 return failure。

**修复**（`LLMEasyShellPropertyLib.cpp`）：

```cpp
// 1. FResolvedProp 加 OwnerObject 字段
struct FResolvedProp {
    FProperty* Property;
    void* ValuePtr;
    UObject* OwnerObject;  // ← 新加：用于 Modify() / FireChangeNotify()
};

// 2. ResolvePath 加 FObjectProperty 处理
if (FObjectProperty* ObjProp = CastField<FObjectProperty>(CurrentProp)) {
    UObject* Obj = ObjProp->GetObjectPropertyValue(ValuePtr);
    if (Obj) {
        FProperty* NextProp = Obj->GetClass()->FindPropertyByName(NextName);
        return RecurseResolve(Obj, NextProp, ...);
    }
}

// 3. FClassProperty 早返回（不能 walk past TSubclassOf）
if (FClassProperty* ClassProp = CastField<FClassProperty>(CurrentProp)) {
    return Failure;  // TSubclassOf 不可 walk
}

// 4. SetUPropertyFromExportText 用 OwnerObject 触发 Modify / FireChangeNotify
Prop->SetValue_InContainer(OwnerObject);
OwnerObject->Modify();
OwnerObject->PostEditChange();
```

**经验**：嵌套路径处理要覆盖 `FStructProperty` / `FObjectProperty` / `FArrayProperty` / `FSetProperty` 等所有容器/指针类型；FClassProperty 早返回。

---

## 教训 5：bpcomp 拿不到 C++ 父类的 CDO

**场景**：`python bpcomp` 想访问 `BP_Shop.ParentClass`（C++ `UUserWidget` 父类）CDO 失败。

**根因**：UE Python 的 `unreal.load_class()` 对 native C++ class 返回 Python type，**没有 `get_default_object()` 方法**。对 BP class 则有。

**Workaround**（`bpcomp.py:113-134`）：用 C++ 函数 `ULLMEasyShellPropertyLib::GetBlueprintParentClassCDOPath()`，返回：
- BP 父类 → CDO 资产路径
- C++ 父类 → class 路径（Python 端用 `unreal.load_asset()` 加载）

**经验**：C++ 父类 CDO 访问**不要在 Python 端硬做**，调 C++ 拿路径再 `load_asset`。

---

## 经验速查

| 症状 | 教训 |
|------|------|
| `set ClassProperty` 报 IsA<UClass> 断言 | 教训 1c / 2 Fix 1：MetaClass 校验 |
| `set C++继承字段` 报 success 但 cat 是 0 | 教训 1e：注释 CompileBlueprint |
| `Component.Property` 路径解析失败 | 教训 2 Fix 3：SCS 节点递归 |
| C++ `CreateDefaultSubobject` 组件 cat 不到 | 教训 3：`#` 路径 fallback 到 FObjectProperty |
| `WeaponComp.NestedField` 失败 | 教训 4：ResolvePath 支持 FObjectProperty walk |
| `bpcomp` 拿不到 C++ 父类 CDO | 教训 5：调 C++ GetBlueprintParentClassCDOPath |
