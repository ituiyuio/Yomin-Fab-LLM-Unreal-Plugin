---
name: ue57-build-bat-unblock-2026-06-12
description: "UE 5.7 InstalledBuild 环境下 LiveCoding 失败时的 unblock 关键路径 — 直接 Build.bat 编 game module 14s 成功,绕过 LC engine relink phantom dependency"
metadata: 
 node_type: memory
 type: project
 originSessionId: 67d12361-0643-4190-ad5b-fd0124907bc5
---

UE 5.7 InstalledBuild 环境下 LiveCoding (LC) 触发的 phantom engine relink 会失败,直接报:
- MiMalloc.c(24): fatal error C1083: 无法打开包括文件: "static.c"
- UnrealMathSSE.cpp(9): fatal error C1083: ThirdParty/SSEMathFun/sse_mathfun_extension.h
- 等等 958 个 action 全是 engine 模块重编

根因:LC 自身的 patch 机制会触发 UBT 把 engine 模块当 user source 重编,而 InstalledBuild 不附带 engine 内部的 ThirdParty 源码(`static.c`/`SSEMathFun`/`skia`/`VHACD`/`oodle2base.h`/`Services/Loader/Loader.h` 等)。

**unblock 路径:直接 `Build.bat` 编 game module 即可。**
```bash
cmd //c "taskkill /F /IM UnrealEditor.exe" # 必须先 kill editor
powershell.exe -Command "Set-Location 'D:/UnrealEngine/CODEO'; & 'C:/Program Files/Epic Games/UE_5.7/Engine/Build/BatchFiles/Build.bat' CODEOEditor Win64 Development 'D:/UnrealEngine/CODEO/CODEO.uproject' -waitmutex -NoHotReload"
```

**实际效果**:6 个 action,14.71s 成功。只编修改的 .cpp + link .dll,不触发 engine relink。

**Why**:Build.bat 走标准 UBT 路径,UBT 知道这是 game module 重链(用 prebuilt engine .lib),不需要 engine source。LC 走另一条 patch 路径,会错误认为 engine 也需要重编。

**How to apply**:任何 UE 5.7 InstalledBuild 项目上:
1. 改 .cpp 后 → 不用 LC
2. 先 `taskkill /F /IM UnrealEditor.exe`
3. 跑 Build.bat(模板如上)
4. `llm-shell --restart` 重启 editor 加载新 .dll

**注意**:`llm-shell --restart` 内部就调 Build.bat,所以 `llm-shell --restart` 是更简单的命令,但它会先检查 crash state — 如果你手动 taskkill 过,LLMEasyShell 会缓存 crash 标志,导致后续 `play` 返回 `crashed:true`。**总是用 `llm-shell --restart` 而不是手动 taskkill + Build.bat**,前者会自动清 crash state。

相关:
- [[llmvfx-build-broken-pre-existing-2026-06-03]] — 历史 LC 失败记录
- [[ue57-installedbuild-thirdparty-missing]] — InstalledBuild 缺 third-party 库的根因
- [[llmeasy-shell-t1-t5-batch-fix-2026-06-11]] — llm-shell 多次迭代的 bug 修复
