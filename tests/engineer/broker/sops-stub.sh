# Body of the fake `sops` used by the broker tests (written into <root>/bin by testlib.stub).
# The "encrypted" file is plain JSON: -e copies its input, -d prints the file or one --extract key.
mode=; extract=; file=
while [ $# -gt 0 ]; do
  case "$1" in
    -d) mode=d ;;
    -e) mode=e ;;
    --extract) extract=$2; shift ;;
    --age|--input-type|--output-type) shift ;;
    *) file=$1 ;;
  esac
  shift
done
if [ "$mode" = e ]; then cat "$file"; exit 0; fi
[ -n "${SOPS_AGE_KEY_FILE:-}" ] || { echo "sops stub: no SOPS_AGE_KEY_FILE" >&2; exit 9; }
[ -f "$file" ] || { echo "sops stub: no file $file" >&2; exit 4; }
if [ -z "$extract" ]; then cat "$file"; exit 0; fi
key=$(printf '%s' "$extract" | sed -E 's/^\["(.*)"\]$/\1/')
jq -j --arg k "$key" '.[$k] // error("missing key")' "$file"
