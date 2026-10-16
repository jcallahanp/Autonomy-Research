"""Shared helpers for tests/engineer/<area>/test_*.py and, through its CLI, lib.sh.

make_root(tmp) copies engineer/ to <tmp>/opt, rewrites etc/engineer.conf so every path points
inside <tmp>, sets BROKER_USER to the current effective user and returns the root. Under run.sh it copies
ENG_TEMPLATE instead: engineer/ copied and byte-compiled once per suite run, so the many Python processes a
test starts from its root do not each recompile the modules (nothing is ever written into the repo).
stub(root, name, body) writes an executable that logs its argv to <tmp>/argv.log.
CLI: python3 testlib.py mk-root DIR | stub ROOT NAME [BODY]
"""
import os
import pwd
import re
import shlex
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
ENGINEER = REPO / "engineer"
if str(ENGINEER / "scripts") not in sys.path:
    sys.path.insert(0, str(ENGINEER / "scripts"))

_LINE = re.compile(r'^([A-Z_][A-Z0-9_]*)=(?:"(.*)"|(.*))$')
_SUDO = re.compile(r"^sudo -n -u \S+ ")
_DIR_KEYS = ("STATE_DIR", "SPOOL_DIR", "RECORDS_DIR", "PROJECTS_DIR", "ETC_DIR", "BROKER_STATE_DIR")


def _map_value(value: str, tmp: Path, root: Path) -> str:
    value = _SUDO.sub("", value)
    if value == "/opt/engineer" or value.startswith("/opt/engineer/"):
        return str(root) + value[len("/opt/engineer"):]
    if value.startswith("/"):
        return str(tmp) + value
    return value


def current_user() -> str:
    return pwd.getpwuid(os.geteuid()).pw_name


def make_root(tmp) -> Path:
    """Copy engineer/ to <tmp>/opt with a test engineer.conf; return the root."""
    tmp = Path(tmp).resolve()
    root = tmp / "opt"
    template = Path(os.environ.get("ENG_TEMPLATE") or ENGINEER)
    ignore = None if template != ENGINEER else shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(template, root, symlinks=True, ignore=ignore)
    conf_path = root / "etc" / "engineer.conf"
    out, values = [], {}
    for line in conf_path.read_text().splitlines():
        m = _LINE.match(line.strip())
        if not m:
            out.append(line)
            continue
        key, value = m.group(1), m.group(2) if m.group(2) is not None else m.group(3)
        value = current_user() if key == "BROKER_USER" else _map_value(value, tmp, root)
        values[key] = value
        out.append(f'{key}="{value}"')
    conf_path.write_text("\n".join(out) + "\n")
    for key in _DIR_KEYS:
        if key in values:
            Path(values[key]).mkdir(parents=True, exist_ok=True)
    return root


def stub(root, name: str, body: str = "exit 0") -> Path:
    """Write <root>/bin/NAME (or <root>/NAME when NAME has a slash) logging argv to <tmp>/argv.log."""
    root = Path(root)
    path = root / name if "/" in name else root / "bin" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    log = shlex.quote(str(root.parent / "argv.log"))
    path.write_text(f'#!/bin/bash\nprintf \'%s\\n\' "$(basename "$0") $*" >> {log}\n{body}\n')
    path.chmod(0o755)
    return path


def argv_log(root) -> list:
    """Lines written by stubs under this root, oldest first."""
    log = Path(root).parent / "argv.log"
    return log.read_text().splitlines() if log.exists() else []


def _main(argv: list) -> int:
    if len(argv) == 2 and argv[0] == "mk-root":
        print(make_root(argv[1]))
        return 0
    if len(argv) in (3, 4) and argv[0] == "stub":
        print(stub(argv[1], argv[2], *argv[3:]))
        return 0
    print("usage: testlib.py mk-root DIR | stub ROOT NAME [BODY]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
