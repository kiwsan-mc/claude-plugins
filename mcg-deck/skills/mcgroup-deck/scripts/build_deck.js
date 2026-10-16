#!/usr/bin/env node
/**
 * build_deck.js — turn a content JSON into an MC Group .pptx.
 *
 * Usage:
 *   node build_deck.js content.json -o deck.pptx [--spec reference/templates.json]
 *
 * The content JSON shape is documented in templates.json under `content_contract`.
 * Missing content is reported and left out; nothing is invented.
 *
 * Layouts: one pptxgenjs layout per archetype frame is NOT used here — the source
 * deck has no custom master, so chrome (top band + header + footer) is drawn per
 * slide by archetypes.js, matching how the original file was built.
 */

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { BUILDERS, C } = require("./archetypes.js");

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const contentPath = process.argv[2];
if (!contentPath || contentPath.startsWith("-")) {
  console.error("usage: node build_deck.js content.json -o deck.pptx [--spec templates.json]");
  process.exit(1);
}
const outPath = arg("-o", "deck.pptx");

const REF_DIR = path.join(__dirname, "..", "reference");

/** Resolve the style spec: explicit --spec > content.style > filename hint > default. */
function resolveSpec(content) {
  const explicit = arg("--spec", null);
  if (explicit) return explicit;

  const styles = ["executive", "kpi-wall", "catalog", "roadmap", "dark"];
  // 1. explicit style field in content
  if (content.style) {
    const f = path.join(REF_DIR, `templates-${content.style}.json`);
    if (fs.existsSync(f)) return f;
    console.warn(`unknown content.style "${content.style}" — falling back`);
  }
  // 2. filename hint, e.g. demo-executive.json → templates-executive.json
  const base = path.basename(contentPath, ".json");
  for (const st of styles) {
    if (base.includes(st)) {
      const f = path.join(REF_DIR, `templates-${st}.json`);
      if (fs.existsSync(f)) return f;
    }
  }
  // 3. default house style
  return path.join(REF_DIR, "templates.json");
}

const content = JSON.parse(fs.readFileSync(contentPath, "utf8"));
const specPath = resolveSpec(content);
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
console.log(`style spec: ${path.basename(specPath)}`);

// deck-level defaults merged from the spec
const deck = Object.assign({}, spec.header_defaults, content);
deck.header_defaults = spec.header_defaults;

const pres = new PptxGenJS();
// LAYOUT_WIDE = 13.3 x 7.5 in, matching the source canvas
pres.layout = spec.canvas.pptxgenjs_layout || "LAYOUT_WIDE";
pres.title = deck.title || "";
pres.author = deck.brand || "MC Group";
pres.company = (deck.brand || "MC Group").replace(/&/g, "&amp;");

const ctx = { spec, deck };

const slides = content.slides || [];
if (!slides.length) {
  console.error("no slides in content");
  process.exit(1);
}

const warnings = [];

slides.forEach((s, i) => {
  const build = BUILDERS[s.archetype];
  if (!build) {
    warnings.push(`slide ${i + 1}: unknown archetype "${s.archetype}" — skipped`);
    return;
  }
  // dark archetypes set their own slide background
  const dark = s.archetype === "cover" || s.archetype === "closing"
    || s.archetype === "dark-cover" || s.dark === true;
  const slide = pres.addSlide();
  if (dark) slide.background = { color: spec.palette.navy };
  else slide.background = { color: spec.palette.white };

  try {
    build(slide, s, ctx);
  } catch (e) {
    warnings.push(`slide ${i + 1} (${s.archetype}): ${e.message}`);
    throw e;
  }
});

pres.writeFile({ fileName: outPath }).then((f) => {
  console.log(`wrote ${f}`);
  if (warnings.length) {
    console.log("warnings:");
    warnings.forEach((w) => console.log("  - " + w));
  }
}).catch((e) => {
  console.error("write failed:", e.message);
  process.exit(1);
});