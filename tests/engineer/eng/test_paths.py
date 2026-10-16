import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from eng import paths  # noqa: E402

RULES = paths.load(REPO / "engineer" / "templates" / "protected-paths.txt")


class MatchTest(unittest.TestCase):
    def test_double_star_spans_directories(self):
        self.assertTrue(paths.match("tests/a/b/c.py", "tests/**"))
        self.assertTrue(paths.match("conftest.py", "**/conftest.py"))
        self.assertTrue(paths.match("a/b/conftest.py", "**/conftest.py"))

    def test_single_star_does_not(self):
        self.assertTrue(paths.match("jest.config.js", "jest.config.*"))
        self.assertFalse(paths.match("a/jest.config.js", "jest.config.*"))
        self.assertFalse(paths.match("docs/plan/plan.approved.d/x", "docs/plan/plan.approved.*"))

    def test_literal_dots(self):
        self.assertFalse(paths.match("CLAUDExmd", "CLAUDE.md"))


class ProtectedTest(unittest.TestCase):
    def test_cases_from_plan(self):
        self.assertEqual(paths.protected("tests/acceptance/a.py", RULES, False), "tests/acceptance/**")
        self.assertIsNone(paths.protected("tests/unit/new_test.py", RULES, False))
        self.assertEqual(paths.protected("tests/unit/old.py", RULES, True), "tests/**")
        self.assertEqual(paths.protected("../other/x", RULES, False), "outside project")
        self.assertEqual(paths.protected("/etc/passwd", RULES, False), "outside project")
        self.assertEqual(paths.protected("pkg/conftest.py", RULES, False), "**/conftest.py")

    def test_normalises_first(self):
        self.assertEqual(paths.protected("src/../tests/acceptance/a.py", RULES, False), "tests/acceptance/**")
        self.assertEqual(paths.protected("./.github/workflows/ci.yml", RULES, False), ".github/**")
        self.assertEqual(paths.protected("src/../../x", RULES, False), "outside project")
        self.assertEqual(paths.protected("CLAUDE.md", RULES, False), "CLAUDE.md")
        self.assertIsNone(paths.protected("src/app.py", RULES, True))

    def test_load_sections(self):
        self.assertIn("tests/acceptance/**", RULES["always"])
        self.assertIn("**/*.spec.*", RULES["existing"])
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "p.txt"
            bad.write_text("x/**\n")
            with self.assertRaises(ValueError):
                paths.load(bad)
            bad.write_text("[sometimes]\nx/**\n")
            with self.assertRaises(ValueError):
                paths.load(bad)


if __name__ == "__main__":
    unittest.main()
