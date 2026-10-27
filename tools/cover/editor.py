#!/usr/bin/env python3
"""Live cover editor — the Photoshop-free way to art-direct the plugin covers.

Serves a local editor that renders the *real* cover (same CSS/JS as the CLI
renderer, so the preview is the export) and writes your changes straight back
into `tools/cover/covers.json`.

    python tools/cover/editor.py            # start the editor
    python tools/cover/editor.py --port 8790
    python tools/cover/editor.py --open     # also launch the system browser

The server binds 127.0.0.1 only; nothing is exposed to the network.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import socket
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "template"
RENDER_TEMPLATE = TEMPLATE / "cover"      # the shared renderer (cover.*)
EDITOR_TEMPLATE = TEMPLATE / "editor"    # the editor's own UI (editor.*)
MANIFEST = HERE / "covers.json"

sys.path.insert(0, str(HERE))
from generate import optimize_png, write_preview  # noqa: E402  (same directory)

REPO_ROOT = HERE.parent.parent
RAW_DIR = REPO_ROOT / "raw"


def out_dir() -> pathlib.Path:
    """Output dir from the manifest — stays in sync with generate.py."""
    manifest = load_manifest()
    root = (HERE / manifest.get("root", "../..")).resolve()
    return (root / manifest.get("output", "docs/public/covers")).resolve()

_lock = threading.Lock()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(data: dict) -> None:
    MANIFEST.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def list_sources() -> list[str]:
    """Every image under raw/ — the pool the editor can pull backgrounds from."""
    out = []
    if RAW_DIR.is_dir():
        for p in sorted(RAW_DIR.rglob("*.png")):
            out.append(p.relative_to(REPO_ROOT).as_posix())
    return out


def file_url(path: pathlib.Path) -> str:
    return "file:///" + urllib.parse.quote(str(path.resolve()).replace("\\", "/"), safe="/:")


def build_config(manifest: dict, cover: dict, variant_name: str, lines: list[str],
                 source: str | None = None, shot: dict | None = None,
                 style: dict | None = None) -> dict:
    variant = dict(manifest["variants"][variant_name])
    variant.update(cover.get("variantOverrides", {}).get(variant_name, {}))
    return {
        "width": variant["w"],
        "height": variant["h"],
        "inset": variant["inset"],
        "radius": variant["radius"],
        "padX": variant["padX"],
        "padY": variant["padY"],
        "baseFontSize": variant["baseFontSize"],
        "lineHeight": variant.get("lineHeight", 1.1),
        "tracking": variant.get("tracking", -0.015),
        "maxHeightRatio": variant["maxHeightRatio"],
        "strokeRatio": variant["strokeRatio"],
        "scrimStart": variant["scrimStart"],
        "align": variant.get("align", "center"),
        "lines": lines,
        "layout": cover.get("layout", "cover"),
        "plate": cover.get("plate"),
        "list": cover.get("list", []),
        "listLabel": cover.get("listLabel", ""),
        "chips": cover.get("chips", []),
        "cta": cover.get("cta", ""),
        "titleOffset": cover.get("titleOffset", {}),
        "palette": cover.get("palette", {}),
        "shot": shot if shot is not None else cover.get("shot", {}),
        "style": style if style is not None else cover.get("style", {}),
        "source": file_url(REPO_ROOT / (source or cover["source"])) if (source or cover.get("source")) else "",
    }


def render_png(manifest: dict, cover: dict, variant_name: str, lines: list[str], out: pathlib.Path,
               source: str | None = None, shot: dict | None = None,
               style: dict | None = None) -> pathlib.Path:
    from playwright.sync_api import sync_playwright

    cfg = build_config(manifest, cover, variant_name, lines, source, shot, style)
    tpl = (RENDER_TEMPLATE / "cover.html").read_text(encoding="utf-8")
    css = (RENDER_TEMPLATE / "cover.css").read_text(encoding="utf-8")
    js = (RENDER_TEMPLATE / "cover.js").read_text(encoding="utf-8")
    html = (
        tpl.replace("/*__CSS__*/", css)
        .replace("/*__JS__*/", js)
        .replace("__FONT_URL__", file_url(REPO_ROOT / manifest.get("font", "tools/cover/fonts/Montserrat-Black.woff2")))
        .replace("/*__CONFIG__*/ null", json.dumps(cfg))
    )
    tmp = HERE / ".editor-render.tmp.html"
    tmp.write_text(html, encoding="utf-8")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page(
                    viewport={"width": cfg["width"], "height": cfg["height"]},
                    device_scale_factor=1,
                )
                page.goto(tmp.as_uri())
                page.wait_for_function("window.__READY__ === true", timeout=30000)
                out.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(out))
            finally:
                browser.close()
    finally:
        tmp.unlink(missing_ok=True)
    optimize_png(out)
    return out


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "CoverEditor/1.0"

    def log_message(self, fmt, *args):  # keep the console readable
        pass

    # ---- helpers -------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str, cache: bool = False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=60" if cache else "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8"))

    # ---- GET ------------------------------------------------------------
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path in ("/", "/index.html"):
                return self._editor_page()
            if path == "/static/cover.css":
                css = (RENDER_TEMPLATE / "cover.css").read_text(encoding="utf-8")
                css = css.replace("__FONT_URL__", self._font_url())
                return self._send(200, css.encode("utf-8"), "text/css; charset=utf-8")
            if path == "/static/cover.js":
                return self._send(200, (RENDER_TEMPLATE / "cover.js").read_bytes(), "application/javascript; charset=utf-8")
            if path == "/static/editor.css":
                return self._send(200, (EDITOR_TEMPLATE / "editor.css").read_bytes(), "text/css; charset=utf-8")
            if path == "/static/editor.js":
                return self._send(200, (EDITOR_TEMPLATE / "editor.js").read_bytes(), "application/javascript; charset=utf-8")
            if path == "/static/font.woff2":
                return self._font()
            if path == "/favicon.ico":
                return self._send(204, b"", "image/x-icon")
            if path == "/api/manifest":
                return self._manifest()
            if path.startswith("/asset/"):
                return self._asset(path[len("/asset/"):])
            self._json({"error": "not found", "path": path}, 404)
        except Exception as exc:  # never take the server down on one bad request
            self._json({"error": repr(exc)}, 500)

    def _font_url(self) -> str:
        # The live editor is served over http, and Chromium refuses to pull a
        # file:// subresource into an http:// page — the preview would then
        # render in the fallback face and measure the headline against the
        # wrong metrics, so the preview would not match the export. Serve the
        # vendored face over the same origin instead.
        return "/static/font.woff2"

    def _font(self):
        manifest = load_manifest()
        font = (REPO_ROOT / manifest.get("font", "tools/cover/fonts/Montserrat-Black.woff2")).resolve()
        if not font.is_file():
            return self._json({"error": "font not found", "path": str(font)}, 404)
        return self._send(200, font.read_bytes(), "font/woff2")

    def _editor_page(self):
        html = (EDITOR_TEMPLATE / "editor.html").read_text(encoding="utf-8")
        html = html.replace("__FONT_URL__", self._font_url())
        self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")

    def _manifest(self):
        with _lock:
            data = load_manifest()
        self._json({
            "manifest": data,
            "sources": list_sources(),
            "repoRoot": REPO_ROOT.as_posix(),
        })

    def _asset(self, rel: str):
        rel = urllib.parse.unquote(rel)
        target = (REPO_ROOT / rel).resolve()
        try:
            target.relative_to(REPO_ROOT.resolve())
        except ValueError:
            return self._json({"error": "forbidden"}, 403)
        if not target.is_file():
            return self._json({"error": "not found", "rel": rel}, 404)
        ctype = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".woff2": "font/woff2", ".json": "application/json",
        }.get(target.suffix.lower(), "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    # ---- POST -----------------------------------------------------------
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path == "/api/save":
                return self._save()
            if path == "/api/render":
                return self._render()
            self._json({"error": "not found"}, 404)
        except Exception as exc:
            self._json({"error": repr(exc)}, 500)

    def _save(self):
        body = self._body()
        slug = body.get("slug")
        cover = body.get("cover")
        if not slug or not isinstance(cover, dict):
            return self._json({"error": "slug and cover are required"}, 400)
        with _lock:
            data = load_manifest()
            covers = data.get("covers", [])
            hit = False
            for i, c in enumerate(covers):
                if c.get("slug") == slug:
                    covers[i] = cover
                    hit = True
                    break
            if not hit:
                return self._json({"error": f"unknown cover '{slug}'"}, 404)
            save_manifest(data)
        self._json({"ok": True, "slug": slug})

    def _render(self):
        body = self._body()
        slug = body.get("slug")
        variant = body.get("variant", "fab")
        lines = body.get("lines") or []
        cover = body.get("cover")
        if not slug or not isinstance(cover, dict):
            return self._json({"error": "slug and cover are required"}, 400)
        with _lock:
            manifest = load_manifest()
        # The folder comes from the slug, never from the caller's file name —
        # and the slug has to be a cover the manifest knows, so a crafted
        # value cannot walk out of the output directory. The name is only the
        # file inside that folder.
        folder = pathlib.PurePosixPath(str(slug)).name
        known = {c.get("slug") for c in manifest.get("covers", [])}
        if folder not in known:
            return self._json({"error": f"unknown cover '{slug}'"}, 400)
        name = pathlib.PurePosixPath(str(body.get("name") or f"{variant}.png")).name
        target_dir = (out_dir() / folder).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        out = (target_dir / name).resolve()
        if out.parent != target_dir:
            return self._json({"error": "invalid name"}, 400)
        render_png(manifest, cover, variant, lines, out,
                   source=body.get("source"), shot=body.get("shot"),
                   style=body.get("style"))
        # the contact sheet belongs to the whole set, not to one cover folder
        write_preview(out_dir())
        self._json({"ok": True, "path": out.relative_to(REPO_ROOT).as_posix(),
                    "url": "/asset/" + out.relative_to(REPO_ROOT).as_posix()})


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="Live cover editor.")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--open", action="store_true", help="launch the system browser too")
    args = ap.parse_args()

    port = args.port or free_port()
    url = f"http://127.0.0.1:{port}/"
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"cover editor  ->  {url}")
    print(f"  manifest: {MANIFEST}")
    print("  ctrl-c to stop")
    if args.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
