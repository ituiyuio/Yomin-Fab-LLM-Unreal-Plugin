---
layout: home

hero:
  name: YominUnreal Plugins
  text: AI-powered Unreal Engine Development Tools
  tagline: Define your intent in JSON, let the plugin handle the rest
  actions:
    - theme: brand
      text: Get Started
      link: /llm-dynamic-ui/
    - theme: alt
      text: View on GitHub
      link: https://github.com/yomin-unreal

features:
  - icon: 🎨
    title: LLM Dynamic UI
    details: DSL-Driven UMG Widget Generation System. Generate complete UMG Widget Blueprints from JSON with layout, animations, and SDF visual effects.
    link: /llm-dynamic-ui/
    linkText: Explore

  - icon: 🎭
    title: LLM Material
    details: JSON-Driven Material Generation System. Create Material Blueprint assets from JSON definitions with full Substrate support and custom HLSL shader functions.
    link: /llm-material/
    linkText: Explore

  - icon: 🌲
    title: LLM StateTree
    details: JSON-driven StateTree Asset Generator. Generate StateTree Blueprint assets from JSON with schema auto-inference and live preview for AI behavior trees.
    link: /llm-statetree/
    linkText: Explore

  - icon: 🔊
    title: LLM MetaSound
    details: JSON-driven MetaSound Audio Asset Generator. Generate UMetaSoundSource and UMetaSoundPatch assets from JSON with auto-connected nodes.
    link: /llm-metasound/
    linkText: Explore

  - icon: 💻
    title: LLM Easy Shell
    details: TCP shell interface for driving the Unreal Editor from any external client. 35+ editor commands, 25+ Python abilities, ports 15151–15200.
    link: /llm-easy-shell/
    linkText: Explore

  - icon: 🔍
    title: LLM Easy Shell Lite
    details: Read-only TCP bridge between any LLM agent and the Unreal Editor. 9 commands, ports 15201–15250, 2 engine plugin deps, free.
    link: /llm-easy-shell-lite/
    linkText: Explore
---

<div style="text-align: center; padding: 2rem 0; color: #888;">
All plugins share the same paradigm: <strong>define your intent in JSON</strong>, and let the plugin handle the rest.
</div>

<LatestNews :count="3" />
