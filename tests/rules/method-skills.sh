# Task 4 rules: method skills (interview, system-map, spike), template-side rules, and the
# diagram checker script. Sourced by tests/check.sh (provides fail, fm).
# Offline and fast: this file never renders a diagram. Run tests/check-mermaid.sh for that.

for k in interview system-map spike; do
  s=plugin/skills/$k/SKILL.md
  if [ ! -f "$s" ]; then fail method-skills "missing $s"; continue; fi
  [ "$(fm "$s" name)" = "$k" ] || fail method-skills "$s name is '$(fm "$s" name)', want $k"
  d=$(fm "$s" description)
  [ -n "$d" ] || fail method-skills "$s missing description"
  [ "${#d}" -lt 1536 ] || fail method-skills "$s description ${#d} chars"
  echo "$d" | grep -qi 'use when' || fail method-skills "$s description does not say when to use it"
done

s=plugin/skills/interview/SKILL.md
if [ -f "$s" ]; then
  for t in 'one open question' 'play back' 'anti-goal' 'five-whys' 'EARS' 'Volere' \
           'research/requirements/' 'research/open-questions.md' 'skip' 'missing' 'inconsistent'; do
    grep -qiF "$t" "$s" || fail method-skills "interview SKILL.md lacks '$t'"
  done
fi

s=plugin/skills/system-map/SKILL.md
if [ -f "$s" ]; then
  for t in 'flowchart' 'sequenceDiagram' 'docs/diagrams/' 'index.md' 'check-mermaid.sh' 'Mermaid Chart' 'context' 'container'; do
    grep -qiF "$t" "$s" || fail method-skills "system-map SKILL.md lacks '$t'"
  done
  grep -qiE 'never.*C4 syntax|C4Context' "$s" || fail method-skills "system-map lacks the no-C4-syntax rule"
fi

s=plugin/skills/spike/SKILL.md
if [ -f "$s" ]; then
  for t in 'research/spikes/' 'three' 'worker' 'probe' 'negative result' 'outside the project tree' \
           'read-only' 'named' 'credentials'; do
    grep -qiF "$t" "$s" || fail method-skills "spike SKILL.md lacks '$t'"
  done
fi

