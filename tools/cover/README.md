# tools/cover — plugin cover generator & editor

Renders the YominUnreal plugin covers (Fab listing images, README banner, docs
OG card) from a declarative manifest, and gives you a live editor to art-direct
them without opening Photoshop.

```
python tools/cover/generate.py                     # render the primary set
python tools/cover/generate.py --only llm-material
python tools/cover/generate.py --variant fab
python tools/cover/generate.py --alt all           # the alternative headlines
python tools/cover/generate.py --list
python tools/cover/generate.py --check             # verify prerequisites

python tools/cover/editor.py                       # live editor (the PS replacement)
```

**Reproducing the committed set** takes two passes — `--alt` *replaces* the
primary headlines, it does not add to them:

```
python tools/cover/generate.py                            # 12 primary PNGs
python tools/cover/generate.py --alt all --variant fab    # 8 alt-gallery PNGs
```

## Source material

`raw/` is **local, untracked scratch** — UE captures (one folder per plugin)
plus the PSD working file. It is not in the repo: a fresh clone does not have
it, and `--check` will fail on the missing screenshots until you supply them.
Manifest `source` paths are repo-root-relative. Only the rendered outputs
under `docs/public/covers/` are committed.

## Scope

Covers exist for the four Fab-listed plugins (llm-dynamic-ui, llm-material,
llm-statetree, llm-metasound). `llm-easy-shell` / `-lite` are CLI skills with
no Fab listing — they deliberately get no cover; the README banner and the
site OG card reuse `llm-dynamic-ui`.

## The type system

The headline is an **advertising lockup**, not a caption:

```
▬▬  LLM MATERIAL          ← kicker: light label + accent rule
One chat                   ← hero line: near-white, 900, big
to rule them all           ← supporting line: accent colour, smaller
```

Two decisions do most of the work:

1. **The bottom fades to a deep base, not to the raw accent.** The accent
   colours are light (sky blue, teal, periwinkle), so fading to them left
   the headline fighting a light background — that was the readability bug.
   `style.baseMix` controls how much accent survives in the base (0.28 ≈ a
   deep, tinted near-black). Every plugin now gets the same contrast floor
   while keeping its hue.

2. **The hero line is near-white and the supporting line carries the accent.**
   `style.heroLine` picks which line is the hero; `style.heroScale` /
   `style.subScale` set the size ratio. A flat fill reads crisp where a
   gradient across the glyphs turns to mud; the hero gets a whisper of sheen
   (white → its own colour) so it does not read flat.

The keyline around the glyphs is the deep base colour and is deliberately thin
(`strokeRatio`, default 0.035). The old thick accent-coloured outline ate the
counters and made small sizes blobby.

## Acid & laser

Two additive systems, each on its own knob, so you can dial them down to
almost nothing (the default look) or up:

**`style.acid`** — iridescence.
- A conic spectrum wash over the backdrop (`hard-light`, so the gradient keeps
  its value structure while the hue swings).
- The headline fill becomes prismatic: the five stops are mixed in JS between
  the line's own colour and a spectrum (cyan → white → magenta → lime → cyan).
  The hero takes the full amount, the supporting line 45% of it.

**`style.laser`** — light.
- Two wide, soft beams crossing the whole cover (`screen` blend). The falloff
  is deliberately wide: a narrow bright band reads as a stripe, not as light in
  the air.
- A lens artefact in the upper left: a hot point plus a horizontal streak.

**`style.prism`** — the R/G/B split on the specular sheen, so a rainbow fringe
rides the edge of the highlight. Nearly free (0.03 MB across the set).

> The fill gradient is built in JS, not with `color-mix()`: that function is
> missing from some Chromium builds and silently drops the whole `background`
> declaration, which leaves the headline as an empty outline.

## Highlights

Three speculars, each on its own knob:

- **`style.gloss`** — a wet/chrome band across the **upper part of the glyphs**.
  Implemented as a fourth text layer clipped to the letterforms, sitting on top
  of the fill, so the type catches the light instead of reading flat.
- **`style.glint`** — one sharp, narrow specular line riding the broad sheen
  across the plate.
- **`style.sparkle`** — star glints on the plate (a hot core plus a crossed
  streak), the small hard specular points a lens makes. Their positions are
  fixed in `cover.js` (`R.sparks`).

## Finish: texture and light

The cover is lit from the **top-left** and the plate reads as a physical
object, not a pasted rectangle:

