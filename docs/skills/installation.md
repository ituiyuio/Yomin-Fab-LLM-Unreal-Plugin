---
outline: [2, 3]
---

# Installation

Every skill is a single folder containing a `SKILL.md` file. Copy the skill folder into the location your AI tool scans, and it will be available next time you start a session.

The path your tool scans is **next to the project root** — for an Unreal project, that means the directory that contains your `.uproject`.

---

## TL;DR — Generic Install

```bash
# From the plugin repo (this repository):
SKILLS_SRC=./skills

# Target: <your UE project>/.claude/skills
TARGET=/path/to/YourUEProject/.claude/skills

# Copy all six skills
for s in llm-dynamic-ui llm-material llm-statetree llm-metasound llm-easy-shell llm-easy-shell-lite; do
  cp -r "$SKILLS_SRC/$s" "$TARGET/$s"
done
```

If your tool uses a different folder name (`.opencode/`, `.cursor/`, etc.), replace `.claude` with the right one. See the per-tool reference below.

---

## How to Get the Skills

The plugin repo ([github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin](https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin)) contains the full UE plugin source, the docs site, and all six skills. Three ways to get just the skill folders:

### Option A — Full clone (simplest, recommended for most users)

```bash
git clone https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin
cd Yomin-Fab-LLM-Unreal-Plugin
# Skills live under ./skills/<name>/SKILL.md
```

You can then copy the folders you want, or symlink them all:

```bash
TARGET=/path/to/YourUEProject/.claude/skills
mkdir -p "$TARGET"
for s in skills/llm-dynamic-ui skills/llm-material skills/llm-statetree \
         skills/llm-metasound skills/llm-easy-shell skills/llm-easy-shell-lite; do
  ln -s "$(pwd)/$s" "$TARGET/$(basename $s)"
done
```

Symlinks update automatically when the repo changes — no re-copy needed.

### Option B — Sparse checkout (smallest download, no history)

If you only need the skills and not the UE plugin source, pull just the `skills/` tree:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/ituiyuio/Yomin-Fab-LLM-Unreal-Plugin
cd Yomin-Fab-LLM-Unreal-Plugin
git sparse-checkout set skills
```

This downloads a few hundred KB of `SKILL.md` plus the bundled `llm-shell.exe` binaries — the plugin source tree is filtered out. To grab a single skill only:

```bash
git sparse-checkout set skills/llm-dynamic-ui
```

### Option C — Download ZIP (no git at all)

On the GitHub repo page → green **Code** button → **Download ZIP**. Extract it, then copy the `skills/<name>/` folders into your project's `<tool>/skills/` directory.

> **Note:** the ZIP always reflects the default branch HEAD. For a specific tagged release, use the **Releases** page on the right sidebar — each release attaches a source archive of that exact commit.

---

## Claude Code

Claude Code reads skills from `<project>/.claude/skills/<skill-name>/SKILL.md`. Skills are scoped to the project — different projects can have different skills.

```bash
# Inside your UE project (the folder with .uproject)
mkdir -p .claude/skills

