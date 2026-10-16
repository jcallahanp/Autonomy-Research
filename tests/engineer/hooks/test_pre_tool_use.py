"""pre_tool_use.py: guard order, kill switch, fail-closed errors, vendor CLIs and deploys."""
import unittest
from pathlib import Path

from hookfix import HookCase


class PreToolUseTest(HookCase):
    def test_plain_command_allowed(self):
        self.assertAllowed(self.bash("ls -la"))
        self.assertAllowed(self.pre("Read", {"file_path": str(self.proj / "src/a.py")}))

    def test_kill_switch_denies_everything(self):
        Path(self.conf["KILL_SWITCH"]).write_text("stop\n")
        self.assertDenied(self.pre("Read", {"file_path": str(self.proj / "src/a.py")}), "kill switch")
        self.assertDenied(self.bash("ls"), "kill switch")
        self.assertDenied(self.pre("mcp__x__y", {}), "kill switch")

    def test_guard_raising_fails_closed(self):
        guard = self.root / "plugin/hooks/guards/vendor.py"
        self.addCleanup(guard.write_text, guard.read_text())
        guard.write_text("def check(event, ctx):\n    raise RuntimeError('boom')\n")
        self.assertDenied(self.bash("ls"), "guard error: RuntimeError")

    def test_bad_input_fails_closed(self):
        r = self.run_hook("pre_tool_use.py", None, raw="{not json")
        self.assertDenied(r, "guard error")
        self.assertDenied(self.run_hook("pre_tool_use.py", None, raw=""), "guard error")
        self.assertDenied(self.run_hook("pre_tool_use.py", None, raw="[1, 2]"), "guard error")

    def test_vendor_cli_denied(self):
        cmds = ("codex exec x", "gemini -p hi", "env codex exec x", "ls && aider --yes",
                "/usr/local/bin/llm 'hi'", "npx -y x | openai api", "agy run", "timeout 9 codex x")
        for cmd, r in self.many(self.bash, cmds):
            with self.subTest(cmd=cmd):
                self.assertDenied(r, "vendor")

    def test_vendor_word_in_argument_allowed(self):
        self.assertAllowed(self.bash("grep -rn codex docs/"))
        self.assertAllowed(self.bash("echo llm"))

    def test_deploy_denied(self):
        cmds = ("vercel --prod", "npx vercel deploy --prod", "wrangler deploy --env production",
                "wrangler deploy --env=production", "gcloud run services update-traffic svc --to-latest",
                "supabase db push", "bash -c 'vercel --prod'")
        for cmd, r in self.many(self.bash, cmds):
            with self.subTest(cmd=cmd):
                self.assertDenied(r, "deploy")

    def test_preview_deploy_allowed(self):
        self.assertAllowed(self.bash("vercel deploy"))
        self.assertAllowed(self.bash("wrangler deploy --env staging"))

    def test_first_guard_reason_wins(self):
        Path(self.conf["KILL_SWITCH"]).write_text("stop\n")
        r = self.bash("git push")
        self.assertDenied(r, "kill switch")
        self.assertNotIn("push", r.stderr)


if __name__ == "__main__":
    unittest.main()