| layer | what it does | knob |
|-------|--------------|------|
| cast shadow | the frame drops onto the accent backdrop | `--inset` gives it room to fall |
| bevel | top edge catches a rim light, bottom edge falls into shadow | fixed in `cover.css` |
| edge shade | ambient occlusion darkening the plate into its own frame | `style.ao` |
| specular sweep | a broad sheen plus a tight glint across the plate | `style.sweep` |
| vignette | pulls the eye to the middle | `style.vignette` |
| contact + ambient shadow | the headline sits ON the image instead of floating | `style.shadow` |
| glow | coloured bloom behind the plate | `style.glowStrength` |
| grain | print-like texture | `style.grain` — **off by default** |

**Grain is off by default on purpose.** Fine noise is incompressible: it added
~330 kB per PNG (6.7 MB across the set) for a texture that is invisible at 3×
zoom. Quantising the turbulence to three levels makes it *more* expensive, not
less. Turn it on if you want it; you are paying for it in bytes.

## The editor

```
python tools/cover/editor.py             # http://127.0.0.1:<port>/
python tools/cover/editor.py --port 8807
python tools/cover/editor.py --open      # also launch the system browser
```

It serves a local page (127.0.0.1 only) that renders the **real** cover with
the same `cover.css` / `cover.js` the CLI exports with — so the preview is the
export, not an approximation. Changes are written straight back into
`covers.json` by **Save**; **Export PNG** renders a single file immediately.

| gesture | effect |
|---------|--------|
| drag the screenshot | reposition the background image |
| drag the headline | move the title block |
| wheel over the canvas | zoom the background image |
| shift + wheel | zoom the headline |

The left panel exposes every knob the renderer knows about: headline text,
size, line height, tracking, alignment, title offset, safe-area margins, the
source screenshot (any PNG under `raw/`), crop zoom/focus, frame margin and
corner radius, scrim position, the four palette colours, and the finish pass
(glow, grain, vignette, sweep, light beam, text shadow, badge).

**Guides** overlays the safe area and centre lines.

## Output

`docs/public/covers/` (the VitePress public dir, so the docs site and the
README serve the same files):

| variant | size      | used for                                  |
|---------|-----------|-------------------------------------------|
| `fab`   | 1920×1080 | Epic Fab listing cover / gallery images   |
| `hero`  | 1280×640  | GitHub README banner + repo social preview |
| `og`    | 1200×630  | Open Graph / Twitter card for the docs site |

Every run also writes `index.html` next to the images — a browsable contact
sheet of the whole set. It lands in the docs site as `/covers/`.

## Requirements

- Python `playwright` package **and** a chromium build it can find.
  If chromium is missing: `python -m playwright install chromium`.
  The playwright version must match the on-disk chromium build number — if it
  does not, playwright tries to download a different browser instead of using
  the one you have.
- `Pillow` (reading the generated image sizes for the contact sheet).

## The manifest — `covers.json`

```jsonc
{
  "root": "../..",                       // repo root, relative to this file
  "output": "docs/public/covers",
  "font": "tools/cover/fonts/Montserrat-Black.woff2",

  "variants": {
    "fab": {
      "w": 1920, "h": 1080,
      "inset": 20,                        // frame margin from the canvas edge
      "radius": 120,                      // frame corner radius
      "padX": 96, "padY": 30,             // headline safe area
      "baseFontSize": 190,                // starting size; auto-shrinks if needed
      "lineHeight": 1.1,
      "maxHeightRatio": 0.54,             // headline may not exceed this much height
      "strokeRatio": 0.035,               // outline width as a fraction of the font size
      "scrimStart": 36,                   // % where the bottom scrim starts
      "align": "center",
      "tracking": -0.015                  // em
    }
  },

  "covers": [
    {
      "slug": "llm-material",
      "source": "raw/llmmat/Screenshot_20260422211840.png",
      "shot": { "zoom": 1.12, "focusX": 0.0, "focusY": 0.43 },
      "titleOffset": { "x": 0, "y": 0 },
      "palette": {
        "frameTop": "#8EC3E6",             // accent gradient, top
        "frameBottom": "#8A89DF",          // accent gradient, bottom (= scrim colour)
        "titleFill": "#8EC3E6",            // headline fill (defaults to frameTop)
        "titleStroke": "#8353D7"           // headline outline
      },
      "style": {
        "kicker": "LLM Material",
        "kickerStyle": "rule",          // "rule" | "pill" | "none"
        "kickerColor": "#EDF1FF",
        "kickerRule": "#8EC3E6",
        "titleColor": "#FFFFFF",        // hero line colour
        "subColor": "#8EC3E6",          // supporting lines
        "heroLine": 0,                  // index of the hero line; -1 = all equal
        "heroScale": 1.0,
        "subScale": 0.6,
        "baseMix": 0.28,                // accent kept in the deep base
        "grain": 0.0,                   // off by default — see "Finish" below
        "ao": 0.28,
        "acid": 0.32, "laser": 0.3, "prism": 0.25,
        "gloss": 0.72, "glint": 0.8, "sparkle": 0.75
      },
      "lines": ["One chat", "to rule them all"],
      "alt": [
        {
          "name": "gui",
          "lines": ["User-friendly", "GUI"],
          "source": "raw/llmmat/Screenshot_20260422211713.png",
          "shot": { "zoom": 1.08, "focusX": 0.47, "focusY": 0.0 }
        }
      ]
    }
  ]
}
```

