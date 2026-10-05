#!/usr/bin/env python3
"""
Stop-hook handler: run check_answer_terms over the last assistant message.

Claude Code calls a Stop hook with JSON on stdin. This reads the transcript,
takes the final assistant message, scans it, and blocks with a reason when
internal identifiers are present so the model rewrites before the user sees it.

FAIL OPEN BY DESIGN. If the transcript cannot be read or the shape is not what
this expects, it exits 0 and lets the answer through. A guard that breaks must
never hold up every reply.

Assumed transcript shape (one JSON object per line), which needs one real
session to confirm:
    {"type": "assistant", "message": {"role": "assistant",
     "content": [{"type": "text", "text": "..."}]}}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "answer-guard"))

from check_answer_terms import scan  # noqa: E402

MAX_BLOCK_REASON = 1200


def last_assistant_text(transcript_path: str) -> str:
    """Concatenate the text blocks of the final assistant turn."""
    text_parts: list[str] = []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = entry.get("message") or {}
        if message.get("role") != "assistant":
            continue
        content = message.get("content")
        if isinstance(content, str):
            text_parts = [content]
        elif isinstance(content, list):
            text_parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
    return "\n".join(part for part in text_parts if part)


def decide(payload: dict) -> dict | None:
    """None means allow. A dict is the block payload for the host."""
    # The host sets this when the turn is already a re-run caused by this hook.
    # Without it a false positive would block, be rewritten, blocked again.
    if payload.get("stop_hook_active"):
        return None

    transcript_path = payload.get("transcript_path") or ""
    if not transcript_path:
        return None

    answer = last_assistant_text(transcript_path)
    if not answer:
        return None

    violations = scan(answer)
    if not violations:
        return None

    listed = "\n".join(f"  - {v.token} ({v.rule})" for v in violations[:20])
    reason = (
        "The draft answer contains internal identifiers the user must not see.\n"
        f"{listed}\n\n"
        "Rewrite the answer replacing each with its business term "
        "(ยอดขายสุทธิ · ใบเสร็จสมาชิก · สัดส่วนสมาชิก · จำนวนรุ่น-สี · ข้อมูลสินค้าในระบบ) "
        "and keep the footer to the source and as-of only. "
        "Do not remove or alter any figure."
    )
    return {"decision": "block", "reason": reason[:MAX_BLOCK_REASON]}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # fail open

    result = decide(payload)
    if result is None:
        return 0

    json.dump(result, sys.stdout)
    return 0  # exit 0 with the decision payload; the block is in the JSON


if __name__ == "__main__":
    raise SystemExit(main())
