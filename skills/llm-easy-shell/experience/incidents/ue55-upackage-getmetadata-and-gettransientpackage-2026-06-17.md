---
name: ue55-upackage-getmetadata-and-gettransientpackage-2026-06-17
description: "UE 5.5 vs 5.6+ API breaks confirmed from engine source — UPackage::GetMetaData() return type change, GetTransientPackageAsObject 5.7-only — fixes verified in LLMDynamicUI 1.1.1 across 5.5/5.6/5.7"
metadata: 
 node_type: memory
 type: reference
 originSessionId: 430031d1-8356-4aa6-9aa7-b8861d9e7338
---

# UE 5.5/5.6/5.7 API diffs — verified from engine source 2026-06-17

While patching LLMDynamicUI for multi-UE Fab clean-build support, I read the actual
engine headers (verified on installed builds) and confirmed two real API breaks
that affect cross-version code.

## 1. `UPackage::GetMetaData()` return type changed in 5.6

| UE | Signature (from `Engine/Source/Runtime/CoreUObject/Public/UObject/Package.h`) | Usage |
|---|---|---|
| 5.5 | `class UMetaData* GetMetaData();` | `->`, **null-check required** |
| 5.6 | `FMetaData& GetMetaData();` | `.`, always valid |
| 5.7 | `FMetaData& GetMetaData();` | `.`, always valid |

5.6+ doesn't `#include "UObject/MetaData.h"` to get the old `UMetaData*` API — that
header now declares `FMetaData` only. Code that compiled on 5.5 will fail to link
on 5.6+ (and vice versa) if you don't guard with `ENGINE_MINOR_VERSION`.

**Fix pattern (3-way compatible):**
```cpp
#if ENGINE_MAJOR_VERSION > 5 || (ENGINE_MAJOR_VERSION == 5 && ENGINE_MINOR_VERSION >= 6)
 Package->GetMetaData().SetValue(BP, TEXT("Key"), *Value);
#else
 if (UMetaData* MetaData = Package->GetMetaData())
 {
 MetaData->SetValue(BP, TEXT("Key"), *Value);
 }
#endif
```

## 2. `GetTransientPackageAsObject()` is UE 5.7-only

| UE | Has it? | Source |
|---|---|---|
| 5.5 | No | (grep `Engine/Source/Runtime/CoreUObject` returns 0 hits) |
| 5.6 | No | (grep returns 0 hits) |
| 5.7 | Yes | `UObject/UObjectGlobals.h:257` `COREUOBJECT_API UObject* GetTransientPackageAsObject();` |

`GetTransientPackage()` is universal (returns `UPackage*` in all three).

**Why the cast is required:** `NewObject<>`'s `Outer` template parameter is
`UObject*`, but `GetTransientPackage()` returns `UPackage*`. A ternary like
`Outer ? Outer : GetTransientPackage()` will fail compile with C2446 (no implicit
conversion between UObject* and UPackage*). Use `(UObject*)GetTransientPackage()` —
semantically safe since `UPackage` is-a `UObject`.

`UPackage* → UObject*` upcast is safe and is what `GetTransientPackageAsObject()`
itself does on 5.7. No reason to gate it on engine version.

**Verified on LLMDynamicUI:** 7 `NewObject<...>(GetTransientPackageAsObject())` call
sites changed to `NewObject<...>((UObject*)GetTransientPackage())` — 5.5/5.6/5.7
all pass clean `RunUAT.bat BuildPlugin ... -rocket`.

## 3. Tag strategy for "tagged too early" scenarios

**Don't `git tag -f` to overwrite a tag** that's already on remote — it
silently changes the commit a tag points to, and if anyone already fetched the
old tag, they keep a divergent reference. Audit trail becomes confused.

**Better:** bump version (`1.1.0 → 1.1.1` patch), commit the version-string-only
change in `.uplugin` + README footer + VERSION-NOTES, tag the new commit. Old
tag stays as historical reference, new tag carries the corrected source.

Related: [[llmdynamicui-1-1-0-tagged-pre-patch-2026-06-17]] (this scenario).
