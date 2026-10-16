"""post_tool_use.py: Mermaid files must be flowchart, graph or sequenceDiagram, never C4."""
import unittest

from hookfix import HookCase


class PostToolUseTest(HookCase):
    def post(self, rel, text, tool="Write"):
        path = self.write(self.proj / rel, text)
        ev = self.event(tool, {"file_path": str(path), "content": text}, name="PostToolUse")
        ev["tool_response"] = {"filePath": str(path), "success": True}
        return self.run_hook("post_tool_use.py", ev)

    def test_c4_denied(self):
        self.assertDenied(self.post("docs/map/a.mmd", "C4Context\n  title x\n"), "C4")
        self.assertDenied(self.post("docs/map/b.mmd", "flowchart LR %% C4Container\n"), "C4")

    def test_other_diagram_types_denied(self):
        self.assertDenied(self.post("docs/map/c.mmd", "classDiagram\n  A <|-- B\n"), "flowchart")
        self.assertDenied(self.post("docs/map/e.mmd", "\n%% only a comment\n"), "flowchart")

    def test_allowed_diagrams(self):
        self.assertAllowed(self.post("docs/map/a.mmd", "flowchart LR\n  a --> b\n"))
        self.assertAllowed(self.post("docs/map/b.mmd", "%% comment\n\ngraph TD\n  a --> b\n"))
        self.assertAllowed(self.post("docs/map/c.mmd", "sequenceDiagram\n  a->>b: hi\n", tool="Edit"))
        self.assertAllowed(self.post("docs/map/d.mmd", "---\ntitle: x\n---\nflowchart TB\n  a\n"))

    def test_non_mermaid_ignored(self):
        self.assertAllowed(self.post("src/a.py", "C4Context\n"))
        self.assertAllowed(self.run_hook("post_tool_use.py", self.event("Bash", {"command": "ls"},
                                                                         name="PostToolUse")))


if __name__ == "__main__":
    unittest.main()
