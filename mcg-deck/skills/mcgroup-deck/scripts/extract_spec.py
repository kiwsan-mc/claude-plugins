#!/usr/bin/env python3
"""
extract_spec.py — reverse a .pptx into a machine-readable template spec.

Usage:
    python extract_spec.py deck.pptx [-o spec.json] [--pretty]

Emits: canvas size, design tokens (color/font), grid margins, footer/header band
positions, and a per-slide archetype classification.

Mode B of the mcgroup-deck skill: point it at ANY deck to replicate that deck's
structure, not just the MC Group house file.

No third-party deps. Pure stdlib + zipfile. Reads the .pptx as a ZIP.
"""
import argparse
import collections
import json
import re
import sys
import zipfile
from pathlib import Path

EMU_PER_IN = 914400.0

# ---------- helpers ----------

def emu_to_in(v):
    try:
        return round(int(v) / EMU_PER_IN, 3)
    except (TypeError, ValueError):
        return None


def read_part(zf, name):
    try:
        return zf.read(name).decode("utf-8", "replace")
    except KeyError:
        return None


def norm_slide_keys(zf):
    """Return slide part names sorted by slide number."""
    names = [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    return sorted(names, key=lambda n: int(re.search(r"slide(\d+)", n).group(1)))


# ---------- extraction ----------

def extract_canvas(zf):
    x = read_part(zf, "ppt/presentation.xml") or ""
    m = re.search(r'<p:sldSz[^>]*cx="(\d+)"[^>]*cy="(\d+)"', x)
    if not m:
        m = re.search(r'<p:sldSz[^>]*cy="(\d+)"[^>]*cx="(\d+)"', x)
        if m:
            cy, cx = m.group(1), m.group(2)
            return {"w_in": emu_to_in(cx), "h_in": emu_to_in(cy),
                    "cx_emu": int(cx), "cy_emu": int(cy)}
        return None
    cx, cy = m.group(1), m.group(2)
    return {"w_in": emu_to_in(cx), "h_in": emu_to_in(cy),
            "cx_emu": int(cx), "cy_emu": int(cy)}


def extract_theme(zf):
    """First theme: color scheme + font scheme."""
    name = "ppt/theme/theme1.xml"
    x = read_part(zf, name)
    if not x:
        cands = [n for n in zf.namelist() if re.match(r"ppt/theme/theme\d+\.xml$", n)]
        x = read_part(zf, sorted(cands)[0]) if cands else ""
    colors, fonts = {}, {}
    m = re.search(r"<a:clrScheme.*?</a:clrScheme>", x, re.S)
    if m:
        blk = m.group(0)
        for slot in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2",
                     "accent3", "accent4", "accent5", "accent6",
                     "hlink", "folHlink"):
            sm = re.search(rf"<a:{slot}>(.*?)</a:{slot}>", blk, re.S)
            if not sm:
                continue
            inner = sm.group(1)
            srgb = re.search(r'srgbClr val="([0-9A-Fa-f]{6})"', inner)
            sysc = re.search(r'sysClr[^>]*lastClr="([0-9A-Fa-f]{6})"', inner)
            colors[slot] = (srgb or sysc).group(1).upper() if (srgb or sysc) else None
    fm = re.search(r"<a:majorFont>.*?</a:majorFont>", x, re.S)
    if fm:
        lat = re.search(r'<a:latin typeface="([^"]*)"', fm.group(0))
        fonts["major"] = lat.group(1) if lat else None
    fm = re.search(r"<a:minorFont>.*?</a:minorFont>", x, re.S)
    if fm:
        lat = re.search(r'<a:latin typeface="([^"]*)"', fm.group(0))
        fonts["minor"] = lat.group(1) if lat else None
    return {"colors": colors, "fonts": fonts}


def extract_color_histogram(zf, slide_names):
    """Most-used srgb colors across slides — the real design palette."""
    hist = collections.Counter()
    for n in slide_names:
        x = read_part(zf, n) or ""
        for c in re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', x):
            hist[c.upper()] += 1
    return [{"hex": c, "count": k} for c, k in hist.most_common(30)]


def extract_shapes(zf, slide_name):
    """Parse top-level <p:sp> shapes: name, position (in), size (in), fill, first text."""
    x = read_part(zf, slide_name) or ""
    out = []
    for m in re.finditer(r"<p:sp>.*?</p:sp>", x, re.S):
        s = m.group(0)
        nm = re.search(r'name="([^"]*)"', s)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', s)
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', s)
        fill = re.search(r'<a:solidFill><a:srgbClr val="([0-9A-Fa-f]{6})"', s)
        texts = re.findall(r"<a:t>(.*?)</a:t>", s, re.S)
        if not (off and ext):
            continue
        out.append({
            "name": nm.group(1) if nm else None,
            "x": emu_to_in(off.group(1)),
            "y": emu_to_in(off.group(2)),
            "w": emu_to_in(ext.group(1)),
            "h": emu_to_in(ext.group(2)),
            "fill": fill.group(1).upper() if fill else None,
            "text": (texts[0].strip() if texts else ""),
        })
    return out


