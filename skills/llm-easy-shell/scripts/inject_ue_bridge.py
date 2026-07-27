#!/usr/bin/env python3
"""
inject_ue_bridge.py — inject <script src="../../_shared/ue-bridge.js"></script>
into every HUD/Html/*.html that uses ue:// but doesn't yet include the shim.

Idempotent: skips files that already include 'ue-bridge.js'.
Safe: only inserts before the FIRST <script> tag (or after </style> if no <script>).
Drift detection: emits a non-zero exit code if no files were modified AND any target
file lacks the include (catches stale worktree / merge residue).

Pattern: tool-fix-07 session88 (2026-07-10) closure of
  sg-webui-bridge-onconsolemsg-fallback-2026-07-09 memory caveat
  "其它 63+ HTML 后续 batch 改" (actual count = 120).
"""
import sys
import re
import glob
from pathlib import Path

# .claude/skills/llm-easy-shell/scripts/inject_ue_bridge.py
#   ↑ scripts/ ↑ llm-easy-shell/ ↑ skills/ ↑ .claude/ ↑ CODEO/ (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
HTML_DIR = PROJECT_ROOT / 'Content' / 'Features' / 'Survivor' / 'HUD' / 'Html'
SHIM_HREF = '../../_shared/ue-bridge.js'
INCLUDE_TAG = f'<script src="{SHIM_HREF}"></script>'

# Patterns
PAT_UE_INLINE = re.compile(r"window\.location\.href\s*=.*ue://")
PAT_UE_HELPER = re.compile(r"function\s+(ue|ueAction)\s*\(")
# Indirect call sites: window.location.href = url where url is a parameter (e.g. fadeThenNavigate(url))
# plus direct ue:// string args (fadeThenNavigate('ue://X'), navigate('ue://X'))
PAT_UE_INDIRECT = re.compile(
    r"function\s+(fadeThenNavigate|navigate|navTo|goto)\s*\("
    r"|(?:fadeThenNavigate|navigate|navTo|goto)\s*\(\s*['\"]ue://"
)
PAT_BRIDGE = re.compile(r'ue-bridge\.js')
PAT_FIRST_SCRIPT = re.compile(r'<script[\s>]')


def files_needing_fix():
    """Find HTML files that use ue:// but don't include the shim yet."""
    out = []
    for f in sorted(HTML_DIR.glob('*.html')):
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        has_ue = (
            PAT_UE_INLINE.search(text)
            or PAT_UE_HELPER.search(text)
            or PAT_UE_INDIRECT.search(text)
        )
        if not has_ue:
            continue
        if PAT_BRIDGE.search(text):
            continue
        out.append(f)
    return out


def inject(path: Path) -> bool:
    """Insert the include tag before the first <script> tag. Returns True if changed."""
    text = path.read_text(encoding='utf-8')
    m = PAT_FIRST_SCRIPT.search(text)
    if not m:
        # No <script> tag — append before </body> or at EOF as fallback
        if '</body>' in text:
            new_text = text.replace('</body>', f'{INCLUDE_TAG}\n</body>', 1)
        else:
            new_text = text.rstrip() + f'\n{INCLUDE_TAG}\n'
    else:
        new_text = text[:m.start()] + INCLUDE_TAG + '\n' + text[m.start():]
    if new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def main():
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
    for f in sorted(HTML_DIR.glob('*.html')):
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        has_ue = (
            PAT_UE_INLINE.search(text)
            or PAT_UE_HELPER.search(text)
            or PAT_UE_INDIRECT.search(text)
        )
        if not has_ue:
            continue
        if not PAT_BRIDGE.search(text):
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