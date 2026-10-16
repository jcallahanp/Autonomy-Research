#!/bin/bash
# seed NAME: value from stdin (or the terminal), merged into the SOPS file, never on a command line.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

decrypt() { SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" "$R/bin/sops" -d --extract "[\"$1\"]" "$SECRETS_FILE"; }

# test_seed_value_not_in_argv
rc=0
printf 'TEST-SECRET-9\n' | SUDO_USER=john-test "$R/bin/seed" ATTIO_API_KEY >"$T/out" 2>"$T/err" || rc=$?
[ "$rc" -eq 0 ] || fail "seed exit $rc: $(cat "$T/err")"
[ "$(decrypt ATTIO_API_KEY)" = "TEST-SECRET-9" ] || fail "ATTIO_API_KEY not seeded"
[ "$(decrypt GH_BOT_PAT)" = "TEST-TOKEN-PAT" ] || fail "seed dropped an existing key"
grep -q -- '--age age1testrecipientnotarealkey' "$T/argv.log" || fail "sops -e did not get the recipient"
grep -rq TEST-SECRET-9 "$T/argv.log" && fail "test_seed_value_not_in_argv: value in argv.log"
grep -q TEST-SECRET-9 "$T/out" "$T/err" && fail "value printed by seed"
grep -q 'seeded ATTIO_API_KEY' "$T/out" || fail "no confirmation line: $(cat "$T/out")"
[ "$(stat -c %a "$SECRETS_FILE")" = 600 ] || fail "secrets file mode $(stat -c %a "$SECRETS_FILE")"
left=$(find "$BROKER_STATE_DIR" -name 'seed.*' | wc -l)
[ "$left" -eq 0 ] || fail "temp files left in BROKER_STATE_DIR"

# Overwrite keeps one key; a value with spaces and quotes survives.
printf 'TEST "two" words\n' | "$R/bin/seed" ATTIO_API_KEY >/dev/null 2>&1 || fail "second seed failed"
[ "$(decrypt ATTIO_API_KEY)" = 'TEST "two" words' ] || fail "overwrite: $(decrypt ATTIO_API_KEY)"

# First seed with no secrets file yet.
rm -f "$SECRETS_FILE"
printf 'TEST-SECRET-FIRST\n' | "$R/bin/seed" HC_PING_URL >/dev/null 2>&1 || fail "first seed failed"
[ "$(decrypt HC_PING_URL)" = "TEST-SECRET-FIRST" ] || fail "first seed value"

expect 1 "empty value" bash -c "printf '\n' | '$R/bin/seed' EMPTY_ONE"
expect 1 "no input" bash -c "'$R/bin/seed' EMPTY_TWO </dev/null"
expect 2 "bad name" bash -c "printf 'x\n' | '$R/bin/seed' bad-name"
expect 2 "no name" "$R/bin/seed"
[ "$(decrypt HC_PING_URL)" = "TEST-SECRET-FIRST" ] || fail "a refused seed changed the file"

# Must run as BROKER_USER.
sed -i 's/^BROKER_USER=.*/BROKER_USER="nobody-test-broker"/' "$R/etc/engineer.conf"
expect 77 "seed as another user" bash -c "printf 'x\n' | '$R/bin/seed' OTHER_KEY"

# seed is not an agent-run job.
grep -q '^seed' "$REPO/engineer/etc/broker-jobs.txt" && fail "seed is in broker-jobs.txt"
exit 0
