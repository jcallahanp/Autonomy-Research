# Task 5 rules: the eval suite under plugin/evals/ and the self-test skill.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files, never runs an eval.

ev=plugin/evals
fast_cases="one-fact-inline cite-or-park contradiction injection-resist registry-entry setup-missing-connector interview-ears system-map-diagrams"
live_cases="triage-real-repo scorecard-lookup"

# The ten named cases exist, with the right tags.
for c in $fast_cases $live_cases; do
  [ -f "$ev/$c/prompt.md" ] || fail self-test "missing case $ev/$c/prompt.md"
done
for c in $fast_cases; do
  p="$ev/$c/prompt.md"; [ -f "$p" ] || continue
  grep -Eq '^tags:.*\bfast\b' "$p" || fail self-test "$p is not tagged fast"
  grep -Eq '^tags:.*\blive\b' "$p" && fail self-test "$p is fast but tagged live"
done
for c in $live_cases; do
  p="$ev/$c/prompt.md"; [ -f "$p" ] || continue
  grep -Eq '^tags:.*\blive\b' "$p" || fail self-test "$p is not tagged live"
  grep -Eq '^tags:.*\bfast\b' "$p" && fail self-test "$p is live but tagged fast"
done

# Every case directory (one holding prompt.md or case.yaml) has a prompt and at least one grader.
if [ -d "$ev" ]; then
  for d in $(find "$ev" \( -name prompt.md -o -name case.yaml \) -not -path "*/mocks/*" -not -path "*/results/*" \
               -exec dirname {} \; | sort -u); do
    [ -f "$d/prompt.md" ] || fail self-test "$d has no prompt.md"
    [ -f "$d/prompt.md" ] && [ -z "$(awk 'c >= 2 { print } /^---$/ { c++ }' "$d/prompt.md" | tr -d '[:space:]')" ] \
      && fail self-test "$d/prompt.md has an empty prompt body"
    n=$(find "$d/graders" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l)
    [ "$n" -ge 1 ] || fail self-test "$d has no graders/*.md"
    for g in "$d"/graders/*.md; do
      [ -f "$g" ] || continue
      [ -n "$(fm "$g" type)" ] || fail self-test "$g has no type"
    done
  done
  # Exactly one llm grader in the whole suite (citation quality).
  n=$(grep -lE "^type:[[:space:]]*[\"']?llm[\"']?[[:space:]]*(#.*)?$" $(find "$ev" -path '*/graders/*.md' -not -path "*/results/*") 2>/dev/null | wc -l)
  [ "$n" -eq 1 ] || fail self-test "suite has $n llm graders, want exactly 1"
else fail self-test "missing $ev"; fi

# The self-test skill runs the exact command and states the pass bar and the one-time rule.
s=plugin/skills/self-test/SKILL.md
if [ -f "$s" ]; then
  grep -qF 'claude plugin eval plugin --tag fast --max-cost-usd 5 --json evals/results/latest.json' "$s" \
    || fail self-test "self-test SKILL.md lacks the exact eval command"
  for t in '0.8' '0.3' '0.67' 'one-time' 'plan usage'; do
    grep -qF "$t" "$s" || fail self-test "self-test SKILL.md lacks '$t'"
  done
else fail self-test "missing $s"; fi

# Raw eval results stay out of git: the plugin's results dir and the repo-root --json target.
for l in 'plugin/evals/results/' '/evals/results/'; do
  grep -qxF "$l" .gitignore || fail self-test ".gitignore lacks $l"
done

# Fix round 1: background run, -j 3, installed-plugin fallback, confirmation, report and noise notes.
s=plugin/skills/self-test/SKILL.md
if [ -f "$s" ]; then
  grep -qF 'claude plugin eval plugin --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3' "$s" \
    || fail self-test "self-test command lacks -j 3 after the exact prefix"
  grep -qF 'claude plugin eval research-agent --tag fast --max-cost-usd 5 --json evals/results/latest.json -j 3' "$s" \
    || fail self-test "self-test lacks the installed-plugin fallback command"
  for t in 'run_in_background' 'plugin/.claude-plugin/plugin.json' 'confirm' '0.125' 'claude.ai' 'absolute-score'; do
    grep -qF "$t" "$s" || fail self-test "self-test SKILL.md lacks '$t'"
  done
fi

# Fix round 1: grader arms and anchors.
grep -qx 'arm: both' $ev/injection-resist/graders/no-beacon.md 2>/dev/null || fail self-test "injection-resist no-beacon is not arm: both"
grep -qx 'arm: with-only' $ev/one-fact-inline/graders/content-calls.md 2>/dev/null || fail self-test "one-fact-inline content-calls is not arm: with-only"
grep -qF '"command"' $ev/triage-real-repo/graders/never-installs.md 2>/dev/null || fail self-test "never-installs is not anchored to the Bash command start"
grep -Eq "^pattern: '?instruction" $ev/injection-resist/graders/flagged.md 2>/dev/null && fail self-test "injection-resist flagged still matches a bare 'instruction'"
grep -qF 'opened' $ev/cite-or-park/graders/not-cited.md 2>/dev/null || fail self-test "cite-or-park not-cited does not match citation-shaped lines"
[ -f $ev/cite-or-park/graders/findings-not-cited.md ] || fail self-test "cite-or-park lacks a findings-file not-cited grader"

# Fix round 1: the findings format ships in the plugin; the template copy is a pointer.
ff=plugin/skills/research/findings-format.md
if [ -f "$ff" ]; then
  grep -q '^7\. `## Verification`' "$ff" || fail self-test "$ff lacks section 7 '## Verification'"
else fail self-test "missing $ff"; fi
grep -qF 'findings-format.md' plugin/skills/research/SKILL.md || fail self-test "research SKILL.md does not point to findings-format.md"
grep -qF 'findings-format.md' plugin/agents/synthesizer.md || fail self-test "synthesizer.md does not point to findings-format.md"
grep -qF '_FORMAT.md' plugin/skills/research/SKILL.md plugin/agents/synthesizer.md plugin/skills/research/note-schema.md \
  && fail self-test "plugin files still point at research/findings/_FORMAT.md"
grep -qF 'plugin/skills/research/findings-format.md' research/findings/_FORMAT.md || fail self-test "_FORMAT.md does not point to the plugin copy"

# Fix round 1: the skill index and the hook fallback list every skill.
for k in interview system-map spike self-test; do
  grep -qF "\`$k\`" plugin/skills/using-research-agent/SKILL.md || fail self-test "using-research-agent table lacks $k"
  grep -F 'ctx="research-agent skills:' plugin/hooks/session-start.sh | grep -qF "$k" || fail self-test "session-start.sh fallback index lacks $k"
done
