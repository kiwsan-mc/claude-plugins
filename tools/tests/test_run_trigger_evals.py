"""Tests for run-trigger-evals.py.

The parser and the static checks are pure functions over a directory tree, so they are tested against
temporary trees rather than the real repository — a test that reads the repository would fail every
time someone legitimately edits a skill.

The network path is not tested here. A test that depends on a model endpoint fails for reasons that
have nothing to do with the code.
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "run_trigger_evals", Path(__file__).resolve().parent.parent / "run-trigger-evals.py"
)
rte = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rte)


def make_skill(root, plugin, skill, description, cases, frontmatter_style="block"):
    d = Path(root) / plugin / "skills" / skill
    (d / "evals").mkdir(parents=True)
    if frontmatter_style == "block":
        fm = f"---\nname: {skill}\ndescription: >\n  {description}\ntools:\n  - x\n---\nbody\n"
    elif frontmatter_style == "inline":
        fm = f"---\nname: {skill}\ndescription: {description}\n---\nbody\n"
    elif frontmatter_style == "none":
        fm = "no frontmatter here\n"
    else:
        fm = f"---\nname: {skill}\n---\nbody\n"
    (d / "SKILL.md").write_text(fm, encoding="utf-8")
    (d / "evals" / "trigger_eval.json").write_text(json.dumps(cases), encoding="utf-8")
    return d


class DescriptionTest(unittest.TestCase):
    def test_block_scalar_is_joined(self):
        with tempfile.TemporaryDirectory() as root:
            d = make_skill(root, "mcg-x", "s", "Ask about yoy sales. Use when the user asks about revenue.", [])
            self.assertEqual(
                rte.description_of(d / "SKILL.md"),
                "Ask about yoy sales. Use when the user asks about revenue.",
            )

    def test_inline_description(self):
        with tempfile.TemporaryDirectory() as root:
            d = make_skill(root, "mcg-x", "s", "one line", [], frontmatter_style="inline")
            self.assertEqual(rte.description_of(d / "SKILL.md"), "one line")

    def test_missing_description_is_none(self):
        with tempfile.TemporaryDirectory() as root:
            d = make_skill(root, "mcg-x", "s", "", [], frontmatter_style="no-description")
            self.assertIsNone(rte.description_of(d / "SKILL.md"))

    def test_no_frontmatter_is_none(self):
        with tempfile.TemporaryDirectory() as root:
            d = make_skill(root, "mcg-x", "s", "", [], frontmatter_style="none")
            self.assertIsNone(rte.description_of(d / "SKILL.md"))

    def test_block_stops_at_the_next_key(self):
        """A description must not swallow the keys below it."""
        with tempfile.TemporaryDirectory() as root:
            d = Path(root) / "p" / "skills" / "s"
            (d / "evals").mkdir(parents=True)
            (d / "SKILL.md").write_text(
                "---\nname: s\ndescription: >\n  first line\n  second line\ntools:\n  - mcp__a__b\n---\n",
                encoding="utf-8",
            )
            got = rte.description_of(d / "SKILL.md")
            self.assertEqual(got, "first line second line")
            self.assertNotIn("tools", got)


class StaticFindingsTest(unittest.TestCase):
    def test_clean_skill_reports_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-x", "s", "a description", [
                {"query": f"yes {i}", "should_trigger": True} for i in range(5)
            ] + [{"query": f"no {i}", "should_trigger": False} for i in range(3)])
            self.assertEqual(rte.static_findings(Path(root)), [])

    def test_thin_positive_set_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-x", "s", "d", [
                {"query": "a", "should_trigger": True},
            ] + [{"query": f"n{i}", "should_trigger": False} for i in range(3)])
            what = " ".join(w for _, w in rte.static_findings(Path(root)))
            self.assertIn("thin positive", what)

    def test_thin_negative_set_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-x", "s", "d", [
                {"query": f"y{i}", "should_trigger": True} for i in range(6)
            ])
            what = " ".join(w for _, w in rte.static_findings(Path(root)))
            self.assertIn("should-not-trigger", what)

    def test_same_query_on_both_sides_is_reported(self):
        """The case that makes an eval set contradictory: it cannot be satisfied."""
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-x", "s", "d", [
                {"query": "revenue", "should_trigger": True},
                {"query": "revenue", "should_trigger": False},
            ] + [{"query": f"y{i}", "should_trigger": True} for i in range(4)])
            what = " ".join(w for _, w in rte.static_findings(Path(root)))
            self.assertIn("both sides", what)

    def test_duplicate_query_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-x", "s", "d", [
                {"query": "same", "should_trigger": True},
                {"query": "same", "should_trigger": True},
            ] + [{"query": f"y{i}", "should_trigger": True} for i in range(4)]
              + [{"query": f"n{i}", "should_trigger": False} for i in range(3)])
            what = " ".join(w for _, w in rte.static_findings(Path(root)))
            self.assertIn("duplicate query", what)

    def test_invalid_json_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as root:
            d = Path(root) / "mcg-x" / "skills" / "s" / "evals"
            d.mkdir(parents=True)
            (d.parent / "SKILL.md").write_text("---\nname: s\ndescription: d\n---\n", encoding="utf-8")
            (d / "trigger_eval.json").write_text("{not json", encoding="utf-8")
            findings = rte.static_findings(Path(root))
            self.assertTrue(any("not valid JSON" in w for _, w in findings))

    def test_evals_without_a_skill_is_reported(self):
        """Renaming a skill leaves its old evals behind, and nothing else would notice."""
        with tempfile.TemporaryDirectory() as root:
            d = Path(root) / "mcg-x" / "skills" / "gone" / "evals"
            d.mkdir(parents=True)
            (d / "trigger_eval.json").write_text(json.dumps([{"query": "q", "should_trigger": True}]), encoding="utf-8")
            findings = rte.static_findings(Path(root))
            self.assertTrue(any("no SKILL.md" in w for _, w in findings))

    def test_discovery_finds_every_skill(self):
        with tempfile.TemporaryDirectory() as root:
            make_skill(root, "mcg-a", "one", "d1", [{"query": "q", "should_trigger": True}])
            make_skill(root, "mcg-b", "two", "d2", [{"query": "q", "should_trigger": True}])
            names = sorted(name for name, _, _, _ in rte.discover(Path(root)))
            self.assertEqual(names, ["one", "two"])


if __name__ == "__main__":
    unittest.main()
