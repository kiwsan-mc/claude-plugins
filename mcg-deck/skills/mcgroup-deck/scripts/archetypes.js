/**
 * archetypes.js — one builder per MC Group deck slide archetype.
 *
 * Each builder receives:
 *   (slide, s, ctx)
 *     slide — a pptxgenjs slide (pres.addSlide())
 *     s     — the slide's content object from the deck JSON
 *     ctx   — { spec, deck, helpers }
 *
 * Builders only ADD shapes. Layout/theme/section wiring lives in build_deck.js.
 * Coordinates are inches. Colors are hex WITHOUT '#'.
 *
 * Footguns honoured here (from the pptx skill):
 *   - every addText with no placeholder gets isTextBox: true
 *   - fresh option object per call (pptxgenjs mutates in place)
 *   - hex is 6 digits, no '#', no alpha baked in
 *   - rectRadius only on ROUNDED_RECTANGLE
 */

const PAL_KEYS = {
  navy: "navy", navy_band: "navy_band", blue: "blue", gold: "gold",
  slate: "slate", slate2: "slate2", ink: "ink",
  bg_soft: "bg_soft", bg_soft2: "bg_soft2", line: "line",
  line_footer: "line_footer", gold_tint: "gold_tint", white: "white", red: "red",
};

/** Resolve a palette name (or pass through a raw 6-hex string). */
function C(ctx, key) {
  const p = ctx.spec.palette[key];
  return p || key;
}

/* ---------- shared chrome ---------- */

function addTopBand(slide, ctx) {
  const b = ctx.spec.grid.top_band;
  slide.addShape("rect", {
    x: b.x, y: b.y, w: b.w, h: b.h,
    fill: { color: C(ctx, b.fill) },
    line: { color: C(ctx, b.fill), width: 0 },
  });
}

function addFooter(slide, ctx, style) {
  const g = ctx.spec.grid;
  const hr = ctx.deck.header_defaults;
  const dark = style === "light_on_dark";
  const textColor = dark ? C(ctx, "white") : C(ctx, "slate2");
  const ruleColor = dark ? C(ctx, "navy_band") : C(ctx, "line_footer");

  slide.addShape("rect", {
    x: g.footer_rule.x, y: g.footer_rule.y, w: g.footer_rule.w, h: g.footer_rule.h,
    fill: { color: ruleColor }, line: { color: ruleColor, width: 0 },
  });
  slide.addText(ctx.deck.footer_left || hr.footer_left, {
    x: g.footer_left.x, y: g.footer_left.y, w: g.footer_left.w, h: g.footer_left.h,
    fontSize: g.footer_left.sz, color: textColor, fontFace: ctx.spec.fonts.body,
    margin: 0, isTextBox: true, valign: "middle",
  });
  slide.addText(ctx.deck.footer_right || hr.footer_right, {
    x: g.footer_right.x, y: g.footer_right.y, w: g.footer_right.w, h: g.footer_right.h,
    fontSize: g.footer_right.sz, color: textColor, fontFace: ctx.spec.fonts.body,
    align: "right", margin: 0, isTextBox: true, valign: "middle",
  });
}

function addBrandHeader(slide, ctx, style) {
  const g = ctx.spec.grid;
  const hr = ctx.deck.header_defaults;
  const gold = C(ctx, "gold");
  const navy = C(ctx, "navy");
  const light = style === "light_on_dark";

  slide.addText(hr.brand, {
    x: g.header_left.x, y: g.header_left.y, w: g.header_left.w, h: g.header_left.h,
    fontSize: g.header_left.sz, bold: true, color: light ? C(ctx, "white") : navy,
    fontFace: ctx.spec.fonts.body, charSpacing: 2, margin: 0, isTextBox: true, valign: "middle",
  });
  slide.addText(ctx.deck.right_label || hr.right_label, {
    x: g.header_right.x, y: g.header_right.y, w: g.header_right.w, h: g.header_right.h,
    fontSize: g.header_right.sz, bold: true, color: light ? C(ctx, "white") : navy,
    fontFace: ctx.spec.fonts.body, charSpacing: 1, align: "right",
    margin: 0, isTextBox: true, valign: "middle",
  });
  // small gold tick under brand, present on light slides only
  if (!light) {
    slide.addShape("rect", {
      x: g.header_left.x, y: g.header_left.y + 0.28, w: 0.3, h: 0.02,
      fill: { color: gold }, line: { color: gold, width: 0 },
    });
  }
}

