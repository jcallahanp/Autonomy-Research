# Shared setup for tests/engineer/setup-root/test_*.sh. Source it after ../lib.sh.
#   SRC   a mk_root copy of engineer/ (the --src) with fixture pins, egress lists and managed hooks
#   P     the --prefix every write goes under
#   SR    command prefix: bash <SRC>/scripts/setup-root.sh
#   sr MODE...  runs SR with --dry-run --prefix P --src SRC --research-plugin <repo>/plugin
SRC=$(mk_root "$T/src")
P="$T/fs"
SR=(bash "$SRC/scripts/setup-root.sh")
HEX64=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
FPR=0123456789ABCDEF0123456789ABCDEF01234567

printf 'sops\thttps://example.invalid/sops-test.linux.amd64\t%s\troot\ntool\thttps://example.invalid/tool.tar.gz\t%s\tuser\n' \
  "$HEX64" "$HEX64" > "$SRC/templates/release-pins.txt"
{
  echo '# fixture'
  printf 'testrepo\thttps://example.invalid/key.gpg\t%s\tdeb [signed-by=/etc/apt/keyrings/testrepo.gpg] https://example.invalid/apt stable main\n' "$FPR"
} > "$SRC/templates/apt-repos.txt"
printf '# fixture install list\napi.anthropic.com\nregistry.npmjs.org\n' > "$SRC/templates/egress-install.txt"
printf '# fixture runtime list\napi.anthropic.com\napi.telegram.org\n' > "$SRC/templates/egress-allowlist.txt"
cat > "$SRC/templates/managed-hooks.json" <<'JSON'
{"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "python3 /opt/engineer/plugin/hooks/pre_tool.py", "timeout": 10}]}]}}
JSON
mkdir -p "$SRC/plugin/hooks"
echo '{"hooks": {"SessionStart": []}}' > "$SRC/plugin/hooks/hooks.json"

sr() { "${SR[@]}" "$@" --dry-run --prefix "$P" --src "$SRC" --research-plugin "$REPO/plugin"; }

# tree_sum DIR: one hash over every path, mode and file content under DIR
tree_sum() {
  (cd "$1" && find . -printf '%p %m %y\n' | sort && find . -type f -print0 | sort -z | xargs -0 sha256sum) | sha256sum
}
