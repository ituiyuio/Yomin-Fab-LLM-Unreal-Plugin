#!/usr/bin/env python3
"""Batch-render the YominUnreal plugin cover set.

The covers used to be assembled by hand in Photoshop, which made every
revision a manual re-do — and every one of the originals clips its second
headline line off the bottom of the canvas. This tool renders the same visual
language from a declarative manifest: one command, reproducible, and the
headline is auto-fitted so it can never overflow.

Usage:
    python tools/cover/generate.py                    # render every cover x variant
    python tools/cover/generate.py --only llm-material
    python tools/cover/generate.py --variant fab
    python tools/cover/generate.py --alt all          # render the alternative headlines
    python tools/cover/generate.py --list
    python tools/cover/generate.py --check

Requires the python `playwright` package plus a matching chromium build.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
import urllib.parse

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "covers.json"
TEMPLATE = HERE / "template" / "cover" / "cover.html"


def die(msg: str, code: int = 1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def file_url(path: pathlib.Path) -> str:
    # The drive letter's colon must survive quoting, otherwise Chromium reads
    # "file:///D%3A/..." and the image silently fails to load.
    return "file:///" + urllib.parse.quote(str(path.resolve()).replace("\\", "/"), safe="/:")


def optimize_png(path: pathlib.Path) -> None:
    """Re-save a rendered PNG with maximum compression.

    Playwright writes a default-compression PNG; these covers carry a full
    editor screenshot, so the extra few percent is worth the bytes.
    """
    with Image.open(path) as im:
        im.load()
        tmp = path.with_name(path.stem + ".opt.png")
        try:
            im.save(tmp, optimize=True, compress_level=9)
            tmp.replace(path)
        finally:
            # A crash between save and replace must not leave a stray .opt.png
            # for write_preview() to list in the contact sheet.
            tmp.unlink(missing_ok=True)


def load_manifest(path: pathlib.Path) -> dict:
    if not path.is_file():
        die(f"manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"manifest is not valid JSON: {exc}")
    for key in ("covers", "variants"):
        if key not in data:
            die(f"manifest is missing the '{key}' section")
    return data


def resolve_paths(manifest: dict, manifest_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    base = manifest_path.parent
    root = (base / manifest.get("root", "../..")).resolve()
    out = (root / manifest.get("output", "docs/public/covers")).resolve()
    return root, out


def check_env(manifest: dict, root: pathlib.Path) -> None:
    """Fail loudly and early on the two things that silently break rendering."""
    try:
        import playwright  # noqa: F401
    except ImportError:
        die(
            "python package 'playwright' is missing.\n"
            "  pip install playwright\n"
            "If chromium is not on disk yet: python -m playwright install chromium"
        )

    font = root / manifest.get("font", "tools/cover/fonts/Montserrat-Black.woff2")
    if not font.is_file():
        die(f"vendored font not found: {font}")

    template = HERE / "template" / "cover" / "cover.html"
    if not template.is_file():
        die(f"template not found: {template}")

    for cover in manifest["covers"]:
        if not cover.get("source"):
            continue
        src = root / cover["source"]
        if not src.is_file():
            die(f"source screenshot not found for '{cover['slug']}': {src}")


def headline_sets(cover: dict, alt_filter) -> list[tuple[str, list[str], str, dict, dict]]:
    """(file-suffix, lines, source, shot) tuples for one cover, honouring --alt.

    An alternative headline may carry its own background screenshot and crop —
    that is how the Photoshop originals were made: each gallery image pairs a
    different capture, framed differently, with a different tagline.
    """
    if not alt_filter:
        return [("", cover["lines"], cover["source"], cover.get("shot", {}), cover.get("style", {}))]
    picks = []
    for alt in cover.get("alt", []):
        if "all" in alt_filter or alt["name"] in alt_filter:
            picks.append((
                alt["name"],
                alt["lines"],
                alt.get("source", cover["source"]),
                alt.get("shot", cover.get("shot", {})),
                {**cover.get("style", {}), **alt.get("style", {})},
            ))
    return picks


def build_config(cover: dict, variant: dict, lines: list[str], source: str,
                 shot: dict, style: dict, root: pathlib.Path) -> dict:
    merged = dict(variant)
    merged.update(cover.get("variantOverrides", {}).get(variant["name"], {}))

    return {
        "width": merged["w"],
        "height": merged["h"],
        "inset": merged["inset"],
        "radius": merged["radius"],
        "padX": merged["padX"],
        "padY": merged["padY"],
        "baseFontSize": merged["baseFontSize"],
        "lineHeight": merged.get("lineHeight", 1.1),
        # number, not "-0.015em": cover.js does Math.max(tracking, 0.005) —
        # a string default silently NaNs the letter-spacing.
        "tracking": merged.get("tracking", -0.015),
        "maxHeightRatio": merged["maxHeightRatio"],
        "strokeRatio": merged["strokeRatio"],
        "scrimStart": merged["scrimStart"],
        "align": merged.get("align", "center"),
        "lines": lines,
        "layout": cover.get("layout", "cover"),
        "plate": cover.get("plate"),
        "list": cover.get("list", []),
        "listLabel": cover.get("listLabel", ""),
        "chips": cover.get("chips", []),
        "cta": cover.get("cta", ""),
        "titleOffset": cover.get("titleOffset", {}),
        "palette": cover.get("palette", {}),
        "shot": shot or {},
        "style": style,
        "source": file_url(root / source) if source else "",
    }


def render(manifest, root, out_dir, covers, variants, alt_filter) -> list[pathlib.Path]:
    from playwright.sync_api import sync_playwright

    font_url = file_url(root / manifest.get("font", "tools/cover/fonts/Montserrat-Black.woff2"))
    template = TEMPLATE.read_text(encoding="utf-8")
    css = (HERE / "template" / "cover" / "cover.css").read_text(encoding="utf-8")
    js = (HERE / "template" / "cover" / "cover.js").read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[pathlib.Path] = []

    with tempfile.TemporaryDirectory(prefix="cover-") as scratch, sync_playwright() as pw:
        scratch_dir = pathlib.Path(scratch)
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
            for cover in covers:
                for suffix, lines, source, shot, style in headline_sets(cover, alt_filter):
                    for vname, variant in manifest["variants"].items():
                        if variants and vname not in variants:
                            continue
                        cfg = build_config(cover, {**variant, "name": vname}, lines, source, shot, style, root)
                        html = (
                            template.replace("/*__CSS__*/", css)
                            .replace("/*__JS__*/", js)
                            .replace("__FONT_URL__", font_url)
                            .replace("/*__CONFIG__*/ null", json.dumps(cfg))
                        )
                        html_path = scratch_dir / f"{cover['slug']}-{suffix}-{vname}.html"
                        html_path.write_text(html, encoding="utf-8")
                        page.set_viewport_size({"width": cfg["width"], "height": cfg["height"]})
                        page.goto(html_path.as_uri())
                        page.wait_for_function("window.__READY__ === true", timeout=20000)
                        metrics = page.evaluate("window.__COVER_METRICS__ || null")
                        stem = f"{suffix}-{vname}" if suffix else vname
                        target = out_dir / cover["slug"] / f"{stem}.png"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(target))
                        optimize_png(target)
                        written.append(target)
                        fs = metrics["fontSize"] if metrics else "?"
                        widest = metrics["widest"] if metrics else "?"
                        loaded = metrics.get("fontLoaded") if metrics else "?"
                        rel = target.relative_to(out_dir).as_posix()
                        print(
                            f"  {rel:42} {cfg['width']}x{cfg['height']}"
                            f"  font={fs}px  widest={widest}  fontLoaded={loaded}"
                        )
        finally:
            browser.close()
    return written


def write_preview(out_dir: pathlib.Path) -> pathlib.Path:
    """Write a browsable contact sheet of everything that was rendered.

    The sheet mirrors the taxonomy on disk: one section per cover, one tile
    per image inside it. Files starting with "_" are scratch (the editor's
    export check) and never make it into the sheet.
    """
    files = sorted(
        p for p in out_dir.rglob("*.png")
        if not p.name.startswith("_") and p.parent != out_dir
    )
    groups: dict[str, list[tuple[str, int, int]]] = {}
    for f in files:
        with Image.open(f) as im:
            w, h = im.size
        rel = f.relative_to(out_dir).as_posix()
        groups.setdefault(f.parent.name, []).append((rel, w, h))

    sections = []
    for group, items in groups.items():
        tiles = "\n".join(
            f"""      <a class="card" href="{name}" target="_blank" rel="noreferrer">
        <img src="{name}" loading="lazy" alt="{name}">
        <span class="meta">{name.split('/')[-1]}<br>{w}×{h}</span>
      </a>"""
            for name, w, h in items
        )
        sections.append(
            f'  <section>\n    <h2>{group} <em>{len(items)}</em></h2>\n    <div class="grid">\n{tiles}\n    </div>\n  </section>'
        )

    count = sum(len(v) for v in groups.values())
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YominUnreal — cover set</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0d0d12; color: #e8e8ef;
    font: 14px/1.5 ui-sans-serif, system-ui, "Segoe UI", sans-serif;
    padding: 32px clamp(16px, 4vw, 64px) 64px;
  }}
  h1 {{ font-size: 22px; font-weight: 650; letter-spacing: -0.01em; }}
  .sub {{ color: #8a8a9e; margin-top: 4px; margin-bottom: 32px; }}
  section {{ margin-bottom: 40px; }}
  h2 {{
    font-size: 13px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #7f7f96; margin-bottom: 12px;
  }}
  h2 em {{ font-style: normal; color: #55556b; margin-left: 6px; }}
  .grid {{
    display: grid; gap: 18px;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }}
  .card {{
    display: block; text-decoration: none; color: inherit;
    background: #16161d; border: 1px solid #24242f; border-radius: 12px;
    overflow: hidden; transition: border-color .15s, transform .15s;
  }}
  .card:hover {{ border-color: #4a4a63; transform: translateY(-2px); }}
  .card img {{ display: block; width: 100%; height: auto; }}
  .meta {{ display: block; padding: 9px 12px; font-size: 12px; color: #8a8a9e; }}
</style>
</head>
<body>
  <h1>YominUnreal — cover set</h1>
  <div class="sub">{count} file(s) in {out_dir.name}/ — generated by <code>tools/cover/generate.py</code></div>
{chr(10).join(sections)}
</body>
</html>
"""
    index = out_dir / "index.html"
    index.write_text(html, encoding="utf-8")
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the plugin cover set.")
    ap.add_argument("--manifest", type=pathlib.Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--out", type=pathlib.Path, default=None, help="override the output directory")
    ap.add_argument("--only", action="append", default=None, help="slug filter (repeatable)")
    ap.add_argument("--variant", action="append", default=None, help="variant filter (repeatable)")
    ap.add_argument("--alt", action="append", default=None, help="alternative headline (repeatable, or 'all')")
    ap.add_argument("--list", action="store_true", help="list covers and exit")
    ap.add_argument("--check", action="store_true", help="verify prerequisites and exit")
    args = ap.parse_args()

    manifest = load_manifest(args.manifest)
    root, out_dir = resolve_paths(manifest, args.manifest)
    if args.out:
        out_dir = args.out.resolve()

    if args.list:
        print(f"root: {root}\nout:  {out_dir}\n")
        for cover in manifest["covers"]:
            print(f"  {cover['slug']:20} {cover['lines']}  <- {cover['source']}")
            for alt in cover.get("alt", []):
                print(f"    alt {alt['name']:10} {alt['lines']}")
        print("\nvariants:")
        for name, v in manifest["variants"].items():
            print(f"  {name:6} {v['w']}x{v['h']}")
        return 0

    check_env(manifest, root)
    if args.check:
        print("prerequisites OK")
        return 0

    covers = manifest["covers"]
    if args.only:
        wanted = set(args.only)
        unknown = wanted - {c["slug"] for c in covers}
        if unknown:
            die(f"unknown slug(s): {', '.join(sorted(unknown))}")
        covers = [c for c in covers if c["slug"] in wanted]

    variants = set(args.variant) if args.variant else None
    if variants:
        unknown = variants - set(manifest["variants"])
        if unknown:
            die(f"unknown variant(s): {', '.join(sorted(unknown))}")

    alt_filter = set(args.alt) if args.alt else None
    if alt_filter:
        known = {a["name"] for c in manifest["covers"] for a in c.get("alt", [])}
        unknown = alt_filter - known - {"all"}
        if unknown:
            die(f"unknown alt headline(s): {', '.join(sorted(unknown))}")

    print(f"rendering {len(covers)} cover(s) -> {out_dir}")
    written = render(manifest, root, out_dir, covers, variants, alt_filter)
    print(f"done: {len(written)} file(s)")

    index = write_preview(out_dir)
    print(f"preview: {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
