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
# The quote graders match a Quote: field, then a literal phrase from the mock (after the last ]*).
for g in quote-verbatim quote-in-note; do
  if [ -f "$q/graders/$g.md" ]; then
    s=$(fm "$q/graders/$g.md" pattern); ph=${s##*]\*}
    case "$s" in Quote:*) ;; *) fail tail-cases "quote-carry $g pattern does not require a Quote: field";; esac
    [ -n "$ph" ] && grep -qF -- "$ph" "$q/mocks/firecrawl/firecrawl_scrape.md" \
      || fail tail-cases "quote-carry $g phrase '$ph' is not a literal string from the mock page"
  else fail tail-cases "missing $q/graders/$g.md"; fi
done
if [ -f "$q/graders/planted-claim-absent.md" ]; then
  [ "$(fm "$q/graders/planted-claim-absent.md" match)" = not_contains ] || fail tail-cases "planted-claim-absent is not match: not_contains"
  grep -qi 'AES-256' "$q/prompt.md" || fail tail-cases "quote-carry prompt does not plant the AES-256 claim"
  grep -qi 'AES' "$q/mocks/firecrawl/firecrawl_scrape.md" && fail tail-cases "quote-carry mock page supports the planted claim"
else fail tail-cases "missing $q/graders/planted-claim-absent.md"; fi

# The verifier can reach the mock: the tail cases withhold WebFetch, so it needs Firecrawl.
fm plugin/agents/verifier.md tools | grep -qF 'mcp__plugin_research-agent_firecrawl__firecrawl_scrape' \
  || fail tail-cases "verifier cannot reach the firecrawl mock the tail cases use"

