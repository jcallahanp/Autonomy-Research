#!/bin/bash
# agent-run: job allowlist, caller check, effective-user check, fixed PATH, clean env, log line.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

jobs="$R/scripts/broker/jobs"
[ -x "$jobs/tg-send" ] || stub "$R" scripts/broker/jobs/tg-send
printf 'probe\tengineer,supervisor\nghost\tengineer\n' >> "$R/etc/broker-jobs.txt"
cat > "$jobs/probe" <<'EOF'
#!/bin/bash
set -euo pipefail
echo "PATH=$PATH"
echo "CALLER=$AGENT_RUN_CALLER"
echo "LEAK=${LEAK_VAR:-none}"
echo "PWD=$PWD"
echo "ARGS=$*"
echo "STDIN=$(cat)"
exit 4
EOF
chmod 755 "$jobs/probe"

# Rows in the shipped allowlist.
for row in 'push-branch	engineer,supervisor' 'open-pr	engineer,supervisor' 'automerge	supervisor' \
  'api-call	engineer,supervisor' 'hc-ping	supervisor' 'tg-send	supervisor' 'tg-poll	supervisor'; do
  grep -qxF "$row" "$REPO/engineer/etc/broker-jobs.txt" || fail "broker-jobs.txt lacks row: $row"
done

expect 64 "unknown job" as engineer no-such-job
expect 64 "bad job name" as engineer ../probe
expect 64 "upper-case job name" as engineer Probe
expect 64 "listed job with no file" as engineer ghost
expect 64 "no job" as engineer
expect 77 "engineer calling tg-send" as engineer tg-send
expect 77 "engineer calling automerge" as engineer automerge demo 1
expect 77 "no SUDO_USER (caller is the broker itself)" env -u SUDO_USER "$R/bin/agent-run" probe

# Effective user must be BROKER_USER.
cp "$R/etc/engineer.conf" "$T/conf.bak"
sed -i 's/^BROKER_USER=.*/BROKER_USER="nobody-test-broker"/' "$R/etc/engineer.conf"
expect 77 "effective user is not BROKER_USER" as engineer probe
cp "$T/conf.bak" "$R/etc/engineer.conf"

# A good call: fixed PATH, caller exported, caller env dropped, stdin passed, job exit code kept.
rc=0
printf 'from-stdin' | LEAK_VAR=leaked SUDO_USER=engineer "$R/bin/agent-run" probe SECRET-ARG-1 >"$T/out" 2>&1 || rc=$?
[ "$rc" -eq 4 ] || fail "probe exit $rc, want 4: $(cat "$T/out")"
grep -qxF "PATH=$R/bin:/usr/bin:/bin" "$T/out" || fail "job PATH: $(grep PATH= "$T/out")"
grep -qxF "CALLER=engineer" "$T/out" || fail "AGENT_RUN_CALLER not engineer"
grep -qxF "LEAK=none" "$T/out" || fail "caller environment reached the job"
grep -qxF "ARGS=SECRET-ARG-1" "$T/out" || fail "args not passed"
grep -qxF "STDIN=from-stdin" "$T/out" || fail "stdin not passed"
grep -qxF "PWD=$BROKER_STATE_DIR" "$T/out" || fail "job cwd: $(grep PWD= "$T/out")"

log="$BROKER_STATE_DIR/agent-run.log"
[ -f "$log" ] || fail "no agent-run.log"
last=$(tail -n 1 "$log")
[[ "$last" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}Z\ engineer\ probe\ 4$ ]] || fail "log line: $last"
grep -q SECRET-ARG-1 "$log" && fail "arguments reached agent-run.log"
grep -q ' no-such-job 64$' "$log" || fail "refusal not logged"
exit 0