# Copy only the skills you need
cp -r <plugin-repo>/skills/llm-dynamic-ui    .claude/skills/
cp -r <plugin-repo>/skills/llm-material      .claude/skills/
cp -r <plugin-repo>/skills/llm-statetree     .claude/skills/
cp -r <plugin-repo>/skills/llm-metasound     .claude/skills/
cp -r <plugin-repo>/skills/llm-easy-shell    .claude/skills/   # optional
cp -r <plugin-repo>/skills/llm-easy-shell-lite .claude/skills/ # optional
```

**Verify it works:** Start Claude Code in the project root and ask:

> "What skills do you have available?"

The agent should list all six skills it found. If a skill is missing, check that the folder name matches the `name:` field in the skill's frontmatter.

**Docs:** [Claude Code — Skills](https://docs.claude.com/en/docs/claude-code/skills)

---

## OpenCode

OpenCode reads skills from `<project>/.opencode/skills/<skill-name>/SKILL.md`. The convention is the same as Claude Code, just the root folder differs.

```bash
mkdir -p .opencode/skills
cp -r <plugin-repo>/skills/llm-dynamic-ui .opencode/skills/
# ... repeat for each skill
```

You can also register skills **globally** by placing them in `~/.config/opencode/skills/`. Those will be available in every project.

**Verify it works:** OpenCode prints the loaded skills at session start, or you can ask:

> "List your available skills."

---

## Cursor

Cursor reads skills from `<project>/.cursor/skills/<skill-name>/SKILL.md`. Same convention.

```bash
mkdir -p .cursor/skills
cp -r <plugin-repo>/skills/llm-dynamic-ui .cursor/skills/
# ... repeat for each skill
```

> **Note:** As of Cursor 1.0, the project-scoped skills directory is `.cursor/skills/`. If you are on an older version, check the [Cursor docs](https://docs.cursor.com/) for the current path.

---

## Codex (OpenAI)

OpenAI Codex reads skills from `<project>/.codex/skills/<skill-name>/SKILL.md`.

```bash
mkdir -p .codex/skills
cp -r <plugin-repo>/skills/llm-dynamic-ui .codex/skills/
# ... repeat for each skill
```

Codex also supports a `~/.codex/skills/` global location for skills shared across projects.

**Docs:** [OpenAI Codex — Skills](https://developers.openai.com/codex/skills)

---

## Per-Project vs. Global Install

| Scope | Path | Available in | Survives repo clone / re-install? |
|-------|------|--------------|------------------------------------|
| Project-scoped | `<project>/.claude/skills/` | That project only | Yes — commit it to share with your team |
| User-scoped (global) | `~/.claude/skills/` | All your projects | Survives, but is per-machine |

**Recommendation:** Install the asset-authoring skills (**llm-dynamic-ui**, **llm-material**, **llm-statetree**, **llm-metasound**) per-project, so the agent never confuses which DSL is in use. Install **llm-easy-shell** per-user if you work on multiple UE projects, since its command set is editor-driven and not tied to any one asset.

---

## One Project, Multiple Tools

If you use both Claude Code *and* Cursor on the same project, the simplest pattern is:

```bash
PROJECT=/path/to/YourUEProject
SRC=./skills

# Install to every tool the project uses
for tool in .claude .cursor .opencode .codex; do
  mkdir -p "$PROJECT/$tool/skills"
  cp -r "$SRC/llm-dynamic-ui"    "$PROJECT/$tool/skills/"
  cp -r "$SRC/llm-material"      "$PROJECT/$tool/skills/"
  cp -r "$SRC/llm-statetree"     "$PROJECT/$tool/skills/"
  cp -r "$SRC/llm-metasound"     "$PROJECT/$tool/skills/"
  cp -r "$SRC/llm-easy-shell"    "$PROJECT/$tool/skills/"
  cp -r "$SRC/llm-easy-shell-lite" "$PROJECT/$tool/skills/"
done
```

Add `.claude/`, `.cursor/`, etc. to `.gitignore` if you do not want the installed skills committed; or keep them in the repo if you want every team member to pick them up automatically.

---

## Updating a Skill

The plugin repo updates skills alongside plugin releases. To refresh a single skill:

```bash
# Pull the latest plugin repo
cd <plugin-repo>
git pull

# Re-copy the one skill that changed
cp -r skills/llm-dynamic-ui <project>/.claude/skills/llm-dynamic-ui
```

Restart the AI tool's session to pick up the new content.

---

## Removing a Skill

```bash
rm -rf <project>/.claude/skills/llm-easy-shell
```

The agent will simply not see that skill on the next session.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent does not list the skill | Check the folder name matches the `name:` field in the YAML frontmatter |
| Agent loads the skill but its instructions are stale | Restart the session — most tools only scan skills on session start |
| Skill loads but the agent does not use it | Check the frontmatter `description:` — that is what the agent matches against your prompt |
| Frontmatter is malformed | Skills are YAML — make sure the `---` fences are intact and there is a `name:` field |
| `llm-easy-shell` commands time out | Make sure the UE editor is running and the `LLMEasyShell` plugin is enabled (see [LLM Easy Shell →](./llm-easy-shell)) |
