#!/bin/bash
set -euo pipefail
# Task 12: the setup-day guide for John (docs/engineer/setup-day.md) and its builder appendix.
# Runs standalone or under tests/engineer/run.sh.
cd "$(dirname "$(readlink -f "$0")")/../../.."
fails=0
fail() { echo "FAIL docs: $*"; fails=$((fails+1)); }

g=docs/engineer/setup-day.md
a=docs/engineer/setup-day-appendix.md
plan=docs/plans/2026-10-16-engineer-stage-1.md
[ -f "$g" ] || { echo "FAIL docs: $g missing"; exit 1; }
[ -f "$a" ] || fail "$a missing"
for f in "$g" "$a"; do
  [ -f "$f" ] || continue
  n=$(wc -l < "$f"); [ "$n" -le 250 ] || fail "$f has $n lines (limit 250)"
done

for h in '## Accounts and costs' '## Before the day' '## The one sitting' '## Setup-day tests' \
         '## If something goes wrong' '## Words used here'; do
  grep -qxF "$h" "$g" || fail "$g lacks heading '$h'"
done

for k in '$48' 'claude auth login' 'setup-token' '/opt/engineer/bin/seed' '--lock' '--unlock' 'novnc.' \
         'Tailscale' 'Mac mini' 'browser-login' 'bootstrap.sh' 'doctor.sh' '/etc/engineer/projects.txt' \
         'sudo -u supervisor /opt/engineer/scripts/checks/verify-all.sh' 'sudo touch /var/lib/engineer/STOP' \
         'engineer-remote-control' 'engineer-channels' 'tests/acceptance' 'check the price on the day' \
         'GH_BOT_PAT' 'TG_SUPERVISOR_TOKEN' 'TG_JOHN_USER_ID' 'TG_JOHN_CHAT_ID' 'HC_PING_URL' \
         'ATTIO_API_KEY' 'N8N_API_KEY' 'N8N_BASE_URL' 'age-keygen'; do
  grep -qF -- "$k" "$g" || fail "$g does not mention '$k'"
done

# Builder appendix: the items gathered from the implementers.
if [ -f "$a" ]; then
  for k in 'release-pins.txt' 'TO-PIN' 'apt-repos.txt' 'safe.directory' 'GIT_CONFIG_COUNT' 'http_connect' \
           'ignore-hosts' 'sync-mirror' 'RECORDS_DIR' 'MIRROR_DIR' 'approve-plan' 'SP07' 'SP16' 'SP64' \
           'SP83' 'SP85' 'SP86' 'gitleaks' 'osv-scanner' 'semgrep' '--metrics=off' 'Bun'; do
    grep -qF -- "$k" "$a" || fail "$a does not mention '$k'"
  done
fi

# Every spike in the plan's "Deferred to setup day" table appears in the guide's test table.
ids=$(awk '/^## Deferred to setup day/{on=1;next} /^## /{on=0} on' "$plan" | grep -oE 'SP[0-9]+' | sort -u)
[ -n "$ids" ] || fail "no spike ids found in $plan"
tests=$(awk '/^## Setup-day tests/{on=1;next} /^## /{on=0} on' "$g")
for s in $ids; do grep -qw "$s" <<< "$tests" || fail "$s missing from '## Setup-day tests'"; done

# Prices: only figures recorded in the repo (research/findings/engineer-host.md, the plan).
for p in $(grep -oE '\$[0-9][0-9.,]*' "$g" "$a" 2>/dev/null | sed 's/^[^$]*//; s/[.,]$//' | sort -u); do
  case "$p" in '$48'|'$0.06'|'$899'|'$9.60') ;; *) fail "price $p is not one recorded in the repo" ;; esac
done

# Every /opt/engineer path named exists in engineer/.
for f in "$g" "$a"; do
  [ -f "$f" ] || continue
  for p in $(grep -oE '/opt/engineer/[A-Za-z0-9_./-]+' "$f" | sed 's/[.]$//' | sort -u); do
    [ -e "engineer/${p#/opt/engineer/}" ] || fail "$f names $p, which is not in engineer/"
  done
