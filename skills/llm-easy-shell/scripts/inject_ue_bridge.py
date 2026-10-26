#!/usr/bin/env python3
"""
inject_ue_bridge.py — inject a <script src="..._shared/ue-bridge.js"></script>
tag into every HUD/Html/**/*.html (recursive) that uses ue:// but doesn't yet
include the shim.

Idempotent: skips files that already include '_shared/ue-bridge.js'.
Depth-aware: the src is computed per file from its nesting depth — the shim
lives at <Feature>/_shared/, pages live at Html/<subdir>/page.html, so a
hardcoded '../../' produced a broken include for one-level-deep pages
(correct form is '../../../_shared/ue-bridge.js', cf. MainMenu/GameOver.html).
Safe: only inserts before the FIRST <script> tag (or before </body> / EOF).
Drift detection: non-zero exit if no files were modified AND any target file
still lacks the include (catches stale worktree / merge residue).

r2161 + 2026-10-26 alignment with verify-e2e.py's ue-bridge coverage lock:
  - rglob (the 2026-08-28 Html restructure moved every page into subdirs;
    the old top-level glob matched an empty set, same bug the verifier had)
  - same PAT_UE_LEGACY surface (uecallback / answercallback / uebridge.broadcast)
  - same include matcher ('_shared/ue-bridge.js' exact substring — a bare
    'ue-bridge.js' mention in a comment is NOT an include)

Pattern: tool-fix-07 session88 (2026-07-10) closure of
  sg-webui-bridge-onconsolemsg-fallback-2026-07-09 memory caveat
  "其它 63+ HTML 后续 batch 改" (actual count = 120).
"""
import os
import sys
import re
from pathlib import Path

# .claude/skills/llm-easy-shell/scripts/inject_ue_bridge.py
#   ↑ scripts/ ↑ llm-easy-shell/ ↑ skills/ ↑ .claude/ ↑ CODEO/ (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
HTML_DIR = PROJECT_ROOT / 'Content' / 'Features' / 'Survivor' / 'HUD' / 'Html'
SHARED_DIR = PROJECT_ROOT / 'Content' / 'Features' / 'Survivor' / '_shared'
BRIDGE_INC = '_shared/ue-bridge.js'   # matches verify-e2e.py's bridge_inc
PAT_FIRST_SCRIPT = re.compile(r'<script[\s>]')

# Patterns — 1:1 with verify-e2e.py's ue-bridge coverage lock
PAT_UE_INLINE = re.compile(r"window\.location\.href\s*=.*ue://")
PAT_UE_HELPER = re.compile(r"function\s+(ue|ueAction)\s*\(")
# Indirect call sites: window.location.href = url where url is a parameter (e.g. fadeThenNavigate(url))
# plus direct ue:// string args (fadeThenNavigate('ue://X'), navigate('ue://X'))
PAT_UE_INDIRECT = re.compile(
    r"function\s+(fadeThenNavigate|navigate|navTo|goto)\s*\("
    r"|(?:fadeThenNavigate|navigate|navTo|goto)\s*\(\s*['\"]ue://"
)
# session94 legacy per-widget helpers — predate the shim rollout, bypass the
# location.href setter override, therefore need the shim too
PAT_UE_LEGACY = re.compile(
    r"function\s+uecallback\s*\("
    r"|\bue\.answercallback\s*\("
    r"|window\.ue\.uebridge\.broadcast\s*\("
)


def uses_ue(text: str) -> bool:
    return bool(
        PAT_UE_INLINE.search(text)
        or PAT_UE_HELPER.search(text)
        or PAT_UE_INDIRECT.search(text)
        or PAT_UE_LEGACY.search(text)
    )


def include_tag_for(path: Path) -> str:
    """src computed from the page's real nesting depth (see module docstring)."""
    src = os.path.relpath(SHARED_DIR / "ue-bridge.js", start=path.parent)
    return f'<script src="{src.replace(os.sep, "/")}"></script>'


def files_needing_fix():
    """Find HTML files that use ue:// but don't include the shim yet."""
    out = []
    for f in sorted(HTML_DIR.rglob('*.html')):
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        if not uses_ue(text):
            continue
        if BRIDGE_INC in text:
            continue
        out.append(f)
    return out


def inject(path: Path) -> bool:
    """Insert the include tag before the first <script> tag. Returns True if changed."""
    text = path.read_text(encoding='utf-8')
    include_tag = include_tag_for(path)
    m = PAT_FIRST_SCRIPT.search(text)
    if not m:
        # No <script> tag — append before </body> or at EOF as fallback
        if '</body>' in text:
            new_text = text.replace('</body>', f'{include_tag}\n</body>', 1)
        else:
            new_text = text.rstrip() + f'\n{include_tag}\n'
    else:
        new_text = text[:m.start()] + include_tag + '\n' + text[m.start():]
    if new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def main():
    if not HTML_DIR.is_dir():
        print(f'ERROR: content tree absent: {HTML_DIR} '
              f'(run inside a consumer project)')
        return 2
    targets = files_needing_fix()
    print(f'HUD/Html files using ue:// pattern: {len(targets)}')
    modified = 0
    skipped = 0
    for f in targets:
        if inject(f):
            modified += 1
        else:
            skipped += 1
    print(f'Injected include into {modified} files, skipped {skipped} (no change needed).')

    # Drift detection — verify every ue:// file now has the include
    drifted = []
    for f in sorted(HTML_DIR.rglob('*.html')):
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        if not uses_ue(text):
            continue
        if BRIDGE_INC not in text:
            drifted.append(str(f.relative_to(PROJECT_ROOT)))
    if drifted:
        print(f'DRIFT: {len(drifted)} files still missing ue-bridge.js include:')
        for d in drifted[:10]:
            print(f'  - {d}')
        if len(drifted) > 10:
            print(f'  ... +{len(drifted) - 10} more')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
