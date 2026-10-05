#!/usr/bin/env python3
"""
Guard against internal identifiers leaking into a user-visible answer.

The skill files ban table names, column names, SQL functions, tool names and
platform names from anything the user sees. That ban is text against text and
has leaked twice on 2026-10-05. This checker enforces the same criteria on a
draft answer instead of asking the model to police itself.

Criteria (from the rule block in every SKILL.md, section 1):
  1. a token starting with `ai.`
  2. a token ending in _synapse / _count / _key / _model / _color / _quantity
  3. a SQL function name
  4. a snake_case or Pascal_Snake column name
  5. a tool or MCP server name
  6. a platform or system name

Usage:
    python check_answer_terms.py draft.md
    cat draft.md | python check_answer_terms.py
Exit code 1 when anything is found, 0 when the draft is clean.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# A token carrying an underscore is an identifier, not Thai business prose.
# This catches snake_case (net_sales) and Pascal_Snake (Branch_Code_Key).
IDENTIFIER = re.compile(r"(?<![\w.])([A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+)(?![\w])")

SQL_FUNCTIONS = re.compile(
    r"(?<![\w])(COUNT|SUM|CAST|DISTINCT|APPROX_COUNT_DISTINCT|APPROX_PERCENTILE|"
    r"AVG|MIN|MAX|NULLIF|COALESCE|ROUND|FILTER|RANK|OVER|PARTITION)(?![\w])"
)

SCHEMA_PREFIX = re.compile(r"(?<![\w.])ai\.[A-Za-z_][A-Za-z0-9_]*")

PLATFORM = re.compile(
    r"(?<![\w])(Postgres|PostgreSQL|pgvector|Synapse|BigQuery|Snowflake)(?![\w])",
    re.IGNORECASE,
)

TOOL_OR_SERVER = re.compile(
    r"(?<![\w-])(mcg-toolbox[a-z-]*|mcg_sales_agent_wrapper|plugin_integration_hook|"
    r"pg_describe_table|pg_list_tables|max_sold_date|max_member_date_synapse|"
    r"member_sales_agent_synapse|member_vs_nonmember|member_crm_schema_cheatsheet_synapse|"
    r"AskUserQuestion)(?![\w-])",
    re.IGNORECASE,
)

RAW_SQL = re.compile(r"(?<![\w])(Raw SQL|raw query|T-SQL)(?![\w])", re.IGNORECASE)

CHECKS: list[tuple[str, re.Pattern[str]]] = [
    ("schema prefix (rule 1)", SCHEMA_PREFIX),
    ("sql function (rule 3)", SQL_FUNCTIONS),
    ("identifier (rule 4)", IDENTIFIER),
    ("tool or mcp name (rule 5)", TOOL_OR_SERVER),
    ("platform name (rule 6)", PLATFORM),
    ("raw-sql mention", RAW_SQL),
]

# Rule 2 is a subset of rule 4 but is reported by name, because the skills call
# it out separately and reviewers look for it.
SYNAPSE_SUFFIX = re.compile(
    r"(?<![\w])([A-Za-z][A-Za-z0-9_]*_(?:synapse|count|key|model|color|quantity))(?![\w])",
    re.IGNORECASE,
)

# A fenced block marked internal is exempt: the skill bodies quote SQL on
# purpose, and a reviewer reading the file is not a user reading an answer.
INTERNAL_FENCE = re.compile(r"^\s*>?\s*🔒", re.MULTILINE)


@dataclass(frozen=True)
class Violation:
    rule: str
    token: str
    line: int

    def __str__(self) -> str:
        return f"line {self.line}: [{self.rule}] {self.token!r}"


def scan(text: str, limit_per_rule: int = 40) -> list[Violation]:
    """Return every forbidden token in `text`, deduplicated by rule and token."""
    found: list[Violation] = []
    seen: set[tuple[str, str]] = set()

    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("🔒"):
            continue
        for rule, pattern in CHECKS:
            for match in pattern.finditer(line):
                token = match.group(0)
                key = (rule, token.lower())
                if key in seen:
                    continue
                seen.add(key)
                found.append(Violation(rule, token, lineno))
                if sum(1 for v in found if v.rule == rule) >= limit_per_rule:
                    break

    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("🔒"):
            continue
        for match in SYNAPSE_SUFFIX.finditer(line):
            token = match.group(1)
            key = ("suffix (rule 2)", token.lower())
            if key in seen:
                continue
            seen.add(key)
            found.append(Violation("suffix (rule 2)", token, lineno))

    return found


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        draft = Path(argv[1]).read_text(encoding="utf-8")
        source = argv[1]
    else:
        draft = sys.stdin.read()
        source = "<stdin>"

    violations = scan(draft)
    if not violations:
        print(f"clean: no internal identifiers in {source}")
        return 0

    print(f"{len(violations)} finding(s) in {source}:")
    for v in violations:
        print(f"  {v}")
    print("\nReplace each with its business term, then re-run.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
