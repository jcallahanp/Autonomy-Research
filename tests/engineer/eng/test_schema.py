import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from eng import schema  # noqa: E402

ROOT = REPO / "engineer"
NAMES = ("tasks event run-status profile integrations approval approval-record "
         "audit-verdict run-result").split()
SHA = "0123456789abcdef0123456789abcdef01234567"


class ValidatorTest(unittest.TestCase):
    S = {"type": "object", "required": ["a"], "additionalProperties": False,
         "properties": {"a": {"type": "string", "enum": ["x", "y"]},
                        "n": {"type": ["integer", "null"], "minimum": 1},
                        "s": {"type": "string", "pattern": "^[0-9a-f]{4}$", "minLength": 4, "maxLength": 4},
                        "l": {"type": "array", "maxItems": 2, "items": {"type": "boolean"}}}}

    def test_valid(self):
        self.assertEqual(schema.validate({"a": "x", "n": None, "s": "beef", "l": [True]}, self.S), [])

    def test_required_missing(self):
        errs = schema.validate({}, self.S)
        self.assertEqual(len(errs), 1)
        self.assertIn("a", errs[0])

    def test_enum_violation(self):
        self.assertEqual(len(schema.validate({"a": "z"}, self.S)), 1)

    def test_additional_properties_false(self):
        errs = schema.validate({"a": "x", "extra": 1}, self.S)
        self.assertEqual(len(errs), 1)
        self.assertIn("extra", errs[0])

    def test_pattern(self):
        self.assertEqual(len(schema.validate({"a": "x", "s": "BEEF"}, self.S)), 1)

    def test_type_minimum_items_maxitems(self):
        self.assertTrue(schema.validate({"a": "x", "n": 0}, self.S))
        self.assertTrue(schema.validate({"a": "x", "n": True}, self.S), "bool is not an integer")
        self.assertTrue(schema.validate({"a": "x", "l": [1]}, self.S))
        self.assertTrue(schema.validate({"a": "x", "l": [True, True, True]}, self.S))
        self.assertTrue(schema.validate([], self.S))

    def test_additional_properties_schema(self):
        s = {"type": "object", "additionalProperties": {"enum": ["public", "health"]}}
        self.assertEqual(schema.validate({"src/**": "public"}, s), [])
        self.assertEqual(len(schema.validate({"src/**": "secret"}, s)), 1)


class SchemaFilesTest(unittest.TestCase):
    def test_every_schema_file_is_valid_json_with_type_object(self):
        files = sorted((ROOT / "templates" / "schemas").glob("*.schema.json"))
        self.assertEqual(sorted(f.name.split(".")[0] for f in files), sorted(NAMES))
        for f in files:
            data = json.loads(f.read_text())
            self.assertEqual(data["type"], "object", f.name)
            self.assertNotIn("$ref", f.read_text(), f.name)

    def test_load(self):
        self.assertIn("verdict", schema.load(ROOT, "audit-verdict")["properties"])

    def test_samples(self):
        good = {
            "tasks": {"version": 1, "tasks": [{"id": "t1", "title": "Add login", "type": "feat", "status": "todo",
                                               "depends_on": [], "requirement_ids": ["R1"], "files": ["a.py"],
                                               "check": "pytest -q", "passes": False, "attempts": 0}]},
            "event": {"ts": "2026-10-16T22:00:00Z", "project": "demo", "event": "night_start", "detail": {}},
            "run-status": {"state": "blocked", "reason": "cycle", "started": "2026-10-16T22:00:00Z"},
            "audit-verdict": {"verdict": "PASS", "head_sha": SHA, "lines": ["ok"]},
            "run-result": {"profile": "check", "exit_code": 0, "timed_out": False, "is_error": False},
            "approval-record": {"ts": "2026-10-16T22:00:00Z", "item": "a1", "tier": "T1", "kind": "merge",
                                "ask": "Merge PR 7?", "answer": "yes", "from_id": 111111, "raw": "y",
                                "source": "telegram"},
            "profile": {"hard_gates": ["money", "delete_data", "store_submission"], "self_merge": True},
        }
        for name, inst in good.items():
            with self.subTest(name=name):
                self.assertEqual(schema.validate(inst, schema.load(ROOT, name)), [])
        bad = {"audit-verdict": {"verdict": "PASS", "head_sha": SHA[:39], "lines": []},
               "tasks": {"version": 1, "tasks": [dict(good["tasks"]["tasks"][0], type="wip")]},
               "event": {"ts": "2026-10-16T22:00:00Z", "project": "demo", "event": "party"}}
        for name, inst in bad.items():
            with self.subTest(name=name):
                self.assertTrue(schema.validate(inst, schema.load(ROOT, name)))
        lines = {"verdict": "FAIL", "head_sha": SHA, "lines": ["x"] * 16}
        self.assertTrue(schema.validate(lines, schema.load(ROOT, "audit-verdict")))

    def test_profile_promote_is_hold_or_t2(self):
        s = schema.load(ROOT, "profile")
        self.assertEqual(s["properties"]["promote"]["default"], "hold")
        base = {"hard_gates": ["money"], "self_merge": True}
        for ok in ("hold", "t2"):
            self.assertEqual(schema.validate(dict(base, promote=ok), s), [], ok)
        for bad in ("auto", "go", "", 1):
            self.assertTrue(schema.validate(dict(base, promote=bad), s), bad)

    def test_run_result_base_sha_and_structured_output(self):
        s = schema.load(ROOT, "run-result")
        ok = {"exit_code": 0, "is_error": False, "base_sha": SHA, "structured_output": {"verdict": "PASS"}}
        self.assertEqual(schema.validate(ok, s), [])
        self.assertEqual(schema.validate({"exit_code": 0, "is_error": False, "base_sha": None}, s), [])
        self.assertTrue(schema.validate(dict(ok, base_sha="main"), s))
        self.assertTrue(schema.validate(dict(ok, structured_output="PASS"), s))

    def test_event_digest_kind(self):
        ev = {"ts": "2026-10-16T11:30:00Z", "project": "demo", "event": "digest", "detail": {"items": [1, 2]}}
        self.assertEqual(schema.validate(ev, schema.load(ROOT, "event")), [])

    def test_profile_self_merge_defaults_true(self):
        self.assertIs(schema.load(ROOT, "profile")["properties"]["self_merge"]["default"], True)


if __name__ == "__main__":
    unittest.main()
