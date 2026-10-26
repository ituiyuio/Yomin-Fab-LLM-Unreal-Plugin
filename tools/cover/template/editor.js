/* ============================================================================
   Cover editor — live manipulation of the plugin covers.

   The canvas is rendered by cover.js (the same runtime the CLI exports with),
   so what you drag here is literally what gets written out.
   ========================================================================== */

(async function () {
  const R = window.CoverRender;

  const S = {
    manifest: null,
    sources: [],
    slug: null,
    variant: "fab",
    headline: "primary",   // "primary" | an alt name
    dirty: false,
    scale: 1,
    win: null              // last shot window, for drag maths
  };

  const $ = (id) => document.getElementById(id);
  const stage = $("stage");
  const viewport = $("viewport");
  const wrap = $("canvasWrap");
  const panel = $("panel");
  const status = $("status");

  /* ---------------------------------------------------------------- utils */
  const get = (obj, path) =>
    path.split(".").reduce((o, k) => (o == null ? o : o[k]), obj);

  const set = (obj, path, value) => {
    const keys = path.split(".");
    const last = keys.pop();
    let cur = obj;
    for (const k of keys) {
      if (typeof cur[k] !== "object" || cur[k] === null) cur[k] = {};
      cur = cur[k];
    }
    cur[last] = value;
  };

  function say(msg, kind) {
    status.textContent = msg || "";
    status.className = kind || "";
    if (msg) setTimeout(() => { if (status.textContent === msg) { status.textContent = ""; status.className = ""; } }, 2600);
  }

  const cover = () => S.manifest.covers.find((c) => c.slug === S.slug);

  function effectiveVariant(name) {
    const c = cover();
    return Object.assign({}, S.manifest.variants[name], (c.variantOverrides || {})[name] || {});
  }

  function currentLines() {
    const c = cover();
    if (S.headline === "primary") return c.lines.slice();
    const alt = (c.alt || []).find((a) => a.name === S.headline);
    return alt ? alt.lines.slice() : c.lines.slice();
  }

  /* Each headline may pair with its own background screenshot — that is how
     the Photoshop originals were made. */
  function currentSource() {
    const c = cover();
    if (S.headline === "primary") return c.source;
    const alt = (c.alt || []).find((a) => a.name === S.headline);
    return (alt && alt.source) || c.source;
  }

  function writeSource(value) {
    const c = cover();
    if (S.headline === "primary") c.source = value;
    else {
      const alt = (c.alt || []).find((a) => a.name === S.headline);
      if (alt) alt.source = value;
    }
    markDirty();
  }

  /* Each headline may carry its own crop of the background — the Photoshop
     originals framed every gallery image differently. */
  function currentShot() {
    const c = cover();
    const holder = S.headline === "primary"
      ? c
      : (c.alt || []).find((a) => a.name === S.headline) || c;
    holder.shot = holder.shot || {};
    return holder.shot;
  }

  function writeShot(path, value) {
    const holder = currentShot();
    set(holder, path, value);
    markDirty();
  }

  function setCurrentLines(lines) {
    const c = cover();
    if (S.headline === "primary") c.lines = lines;
    else {
      const alt = (c.alt || []).find((a) => a.name === S.headline);
      if (alt) alt.lines = lines;
    }
  }

  /* -------------------------------------------------------------- config */
  function buildConfig() {
    const c = cover();
    const v = effectiveVariant(S.variant);
    return {
      width: v.w,
      height: v.h,
      inset: v.inset,
      radius: v.radius,
      padX: v.padX,
      padY: v.padY,
      baseFontSize: v.baseFontSize,
      lineHeight: v.lineHeight,
      tracking: v.tracking,
      maxHeightRatio: v.maxHeightRatio,
      strokeRatio: v.strokeRatio,
      scrimStart: v.scrimStart,
      align: v.align,
      lines: currentLines(),
      titleOffset: c.titleOffset || {},
      palette: c.palette || {},
      shot: currentShot(),
      style: c.style || {},
      source: "/asset/" + currentSource()
    };
  }

  /* -------------------------------------------------------------- render */
  let renderTimer = null;
  function render() {
    const cfg = buildConfig();
    R.build(stage, cfg);
    const shot = stage.querySelector(".shot");
    const place = () => {
      S.win = R.placeShot(stage, cfg);
      R.fit(stage, cfg);
      layout();
      drawGuides(cfg);
    };
    if (shot.complete && shot.naturalWidth) place();
    else shot.addEventListener("load", place, { once: true });
  }

  function scheduleRender() {
    if (renderTimer) cancelAnimationFrame(renderTimer);
    renderTimer = requestAnimationFrame(render);
  }

  function layout() {
    const cfg = buildConfig();
    const vp = viewport.getBoundingClientRect();
    const s = Math.min((vp.width - 60) / cfg.width, (vp.height - 60) / cfg.height, 1);
    S.scale = s;
    stage.style.transform = "scale(" + s + ")";
    wrap.style.width = cfg.width * s + "px";
    wrap.style.height = cfg.height * s + "px";
  }

  function drawGuides(cfg) {
    const g = $("guides");
    const safe = g.querySelector(".safe");
    safe.style.left = cfg.padX + "px";
    safe.style.top = cfg.padY + "px";
    safe.style.right = cfg.padX + "px";
    safe.style.bottom = cfg.padY + "px";
    const v = g.querySelector(".mid.v");
    v.style.left = "0";
    v.style.width = "1px";
    v.style.top = "0";
    v.style.height = cfg.height + "px";
    const h = g.querySelector(".mid.h");
    h.style.top = "0";
    h.style.height = "1px";
    h.style.left = "0";
    h.style.width = cfg.width + "px";
  }

  /* ------------------------------------------------------------- controls */
  const GROUPS = [
    {
      title: "Headline",
      controls: [
        { type: "lines", label: "Text", hint: "One line per row. The block auto-shrinks to fit." },
        { type: "range", scope: "variant", path: "baseFontSize", label: "Size", min: 60, max: 320, step: 1, unit: "px" },
        { type: "range", scope: "variant", path: "lineHeight", label: "Line height", min: 0.7, max: 1.6, step: 0.01 },
        { type: "range", scope: "variant", path: "tracking", label: "Tracking", min: -0.08, max: 0.12, step: 0.005, unit: "em" },
        { type: "range", scope: "variant", path: "strokeRatio", label: "Keyline", min: 0, max: 0.12, step: 0.001 },
        { type: "select", scope: "variant", path: "align", label: "Align", options: ["left", "center", "right"] },
        { type: "range", scope: "cover", path: "titleOffset.x", label: "Offset X", min: -700, max: 700, step: 1, unit: "px", def: 0 },
        { type: "range", scope: "cover", path: "titleOffset.y", label: "Offset Y", min: -500, max: 500, step: 1, unit: "px", def: 0 },
        { type: "range", scope: "variant", path: "padX", label: "Side margin", min: 0, max: 400, step: 1, unit: "px" },
        { type: "range", scope: "variant", path: "padY", label: "Bottom margin", min: 0, max: 400, step: 1, unit: "px" }
      ]
    },
    {
      title: "Emphasis",
      hint: "One line carries the punch; the rest support it.",
      controls: [
        { type: "select", scope: "cover", path: "style.heroLine", label: "Hero line", options: ["first", "second", "none"], map: { first: 0, second: 1, none: -1 } },
        { type: "range", scope: "cover", path: "style.heroScale", label: "Hero size", min: 0.5, max: 1.6, step: 0.01, def: 1 },
        { type: "range", scope: "cover", path: "style.subScale", label: "Other size", min: 0.3, max: 1.4, step: 0.01, def: 0.6 },
        { type: "color", scope: "cover", path: "style.titleColor", label: "Hero colour" },
        { type: "color", scope: "cover", path: "style.subColor", label: "Other colour" }
      ]
    },
    {
      title: "Kicker",
      hint: "The small label above the headline — the advertising label.",
      controls: [
        { type: "text", scope: "cover", path: "style.kicker", label: "Text" },
        { type: "select", scope: "cover", path: "style.kickerStyle", label: "Style", options: ["rule", "pill", "none"] },
        { type: "color", scope: "cover", path: "style.kickerColor", label: "Text colour" },
        { type: "color", scope: "cover", path: "style.kickerRule", label: "Rule colour" }
      ]
    },
    {
      title: "Background image",
      controls: [
        { type: "source", scope: "cover", path: "source", label: "Screenshot" },
        { type: "range", scope: "shot", path: "zoom", label: "Zoom", min: 0.3, max: 4, step: 0.01 },
        { type: "range", scope: "shot", path: "focusX", label: "Focus X", min: 0, max: 1, step: 0.005 },
        { type: "range", scope: "shot", path: "focusY", label: "Focus Y", min: 0, max: 1, step: 0.005 }
      ]
    },
    {
      title: "Frame",
      controls: [
        { type: "range", scope: "variant", path: "inset", label: "Margin", min: 0, max: 80, step: 1, unit: "px" },
        { type: "range", scope: "variant", path: "radius", label: "Corner", min: 0, max: 400, step: 1, unit: "px" },
        { type: "range", scope: "variant", path: "scrimStart", label: "Scrim", min: 0, max: 100, step: 1, unit: "%" }
      ]
    },
    {
      title: "Colour",
      controls: [
        { type: "color", scope: "cover", path: "palette.frameTop", label: "Backdrop top" },
        { type: "color", scope: "cover", path: "palette.frameBottom", label: "Backdrop bottom" },
        { type: "color", scope: "cover", path: "palette.titleFill", label: "Title fill" },
        { type: "color", scope: "cover", path: "palette.titleStroke", label: "Title outline" }
      ]
    },
    {
      title: "Acid & laser",
      hint: "Prismatic iridescence and laser light — both are additive, keep them low.",
      controls: [
        { type: "range", scope: "cover", path: "style.acid", label: "Acid", min: 0, max: 1, step: 0.01, def: 0.32 },
        { type: "range", scope: "cover", path: "style.laser", label: "Laser", min: 0, max: 1, step: 0.01, def: 0.3 },
        { type: "range", scope: "cover", path: "style.prism", label: "Prism", min: 0, max: 1, step: 0.01, def: 0.25 }
      ]
    },
    {
      title: "Highlights",
      hint: "Speculars — the wet gloss on the type, the sharp line on the plate, the star glints.",
      controls: [
        { type: "range", scope: "cover", path: "style.gloss", label: "Type gloss", min: 0, max: 1, step: 0.01, def: 0.72 },
        { type: "range", scope: "cover", path: "style.glint", label: "Plate glint", min: 0, max: 1, step: 0.01, def: 0.8 },
        { type: "range", scope: "cover", path: "style.sparkle", label: "Star glints", min: 0, max: 1, step: 0.01, def: 0.75 }
      ]
    },
    {
      title: "Finish",
      controls: [
        { type: "range", scope: "cover", path: "style.baseMix", label: "Base depth", min: 0, max: 0.7, step: 0.01, def: 0.28 },
        { type: "range", scope: "cover", path: "style.glowStrength", label: "Glow", min: 0, max: 1, step: 0.01 },
        { type: "range", scope: "cover", path: "style.grain", label: "Grain", min: 0, max: 0.3, step: 0.005 },
        { type: "range", scope: "cover", path: "style.vignette", label: "Vignette", min: 0, max: 1, step: 0.01 },
        { type: "range", scope: "cover", path: "style.ao", label: "Edge shade", min: 0, max: 1, step: 0.01, def: 0.28 },
        { type: "range", scope: "cover", path: "style.sweep", label: "Sweep", min: 0, max: 1, step: 0.01 },
        { type: "range", scope: "cover", path: "style.beam", label: "Light beam", min: 0, max: 1, step: 0.01 },
        { type: "range", scope: "cover", path: "style.shadow", label: "Text shadow", min: 0, max: 1, step: 0.01 }
      ]
    }
  ];

  function controlTarget(scope) {
    const c = cover();
    if (scope === "shot") return currentShot();
    return scope === "variant" ? effectiveVariant(S.variant) : c;
  }

  /* The manifest only stores what was explicitly set; everything else falls
     back to the render defaults in cover.js. The panel must show the value
     that will actually be rendered, otherwise the first nudge of a slider
     snaps it to the wrong number. */
  function effectiveValue(scope, path) {
    const v = get(controlTarget(scope), path);
    if (v !== undefined && v !== null) return v;
    // Cover-scope paths already carry the "style." prefix, variant-scope paths
    // do not — both resolve against the same defaults object.
    if (scope === "shot") return get(R.defaults.shot, path);
    return get(R.defaults, path);
  }

  function writeControl(scope, path, value) {
    if (scope === "shot") {
      writeShot(path, value);
      return;
    }
    const c = cover();
    if (scope === "variant") {
      c.variantOverrides = c.variantOverrides || {};
      c.variantOverrides[S.variant] = c.variantOverrides[S.variant] || {};
      set(c.variantOverrides[S.variant], path, value);
    } else {
      set(c, path, value);
    }
    markDirty();
  }



  function buildPanel() {
    panel.innerHTML = "";
    for (const g of GROUPS) {
      const sec = document.createElement("section");
      sec.className = "group";
      const h = document.createElement("h3");
      h.textContent = g.title;
      sec.appendChild(h);
      if (g.hint) {
        const gh = document.createElement("div");
        gh.className = "hint";
        gh.textContent = g.hint;
        sec.appendChild(gh);
      }

      for (const ctl of g.controls) {
        const row = document.createElement("div");
        row.className = ctl.type === "lines" ? "row wide" : "row";
        const label = document.createElement("label");
        label.textContent = ctl.label;
        row.appendChild(label);
        const holder = document.createElement("div");
        row.appendChild(holder);
        sec.appendChild(row);

        const target = controlTarget(ctl.scope);

        if (ctl.type === "lines") {
          const ta = document.createElement("textarea");
          ta.rows = 2;
          ta.value = currentLines().join("\n");
          ta.addEventListener("input", () => {
            setCurrentLines(ta.value.split("\n"));
            markDirty();
            scheduleRender();
          });
          holder.appendChild(ta);
          if (ctl.hint) {
            const hint = document.createElement("div");
            hint.className = "hint";
            hint.textContent = ctl.hint;
            sec.appendChild(hint);
          }
          continue;
        }

        if (ctl.type === "range") {
          const wrap2 = document.createElement("div");
          wrap2.style.display = "flex";
          wrap2.style.alignItems = "center";
          wrap2.style.gap = "8px";
          const inp = document.createElement("input");
          inp.type = "range";
          inp.min = ctl.min; inp.max = ctl.max; inp.step = ctl.step;
          const cur = effectiveValue(ctl.scope, ctl.path);
          inp.value = typeof cur === "number" ? cur : (ctl.def ?? ctl.min);
          const out = document.createElement("span");
          out.className = "val";
          const fmt = (v) => (Math.round(v * 1000) / 1000) + (ctl.unit || "");
          out.textContent = fmt(Number(inp.value));
          inp.addEventListener("input", () => {
            const v = Number(inp.value);
            out.textContent = fmt(v);
            writeControl(ctl.scope, ctl.path, v);
            scheduleRender();
          });
          wrap2.appendChild(inp);
          wrap2.appendChild(out);
          holder.appendChild(wrap2);
          continue;
        }

        if (ctl.type === "color") {
          const inp = document.createElement("input");
          inp.type = "color";
          inp.value = effectiveValue(ctl.scope, ctl.path) || "#000000";
          inp.addEventListener("input", () => {
            writeControl(ctl.scope, ctl.path, inp.value);
            scheduleRender();
          });
          holder.appendChild(inp);
          continue;
        }

        if (ctl.type === "check") {
          const inp = document.createElement("input");
          inp.type = "checkbox";
          inp.checked = !!get(target, ctl.path);
          inp.addEventListener("change", () => {
            writeControl(ctl.scope, ctl.path, inp.checked);
            scheduleRender();
          });
          holder.appendChild(inp);
          continue;
        }

        if (ctl.type === "select") {
          const inp = document.createElement("select");
          for (const o of ctl.options) {
            const opt = document.createElement("option");
            opt.value = o;
            opt.textContent = o;
            inp.appendChild(opt);
          }
          if (ctl.map) {
            const cur = effectiveValue(ctl.scope, ctl.path);
            let shown = ctl.options[0];
            for (const o of ctl.options) if (ctl.map[o] === cur) shown = o;
            inp.value = shown;
            inp.addEventListener("change", () => {
              writeControl(ctl.scope, ctl.path, ctl.map[inp.value]);
              scheduleRender();
            });
          } else {
            inp.value = effectiveValue(ctl.scope, ctl.path) || ctl.options[0];
            inp.addEventListener("change", () => {
              writeControl(ctl.scope, ctl.path, inp.value);
              scheduleRender();
            });
          }
          holder.appendChild(inp);
          continue;
        }

        if (ctl.type === "text") {
          const inp = document.createElement("input");
          inp.type = "text";
          inp.value = get(target, ctl.path) || "";
          inp.addEventListener("input", () => {
            writeControl(ctl.scope, ctl.path, inp.value);
            scheduleRender();
          });
          holder.appendChild(inp);
          continue;
        }

        if (ctl.type === "source") {
          const inp = document.createElement("select");
          for (const s of S.sources) {
            const opt = document.createElement("option");
            opt.value = s;
            opt.textContent = s.replace(/^raw\//, "");
            inp.appendChild(opt);
          }
          inp.value = currentSource();
          if (!inp.value && S.sources.length) inp.value = S.sources[0];
          inp.addEventListener("change", () => {
            writeSource(inp.value);
            scheduleRender();
          });
          holder.appendChild(inp);
          continue;
        }
      }
      panel.appendChild(sec);
    }
  }

  /* --------------------------------------------------------- interaction */
  function framePoint(ev) {
    const r = stage.getBoundingClientRect();
    return { x: (ev.clientX - r.left) / S.scale, y: (ev.clientY - r.top) / S.scale };
  }

  function titleHit(pt) {
    const t = stage.querySelector(".title");
    if (!t) return false;
    // getBoundingClientRect is in screen pixels; the stage is scaled and
    // offset, so translate the title's box into frame coordinates first.
    const sr = stage.getBoundingClientRect();
    const r = t.getBoundingClientRect();
    const left = (r.left - sr.left) / S.scale;
    const top = (r.top - sr.top) / S.scale;
    const right = (r.right - sr.left) / S.scale;
    const bottom = (r.bottom - sr.top) / S.scale;
    return pt.x >= left && pt.x <= right && pt.y >= top && pt.y <= bottom;
  }

  let drag = null;

  stage.addEventListener("pointerdown", (ev) => {
    const pt = framePoint(ev);
    const mode = titleHit(pt) ? "title" : "shot";
    drag = { mode: mode, x: pt.x, y: pt.y };
    stage.classList.add("dragging");
    stage.setPointerCapture(ev.pointerId);
    ev.preventDefault();
  });

  stage.addEventListener("pointermove", (ev) => {
    if (!drag) {
      const pt = framePoint(ev);
      stage.classList.toggle("over-title", titleHit(pt));
      stage.classList.toggle("over-shot", !titleHit(pt));
      return;
    }
    const pt = framePoint(ev);
    const dx = pt.x - drag.x;
    const dy = pt.y - drag.y;
    drag.x = pt.x;
    drag.y = pt.y;
    const c = cover();

    if (drag.mode === "title") {
      c.titleOffset = c.titleOffset || {};
      c.titleOffset.x = Math.round(((c.titleOffset.x || 0) + dx) * 10) / 10;
      c.titleOffset.y = Math.round(((c.titleOffset.y || 0) + dy) * 10) / 10;
    } else {
      const cfg = buildConfig();
      const fw = cfg.width - cfg.inset * 2;
      const fh = cfg.height - cfg.inset * 2;
      const shot = stage.querySelector(".shot");
      const srcW = shot.naturalWidth || 1;
      const srcH = shot.naturalHeight || 1;
      const win = R.shotWindow(fw, fh, srcW, srcH, cfg.shot.zoom ?? 1, cfg.shot.focusX ?? 0.5, cfg.shot.focusY ?? 0.5);
      c.shot = c.shot || {};
      c.shot.focusX = Math.min(1, Math.max(0, (c.shot.focusX ?? 0.5) - (dx * win.visW) / (fw * srcW)));
      c.shot.focusY = Math.min(1, Math.max(0, (c.shot.focusY ?? 0.5) - (dy * win.visH) / (fh * srcH)));
    }
    markDirty();
    scheduleRender();
    syncPanel();
  });

  const endDrag = (ev) => {
    drag = null;
    stage.classList.remove("dragging");
    try { stage.releasePointerCapture(ev.pointerId); } catch (e) { /* already released */ }
  };
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);

  stage.addEventListener("wheel", (ev) => {
    ev.preventDefault();
    const c = cover();
    const cfg = buildConfig();
    const factor = ev.deltaY > 0 ? 0.92 : 1.087;
    if (ev.shiftKey) {
      const v = effectiveVariant(S.variant);
      writeControl("variant", "baseFontSize", Math.min(320, Math.max(40, (v.baseFontSize || 160) * factor)));
    } else {
      c.shot = c.shot || {};
      c.shot.zoom = Math.min(4, Math.max(0.3, (c.shot.zoom ?? 1) * factor));
    }
    markDirty();
    scheduleRender();
    syncPanel();
  }, { passive: false });

  /* keep the panel in sync with drags (the sliders move too) */
  function syncPanel() {
    const inputs = panel.querySelectorAll("input[type=range]");
    let i = 0;
    for (const g of GROUPS) {
      for (const ctl of g.controls) {
        if (ctl.type !== "range") continue;
        const inp = inputs[i++];
        if (!inp) continue;
        const target = controlTarget(ctl.scope);
        const cur = effectiveValue(ctl.scope, ctl.path);
        if (typeof cur === "number") {
          inp.value = cur;
          const out = inp.parentElement.querySelector(".val");
          if (out) out.textContent = (Math.round(cur * 1000) / 1000) + (ctl.unit || "");
        }
      }
    }
  }

  function markDirty() {
    S.dirty = true;
    $("saveBtn").textContent = "Save •";
  }

  /* ------------------------------------------------------------- top bar */
  function buildTopbar() {
    const sel = $("coverSel");
    sel.innerHTML = "";
    for (const c of S.manifest.covers) {
      const o = document.createElement("option");
      o.value = c.slug;
      o.textContent = c.slug;
      sel.appendChild(o);
    }
    sel.value = S.slug;
    sel.onchange = () => selectCover(sel.value);

    const tabs = $("variantTabs");
    tabs.innerHTML = "";
    for (const name of Object.keys(S.manifest.variants)) {
      const b = document.createElement("button");
      b.textContent = name;
      b.className = name === S.variant ? "sel" : "";
      b.onclick = () => { S.variant = name; buildTopbar(); buildPanel(); render(); };
      tabs.appendChild(b);
    }
    buildHeadlineSelect();
  }

  function buildHeadlineSelect() {
    const sel = $("headlineSel");
    sel.innerHTML = "";
    const c = cover();
    const o0 = document.createElement("option");
    o0.value = "primary";
    o0.textContent = "Headline";
    sel.appendChild(o0);
    for (const a of c.alt || []) {
      const o = document.createElement("option");
      o.value = a.name;
      o.textContent = "Headline · " + a.name;
      sel.appendChild(o);
    }
    sel.value = S.headline;
    sel.onchange = () => { S.headline = sel.value; buildPanel(); render(); };
  }

  function selectCover(slug) {
    S.slug = slug;
    S.headline = "primary";
    S.dirty = false;
    $("saveBtn").textContent = "Save";
    buildTopbar();
    buildPanel();
    render();
  }

  /* ----------------------------------------------------------------- save */
  async function save() {
    const res = await fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug: S.slug, cover: cover() })
    });
    const out = await res.json();
    if (out.ok) { S.dirty = false; $("saveBtn").textContent = "Save"; say("saved to covers.json", "ok"); }
    else say(out.error || "save failed", "err");
  }

  async function exportPng() {
    say("rendering…");
    const name = S.headline === "primary"
      ? S.slug + "-" + S.variant + ".png"
      : S.slug + "-" + S.headline + "-" + S.variant + ".png";
    const res = await fetch("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        slug: S.slug, variant: S.variant, lines: currentLines(),
        cover: cover(), name: name,
        source: currentSource(), shot: currentShot()
      })
    });
    const out = await res.json();
    if (out.ok) say("exported " + out.path, "ok");
    else say(out.error || "export failed", "err");
  }

  /* ----------------------------------------------------------------- init */
  $("saveBtn").onclick = save;
  $("renderBtn").onclick = exportPng;
  $("guidesBtn").onclick = () => {
    const g = $("guides");
    g.classList.toggle("on");
    $("guidesBtn").classList.toggle("on", g.classList.contains("on"));
  };
  $("resetBtn").onclick = async () => {
    const res = await fetch("/api/manifest");
    const data = await res.json();
    S.manifest = data.manifest;
    buildTopbar();
    buildPanel();
    render();
    say("reloaded from disk");
  };

  window.addEventListener("resize", layout);
  document.addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "s") { ev.preventDefault(); save(); }
  });

  const res = await fetch("/api/manifest");
  const data = await res.json();
  S.manifest = data.manifest;
  S.sources = data.sources;
  S.slug = S.manifest.covers[0].slug;
  buildTopbar();
  buildPanel();
  render();
  await document.fonts.ready;
  render();
})();
