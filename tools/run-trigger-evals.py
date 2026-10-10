#!/usr/bin/env python3
"""Run and check the skill trigger evals.

Two passes, because they fail for different reasons and only one of them needs a model.

**Static** (always runs, no network). Schema, duplicates, a query that appears on both sides of the
line, a skill whose evals file is missing or empty, and — the check that would have caught a real
mistake — whether the skills of a plugin still match what the plugin declares. A renamed or deleted
skill leaves its evals behind.

**Trigger** (needs a model, opt-in). Presents a skill's own description and one query, and asks
whether the skill would be invoked. This is a PROXY, not the real thing: the deployment answers that
question with its own model, and no local endpoint reproduces that judgement. A clean run means the
description discriminates on the model you pointed it at, which is worth knowing and is not the same
as knowing how the deployment behaves.

    python tools/run-trigger-evals.py                              # static only
    python tools/run-trigger-evals.py --model qwen2.5-coder:32b   # static + trigger
    python tools/run-trigger-evals.py --model gpt-4o-mini \
        --base-url https://api.openai.com/v1                      # any OpenAI-compatible endpoint

Exit is 0 unless --strict is given, matching tools/check-pinned-values.py: these are questions to
read, not verdicts to act on blind.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_TIMEOUT = 120
# Enough for a reasoning model to finish thinking and still answer in a word.
DEFAULT_MAX_TOKENS = 1024

# The instruction the real deployment receives is the skill's description and nothing else, so that
# is what the proxy is given too.
PROMPT = """You are deciding whether to load a skill.

Skill description:
{description}

User request:
{query}

