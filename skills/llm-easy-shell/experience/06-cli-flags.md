# LLMEasyShell CLI 旗标经验(2026-06-13)

## 背景
LLM 用 llm-shell 调用 UE 编辑器时,70% 输出是噪声:
1. **stderr 流**:`[llm-shell] Engine path found...`、`Trying port 15151...`、
   `Found instance on port 15151: ...`、`[preflight] Unknown command...`、
   `[preflight] Warning: ...` 大量诊断/警告
2. **stdout 嵌套 JSON**:`{"success":true,"output":"{\"wave\":{...}}"}` — server
   端把结果 JSON 再序列化进 `output` 字段,LLM 还要再 parse 一次字符串

上下文是稀缺资源,必须压缩。

## 设计决策
加两个**正交**的旗标(可单独/组合使用):

| 旗标 | 等价 | 作用范围 | 原理 |
|------|------|----------|------|
| `-q` | `--quiet` | REPL 不影响,只 -c 静默 | `freopen()` stderr 到 `llm-shell-quiet.log`(写回 exe 同目录) |
| `-j` | `--json-only` | -c 模式下生效 | parse server 响应的 `output`/`result` 字段,做 JSON 反转义后原样 stdout |

## 实现细节
1. **早解析 argv** 在 `DetectProjectPaths()` 之前
   - 原因:启动期的 fprintf 路径查找/端口扫描噪声必须被截
   - 即:`for (int i = 1; ...) if (argv[i]=="-q") { freopen(...); break; }`
2. **JSON 反转义**支持:`\n \r(丢弃) \t \" \\ / \b \f \uXXXX(→ UTF-8 BMP)`
3. **优先 output 字段**,fallback 到 result(给 `reload` 用)
4. 失败时回退打印原始 JSON 字符串,避免 extract 错而丢数据
5. REPL 模式不静默,只 -c 静默(交互场景要给人类看诊断)

## 验证
| 命令 | Before | After(`-q -j`) |
|------|--------|------------------|
| 输出行数 | 17 | 7 |
| 噪声行 | 10+ stderr | 0 |
| 数据格式 | 嵌套 JSON | 纯 JSON |
| LLM 可读 | 需二次解析 | 直接 parse |

## 教训
- stderr 重定向**必须早于** `DetectProjectPaths()`,否则启动期 fprintf 已经飞走
- `freopen()` 用 C 风格比 redirect 简单,但有 deprecation warning(MSVC C4996)
- REPL 模式下 `fprintf(stderr, ...)` 是合理的(人要看),不要全部都静默
- 嵌套 JSON 反转义是边界:既要处理 `\n`(换行)、`\"`(引号)、`\uXXXX`(Unicode 4 位 hex)
- LLM 上下文对噪声敏感度极高,`-q -j` 这两个 flag 是 ROI 极高的工程优化

## 经验值
- 把复杂输出改造为 LLM-friendly 默认值是基本功
- 诊断信息放文件,主输出放 stdout 是 Unix 哲学(2>&1、tee)
