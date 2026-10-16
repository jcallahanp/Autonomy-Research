#!/bin/bash
# Engineer plugin skills: the engineer's own skills plus the vendored Superpowers subset.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

skills=engineer/plugin/skills
fm() { python3 tests/engineer/plugin/fm.py "$1"; }
field() { python3 -c 'import json,sys; v=json.load(sys.stdin).get(sys.argv[1]); print("" if v is None else v)' "$1"; }

own=(as-is plan deploy security-review digest)
[ -f "$skills/browser/SKILL.md" ] && own+=(browser)   # Task 10's skill, checked when present
vendored=(brainstorming writing-plans subagent-driven-development executing-plans
          verification-before-completion using-git-worktrees using-superpowers)

check_skill() {  # check_skill NAME LINE_RULE(yes|no)
  local f="$skills/$1/SKILL.md" j name desc lines
  [ -f "$f" ] || { fail "$f missing"; return; }
  j=$(fm "$f") || { fail "$f: bad frontmatter"; return; }
  name=$(field name <<<"$j"); desc=$(field description <<<"$j"); lines=$(field _lines <<<"$j")
  [ "$name" = "$1" ] || fail "$f: name '$name' does not match folder"
  [ -n "$desc" ] || fail "$f: no description"
  [ "${#desc}" -lt 1536 ] || fail "$f: description ${#desc} characters (limit 1535)"
  if [ "$2" = yes ]; then [ "$lines" -le 300 ] || fail "$f: $lines lines (limit 300)"; fi
}

for s in "${own[@]}"; do check_skill "$s" yes; done
for s in "${vendored[@]}"; do check_skill "$s" no; done

for s in test-driven-development finishing-a-development-branch; do
  [ ! -e "$skills/$s" ] || fail "$skills/$s must not be vendored"
done

has() {  # has SKILL TEXT
  grep -qF -- "$2" "$skills/$1/SKILL.md" 2>/dev/null || fail "$1/SKILL.md does not mention '$2'"
}
for w in tasks.json approval Minor Moderate Major DEPENDENTS.md "one commit"; do has plan "$w"; done
for w in --decrypted observed inferred asserted "docs/map/"; do has as-is "$w"; done
for w in preview hold rollback T2; do has deploy "$w"; done
for w in CWE severity repro scope REPORT.md; do has security-review "$w"; done
for w in "CONFIRM" "all y" "4096" "default"; do has digest "$w"; done

# The engineer's own skills are instructions in plain English: no leftover template markers.
for s in "${own[@]}"; do
  ! grep -nE 'TODO|TBD|\{\{' "$skills/$s/SKILL.md" >/dev/null 2>&1 || fail "$s/SKILL.md has a placeholder"
done