# Template-side rules: short, path-scoped, pointing at the source files.
for pair in research-format:'research/**':research/findings/_FORMAT.md diagrams:'docs/diagrams/**':docs/diagrams/index.md; do
  n=${pair%%:*}; rest=${pair#*:}; glob=${rest%%:*}; ptr=${rest#*:}
  f=.claude/rules/$n.md
  if [ ! -f "$f" ]; then fail method-skills "missing $f"; continue; fi
  l=$(wc -l < "$f"); [ "$l" -lt 40 ] || fail method-skills "$f has $l lines (limit 39)"
  grep -qF "$glob" "$f" || fail method-skills "$f lacks paths: $glob"
  [ "$(sed -n 1p "$f")" = "---" ] && sed -n '2,/^---$/p' "$f" | grep -q '^paths:' || fail method-skills "$f lacks paths: frontmatter"
  grep -qF "$ptr" "$f" || fail method-skills "$f does not point to $ptr"
done

# Diagram checker exists, is executable, and carries the pinned renderer and the three checks.
c=tests/check-mermaid.sh
if [ -f "$c" ]; then
  [ -x "$c" ] || fail method-skills "$c is not executable"
  grep -qE '^MMDC_VERSION=[0-9]+\.[0-9]+\.[0-9]+' "$c" && grep -qF '@mermaid-js/mermaid-cli@$MMDC_VERSION' "$c" || fail method-skills "$c does not pin an exact mermaid-cli version"
  grep -qF '/opt/pw-browsers/chromium' "$c" || fail method-skills "$c does not use /opt/pw-browsers/chromium"
  grep -qF 'index.md' "$c" || fail method-skills "$c does not check the index"
  grep -qF 'C4' "$c" || fail method-skills "$c does not reject C4 syntax"
else fail method-skills "missing $c"; fi

# Fix round 1: spike runs candidates only in its own worker, with isolation rules; the
# researcher's never-install rule stays absolute.
w=plugin/agents/spike-worker.md
if [ -f "$w" ]; then
  [ "$(fm "$w" name)" = "spike-worker" ] || fail method-skills "$w name is not spike-worker"
  [ "$(fm "$w" model)" = "sonnet" ] || fail method-skills "$w model is '$(fm "$w" model)', want sonnet"
  [ "$(fm "$w" maxTurns)" = "40" ] || fail method-skills "$w maxTurns is not 40"
  [ "$(fm "$w" omitClaudeMd)" = "true" ] || fail method-skills "$w does not set omitClaudeMd: true"
  [ "$(fm "$w" disallowedTools)" = "Agent" ] || fail method-skills "$w does not disallow Agent"
  t=$(fm "$w" tools)
  echo "$t" | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//' | grep -qx ToolSearch || fail method-skills "$w tools lack ToolSearch"
  echo "$t" | tr ',' '\n' | sed 's/^[ \t]*//; s/[ \t]*$//' | grep -qx Agent && fail method-skills "$w tools include Agent"
  fm "$w" description | grep -qi 'spike' || fail method-skills "$w description does not say it is for the spike skill"
  for t in 'env -i' '--ignore-scripts' 'mktemp -d' 'HTTPS_PROXY' 'SSL_CERT_FILE' 'NODE_EXTRA_CA_CERTS' \
           'sudo' 'curl | sh' '~/.ssh' "user's own message" 'as data' 'PATH:' 'TAKEAWAYS:' 'GAPS:' 'CONFIDENCE:' \
           'install surface'; do
    grep -qiF -- "$t" "$w" || fail method-skills "spike-worker.md lacks '$t'"
  done
else fail method-skills "missing $w"; fi
s=plugin/skills/spike/SKILL.md
if [ -f "$s" ]; then
  grep -qF 'spike-worker' "$s" || fail method-skills "spike SKILL.md does not dispatch spike-worker"
  grep -qE 'Spawn one `researcher`|`researcher` worker per path' "$s" && fail method-skills "spike SKILL.md still dispatches researcher to run paths"
  grep -qF 'env -i' "$s" || fail method-skills "spike SKILL.md does not mirror the env -i isolation"
  grep -qF -- '--ignore-scripts' "$s" || fail method-skills "spike SKILL.md does not mirror --ignore-scripts"
  grep -qF 'repo-triage' "$s" && grep -qiE 'lead runs .?repo-triage' "$s" || fail method-skills "spike SKILL.md does not say the lead runs repo-triage first"
  grep -qF '`synthesizer`' "$s" || fail method-skills "spike SKILL.md does not use the synthesizer to write the spike file"
fi
grep -qiE 'in a worker' plugin/skills/system-map/SKILL.md && fail method-skills "system-map still says to run the Mermaid Chart connector in a worker"
grep -qiE 'never (install|run)' plugin/agents/researcher.md || fail method-skills "researcher.md lost its never-install rule"
grep -qi 'spike' plugin/agents/researcher.md && fail method-skills "researcher.md mentions spike (no exception allowed)"

# Fix round 2.
w=plugin/agents/spike-worker.md
sy=plugin/agents/synthesizer.md
s=plugin/skills/spike/SKILL.md
flat() { tr '\n' ' ' < "$1" | tr -s ' '; }
if [ -f "$w" ]; then
  # Verdict line and its exact vocabulary, in the worker note shape and in the spike file shape.
  grep -qF 'Verdict: works | fails | blocked' "$w" || fail method-skills "spike-worker.md lacks the 'Verdict: works | fails | blocked' line"
  grep -qF 'works | fails | blocked | inconclusive' "$s" || fail method-skills "spike SKILL.md Results does not use 'works | fails | blocked | inconclusive'"
  # No state carries between Bash calls.
  grep -qF 'ONE Bash call' "$w" || fail method-skills "spike-worker.md does not say to run create/install/probe/cleanup in ONE Bash call"
  grep -qiF 'literal temp path' "$w" || fail method-skills "spike-worker.md does not say to reuse the literal temp path"
  grep -qi 'never rely on `\$T`' "$w" || fail method-skills "spike-worker.md does not forbid relying on \$T across calls"
  # Exact env recipe, one ${VAR:+VAR="$VAR"} per pass-through variable, both cases.
  for v in HTTPS_PROXY HTTP_PROXY NO_PROXY https_proxy http_proxy no_proxy SSL_CERT_FILE NODE_EXTRA_CA_CERTS REQUESTS_CA_BUNDLE; do
    grep -qF "\${$v:+$v=\"\$$v\"}" "$w" || fail method-skills "spike-worker.md env recipe lacks \${$v:+$v=\"\$$v\"}"
  done
  # git clone of the candidate runs under the same env -i recipe.
  flat "$w" | grep -qE 'env -i[^`]{0,400}git clone|git clone[^`]{0,40}env -i|`env -i[^`]*git clone' \
    || fail method-skills "spike-worker.md does not run git clone under env -i"
  grep -qF '.gitconfig' "$w" || fail method-skills "spike-worker.md does not mention ~/.gitconfig / credential helpers for the clone"
fi
# Synthesizer spike mode.
if [ -f "$sy" ]; then
  grep -qF 'Spike mode' "$sy" || fail method-skills "synthesizer.md lacks a 'Spike mode' section"
  grep -qF 'SPIKE' "$sy" || fail method-skills "synthesizer.md does not mention SPIKE"
  flat "$sy" | grep -qiE 'negative results.{0,60}never dropped|never drop.{0,40}negative' || fail method-skills "synthesizer.md Spike mode does not keep negative results"
  flat "$sy" | grep -qiE 'command and the output excerpt' || fail method-skills "synthesizer.md Spike mode does not accept command and output excerpt as evidence"
fi
flat "$s" | grep -qE 'Spawn one `synthesizer`.{0,400}Begin its brief with the word `SPIKE`' || fail method-skills "spike SKILL.md synthesizer brief does not say SPIKE"
# Triage before PLAN.md records the verdicts.
tl=$(grep -n 'Run `repo-triage`' "$s" | head -1 | cut -d: -f1)
pl=$(grep -n 'Write `research/runs/<slug>/PLAN.md`' "$s" | head -1 | cut -d: -f1)
{ [ -n "$tl" ] && [ -n "$pl" ] && [ "$tl" -lt "$pl" ]; } || fail method-skills "spike SKILL.md: repo-triage step does not come before the PLAN.md step"
