---
name: llmeasyshell-lite-plugin-paths
description: "Historical record: 2026-06-01 目录重命名冲突已通过 phase6-fixes 闭环。本 doc 仅作 audit trail,实际 plugin 路径以 filesystem 为准。"
metadata:
 node_type: memory
 type: project
 originSessionId: 967ae0f0-0803-4aa9-94ce-cafc6386a200
---

> [tool-fix-165 2026-06-29] **本 doc 是历史记录,问题已在 phase6-fixes-2026-06-01 闭环。** 当前 filesystem 验证: `find Plugins -maxdepth 1 -name 'LLMEasyShell*' -type d` = `Plugins/LLMEasyShell` + `Plugins/LLMEasyShellLite` (无 underscore),`Plugins/LLMEasyShell_Lite` 不存在。下文 "the plugin currently cannot load" 是 2026-06-01 当时快照,留作 audit trail 不要按其操作 — 找 Lite plugin 文件直接 `Plugins/LLMEasyShellLite/` (无 underscore) 即可。

LLMEasyShell Lite plugin physical location vs uproject path mismatch (historical, resolved).

**Where the files actually are:** `Plugins/LLMEasyShell_Lite/` (with underscore between "Shell" and "Lite"). Contains the full 40+ files (uplugin, Build.cs, Public/*.h, Private/*.cpp, PyAbilities/, Config/).

**Where CODEO.uproject points:** `Plugins/LLMEasyShellLite` (no underscore). This is the path UE's plugin manager uses.

**Why the conflict exists:** the previous session renamed the directory to remove the underscore, but the physical files (uplugin, Build.cs module declaration `LLMEasyShellLite`) still use the underscored path because UBT auto-generates the module API macro from the directory name.

**Implication:** the plugin currently cannot load — `CODEO.uproject` references `Plugins/LLMEasyShellLite` but the actual files are at `Plugins/LLMEasyShell_Lite`. Either:
1. Move the physical directory to `Plugins/LLMEasyShellLite` (remove underscore), OR
2. Update `CODEO.uproject` to point to `Plugins/LLMEasyShell_Lite`

**How to apply:** when looking for Lite plugin files, search `LLMEasyShell_Lite` (underscore) first. Verify with `find`/`ls` rather than relying on Glob results alone, as Glob can show stale data.