DARK_FILLS = {"001245", "000000", "0B1F3A", "142A60"}  # navy-family backgrounds


def slide_bg_fill(zf, slide_name):
    """Return hex of the slide's <p:bg> solid fill, or None."""
    x = read_part(zf, slide_name) or ""
    m = re.search(r"<p:bg>.*?</p:bg>", x, re.S)
    if not m:
        return None
    c = re.search(r'srgbClr val="([0-9A-Fa-f]{6})"', m.group(0))
    return c.group(1).upper() if c else None


def classify_slide(zf, slide_name, shapes):
    """Heuristic archetype label from shape layout. Order matters: most specific first."""
    x = read_part(zf, slide_name) or ""
    pics = x.count("<p:pic>") + x.count("<p:graphicFrame>")
    texts = x.count("<a:t>")
    n_sp = len(shapes)

    # full-bleed image slide: pictures/graphicFrames present, no text
    if pics >= 1 and texts == 0:
        return "image"

    joined = " ".join(s["text"] for s in shapes).upper()
    bg = slide_bg_fill(zf, slide_name)

    # dark slide background => cover / closing
    if bg and bg in DARK_FILLS:
        if "THANK" in joined:
            return "closing"
        return "cover"

    # section divider: sparse slide, tall gold side rule, blue eyebrow, no body rows
    gold_rule = [s for s in shapes
                 if (s["fill"] or "").upper() == "E6A82D"
                 and s["h"] and s["h"] >= 1.5 and s["w"] and s["w"] <= 0.2]
    if gold_rule and n_sp <= 14:
        return "section"

    # timeline: >=3 small near-square dots (checked before kpi/table)
    dots = [s for s in shapes
            if s["h"] and 0.14 <= s["h"] <= 0.26 and s["w"] and 0.14 <= s["w"] <= 0.26]
    if len(dots) >= 3:
        return "timeline"

    # KPI cards: >=3 shapes same band, w ~2.9-3.1, h ~0.9-1.15
    cards = [s for s in shapes
             if s["w"] and 2.8 <= s["w"] <= 3.2 and s["h"] and 0.85 <= s["h"] <= 1.15]
    if len(cards) >= 3:
        return "kpi-bar"

    # zebra table: >=4 rows sharing an x, small equal h, alternating fills
    rows = collections.defaultdict(list)
    for s in shapes:
        if s["h"] and 0.2 <= s["h"] <= 0.5 and s["w"] and s["w"] >= 2.0:
            rows[round(s["x"], 1)].append(s)
    for _, grp in rows.items():
        if len(grp) >= 4 and len({g["fill"] for g in grp}) >= 2:
            return "table"

    if texts > 0:
        return "content"
    return "blank"


def extract_slides(zf):
    out = []
    for n in norm_slide_keys(zf):
        shapes = extract_shapes(zf, n)
        out.append({
            "part": n,
            "index": int(re.search(r"slide(\d+)", n).group(1)),
            "archetype": classify_slide(zf, n, shapes),
            "shape_count": len(shapes),
            "shapes": shapes,
        })
    return out


def detect_grid(slides):
    """Infer margin, footer band, top band from shape x/y clusters.
    Excludes full-bleed background/rule shapes (x=0 or width >= 12in)."""
    xs, footers, tops = [], [], []
    for s in slides:
        for sh in s["shapes"]:
            w = sh.get("w")
            if sh["x"] is not None and w is not None and sh["x"] > 0.05 and w < 12.0:
                xs.append(sh["x"])
            if sh["y"] is not None:
                if 6.7 <= sh["y"] <= 7.3 and sh["h"] is not None and sh["h"] < 0.3:
                    footers.append(sh["y"])
                if sh["y"] < 0.2 and sh["h"] and sh["h"] <= 0.15:
                    tops.append(sh["h"])
    margin = min(xs) if xs else None
    return {
        "margin_x_in": round(margin, 2) if margin is not None else None,
        "footer_y_in": round(min(footers), 2) if footers else None,
        "top_band_h_in": round(min(tops), 2) if tops else None,
    }


def main():
    ap = argparse.ArgumentParser(description="Extract a .pptx into a template spec JSON.")
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--with-shapes", action="store_true",
                    help="include full per-shape geometry (large)")
    args = ap.parse_args()

    path = Path(args.pptx)
    if not path.exists():
        sys.exit(f"not found: {path}")

    with zipfile.ZipFile(path) as zf:
        slides = extract_slides(zf)
        spec = {
            "source": path.name,
            "canvas": extract_canvas(zf),
            "theme": extract_theme(zf),
            "palette_histogram": extract_color_histogram(zf, norm_slide_keys(zf)),
            "grid": detect_grid(slides),
            "slide_count": len(slides),
            "archetypes": [{"index": s["index"], "archetype": s["archetype"]} for s in slides],
            "archetype_counts": dict(collections.Counter(s["archetype"] for s in slides)),
        }
        if args.with_shapes:
            spec["slides"] = slides

    out_path = Path(args.out) if args.out else path.with_suffix(".spec.json")
    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.pretty:
        print(json.dumps(spec, indent=2, ensure_ascii=False))
    else:
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()