### One cover, several gallery images

Each alternative headline may carry **its own background screenshot and its own
crop**. That mirrors how the Photoshop originals were made: every gallery image
paired a different capture, framed differently, with a different tagline —
"User-friendly GUI" showed the empty Material Bridge, "ALL DOMAIN Support"
showed a different material preview, "RICH Examples" showed the content
browser. Anything an alt does not override falls back to the cover's
`source` / `shot`.

The correspondence was recovered by correlating each original cover's frame
interior against every candidate capture in its folder — and then checked by
eye, because the correlation is easy to fool: a high-contrast content browser
correlates well with almost any dark screenshot.

### `shot` — the crop of the source screenshot

`zoom` and `focusX`/`focusY` describe **which window of the source image** ends
up in the frame. `zoom: 1` is "as much as fits"; `focus` is the normalised
centre of that window (`0` = top/left, `1` = bottom/right). These were
recovered from the Photoshop originals by correlating each cover's frame
interior against its source image — correlating the **upper** half only, since
the lower band is covered by the headline and the accent scrim.

### `palette`

The headline fill always equals `frameTop` in the current set; `titleStroke` is
the per-plugin contrast colour. The bottom scrim fades into `frameBottom`, so
the screenshot dissolves into the backdrop instead of ending on a hard edge.

### `variantOverrides`

Per-cover overrides of a variant's geometry — what the editor writes when you
tune the hero but not the fab. Anything not overridden falls back to
`variants.<name>`.

## How the template works — `template/`

`cover.css` + `cover.js` are the single source of truth, shared by the CLI
renderer and the editor. Layers, bottom to top:

1. **Backdrop** — a vertical gradient from `frameTop` to `frameBottom`, plus a
   soft coloured bloom behind the frame.
2. **Frame** — the screenshot, inset by `inset` with a `radius` corner radius,
   an inner hairline, a vignette, and a specular sweep across the plate.
3. **Scrim** — a bottom-anchored gradient into `frameBottom`.
4. **Grain** — an SVG turbulence overlay, so the frame is not flat.
5. **Headline** — two stacked copies of the same text: the back one paints
   only the stroke (`-webkit-text-stroke`), the front one paints only the
   gradient fill (`background-clip: text`). Stacking them keeps the outline
   strictly *outside* the glyph — a single stroked element would eat into the
   fill.
6. **Badge** — an optional frosted pill above the headline.

The headline is **auto-fitted**: the page measures the widest line and shrinks
the font size until the block fits inside the safe area. The webfont is
explicitly awaited (`document.fonts.load`) before measuring — measuring against
a fallback face yields a narrower width, and the headline then overflows once
the real face swaps in.

## Changing the typeface

Drop a `woff2` into `tools/cover/fonts/` and point `"font"` at it. The face is
vendored rather than loaded from a CDN so a cover renders identically on any
machine, offline.

The original Photoshop typeface could not be recovered: the source PSD only
carries Adobe's CJK fallback chain (`PhotoshopKinsokuHard`, `SourceHanSansSC-
Heavy`, …), not the face that was actually used. **Montserrat Black** is the
closest available match — same double-storey `a` with a flat diagonal
terminal, near-circular `O`, and a flat-topped `t`. Swap the file and re-run
if you have the original.

Fonts must be licensed for redistribution. The vendored **Montserrat** is
SIL OFL 1.1 (`fonts/OFL.txt` ships its license). If you swap in another face
(Poppins is a similar OFL option), vendor its OFL.txt alongside it.
