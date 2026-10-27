#!/usr/bin/env python3
"""Prove the live editor exports byte-identical PNGs to the CLI.

The editor is only worth trusting if what it renders IS the product. Both
paths share `cover.css` / `cover.js`, but the editor assembles its config in
`editor.js` while the CLI assembles it in `generate.py` — so the guarantee
has to be checked on real output, not assumed from the shared code.

    python tools/cover/editor.py --port 8821 &
    python tools/cover/check_editor.py 8821

Each case is rendered through the editor's own /api/render endpoint and
compared by SHA256 against the committed PNG in docs/public/covers/.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "docs" / "public" / "covers"

# Slugs to check, with the variants to check for each.
CASES = [
    ("llm-easy-shell-lite", ["fab", "hero", "og"]),
    ("llm-easy-shell-works-with", ["fab", "hero", "og"]),
    ("llm-easy-shell", ["fab", "hero", "og"]),
    ("yominunreal-plugins", ["fab", "hero", "og"]),
    ("llm-dynamic-ui", ["fab", "hero", "og"]),
    ("llm-material", ["fab", "hero", "og"]),
    ("llm-metasound", ["fab", "hero", "og"]),
    ("llm-statetree", ["fab", "hero", "og"]),
]


def post(base: str, path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def get(base: str, path: str) -> dict:
    with urllib.request.urlopen(base + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8821
    base = f"http://127.0.0.1:{port}"
    manifest = get(base, "/api/manifest")["manifest"]
    covers = {c["slug"]: c for c in manifest["covers"]}

    fails = 0
    checked = 0
    for slug, variants in CASES:
        cover = covers.get(slug)
        if cover is None:
            print(f"  {slug}: NOT IN MANIFEST")
            fails += 1
            continue
        for variant in variants:
            ref = OUT / slug / f"{variant}.png"
            if not ref.is_file():
                print(f"  {slug}-{variant}: no committed PNG to compare against")
                fails += 1
                continue
            name = f"_check-{variant}.png"
            res = post(base, "/api/render", {
                "slug": slug,
                "variant": variant,
                "lines": cover["lines"],
                "cover": cover,
                "name": name,
                "source": cover.get("source", ""),
                "shot": cover.get("shot", {}),
                "style": cover.get("style", {}),
            })
            tmp = OUT / slug / name
            try:
                if not res.get("ok"):
                    print(f"  {slug}-{variant}: RENDER FAILED {res}")
                    fails += 1
                    continue
                same = tmp.is_file() and sha(tmp) == sha(ref)
                checked += 1
                print(f"  {slug}-{variant:5} {'MATCH' if same else 'DIFF'}  {sha(ref)[:16]}")
                if not same:
                    fails += 1
            finally:
                tmp.unlink(missing_ok=True)

    print(f"checked {checked}, failures: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