Would you load this skill for that request? Answer with exactly one word: yes or no."""


class Case:
    def __init__(self, skill, query, should_trigger, source):
        self.skill = skill
        self.query = query
        self.should_trigger = should_trigger
        self.source = source

    def __repr__(self):
        return f"Case({self.skill!r}, {self.query!r}, {self.should_trigger})"


def frontmatter(text):
    """The frontmatter block, or '' when there is none."""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def description_of(skill_md: Path):
    """The skill's own description.

    Handles both shapes this repo uses: `description: text` on one line, and the `>` block scalar
    whose value is the indented lines below it. A YAML library would be the general answer; this is
    deliberately narrow, because the alternative is a dependency for one field.
    """
    fm = frontmatter(skill_md.read_text(encoding="utf-8"))
    if not fm:
        return None

    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^description:\s*(.*)$", line)
        if not m:
            continue

        inline = m.group(1).strip()
        if inline and inline not in (">", "|", ">-", "|-"):
            return inline

        block = []
        for following in lines[i + 1:]:
            if following.strip() and not following.startswith((" ", "\t")):
                break
            block.append(following.strip())
        return " ".join(part for part in block if part)

    return None


def discover(root: Path):
    """Every skill with evals, as (skill_name, description, evals_path, cases)."""
    found = []
    for evals in sorted(root.glob("*/skills/*/evals/trigger_eval.json")):
        skill_md = evals.parent.parent / "SKILL.md"
        try:
            raw = json.loads(evals.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            found.append((evals.parent.parent.name, None, evals, exc))
            continue

        cases = [
            Case(evals.parent.parent.name, item.get("query", ""), bool(item.get("should_trigger")), evals)
            for item in raw
        ]
        found.append((evals.parent.parent.name, description_of(skill_md) if skill_md.is_file() else None, evals, cases))
    return found


def static_findings(root: Path):
    """Problems a machine can settle without asking a model."""
    findings = []

    for name, description, evals, cases in discover(root):
        rel = evals.relative_to(root)

        if isinstance(cases, Exception):
            findings.append((rel, f"not valid JSON: {cases}"))
            continue

        if not cases:
            findings.append((rel, "no cases"))
            continue

        if description is None:
            findings.append((rel.parent.parent, "SKILL.md has no description, so nothing decides on it"))

        seen = {}
        for case in cases:
            key = case.query.strip().lower()
            if key in seen and seen[key] != case.should_trigger:
                findings.append((rel, f"same query on both sides: {case.query!r}"))
            seen[key] = case.should_trigger

        duplicates = {q for q, _ in seen.items() if sum(1 for c in cases if c.query.strip().lower() == q) > 1}
        for dup in sorted(duplicates):
            findings.append((rel, f"duplicate query: {dup!r}"))

        positives = sum(1 for c in cases if c.should_trigger)
        negatives = len(cases) - positives
        if positives < 5:
            findings.append((rel, f"only {positives} should-trigger cases; a thin positive set proves little"))
        if negatives < 3:
            findings.append((rel, f"only {negatives} should-not-trigger cases; a description is only tested by what it must refuse"))

    findings.extend(orphan_findings(root))
    return findings


def orphan_findings(root: Path):
    """Evidently abandoned or mismatched eval files.

    The check that earns its place: renaming a skill leaves its old evals behind under the old name,
    and nothing else notices.
    """
    findings = []
    for plugin in sorted(p for p in root.glob("mcg-*") if p.is_dir()):
        declared = set()
        for skill_md in plugin.glob("skills/*/SKILL.md"):
            declared.add(skill_md.parent.name)

        for d in sorted(plugin.glob("skills/*")):
            if not d.is_dir():
                continue
            if d.name not in declared and (d / "evals").is_dir():
                findings.append((d, "has evals but no SKILL.md"))
    return findings


def ask(base_url, model, api_key, description, query, timeout, max_tokens):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT.format(description=description, query=query)}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }).encode()

    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read())

    choice = payload["choices"][0]
    content = (choice["message"].get("content") or "").strip()

    # A reasoning model spends the budget thinking and returns an empty content field with
    # finish_reason "length". Reading its reasoning instead would be wrong: that text discusses the
    # question and contains both words, so it is not an answer. Report the cause instead.
    if not content:
        raise ValueError(
            f"model returned no answer (finish_reason={choice.get('finish_reason')!r}); "
            "a reasoning model needs a larger --max-tokens")

    answer = content.lower().strip(" 	.\"'*`")

    # "Yes." and "yes, because ..." both mean yes; a reply that says both is refused rather than
    # guessed at. Split into words instead of matching with a word-boundary pattern.
    words = set(re.findall("[a-z]+", answer))
    says_yes = "yes" in words
    says_no = "no" in words
    if says_yes != says_no:
        return says_yes

    raise ValueError(f"model did not answer yes or no: {content[:80]!r}")


def run_trigger(root: Path, args):
    totals = {"hit": 0, "miss": 0, "error": 0}
    misses = []

    for name, description, evals, cases in discover(root):
        if isinstance(cases, Exception):
            continue
        if not args.filter or args.filter in str(evals):
            print(f"\n* {evals.relative_to(root)}  ({len(cases)} cases)")
        else:
            continue

        if not description:
            print("   skipped: no description to decide on")
            continue

        for case in cases:
            try:
                got = ask(args.base_url, args.model, args.api_key, description, case.query, args.timeout, args.max_tokens)
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError) as exc:
                totals["error"] += 1
                print(f"   ERROR  {case.query!r}: {exc}")
                continue

            if got == case.should_trigger:
                totals["hit"] += 1
                mark = "ok  "
            else:
                totals["miss"] += 1
                mark = "MISS"
                misses.append((name, case.query, case.should_trigger, got))

            want = "yes" if case.should_trigger else "no "
            print(f"   {mark}  want {want}  got {'yes' if got else 'no '}  {case.query}")

    return totals, misses


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument("--model", help="run the trigger pass against this model; omit for static only")
    parser.add_argument("--base-url", default=os.environ.get("TRIGGER_EVAL_BASE_URL", DEFAULT_BASE_URL),
                        help=f"OpenAI-compatible endpoint (default {DEFAULT_BASE_URL})")
    parser.add_argument("--api-key", default=os.environ.get("TRIGGER_EVAL_API_KEY"),
                        help="bearer token; also read from TRIGGER_EVAL_API_KEY")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                        help="completion budget; a reasoning model needs room to think before it answers")
    parser.add_argument("--filter", help="only skills whose evals path contains this text")
    parser.add_argument("--strict", action="store_true", help="exit 1 when anything is reported")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    print("== static ==")
    findings = static_findings(root)
    if findings:
        for where, what in findings:
            print(f"   {where}: {what}")
    else:
        print("   nothing to review")

    failed = bool(findings)

    if args.model:
        print(f"\n== trigger (proxy, {args.model} at {args.base_url}) ==")
        totals, misses = run_trigger(root, args)
        graded = totals["hit"] + totals["miss"]
        if graded:
            print(f"\n   {totals['hit']}/{graded} agree "
                  f"({totals['hit'] / graded * 100:.0f}%), {totals['error']} errored")
        if misses:
            print("   disagreements — read each as a question about the DESCRIPTION, not the case:")
            for name, query, want, got in misses:
                print(f"     {name}: want {'yes' if want else 'no'}, got {'yes' if got else 'no'} — {query!r}")
        failed = failed or bool(misses) or totals["error"] > 0
        print("\n   Reminder: this endpoint is a proxy. A clean run does not prove how the deployment decides.")

    if args.strict and failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
