/* Optional SVG lettering with independently tilted text and banded extrusion. */
(() => {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const rainbow = ["#fff000", "#ffca00", "#ff9c00", "#ff6500", "#ff2400", "#ed0066", "#e100d8", "#a000ff", "#6200ef", "#2519d8", "#009ee5", "#19c6cf"];
  const presets = {
    rainbow,
    "rainbow-inverted": [...rainbow].reverse(),
    "rainbow-muted": ["#dfcd72", "#d9b16a", "#ce9364", "#c77969", "#bc6d80", "#ae719c", "#9676ae", "#7d7db1", "#6587b2", "#5c9eb2", "#68b2b3", "#8bc4b5"],
  };
  const defaults = {
    tilt_angle: -10,
    shadow_angle: 90,
    shadow_colors_set: "rainbow",
    text_color: null,
    shadow_layers: null,
    shadow_thickness: 6,
    shadow_spacing: 0,
    font_size: 80,
    font_family: 'Impact, "Arial Black", Inter, sans-serif',
    font_weight: 900,
  };
  const states = new WeakMap();
  let nextId = 0;

  function node(name, attributes = {}) {
    const element = document.createElementNS(NS, name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    return element;
  }

  function optionsFor(options) {
    if (options === true) options = {};
    if (!options || typeof options !== "object" || Array.isArray(options)) {
      throw new TypeError("Stacked text options must be an object (or true for defaults).");
    }
    const settings = { ...defaults, ...options };
    for (const key of ["tilt_angle", "shadow_angle", "shadow_thickness", "shadow_spacing", "font_size", "font_weight"]) {
      if (typeof settings[key] !== "number" || !Number.isFinite(settings[key])) {
        throw new TypeError(`${key} must be a finite number.`);
      }
    }
    if (settings.font_size < 1 || settings.font_size > 512 || settings.shadow_thickness <= 0 || settings.shadow_thickness > 32 || settings.font_weight < 1 || settings.font_weight > 1000) {
      throw new RangeError("Use font_size 1–512, shadow_thickness > 0 and <= 32, and font_weight 1–1000.");
    }
    if (settings.shadow_spacing < 0 || settings.shadow_spacing > 32) {
      throw new RangeError("shadow_spacing must be between 0 and 32 SVG units.");
    }
    if (typeof settings.font_family !== "string" || !settings.font_family.trim()) {
      throw new TypeError("font_family must be a nonempty font-family string.");
    }
    const colors = Array.isArray(settings.shadow_colors_set)
      ? settings.shadow_colors_set.slice()
      : presets[settings.shadow_colors_set];
    if (!Array.isArray(colors) || !colors.length || colors.length > 64) {
      throw new TypeError("shadow_colors_set must be rainbow, rainbow-inverted, rainbow-muted, or an array of 1–64 colors.");
    }
    for (const color of colors) {
      if (typeof color !== "string" || !CSS.supports("color", color)) {
        throw new TypeError(`Invalid stacked text color: ${String(color)}`);
      }
    }
    let textColor = settings.text_color;
    const usesPaletteFace = textColor == null || (typeof textColor === "string" && !textColor.trim());
    if (usesPaletteFace) textColor = colors[0];
    else if (typeof textColor === "string") textColor = textColor.trim();
    else throw new TypeError("text_color must be a CSS color or empty to use the first palette color.");
    if (!CSS.supports("color", textColor)) {
      throw new TypeError(`Invalid text_color: ${textColor}`);
    }
    // A fallback face owns the first palette entry instead of sharing it with
    // the nearest shadow. Explicit text colors keep the full shadow palette.
    const shadowColors = usesPaletteFace ? colors.slice(1) : colors;
    const count = settings.shadow_layers === null ? shadowColors.length : settings.shadow_layers;
    if (!Number.isInteger(count) || count < 0 || count > shadowColors.length) {
      throw new RangeError(`shadow_layers must be an integer between 0 and ${shadowColors.length} for this colors set.`);
    }
    return { ...settings, text_color: textColor, colors: shadowColors.slice(0, count) };
  }

  async function render(element, options = {}) {
    if (!(element instanceof HTMLElement)) throw new TypeError("Supply an HTML text element.");
    const settings = optionsFor(options);
    let state = states.get(element);
    if (!state) {
      state = { text: element.textContent.trim(), revision: 0 };
      states.set(element, state);
    }
    const text = options.text === undefined ? state.text : options.text;
    if (typeof text !== "string" || !text.trim() || text.length > 512) {
      throw new TypeError("Text must contain 1–512 characters.");
    }
    const revision = ++state.revision;
    if (document.fonts) {
      await document.fonts.load(`${settings.font_weight} ${settings.font_size}px ${settings.font_family}`, text);
      await document.fonts.ready;
    }
    if (revision !== state.revision) return null;

    const id = `pixel-lab-stacked-text-${++nextId}`;
    const svg = node("svg", { xmlns: NS, "aria-hidden": "true", focusable: "false", class: "stacked-text__svg" });
    const defs = node("defs");
    const glyph = node("text", {
      id, x: 0, y: 0, "font-family": settings.font_family,
      "font-size": settings.font_size, "font-weight": settings.font_weight,
      "letter-spacing": 0, "text-anchor": "start", "xml:space": "preserve",
    });
    glyph.textContent = text;
    defs.append(glyph);
    svg.append(defs);
    // Measure in a connected, invisible SVG without disturbing the original title.
    const measurement = node("use", { href: `#${id}` });
    svg.append(measurement);
    svg.style.cssText = "position:fixed;visibility:hidden;pointer-events:none;left:0;top:0";
    document.body.append(svg);
    let box;
    try {
      box = measurement.getBBox();
    } finally {
      svg.remove();
      measurement.remove();
      svg.removeAttribute("style");
    }
    if (!box.width || !box.height) throw new Error("Could not measure stacked text glyphs.");
    const radians = (settings.tilt_angle % 360) * Math.PI / 180;
    const corners = [[box.x, box.y], [box.x + box.width, box.y], [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]]
      .map(([x, y]) => [x * Math.cos(radians) - y * Math.sin(radians), x * Math.sin(radians) + y * Math.cos(radians)]);
    const direction = (settings.shadow_angle % 360) * Math.PI / 180;
    const dx = Math.cos(direction);
    const dy = Math.sin(direction);
    const stride = settings.shadow_thickness + settings.shadow_spacing;
    const depth = settings.colors.length
      ? settings.colors.length * settings.shadow_thickness + (settings.colors.length - 1) * settings.shadow_spacing
      : 0;
    const pad = 2;
    const left = Math.min(...corners.map(([x]) => x)) + Math.min(0, dx * depth) - pad;
    const top = Math.min(...corners.map(([, y]) => y)) + Math.min(0, dy * depth) - pad;
    const width = Math.max(...corners.map(([x]) => x)) + Math.max(0, dx * depth) + pad - left;
    const height = Math.max(...corners.map(([, y]) => y)) + Math.max(0, dy * depth) + pad - top;
    svg.setAttribute("viewBox", `${left} ${top} ${width} ${height}`);
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

    const copyAt = distance => node("use", {
      href: `#${id}`,
      transform: `translate(${dx * distance} ${dy * distance}) rotate(${settings.tilt_angle % 360})`,
    });
    function sweep(target, start, end) {
      // Subpixel copies close unwanted gaps within each solid band.
      const steps = Math.ceil((end - start) / 0.5);
      for (let step = steps; step >= 1; step--) {
        target.append(copyAt(start + (end - start) * step / steps));
      }
    }

    // Keep full colored copies underneath: spacing reveals lower layers instead
    // of cutting transparent holes through the stack. Paint farthest first.
    for (let layer = settings.colors.length - 1; layer >= 0; layer--) {
      const band = node("g", { class: "stacked-text__band", fill: settings.colors[layer], "data-layer": layer });
      sweep(band, layer * stride, layer * stride + settings.shadow_thickness);
      svg.append(band);
    }
    svg.append(node("use", { class: "stacked-text__face", href: `#${id}`, fill: settings.text_color, transform: `rotate(${settings.tilt_angle % 360})` }));
    const label = document.createElement("span");
    label.className = "stacked-text__label";
    label.textContent = text;
    element.replaceChildren(label, svg);
    element.classList.add("stacked-text");
    state.text = text;
    return svg;
  }

  function init(root = document) {
    const elements = [...root.querySelectorAll("[data-stacked-text]")];
    if (root.matches?.("[data-stacked-text]")) elements.unshift(root);
    return Promise.all(elements.map(async element => {
      try {
        return await render(element, JSON.parse(element.dataset.stackedText || "{}"));
      } catch (error) {
        // Invalid configuration or missing font support keeps the readable plain text.
        console.warn("Pixel Lab stacked text:", error);
        return null;
      }
    }));
  }

  window.PixelLabStackedText = Object.freeze({ render, init });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init());
  else init();
})();
