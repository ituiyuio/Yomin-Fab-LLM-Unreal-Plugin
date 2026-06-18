# News — Maintainer Guide

This directory holds news entries. Each entry is one `.md` file named
`YYYY-MM-DD-<slug>.md` (date is the publish date; the `slug` is purely
human-friendly, the URL segment is driven by the `slug` front-matter).

## Required front-matter

```yaml
---
title: Agent Online                          # required
date: 2026-06-19                             # required, YYYY-MM-DD, drives sort
tag: Release                                 # required, see table below
summary: |                                   # required, 1-3 line teaser
  AI 代理现可通过 LLM Easy Shell 直连 UE 编辑器…
emoji: ⚡                                    # optional, large icon on home banner
slug: agent-online                           # required, URL segment, kebab-case
---
```

## Tag vocabulary (controlled)

| Tag      | Meaning                  | Color (hex) |
|----------|--------------------------|-------------|
| Release  | Major release            | `#e06c75`   |
| Plugin   | New plugin / sub-module  | `#c678dd`   |
| Skill    | AI skill related         | `#61afef`   |
| Update   | General feature update   | `#e5c07b`   |
| Fix      | Bug fix                  | `#98c379`   |

Don't introduce new tags without updating this table.
