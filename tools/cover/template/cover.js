/* ============================================================================
   Cover runtime — shared by the CLI renderer and the live editor.
   The editor mutates a config object and calls render() again; the CLI builds
   one config and renders it once. Same code either way, so what you see in
   the editor is exactly what gets exported.
   ========================================================================== */

(function () {
  const R = {};

  /* ---- colour helpers ---------------------------------------------------- */
  function hexToRgb(hex) {
    if (typeof hex !== "string") return [0, 0, 0];
    let h = hex.trim().replace("#", "");
    if (h.length === 3) h = h.split("").map((c) => c + c).join("");
    if (h.length !== 6) return [0, 0, 0];
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }

  function rgbToHex(rgb) {
    return (
      "#" +
      rgb
        .map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0"))
        .join("")
    );
  }

  /** mix(a, b, t): t=0 → a, t=1 → b */
  function mix(a, b, t) {
    const pa = hexToRgb(a);
    const pb = hexToRgb(b);
    return rgbToHex([0, 1, 2].map((i) => pa[i] + (pb[i] - pa[i]) * t));
  }

  /* ---- defaults ---------------------------------------------------------- */
  R.defaults = {
    width: 1920,
    height: 1080,
    inset: 10,
    radius: 120,
    padX: 96,
    padY: 30,
    baseFontSize: 160,
    lineHeight: 1.1,
    tracking: -0.015,
    maxHeightRatio: 0.46,
    strokeRatio: 0.035,
    scrimStart: 44,
    align: "center",
    lines: [],
    titleOffset: { x: 0, y: 0 },
    palette: {
      frameTop: "#8EC3E6",
      frameBottom: "#8A89DF",
      titleFill: "#8EC3E6",
      titleStroke: "#8353D7"
    },
    shot: { zoom: 1, focusX: 0.5, focusY: 0.5 },
    style: {
      glow: { color: null, x: 50, y: 86, size: 60 },
      glowStrength: 0.1,
      grain: 0.02,
      vignette: 0.22,
      ao: 0.28,
      sweep: 0.5,
      beam: 0.1,
      shadow: 0.6,
      baseMix: 0.28,          // how much accent survives in the deep base
      acid: 0.32,             // iridescent wash + prismatic title fill
      laser: 0.3,             // beams, lens flare
      prism: 0.25,            // R/G/B split on the specular sheen
      gloss: 0.55,            // specular band across the top of the glyphs
      glint: 0.5,              // one sharp specular line on the plate
      sparkle: 0.7,            // star glints on the plate
      titleColor: "#FFFFFF",  // hero line colour
      subColor: null,         // secondary lines (defaults to the accent)
      heroLine: 0,            // index of the hero line; -1 = every line equal
      heroScale: 1.0,
      subScale: 0.6,
      kicker: "",
      kickerStyle: "rule"     // "rule" | "pill" | "none"
    }
  };

  R.merge = function (base, over) {
    const out = Array.isArray(base) ? base.slice() : Object.assign({}, base);
    if (!over || typeof over !== "object") return out;
    for (const k of Object.keys(over)) {
      const v = over[k];
      if (v && typeof v === "object" && !Array.isArray(v) && base && typeof base[k] === "object" && base[k] !== null && !Array.isArray(base[k])) {
        out[k] = R.merge(base[k], v);
      } else {
        out[k] = v;
      }
    }
    return out;
  };

  /* ---- the visible window into the source screenshot ---------------------- */
  R.shotWindow = function (frameW, frameH, srcW, srcH, zoom, focusX, focusY) {
    if (!(zoom > 0)) zoom = 1;
    const cover = Math.max(frameW / srcW, frameH / srcH);
    const visW = Math.min(srcW, frameW / (cover * zoom));
    const visH = Math.min(srcH, frameH / (cover * zoom));
    const ox = Math.min(Math.max(focusX * srcW - visW / 2, 0), srcW - visW);
    const oy = Math.min(Math.max(focusY * srcH - visH / 2, 0), srcH - visH);
    const k = frameW / visW;
    return {
      left: -ox * k,
      top: -oy * k,
      width: srcW * k,
      height: srcH * k,
      k: k,
      visW: visW,
      visH: visH,
      ox: ox,
      oy: oy
    };
  };

  /* ---- per-line styling -------------------------------------------------- */
  R.lineStyle = function (cfg, index) {
    const st = cfg.style || {};
    const hero = st.heroLine === undefined ? 0 : st.heroLine;
    const isHero = hero >= 0 && index === hero;
    const accent = cfg.palette.titleFill || cfg.palette.titleStroke || "#8EC3E6";
    const color = isHero
      ? (st.titleColor || "#FFFFFF")
      : (st.subColor || accent);
    const scale = isHero
      ? (st.heroScale === undefined ? 1 : st.heroScale)
      : (st.subScale === undefined ? 0.6 : st.subScale);
    return {
      color: color,
      scale: scale,
      weight: isHero ? 900 : 800,
      tracking: isHero ? cfg.tracking : Math.max(cfg.tracking, 0.005),
      // The hero takes the full acid; the supporting line only hints at it.
      acid: isHero ? (st.acid ?? 0) : (st.acid ?? 0) * 0.45
    };
  };

  /* ---- the headline fill gradient ---------------------------------------- */
  /* Built here rather than in CSS: color-mix() is not available in every
     Chromium build, and mixing in JS also lets the acid stops scale exactly
     with the knob. */
  R.fillGradient = function (color, acid) {
    const a = Math.max(0, Math.min(1, acid || 0));
    const stops = [
      [0, mix(color, "#7bffea", a)],
      [24, mix(color, "#ffffff", 0.25 + a * 0.5)],
      [50, mix(color, "#ff7ae0", a)],
      [74, mix(color, "#d6ff5c", a)],
      [100, mix(color, "#7bffea", a)]
    ];
    return (
      "linear-gradient(96deg, " +
      stops.map(([p, c]) => c + " " + p + "%").join(", ") +
      ")"
    );
  };

  /* ---- CSS variables ------------------------------------------------------ */
  R.applyVars = function (stage, cfg) {
    const st = stage.style;
    const set = (k, v) => st.setProperty(k, v);
    const px = (v, d) => (typeof v === "number" ? v + "px" : v ?? d + "px");
    const em = (v, d) => (typeof v === "number" ? v + "em" : v ?? d + "em");
    const pct = (v, d) => (typeof v === "number" ? v + "%" : v ?? d + "%");
    const stl = cfg.style || {};
    const glow = stl.glow || {};
    const accent = cfg.palette.titleFill || cfg.palette.titleStroke || "#8EC3E6";

    // The deep base: the accent hue pushed most of the way to black, so the
    // headline always has the same contrast floor to sit on.
    const base = mix("#080A14", cfg.palette.frameBottom || "#2A2A44", stl.baseMix ?? 0.28);

    set("--w", px(cfg.width));
    set("--h", px(cfg.height));
    set("--inset", px(cfg.inset));
    set("--radius", px(cfg.radius));
    set("--pad-x", px(cfg.padX));
    set("--pad-y", px(cfg.padY));
    set("--line-height", String(cfg.lineHeight));
    set("--tracking", em(cfg.tracking, -0.015));
    set("--align", cfg.align);
    set("--scrim-start", pct(cfg.scrimStart, 44));

    set("--frame-top", cfg.palette.frameTop);
    set("--frame-bottom", cfg.palette.frameBottom);
    set("--base", base);
    set("--stroke-color", stl.strokeColor || base);

    set("--title-x", px(cfg.titleOffset?.x, 0));
    set("--title-y", px(cfg.titleOffset?.y, 0));

    set("--glow-color", glow.color || accent);
    set("--glow-x", pct(glow.x, 50));
    set("--glow-y", pct(glow.y, 86));
    set("--glow-size", pct(glow.size, 60));
    set("--glow-strength", String(stl.glowStrength ?? 0.1));
    set("--acid", String(stl.acid ?? 0));
    set("--laser", String(stl.laser ?? 0));
    set("--prism", (stl.prism ?? 0) * 3 + "%");
    set("--gloss", String(stl.gloss ?? 0.55));
    set("--glint", String(stl.glint ?? 0.5));
    set("--sparkle", String(stl.sparkle ?? 0.7));
    set("--flare-color", glow.color || accent);
    set("--grain", String(stl.grain ?? 0.035));
    set("--vignette", String(stl.vignette ?? 0.22));
    set("--ao", String(stl.ao ?? 0.28));
    set("--sweep", String(stl.sweep ?? 0.5));
    set("--beam", String(stl.beam ?? 0.1));
    set("--beam-color", mix("#ffffff", accent, 0.45));
    set("--title-shadow", String(stl.shadow ?? 0.6));

    set("--kicker-color", stl.kickerColor || "#EDF1FF");
    set("--kicker-rule", stl.kickerRule || accent);
    set("--kicker-display", stl.kickerStyle === "none" ? "none" : "flex");
  };

  /* ---- where the star glints sit on the plate ---------------------------- */
  R.sparks = [
    { x: 73, y: 14, s: 1.0 },
    { x: 13, y: 33, s: 0.72 },
    { x: 88, y: 56, s: 0.5 }
  ];

  /* ---- DOM --------------------------------------------------------------- */
  R.build = function (stage, cfgIn) {
    const cfg = R.merge(R.defaults, cfgIn);
    let root = stage.querySelector(":scope > .cover-root");
    if (!root) {
      root = document.createElement("div");
      root.className = "cover-root";
      root.style.cssText = "position:absolute;inset:0;";
      root.innerHTML =
        '<div class="glow"></div>' +
        '<div class="acid"></div>' +
        '<div class="frame"><img class="shot" alt=""><div class="scrim"></div>' +
        '<div class="sweep"></div><div class="sparkles"></div></div>' +
        '<div class="lasers"></div>' +
        '<div class="flare"></div>' +
        '<div class="grain"></div>' +
        '<div class="title"><div class="beam"></div>' +
        '<div class="kicker"><span class="label"></span></div></div>';
      stage.appendChild(root);
    }
    const shot = root.querySelector(".shot");
    const title = root.querySelector(".title");
    const kicker = root.querySelector(".kicker");

    if (shot.dataset.src !== cfg.source) {
      shot.dataset.src = cfg.source;
      shot.src = cfg.source;
    }

    // headline lines
    const wanted = cfg.lines.join("\u0000");
    if (title.dataset.lines !== wanted) {
      title.dataset.lines = wanted;
      title.querySelectorAll(".line").forEach((n) => n.remove());
      for (const text of cfg.lines) {
        const line = document.createElement("div");
        line.className = "line";
        const back = document.createElement("span");
        back.className = "stroke";
        back.textContent = text;
        const front = document.createElement("span");
        front.className = "fill";
        front.textContent = text;
        const gloss = document.createElement("span");
        gloss.className = "gloss";
        gloss.textContent = text;
        line.appendChild(back);
        line.appendChild(front);
        line.appendChild(gloss);
        title.appendChild(line);
      }
    }

    // per-line scale / colour / weight
    const lineEls = title.querySelectorAll(".line");
    lineEls.forEach((el, i) => {
      const ls = R.lineStyle(cfg, i);
      el.style.setProperty("--line-scale", String(ls.scale));
      el.style.setProperty("--line-color", ls.color);
      el.style.setProperty("--line-weight", String(ls.weight));
      el.style.setProperty("--line-tracking", ls.tracking + "em");
      el.style.setProperty("--line-acid", String(ls.acid));
      el.style.setProperty("--line-fill", R.fillGradient(ls.color, ls.acid));
    });

    const ks = (cfg.style?.kickerStyle) || "none";
    kicker.classList.toggle("pill", ks === "pill");
    kicker.querySelector(".label").textContent = (cfg.style?.kicker) || "";

    // star glints
    const sparkHost = root.querySelector(".sparkles");
    if (!sparkHost.childElementCount) {
      for (const sp of R.sparks) {
        const el = document.createElement("div");
        el.className = "spark";
        el.style.left = sp.x + "%";
        el.style.top = sp.y + "%";
        el.style.setProperty("--spark-scale", String(sp.s));
        el.appendChild(document.createElement("i"));
        sparkHost.appendChild(el);
      }
    }

    R.applyVars(stage, cfg);
    return { root: root, cfg: cfg };
  };

  /* ---- auto-fit: the headline can never overflow the safe area ----------- */
  R.fit = function (stage, cfg) {
    const title = stage.querySelector(".title");
    const lines = Array.from(stage.querySelectorAll(".line"));
    if (!lines.length) return { fontSize: cfg.baseFontSize, widest: 0, height: 0 };

    const setFontSize = (fs) => {
      stage.style.setProperty("--fs", fs + "px");
      stage.style.setProperty("--stroke", fs * cfg.strokeRatio + "px");
    };

    const measure = () => {
      let widest = 0;
      for (const el of lines) widest = Math.max(widest, el.getBoundingClientRect().width);
      return { widest: widest, height: title.getBoundingClientRect().height };
    };

    let fs = cfg.baseFontSize;
    setFontSize(fs);
    const maxW = cfg.width - cfg.padX * 2;
    const maxH = cfg.height * cfg.maxHeightRatio;
    for (let i = 0; i < 60; i++) {
      const m = measure();
      if (m.widest <= maxW && m.height <= maxH) break;
      const k = Math.min(
        m.widest > maxW ? maxW / m.widest : 1,
        m.height > maxH ? maxH / m.height : 1
      );
      fs *= k * 0.995;
      if (fs < 10) break;
      setFontSize(fs);
    }
    const m = measure();
    return { fontSize: fs, widest: m.widest, height: m.height, maxW: maxW };
  };

  /* ---- place the source screenshot inside the frame ----------------------- */
  R.placeShot = function (stage, cfg) {
    const shot = stage.querySelector(".shot");
    const frame = stage.querySelector(".frame");
    if (!shot || !frame) return null;
    const srcW = shot.naturalWidth;
    const srcH = shot.naturalHeight;
    if (!srcW || !srcH) return null;
    const fw = cfg.width - cfg.inset * 2;
    const fh = cfg.height - cfg.inset * 2;
    const win = R.shotWindow(fw, fh, srcW, srcH, cfg.shot.zoom, cfg.shot.focusX, cfg.shot.focusY);
    shot.style.left = win.left + "px";
    shot.style.top = win.top + "px";
    shot.style.width = win.width + "px";
    shot.style.height = win.height + "px";
    return win;
  };

  /* ---- one-shot render ---------------------------------------------------- */
  R.render = function (stage, cfgIn) {
    const built = R.build(stage, cfgIn);
    R.placeShot(stage, built.cfg);
    const metrics = R.fit(stage, built.cfg);
    return metrics;
  };

  window.CoverRender = R;
})();
