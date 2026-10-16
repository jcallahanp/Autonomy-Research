# Self-improvement round 1, changes 9-10: the self-improve skill that writes down the loop, and
# the one-fact path when no search or fetch tool exists.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files only.

s=plugin/skills/self-improve/SKILL.md
if [ -f "$s" ]; then
  [ "$(fm "$s" name)" = self-improve ] || fail self-improve "$s name is not self-improve"
  n=$(wc -l < "$s"); [ "$n" -lt 150 ] || fail self-improve "$s has $n lines (limit 149)"
  d=$(fm "$s" description)
  for t in 'improve yourself' 'self-improve' 'self-improvement round' 'Use when'; do
    echo "$d" | grep -qiF -- "$t" || fail self-improve "self-improve description lacks '$t'"
  done
  for t in 'tests/frozen-exam.sha256' 'tests/check.sh' '`tail`' 'reported separately' 'research' 'verifier' \
           '20 citations' 'keep rule' '--runs 3' '5 runs' '2 rounds' 'docs/self-improvement/' 'pull request' \
           'never edit' 'graders' 'mocks' \
           'claude plugin eval plugin --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3 --allow-tools Write Edit' \
           'claude plugin eval plugin --tag live --allow-real-servers --max-cost-usd 5 --json evals/results/live.json' \
           'claude plugin eval plugin --tag tail'; do
    tr '\n' ' ' < "$s" | tr -s ' ' | grep -qiF -- "$t" || fail self-improve "self-improve SKILL.md lacks '$t'"
  done
else fail self-improve "missing $s"; fi
grep -qF '`self-improve`' plugin/skills/using-research-agent/SKILL.md || fail self-improve "using-research-agent table lacks self-improve"
grep -F 'ctx="research-agent skills:' plugin/hooks/session-start.sh | grep -qF 'self-improve' \
  || fail self-improve "session-start.sh fallback index lacks self-improve"
grep -qF '`self-improve`' CHANGELOG.md || fail self-improve "CHANGELOG.md does not mention self-improve"

# Change 10: with no search or fetch tool, the lead says so, names the page, and spawns no worker.
r=plugin/skills/research/SKILL.md
rf=$(tr '\n' ' ' < "$r" | tr -s ' ')
echo "$rf" | grep -qiF 'no search or fetch tool' || fail self-improve "research SKILL.md lacks the no-search-or-fetch-tool one-fact rule"
echo "$rf" | grep -qiF 'a worker has the same tools' || fail self-improve "research SKILL.md does not say why no worker is spawned without tools"
grep -qiE '^- When .*no search or fetch tool.*shall' "$r" || fail self-improve "research SKILL.md lacks an EARS line for the no-tool one-fact path"
