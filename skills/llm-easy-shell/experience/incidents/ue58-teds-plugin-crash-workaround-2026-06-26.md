---
name: ue58-teds-plugin-crash-workaround-2026-06-26
description: UE 5.8 EditorDataStorage TEDS experimental plugin crashes editor at startup with EXCEPTION_ACCESS_VIOLATION 0xffffffffffffffff in TedsCore/TedsTableViewer — disable via .uproject + DefaultEngine.ini double-bind workaround
metadata: 
 node_type: memory
 type: tool-fix
 originSessionId: a0e4f2b8-dbe6-42e5-b93d-ddead6bd4610
---

UE 5.8 TEDS (EditorDataStorage + EditorDataStorageFeatures) IsExperimental=true plugin crashes editor at startup EXCEPTION_ACCESS_VIOLATION 0xffffffffffffffff in TedsCore → TedsTableViewer → Core, SecondsSinceStart=0 (immediate crash, not load-time). 锁定 harness 13 次 Session 7-19 editor offline。

**Why:** 已知 UE 5.8 实验性 plugin 不稳定 + 编辑器启动加载顺序中 TedsCore 调到 TedsTableViewer 时 null deref。

**How to apply:** 双保险 disable (光 .uproject Enabled:false 不够，因 EditorDataStorage.uplugin EnabledByDefault:true 强制 load):
1. `.uproject` 加 2 plugin disable entry:
 ```json
 { "Name": "EditorDataStorage", "Enabled": false, "Comment": "Disable TEDS — crash workaround" }
 { "Name": "EditorDataStorageFeatures", "Enabled": false, "Comment": "Disable TEDS Features — contains TedsTableViewer" }
 ```
2. `Config/DefaultEngine.ini` [Plugins] section 加 blacklist:
 ```ini
 [Plugins]
 -EnabledPlugins=EditorDataStorage
 -EnabledPlugins=TedsCore
 -EnabledPlugins=TedsUI
 -EnabledPlugins=TedsTableViewer
 ```

**踩坑 5 维:**
1. `.uproject` `Enabled:false` 单独用没生效 — `EnabledByDefault:true` 强制 load, 需 `[Plugins] -EnabledPlugins=` 语法 override
2. rename `.uplugin` → `.uplugin.disabled` 硬 disable 反而 build 失败 — `CODEO → Bridge → MetaHumanSDK → HairStrands → Dataflow → EditorDataStorage` 强依赖链缺一不可 (Bridge → MetaHumanSDK 是项目启用 chain)
3. Edit tool 写 LF 但文件原本 LF-only (DefaultEngine.ini/.uproject 都是 LF 不是 CRLF), 假 CRLF 误判会触发全文件 diff, python script 还原 LF 后 diff 才干净
4. build log 写到 `%TEMP%/llm_shell_build_*.log` 跑完即清, verify 只能用 JSON `[Output]` 字段
5. llm-shell `--restart` push-model 信号 12s 就报 ready 但 info probe 实际还没连 — 假阳性, 必须 `Test-NetConnection port 15151` 或 `Get-Process UnrealEditor` 双重 verify

**Verify:** llm-shell --restart 第 4 次双 disable 后 PID 40140 + port 15151=True, CrashContext 消失, `info -j` 返回 `{project, level, pieState, editorState}` 完整 JSON。

**Apply when:** 看到 Saved/Crashes/UECC-Windows-*_0000/CODEO.log ErrorMessage="Unhandled Exception: EXCEPTION_ACCESS_VIOLATION reading address 0xffffffffffffffff" + CallStack 多个 UnrealEditor-TedsCore + UnrealEditor-TedsTableViewer + SecondsSinceStart=0。related(crash dump 命名模式 UECC-Windows-{GUID}_0000)。