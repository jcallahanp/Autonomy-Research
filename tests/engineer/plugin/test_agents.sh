#!/bin/bash
# Engineer plugin agents: frontmatter fields, models, tool limits and read-only bodies.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

agents=engineer/plugin/agents
fm() { python3 tests/engineer/plugin/fm.py "$1"; }
field() { python3 -c 'import json,sys; v=json.load(sys.stdin).get(sys.argv[1]); print("" if v is None else v)' "$1"; }
tools_of() {  # one tool per line
  python3 -c 'import json,sys; t=json.load(sys.stdin).get("tools") or ""
for x in (t if isinstance(t, list) else str(t).split(",")): print(x.strip())'
}

declare -A model=([planner]=opus [implementer]=sonnet [plan-reviewer]=sonnet [auditor]=sonnet
                  [mapper]=sonnet [merger]=sonnet [triage-reader]=haiku)
n=$(find "$agents" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l)
[ "$n" -eq 7 ] || fail "expected 7 agents, found $n"

for a in "${!model[@]}"; do
  f="$agents/$a.md"
  [ -f "$f" ] || { fail "$f missing"; continue; }
  j=$(fm "$f") || { fail "$f: bad frontmatter"; continue; }
  [ "$(field name <<<"$j")" = "$a" ] || fail "$f: name does not match file"
  [ -n "$(field description <<<"$j")" ] || fail "$f: no description"
  [ "$(field model <<<"$j")" = "${model[$a]}" ] || fail "$f: model is not ${model[$a]}"
  [ -n "$(field tools <<<"$j")" ] || fail "$f: no tools"
  for k in hooks mcpServers permissionMode; do
    python3 -c 'import json,sys; sys.exit(sys.argv[1] in json.load(sys.stdin))' "$k" <<<"$j" \
      || fail "$f: sets $k (plugin agents ignore it)"
  done
done

tools() { fm "$agents/$1.md" 2>/dev/null | tools_of; }
no_write() {  # no_write AGENT
  local t; t=$(tools "$1")
  for w in Write Edit MultiEdit NotebookEdit; do
    ! grep -qx "$w" <<<"$t" || fail "$1 has $w"
  done
}
only() {  # only AGENT TOOL...
  local a=$1; shift
  local want; want=$(printf '%s\n' "$@" | sort)
  [ "$(tools "$a" | sort)" = "$want" ] || fail "$a tools are not exactly: $*"
}

no_write auditor; no_write plan-reviewer; no_write mapper; no_write merger; no_write triage-reader
only auditor Read Glob Grep Bash
only plan-reviewer Read Glob Grep
only triage-reader Read
only planner Read Glob Grep Write Edit
grep -q 'audit-verdict' "$agents/auditor.md" || fail "auditor body does not name audit-verdict"
grep -q 'FAIL' "$agents/auditor.md" || fail "auditor body does not default to FAIL"
grep -q 'path:line' "$agents/auditor.md" || fail "auditor body does not require path:line"
grep -q 'docs/plan/' "$agents/planner.md" || fail "planner body does not limit writes to docs/plan/"
grep -qi 'untrusted' "$agents/triage-reader.md" || fail "triage-reader does not treat input as untrusted"
grep -q 'JSON' "$agents/triage-reader.md" || fail "triage-reader does not return JSON"
for a in mapper merger; do grep -q 'path:line' "$agents/$a.md" || fail "$a does not cite path:line"; done
impl=$(tools implementer)
for w in Bash Write Edit Read; do grep -qx "$w" <<<"$impl" || fail "implementer lacks $w"; done