function addTitleBlock(slide, s, ctx) {
  const t = ctx.spec.archetypes.title.elements;
  const navy = C(ctx, "navy");
  for (const el of t) {
    if (el.role === "rule_under") {
      slide.addShape("rect", {
        x: el.x, y: el.y, w: el.w, h: el.h,
        fill: { color: C(ctx, el.fill) }, line: { color: C(ctx, el.fill), width: 0 },
      });
      continue;
    }
    const value = el.role === "title" ? s.title
                : el.role === "kicker" ? s.kicker
                : s.subtitle;
    if (!value) continue;
    slide.addText(value, {
      x: el.x, y: el.y, w: el.w, h: el.h,
      fontSize: el.sz, bold: !!el.bold, color: C(ctx, el.color),
      fontFace: ctx.spec.fonts.heading, charSpacing: el.charSpacing || 0,
      margin: 0, isTextBox: true, valign: "top",
    });
  }
}

/* ---------- archetypes ---------- */

function cover(slide, s, ctx) {
  addTopBand(slide, ctx);
  const a = ctx.spec.archetypes.cover;
  const r = a.accent_rule;
  slide.addShape("rect", {
    x: r.x, y: r.y, w: r.w, h: r.h,
    fill: { color: C(ctx, r.fill) }, line: { color: C(ctx, r.fill), width: 0 },
  });
  for (const el of a.elements) {
    if (el.role === "rule_under") {
      slide.addShape("rect", {
        x: el.x, y: el.y, w: el.w, h: el.h,
        fill: { color: C(ctx, el.fill) }, line: { color: C(ctx, el.fill), width: 0 },
      });
      continue;
    }
    const value = s[el.role];
    if (!value) continue;
    slide.addText(value, {
      x: el.x, y: el.y, w: el.w, h: el.h,
      fontSize: el.sz, bold: !!el.bold, color: C(ctx, el.color),
      fontFace: ctx.spec.fonts.heading, charSpacing: el.charSpacing || 0,
      margin: 0, isTextBox: true, valign: "middle",
    });
  }
  addBrandHeader(slide, ctx, "light_on_dark");
  addFooter(slide, ctx, "light_on_dark");
}

function closing(slide, s, ctx) {
  addTopBand(slide, ctx);
  const a = ctx.spec.archetypes.closing;
  const r = a.accent_rule;
  slide.addShape("rect", {
    x: r.x, y: r.y, w: r.w, h: r.h,
    fill: { color: C(ctx, r.fill) }, line: { color: C(ctx, r.fill), width: 0 },
  });
  for (const el of a.elements) {
    if (el.role === "rule_under") {
      slide.addShape("rect", {
        x: el.x, y: el.y, w: el.w, h: el.h,
        fill: { color: C(ctx, el.fill) }, line: { color: C(ctx, el.fill), width: 0 },
      });
      continue;
    }
    const value = s[el.role] || el.default_text;
    if (!value) continue;
    slide.addText(value, {
      x: el.x, y: el.y, w: el.w, h: el.h,
      fontSize: el.sz, bold: !!el.bold, color: C(ctx, el.color),
      fontFace: ctx.spec.fonts.heading, charSpacing: el.charSpacing || 0,
      margin: 0, isTextBox: true, valign: "middle",
    });
  }
  addBrandHeader(slide, ctx, "light_on_dark");
  addFooter(slide, ctx, "light_on_dark");
}