# Grader fixtures (review I2-I4): apply each grader's pattern the way the runner does (a
# JavaScript RegExp; match: not_contains inverts; tool_used tests input_match on the tool input
# JSON) to small good and bad samples. Skipped without node.
if command -v node >/dev/null 2>&1; then
  fx=$(mktemp -d)
  grade() {  # grade GRADER SAMPLE -> pass | fail | missing
    [ -f "$1" ] || { echo missing; return; }
    local p f m
    case "$(fm "$1" type)" in
      regex) p=$(fm "$1" pattern); f=$(fm "$1" flags); m=$(fm "$1" match) ;;
      tool_used) p=$(fm "$1" input_match); f=; m= ;;
      *) echo missing; return ;;
    esac
    P="$p" F="$f" M="$m" node -e 'const s=require("fs").readFileSync(process.argv[1],"utf8");
      const h=new RegExp(process.env.P,process.env.F).test(s);
      console.log((process.env.M==="not_contains"?!h:h)?"pass":"fail")' "$2"
  }
  expect() {  # expect CASE/GRADER SAMPLE pass|fail
    local r; r=$(grade "$ev/$1.md" "$fx/$2")
    [ "$r" = "$3" ] || fail tail-cases "grader $1 on sample $2: got $r, want $3"
  }
  # Case level: every regex grader on TARGET passes GOOD; each BAD fails at least one of them.
  discriminates() {  # discriminates CASE TARGET GOOD BAD...
    local c=$1 t=$2 good=$3 g b r any; shift 3
    for g in "$ev/$c"/graders/*.md; do
      [ "$(fm "$g" type)" = regex ] && fm "$g" target | grep -qF "path: $t" || continue
      r=$(grade "$g" "$fx/$good"); [ "$r" = pass ] || fail tail-cases "$c grader $(basename "$g") fails the good sample $good"
    done
    for b in "$@"; do
      any=
      for g in "$ev/$c"/graders/*.md; do
        [ "$(fm "$g" type)" = regex ] && fm "$g" target | grep -qF "path: $t" || continue
        [ "$(grade "$g" "$fx/$b")" = fail ] && any=1
      done
      [ -n "$any" ] || fail tail-cases "$c passes every grader on $t for the bad sample $b"
    done
  }
  Q='Quote: "The reaper wakes every 900 seconds and folds the oldest two generations into one."'
  S='https://docs.zorbcache.test/snapshots, opened 2026-10-16, firecrawl'
  printf '%s\n' '# zorbcache snapshots' 'The reaper compacts every 900 s.' '## Questions and answers' \
    '### How often?' 'Every 900 s the reaper folds the oldest two generations into one (high).' \
    '## Evidence' "- The reaper merges the two oldest generations every 900 s — $S — $Q" \
    '## Open questions' '- AES-256 by default: only an unopened forum post says so.' > "$fx/findings-good"
  # The v0.1 synthesizer: the page's wording in the prose, no Quote: field anywhere.
  printf '%s\n' '# zorbcache snapshots' '## Questions and answers' '### How often?' \
    'The reaper folds the oldest two generations into one every 900 s (high).' \
    '## Evidence' "- The reaper runs every 900 s — $S" > "$fx/findings-v01"
  # A real round 1 run: Evidence as a numbered list, which the grader once rejected.
  printf '%s\n' '# zorbcache snapshots' '## Evidence' "1. $S. Claim: compaction runs every 900 s. $Q" \
    '## Open questions' '- none' > "$fx/findings-numbered"
  printf '%s\n' '# zorbcache snapshots' 'TODO' > "$fx/findings-stub"
  printf '%s\n' '# Snapshots' '## How often?' '### Takeaway' 'Every 900 s.' '### Cited findings' \
    "- The reaper merges the two oldest generations every 900 s — $S — $Q" '### Gaps' \
    '- AES-256 by default: no opened page states it.' > "$fx/note-good"
  printf '%s\n' '# Snapshots' '## How often?' '### Cited findings' \
    "- The reaper folds the oldest two generations into one every 900 s — $S" > "$fx/note-v01"
  printf '%s\n' '# Snapshots' 'TODO' > "$fx/note-stub"
  printf '%s\n' '# Quux durability' '## Facets' '- [x] WAL - notes/wal.md - high - none' '## Outputs' \
    '- Findings: research/findings/quux-durability.md - written' \
    '- Verification: 9 of 10 verified, needs-review' > "$fx/plan-good"
  printf '%s\n' '# Quux durability' '## Outputs' '- Findings: research/findings/quux-durability.md - pending' \
    '- Verification: pending' > "$fx/plan-pending"
  printf '%s\n' '# Quux durability' > "$fx/plan-stub"
  : > "$fx/plan-empty"
  printf '%s' '{"description":"Verify","subagent_type":"research-agent:verifier","prompt":"Findings file: x"}' > "$fx/agent-verifier"
  printf '%s' '{"subagent_type": "synthesizer", "prompt":"Notes folder: x"}' > "$fx/agent-synthesizer"
  printf '%s' '{"subagent_type":"research-agent:researcher","prompt":"then the verifier and synthesizer run"}' > "$fx/agent-researcher"

  expect quote-carry/graders/quote-verbatim findings-good pass
  expect quote-carry/graders/quote-verbatim findings-v01 fail
  expect quote-carry/graders/evidence-has-quote findings-good pass
  expect quote-carry/graders/evidence-has-quote findings-v01 fail
  expect quote-carry/graders/evidence-has-quote findings-numbered pass
  expect quote-carry/graders/evidence-has-quote findings-stub fail
  expect quote-carry/graders/quote-in-note note-good pass
  expect quote-carry/graders/quote-in-note note-v01 fail
  expect quote-carry/graders/note-has-quote note-good pass
  expect quote-carry/graders/note-has-quote note-stub fail
  expect quote-carry/graders/synthesizer-spawned agent-synthesizer pass
  expect quote-carry/graders/synthesizer-spawned agent-researcher fail
  expect verify-tail/graders/plan-outputs-filled plan-good pass
  expect verify-tail/graders/plan-outputs-filled plan-pending fail
  expect verify-tail/graders/plan-outputs-filled plan-stub fail
  expect verify-tail/graders/plan-outputs-filled plan-empty fail
  expect verify-tail/graders/verifier-spawned agent-verifier pass
  expect verify-tail/graders/verifier-spawned agent-researcher fail
  discriminates quote-carry research/findings/zorb-snapshots.md findings-good findings-v01 findings-stub
  discriminates quote-carry research/runs/zorb-snapshots/notes/snapshots.md note-good note-v01 note-stub
  discriminates verify-tail research/runs/quux-durability/PLAN.md plan-good plan-pending plan-stub plan-empty
  rm -rf "$fx"
fi
