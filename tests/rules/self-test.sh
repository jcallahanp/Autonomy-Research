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
  n=$(grep -lx 'type: llm' $(find "$ev" -path '*/graders/*.md' -not -path "*/results/*") 2>/dev/null | wc -l)
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

# Raw eval results stay out of git.
grep -qxF 'plugin/evals/results/' .gitignore || fail self-test ".gitignore lacks plugin/evals/results/"
