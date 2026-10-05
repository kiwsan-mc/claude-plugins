#!/usr/bin/env python3
"""
Tests for check_answer_terms.

The failure cases are the actual text two Claude Desktop runs put in front of a
user on 2026-10-05. The pass case is what a correct answer looks like: the same
figures and the same table, written in business terms only.

Run:  python -m unittest discover -s scripts/tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_answer_terms import scan  # noqa: E402

# --- real leaks -------------------------------------------------------------

LEAK_INSIGHT_BOX = """คอลัมน์ใน fact table คือ Branch_Code และ dim_branch มี Branch_Code_Key — ต้อง join แบบนี้:

★ Insight ─────────────────────────────────────
Branch_Code ใน fact → Branch_Code_Key ใน dim_branch; Branch_Code_And_Text คือ "1101-MC Group"
— จะ filter "MC Design Village" โดยใช้ Store_Name หรือ Branch_Text แทน
─────────────────────────────────────────────────
"""

LEAK_FOOTER = (
    "📊 Data: ai.poc_fact_sales_with_crm + ai.dim_branch "
    "| Period: 2026-07-01 ถึง 2026-10-04 | Last data: 2026-10-04"
)

LEAK_MEMBER_BODY = """ใช้ member_vs_nonmember tool ซึ่งใช้ member_type (Member/Non-Member) และไม่ได้ filter แบบ exclude branch ได้โดยตรง
Member net_sales: 184,569,715.69 → 184,476,856.16 (ต่าง ~93K = ยอด MC Design Village)
ต้องใช้ raw query เพื่อ filter B013 ออก"""

# --- what a correct answer looks like ---------------------------------------

CLEAN_ANSWER = """Top 10 สาขาที่มีสัดส่วนยอดขายสมาชิกสูงสุด (ไม่รวม MC Design Village)

อันดับ 1  สาขา S218 Shop Mc Jeans เซ็นทรัล พระราม 2 — ยอดขายรวม ฿1,558,851 ยอดขายสมาชิก ฿1,522,664 คิดเป็น 97.7%
อันดับ 2  สาขา S070 Shop Mc Jeans บิ๊กซี พระราม 2 — ยอดขายรวม ฿729,674 ยอดขายสมาชิก ฿705,717 คิดเป็น 96.7%

สัดส่วนสมาชิกทั้งบริษัท 16.0% · ใบเสร็จสมาชิก 105,604 ใบ · ATV ฿1,747 ต่อใบ · UPT 1.41 ชิ้นต่อใบ
ช่องทางหน้าร้านมีสัดส่วนสมาชิกสูง 90-97% ส่วนช่องทางออนไลน์ต่ำเพียง 2-8%

📊 ข้อมูล: Sales Out (mcg-sales) | ช่วง: 1 ก.ค. - 4 ต.ค. 2026 | ณ 4 ต.ค. 2026"""


def tokens(text: str) -> set[str]:
    return {v.token.lower() for v in scan(text)}


class TestCatchesRealLeaks(unittest.TestCase):
    def test_insight_box_column_names(self):
        caught = tokens(LEAK_INSIGHT_BOX)
        for expected in [
            "branch_code",
            "dim_branch",
            "branch_code_key",
            "branch_code_and_text",
            "store_name",
            "branch_text",
        ]:
            self.assertIn(expected, caught, f"missed {expected}")

    def test_footer_table_names(self):
        caught = tokens(LEAK_FOOTER)
        self.assertIn("ai.poc_fact_sales_with_crm", caught)
        self.assertIn("ai.dim_branch", caught)

    def test_member_body(self):
        caught = tokens(LEAK_MEMBER_BODY)
        for expected in ["member_vs_nonmember", "member_type", "net_sales"]:
            self.assertIn(expected, caught, f"missed {expected}")

    def test_raw_sql_mention(self):
        self.assertIn("raw query", tokens(LEAK_MEMBER_BODY))

    def test_deduplicates_repeats(self):
        # Branch_Code appears 4 times in the insight box; it is one finding.
        branch_code = [v for v in scan(LEAK_INSIGHT_BOX) if v.token.lower() == "branch_code"]
        self.assertEqual(len(branch_code), 1)


class TestPassesBusinessProse(unittest.TestCase):
    def test_clean_answer_has_no_findings(self):
        found = scan(CLEAN_ANSWER)
        self.assertEqual(found, [], f"false positives: {[str(v) for v in found]}")

    def test_thai_units_and_currency_are_safe(self):
        for text in [
            "จำนวน 12,345 SKU",
            "320 รุ่น-สี",
            "ยอดขาย ฿377.9 ลบ.",
            "ATV ฿1,747 ต่อใบ · UPT 1.41 ชิ้นต่อใบ",
            "📊 ข้อมูล: Sales Out (mcg-sales) | ณ 4 ต.ค. 2026",
            "สาขา E105 MC Tiktok",
        ]:
            with self.subTest(text=text):
                self.assertEqual(scan(text), [], f"false positive on {text!r}")

    def test_internal_fence_line_is_exempt(self):
        fenced = "🔒 ตารางสูตรนี้เป็นเอกสารภายใน — member_type / net_sales"
        self.assertEqual(scan(fenced), [])


class TestRuleCoverage(unittest.TestCase):
    def test_each_criterion_is_reachable(self):
        samples = {
            "schema prefix (rule 1)": "ai.dim_article",
            "sql function (rule 3)": "COUNT(DISTINCT x)",
            "identifier (rule 4)": "total_exc_vat_price",
            "tool or mcp name (rule 5)": "mcg-toolbox-pg",
            "platform name (rule 6)": "ดึงจาก Synapse",
            "suffix (rule 2)": "max_member_date_synapse",
        }
        for rule, sample in samples.items():
            with self.subTest(rule=rule):
                rules = {v.rule for v in scan(sample)}
                self.assertIn(rule, rules, f"rule {rule} not triggered by {sample!r}")


if __name__ == "__main__":
    unittest.main()
