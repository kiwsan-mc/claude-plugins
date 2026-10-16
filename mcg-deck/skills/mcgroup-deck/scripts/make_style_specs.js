#!/usr/bin/env node
/**
 * make_style_specs.js — generate the 5 style spec files from the base spec.
 *
 * Each style keeps the SAME canvas, palette, fonts and grid as templates.json,
 * and adds its own archetype coordinate block(s). Run once; committed output is
 * reference/templates-<style>.json.
 */
const fs = require("fs");
const path = require("path");

const REF = path.join(__dirname, "..", "reference");
const base = JSON.parse(fs.readFileSync(path.join(REF, "templates.json"), "utf8"));

// shared blocks copied verbatim into every style
const shared = {
  _meta_base: base._meta,
  canvas: base.canvas,
  palette: base.palette,
  fonts: base.fonts,
  grid: base.grid,
  header_defaults: base.header_defaults,
  title: base.archetypes.title,
  section: base.archetypes.section,
  closing: base.archetypes.closing,
  image: base.archetypes.image,
  "two-col": base.archetypes["two-col"],
  bullets: base.archetypes.bullets,
  table: base.archetypes.table,
  timeline: base.archetypes.timeline,
  "kpi-bar": base.archetypes["kpi-bar"],
  "stat-row": base.archetypes["stat-row"],
  "card-panel": base.archetypes["card-panel"],
  chart: base.archetypes.chart,
};

function write(name, style, meta, archetypes, contract_note) {
  const spec = {
    _meta: {
      name: meta.name,
      derived_from: base._meta.derived_from,
      canvas: base._meta.canvas,
      units: "inches",
      style,
      how_to_use: `build_deck.js picks this spec when content.style === "${style}" or the content filename contains "${style}".`,
      note_layers: meta.note_layers,
    },
    canvas: shared.canvas,
    palette: shared.palette,
    fonts: shared.fonts,
    grid: shared.grid,
    header_defaults: base.header_defaults,
    archetypes: { ...shared, ...archetypes },
    content_contract: {
      _note: contract_note,
      deck: base.content_contract.deck,
    },
  };
  const out = path.join(REF, `templates-${style}.json`);
  fs.writeFileSync(out, JSON.stringify(spec, null, 2), "utf8");
  console.log(`wrote ${path.basename(out)}`);
}

/* ---------- 1. Executive Brief ---------- */
write("executive", "executive",
  { name: "MC Group — Executive Brief",
    note_layers: "white content slides; optional dark (navy) slides via slide.dark=true; thin navy hairline instead of the thick band." },
  {
    "exec-brief": {
      _note: "text-first slide: eyebrow + title + body + optional inline metric row",
      x: 0.6, w: 12.1, rule_w: 12.1,
      eyebrow_sz: 10, title_y: 0.95, title_sz: 28,
      body_y: 1.8, body_w: 9.6, body_h: 3.0, body_sz: 11,
      metric_y: 5.15
    },
    cover: base.archetypes.cover,
    "kpi-bar": base.archetypes["kpi-bar"],
  },
  "supports archetypes: exec-brief (primary), cover, closing, section, kpi-bar, table, two-col, bullets, chart"
);

/* ---------- 2. KPI Wall ---------- */
write("kpi-wall", "kpi-wall",
  { name: "MC Group — Data / KPI Wall",
    note_layers: "white deck; 6 KPI cards (3x2) with a chart band beneath." },
  {
    "kpi-wall": {
      _note: "6-card grid (3 cols x 2 rows) + optional chart band",
      x: 0.5, y: 1.7, w: 12.3, gap: 0.18, cell_h: 1.35, value_sz: 30
    },
    chart: Object.assign({}, base.archetypes.chart, { embedded_y: 4.95, embedded_h: 1.85 }),
    "kpi-bar": base.archetypes["kpi-bar"],
    cover: base.archetypes.cover,
  },
  "supports archetypes: kpi-wall (primary), cover, closing, section, chart, table"
);

/* ---------- 3. Product Catalogue ---------- */
write("catalog", "catalog",
  { name: "MC Group — Product Catalogue",
    note_layers: "white deck; 3x2 product card grid with image slot and navy price band." },
  {
    catalog: {
      _note: "product card grid: 3 cols x 2 rows, image slot + name + sku + price band",
      x: 0.5, y: 1.7, w: 12.3, gap: 0.2, card_h: 2.35, img_h: 1.4
    },
    cover: base.archetypes.cover,
    "kpi-bar": base.archetypes["kpi-bar"],
  },
  "supports archetypes: catalog (primary), cover, closing, section, two-col"
);

/* ---------- 4. Roadmap Horizontal ---------- */
write("roadmap", "roadmap",
  { name: "MC Group — Timeline / Roadmap (horizontal)",
    note_layers: "white deck; horizontal time band with milestone markers and cards above." },
  {
    "roadmap-h": {
      _note: "horizontal band: milestones spaced evenly across a navy bar, cards above, captions below",
      x: 0.5, w: 12.3, band_y: 4.15, card_y: 1.9, card_h: 1.9
    },
    cover: base.archetypes.cover,
    "kpi-bar": base.archetypes["kpi-bar"],
  },
  "supports archetypes: roadmap-h (primary), cover, closing, section, bullets"
);

/* ---------- 5. Dark Premium ---------- */
write("dark", "dark",
  { name: "MC Group — Dark Premium",
    note_layers: "navy cover/section/closing + white content slides. Use archetype dark-cover; add slide.dark=true for other dark slides." },
  {
    "dark-cover": {
      _note: "navy full-bleed cover with larger type and gold rule",
      bg: "navy", footer_style: "light_on_dark"
    },
    cover: base.archetypes.cover,
    "kpi-bar": base.archetypes["kpi-bar"],
  },
  "supports archetypes: dark-cover (primary), cover, closing, section, kpi-bar, table, chart, bullets"
);

console.log("done");