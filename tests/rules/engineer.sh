# Engineer stage-1 tests (tests/engineer/run.sh). Sourced by tests/check.sh (provides fail).
_eng_out=$(mktemp)
if ! bash tests/engineer/run.sh >"$_eng_out" 2>&1; then
  _eng_first=$(grep '^FAIL' "$_eng_out" | head -3 | paste -sd ';' -)
  fail engineer "${_eng_first:-$(tail -1 "$_eng_out")}"
fi
rm -f "$_eng_out"
unset _eng_out _eng_first
