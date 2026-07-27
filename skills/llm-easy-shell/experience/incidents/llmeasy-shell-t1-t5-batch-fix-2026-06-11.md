---
name: llmeasy-shell-t1-t5-batch-fix-2026-06-11
description: "2026-06-11 一次性修 5 个 LLMEasyShell 仍存在的痛点 (T1-T5),9 commits on master, 完整回顾 + verification 状态 + 已知未修 limitation"
metadata: 
 node_type: memory
 type: project
 originSessionId: c1fb4fc9-0a97-47c6-9395-6afe4866ea30
---

# LLMEasyShell Pain-Points 批量修复 (T1-T5) — 2026-06-11

## 5 痛点 + 修复

| 痛点 | 根因 | 修法 | Commit | 验证状态 |
|---|---|---|---|---|
| T1 args-dropped | `llm-shell/main.cpp:3446` 只存首 argv | `JoinArgsToCommand` helper | `be8c393` | ✅ 4 CLI 验证全 pass |
| T2 BP CDO 不持久化 | `SetAssetProperty` 缺 `CompileBlueprint` | 加 `CompileBlueprint(SkipGarbageCollection, &CompileResults)` + error 捕获 | `afd08d7` + `637beb9` | ✅ set + save + restart 验证 |
| T3 bpcomp 拿不到 TObjectPtr | Python `get_components()` 不返 C++ 属性 | `ULLMEasyShellPropertyLib::ResolveBlueprintObjectProperty` UFUNCTION + bpcomp.py C++ 路径优先 | `eaea5be` + `f96aa30` | ✅ `bpcomp get WeaponComponent` 验证 |
| T4 Python ability cache | `bPythonAbilitiesRegistered` one-shot | MD5 hash 检测 + `python reload` 触发 re-register | `f99a8f0` + `6212bab` | ✅ `python t4_test_ability run` 立即 work |
| T5 multiengine 4 子项 | 多个独立 bug (null guard, engine path, .current_port, Tickable log) | 4 sub-fixes | `ad521cc` + `7d6630b` | ⚠️ T5a/b/c 验证过,d/dual-instance 受 pre-existing HD3D crash 阻塞 |

## 关键 review-fix 循环 (不是 1-shot implementer)

- T2 C1 (game thread 验证) + C2 (FCompilerResultsLog 错误捕获) — `637beb9`
- T3 I1 (cast 收紧到 FObjectProperty 拒容器/soft/weak) — `f96aa30`
- T4 I-1 (删冗余 AbilityCommandHandlers.Remove) + I-2 (删 dead bNeedsReRegistration) — `6212bab`
- T5 I-1 (SendResponse 包 ClientSocket null check) — `7d6630b`

## 仍未修的 limitation (out of scope, 已记入各 t*-memory)

1. **Lite 版 main.cpp 编译失败** — `MAX_PORT`/`BASE_PORT`/`kScanPortCount` 未定义 (T1 第一次发现, T5 完整确认 3 个常量). 与 T1/T5 修复无关, 是 pre-existing 引入的 constexpr vs const 错配.
2. **HD3D `UnrealEditor_TedsCore` crash** — 阻塞 T5 dual-instance PIE 验证. 需独立修.
3. **`set` 命令 dot-notation 解析 bug** — `ShellCommand_Set.cpp:103`,`set /Game/.../BP_X.BP_X Prop Val` 失败, 正确语法 `set /Assets/.../BP_X/Prop Val`.
4. **`bpcomp set` `'Class' object has no attribute 'find_property_by_name'`** — pre-existing, T3 没解决 set 路径.
5. **T3 quoted-arg 边缘 case** — `find "My Actor"` 丢引号语义.

## 实施策略 (供未来类似批量修复参考)

1. **每痛点独立 subagent-driven 流程**: implementer + spec reviewer + code quality reviewer
2. **按风险递增顺序**: T1 (shell 1 行) → T5 (multi-engine routing)
3. **每步独立 commit** 不批量, 失败时只回滚一 commit
4. **reviewer 标 important 必修** 走 re-review, 标 minor 接受
5. **Final code reviewer 看 cross-task consistency** 是关键 catch (本批次的 F2/F3 漏掉就是 final reviewer 抓到的)

## 相关

- Spec: `docs/superpowers/specs/2026-06-11-llmeashyshell-pain-points-batch-fix-design.md`
- Plan: `docs/superpowers/plans/2026-06-11-llmeashyshell-pain-points-batch-fix.md`
- 5 task memory: `t1-llmshell-args-dropped-fix.md` / `t2-bp-cdo-persistence-fix.md` / `t3-bpcomp-tobjectptr-reflection-fix.md` / `t4-python-ability-cache-hash-fix.md` / `t5-multiengine-routing-fix.md`

[[t1-llmshell-args-dropped-fix]] [[t2-bp-cdo-persistence-fix]] [[t3-bpcomp-tobjectptr-reflection-fix]] [[t4-python-ability-cache-hash-fix]] [[t5-multiengine-routing-fix]]
