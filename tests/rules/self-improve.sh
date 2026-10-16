# Self-improvement round 1, changes 9-10: the self-improve skill that writes down the loop, and
# the one-fact path when no search or fetch tool exists.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files only.

s=plugin/skills/self-improve/SKILL.md
if [ -f "$s" ]; then
  [ "$(fm "$s" name)" = self-improve ] || fail self-improve "$s name is not self-improve"
  n=$(wc -l < "$s"); [ "$n" -lt 150 ] || fail self-improve "$s has $n lines (limit 149)"
  d=$(fm "$s" description); sf=$(tr '\n' ' ' < "$s" | tr -s ' ')
  for t in 'improve yourself' 'self-improve' 'self-improvement round' 'Use when'; do
    echo "$d" | grep -qiF -- "$t" || fail self-improve "self-improve description lacks '$t'"
  done
  for t in 'tests/frozen-exam.sha256' 'tests/check.sh' '`tail`' 'reported separately' 'research' 'verifier' \
           '20 citations' 'keep rule' '--runs 3' '5 runs' '2 rounds' 'docs/self-improvement/' 'pull request' \
           'never edit' 'graders' 'mocks' \
           'claude plugin eval plugin --tag tail' 'Series:' 'round 2 of 2' '--case <name>' \
           'withheld'; do
    tr '\n' ' ' < "$s" | tr -s ' ' | grep -qiF -- "$t" || fail self-improve "self-improve SKILL.md lacks '$t'"
  done
  # Every `claude plugin eval plugin` command in self-test, with all its --allow-tools grants,
  # appears verbatim here: a tool left out of --allow-tools is withheld without an error.
  st=plugin/skills/self-test/SKILL.md
  cmds=$(grep -oE 'claude plugin eval plugin [^`]*' "$st" | sed 's/[ \t]*$//' | sort -u)
  [ -n "$cmds" ] || fail self-improve "no claude plugin eval command found in $st"
  miss=$(printf '%s\n' "$cmds" | while IFS= read -r c; do [ -z "$c" ] || grep -qF -- "$c" "$s" || echo "[$c]"; done)
  [ -z "$miss" ] || fail self-improve "self-improve SKILL.md lacks the self-test command(s) verbatim: $miss"
  live=$(grep -F 'claude plugin eval plugin --tag live' "$s")
  for t in WebFetch WebSearch '"Bash(git clone *)"' '"Bash(grep *)"' \
           '"mcp__plugin_research-agent_deepwiki__*"' '"mcp__plugin_research-agent_firecrawl__*"'; do
    echo "$live" | grep -qF -- "$t" || fail self-improve "self-improve live command does not grant $t"
  done
  # Review I6: a series is 2 rounds; the budget and plan yeses inside a round do not reset it.
  echo "$sf" | grep -qiF 'do not start a new series' || fail self-improve "self-improve does not say which yeses leave the series count alone"
  echo "$sf" | grep -qiE -- '- When [^.]*round 2 of 2[^.]*shall stop' || fail self-improve "self-improve lacks the EARS line for the series cap"
  # Review I7: a dropped after-score reverts what the dropped case exercises, re-runs that case only.
  echo "$sf" | grep -qiF 'revert every plugin change of the round' || fail self-improve "self-improve lacks the whole-round revert fallback"
  echo "$sf" | grep -qiF 'chase a better number' || fail self-improve "self-improve no longer forbids re-running to chase a number"
  echo "$sf" | grep -qiE -- '- When [^.]*after-score[^.]*re-run only that case' || fail self-improve "self-improve EARS keep line lacks the targeted re-run"
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
