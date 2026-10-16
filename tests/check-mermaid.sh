#!/bin/bash
# Render-check every .mmd diagram. Slow and networked (npx), so tests/check.sh does not run it;
# run it by hand or in CI.
#
# Usage: tests/check-mermaid.sh [DIR]     (DIR defaults to docs/diagrams)
#
# Fails (exit 1) when a .mmd file:
#   - is not linked from DIR/index.md,
#   - starts with anything but flowchart, graph or sequenceDiagram (C4Context etc. are rejected),
#   - does not render with mermaid-cli.
# Render output goes to a temp dir that is removed on exit; nothing is written into the repo.
# Set MERMAID_SKIP_RENDER=1 to run only the two static checks.

MMDC_VERSION=11.12.0   # published 2025-09-25; bump deliberately
CHROMIUM=/opt/pw-browsers/chromium

root=$(cd "$(dirname "$0")/.." && pwd)
dir=${1:-$root/docs/diagrams}
[ -d "$dir" ] || { echo "FAIL mermaid: $dir is not a directory"; exit 1; }
dir=$(cd "$dir" && pwd)
index=$dir/index.md

fails=0
fail() { echo "FAIL mermaid: $1"; fails=$((fails+1)); }

shopt -s nullglob
files=("$dir"/*.mmd)
[ "${#files[@]}" -gt 0 ] || { echo "FAIL mermaid: no .mmd files in $dir"; exit 1; }
[ -f "$index" ] || fail "missing $index"

work=$(mktemp -d "${TMPDIR:-/tmp}/check-mermaid.XXXXXX") || exit 1
trap 'rm -rf "$work"' EXIT

# Static checks: linked from the index; first real line is a supported diagram type.
for f in "${files[@]}"; do
  n=$(basename "$f")
  if [ -f "$index" ] && ! grep -qF "($n)" "$index"; then fail "$n is not linked from index.md"; fi
  first=$(grep -vE '^[[:space:]]*(%%.*)?$' "$f" | head -1 | sed 's/^[[:space:]]*//')
  case "$first" in
    flowchart*|graph*|sequenceDiagram*) ;;
    C4*) fail "$n uses C4 syntax ('$first'); draw C4 levels as flowcharts" ;;
    *) fail "$n starts with '$first'; only flowchart or sequenceDiagram are allowed" ;;
  esac
  case "$first" in C4*) ;; *)
    grep -qE '^[[:space:]]*(C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b' "$f" \
      && fail "$n contains C4 syntax" ;;
  esac
done

# Render each file.
if [ -z "$MERMAID_SKIP_RENDER" ]; then
  pcfg=$work/puppeteer.json
  if [ -x "$CHROMIUM" ]; then
    printf '{"executablePath":"%s","args":["--no-sandbox","--disable-setuid-sandbox"]}\n' "$CHROMIUM" > "$pcfg"
  else
    printf '{"args":["--no-sandbox","--disable-setuid-sandbox"]}\n' > "$pcfg"
  fi
  for f in "${files[@]}"; do
    n=$(basename "$f" .mmd)
    if ! (cd "$work" && npx -y "@mermaid-js/mermaid-cli@$MMDC_VERSION" -p "$pcfg" -i "$f" -o "$work/$n.svg" >"$work/$n.log" 2>&1); then
      fail "$(basename "$f") does not render: $(grep -m1 -iE 'error|parse' "$work/$n.log" | cut -c1-200)"
    elif [ ! -s "$work/$n.svg" ]; then
      fail "$(basename "$f") rendered an empty file"
    fi
  done
fi

if [ "$fails" -eq 0 ]; then echo "check-mermaid.sh: ${#files[@]} diagram(s) ok"; exit 0; fi
echo "check-mermaid.sh: $fails failure(s)"; exit 1
