/*
 * flowshot player — renders an interactive demo from a demo.json document.
 * No dependencies. Works as a <script> tag (window.Flowshot) or CommonJS require.
 */
(function (global) {
  "use strict";

  var CSS = [
    ".fs-root{--fs-accent:#2563eb;--fs-accent-2:#2563eb;--fs-radius:10px;--fs-surface:#fff;",
    "--fs-text:#0f172a;--fs-muted:#64748b;--fs-chrome:#0f172a;--fs-caption-width:300px;",
    "--fs-card-bg:rgba(15,23,42,.72);--fs-ann-color:var(--fs-accent-2);--fs-ann-border:2px;--fs-ann-radius:10px;",
    "--fs-ann-fill:color-mix(in srgb,var(--fs-ann-color) 14%,transparent);--fs-ann-shadow:0 10px 24px rgba(15,23,42,.22);",
    "--fs-card-surface:transparent;--fs-card-text:#fff;--fs-card-padding:0;--fs-card-shadow:0 1px 3px rgba(15,23,42,.4);",
    "position:relative;width:100%;",
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;",
    "color:var(--fs-text);box-sizing:border-box;-webkit-user-select:none;user-select:none}",
    ".fs-root *{box-sizing:border-box}",
    ".fs-stage{position:relative;width:100%;overflow:hidden;border-radius:var(--fs-radius);",
    "background:var(--fs-chrome);box-shadow:0 1px 2px rgba(15,23,42,.08),0 8px 24px rgba(15,23,42,.12)}",
    ".fs-stage-inner{position:relative;width:100%;height:100%;transform-origin:var(--fs-focus-x,50%) var(--fs-focus-y,50%);",
    "transform:scale(var(--fs-zoom,1));transition:transform .72s cubic-bezier(.2,.72,.18,1);will-change:transform;z-index:1}",
    ".fs-img,.fs-video{display:block;width:100%;height:100%;object-fit:cover;object-position:top left}",
    ".fs-annotations{position:absolute;inset:0;z-index:3;pointer-events:none}",
    ".fs-ann{position:absolute;pointer-events:none;color:#fff;--fs-ann-color:var(--fs-accent-2)}",
    ".fs-ann-box{border:var(--fs-ann-border) solid var(--fs-ann-color);border-radius:var(--fs-ann-radius);background:var(--fs-ann-fill);box-shadow:var(--fs-ann-shadow),0 0 0 1px rgba(255,255,255,.38)}",
    ".fs-ann-label{min-width:max-content;max-width:220px;background:var(--fs-ann-color);border:var(--fs-ann-border) solid color-mix(in srgb,var(--fs-ann-color) 76%,#fff);padding:7px 10px;border-radius:var(--fs-ann-radius);font-size:12px;font-weight:700;letter-spacing:0;line-height:1.2;box-shadow:var(--fs-ann-shadow);overflow-wrap:anywhere}",
    ".fs-ann-arrow{filter:drop-shadow(0 8px 14px rgba(15,23,42,.24))}.fs-ann-arrow svg{display:block;width:100%;height:100%;overflow:visible}.fs-ann-arrow line{stroke:var(--fs-ann-color);stroke-width:var(--fs-ann-border);stroke-linecap:round}",
    ".fs-hotspot{position:absolute;z-index:4;border:2px solid var(--fs-accent);border-radius:8px;",
    "background:rgba(37,99,235,.10);cursor:pointer;padding:0;margin:0;outline:none;",
    "box-shadow:0 0 0 4px rgba(37,99,235,.18);animation:fs-pulse 1.8s ease-out infinite}",
    ".fs-hotspot:focus-visible,.fs-btn:focus-visible,.fs-dot:focus-visible,.fs-card-btn:focus-visible,.fs-cta:focus-visible,.fs-menu button:focus-visible{outline:3px solid var(--fs-accent-2);outline-offset:3px}",
    ".fs-hotspot:focus-visible{box-shadow:0 0 0 4px rgba(37,99,235,.45)}",
    "@keyframes fs-pulse{0%{box-shadow:0 0 0 0 rgba(37,99,235,.45)}",
    "70%{box-shadow:0 0 0 12px rgba(37,99,235,0)}100%{box-shadow:0 0 0 0 rgba(37,99,235,0)}}",
    ".fs-caption{position:absolute;width:min(var(--fs-caption-width),calc(100% - 16px));max-width:78%;",
    "background:var(--fs-surface);color:var(--fs-text);overflow-wrap:anywhere;",
    "font-size:14px;line-height:1.45;padding:10px 12px;border-radius:10px;z-index:3;",
    "box-shadow:0 4px 14px rgba(15,23,42,.22);transform:translateX(-50%)}",
    ".fs-caption .fs-cta{display:inline-block;margin-top:8px;background:var(--fs-accent-2);color:#fff;",
    "text-decoration:none;font-weight:600;font-size:13px;padding:7px 12px;border-radius:8px}",
    ".fs-bar{position:absolute;left:0;bottom:0;height:3px;background:var(--fs-accent);",
    "transition:width .25s ease;z-index:4}",
    ".fs-spotlight{position:absolute;inset:0;display:none;pointer-events:none;z-index:2;",
    "background:radial-gradient(circle at var(--fs-focus-x,50%) var(--fs-focus-y,50%),transparent 0,transparent 16%,rgba(15,23,42,.58) 32%,rgba(15,23,42,.64) 100%)}",
    ".fs-cursor{position:absolute;display:none;left:var(--fs-focus-x,50%);top:var(--fs-focus-y,50%);",
    "width:18px;height:18px;border-radius:50%;background:#fff;border:2px solid var(--fs-accent);",
    "box-shadow:0 8px 18px rgba(15,23,42,.28);transform:translate(-50%,-50%);z-index:5;",
    "transition:left .55s cubic-bezier(.2,.72,.18,1),top .55s cubic-bezier(.2,.72,.18,1)}",
    ".fs-controls{display:flex;align-items:center;gap:8px;margin-top:12px;min-height:40px}",
    ".fs-btn{appearance:none;border:1px solid color-mix(in srgb,var(--fs-text) 14%,transparent);background:color-mix(in srgb,var(--fs-surface) 94%,#fff);color:var(--fs-text);",
    "font-size:14px;font-weight:650;height:38px;padding:0 16px;border-radius:10px;cursor:pointer;box-shadow:0 1px 2px rgba(15,23,42,.08),0 6px 16px rgba(15,23,42,.08);transition:transform .16s ease,border-color .16s ease,background .16s ease,box-shadow .16s ease,color .16s ease}",
    ".fs-btn:hover{border-color:color-mix(in srgb,var(--fs-accent) 42%,#cbd5e1);box-shadow:0 2px 4px rgba(15,23,42,.10),0 10px 22px rgba(15,23,42,.10);transform:translateY(-1px)}",
    ".fs-btn:active{transform:translateY(0);box-shadow:0 1px 2px rgba(15,23,42,.08)}",
    ".fs-btn[disabled]{opacity:.45;cursor:default;transform:none;box-shadow:none}",
    ".fs-next{background:var(--fs-accent);border-color:var(--fs-accent);color:#fff;box-shadow:0 2px 5px color-mix(in srgb,var(--fs-accent) 28%,transparent),0 10px 24px rgba(15,23,42,.12)}",
    ".fs-next:hover{background:color-mix(in srgb,var(--fs-accent) 88%,#000);border-color:color-mix(in srgb,var(--fs-accent) 88%,#000)}",
    ".fs-menu-wrap{position:relative}",
    ".fs-menu-btn{width:38px;padding:0;font-size:17px;line-height:1;color:var(--fs-accent)}",
    ".fs-menu{position:absolute;left:0;bottom:48px;min-width:210px;max-width:calc(100vw - 32px);",
    "max-height:min(260px,65vh);overflow:auto;background:var(--fs-surface);border:1px solid #e2e8f0;",
    "border-radius:10px;padding:6px;box-shadow:0 14px 34px rgba(15,23,42,.18);z-index:6}",
    ".fs-menu[hidden]{display:none}",
    ".fs-menu button{display:block;width:100%;appearance:none;border:0;background:transparent;color:var(--fs-text);",
    "font:inherit;font-size:13px;font-weight:650;text-align:left;padding:9px 10px;border-radius:7px;cursor:pointer}",
    ".fs-menu button:hover,.fs-menu button.is-on{background:color-mix(in srgb,var(--fs-accent) 10%,var(--fs-surface));color:var(--fs-accent)}",
    ".fs-count{font-size:13px;color:var(--fs-muted);margin-left:auto;font-variant-numeric:tabular-nums}",
    ".fs-dots{display:flex;align-items:center;gap:3px}",
    ".fs-dot{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:999px;background:transparent;border:1px solid transparent;padding:0;cursor:pointer;transition:background .16s ease,border-color .16s ease,transform .16s ease}",
    ".fs-dot::before{content:'';display:block;width:7px;height:7px;border-radius:50%;background:#cbd5e1;transition:width .16s ease,background .16s ease}",
    ".fs-dot:hover{background:color-mix(in srgb,var(--fs-accent) 9%,transparent);border-color:color-mix(in srgb,var(--fs-accent) 20%,transparent)}",
    ".fs-dot:active{transform:scale(.92)}.fs-dot.is-on{background:color-mix(in srgb,var(--fs-accent) 12%,transparent);border-color:color-mix(in srgb,var(--fs-accent) 28%,transparent)}",
    ".fs-dot.is-on::before{width:9px;background:var(--fs-accent)}",
    ".fs-resume{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:10px 0 0;padding:9px 10px;",
    "border:1px solid #dbe3ef;border-radius:8px;background:var(--fs-surface);color:var(--fs-text);font-size:13px}",
    ".fs-resume[hidden]{display:none}.fs-resume span{margin-right:auto;color:var(--fs-muted)}",
    ".fs-transcript{margin:10px 0 0;border:1px solid #dbe3ef;border-radius:8px;background:var(--fs-surface);color:var(--fs-text);font-size:13px}",
    ".fs-transcript[hidden]{display:none}.fs-transcript summary{cursor:pointer;font-weight:700;padding:9px 10px}.fs-transcript div{padding:0 10px 10px;line-height:1.5;color:var(--fs-muted);white-space:pre-wrap}",
    ".fs-card{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;",
    "padding:32px;z-index:2;background:var(--fs-card-bg)}",
    ".fs-card[hidden]{display:none}",
    ".fs-card-inner{max-width:620px;text-align:center;color:var(--fs-card-text);overflow-wrap:anywhere;",
    "background:var(--fs-card-surface);padding:var(--fs-card-padding);border-radius:var(--fs-radius);",
    "text-shadow:var(--fs-card-shadow)}",
    ".fs-card-logo{display:block;width:min(220px,48%);max-height:54px;object-fit:contain;margin:0 auto 18px}",
    ".fs-card-title{font-size:clamp(26px,4vw,44px);line-height:1.15;font-weight:520;letter-spacing:0;text-wrap:balance;font-kerning:normal;text-rendering:optimizeLegibility;margin:0}",
    ".fs-card-subtitle{font-size:16px;line-height:1.55;margin:12px auto 0;max-width:540px;color:var(--fs-card-text)}",
    ".fs-card-actions{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:20px}",
    ".fs-card-btn{appearance:none;border:0;background:var(--fs-accent);color:#fff;",
    "font-size:13.5px;font-weight:500;letter-spacing:.005em;padding:11px 20px;border-radius:999px;cursor:pointer;",
    "box-shadow:0 1px 2px rgba(15,23,42,.05),0 6px 16px color-mix(in srgb,var(--fs-accent) 20%,transparent);transition:transform .16s ease,box-shadow .16s ease,filter .16s ease}",
    ".fs-card-btn:hover{filter:brightness(1.04);transform:translateY(-1px);box-shadow:0 2px 6px rgba(15,23,42,.07),0 10px 22px color-mix(in srgb,var(--fs-accent) 24%,transparent)}",
    ".fs-card-btn:active{transform:translateY(0);filter:brightness(.99);box-shadow:0 1px 3px rgba(15,23,42,.09)}.fs-card-btn[disabled]{opacity:.5;cursor:default;transform:none;filter:none}",
    ".fs-card-btn.is-ghost{background:color-mix(in srgb,var(--fs-accent) 8%,#fff);color:color-mix(in srgb,var(--fs-accent) 82%,#000);box-shadow:none;border:1px solid color-mix(in srgb,var(--fs-accent) 24%,transparent)}",
    ".fs-card-btn.is-ghost:hover{background:color-mix(in srgb,var(--fs-accent) 14%,#fff);border-color:color-mix(in srgb,var(--fs-accent) 38%,transparent);box-shadow:0 4px 12px rgba(15,23,42,.06)}",
    ".fs-form{display:grid;gap:12px;margin-top:18px;text-align:left;text-shadow:none}",
    ".fs-field{display:grid;gap:5px}.fs-field label{font-size:13px;font-weight:700;color:var(--fs-card-text)}",
    ".fs-field input{width:100%;min-height:40px;border:1px solid #cbd5e1;border-radius:8px;padding:0 10px;",
    "font:inherit;font-size:14px;color:var(--fs-text);background:var(--fs-surface)}",
    ".fs-field input[aria-invalid='true']{border-color:#dc2626;box-shadow:0 0 0 2px rgba(220,38,38,.12)}",
    ".fs-form-status{min-height:18px;font-size:13px;color:var(--fs-card-text);text-align:center}",
    ".fs-sr{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}",
    ".fs-img.is-blur-light{filter:blur(3px);transform:scale(1.02)}",
    ".fs-img.is-blur-medium{filter:blur(7px);transform:scale(1.04)}",
    ".fs-img.is-blur-heavy{filter:blur(12px);transform:scale(1.07)}",
    "@media(max-width:820px){.fs-root{--fs-caption-width:280px}.fs-card{padding:24px}",
    ".fs-card-title{font-size:clamp(23px,6vw,34px)}.fs-card-subtitle{font-size:15px}",
    ".fs-controls{gap:8px;flex-wrap:wrap}.fs-dots{flex-wrap:wrap}}",
    "@media(max-width:560px){.fs-card{padding:18px}.fs-card-actions{flex-direction:column;align-items:stretch}",
    ".fs-card-logo{width:min(190px,62%);max-height:44px;margin-bottom:14px}",
    ".fs-card-btn{width:100%}.fs-caption{--fs-caption-width:260px;font-size:13px;line-height:1.35;padding:8px 10px}",
    ".fs-menu{left:auto;right:0;min-width:170px}.fs-dots{order:2;flex:1 1 calc(100% - 64px)}.fs-count{order:2;width:auto;margin-left:auto}}",
    "@media(max-width:380px){.fs-card{padding:12px}.fs-card-title{font-size:22px}.fs-card-subtitle{font-size:14px}",
    ".fs-card-actions{gap:8px;margin-top:16px}.fs-caption{--fs-caption-width:220px;font-size:12px}",
    ".fs-btn{height:36px;padding:0 12px;font-size:13px}.fs-menu-btn{width:36px;padding:0}.fs-menu{max-width:calc(100vw - 20px)}}",
    "@media(prefers-reduced-motion:reduce){.fs-hotspot{animation:none}.fs-bar,.fs-cursor,.fs-img,.fs-video,.fs-stage-inner,.fs-btn,.fs-dot{transition:none!important}}",
    ".fs-root.is-fit{height:100%}.fs-root.is-fit .fs-stage{height:100%}",
    ".fs-root.is-fit .fs-controls{position:absolute;left:12px;right:12px;bottom:10px;margin:0;z-index:7;",
    "background:rgba(255,255,255,.92);padding:8px 10px;border-radius:10px;backdrop-filter:blur(6px)}",
    ".fs-fallback{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;",
    "background:#fff;color:#0f172a;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;",
    "box-shadow:0 1px 2px rgba(15,23,42,.08)}",
    ".fs-fallback strong{display:block;font-size:14px;margin-bottom:4px}.fs-fallback span{font-size:13px;color:#64748b}"
  ].join("");

  var styleInjected = false;
  var THEME_PRESETS = {
    aggregator: {
      accent: "#3D6B5E",
      "accent-2": "#E8836B",
      surface: "#FAF6F3",
      text: "#2D3B35",
      muted: "#64756E",
      chrome: "#2D3B35",
      "card-bg": "rgba(45,59,53,.62)",
      "card-surface": "#FAF6F3",
      "card-text": "#2D3B35",
      "card-padding": "26px 28px 22px",
      "card-shadow": "none",
      radius: "10px"
    },
    spotlight: {
      accent: "#E2126A",
      "accent-2": "#E2126A",
      surface: "#fff",
      text: "#2D344B",
      muted: "#64748b",
      chrome: "#2D344B",
      "card-bg": "rgba(45,52,75,.74)",
      "card-surface": "#fff",
      "card-text": "#2D344B",
      "card-padding": "26px 28px 22px",
      "card-shadow": "none",
      radius: "12px"
    }
  };

  function injectCSS(doc) {
    if (styleInjected) return;
    var s = doc.createElement("style");
    s.setAttribute("data-flowshot-style", "");
    s.textContent = CSS;
    (doc.head || doc.documentElement).appendChild(s);
    styleInjected = true;
  }

  function clampPct(v) { return Math.max(0, Math.min(100, v)); }

  function stepType(step) {
    if (step && step.type === "card") return "card";
    if (step && step.type === "video") return "video";
    if (step && step.type === "form") return "form";
    return "shot";
  }

  function isChooserCard(step) { return stepType(step) === "card" && Array.isArray(step.buttons) && step.buttons.length > 0; }

  function isMediaStep(step) { return stepType(step) === "shot" || stepType(step) === "video"; }

  function focusStyle(step) {
    var style = step && step.focus;
    if (style === "cursor" || style === "zoom" || style === "spotlight" || style === "hotspot") return style;
    return "hotspot";
  }

  function stepLabel(step, index) {
    if (!step) return "step-" + (index + 1);
    if (step.title) return step.title;
    if (step.caption) return step.caption;
    if (step.id) return step.id;
    return "step-" + (index + 1);
  }

  function slugify(text) {
    return String(text || "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "") || "";
  }

  function hashString(text) {
    var hash = 0;
    text = String(text || "");
    for (var i = 0; i < text.length; i++) hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
    return Math.abs(hash).toString(36);
  }

  function isInteractiveTarget(target) {
    return target && target.closest && target.closest("button,a,input,select,textarea");
  }

  function trimText(text, fallback) {
    text = String(text || "").replace(/\s+/g, " ").trim();
    if (!text) return fallback || "";
    return text.length > 72 ? text.slice(0, 69) + "..." : text;
  }

  function isPlainObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
  }

  function collectTemplateVars(value, out) {
    if (typeof value === "string") {
      value.replace(/\{\{\s*([A-Za-z0-9_-]+)\s*(?:\|[^}]*)?\s*\}\}/g, function (_match, name) {
        out[name] = true;
        return "";
      });
      return out;
    }
    if (Array.isArray(value)) {
      for (var i = 0; i < value.length; i++) collectTemplateVars(value[i], out);
      return out;
    }
    if (isPlainObject(value)) {
      for (var key in value) collectTemplateVars(value[key], out);
    }
    return out;
  }

  function prefersReducedMotion() {
    return typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function el(tag, cls, attrs) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (attrs) for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }

  function setVar(root, name, value) {
    if (value == null || value === "") return;
    root.style.setProperty("--fs-" + name, value);
  }

  function applyTheme(root, theme, opts) {
    theme = theme || {};
    opts = opts || {};
    var presetName = opts.preset || theme.preset;
    var preset = THEME_PRESETS[presetName];
    if (preset) {
      for (var key in preset) setVar(root, key, preset[key]);
    }
    if (opts.accent) setVar(root, "accent", opts.accent);
    if (theme.accent) setVar(root, "accent", theme.accent);
    if (theme.accent2) setVar(root, "accent-2", theme.accent2);
    if (theme.surface) setVar(root, "surface", theme.surface);
    if (theme.text) setVar(root, "text", theme.text);
    if (theme.chrome) setVar(root, "chrome", theme.chrome);
    if (theme.radius != null) setVar(root, "radius", typeof theme.radius === "number" ? theme.radius + "px" : theme.radius);
  }

  function validateDemoDocument(demo) {
    if (!demo || typeof demo !== "object") return ["demo must be an object"];
    if (!Array.isArray(demo.steps) || demo.steps.length === 0) return ["demo.steps must be a non-empty array"];
    var errors = [];
    // Keep these structural rules in sync with cli/schema.js. Branch goTo
    // reachability is intentionally handled non-fatally when buttons render.
    validateStepIds(demo, errors);
    if (demo.size && (!isPosInt(demo.size.width) || !isPosInt(demo.size.height))) {
      errors.push("size must have positive integer width and height");
    }
    if (demo.description != null && typeof demo.description !== "string") errors.push("description must be a string");
    if (demo.poster != null && typeof demo.poster !== "string") errors.push("poster must be a string");
    if (demo.analytics != null) {
      if (typeof demo.analytics !== "object") errors.push("analytics must be an object");
      else {
        if (demo.analytics.beacon != null && typeof demo.analytics.beacon !== "string") errors.push("analytics.beacon must be a string");
        if (demo.analytics.dataLayer != null && typeof demo.analytics.dataLayer !== "boolean") errors.push("analytics.dataLayer must be a boolean");
      }
    }
    if (demo.variables != null) {
      if (!isPlainObject(demo.variables)) errors.push("variables must be an object");
      else {
        for (var key in demo.variables) {
          if (typeof demo.variables[key] !== "string" && typeof demo.variables[key] !== "number" && typeof demo.variables[key] !== "boolean") {
            errors.push("variables." + key + " must be a string, number, or boolean");
          }
        }
      }
    }
    validateChapters(demo, demo.steps.length, errors);
    for (var i = 0; i < demo.steps.length; i++) {
      var step = demo.steps[i];
      var at = "steps[" + i + "]";
      if (!step || typeof step !== "object") { errors.push(at + " must be an object"); continue; }
      if (step.id != null && (typeof step.id !== "string" || !validId(step.id))) errors.push(at + ".id must be a non-empty slug");
      if (step.focus != null && !/^(hotspot|cursor|zoom|spotlight)$/.test(step.focus)) errors.push(at + ".focus is not supported");
      validateFocusOptions(step, at, errors);
      var type = stepType(step);
      if (step.type && type === "shot" && step.type !== "shot") errors.push(at + ".type is not supported");
      if (type === "shot" && (typeof step.image !== "string" || !step.image)) errors.push(at + ".image is required");
      if (type === "card") validateCardStep(step, at, errors);
      if (type === "video") validateVideoStep(step, at, errors);
      if (type === "form") validateFormStep(step, at, errors);
      if (isMediaStep(step)) validateMediaOverlays(step, at, errors);
      validateAnnotations(step, at, errors);
      validateChapterRef(demo, step, at, errors);
    }
    return errors;
  }

  function validateStepIds(doc, errors) {
    var seen = {};
    for (var i = 0; i < doc.steps.length; i++) {
      var step = doc.steps[i];
      if (!step || typeof step !== "object" || step.id == null || typeof step.id !== "string") continue;
      if (seen[step.id]) errors.push("steps[" + i + "].id must be unique");
      seen[step.id] = true;
    }
  }

  function validateCardStep(step, at, errors) {
    if (typeof step.title !== "string" || !step.title) errors.push(at + ".title is required");
    if (step.subtitle != null && typeof step.subtitle !== "string") errors.push(at + ".subtitle must be a string");
    if (step.background != null && (typeof step.background !== "string" || !step.background)) errors.push(at + ".background must be a non-empty string");
    if (step.logo != null && (typeof step.logo !== "string" || !step.logo)) errors.push(at + ".logo must be a non-empty string");
    if (step.logoAlt != null && typeof step.logoAlt !== "string") errors.push(at + ".logoAlt must be a string");
    if (step.blur != null && !/^(none|light|medium|heavy)$/.test(step.blur)) errors.push(at + ".blur is not supported");
    if (step.buttons != null) {
      if (!Array.isArray(step.buttons)) {
        errors.push(at + ".buttons must be an array");
        return;
      }
      for (var i = 0; i < step.buttons.length; i++) {
        var button = step.buttons[i];
        var btnAt = at + ".buttons[" + i + "]";
        if (!button || typeof button !== "object") { errors.push(btnAt + " must be an object"); continue; }
        if (typeof button.text !== "string" || !button.text) errors.push(btnAt + ".text is required");
      }
    }
  }

  function validateVideoStep(step, at, errors) {
    if (!step.video || typeof step.video !== "object") {
      errors.push(at + ".video must be { src, poster }");
    } else {
      if (typeof step.video.src !== "string" || !step.video.src) errors.push(at + ".video.src is required");
      if (step.video.poster != null && typeof step.video.poster !== "string") errors.push(at + ".video.poster must be a string");
      if (step.video.transcript != null && typeof step.video.transcript !== "string") errors.push(at + ".video.transcript must be a string");
      if (step.video.tracks != null) {
        if (!Array.isArray(step.video.tracks)) {
          errors.push(at + ".video.tracks must be an array");
        } else {
          for (var i = 0; i < step.video.tracks.length; i++) {
            var track = step.video.tracks[i];
            var trackAt = at + ".video.tracks[" + i + "]";
            if (!track || typeof track !== "object") { errors.push(trackAt + " must be an object"); continue; }
            if (typeof track.src !== "string" || !track.src) errors.push(trackAt + ".src is required");
            if (typeof track.srclang !== "string" || !track.srclang) errors.push(trackAt + ".srclang is required");
            if (typeof track.label !== "string" || !track.label) errors.push(trackAt + ".label is required");
            if (track.default != null && typeof track.default !== "boolean") errors.push(trackAt + ".default must be a boolean");
          }
        }
      }
    }
    ["autoplay", "muted", "loop", "controls", "advanceOnEnd"].forEach(function (key) {
      if (step[key] != null && typeof step[key] !== "boolean") errors.push(at + "." + key + " must be a boolean");
    });
  }

  function validateFormStep(step, at, errors) {
    if (typeof step.title !== "string" || !step.title) errors.push(at + ".title is required");
    if (step.subtitle != null && typeof step.subtitle !== "string") errors.push(at + ".subtitle must be a string");
    if (!Array.isArray(step.fields) || step.fields.length === 0) {
      errors.push(at + ".fields must be a non-empty array");
    } else {
      for (var i = 0; i < step.fields.length; i++) {
        var field = step.fields[i];
        var fieldAt = at + ".fields[" + i + "]";
        if (!field || typeof field !== "object") { errors.push(fieldAt + " must be an object"); continue; }
        if (typeof field.name !== "string" || !field.name) errors.push(fieldAt + ".name is required");
        if (typeof field.label !== "string" || !field.label) errors.push(fieldAt + ".label is required");
        if (field.type !== "text" && field.type !== "email") errors.push(fieldAt + ".type must be \"text\" or \"email\"");
        if (field.required != null && typeof field.required !== "boolean") errors.push(fieldAt + ".required must be a boolean");
      }
    }
    if (step.submit != null) {
      if (typeof step.submit !== "object") {
        errors.push(at + ".submit must be { text, action }");
      } else {
        if (step.submit.text != null && typeof step.submit.text !== "string") errors.push(at + ".submit.text must be a string");
        if (step.submit.action != null && typeof step.submit.action !== "string") errors.push(at + ".submit.action must be a string");
      }
    }
  }

  function validateMediaOverlays(step, at, errors) {
    if (step.hotspot != null) {
      var h = step.hotspot;
      ["x", "y", "w", "h"].forEach(function (key) {
        if (typeof h[key] !== "number" || h[key] < 0 || h[key] > 100) errors.push(at + ".hotspot." + key + " must be a number in [0,100]");
      });
    }
    if (step.cta != null && (typeof step.cta !== "object" || typeof step.cta.url !== "string")) {
      errors.push(at + ".cta must be { text, url }");
    }
  }

  function validateAnnotations(step, at, errors) {
    if (step.annotations == null) return;
    if (!Array.isArray(step.annotations)) {
      errors.push(at + ".annotations must be an array");
      return;
    }
    for (var i = 0; i < step.annotations.length; i++) {
      var annotation = step.annotations[i];
      var annAt = at + ".annotations[" + i + "]";
      if (!annotation || typeof annotation !== "object") { errors.push(annAt + " must be an object"); continue; }
      if (!/^(box|arrow|label)$/.test(annotation.type)) errors.push(annAt + ".type must be box, arrow, or label");
      ["x", "y", "w", "h"].forEach(function (key) {
        if (typeof annotation[key] !== "number" || annotation[key] < 0 || annotation[key] > 100) errors.push(annAt + "." + key + " must be a number in [0,100]");
      });
      if (annotation.text != null && typeof annotation.text !== "string") errors.push(annAt + ".text must be a string");
      if (annotation.color != null && typeof annotation.color !== "string") errors.push(annAt + ".color must be a string");
    }
  }

  function validateFocusOptions(step, at, errors) {
    if (step.zoomLevel != null && (typeof step.zoomLevel !== "number" || !isFinite(step.zoomLevel) || step.zoomLevel < 1)) {
      errors.push(at + ".zoomLevel must be a number >= 1");
    }
    if (step.focusPoint != null) {
      if (!step.focusPoint || typeof step.focusPoint !== "object") {
        errors.push(at + ".focusPoint must be { x, y }");
      } else {
        ["x", "y"].forEach(function (key) {
          if (typeof step.focusPoint[key] !== "number" || step.focusPoint[key] < 0 || step.focusPoint[key] > 100) {
            errors.push(at + ".focusPoint." + key + " must be a number in [0,100]");
          }
        });
      }
    }
  }

  function svgEl(tag) {
    if (document.createElementNS) return document.createElementNS("http://www.w3.org/2000/svg", tag);
    return document.createElement(tag);
  }

  function validateChapters(doc, stepCount, errors) {
    if (doc.chapters == null) return;
    if (!Array.isArray(doc.chapters)) {
      errors.push("chapters must be an array");
      return;
    }
    var seen = {};
    for (var i = 0; i < doc.chapters.length; i++) {
      var chapter = doc.chapters[i];
      var at = "chapters[" + i + "]";
      if (!chapter || typeof chapter !== "object") { errors.push(at + " must be an object"); continue; }
      if (typeof chapter.id !== "string" || !validId(chapter.id)) errors.push(at + ".id must be a non-empty slug");
      else if (seen[chapter.id]) errors.push(at + ".id must be unique");
      else seen[chapter.id] = true;
      if (typeof chapter.title !== "string" || !chapter.title) errors.push(at + ".title is required");
      if (!isIntInRange(chapter.start, 0, stepCount - 1)) errors.push(at + ".start must be an in-range step index");
    }
  }

  function validateChapterRef(doc, step, at, errors) {
    if (step.chapter == null) return;
    if (typeof step.chapter !== "string" || !step.chapter) {
      errors.push(at + ".chapter must be a string");
      return;
    }
    if (Array.isArray(doc.chapters)) {
      for (var i = 0; i < doc.chapters.length; i++) {
        if (doc.chapters[i] && doc.chapters[i].id === step.chapter) return;
      }
      errors.push(at + ".chapter must match a chapter id");
    }
  }

  function isPosInt(n) {
    return typeof n === "number" && isFinite(n) && n > 0 && Math.floor(n) === n;
  }

  function isIntInRange(n, min, max) {
    return typeof n === "number" && isFinite(n) && Math.floor(n) === n && n >= min && n <= max;
  }

  function validId(id) {
    return /^[A-Za-z0-9_-]+$/.test(id);
  }

  function normalizeStepIds(steps) {
    var seen = {};
    var out = [];
    for (var i = 0; i < steps.length; i++) {
      var step = steps[i] || {};
      var base = step.id || slugify(stepLabel(step, i)) || ("step-" + (i + 1));
      var id = base;
      var n = 2;
      while (seen[id]) {
        id = base + "-" + n;
        n += 1;
      }
      seen[id] = true;
      step._fsId = id;
      out.push(id);
    }
    return out;
  }

  function stepIdsSignature(stepIds) {
    var count = stepIds.length;
    var first = count ? stepIds[0] : "";
    var last = count ? stepIds[count - 1] : "";
    return count + "|" + first + "|" + last + "|" + hashString(stepIds.join("|"));
  }

  function validateGoToTarget(goTo, demo) {
    if (typeof goTo === "number" && isFinite(goTo) && Math.floor(goTo) === goTo && goTo >= 0) {
      return Array.isArray(demo.steps) && goTo < demo.steps.length ? "" : "must reference an existing step";
    }
    if (typeof goTo !== "string") return "must be a step index, #chapterId, next, prev, restart, or http(s) URL";
    if (goTo === "next" || goTo === "prev" || goTo === "restart") return "";
    if (/^https?:\/\//i.test(goTo)) return "";
    if (/^#[A-Za-z0-9_-]+$/.test(goTo)) {
      var id = goTo.slice(1);
      var chapters = Array.isArray(demo.chapters) ? demo.chapters : [];
      for (var i = 0; i < chapters.length; i++) {
        if (chapters[i] && chapters[i].id === id) return "";
      }
      return "must reference an existing chapter";
    }
    return "must be a step index, #chapterId, next, prev, restart, or http(s) URL";
  }

  // Resolve a step image path against the directory of the demo.json URL.
  // The base may itself be relative, so absolutize it against the document first.
  function resolveImage(src, baseUrl) {
    if (/^([a-z]+:)?\/\//i.test(src) || src.charAt(0) === "/") return src;
    try {
      var abs = new URL(baseUrl || ".", document.baseURI).href;
      return new URL(src, abs).href;
    } catch (e) { return src; }
  }

  function isSafeUrl(url) {
    if (typeof url !== "string") return false;
    try {
      var parsed = new URL(url, document.baseURI);
      return /^(https?:|mailto:)$/i.test(parsed.protocol);
    } catch (e) {
      return false;
    }
  }

  function Flowshot(container, source, opts) {
    if (typeof container === "string") container = document.querySelector(container);
    if (!container) throw new Error("flowshot: container not found");
    this.container = container;
    this.opts = opts || {};
    this.index = 0;
    this.demo = null;
    this.baseUrl = "";
    this._preloaded = {};
    this.stepIds = [];
    this._deepLinkEnabled = false;
    this._deepLinkStart = null;
    this._suppressDeepLinkUpdate = false;
    this._persistEnabled = false;
    this._persistKey = "";
    this._resumeIndex = null;
    this._suppressPersistSave = false;
    this._captionResizeTimer = null;
    this._onViewportChange = null;
    this._vars = {};
    this._urlVars = {};
    this._urlVariableNames = [];
    this._warnedMissingVars = {};
    this._analytics = { disabled: false, beacon: "", dataLayer: false, attribution: {}, furthestIndex: 0, complete: false, lastChapter: "", dropped: false };
    injectCSS(container.ownerDocument || document);

    var self = this;
    if (typeof source === "string") {
      this.baseUrl = source;
      fetch(source).then(function (r) {
        if (!r.ok) throw new Error("flowshot: failed to load " + source + " (" + r.status + ")");
        return r.json();
      }).then(function (d) { self._init(d); }).catch(function (e) {
        self._showFallback(e.message);
      });
    } else {
      this.baseUrl = this.opts.base || "";
      this._init(source);
    }
  }

  Flowshot.prototype._init = function (demo) {
    this.demo = demo || {};
    this.steps = Array.isArray(demo.steps) ? demo.steps : [];
    var errors = validateDemoDocument(this.demo);
    if (errors.length) { this._showFallback("Invalid demo: " + errors.join("; ")); return; }
    this.stepIds = normalizeStepIds(this.steps);
    this._setupVariables();
    this._setupDeepLink();
    this._setupPersistence();
    this._setupAnalytics();
    this._build();
    var startIndex = this._initialIndex();
    this._emitEvent("ready", this._deepLinkStart ? { deepLink: this._deepLinkStart } : {});
    this._suppressPersistSave = true;
    this.goTo(startIndex);
    this._suppressPersistSave = false;
    this._showResumePrompt();
    if (this.opts.autoplay || this.demo.autoplay) this._startAutoplay();
  };

  Flowshot.prototype._showFallback = function (message) {
    if (typeof console !== "undefined" && console.warn) console.warn("flowshot:", message);
    var box = el("div", "fs-fallback", { role: "status" });
    var title = el("strong");
    title.textContent = "flowshot demo unavailable";
    var detail = el("span");
    detail.textContent = message || "The demo could not be loaded.";
    box.appendChild(title);
    box.appendChild(detail);
    this.container.textContent = "";
    this.container.appendChild(box);
  };

  Flowshot.prototype._build = function () {
    var d = this.demo;
    var root = el("div", "fs-root" + (this.opts.fit ? " is-fit" : ""), { tabindex: "0", role: "group", "aria-roledescription": "interactive demo" });
    if (d.title) root.setAttribute("aria-label", this._text(d.title));
    applyTheme(root, d.theme, this.opts);

    var stage = el("div", "fs-stage");
    if (d.size && d.size.width && d.size.height) {
      stage.style.aspectRatio = d.size.width + " / " + d.size.height;
    }
    var stageInner = el("div", "fs-stage-inner");
    var img = el("img", "fs-img", { alt: "" });
    var video = el("video", "fs-video", { playsinline: "", preload: "metadata" });
    video.style.display = "none";
    var card = el("div", "fs-card", { hidden: "", "aria-live": "polite" });
    var hotspot = el("button", "fs-hotspot", { type: "button", "aria-label": "Next step" });
    hotspot.style.display = "none";
    var annotations = el("div", "fs-annotations", { "aria-hidden": "true" });
    var caption = el("div", "fs-caption");
    caption.style.display = "none";
    var bar = el("div", "fs-bar");
    var live = el("div", "fs-sr", { "aria-live": "polite", "aria-atomic": "true" });
    var spotlight = el("div", "fs-spotlight");
    var cursor = el("div", "fs-cursor", { "aria-hidden": "true" });
    stageInner.appendChild(img);
    stageInner.appendChild(video);
    stageInner.appendChild(hotspot);
    stageInner.appendChild(annotations);
    stageInner.appendChild(cursor);
    stage.appendChild(stageInner);
    stage.appendChild(card);
    stage.appendChild(spotlight);
    stage.appendChild(caption);
    stage.appendChild(bar);

    var controls = el("div", "fs-controls");
    var prev = el("button", "fs-btn fs-prev", { type: "button", "aria-label": "Previous step" });
    prev.textContent = "Back";
    var next = el("button", "fs-btn fs-next", { type: "button", "aria-label": "Next step" });
    next.textContent = "Next";
    var chapterWrap = null;
    var chapterMenu = null;
    var chapterBtn = null;
    if (Array.isArray(d.chapters) && d.chapters.length) {
      chapterWrap = el("div", "fs-menu-wrap");
      chapterBtn = el("button", "fs-btn fs-menu-btn", { type: "button", "aria-label": "Chapter menu", "aria-expanded": "false" });
      chapterBtn.textContent = "\u2630";
      chapterMenu = el("div", "fs-menu", { hidden: "", "aria-label": "Chapters" });
      chapterWrap.appendChild(chapterBtn);
      chapterWrap.appendChild(chapterMenu);
    }
    var dots = el("div", "fs-dots");
    var count = el("div", "fs-count");
    controls.appendChild(prev);
    if (chapterWrap) controls.appendChild(chapterWrap);
    controls.appendChild(next);
    controls.appendChild(dots);
    controls.appendChild(count);
    var resume = el("div", "fs-resume", { hidden: "" });
    var resumeText = el("span");
    var resumeBtn = el("button", "fs-btn", { type: "button" });
    resumeBtn.textContent = "Resume";
    var restartBtn = el("button", "fs-btn", { type: "button" });
    restartBtn.textContent = "Restart";
    resume.appendChild(resumeText);
    resume.appendChild(resumeBtn);
    resume.appendChild(restartBtn);
    var transcript = el("details", "fs-transcript", { hidden: "" });
    var transcriptSummary = el("summary");
    transcriptSummary.textContent = "Transcript";
    var transcriptBody = el("div");
    transcript.appendChild(transcriptSummary);
    transcript.appendChild(transcriptBody);

    root.appendChild(stage);
    root.appendChild(live);
    root.appendChild(transcript);
    root.appendChild(resume);
    root.appendChild(controls);
    this.container.textContent = "";
    this.container.appendChild(root);

    this.dom = {
      root: root, stage: stage, stageInner: stageInner, img: img, video: video, card: card, hotspot: hotspot, annotations: annotations, caption: caption, bar: bar,
      spotlight: spotlight, cursor: cursor,
      transcript: transcript, transcriptBody: transcriptBody,
      live: live, resume: resume, resumeText: resumeText, resumeBtn: resumeBtn, restartBtn: restartBtn,
      prev: prev, next: next, dots: dots, count: count, chapterBtn: chapterBtn, chapterMenu: chapterMenu
    };

    var self = this;
    hotspot.addEventListener("click", function () { self.next(); });
    next.addEventListener("click", function () { self.next(); });
    prev.addEventListener("click", function () { self.prev(); });
    resumeBtn.addEventListener("click", function () {
      self._hideResumePrompt();
      if (self._resumeIndex != null) self.goTo(self._resumeIndex);
    });
    restartBtn.addEventListener("click", function () {
      self._clearProgress();
      self._hideResumePrompt();
      self._suppressPersistSave = true;
      self.goTo(0);
      self._suppressPersistSave = false;
    });
    if (chapterBtn) {
      chapterBtn.addEventListener("click", function () { self._toggleChapterMenu(); });
      chapterBtn.setAttribute("aria-haspopup", "menu");
      this._renderChapters();
    }
    root.addEventListener("keydown", function (e) {
      if (e.key === "Escape") self._closeChapterMenu(true);
      if ((e.key === "Enter" || e.key === " ") && isInteractiveTarget(e.target)) return;
      if (e.key === "ArrowRight" || e.key === "Enter" || e.key === " ") { e.preventDefault(); self.next(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); self.prev(); }
    });
    img.addEventListener("load", function () { self._placeCaption(); });
    video.addEventListener("loadedmetadata", function () { self._placeCaption(); });
    video.addEventListener("ended", function () {
      var step = self.steps[self.index];
      if (stepType(step) === "video" && step.advanceOnEnd) self.next();
    });
    this._bindCaptionResize();

    for (var i = 0; i < this.steps.length; i++) {
      (function (idx) {
        var dot = el("button", "fs-dot", { type: "button", "aria-label": self._stepControlLabel(idx) });
        dot.addEventListener("click", function () { self.goTo(idx); });
        dots.appendChild(dot);
      })(i);
    }
  };

  Flowshot.prototype.goTo = function (i) {
    if (i < 0 || i >= this.steps.length) return;
    this._stopStepVideo();
    this.index = i;
    var step = this.steps[i];
    var dom = this.dom;
    if (stepType(step) === "card") this._renderCard(step);
    else if (stepType(step) === "form") {
      this._hideCard();
      this._renderForm(step);
    }
    else if (stepType(step) === "video") {
      this._hideCard();
      this._renderVideo(step);
    }
    else {
      this._hideCard();
      this._hideTranscript();
      dom.video.style.display = "none";
      dom.img.style.display = "block";
      dom.img.className = "fs-img";
      dom.img.src = resolveImage(step.image, this.baseUrl);
      dom.img.alt = this._text(step.caption) || ("Step " + (i + 1));
    }

    if (isMediaStep(step) && step.hotspot) {
      var h = step.hotspot;
      dom.hotspot.style.display = "block";
      dom.hotspot.style.left = clampPct(h.x) + "%";
      dom.hotspot.style.top = clampPct(h.y) + "%";
      dom.hotspot.style.width = clampPct(h.w) + "%";
      dom.hotspot.style.height = clampPct(h.h) + "%";
      dom.hotspot.setAttribute("aria-label", this._text(step.caption) || "Next step");
    } else {
      dom.hotspot.style.display = "none";
    }

    if (isMediaStep(step)) this._renderCaption(step);
    else dom.caption.style.display = "none";
    this._renderAnnotations(step);
    this._placeCaption();
    this._applyFocusStyle(step);

    dom.bar.style.width = ((i + 1) / this.steps.length * 100) + "%";
    dom.count.textContent = (i + 1) + " / " + this.steps.length;
    dom.prev.disabled = i === 0;
    dom.next.disabled = isChooserCard(step);
    dom.next.textContent = i === this.steps.length - 1 ? "Restart" : "Next";
    var dotEls = dom.dots.children;
    for (var k = 0; k < dotEls.length; k++) {
      dotEls[k].classList.toggle("is-on", k === i);
      if (k === i) dotEls[k].setAttribute("aria-current", "step");
      else dotEls[k].removeAttribute("aria-current");
    }
    this._updateChapters();
    this._announceStep();
    this._trackStepView(i, step);
    this._updateDeepLink();
    this._saveProgress();
    this._preloadStep(i + 1);

    if (typeof this.opts.onStep === "function") this.opts.onStep(i, step);
  };

  Flowshot.prototype._renderCard = function (step) {
    var dom = this.dom;
    var card = dom.card;
    card.textContent = "";
    card.removeAttribute("hidden");
    dom.hotspot.style.display = "none";
    dom.caption.style.display = "none";
    dom.video.style.display = "none";
    dom.video.className = "fs-video";
    this._hideTranscript();

    if (step.background) {
      dom.img.style.display = "block";
      dom.img.className = "fs-img is-blur-" + (step.blur || "medium");
      dom.img.src = resolveImage(step.background, this.baseUrl);
      dom.img.alt = "";
    } else {
      dom.img.removeAttribute("src");
      dom.img.style.display = "none";
      dom.img.className = "fs-img";
    }

    var inner = el("div", "fs-card-inner");
    if (step.logo) {
      var logo = el("img", "fs-card-logo");
      logo.src = resolveImage(step.logo, this.baseUrl);
      logo.alt = step.logoAlt || "";
      inner.appendChild(logo);
    }
    var title = el("h2", "fs-card-title");
    title.textContent = this._text(step.title);
    inner.appendChild(title);
    if (step.subtitle) {
      var subtitle = el("p", "fs-card-subtitle");
      subtitle.textContent = this._text(step.subtitle);
      inner.appendChild(subtitle);
    }
    if (Array.isArray(step.buttons) && step.buttons.length) {
      var actions = el("div", "fs-card-actions");
      for (var i = 0; i < step.buttons.length; i++) {
        this._appendCardButton(actions, step.buttons[i]);
      }
      inner.appendChild(actions);
    }
    card.appendChild(inner);
  };

  Flowshot.prototype._renderForm = function (step) {
    var dom = this.dom;
    var card = dom.card;
    card.textContent = "";
    card.removeAttribute("hidden");
    dom.hotspot.style.display = "none";
    dom.caption.style.display = "none";
    dom.video.style.display = "none";
    dom.img.style.display = "none";
    dom.img.className = "fs-img";
    this._hideTranscript();

    var inner = el("div", "fs-card-inner");
    var title = el("h2", "fs-card-title");
    title.textContent = this._text(step.title);
    inner.appendChild(title);
    if (step.subtitle) {
      var subtitle = el("p", "fs-card-subtitle");
      subtitle.textContent = this._text(step.subtitle);
      inner.appendChild(subtitle);
    }
    var form = el("form", "fs-form", { novalidate: "" });
    form.noValidate = true;
    var fields = Array.isArray(step.fields) ? step.fields : [];
    for (var i = 0; i < fields.length; i++) this._appendFormField(form, fields[i]);
    var submit = el("button", "fs-card-btn", { type: "submit" });
    submit.textContent = this._text(step.submit && step.submit.text) || "Submit";
    var status = el("div", "fs-form-status", { id: "fs-form-status-" + this.index, role: "status", "aria-live": "polite" });
    form.appendChild(submit);
    form.appendChild(status);
    var self = this;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      self._submitFormStep(step, form, status);
    });
    inner.appendChild(form);
    card.appendChild(inner);
  };

  Flowshot.prototype._appendFormField = function (form, field) {
    var wrap = el("div", "fs-field");
    var id = "fs-field-" + this.index + "-" + field.name;
    var label = el("label", "", { for: id });
    label.textContent = this._text(field.label) || field.name;
    var input = el("input", "", { id: id, name: field.name, type: field.type || "text" });
    input.name = field.name;
    input.type = field.type || "text";
    input.setAttribute("data-label", this._text(field.label) || field.name);
    input.value = "";
    if (field.required) {
      input.required = true;
      input.setAttribute("required", "");
    }
    wrap.appendChild(label);
    wrap.appendChild(input);
    form.appendChild(wrap);
  };

  Flowshot.prototype._submitFormStep = function (step, form, status) {
    var inputs = this._formInputs(form);
    var values = {};
    var names = [];
    var valid = true;
    var labels = [];
    var firstInvalid = null;
    for (var i = 0; i < inputs.length; i++) {
      var input = inputs[i];
      var name = input.name || input.getAttribute("name");
      var value = input.value || "";
      if (!name) continue;
      input.setAttribute("aria-invalid", "false");
      input.removeAttribute("aria-describedby");
      if ((input.required || input.hasAttribute("required")) && !value.trim()) {
        valid = false;
        firstInvalid = firstInvalid || input;
        labels.push(input.getAttribute("data-label") || name);
        this._markInvalid(input, status);
      }
      if ((input.type || input.getAttribute("type")) === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        valid = false;
        firstInvalid = firstInvalid || input;
        labels.push(input.getAttribute("data-label") || name);
        this._markInvalid(input, status);
      }
      values[name] = value;
      names.push(name);
    }
    if (!valid) {
      status.textContent = "Please complete: " + labels.join(", ") + ".";
      if (firstInvalid && firstInvalid.focus) firstInvalid.focus();
      return;
    }
    var self = this;
    var action = step.submit && step.submit.action;
    var done = function () {
      self._emitEvent("lead_submit", { fields: names });
      self._showFormThanks(form, status);
    };
    if (action && window.fetch) {
      status.textContent = "Submitting...";
      window.fetch(action, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(values)
      }).then(function (r) {
        if (!r.ok) throw new Error("submit failed");
        done();
      }).catch(function () {
        status.textContent = "Submission failed. Please try again.";
      });
    } else {
      done();
    }
  };

  Flowshot.prototype._markInvalid = function (input, status) {
    input.setAttribute("aria-invalid", "true");
    if (status && status.getAttribute && status.getAttribute("id")) input.setAttribute("aria-describedby", status.getAttribute("id"));
    return false;
  };

  Flowshot.prototype._formInputs = function (node) {
    var found = [];
    function walk(current) {
      if (current.tagName === "INPUT") found.push(current);
      var children = current.children || [];
      for (var i = 0; i < children.length; i++) walk(children[i]);
    }
    walk(node);
    return found;
  };

  Flowshot.prototype._showFormThanks = function (form, status) {
    form.textContent = "";
    var msg = el("div", "fs-form-status", { role: "status" });
    msg.textContent = "Thanks. We received your details.";
    form.appendChild(msg);
    if (status) status.textContent = "";
  };

  Flowshot.prototype._renderVideo = function (step) {
    var dom = this.dom;
    var video = dom.video;
    var opts = step.video || {};
    var reduced = prefersReducedMotion();
    dom.img.style.display = "none";
    dom.img.className = "fs-img";
    video.style.display = "block";
    video.className = "fs-video";
    video.textContent = "";
    video.src = resolveImage(opts.src, this.baseUrl);
    if (opts.poster) video.poster = resolveImage(opts.poster, this.baseUrl);
    else video.removeAttribute("poster");
    video.preload = "metadata";
    video.muted = step.muted !== false;
    video.loop = step.loop === true;
    video.controls = step.controls === true || reduced;
    video.autoplay = step.autoplay !== false && !reduced;
    this._renderTracks(video, opts.tracks);
    this._renderTranscript(this._text(opts.transcript));
    if (video.autoplay) {
      var play = video.play();
      if (play && play.catch) play.catch(function () {});
    }
  };

  Flowshot.prototype._renderTracks = function (video, tracks) {
    if (!Array.isArray(tracks)) return;
    for (var i = 0; i < tracks.length; i++) {
      var spec = tracks[i] || {};
      if (!spec.src) continue;
      var track = el("track", "", { kind: "captions", src: resolveImage(spec.src, this.baseUrl) });
      if (spec.srclang) track.setAttribute("srclang", spec.srclang);
      if (spec.label) track.setAttribute("label", spec.label);
      if (spec.default) {
        track.default = true;
        track.setAttribute("default", "");
      }
      video.appendChild(track);
    }
  };

  Flowshot.prototype._renderTranscript = function (transcript) {
    if (!this.dom || !this.dom.transcript) return;
    this._hideTranscript();
    if (!transcript) return;
    this.dom.transcript.removeAttribute("hidden");
    var body = this.dom.transcriptBody;
    if ((/\.(txt|md|vtt)$/i.test(transcript) || transcript.indexOf("/") !== -1) && typeof fetch === "function") {
      body.textContent = "Loading transcript...";
      fetch(resolveImage(transcript, this.baseUrl)).then(function (r) {
        if (!r.ok) throw new Error("transcript failed");
        return r.text();
      }).then(function (text) {
        body.textContent = text;
      }).catch(function () {
        body.textContent = transcript;
      });
    } else {
      body.textContent = transcript;
    }
  };

  Flowshot.prototype._renderAnnotations = function (step) {
    var layer = this.dom.annotations;
    if (!layer) return;
    layer.textContent = "";
    var annotations = step && Array.isArray(step.annotations) ? step.annotations : [];
    for (var i = 0; i < annotations.length; i++) this._appendAnnotation(layer, annotations[i]);
  };

  Flowshot.prototype._appendAnnotation = function (layer, spec) {
    spec = spec || {};
    var type = spec.type === "arrow" || spec.type === "label" ? spec.type : "box";
    var node = el("div", "fs-ann fs-ann-" + type);
    node.style.left = clampPct(spec.x) + "%";
    node.style.top = clampPct(spec.y) + "%";
    node.style.width = clampPct(spec.w) + "%";
    node.style.height = clampPct(spec.h) + "%";
    if (spec.color) node.style.setProperty("--fs-ann-color", spec.color);
    if (type === "label") {
      node.textContent = this._text(spec.text) || "";
    } else if (type === "arrow") {
      var svg = svgEl("svg");
      svg.setAttribute("viewBox", "0 0 100 100");
      svg.setAttribute("preserveAspectRatio", "none");
      var markerId = "fs-ann-arrowhead-" + hashString([layer.children.length, spec.x, spec.y, spec.w, spec.h, spec.color || ""].join("|"));
      var defs = svgEl("defs");
      var marker = svgEl("marker");
      marker.setAttribute("id", markerId);
      marker.setAttribute("markerWidth", "7");
      marker.setAttribute("markerHeight", "7");
      marker.setAttribute("refX", "6");
      marker.setAttribute("refY", "3.5");
      marker.setAttribute("orient", "auto");
      var arrowHead = svgEl("path");
      arrowHead.setAttribute("d", "M0,0 L7,3.5 L0,7 Z");
      arrowHead.style.fill = "var(--fs-ann-color)";
      marker.appendChild(arrowHead);
      defs.appendChild(marker);
      svg.appendChild(defs);
      var line = svgEl("line");
      line.setAttribute("x1", "0");
      line.setAttribute("y1", "0");
      line.setAttribute("x2", "100");
      line.setAttribute("y2", "100");
      line.setAttribute("marker-end", "url(#" + markerId + ")");
      svg.appendChild(line);
      node.appendChild(svg);
    } else if (spec.text) {
      node.setAttribute("aria-label", this._text(spec.text));
    }
    layer.appendChild(node);
  };

  Flowshot.prototype._appendCardButton = function (actions, spec) {
    var self = this;
    spec = spec || {};
    var button = el("button", "fs-card-btn" + (spec.variant === "ghost" ? " is-ghost" : ""), { type: "button" });
    button.textContent = this._text(spec.text) || "Continue";
    var targetError = validateGoToTarget(spec.goTo, this.demo);
    if (targetError) {
      button.disabled = true;
      button.setAttribute("disabled", "");
      button.setAttribute("aria-disabled", "true");
      button.setAttribute("title", "Unavailable");
      actions.appendChild(button);
      return;
    }
    button.addEventListener("click", function () {
      self._stopAutoplay();
      self._emitEvent("branch_click", { goTo: spec.goTo, label: spec.text || "" });
      self._resolveGoTo(spec.goTo);
    });
    actions.appendChild(button);
  };

  Flowshot.prototype._hideCard = function () {
    this.dom.card.textContent = "";
    this.dom.card.setAttribute("hidden", "");
  };

  Flowshot.prototype._hideTranscript = function () {
    if (!this.dom || !this.dom.transcript) return;
    this.dom.transcript.setAttribute("hidden", "");
    this.dom.transcript.open = false;
    this.dom.transcriptBody.textContent = "";
  };

  Flowshot.prototype._stopStepVideo = function () {
    if (!this.dom || !this.dom.video) return;
    var video = this.dom.video;
    video.pause();
    video.textContent = "";
    video.removeAttribute("src");
    video.load();
    video.style.display = "none";
  };

  Flowshot.prototype._preloadStep = function (index) {
    if (index < 0 || index >= this.steps.length || typeof Image === "undefined") return;
    var step = this.steps[index];
    var src = "";
    if (stepType(step) === "shot") src = step.image;
    else if (stepType(step) === "card") src = step.background || "";
    else if (stepType(step) === "video" && step.video) src = step.video.poster || "";
    if (!src) return;
    var url = resolveImage(src, this.baseUrl);
    if (this._preloaded[url]) return;
    var img = new Image();
    img.src = url;
    this._preloaded[url] = img;
  };

  Flowshot.prototype._resolveGoTo = function (target) {
    var index = this._targetIndex(target);
    if (index != null) return this.goTo(index);
    if (target === "next") return this._linearNext();
    if (target === "prev") return this.prev();
    if (target === "restart") return this.goTo(0);
    if (typeof target !== "string") return;
    if (isSafeUrl(target)) {
      window.open(target, "_blank", "noopener");
      return;
    }
  };

  Flowshot.prototype._targetIndex = function (target) {
    if (typeof target === "number" && target >= 0 && target < this.steps.length) return target;
    if (typeof target !== "string") return null;
    if (/^\d+$/.test(target)) {
      var n = Number(target);
      return n >= 0 && n < this.steps.length ? n : null;
    }
    if (target.charAt(0) === "#") return this._chapterIndex(target.slice(1));
    for (var i = 0; i < this.stepIds.length; i++) {
      if (this.stepIds[i] === target) return i;
    }
    return null;
  };

  Flowshot.prototype._chapterIndex = function (id) {
    var chapters = this.demo && Array.isArray(this.demo.chapters) ? this.demo.chapters : [];
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i] && chapters[i].id === id) return chapters[i].start;
    }
    return null;
  };

  Flowshot.prototype._initialIndex = function () {
    var target = null;
    if (this.opts.initialChapter) {
      target = this._chapterIndex(this.opts.initialChapter);
      if (target != null) this._deepLinkStart = { type: "chapter", id: this.opts.initialChapter, index: target };
    }
    if (target == null && this.opts.initialStep != null) {
      target = this._targetIndex(this.opts.initialStep);
      if (target != null) this._deepLinkStart = { type: "step", id: this.stepIds[target], index: target };
    }
    if (target == null && this._deepLinkEnabled) {
      var parsed = this._parseDeepLinkHash();
      if (parsed.type === "chapter") target = this._chapterIndex(parsed.id);
      else if (parsed.type === "step") target = this._targetIndex(parsed.id);
      if (target != null) this._deepLinkStart = { type: parsed.type, id: parsed.id, index: target };
    }
    return target == null ? 0 : target;
  };

  Flowshot.prototype._setupDeepLink = function () {
    this._deepLinkEnabled = this.opts.deepLink === "flowshot" || this.opts.deepLink === true;
  };

  Flowshot.prototype._setupPersistence = function () {
    this._persistEnabled = this.opts.persistProgress === true || this.opts.persistProgress === "true";
    if (!this._persistEnabled) return;
    this._persistKey = "flowshot:progress:" + hashString((this.baseUrl || "") + "|" + (this.demo.title || "") + "|" + stepIdsSignature(this.stepIds));
    this._resumeIndex = this._readProgress();
  };

  Flowshot.prototype._readProgress = function () {
    try {
      if (!window.localStorage || !this._persistKey) return null;
      var raw = window.localStorage.getItem(this._persistKey);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || typeof data.index !== "number" || !isFinite(data.index)) return null;
      var index = Math.floor(data.index);
      if (index <= 0 || index >= this.steps.length) return null;
      if (typeof data.id === "string" && data.id && data.id !== this.stepIds[index]) {
        for (var i = 1; i < this.stepIds.length; i++) {
          if (this.stepIds[i] === data.id) return i;
        }
        return null;
      }
      return index;
    } catch (e) {}
    return null;
  };

  Flowshot.prototype._saveProgress = function () {
    if (!this._persistEnabled || !this._persistKey || this._suppressPersistSave) return;
    try {
      if (!window.localStorage) return;
      window.localStorage.setItem(this._persistKey, JSON.stringify({ index: this.index, id: this.stepIds[this.index] || "", updated: Date.now() }));
    } catch (e) {}
  };

  Flowshot.prototype._clearProgress = function () {
    if (!this._persistEnabled || !this._persistKey) return;
    try {
      if (window.localStorage) window.localStorage.removeItem(this._persistKey);
    } catch (e) {}
  };

  Flowshot.prototype._showResumePrompt = function () {
    if (!this.dom || !this.dom.resume || this._resumeIndex == null || this._deepLinkStart) return;
    this.dom.resumeText.textContent = "Resume from step " + (this._resumeIndex + 1) + " of " + this.steps.length + "?";
    this.dom.resume.removeAttribute("hidden");
  };

  Flowshot.prototype._hideResumePrompt = function () {
    if (this.dom && this.dom.resume) this.dom.resume.setAttribute("hidden", "");
  };

  Flowshot.prototype._setupVariables = function () {
    var vars = {};
    var defaults = isPlainObject(this.demo.variables) ? this.demo.variables : {};
    for (var key in defaults) vars[key] = String(defaults[key]);
    try {
      var params = new URLSearchParams((window.location && window.location.search) || "");
      var self = this;
      if (params.forEach) params.forEach(function (value, key) {
        vars[key] = String(value);
        self._urlVars[key] = true;
      });
    } catch (e) {}
    this._vars = vars;
    var tokenNames = collectTemplateVars(this.demo, {});
    this._urlVariableNames = [];
    for (var name in tokenNames) {
      if (this._urlVars[name]) this._urlVariableNames.push(name);
    }
    this._urlVariableNames.sort();
  };

  Flowshot.prototype._text = function (text) {
    if (text == null) return "";
    var self = this;
    return String(text).replace(/\{\{\s*([A-Za-z0-9_-]+)\s*(?:\|\s*([^}]*?))?\s*\}\}/g, function (_match, name, fallback) {
      if (Object.prototype.hasOwnProperty.call(self._vars, name)) {
        return self._vars[name];
      }
      if (fallback != null) return fallback;
      if (!self._warnedMissingVars[name]) {
        self._warnedMissingVars[name] = true;
        if (typeof console !== "undefined" && console.warn) console.warn("flowshot: missing variable " + name);
      }
      return "";
    });
  };

  Flowshot.prototype._stepLabel = function (step, index) {
    return this._text(stepLabel(step, index));
  };

  Flowshot.prototype._parseDeepLinkHash = function () {
    var hash = window.location && window.location.hash ? window.location.hash : "";
    var match = hash.match(/^#flowshot-(step|chapter)-(.+)$/);
    if (!match) return {};
    return { type: match[1], id: decodeURIComponent(match[2]) };
  };

  Flowshot.prototype._updateDeepLink = function () {
    if (!this._deepLinkEnabled || this._suppressDeepLinkUpdate) return;
    var id = this.stepIds[this.index] || ("step-" + (this.index + 1));
    var hash = "#flowshot-step-" + encodeURIComponent(id);
    if (window.location && window.location.hash === hash) return;
    if (window.history && window.history.replaceState) window.history.replaceState(null, "", hash);
    else if (window.location) window.location.hash = hash;
  };

  Flowshot.prototype._stepControlLabel = function (index) {
    return "Go to step " + (index + 1) + ": " + trimText(this._stepLabel(this.steps[index], index), "Step " + (index + 1));
  };

  Flowshot.prototype._currentChapterTitle = function () {
    var id = this._currentChapterId();
    var chapters = this.demo && Array.isArray(this.demo.chapters) ? this.demo.chapters : [];
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i] && chapters[i].id === id) return this._text(chapters[i].title) || chapters[i].id;
    }
    return "";
  };

  Flowshot.prototype._announceStep = function () {
    if (!this.dom || !this.dom.live) return;
    var step = this.steps[this.index];
    var parts = ["Step " + (this.index + 1) + " of " + this.steps.length, trimText(this._stepLabel(step, this.index), "")];
    var chapter = this._currentChapterTitle();
    if (chapter) parts.push("Chapter " + chapter);
    this.dom.live.textContent = parts.filter(Boolean).join(". ");
  };

  Flowshot.prototype._renderChapters = function () {
    var self = this;
    var menu = this.dom.chapterMenu;
    if (!menu) return;
    menu.textContent = "";
    menu.setAttribute("role", "menu");
    var chapters = this.demo.chapters || [];
    for (var i = 0; i < chapters.length; i++) {
      (function (chapter) {
        var button = el("button", "", { type: "button", role: "menuitem", tabindex: "-1" });
        button.textContent = self._text(chapter.title);
        button.addEventListener("click", function () {
          self._closeChapterMenu(true);
          self.goTo(chapter.start);
        });
        menu.appendChild(button);
      })(chapters[i]);
    }
    menu.addEventListener("keydown", function (e) { self._handleChapterMenuKey(e); });
  };

  Flowshot.prototype._toggleChapterMenu = function () {
    if (!this.dom.chapterMenu) return;
    if (this.dom.chapterMenu.hasAttribute("hidden")) {
      this.dom.chapterMenu.removeAttribute("hidden");
      this.dom.chapterBtn.setAttribute("aria-expanded", "true");
      this._focusChapterMenuItem();
    } else {
      this._closeChapterMenu(true);
    }
  };

  Flowshot.prototype._closeChapterMenu = function (returnFocus) {
    if (!this.dom.chapterMenu) return;
    this.dom.chapterMenu.setAttribute("hidden", "");
    this.dom.chapterBtn.setAttribute("aria-expanded", "false");
    if (returnFocus && this.dom.chapterBtn && this.dom.chapterBtn.focus) this.dom.chapterBtn.focus();
  };

  Flowshot.prototype._focusChapterMenuItem = function (offset) {
    var menu = this.dom.chapterMenu;
    if (!menu || !menu.children.length) return;
    var active = this._currentChapterId();
    var chapters = this.demo.chapters || [];
    var index = 0;
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i] && chapters[i].id === active) { index = i; break; }
    }
    if (typeof offset === "number") index = Math.max(0, Math.min(menu.children.length - 1, offset));
    if (menu.children[index] && menu.children[index].focus) menu.children[index].focus();
  };

  Flowshot.prototype._handleChapterMenuKey = function (e) {
    var menu = this.dom.chapterMenu;
    if (!menu) return;
    var items = menu.children || [];
    if (!items.length) return;
    var current = 0;
    for (var i = 0; i < items.length; i++) {
      if (items[i] === document.activeElement) { current = i; break; }
    }
    if (e.key === "Escape") {
      e.preventDefault();
      this._closeChapterMenu(true);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      this._focusChapterMenuItem((current + 1) % items.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      this._focusChapterMenuItem((current - 1 + items.length) % items.length);
    } else if (e.key === "Home") {
      e.preventDefault();
      this._focusChapterMenuItem(0);
    } else if (e.key === "End") {
      e.preventDefault();
      this._focusChapterMenuItem(items.length - 1);
    }
  };

  Flowshot.prototype._currentChapterId = function () {
    var step = this.steps[this.index];
    if (step && step.chapter) return step.chapter;
    var chapters = this.demo && Array.isArray(this.demo.chapters) ? this.demo.chapters : [];
    var current = "";
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i].start <= this.index) current = chapters[i].id;
    }
    return current;
  };

  Flowshot.prototype._updateChapters = function () {
    var menu = this.dom.chapterMenu;
    if (!menu) return;
    var active = this._currentChapterId();
    var chapters = this.demo.chapters || [];
    for (var i = 0; i < menu.children.length; i++) {
      menu.children[i].classList.toggle("is-on", chapters[i] && chapters[i].id === active);
    }
  };

  Flowshot.prototype._renderCaption = function (step) {
    var cap = this.dom.caption;
    cap.textContent = "";
    if (!step.caption && !step.cta) { cap.style.display = "none"; return; }
    cap.style.display = "block";
    if (step.caption) cap.appendChild(document.createTextNode(this._text(step.caption)));
    if (step.cta && step.cta.url) {
      var safe = isSafeUrl(step.cta.url);
      var a = safe ? el("a", "fs-cta", { href: step.cta.url, target: "_blank", rel: "noopener noreferrer" }) : el("span", "fs-cta");
      a.textContent = this._text(step.cta.text) || "Learn more";
      if (safe) {
        var self = this;
        a.addEventListener("click", function () {
          self._emitEvent("cta_click", { url: step.cta.url });
        });
      }
      cap.appendChild(document.createElement("br"));
      cap.appendChild(a);
    }
  };

  // Anchor the caption near the hotspot, flip above when low, clamp inside the stage.
  Flowshot.prototype._placeCaption = function () {
    var step = this.steps[this.index];
    var cap = this.dom.caption;
    if (cap.style.display === "none") return;
    var h = step && step.hotspot;
    cap.style.bottom = "";
    cap.style.top = "";
    if (h) {
      var cx = clampPct(h.x + h.w / 2);
      var below = (h.y + h.h) < 62;
      if (step.captionPosition === "above") below = false;
      else if (step.captionPosition === "below") below = true;
      cap.style.left = cx + "%";
      if (below) cap.style.top = "calc(" + clampPct(h.y + h.h) + "% + 10px)";
      else cap.style.bottom = "calc(" + clampPct(100 - h.y) + "% + 10px)";
    } else {
      cap.style.left = "50%";
      cap.style.bottom = "16px";
    }
    // Horizontal clamp so the bubble never overflows the stage edges.
    var stageRect = this.dom.stage.getBoundingClientRect();
    if (!stageRect.width) return;
    var capRect = cap.getBoundingClientRect();
    var leftEdge = capRect.left - stageRect.left;
    var rightEdge = capRect.right - stageRect.left;
    var shift = 0;
    if (leftEdge < 8) shift = 8 - leftEdge;
    else if (rightEdge > stageRect.width - 8) shift = (stageRect.width - 8) - rightEdge;
    if (shift) {
      var basePct = parseFloat(cap.style.left);
      cap.style.left = "calc(" + basePct + "% + " + Math.round(shift) + "px)";
    }
  };

  Flowshot.prototype._bindCaptionResize = function () {
    if (!window.addEventListener) return;
    var self = this;
    this._onViewportChange = function () {
      if (self._captionResizeTimer && typeof clearTimeout === "function") clearTimeout(self._captionResizeTimer);
      if (typeof setTimeout === "function") {
        self._captionResizeTimer = setTimeout(function () {
          self._captionResizeTimer = null;
          self._placeCaption();
        }, 80);
      } else {
        self._placeCaption();
      }
    };
    window.addEventListener("resize", this._onViewportChange);
    window.addEventListener("orientationchange", this._onViewportChange);
  };

  Flowshot.prototype._focusTarget = function (step) {
    if (step && step.focusPoint) return { x: clampPct(step.focusPoint.x), y: clampPct(step.focusPoint.y) };
    var h = step && step.hotspot;
    if (!h) return { x: 50, y: 50 };
    return { x: clampPct(h.x + h.w / 2), y: clampPct(h.y + h.h / 2) };
  };

  Flowshot.prototype._applyFocusStyle = function (step) {
    var style = focusStyle(step);
    var target = this._focusTarget(step);
    var dom = this.dom;
    dom.root.style.setProperty("--fs-focus-x", target.x + "%");
    dom.root.style.setProperty("--fs-focus-y", target.y + "%");
    dom.root.style.setProperty("--fs-zoom", style === "zoom" && isMediaStep(step) ? String(this._zoomLevel(step)) : "1");
    dom.stage.className = "fs-stage";
    dom.spotlight.style.display = style === "spotlight" ? "block" : "none";
    dom.cursor.style.display = style === "cursor" ? "block" : "none";
  };

  Flowshot.prototype._zoomLevel = function (step) {
    var level = step && typeof step.zoomLevel === "number" ? step.zoomLevel : 1.55;
    return Math.max(1, Math.min(4, level));
  };

  Flowshot.prototype.next = function () {
    this._stopAutoplay();
    if (isChooserCard(this.steps[this.index])) return;
    this._linearNext();
  };
  Flowshot.prototype.prev = function () { this._stopAutoplay(); this.goTo(this.index - 1); };

  Flowshot.prototype._linearNext = function () {
    if (this.index >= this.steps.length - 1) this.goTo(0);
    else this.goTo(this.index + 1);
  };

  Flowshot.prototype._startAutoplay = function () {
    var self = this;
    var interval = this.opts.interval || this.demo.interval || 3000;
    this._timer = setInterval(function () {
      if (self.index >= self.steps.length - 1) { self._stopAutoplay(); return; }
      self.goTo(self.index + 1);
    }, interval);
  };
  Flowshot.prototype._stopAutoplay = function () { if (this._timer) { clearInterval(this._timer); this._timer = null; } };

  Flowshot.prototype._setupAnalytics = function () {
    var disabled = this.opts.analytics === false;
    if (this.opts.analytics === "false" || this.opts.analytics === "0" || this.opts.analytics === "off") disabled = true;
    this._analytics = {
      disabled: disabled,
      beacon: this.opts.analyticsUrl || (this.demo.analytics && this.demo.analytics.beacon) || "",
      dataLayer: this.opts.dataLayer === true || !!(this.demo.analytics && this.demo.analytics.dataLayer === true),
      attribution: this._captureAttribution(),
      furthestIndex: 0,
      complete: false,
      readyEmitted: false,
      viewedSteps: {},
      lastChapter: "",
      dropped: false
    };
    if (this._analytics.dataLayer && !window.dataLayer) window.dataLayer = [];
    if (disabled) return;
    var self = this;
    this._onVisibilityChange = function () {
      if (document.visibilityState === "hidden") self._sendDropoff();
    };
    this._onPageHide = function () { self._sendDropoff(); };
    if (document.addEventListener) document.addEventListener("visibilitychange", this._onVisibilityChange);
    if (window.addEventListener) window.addEventListener("pagehide", this._onPageHide);
  };

  Flowshot.prototype._trackStepView = function (index, step) {
    if (index > this._analytics.furthestIndex) this._analytics.furthestIndex = index;
    if (!this._analytics.viewedSteps[index]) {
      this._analytics.viewedSteps[index] = true;
      this._emitEvent("step_view", { index: index, id: this.stepIds[index] || step.id || "", type: stepType(step) });
    }
    var chapter = this._currentChapterId();
    if (chapter && chapter !== this._analytics.lastChapter) {
      this._analytics.lastChapter = chapter;
      this._emitEvent("chapter_view", { id: chapter });
    }
    if (index === this.steps.length - 1 && !this._analytics.complete) {
      this._analytics.complete = true;
      this._emitEvent("complete", {});
    }
  };

  Flowshot.prototype._emitEvent = function (type, payload) {
    if (this._analytics.disabled) return;
    if (type === "ready") {
      if (this._analytics.readyEmitted) return;
      this._analytics.readyEmitted = true;
    }
    var fullPayload = payload || {};
    fullPayload.title = this.demo.title || "";
    fullPayload.attribution = this._analytics.attribution || {};
    fullPayload.variables = { fromUrl: this._urlVariableNames.slice() };
    if (typeof this.opts.onEvent === "function") this.opts.onEvent(type, fullPayload);
    if (this._analytics.dataLayer && window.dataLayer && window.dataLayer.push) {
      window.dataLayer.push({ event: "flowshot_" + type, flowshot: { type: type, payload: fullPayload } });
    }
    if (this._analytics.beacon) this._sendBeacon(type, fullPayload);
  };

  Flowshot.prototype._captureAttribution = function () {
    var out = {};
    var search = (window.location && window.location.search) || "";
    var params = new URLSearchParams(search);
    ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"].forEach(function (key) {
      var value = params.get(key);
      if (value) out[key] = value;
    });
    if (document.referrer) out.referrer = document.referrer;
    return out;
  };

  Flowshot.prototype._sendBeacon = function (type, payload) {
    var body = JSON.stringify({ type: type, payload: payload });
    if (typeof navigator !== "undefined" && navigator.sendBeacon) {
      navigator.sendBeacon(this._analytics.beacon, body);
    } else if (window.fetch) {
      window.fetch(this._analytics.beacon, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: body,
        keepalive: true
      }).catch(function () {});
    }
  };

  Flowshot.prototype._sendDropoff = function () {
    if (this._analytics.dropped || this._analytics.complete) return;
    this._analytics.dropped = true;
    this._emitEvent("dropoff", { furthestIndex: this._analytics.furthestIndex });
  };

  Flowshot.prototype.destroy = function () {
    this._stopAutoplay();
    this._stopStepVideo();
    this._sendDropoff();
    if (this._captionResizeTimer && typeof clearTimeout === "function") clearTimeout(this._captionResizeTimer);
    this._captionResizeTimer = null;
    if (this._onViewportChange && window.removeEventListener) {
      window.removeEventListener("resize", this._onViewportChange);
      window.removeEventListener("orientationchange", this._onViewportChange);
    }
    if (this._onVisibilityChange && document.removeEventListener) document.removeEventListener("visibilitychange", this._onVisibilityChange);
    if (this._onPageHide && window.removeEventListener) window.removeEventListener("pagehide", this._onPageHide);
    this.container.textContent = "";
  };

  function autoInit() {
    var nodes = document.querySelectorAll("[data-flowshot]:not([data-fs-ready])");
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      node.setAttribute("data-fs-ready", "");
      var opts = {
        autoplay: node.hasAttribute("data-autoplay"),
        interval: parseInt(node.getAttribute("data-interval"), 10) || undefined,
        accent: node.getAttribute("data-accent") || undefined,
        preset: node.getAttribute("data-preset") || undefined,
        analytics: parseAnalyticsAttr(node.getAttribute("data-analytics")),
        analyticsUrl: node.getAttribute("data-analytics-url") || undefined,
        dataLayer: parseDataLayerAttr(node.getAttribute("data-datalayer")),
        deepLink: node.hasAttribute("data-deeplink") ? "flowshot" : undefined,
        persistProgress: node.hasAttribute("data-persist-progress")
      };
      new Flowshot(node, node.getAttribute("data-flowshot"), opts);
    }
  }

  function parseAnalyticsAttr(value) {
    if (value == null || value === "") return undefined;
    if (value === "false" || value === "0" || value === "off") return false;
    return true;
  }

  function parseDataLayerAttr(value) {
    if (value == null) return undefined;
    if (value === "false" || value === "0" || value === "off") return false;
    return true;
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", autoInit);
    else autoInit();
  }

  Flowshot.autoInit = autoInit;
  global.Flowshot = Flowshot;
  if (typeof module !== "undefined" && module.exports) module.exports = Flowshot;
})(typeof window !== "undefined" ? window : this);
