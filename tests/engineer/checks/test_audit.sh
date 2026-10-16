#!/bin/bash
# audit.sh against a temp project repo; scanners are stubs in <root>/bin.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

root=$(mk_root "$T")
. "$root/etc/engineer.conf"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.invalid GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.invalid
printf 'demo owner/demo main self_merge=on scratch=no owner_login=octo\n' > "$ETC_DIR/projects.txt"
stub "$root" gitleaks 'while [ $# -gt 0 ]; do [ "$1" = --report-path ] && echo "[]" > "$2"; shift; done'
stub "$root" osv-scanner 'echo "{\"results\": []}"'
stub "$root" semgrep 'echo "{\"results\": [], \"errors\": []}"'

p="$PROJECTS_DIR/demo"
git init -q -b main "$p"
g() { git -C "$p" "$@"; }
mkdir -p "$p/src" "$p/tests"
echo 'x = 1' > "$p/src/a.py"
printf 'def test_a():\n    assert 1\n' > "$p/tests/test_a.py"
g add -A; g commit -qm base
g checkout -qb task/t1
echo 'x = 2' > "$p/src/a.py"; g commit -qam change

set_result() {  # set_result SHA TAIL [EXIT]
  mkdir -p "$STATE_DIR/checks/demo"
  python3 - "$STATE_DIR/checks/demo/t1.json" "$1" "$2" "${3:-0}" <<'PY'
import json, sys
path, sha, tail, code = sys.argv[1:]
json.dump({"exit_code": int(code), "is_error": code != "0", "head_sha": sha, "output_tail": tail}, open(path, "w"))
PY
}
audit() { rc=0; out=$("$root/scripts/checks/audit.sh" demo t1 2>"$T/err") || rc=$?; }
field() { python3 -c 'import json,sys; v=json.loads(sys.argv[1])[sys.argv[2]]; print(v if isinstance(v, str) else "\n".join(v))' "$out" "$1"; }

# clean branch, 3 tests run -> PASS
head=$(g rev-parse HEAD)
set_result "$head" $'ok\nTESTS_RUN=3'
audit
[ "$rc" -eq 0 ] || fail "clean: exit $rc: $out $(cat "$T/err")"
[ "$(field verdict)" = PASS ] || fail "clean: verdict: $out"
[ "$(field head_sha)" = "$head" ] || fail "clean: head_sha: $out"
python3 - "$root" "$out" <<'PY' || fail "clean: output does not validate against audit-verdict"
import json, sys
sys.path.insert(0, sys.argv[1] + "/scripts")
from eng import schema
errs = schema.validate(json.loads(sys.argv[2]), schema.load(sys.argv[1], "audit-verdict"))
sys.exit(1 if errs else 0)
PY

# stale check result SHA -> FAIL
set_result "$(printf 'b%.0s' {1..40})" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] && [ "$(field verdict)" = FAIL ] || fail "stale sha: exit $rc: $out"
field lines | grep -q head_sha || fail "stale sha: no head_sha line: $out"

# zero tests -> FAIL
set_result "$head" 'TESTS_RUN=0'
audit
[ "$rc" -eq 1 ] || fail "zero tests: exit $rc: $out"

# failing check -> FAIL
set_result "$head" 'TESTS_RUN=3' 1
audit
[ "$rc" -eq 1 ] || fail "check exit 1: exit $rc: $out"

# added skip marker -> FAIL
printf 'import pytest\n@pytest.mark.skip\ndef test_b():\n    assert 1\n' > "$p/tests/test_b.py"
g add -A; g commit -qm skip
set_result "$(g rev-parse HEAD)" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] || fail "skip marker: exit $rc: $out"
field lines | grep -q skip_marker || fail "skip marker: no line: $out"
g reset -q --hard HEAD~1

# fake token shaped like a GitHub classic token -> FAIL, value never printed
tok="gh""p_TESTTOKEN$(printf '0%.0s' {1..27})"
echo "TOKEN = '$tok'" > "$p/src/conf.py"
g add -A; g commit -qm token
set_result "$(g rev-parse HEAD)" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] || fail "token: exit $rc: $out"
field lines | grep -q 'src/conf.py:1 github_token' || fail "token: no line: $out"
case "$out$(cat "$T/err")" in *TESTTOKEN*) fail "token: value printed" ;; esac
g reset -q --hard HEAD~1

# protected path -> FAIL
mkdir -p "$p/.github/workflows"; echo 'on: push' > "$p/.github/workflows/ci.yml"
g add -A; g commit -qm ci
set_result "$(g rev-parse HEAD)" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] || fail "protected: exit $rc: $out"
field lines | grep -q '.github/workflows/ci.yml' || fail "protected: no line: $out"
g reset -q --hard HEAD~1

# integrations.yaml changed without .env.example -> FAIL
mkdir -p "$p/docs/plan"
printf 'services:\n  - id: attio\n    env_vars: [ATTIO_API_KEY]\n' > "$p/docs/plan/integrations.yaml"
g add -A; g commit -qm integ
set_result "$(g rev-parse HEAD)" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] || fail "integrations: exit $rc: $out"
field lines | grep -q 'missing: ATTIO_API_KEY' || fail "integrations: no line: $out"
g reset -q --hard HEAD~1

# scanner finding (stub gitleaks reports one) -> FAIL
stub "$root" gitleaks 'while [ $# -gt 0 ]; do [ "$1" = --report-path ] && echo "[{\"File\": \"src/a.py\", \"StartLine\": 1, \"RuleID\": \"generic-api-key\"}]" > "$2"; shift; done'
set_result "$head" 'TESTS_RUN=3'
audit
[ "$rc" -eq 1 ] || fail "gitleaks finding: exit $rc: $out"
stub "$root" gitleaks 'while [ $# -gt 0 ]; do [ "$1" = --report-path ] && echo "[]" > "$2"; shift; done'

# bad arguments -> exit 2
rc=0; "$root/scripts/checks/audit.sh" ../demo t1 >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "bad project: exit $rc"
rc=0; "$root/scripts/checks/audit.sh" demo '--upload-pack=x' >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "bad task id: exit $rc"
rc=0; "$root/scripts/checks/audit.sh" nope t1 >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 2 ] || fail "unknown project: exit $rc"

# test_audit_ignores_repo_config: the engineer-writable clone carries traps; none may run.
mkdir -p "$T/evil-hooks"
for h in pre-commit post-checkout post-merge reference-transaction pre-auto-gc post-rewrite push-to-checkout; do
  printf '#!/bin/sh\ntouch %s/pwned\n' "$T" > "$T/evil-hooks/$h"; chmod +x "$T/evil-hooks/$h"
  cp "$T/evil-hooks/$h" "$p/.git/hooks/$h"
done
g config core.fsmonitor "touch $T/pwned; false"
g status >/dev/null 2>&1 || true
[ -e "$T/pwned" ] || fail "repo config: control failed, fsmonitor trap did not fire on a plain git status"
rm -f "$T/pwned"
g config core.hooksPath "$T/evil-hooks"
g config uploadpack.packObjectsHook "touch $T/pwned"
g config core.sshCommand "touch $T/pwned"
echo 'x = 5' > "$p/src/a.py"; g commit -qam trap --no-verify 2>/dev/null || true
rm -f "$T/pwned"
set_result "$(g rev-parse HEAD)" 'TESTS_RUN=3'
audit
[ ! -e "$T/pwned" ] || fail "test_audit_ignores_repo_config: a trap in the project's git config ran"
[ "$rc" -eq 0 ] || fail "repo config: exit $rc: $out $(cat "$T/err")"
