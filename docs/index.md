---
layout: home

hero:
  name: YominUnreal Plugins
  text: AI 驱动的 Unreal Engine 开发工具
  tagline: 用 JSON 描述你的意图，剩下交给插件
  actions:
    - theme: brand
      text: 快速开始
      link: /llm-dynamic-ui/
    - theme: alt
      text: 在 GitHub 上查看
      link: https://github.com/yomin-unreal

features:
  - icon: 🎨
    title: LLM Dynamic UI
    details: DSL 驱动的 UMG Widget 生成系统。从 JSON 生成完整的 UMG Widget 蓝图,包含布局、动画和 SDF 视觉效果。
    link: /llm-dynamic-ui/
    linkText: 了解

  - icon: 🎭
    title: LLM Material
    details: JSON 驱动的 Material 生成系统。从 JSON 定义创建 Material 蓝图资产,完整支持 Substrate 与自定义 HLSL shader 函数。
    link: /llm-material/
    linkText: 了解

  - icon: 🌲
    title: LLM StateTree
    details: JSON 驱动的 StateTree 资产生成器。从 JSON 生成 StateTree 蓝图资产,支持 schema 自动推断与 AI 行为树实时预览。
    link: /llm-statetree/
    linkText: 了解

  - icon: 🔊
    title: LLM MetaSound
    details: JSON 驱动的 MetaSound 音频资产生成器。从 JSON 生成 UMetaSoundSource 与 UMetaSoundPatch 资产,节点自动连接。
    link: /llm-metasound/
    linkText: 了解
---

<section class="shell-section">
  <h2 class="shell-section-title">LLM Easy Shell</h2>
  <p class="shell-section-tagline">用任意 LLM agent 驱动 Unreal Editor — 完整读写版,或只读安全子集。</p>
  <div class="shell-grid">
    <a class="shell-card" href="/llm-easy-shell/">
      <div class="shell-card-icon">💻</div>
      <h3 class="shell-card-title">LLM Easy Shell</h3>
      <p class="shell-card-desc">TCP shell 接口,可从任意外部客户端驱动 Unreal Editor。35+ 编辑器命令、25+ Python 能力,端口 15151–15200。</p>
      <span class="shell-card-link">了解 →</span>
    </a>
    <a class="shell-card" href="/llm-easy-shell-lite/">
      <div class="shell-card-icon">🔍</div>
      <h3 class="shell-card-title">LLM Easy Shell Lite</h3>
      <p class="shell-card-desc">任意 LLM agent 与 Unreal Editor 之间的只读 TCP 桥接。9 个命令,端口 15201–15250,依赖 2 个引擎插件,免费。</p>
      <span class="shell-card-link">了解 →</span>
    </a>
  </div>
</section>

<div style="text-align: center; padding: 2rem 0; color: #888;">
所有插件共享同一范式:<strong>用 JSON 描述你的意图</strong>,剩下交给插件。
</div>

<LatestNews :count="3" />