done

# No secret-shaped text (Task 2 pattern; written so it does not match itself).
secret='(sk[-]ant-|ghp[_][A-Za-z0-9]{20,}|github[_]pat_|xox[baprs]-|AKIA[0-9A-Z]{16}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|BEGIN [A-Z ]*PRIVATE KEY)'
for f in "$g" "$a"; do [ -f "$f" ] && grep -qE "$secret" "$f" && fail "$f has secret-shaped text"; done

# Relative links resolve.
for f in "$g" "$a" engineer/README.md; do
  [ -f "$f" ] || continue
  d=$(dirname "$f")
  for l in $(grep -oE '\]\(([^)#:]+)(#[^)]*)?\)' "$f" | sed -E 's/^\]\(([^)#]*).*/\1/'); do
    [ -e "$d/$l" ] || fail "$f links to missing $l"
  done
done

grep -qF '](../docs/engineer/setup-day.md)' engineer/README.md || fail "engineer/README.md does not link the guide"

# Fix round F3 (review R3): every step works in order with the code as it is.
sitting=$(awk '/^## The one sitting/{on=1;next} /^## /{on=0} on' "$g")
before=$(awk '/^## Before the day/{on=1;next} /^## /{on=0} on' "$g")
grep -q 'age-keygen -o' <<< "$sitting" && fail "the guide makes the age key; --install already does (R3-2)"
ln_of() { grep -nF -- "$1" <<< "$sitting" | head -1 | cut -d: -f1; }
b=$(ln_of 'bootstrap.sh'); l=$(ln_of 'claude auth login')
[ -n "$b" ] && [ -n "$l" ] && [ "$b" -lt "$l" ] || fail "bootstrap.sh must come before claude auth login (R3-3)"
grep -qF 'sudo -iu engineer' <<< "$sitting" || fail "no fresh login shell for engineer (R3-3)"
grep -qF 'new-project' <<< "$before" || fail "engineer-scratch is not made from the skeleton before the day (R3-9)"
grep -qF 'classic' "$g" && grep -qF '`repo`' "$g" || fail "guide lacks the classic token with repo scope (R3-10)"
for f in research/blueprint/setup.md research/blueprint/stack.md "$a" "$plan"; do
  grep -qi 'fine-grained PAT\|fine-grained token (Contents' "$f" && fail "$f still names a fine-grained PAT (R3-10)"
done
grep -qF "John's classic" "$a" && fail "$a: the token is the bot's, not John's (R3-10)"
grep -qF 'setup-root.sh --allow' <<< "$sitting" || fail "the n8n host is never added with --allow (R3-13)"
grep -qF 'browser-allowlist.txt' "$g" || fail "the n8n host never reaches the browser allowlist (R3-13)"
grep -qF '/etc/cloudflared/config.yml' "$g" || fail "cloudflared config is not written to /etc/cloudflared (R3-13)"
grep -qF 'claude.ai/code' "$g" && grep -qF 'claude.ai/code' "$a" || fail "no push route for builder changes (R3-11)"
for claim in 'rootless Podman, a dummy `CANARY`' 'it also makes the builder'"'"'s checkout'; do
  grep -qF "$claim" research/blueprint/setup.md && fail "setup.md claims --install does: $claim (R3-11)"
done
grep -q '^| `gh`, `gcloud`, `cloudflared`, Lynis | root |' research/blueprint/stack.md && fail "stack.md: gcloud/Lynis by --install (R3-11)"
grep -qF 'excludedCommands' "$a" || fail "appendix lacks the sandbox broker-call check (R1-7)"

[ "$fails" -eq 0 ] || { echo "test_setup_day.sh: $fails failure(s)"; exit 1; }
echo "test_setup_day.sh: ok"