function section(slide, s, ctx) {
  addTopBand(slide, ctx);
  const a = ctx.spec.archetypes.section;
  const r = a.accent_rule;
  slide.addShape("rect", {
    x: r.x, y: r.y, w: r.w, h: r.h,
    fill: { color: C(ctx, r.fill) }, line: { color: C(ctx, r.fill), width: 0 },
  });
  for (const el of a.elements) {
    if (el.role === "rule_under") {
      slide.addShape("rect", {
        x: el.x, y: el.y, w: el.w, h: el.h,
        fill: { color: C(ctx, el.fill) }, line: { color: C(ctx, el.fill), width: 0 },
      });
      continue;
    }
    const value = el.role === "eyebrow" ? s.eyebrow
                : el.role === "title" ? s.title
                : s.subtitle;
    if (!value) continue;
    slide.addText(value, {
      x: el.x, y: el.y, w: el.w, h: el.h,
      fontSize: el.sz, bold: !!el.bold, color: C(ctx, el.color),
      fontFace: ctx.spec.fonts.heading, charSpacing: el.charSpacing || 0,
      margin: 0, isTextBox: true, valign: "middle",
    });
  }
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");
}

function kpiBar(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const card = ctx.spec.archetypes["kpi-bar"].card;
  const kpis = (s.kpis || []).slice(0, 4);
  kpis.forEach((k, i) => {
    const x = card.x_start + i * (card.w + card.gap);
    slide.addShape("rect", {
      x, y: card.y, w: card.w, h: card.h,
      fill: { color: C(ctx, card.fill) },
      line: { color: C(ctx, "line"), width: 0.5 },
    });
    const barColor = C(ctx, k.accent || card.accent_bar.fills[i % 2]);
    slide.addShape("rect", {
      x, y: card.y, w: card.accent_bar.w, h: card.h,
      fill: { color: barColor }, line: { color: barColor, width: 0 },
    });
    slide.addText(String(k.value), {
      x: x + card.value.dx, y: card.y + card.value.dy, w: card.value.w, h: card.value.h,
      fontSize: card.value.sz, bold: true, color: C(ctx, k.value_color || card.value_color_alternates[i % 2]),
      fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
    });
    slide.addText(String(k.label || ""), {
      x: x + card.label.dx, y: card.y + card.label.dy, w: card.label.w, h: card.label.h,
      fontSize: card.label.sz, bold: true, color: C(ctx, card.label.color),
      fontFace: ctx.spec.fonts.body, charSpacing: 1, margin: 0, isTextBox: true, valign: "middle",
    });
  });
}

function timeline(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes.timeline;
  const p = a.plate;
  slide.addShape("rect", {
    x: p.x, y: p.y, w: p.w, h: p.h,
    fill: { color: C(ctx, p.fill) }, line: { color: C(ctx, "line"), width: 0 },
  });
  slide.addText(s.head || s.kicker || "", {
    x: a.head.x, y: a.head.y, w: a.head.w, h: a.head.h,
    fontSize: a.head.sz, bold: true, color: C(ctx, a.head.color),
    fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true,
  });
  if (s.range) {
    slide.addText(s.range, {
      x: a.range.x, y: a.range.y, w: a.range.w, h: a.range.h,
      fontSize: a.range.sz, bold: true, color: C(ctx, a.range.color),
      align: "right", fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true,
    });
  }

  const items = s.items || [];
  const rows = a.rows;
  const spineTop = rows.y_start - 0.04;
  const spineBottom = rows.y_start + (items.length - 1) * rows.row_pitch + 0.14;
  slide.addShape("rect", {
    x: a.spine.x, y: spineTop, w: 0.02, h: Math.max(0.2, spineBottom - spineTop),
    fill: { color: C(ctx, a.spine.fill) }, line: { color: C(ctx, a.spine.fill), width: 0 },
  });

  items.forEach((it, i) => {
    const y = rows.y_start + i * rows.row_pitch;
    const accent = C(ctx, it.accent || a.dot.inner_fills[i % 2]);
    // dot: white outer + colored inner
    slide.addShape("ellipse", {
      x: a.spine.x - 0.1, y: y, w: a.dot.outer, h: a.dot.outer,
      fill: { color: C(ctx, a.dot.outer_fill) }, line: { color: accent, width: 1 },
    });
    slide.addShape("ellipse", {
      x: a.spine.x - 0.04, y: y + 0.06, w: a.dot.inner, h: a.dot.inner,
      fill: { color: accent }, line: { color: accent, width: 0 },
    });
    slide.addText(it.date || "", {
      x: rows.date.x, y: y - 0.03, w: rows.date.w, h: rows.date.h,
      fontSize: rows.date.sz, bold: true,
      color: C(ctx, it.accent ? it.accent : (i % 2 ? rows.date.color_alt : rows.date.color)),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
    });
    slide.addText(it.title || "", {
      x: rows.title.x, y: y - 0.04, w: rows.title.w, h: rows.title.h,
      fontSize: rows.title.sz, color: C(ctx, rows.title.color),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
    });
    if (it.sub) {
      slide.addText(it.sub, {
        x: rows.sub.x, y: y + 0.19, w: rows.sub.w, h: rows.sub.h,
        fontSize: rows.sub.sz, color: C(ctx, rows.sub.color),
        fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
      });
    }
  });
}

