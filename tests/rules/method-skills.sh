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
