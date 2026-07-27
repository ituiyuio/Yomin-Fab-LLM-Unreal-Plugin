---
name: ue-uplugin-json-no-comments-2026-06-09
description: "UE .uplugin 用的是严格 JSON 解析器,// 和 /* */ 注释都非法;会导致 plugin 整加载失败 + \"Missing Plugin\" modal 阻塞"
metadata: 
 node_type: memory
 type: feedback
 originSessionId: ab89b52f-89eb-4e8e-ab02-8aed304a4d33
---

# UE .uplugin 不支持 JSON 注释

## 症状
`LogPluginManager: Error: Failed to load Plugin (.../LLMMaterial.uplugin); Failed to read file. Missing a comma or ']' after an array element., Line N: // ...`
跟着一条:
`LogPluginManager: Error: Unable to load plugin 'LLMMaterial'. It was requested by Enabled plugins in .uproject for , but is missing on disk. Aborting.`
最后 UE 弹 modal "This project requires the 'LLMMaterial' plugin, which could not be found. Would you like to disable it and continue?"

## 根因
UE 的 PluginManager 用 **严格 JSON 解析器**(FJsonSerializer 严格模式),JSON 规范本身不允许 `//` 或 `/* */` 注释。看到注释行直接报语法错,整个 .uplugin 拒绝加载。

**第一次踩坑**:b5b8596 (2026-06-07) 在 `LLMMaterial.uplugin` 的 `Plugins[]` 数组里加了一段 `//` 注释解释为什么 LLMEasyShell/Lite 不列在 dependencies 里。结果 2026-06-09 editor 启动全部崩在 modal,排查走错路(以为是 TedsCore crash 的连锁反应,实际是 LLMMaterial 整 plugin 没加载)。

## How to apply

1. **任何 .uplugin 编辑**:只能写合法 JSON,加注释用 `Description` 字段承载设计意图
2. **看到 "Missing Plugin" modal**:第一反应查 `Saved/Logs/CODEO*.log` 里 `LogPluginManager: Error: Failed to load Plugin` 的具体 line — 99% 是 JSON 语法错
3. **校验手段**:`python -c "import json; json.load(open('path/to/.uplugin'))"` 立即验证
4. **同类禁忌**:
 - `//` 行注释
 - `/* */` 块注释
 - 尾部逗号 (trailing comma)
 - 单引号字符串(必须双引号)
 - 注释掉的字段(`// "Field": ...`)— 这是个常见误操作,JSON 解析器不会跳过

关联:[[llmmat-silent-success-regression-2026-06-09]] (同一个 batch 4/8 commit 引入,但语义错误是另一个问题)
