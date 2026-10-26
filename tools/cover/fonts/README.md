# Vendored fonts

| file | family | licence |
|------|--------|---------|
| `Montserrat-Black.woff2` | Montserrat Black (800/900 weight of the Montserrat family) | SIL Open Font License 1.1 — see `OFL.txt` |

The file is the Latin subset of the woff2 build published by Google Fonts, so
a cover renders identically on any machine with no install and no network.

**The typeface used in the original Photoshop covers could not be recovered.**
The source PSD (`raw/screenshot-20260411-213906.psd`) only stores Adobe's
CJK fallback chain (`PhotoshopKinsokuHard`, `PhotoshopKinsokuSoft`,
`SourceHanSansSC-Heavy`, `AdobeInvisFont`, `AdobeHeitiStd-Regular`) — the face
that was actually used is not in the file.

Montserrat Black was chosen as the closest available match (double-storey `a`
with a flat diagonal terminal, near-circular `O`, flat-topped `t`).

To swap in another face: drop the `woff2` here, point `"font"` in
`../covers.json` at it, and re-run `python tools/cover/generate.py`. Check the
licence permits redistribution before committing it.
