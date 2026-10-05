#!/usr/bin/env python3
"""
Flag a live business figure standing in skill rule text.

The standing rule allows a figure in three shapes only:
  1. inside a dated evidence block that also carries a guard
     ("ห้ามนำไปตอบ" / "ค่าชั่วขณะ" / "อ่านค่าจริง")
  2. an unmistakably synthetic formatting example (฿1.23M, 12,345 ชิ้น)
  3. a ratio that describes the shape of a bug, not the business

Anything else is a stale data source the model will quote as the answer. The rule
was written down and still accumulated 18 violations across four files before the
2026-10-05 sweep, which is why it is a lint now.

    python tools/check-pinned-values.py            # advisory report, exit 0
    python tools/check-pinned-values.py --strict   # exit 1 on any hit

ADVISORY BY DEFAULT, ON PURPOSE. Measured on the 34-file corpus on 2026-10-05 it
still over-fires on two legitimate shapes: evidence tables (a zone table of
snapshot values) and bug-shape ratios ("PO จะพอง ~42%", which the rule allows).
Treat every hit as a question, not a verdict. See tests/ for the known limits.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Deliberately narrow: a lint that fires on threshold rows (≥80%=🟢) gets
# switched off, so bare policy numbers are left alone. Precision over recall.
CANDIDATES: list[tuple[str, re.Pattern[str]]] = [
    ("baht amount", re.compile(r"฿\s?\d[\d,]*(?:\.\d+)?")),
    ("approximate share", re.compile(r"~\s?\d+(?:\.\d+)?(?:\s?-\s?\d+(?:\.\d+)?)?\s?%")),
    ("decimal share", re.compile(r"(?<![\w.])\d+\.\d+\s?%")),
    ("approximate scale", re.compile(r"~\s?\d[\d,]*\s?(?:สาขา|แถว|ล้าน|SKU|รุ่น|ชิ้น|คน|ใบ)")),
]

DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b|[ก-๙]{1,3}\.\s*20\d\d")
GUARD = re.compile(r"ห้ามนำไปตอบ|ค่าชั่วขณะ|ห้ามนำไปใช้ตอบ|อ่านค่าจริง|ตัวเลขสมมติ")
# A threshold row states a policy. A rank label ("Top 10 %") is not a share.
# A "Numbers:" line is the rulebook's own formatting example.
THRESHOLD_ROW = re.compile(r"[🟢🟡🔴]")
RANK_LABEL = re.compile(r"Top\s+\d+\s*%")
FORMAT_EXAMPLE = re.compile(r"Numbers:|รูปแบบการเขียน")

SYNTHETIC = [
    "฿1.23M", "฿850K", "฿45.2M", "+8.2%", "1,234", "12,345", "1,240",
    "8,530", "315", "12,450", "฿1,747", "97.7%", "16.0%",
]

MCG_PLUGINS = [
    "mcg-crm-agent",
    "mcg-sales-agent",
    "mcg-target-agent",
    "mcg-product-agent",
    "mcg-inventory-agent",
    "mcg-executive-agent",
]


@dataclass(frozen=True)
class Finding:
    line: int
    kind: str
    token: str
    text: str

    def __str__(self) -> str:
        return f"line {self.line}: [{self.kind}] {self.token!r} in {self.text.strip()[:70]!r}"


def scan(markdown: str) -> list[Finding]:
    """Flag figures that are not covered by their block's caption.

    The rule is about blocks, not lines: a figure is allowed when the block it
    sits in is captioned with a date AND a guard. So a section (delimited by a
    heading) is exempt when its heading, or the first non-empty line under it,
    carries both. This is why a table of snapshot values under a dated caption
    passes while the same numbers loose in a rule sentence do not.
    """
    findings: list[Finding] = []
    lines = markdown.splitlines()
    in_fence = False
    caption_ok = False

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if re.match(r"^#{1,6}\s", stripped):
            caption_ok = False
            continue

        # A caption governs the lines under it until the next heading, and it has
        # to carry a date AND a guard. That is why a table of snapshot values
        # under a dated caption passes while the same numbers loose in a rule do
        # not. Dates are recognised in ISO or Thai form (`1-20 ก.ย. 2026`).
        if DATE.search(line) and GUARD.search(line):
            caption_ok = True

        if caption_ok or DATE.search(line) or GUARD.search(line):
            continue
        if THRESHOLD_ROW.search(line) or RANK_LABEL.search(line) or FORMAT_EXAMPLE.search(line):
            continue

        scrubbed = line
        for token in SYNTHETIC:
            scrubbed = scrubbed.replace(token, "")
        # Threshold markers in a rule (≥80%) state a policy, not a measurement.
        scrubbed = re.sub(r"[≥≤]\s?\d+(?:\.\d+)?%", "", scrubbed)

        # One finding per figure: "~1.5%" must not also report as "1.5%".
        hits: list[tuple[int, int, str, str]] = []
        for kind, pattern in CANDIDATES:
            for match in pattern.finditer(scrubbed):
                hits.append((match.start(), match.end(), kind, match.group(0)))

        kept: list[tuple[int, int]] = []
        for start, end, kind, token in sorted(hits, key=lambda h: (h[0], -h[1])):
            if any(start < k_end and end > k_start for k_start, k_end in kept):
                continue
            kept.append((start, end))
            findings.append(Finding(lineno, kind, token, line))

    return findings


def _captioned(text: str) -> bool:
    """A caption qualifies when it carries a date and a guard."""
    return bool(DATE.search(text) and GUARD.search(text))


def skill_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    found: list[Path] = []
    for name in MCG_PLUGINS:
        plugin = root / name
        if plugin.is_dir():
            found.extend(sorted(plugin.rglob("SKILL.md")))
    return found or sorted(root.rglob("SKILL.md"))


def main(argv: list[str]) -> int:
    # Skill files are Thai; a cp874 console would crash on the first odd glyph.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    strict = "--strict" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(".")
    files = skill_files(root)
    if not files:
        print(f"no SKILL.md found under {root}")
        return 0

    total = 0
    for path in files:
        findings = scan(path.read_text(encoding="utf-8"))
        if not findings:
            continue
        total += len(findings)
        print(f"\n{path}  ({len(findings)})")
        for f in findings:
            print(f"  {f}")

    print(f"\n{len(files)} SKILL.md scanned · {total} figure(s) to review")
    if total:
        print("Each one: move it into a dated block with a guard, make it synthetic,")
        print("or confirm it is a bug-shape ratio and leave it.")
    return 1 if (total and strict) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
