# Self-improvement round 1, change 7: offline cases for the pipeline tail, tagged [tail] only.
# They are development cases (same author as the fixes), reported apart from the frozen exam.
# Sourced by tests/check.sh (provides fail, fm). Offline: reads files, never runs an eval.

ev=plugin/evals
for c in verify-tail quote-carry; do
  d=$ev/$c; p=$d/prompt.md
  if [ ! -f "$p" ]; then fail tail-cases "missing $p"; continue; fi
  grep -Eq '^tags: *\[ *tail *\] *$' "$p" || fail tail-cases "$p is not tagged [tail] only"
  mt=$(fm "$p" max_turns); [ "${mt:-0}" -ge 60 ] 2>/dev/null || fail tail-cases "$p max_turns '$mt' < 60"
  [ "$(fm "$p" timeout_seconds)" = 900 ] || fail tail-cases "$p timeout_seconds is not 900"
  for t in WebFetch WebSearch Bash; do
    fm "$p" disallowed_tools | grep -qw "$t" || fail tail-cases "$p does not disallow $t"
  done
  m=$d/mocks/firecrawl/firecrawl_scrape.md
  [ -f "$m" ] && [ "$(fm "$m" type)" = agent ] || fail tail-cases "$c lacks an agent mock at mocks/firecrawl/firecrawl_scrape.md"
  bad=$(grep -ohE 'https?://[^ )`"]+' "$p" "$m" 2>/dev/null | grep -vE '^https?://[a-z0-9.-]+\.test(/|$)')
  [ -z "$bad" ] || fail tail-cases "$c uses non-.test URLs: $bad"
  for g in "$d"/graders/*.md; do
    [ -f "$g" ] || continue
    case "$(fm "$g" type)" in regex|file_exists|tool_used) ;; *) fail tail-cases "$g type '$(fm "$g" type)' is not a free grader";; esac
  done
  grep -qF "$d/" tests/frozen-exam.sha256 && fail tail-cases "$c is listed in the frozen manifest"
done

# verify-tail grades the tail: findings file, Verification heading, INDEX line, PLAN.md Outputs.
g=$ev/verify-tail/graders
grep -lq 'research/findings/quux-durability.md' $g/*.md 2>/dev/null || fail tail-cases "verify-tail has no grader on the findings file"
grep -l '## Verification' $g/*.md >/dev/null 2>&1 || fail tail-cases "verify-tail does not grade a ## Verification heading"
grep -l 'research/findings/INDEX.md' $g/*.md >/dev/null 2>&1 || fail tail-cases "verify-tail does not grade the INDEX line"
pg=$(grep -l 'research/runs/quux-durability/PLAN.md' $g/*.md 2>/dev/null)
{ [ -n "$pg" ] && grep -l 'not_contains' $pg >/dev/null 2>&1; } \
  || fail tail-cases "verify-tail does not grade that PLAN.md Outputs no longer say pending"

# quote-carry: a verbatim string from the mock page is in the findings; a planted claim is not.
q=$ev/quote-carry
if [ -f "$q/graders/quote-verbatim.md" ]; then
  s=$(fm "$q/graders/quote-verbatim.md" pattern)
  [ -n "$s" ] && grep -qF -- "$s" "$q/mocks/firecrawl/firecrawl_scrape.md" \
    || fail tail-cases "quote-carry quote-verbatim pattern is not a literal string from the mock page"
else fail tail-cases "missing $q/graders/quote-verbatim.md"; fi
if [ -f "$q/graders/planted-claim-absent.md" ]; then
  [ "$(fm "$q/graders/planted-claim-absent.md" match)" = not_contains ] || fail tail-cases "planted-claim-absent is not match: not_contains"
  grep -qi 'AES-256' "$q/prompt.md" || fail tail-cases "quote-carry prompt does not plant the AES-256 claim"
  grep -qi 'AES' "$q/mocks/firecrawl/firecrawl_scrape.md" && fail tail-cases "quote-carry mock page supports the planted claim"
else fail tail-cases "missing $q/graders/planted-claim-absent.md"; fi

# The verifier can reach the mock: the tail cases withhold WebFetch, so it needs Firecrawl.
fm plugin/agents/verifier.md tools | grep -qF 'mcp__plugin_research-agent_firecrawl__firecrawl_scrape' \
  || fail tail-cases "verifier cannot reach the firecrawl mock the tail cases use"