/** Optional rounded stat pills at the top of a content slide. */
function addStatRow(slide, stats, ctx) {
  const a = ctx.spec.archetypes["stat-row"];
  (stats || []).slice(0, 3).forEach((st, i) => {
    const c = a.cells[i];
    if (!c) return;
    slide.addShape("roundRect", {
      x: c.x, y: a.row.y, w: c.w, h: a.row.h, rectRadius: a.row.radius,
      fill: { color: C(ctx, c.fill) }, line: { color: C(ctx, "line"), width: 0 },
    });
    slide.addText(String(st.label || ""), {
      x: c.x + a.label.dx, y: a.row.y + a.label.dy, w: c.w - 0.3, h: a.label.sz / 72 + 0.06,
      fontSize: a.label.sz, bold: true, color: C(ctx, a.label.color),
      fontFace: ctx.spec.fonts.body, charSpacing: 1, margin: 0, isTextBox: true,
    });
    slide.addText(String(st.value || ""), {
      x: c.x + a.value.dx, y: a.row.y + a.value.dy, w: c.w - 0.3, h: 0.3,
      fontSize: a.value.sz, bold: true, color: C(ctx, c.value_color),
      fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
    });
  });
}

/**
 * Zebra table. `blocks` = [{ head, columns: [...], rows: [[...]], total_row: idx }]
 * Up to 2 side-by-side blocks, or 1 full-width block.
 *
 * Column geometry is derived PER BLOCK from that block's own column count, so a
 * 3-column block and a 2-column block can sit side by side without overflow.
 *   block left  x=0.50  w=6.10
 *   block right x=6.82  w=5.99
 *   label column = 44% of block width; remaining columns split the rest evenly.
 */
function table(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");
  if (s.stats && s.stats.length) addStatRow(slide, s.stats, ctx);

  const a = ctx.spec.archetypes.table;
  const blocks = (s.blocks || []).slice(0, 2);
  const yStart = 2.58;
  const GAP = 0.12;

  // block frames
  const frames = blocks.length === 2
    ? [{ x: a.cols_2.x[0], w: a.cols_2.w[0] }, { x: a.cols_2.x[1], w: a.cols_2.w[1] }]
    : [{ x: a.cols_2.x[0], w: a.cols_2.x[1] + a.cols_2.w[1] - a.cols_2.x[0] }];

  blocks.forEach((blk, bi) => {
    const fr = frames[bi];
    const cols = (blk.columns || []).slice();
    if (!cols.length) return;

    // label column 44%, value columns split the remainder
    const labelW = cols.length > 1 ? fr.w * 0.44 : fr.w;
    const nVal = cols.length - 1;
    const valW = nVal > 0 ? (fr.w - labelW - GAP * nVal) / nVal : 0;

    const colX = [fr.x];
    for (let c = 1; c < cols.length; c++) colX.push(colX[c - 1] + (c === 1 ? labelW : valW) + GAP);
    const colW = [labelW, ...Array(nVal).fill(valW)];

    // block head
    slide.addText(blk.head || "", {
      x: fr.x, y: yStart, w: fr.w, h: a.block_head.sz / 72 + 0.12,
      fontSize: a.block_head.sz, bold: true, color: C(ctx, a.block_head.color),
      fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true,
    });

    let y = yStart + 0.30;

    // header row (navy)
    slide.addShape("rect", {
      x: fr.x, y, w: fr.w, h: a.row.h_wide,
      fill: { color: C(ctx, "navy") }, line: { color: C(ctx, "navy"), width: 0 },
    });
    cols.forEach((cname, ci) => {
      slide.addText(cname, {
        x: colX[ci] + a.row.label.dx, y, w: colW[ci] - a.row.label.dx, h: a.row.h_wide,
        fontSize: a.row.label.sz, bold: true, color: C(ctx, "white"),
        fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
      });
    });
    y += a.row.h_wide;

    // data rows (zebra)
    (blk.rows || []).forEach((row, ri) => {
      const isTotal = blk.total_row === ri;
      const zebraKey = isTotal ? a.row.total_fill : a.row.zebra[ri % 2];
      slide.addShape("rect", {
        x: fr.x, y, w: fr.w, h: a.row.h,
        fill: { color: C(ctx, zebraKey) }, line: { color: C(ctx, "line"), width: 0 },
      });
      for (let ci = 0; ci < cols.length; ci++) {
        const v = row[ci];
        const isLabel = ci === 0;
        const warn = !isLabel && typeof v === "string" && v.trim().startsWith("-");
        slide.addText(String(v ?? "—"), {
          x: colX[ci] + a.row.label.dx, y, w: colW[ci] - a.row.label.dx, h: a.row.h,
          fontSize: isLabel ? a.row.label.sz : a.row.value.sz,
          bold: isLabel,
          color: isTotal ? (isLabel ? C(ctx, a.row.total_label_color) : C(ctx, a.row.total_value_color))
               : warn ? C(ctx, a.row.warn_color)
               : isLabel ? C(ctx, a.row.label.color) : C(ctx, a.row.value.color),
          fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
        });
      }
      y += a.row.h;
    });
  });
}

