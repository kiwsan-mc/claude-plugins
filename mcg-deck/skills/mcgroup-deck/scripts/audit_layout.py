#!/usr/bin/env python3
"""Audit a pptx for layout problems: off-canvas shapes, text overflow, overlaps."""
import re, sys, zipfile
from pathlib import Path

EMU = 914400
CANVAS_W, CANVAS_H = 13.333, 7.5

def emu(v):
    try: return int(v)/EMU
    except: return None

def sp_boxes(x):
    """Yield dicts for each <=p:sp> and <p:pic> with name, box, text, font sizes."""
    for m in re.finditer(r'<p:(sp|pic)>.*?</p:\1>', x, re.S):
        s = m.group(0)
        nm = re.search(r'name="([^"]*)"', s)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', s)
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', s)
        if not (off and ext): continue
        texts = re.findall(r'<a:t>(.*?)</a:t>', s, re.S)
        sizes = [int(z) for z in re.findall(r'sz="(\d+)"', s)]
        yield {
            "kind": m.group(1),
            "name": nm.group(1) if nm else "?",
            "x": emu(off.group(1)), "y": emu(off.group(2)),
            "w": emu(ext.group(1)), "h": emu(ext.group(2)),
            "text": " ".join(texts),
            "maxsz": max(sizes) if sizes else 0,
        }

def overlap(a, b):
    ax2, ay2 = a["x"]+a["w"], a["y"]+a["h"]
    bx2, by2 = b["x"]+b["w"], b["y"]+b["h"]
    ox = max(0, min(ax2,bx2)-max(a["x"],b["x"]))
    oy = max(0, min(ay2,by2)-max(a["y"],b["y"]))
    return ox*oy, ox, oy

def main(path):
    z = zipfile.ZipFile(path)
    slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
                    key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
    problems = 0
    for sn in slides:
        x = z.read(sn).decode("utf-8","replace")
        idx = int(re.search(r'slide(\d+)', sn).group(1))
        boxes = list(sp_boxes(x))
        issues = []
        # 1. off-canvas / clipped
        for b in boxes:
            if b["x"] < -0.01 or b["y"] < -0.01:
                issues.append(f"OFF-CANVAS  {b['name']:18} x={b['x']:.2f} y={b['y']:.2f}  '{b['text'][:30]}'")
            if b["x"]+b["w"] > CANVAS_W+0.02 or b["y"]+b["h"] > CANVAS_H+0.02:
                issues.append(f"OVERFLOW    {b['name']:18} right={b['x']+b['w']:.2f} bot={b['y']+b['h']:.2f}  '{b['text'][:30]}'")
            # negative / zero size
            if b["w"] <= 0 or b["h"] <= 0:
                issues.append(f"ZERO-SIZE   {b['name']:18} w={b['w']:.2f} h={b['h']:.2f}  '{b['text'][:30]}'")
        # 2. overlap between two text-bearing shapes
        txts = [b for b in boxes if b["text"].strip()]
        for i in range(len(txts)):
            for j in range(i+1, len(txts)):
                area, ox, oy = overlap(txts[i], txts[j])
                if area > 0.003 and ox > 0.05 and oy > 0.05:
                    issues.append(f"OVERLAP     '{txts[i]['text'][:22]}' x '{txts[j]['text'][:22]}'  ox={ox:.2f} oy={oy:.2f}")
        # 3. text overflow: estimate wrapped lines vs box height.
        #    OOXML sz is centipoints: pt = sz/100 ; em(in) = pt/72 ; line height ~1.2em
        for b in txts:
            if b["maxsz"] and b["w"] > 0.3:
                em = (b["maxsz"] / 100.0) / 72.0
                cpl = max(1, int(b["w"] / (0.52 * em)))
                lines = max(1, -(-len(b["text"]) // cpl))
                need = lines * 1.2 * em
                if need > b["h"] + 0.10:
                    issues.append(f"TXT-CLIP    {b['name']:18} need~{need:.2f}in box.h={b['h']:.2f} sz={b['maxsz']} '{b['text'][:40]}'")
        if issues:
            problems += len(issues)
            print(f"--- slide {idx} ({len(boxes)} shapes) ---")
            for i in issues: print("   " + i)
    if problems == 0:
        print("No layout problems found.")
    else:
        print(f"\nTotal: {problems} issue(s)")

if __name__ == "__main__":
    main(sys.argv[1])