"""hooks.json registration and its managed-settings twin."""
import json
import re
import shutil
import subprocess
import unittest

from hookfix import testlib

HOOKS = testlib.ENGINEER / "plugin" / "hooks" / "hooks.json"
MANAGED = testlib.ENGINEER / "templates" / "managed-hooks.json"
PLUGIN_VAR = "${CLAUDE_PLUGIN_ROOT}"
CMD = re.compile(r'^python3 -I "(?P<path>[^"]+)"$')
EXPECTED = {  # event: (matcher or None, script, timeout seconds)
    "SessionStart": ("startup|resume|compact", "session_start.py", None),
    "PreToolUse": ("*", "pre_tool_use.py", 10),
    "PostToolUse": ("Edit|Write|MultiEdit", "post_tool_use.py", 10),
    "Stop": (None, "stop_gate.py", 1200),
    "TaskCompleted": (None, "stop_gate.py", 1200),
    "StopFailure": (None, "event_tap.py", 5),
    "Notification": (None, "event_tap.py", 5),
}


class RegistrationTest(unittest.TestCase):
    def setUp(self):
        self.hooks = json.loads(HOOKS.read_text())

    def commands(self, obj):
        for groups in obj["hooks"].values():
            for group in groups:
                for h in group["hooks"]:
                    yield h

    def test_events_matchers_timeouts(self):
        self.assertEqual(set(self.hooks["hooks"]), set(EXPECTED))
        for event, (matcher, script, timeout) in EXPECTED.items():
            with self.subTest(event=event):
                (group,) = self.hooks["hooks"][event]
                self.assertEqual(group.get("matcher"), matcher)
                (h,) = group["hooks"]
                self.assertEqual(h["type"], "command")
                self.assertEqual(h["command"], f'python3 -I "{PLUGIN_VAR}/hooks/{script}"')
                self.assertEqual(h.get("timeout"), timeout)

    def test_every_command_names_an_existing_file(self):
        for h in self.commands(self.hooks):
            m = CMD.match(h["command"])
            self.assertIsNotNone(m, h["command"])
            path = m.group("path").replace(PLUGIN_VAR, str(testlib.ENGINEER / "plugin"))
            self.assertTrue(testlib.Path(path).is_file(), path)

    def test_managed_equals_plugin_after_substitution(self):
        text = HOOKS.read_text().replace(PLUGIN_VAR, "/opt/engineer/plugin")
        self.assertEqual(json.loads(MANAGED.read_text()), json.loads(text))

    def test_claude_plugin_validate(self):
        if shutil.which("claude") is None:
            self.skipTest("claude not on PATH")
        r = subprocess.run(["claude", "plugin", "validate", str(testlib.ENGINEER / "plugin"), "--strict"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