function twoCol(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes["two-col"];
  const cols = [s.left || {}, s.right || {}];
  cols.forEach((col, i) => {
    const x = a.cols_2.x[i];
    const w = a.cols_2.w[i];
    if (col.head) {
      slide.addText(col.head, {
        x, y: 1.9, w, h: 0.3, fontSize: a.head.sz, bold: true,
        color: C(ctx, a.head.color), fontFace: ctx.spec.fonts.heading,
        margin: 0, isTextBox: true,
      });
    }
    if (col.body) {
      slide.addText(col.body, {
        x, y: 2.3, w, h: 4.3, fontSize: a.body.sz, color: C(ctx, a.body.color),
        fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "top",
        lineSpacingMultiple: 1.2,
      });
    }
  });
}

function bullets(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes.bullets;
  const items = s.items || [];
  if (!items.length) return;
  const rowH = Math.min(0.9, 4.3 / items.length);
  items.forEach((it, i) => {
    const y = 2.2 + i * rowH;
    slide.addShape("rect", {
      x: 0.5, y: y + 0.14, w: 0.09, h: 0.09,
      fill: { color: C(ctx, i % 2 ? "gold" : "blue") },
      line: { color: C(ctx, i % 2 ? "gold" : "blue"), width: 0 },
    });
    slide.addText(it, {
      x: 0.78, y, w: 12.0, h: rowH,
      fontSize: a.item.sz, color: C(ctx, a.item.color),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "middle",
    });
  });
}

function chart(slide, s, ctx) {
  // standalone chart slide adds its own chrome; embedded (frame already drawn) skips it
  if (!s._embedded) {
    addTopBand(slide, ctx);
    addTitleBlock(slide, s, ctx);
    addBrandHeader(slide, ctx, "dark_on_light");
    addFooter(slide, ctx, "dark_on_light");
  }

  const a = ctx.spec.archetypes.chart;
  const ch = s.chart || {};
  const data = (ch.series || []).map((ser, i) => ({
    name: ser.name,
    labels: ch.categories || [],
    values: ser.values || [],
  }));
  // single series: ONE color. multiple series: cycle the palette.
  const colors = data.length > 1
    ? a.series_colors.map((k) => C(ctx, k)).slice(0, Math.max(1, data.length))
    : [C(ctx, a.series_colors[0])];

  slide.addChart(ch.type || "bar", data, {
    x: a.plot_x, y: s._embedded ? (a.embedded_y || 4.9) : a.plot_y,
    w: a.plot_w, h: s._embedded ? (a.embedded_h || 2.0) : a.plot_h,
    showTitle: !!ch.title, title: ch.title || "",
    showValue: true,
    chartColors: colors,
    catAxisLabelColor: C(ctx, a.axis_label_color),
    valAxisLabelColor: C(ctx, a.axis_label_color),
    catAxisLabelFontFace: ctx.spec.fonts.chart,
    valAxisLabelFontFace: ctx.spec.fonts.chart,
    valGridLine: { color: C(ctx, a.gridline_color), size: 0.5 },
    catGridLine: { style: "none" },
    showLegend: data.length > 1,
    singleSeriesOverlay: data.length === 1,
    legendPos: "b",
    barDir: ch.barDir || "col",
  });
}

