# Shared helpers for tests/engineer/<area>/test_*.sh. Source it; do not run it.
#   REPO        repo root (the working directory after sourcing)
#   T           a fresh temp dir, removed on exit
#   fail MSG    print "FAIL MSG" and make the test exit 1 at the end
#   mk_root DIR copy engineer/ to DIR/opt with a test engineer.conf; prints the root
#   stub ROOT NAME [BODY]  executable <root>/bin/NAME (or <root>/NAME) logging argv to DIR/argv.log
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$REPO"
export PYTHONDONTWRITEBYTECODE=1
_ENG_TMP=$(mktemp -d)
T=$_ENG_TMP
_eng_fails=0

fail() { echo "FAIL $*"; _eng_fails=$((_eng_fails+1)); }

_eng_exit() {
  local rc=$?
  [ "$_eng_fails" -eq 0 ] || rc=1
  rm -rf "$_ENG_TMP"
  exit "$rc"
}
trap _eng_exit EXIT

mk_root() { python3 "$REPO/tests/engineer/testlib.py" mk-root "$1"; }

stub() { python3 "$REPO/tests/engineer/testlib.py" stub "$@" >/dev/null; }
