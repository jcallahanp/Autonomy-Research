#!/bin/bash
# open-pr PROJECT BRANCH TITLE (body on stdin): Conventional Commit title, gh with GH_TOKEN in env.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

stub "$R" gh "[ \"\${GH_TOKEN:-}\" = TEST-TOKEN-PAT ] || { echo 'no GH_TOKEN' >&2; exit 9; }
cat > '$T/pr-body'
echo https://github.com/owner/demo/pull/12"

printf 'Audit: PASS\nline two\n' | SUDO_USER=engineer "$R/bin/agent-run" open-pr demo task/t1 "feat(api): add the t1 endpoint" \
  >"$T/out" 2>"$T/err" || fail "open-pr exit $?: $(cat "$T/err")"
line=$(grep '^gh ' "$T/argv.log" | tail -n 1)
case "$line" in *"pr create"*) ;; *) fail "gh not called with pr create: $line" ;; esac
case "$line" in *"--repo owner/demo"*) ;; *) fail "no --repo owner/demo: $line" ;; esac
case "$line" in *"--base main"*) ;; *) fail "no --base main: $line" ;; esac
case "$line" in *"--head task/t1"*) ;; *) fail "no --head task/t1: $line" ;; esac
case "$line" in *"--body-file -"*) ;; *) fail "body not from stdin: $line" ;; esac
[ "$(cat "$T/pr-body")" = "$(printf 'Audit: PASS\nline two')" ] || fail "PR body: $(cat "$T/pr-body")"
jq -e '.number == 12 and .url == "https://github.com/owner/demo/pull/12"' "$T/out" >/dev/null || fail "output: $(cat "$T/out")"
grep -q TEST-TOKEN-PAT "$T/argv.log" "$T/out" "$T/err" && fail "token in argv or output"

n=$(grep -c '^gh ' "$T/argv.log")
expect 65 "title without a type" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo task/t1 'update stuff'"
expect 65 "title too long" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo task/t1 'fix: $(printf 'x%.0s' $(seq 1 80))'"
expect 65 "title with a newline" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo task/t1 \$'fix: a\nb'"
expect 65 "head is the default branch" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo main 'fix: x'"
expect 65 "unknown project" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr nope task/t1 'fix: x'"
expect 65 "bad branch" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo -x 'fix: x'"
expect 0 "breaking-change title" bash -c "echo body | SUDO_USER=supervisor '$R/bin/agent-run' open-pr demo task/t1 'feat!: drop v1'"
[ "$(grep -c '^gh ' "$T/argv.log")" -eq $((n + 1)) ] || fail "gh called for a refused request"

stub "$R" gh "echo 'pull request create failed' >&2; exit 1"
expect 1 "gh failure is passed on" bash -c "echo body | SUDO_USER=engineer '$R/bin/agent-run' open-pr demo task/t1 'fix: x'"
exit 0
