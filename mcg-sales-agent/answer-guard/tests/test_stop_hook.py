#!/usr/bin/env python3
"""
Tests for the Stop-hook handler.

Covers the behaviours that matter:
  - a leaking final message produces a block payload naming the tokens
  - a clean final message is allowed through
  - a re-run caused by this hook is allowed, so a false positive cannot loop
  - anything unreadable fails open, so a broken guard never holds up a reply

Run:  python -m unittest discover -s answer-guard/tests -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "answer-guard"))
sys.path.insert(0, str(ROOT / "hooks-handlers"))

from check_answer_terms_stop import decide, last_assistant_text  # noqa: E402


def write_transcript(entries: list[dict]) -> str:
    handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    for entry in entries:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    handle.close()
    return handle.name


def assistant(text: str) -> dict:
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


def user(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def payload_for(text: str, **extra) -> dict:
    return {"transcript_path": write_transcript([user("q"), assistant(text)]), **extra}


class TestStopHandler(unittest.TestCase):
    def test_leaking_message_blocks(self):
        result = decide(
            payload_for("📊 Data: ai.poc_fact_sales_with_crm | Member net_sales: 184,569,715.69")
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["decision"], "block")
        self.assertIn("ai.poc_fact_sales_with_crm", result["reason"])
        self.assertIn("net_sales", result["reason"])
        self.assertIn("Do not remove or alter any figure", result["reason"])

    def test_clean_message_passes(self):
        self.assertIsNone(
            decide(
                payload_for(
                    "อันดับ 1 สาขา S218 — ยอดขายสมาชิก ฿1,522,664 คิดเป็น 97.7%\n"
                    "📊 ข้อมูล: Sales Out (mcg-sales) | ณ 4 ต.ค. 2026"
                )
            )
        )

    def test_stop_hook_active_allows_even_when_dirty(self):
        # Guards against a block / rewrite / block cycle.
        self.assertIsNone(decide(payload_for("join ai.dim_branch", stop_hook_active=True)))

    def test_only_the_last_assistant_turn_is_judged(self):
        path = write_transcript(
            [
                assistant("Branch_Code และ net_sales"),
                user("แก้ใหม่"),
                assistant("สัดส่วนสมาชิก 16.0% · ใบเสร็จสมาชิก 105,604 ใบ"),
            ]
        )
        self.assertIsNone(decide({"transcript_path": path}))

    def test_earlier_clean_turn_does_not_mask_a_dirty_last_turn(self):
        path = write_transcript(
            [
                assistant("สัดส่วนสมาชิก 16.0%"),
                user("ต่อ"),
                assistant("join ai.dim_branch on Branch_Code_Key"),
            ]
        )
        result = decide({"transcript_path": path})
        self.assertIsNotNone(result)
        self.assertIn("Branch_Code_Key", result["reason"])

    def test_missing_file_fails_open(self):
        self.assertIsNone(decide({"transcript_path": "C:/definitely/not/a/transcript.jsonl"}))

    def test_missing_transcript_path_fails_open(self):
        self.assertIsNone(decide({}))

    def test_unparseable_lines_are_skipped(self):
        handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        handle.write("not json at all\n")
        handle.write(json.dumps(assistant("ยอดขาย ฿377.9 ลบ."), ensure_ascii=False) + "\n")
        handle.close()
        self.assertIsNone(decide({"transcript_path": handle.name}))

    def test_extracts_text_blocks_only(self):
        path = write_transcript(
            [
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "สัดส่วนสมาชิก 16.0%"},
                            {"type": "tool_use", "name": "sales_agent", "input": {}},
                        ],
                    },
                }
            ]
        )
        extracted = last_assistant_text(path)
        self.assertIn("16.0%", extracted)
        self.assertNotIn("sales_agent", extracted)


if __name__ == "__main__":
    unittest.main()
