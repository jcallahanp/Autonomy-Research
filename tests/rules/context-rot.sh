# Self-improvement round 1, changes 4-5: the SessionStart hook re-injects the active run's
# PLAN.md and the newest INDEX lines; workers expect compaction; dispatches copy the Rulings.
# Sourced by tests/check.sh (provides fail, fm). Runs the hook against a temp project dir.

h=plugin/hooks/session-start.sh
if [ -f "$h" ]; then
  tmp=$(mktemp -d)
  # mkplan SLUG OUTPUT-STATUS MTIME FILLER-LINES: a PLAN.md whose Outputs say OUTPUT-STATUS.
  mkplan() {
    d="$tmp/research/runs/$1"; mkdir -p "$d"
    {
      printf '%s\n' "# Run $1" "Rulings: marker-$1" "## Facets" "- [x] a - notes/a.md - high - none"
      [ "$1" = finished ] && echo "- [ ] dropped facet - notes/b.md - pending"
      printf '%s\n' "## Outputs" "- Findings: research/findings/$1.md - $2" "- Verification: $2"
      for i in $(seq 1 "$4"); do echo "filler $1 $i"; done
    } > "$d/PLAN.md"
    touch -t "$3" "$d/PLAN.md"
  }
  mkplan old-active pending 202601010000 0
  mkplan active running 202602010000 60      # lines 8-67 are filler; line 60 is "filler active 53"
  mkplan finished "written, 3 of 3 verified" 202603010000 0   # newest, but nothing pending in Outputs
  mkdir -p "$tmp/research/findings"
  echo '# Findings index' > "$tmp/research/findings/INDEX.md"
  for i in $(seq 1 45); do echo "- entry $i" >> "$tmp/research/findings/INDEX.md"; done

  check_ctx() { # label context
    case "$2" in *marker-active*) ;; *) fail context-rot "$1: hook did not inject the active run's PLAN.md";; esac
    case "$2" in *research/runs/active/PLAN.md*) ;; *) fail context-rot "$1: hook does not name the active PLAN.md path";; esac
    case "$2" in *marker-finished*) fail context-rot "$1: hook injected a finished run (Outputs not pending)";; esac
    case "$2" in *marker-old-active*) fail context-rot "$1: hook injected an older run instead of the newest active one";; esac
    case "$2" in *'filler active 53'*) ;; *) fail context-rot "$1: hook cut PLAN.md before line 60";; esac
    case "$2" in *'filler active 54'*) fail context-rot "$1: hook injected more than 60 PLAN.md lines";; esac
    case "$2" in *'- entry 45'*) ;; *) fail context-rot "$1: hook dropped the newest INDEX.md line";; esac
    case "$2" in *'- entry 15'*) fail context-rot "$1: hook injected more than the newest 30 INDEX.md lines";; esac
    case "$2" in *'newest 30'*) ;; *) fail context-rot "$1: INDEX label does not say 'newest 30'";; esac
  }

  out=$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$PWD/plugin" bash "$h"); rc=$?
  [ "$rc" -eq 0 ] || fail context-rot "session-start.sh exited $rc with an active run"
  check_ctx "with jq" "$(echo "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"

  # Without jq: a PATH holding only the basic tools the hook may use.
  mkdir "$tmp/bin"
  for t in dirname awk head tail ls cat sed tr; do
    p=$(command -v "$t") && ln -s "$p" "$tmp/bin/$t"
  done
  bash_bin=$(command -v bash)
  out=$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$PWD/plugin" PATH="$tmp/bin" "$bash_bin" "$h"); rc=$?
  [ "$rc" -eq 0 ] || fail context-rot "session-start.sh exited $rc without jq"
  check_ctx "without jq" "$out"

  # No active run: nothing about runs is injected, and the hook still exits 0.
  rm -rf "$tmp/research/runs/active" "$tmp/research/runs/old-active"
  out=$(CLAUDE_PROJECT_DIR="$tmp" CLAUDE_PLUGIN_ROOT="$PWD/plugin" bash "$h"); rc=$?
  [ "$rc" -eq 0 ] || fail context-rot "session-start.sh exited $rc with no active run"
  case "$out" in *marker-finished*) fail context-rot "hook injected a finished run when no run is active";; esac
  rm -rf "$tmp"
else fail context-rot "missing $h"; fi

# The lead marks the run finished, so the hook stops injecting it.
grep -qF 'neither says pending' plugin/skills/research/SKILL.md \
  || fail context-rot "research SKILL.md does not rewrite the PLAN.md Outputs lines after verification"

# Change 5: workers write the note skeleton first and are told they may be compacted.
r=plugin/agents/researcher.md
grep -qi 'skeleton' "$r" || fail context-rot "researcher.md does not write the note skeleton first"
grep -qi 'compacted' "$r" || fail context-rot "researcher.md does not say the worker may be compacted"
grep -qi 'wrap up early' "$r" || fail context-rot "researcher.md does not say not to wrap up early"
grep -qE '^Rulings: .*verbatim' plugin/skills/research/SKILL.md \
  || fail context-rot "research SKILL.md dispatch template does not copy the PLAN.md Rulings line verbatim"
