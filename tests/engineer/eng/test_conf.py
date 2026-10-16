import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
sys.path.insert(0, str(REPO / "tests" / "engineer"))

from eng import conf  # noqa: E402
import testlib  # noqa: E402

KEYS = ("STATE_DIR SPOOL_DIR RECORDS_DIR KILL_SWITCH PROJECTS_DIR ETC_DIR MANAGED_SETTINGS CHROME_PROFILE "
        "DISPLAY NOVNC_PORT PROXY_PORT BROKER_USER SECRETS_FILE AGE_KEY_FILE AGE_RECIPIENT_FILE "
        "BROKER_STATE_DIR TZ_NAME BOT_EMAIL TELEGRAM_API GITHUB_URL RUN_TASK AGENT_RUN AUDIT_CMD").split()


def write_conf(tmp, text):
    root = Path(tmp)
    (root / "etc").mkdir()
    (root / "etc" / "engineer.conf").write_text(text)
    return root


class ConfTest(unittest.TestCase):
    def test_parses_quoted_and_plain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_conf(tmp, '# comment\n\nA=/x/y\nB="sudo -n -u e /opt/b"\n  C=:99  \nD=""\n')
            self.assertEqual(conf.load(root), {"A": "/x/y", "B": "sudo -n -u e /opt/b", "C": ":99", "D": ""})

    def test_rejects_dollar_expansion_line(self):
        for bad in ("A=$HOME", 'A="$HOME"', "A=`id`", "A=b c", "A=~/x", "a=b", "A=b;c", "just text"):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as tmp:
                root = write_conf(tmp, bad + "\n")
                with self.assertRaises(ValueError):
                    conf.load(root)

    def test_real_conf_has_every_key(self):
        values = conf.load(REPO / "engineer")
        self.assertEqual(sorted(values), sorted(KEYS))
        self.assertEqual(values["STATE_DIR"], "/var/lib/engineer")
        self.assertEqual(values["RUN_TASK"], "sudo -n -u engineer /opt/engineer/bin/run-task")

    def test_bash_and_python_agree(self):
        path = REPO / "engineer" / "etc" / "engineer.conf"
        script = 'set -euo pipefail; . "$1"; shift; for k in "$@"; do printf "%s=%s\\n" "$k" "${!k}"; done'
        out = subprocess.run(["bash", "-c", script, "x", str(path), *KEYS],
                             capture_output=True, text=True, check=True, env={"PATH": "/usr/bin:/bin"}).stdout
        from_bash = dict(line.split("=", 1) for line in out.splitlines())
        self.assertEqual(from_bash, conf.load(REPO / "engineer"))

    def test_make_root_points_inside_tmp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = testlib.make_root(tmp)
            values = conf.load(root)
            tmp = str(Path(tmp).resolve())
            for key in ("STATE_DIR", "KILL_SWITCH", "ETC_DIR", "SECRETS_FILE", "MANAGED_SETTINGS"):
                self.assertTrue(values[key].startswith(tmp + "/"), key)
            self.assertEqual(values["AUDIT_CMD"], f"{root}/scripts/checks/audit.sh")
            self.assertEqual(values["AGENT_RUN"], f"{root}/bin/agent-run")
            self.assertEqual(values["BROKER_USER"], testlib.current_user())
            self.assertTrue(Path(values["STATE_DIR"]).is_dir())


if __name__ == "__main__":
    unittest.main()
