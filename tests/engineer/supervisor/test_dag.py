import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))

from supervisor import dag  # noqa: E402


def task(tid, deps=(), status="todo"):
    return {"id": tid, "title": f"task {tid}", "type": "feat", "status": status, "depends_on": list(deps),
            "requirement_ids": [], "files": [], "check": "true", "passes": False, "attempts": 0}


def write(tmp, tasks):
    p = Path(tmp) / "tasks.json"
    p.write_text(json.dumps({"version": 1, "tasks": tasks}))
    return p


class DagTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_load_valid(self):
        tasks = dag.load(write(self.tmp.name, [task("a"), task("b", ["a"])]))
        self.assertEqual([t["id"] for t in tasks], ["a", "b"])

    def test_load_invalid_raises_listing_errors(self):
        bad = task("a")
        del bad["check"]
        with self.assertRaises(ValueError) as cm:
            dag.load(write(self.tmp.name, [bad]))
        self.assertIn("check", str(cm.exception))

    def test_load_not_json_raises(self):
        p = Path(self.tmp.name) / "tasks.json"
        p.write_text("{not json")
        with self.assertRaises(ValueError):
            dag.load(p)

    def test_load_duplicate_id_raises(self):
        with self.assertRaises(ValueError):
            dag.load(write(self.tmp.name, [task("a"), task("a")]))

    def test_dag_ready_respects_depends_on(self):
        tasks = [task("a"), task("b", ["a"]), task("c"), task("d", ["b", "c"])]
        self.assertEqual(dag.ready(tasks, set(), set(), set()), ["a", "c"])
        self.assertEqual(dag.ready(tasks, {"a"}, set(), set()), ["b", "c"])
        self.assertEqual(dag.ready(tasks, {"a", "c"}, set(), {"b"}), [])
        self.assertEqual(dag.ready(tasks, {"a", "b", "c"}, set(), set()), ["d"])
        self.assertEqual(dag.ready(tasks, {"a"}, {"c"}, set()), ["b"])

    def test_dag_cycle_detected(self):
        tasks = [task("a", ["c"]), task("b", ["a"]), task("c", ["b"]), task("d")]
        cyc = dag.find_cycle(tasks)
        self.assertIsNotNone(cyc)
        self.assertEqual(set(cyc[:-1]), {"a", "b", "c"})
        self.assertEqual(cyc[0], cyc[-1])
        self.assertIsNone(dag.find_cycle([task("a"), task("b", ["a"])]))

    def test_self_dependency_is_a_cycle(self):
        self.assertIsNotNone(dag.find_cycle([task("a", ["a"])]))

    def test_dag_unknown_dependency_raises(self):
        tasks = [task("a"), task("b", ["zz"])]
        with self.assertRaises(ValueError) as cm:
            dag.ready(tasks, set(), set(), set())
        self.assertIn("zz", str(cm.exception))
        with self.assertRaises(ValueError):
            dag.find_cycle(tasks)


if __name__ == "__main__":
    unittest.main()