function image(slide, s, ctx) {
  const a = ctx.spec.archetypes.image;
  if (!s.path) return;
  slide.addImage({ path: s.path, x: a.x, y: a.y, w: a.w, h: a.h });
  if (s.caption) {
    slide.addText(s.caption, {
      x: a.caption_x, y: a.caption_y, w: 8, h: 0.16,
      fontSize: a.caption_sz, color: C(ctx, a.caption_color),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true,
    });
  }
}

/* ================= style-specific builders ================= */

/** Executive Brief — light, text-heavy, hairline rules, one idea per slide. */
function execBrief(slide, s, ctx) {
  const a = ctx.spec.archetypes["exec-brief"];
  const light = s.dark === true;
  slide.background = { color: light ? C(ctx, "navy") : C(ctx, "white") };
  const fg = light ? C(ctx, "white") : C(ctx, "navy");
  const sub = light ? C(ctx, "slate2") : C(ctx, "slate2");

  // thin navy hairline top instead of the thick band
  slide.addShape("rect", {
    x: 0, y: 0.42, w: a.rule_w, h: 0.02,
    fill: { color: C(ctx, "navy") }, line: { color: C(ctx, "navy"), width: 0 },
  });
  if (s.eyebrow) slide.addText(s.eyebrow, {
    x: a.x, y: 0.6, w: a.w, h: 0.24, fontSize: a.eyebrow_sz, bold: true,
    color: C(ctx, "blue"), fontFace: ctx.spec.fonts.body, charSpacing: 2,
    margin: 0, isTextBox: true,
  });
  if (s.title) slide.addText(s.title, {
    x: a.x, y: a.title_y, w: a.w, h: 0.7, fontSize: a.title_sz, bold: true,
    color: fg, fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
  });
  if (s.body) slide.addText(s.body, {
    x: a.x, y: a.body_y, w: a.body_w, h: a.body_h, fontSize: a.body_sz,
    color: light ? C(ctx, "white") : C(ctx, "ink"), fontFace: ctx.spec.fonts.body,
    margin: 0, isTextBox: true, valign: "top", lineSpacingMultiple: 1.25,
  });
  if (s.kpis && s.kpis.length) {
    // inline metric row beneath the body
    s.kpis.slice(0, 4).forEach((k, i) => {
      const cw = 2.9, gap = 0.35, x = a.x + i * (cw + gap), y = 5.15;
      slide.addText(String(k.value), {
        x, y, w: cw, h: 0.5, fontSize: 26, bold: true, color: C(ctx, "navy"),
        fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true,
      });
      slide.addText(String(k.label), {
        x, y: y + 0.52, w: cw, h: 0.2, fontSize: 9, bold: true, color: sub,
        fontFace: ctx.spec.fonts.body, charSpacing: 1, margin: 0, isTextBox: true,
      });
      if (i < s.kpis.length - 1) slide.addShape("rect", {
        x: x + cw + gap / 2 - 0.01, y, w: 0.01, h: 0.75,
        fill: { color: C(ctx, "line") }, line: { color: C(ctx, "line"), width: 0 },
      });
    });
  }
  addFooter(slide, ctx, light ? "light_on_dark" : "dark_on_light");
}

