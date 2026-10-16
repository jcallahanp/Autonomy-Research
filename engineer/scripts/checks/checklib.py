"""Shared helpers for the checks: git run safely on a repo the checker owns, and repo-relative reads.

Every git call passes `-c core.hooksPath=/dev/null -c core.fsmonitor=`, `--no-ext-diff --no-textconv` where
diffs are made, and GIT_CONFIG_NOSYSTEM=1, so no hook, fsmonitor, diff driver or filter runs.
Blobs are read with `cat-file`, never checked out, so .gitattributes cannot hide or rewrite a file.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from eng import paths  # noqa: E402

SHA = re.compile(r"^[0-9a-f]{40}$")
SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=", "-c", "core.quotePath=false"]
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def git(gitdir, *args, text=True) -> str:
    """Run git on gitdir; raise CalledProcessError on failure."""
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_LITERAL_PATHSPECS="1")
    env.pop("GIT_DIR", None)
    r = subprocess.run(["git", *SAFE, f"--git-dir={gitdir}", *args], env=env, check=True,
                       capture_output=True, text=text)
    return r.stdout


def check_sha(value: str) -> str:
    """Return value when it is a 40-hex SHA, else raise ValueError (keeps options out of git argv)."""
    if not SHA.match(value or ""):
        raise ValueError(f"not a 40-hex SHA: {value[:50]!r}")
    return value


def changes(gitdir, base, head) -> list:
    """[(status letter, path)] between base and head, renames split into delete and add."""
    out = git(gitdir, "diff", "--name-status", "-z", "--no-renames", "--no-ext-diff", "--no-textconv",
              base, head, "--")
    parts = out.split("\0")
    return [(parts[i][0], parts[i + 1]) for i in range(0, len(parts) - 1, 2) if parts[i]]


def blob(gitdir, sha, path):
    """Text of path at sha, or None when absent or not a regular file."""
    entry = git(gitdir, "ls-tree", "-z", sha, "--", path).rstrip("\0")
    if not entry or not entry.startswith("100"):
        return None
    obj = entry.split()[2]
    return git(gitdir, "cat-file", "blob", obj, text=False).decode("utf-8", "replace")


def tree(gitdir, sha) -> list:
    """Regular files at sha as [(path, blob id)]; symlinks and submodules are left out."""
    out = []
    for entry in git(gitdir, "ls-tree", "-r", "-z", sha).split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode, kind, obj = meta.split()
        if kind == "blob" and mode in ("100644", "100755"):
            out.append((path, obj))
    return out


def extract(gitdir, sha, wanted, dest) -> list:
    """Write the regular files at sha whose path is in wanted (a set or a predicate) under dest."""
    dest = Path(dest)
    written = []
    for path, obj in tree(gitdir, sha):
        ok = wanted(path) if callable(wanted) else path in wanted
        clean = paths.normalise(path)
        if not ok or clean is None:
            continue
        target = dest / clean
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(gitdir, "cat-file", "blob", obj, text=False))
        written.append(clean)
    return written


def added_lines(gitdir, base, head):
    """Yield (path, line number, text) for every line added between base and head."""
    out = git(gitdir, "diff", "-U0", "--no-color", "--no-ext-diff", "--no-textconv", "--no-renames",
              "--src-prefix=a/", "--dst-prefix=b/", base, head, "--", text=False).decode("utf-8", "replace")
    path, n = None, 0
    for line in out.split("\n"):
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            m = HUNK.match(line)
            n = int(m.group(1)) if m else 0
        elif line.startswith("+") and path is not None:
            yield path, n, line[1:]
            n += 1


def rules(root=ROOT) -> dict:
    """The protected-path rules shipped in <root>/templates/protected-paths.txt."""
    return paths.load(Path(root) / "templates" / "protected-paths.txt")
