#!/usr/bin/env python3
"""
Tests for check-pinned-values.

The catch cases are the real pre-sweep strings from 2026-10-05. The pass cases
are the shapes the rule allows. The last class asserts the KNOWN FALSE POSITIVES:
they are encoded here so nobody silently "fixes" the lint by loosening it, and so
the advisory default has a reason on record.

Run:  python -m unittest discover -s tools/tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# The module name has a dash, so load it by path.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "check_pinned_values", Path(__file__).resolve().parents[1] / "check-pinned-values.py"
)
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod  # dataclasses needs the module resolvable by name
_spec.loader.exec_module(mod)
scan = mod.scan


def tokens(text: str) -> set[str]:
    return {f.token for f in scan(text)}


class TestCatchesRealPinnedValues(unittest.TestCase):
    def test_member_source_claim(self):
        line = ('3. **Member 2 แหล่งให้ค่าไม่ตรงกันมาก** (Postgres ~55% ของยอดขาย '
                'vs CRM ~16%) เพราะ **scope + นิยามต่างกัน** — ต้องระบุเสมอว่าใช้แหล่งไหน')
        caught = tokens(line)
        self.assertIn("~55%", caught)
        self.assertIn("~16%", caught)

    def test_channel_penetration_shares(self):
        line = ('2. **Member penetration ต่างกันตาม channel** — OFFLINE (~64%) และ '
                'MCSHOP.COM (~62%) member-driven; TIKTOK/SHOPEE/LAZADA guest-driven '
                '(member แค่ ~4-9%)')
        caught = tokens(line)
        self.assertIn("~64%", caught)
        self.assertIn("~62%", caught)
        self.assertIn("~4-9%", caught)

    def test_member_row_share(self):
        line = ('1. **ตารางคือยอดขายทั้งหมด** — `Member_Code` เป็นค่าว่าง ~86.7% ของแถว; '
                'member-attributed net sales ≈ 16.6% ของรวม')
        caught = tokens(line)
        self.assertIn("~86.7%", caught)
        self.assertIn("16.6%", caught)

    def test_branch_count(self):
        self.assertIn("~88 สาขา", tokens("4. **ครอบคลุม ~88 สาขา** (Bangkok + ecommerce) — ไม่ใช่ทุกสาขา"))

    def test_small_share(self):
        self.assertIn("~1.5%", tokens("- ⚠️ มีแค่ ~1.5% ของ**รายการขาย**ที่มีส่วนลดสมาชิก"))

    def test_executive_agent_copy(self):
        line = "- ⚠️ **ไม่ตรง**: Discount, Gross · **Member** (Postgres ~55% ทุกสาขา vs CRM ~16% / 88 สาขา)"
        caught = tokens(line)
        self.assertIn("~55%", caught)
        self.assertIn("~16%", caught)

    def test_one_finding_per_figure(self):
        # "~1.5%" must not also be reported as "1.5%".
        found = [f.token for f in scan("- ⚠️ มีแค่ ~1.5% ของรายการขาย")]
        self.assertEqual(found, ["~1.5%"])


class TestAllowsRuleShapes(unittest.TestCase):
    def test_threshold_row(self):
        for line in [
            "| >50%=🔴 | <50%=🔴 |",
            "Discount: ≤40%=🟢, 40-50%=🟡, >50%=🔴",
            "Margin: ≥60%=🟢, 50-<60%=🟡, <50%=🔴",
            "Member Ticket% (SHOP): ≥80%=🟢, 75-79%=🟡, <75%=🔴",
        ]:
            with self.subTest(line=line):
                self.assertEqual(scan(line), [])

    def test_dated_evidence_block(self):
        line = "- ⚠️ ตรวจ 2026-08-26 เป็นต้นมา (30 วัน): ส่วนลดรวม ฿72,782,318.86 (164,252 แถว)"
        self.assertEqual(scan(line), [])

    def test_guarded_evidence_block(self):
        line = "📌 **หลักฐาน ณ 2026-08-26**: ฿141,838.72 ⇒ ต่างกัน ~513 เท่า · 🚫 ห้ามนำไปตอบ"
        self.assertEqual(scan(line), [])

    def test_synthetic_formatting_examples(self):
        for line in [
            "# 20. Numbers: ฿1.23M, +8.2%, ฿850K, 1,234 ชิ้น",
            "# 13. Numbers (ตัวอย่างรูปแบบการเขียน — ตัวเลขสมมติทั้งชุด): SKU ≠ รุ่น",
        ]:
            with self.subTest(line=line):
                self.assertEqual(scan(line), [])

    def test_rank_label_is_not_a_share(self):
        line = "🚫 **ห้ามตอบคำถามจัดอันดับด้วยยอดรวมก้อนเดียว** — Top 10 % Member Sales"
        self.assertEqual(scan(line), [])

    def test_code_fence_is_skipped(self):
        self.assertEqual(scan("```\nSUM(x) / 100 * 100\n฿1,000,000.00\n```"), [])


class TestKnownFalsePositives(unittest.TestCase):
    """Asserted, not excused. If one of these stops firing, update the README."""

    def test_bug_shape_ratio_is_reported(self):
        # The rule explicitly allows a ratio that describes a bug's shape.
        self.assertIn("~42%", tokens("ถ้าไม่กรอง PO จะพอง ~42% และ STO พอง ~239%"))

    def test_evidence_table_is_reported(self):
        self.assertIn("฿875.0", tokens("| GREEN | 3,944,606 | ฿875.0M | ฿904.6M |"))


if __name__ == "__main__":
    unittest.main()