/** KPI Wall — 6-card grid (2 rows x 3) with a chart band beneath. */
function kpiWall(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes["kpi-wall"];
  const items = (s.kpis || []).slice(0, 6);
  const cols = 3, rows = 2, gap = a.gap;
  const cw = (a.w - gap * (cols - 1)) / cols;
  const ch = a.cell_h;

  items.forEach((k, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = a.x + c * (cw + gap), y = a.y + r * (ch + gap);
    slide.addShape("rect", {
      x, y, w: cw, h: ch,
      fill: { color: C(ctx, i % 2 ? "bg_soft" : "white") },
      line: { color: C(ctx, "line"), width: 0.5 },
    });
    slide.addShape("rect", {
      x, y, w: 0.07, h: ch,
      fill: { color: C(ctx, i % 2 ? "gold" : "blue") },
      line: { color: C(ctx, i % 2 ? "gold" : "blue"), width: 0 },
    });
    slide.addText(String(k.value), {
      x: x + 0.22, y: y + 0.10, w: cw - 0.4, h: 0.5,
      fontSize: a.value_sz, bold: true, color: C(ctx, i % 2 ? "gold" : "navy"),
      fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
    });
    slide.addText(String(k.label), {
      x: x + 0.23, y: y + ch - 0.32, w: cw - 0.4, h: 0.2,
      fontSize: 9, bold: true, color: C(ctx, "slate"),
      fontFace: ctx.spec.fonts.body, charSpacing: 1, margin: 0, isTextBox: true,
    });
  });
  if (s.chart && (s.chart.series || []).length) {
    chart(slide, Object.assign({}, s, { _embedded: true }), ctx);
  }
}

/** Product Catalogue — 3x2 card grid with image slot + name + price band. */
function catalog(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes.catalog;
  const items = (s.items || []).slice(0, 6);
  const cols = 3, gap = a.gap;
  const cw = (a.w - gap * (cols - 1)) / cols;

  items.forEach((it, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const x = a.x + c * (cw + gap), y = a.y + r * (a.card_h + gap);
    slide.addShape("rect", {
      x, y, w: cw, h: a.card_h,
      fill: { color: C(ctx, "white") }, line: { color: C(ctx, "line"), width: 0.75 },
    });
    // image slot
    if (it.path) {
      slide.addImage({ path: it.path, x: x + 0.1, y: y + 0.1, w: cw - 0.2, h: a.img_h });
    } else {
      slide.addShape("rect", {
        x: x + 0.1, y: y + 0.1, w: cw - 0.2, h: a.img_h,
        fill: { color: C(ctx, "bg_soft") }, line: { color: C(ctx, "line"), width: 0.5 },
      });
      slide.addText(it.sku || "no image", {
        x: x + 0.1, y: y + 0.1, w: cw - 0.2, h: a.img_h,
        fontSize: 8, color: C(ctx, "slate"), align: "center", valign: "middle",
        fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true,
      });
    }
    slide.addText(it.name || "", {
      x: x + 0.14, y: y + a.img_h + 0.14, w: cw - 0.28, h: 0.32,
      fontSize: 10, bold: true, color: C(ctx, "navy"),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "top",
    });
    if (it.sku) slide.addText(it.sku, {
      x: x + 0.14, y: y + a.img_h + 0.46, w: cw - 0.28, h: 0.14,
      fontSize: 7.5, color: C(ctx, "slate"), fontFace: ctx.spec.fonts.body,
      margin: 0, isTextBox: true,
    });
    // price band
    slide.addShape("rect", {
      x, y: y + a.card_h - 0.34, w: cw, h: 0.34,
      fill: { color: C(ctx, "navy") }, line: { color: C(ctx, "navy"), width: 0 },
    });
    slide.addText(String(it.price ?? "—"), {
      x: x + 0.14, y: y + a.card_h - 0.34, w: cw - 0.28, h: 0.34,
      fontSize: 11, bold: true, color: C(ctx, "gold"),
      fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
    });
  });
}

/** Roadmap Horizontal — horizontal time band with milestones. */
function roadmapH(slide, s, ctx) {
  addTopBand(slide, ctx);
  addTitleBlock(slide, s, ctx);
  addBrandHeader(slide, ctx, "dark_on_light");
  addFooter(slide, ctx, "dark_on_light");

  const a = ctx.spec.archetypes["roadmap-h"];
  const items = s.items || [];
  const n = Math.max(1, items.length);
  const bandY = a.band_y;
  const segW = a.w / n;

  // horizontal band
  slide.addShape("rect", {
    x: a.x, y: bandY, w: a.w, h: 0.16,
    fill: { color: C(ctx, "navy") }, line: { color: C(ctx, "navy"), width: 0 },
  });
  items.forEach((it, i) => {
    const cx = a.x + i * segW + segW / 2;
    const accent = i % 2 ? "gold" : "blue";
    // milestone marker
    slide.addShape("rect", {
      x: cx - 0.13, y: bandY - 0.11, w: 0.26, h: 0.38,
      fill: { color: C(ctx, accent) }, line: { color: C(ctx, accent), width: 0 },
    });
    // card above
    const cardW = segW - 0.2;
    slide.addShape("rect", {
      x: a.x + i * segW + 0.1, y: a.card_y, w: cardW, h: a.card_h,
      fill: { color: C(ctx, "bg_soft") }, line: { color: C(ctx, "line"), width: 0.5 },
    });
    slide.addText(it.date || "", {
      x: a.x + i * segW + 0.2, y: a.card_y + 0.12, w: cardW - 0.2, h: 0.2,
      fontSize: 9, bold: true, color: C(ctx, accent),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true,
    });
    slide.addText(it.title || "", {
      x: a.x + i * segW + 0.2, y: a.card_y + 0.36, w: cardW - 0.2, h: 0.36,
      fontSize: 10, bold: true, color: C(ctx, "navy"),
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true, valign: "top",
    });
    if (it.sub) slide.addText(it.sub, {
      x: a.x + i * segW + 0.2, y: a.card_y + 0.74, w: cardW - 0.2, h: 0.5,
      fontSize: 8.5, color: C(ctx, "slate"), fontFace: ctx.spec.fonts.body,
      margin: 0, isTextBox: true, valign: "top",
    });
    // caption below band
    slide.addText(it.milestone || "", {
      x: a.x + i * segW, y: bandY + 0.3, w: segW, h: 0.2,
      fontSize: 8.5, color: C(ctx, "ink"), align: "center",
      fontFace: ctx.spec.fonts.body, margin: 0, isTextBox: true,
    });
  });
}

/** Dark Premium — navy cover/section/closing, white content. */
function darkCover(slide, s, ctx) {
  slide.background = { color: C(ctx, "navy") };
  const a = ctx.spec.archetypes.cover;
  // gold rule anchored left, larger type
  slide.addShape("rect", {
    x: 0.65, y: 2.1, w: 0.09, h: 2.4,
    fill: { color: C(ctx, "gold") }, line: { color: C(ctx, "gold"), width: 0 },
  });
  if (s.eyebrow) slide.addText(s.eyebrow, {
    x: 1.0, y: 2.2, w: 10, h: 0.3, fontSize: 13, bold: true, color: C(ctx, "gold"),
    fontFace: ctx.spec.fonts.heading, charSpacing: 3, margin: 0, isTextBox: true,
  });
  if (s.title) slide.addText(s.title, {
    x: 1.0, y: 2.7, w: 11.5, h: 1.0, fontSize: 40, bold: true, color: C(ctx, "white"),
    fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true, valign: "middle",
  });
  if (s.subtitle) slide.addText(s.subtitle, {
    x: 1.0, y: 3.85, w: 10, h: 0.45, fontSize: 17, color: C(ctx, "slate2"),
    fontFace: ctx.spec.fonts.heading, margin: 0, isTextBox: true,
  });
  if (s.tagline) slide.addText(s.tagline, {
    x: 1.0, y: 4.9, w: 10, h: 0.3, fontSize: 10, bold: true, color: C(ctx, "white"),
    fontFace: ctx.spec.fonts.body, charSpacing: 3, margin: 0, isTextBox: true,
  });
  addBrandHeader(slide, ctx, "light_on_dark");
  addFooter(slide, ctx, "light_on_dark");
}

const STYLE_BUILDERS = {
  "exec-brief": execBrief,
  "kpi-wall": kpiWall,
  catalog,
  "roadmap-h": roadmapH,
  "dark-cover": darkCover,
};

const BUILDERS = {
  cover, closing, section, "kpi-bar": kpiBar, timeline, table,
  "two-col": twoCol, bullets, chart, image,
  ...STYLE_BUILDERS,
};

module.exports = { BUILDERS, STYLE_BUILDERS, C, addTopBand, addFooter, addBrandHeader, addTitleBlock };