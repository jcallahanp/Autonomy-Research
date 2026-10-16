#!/bin/bash
# setup-root.sh --install: /opt/engineer, the research-agent subset, state and log dirs, ACLs (sourced).
set -euo pipefail

RESEARCH_SKILLS="interview research tool-scan repo-triage spike system-map setup"
RESEARCH_AGENTS="researcher synthesizer verifier spike-worker"

# source_sha: the commit of the checkout SRC sits in, else a hash of SRC's files.
source_sha() {
  local sha
  if sha=$(git -C "$SRC" rev-parse --verify -q HEAD 2>/dev/null) && [[ $sha =~ ^[0-9a-f]{40}$ ]]; then
    echo "$sha"
  else
    echo "tree-$( (cd "$SRC" && find . -type f ! -path '*/__pycache__/*' ! -name '*.pyc' -print0 \
      | sort -z | xargs -0 sha256sum) | sha256sum | cut -c1-40)"
  fi
}

# install_tree: copy SRC to /opt/engineer (root-owned), swap in the empty plugin hooks, add the
# research-agent skills and agents, record SOURCE_SHA.
install_tree() {
  local stage="$OPT.setup-root.new" s a sha
  case "$OPT/" in "$SRC/"*) die "--prefix puts /opt/engineer inside --src";; esac
  [ -d "$RESEARCH_PLUGIN/skills" ] && [ -d "$RESEARCH_PLUGIN/agents" ] \
    || die "no research-agent plugin at $RESEARCH_PLUGIN (use --research-plugin)"
  sha=$(source_sha)
  rm -rf "$stage"
  mkdir -p "$(dirname "$OPT")"
  cp -R --preserve=mode "$SRC" "$stage"
  find "$stage" \( -name __pycache__ -o -name '*.pyc' -o -name '*.setup-root.tmp' \) -prune -exec rm -rf {} +
  rm -f "$stage/LOCKED"
  # The plugin's own hooks stay off until --lock puts the managed hooks in place.
  mkdir -p "$stage/plugin/hooks" "$stage/plugin/skills" "$stage/plugin/agents"
  echo '{"hooks": {}}' > "$stage/plugin/hooks/hooks.json"
  for s in $RESEARCH_SKILLS; do
    [ -f "$RESEARCH_PLUGIN/skills/$s/SKILL.md" ] || die "research skill $s missing from $RESEARCH_PLUGIN"
    [ ! -e "$stage/plugin/skills/$s" ] || die "engineer plugin already has a skill named $s"
    cp -R --preserve=mode "$RESEARCH_PLUGIN/skills/$s" "$stage/plugin/skills/$s"
  done
  for a in $RESEARCH_AGENTS; do
    [ -f "$RESEARCH_PLUGIN/agents/$a.md" ] || die "research agent $a missing from $RESEARCH_PLUGIN"
    [ ! -e "$stage/plugin/agents/$a.md" ] || die "engineer plugin already has an agent named $a"
    cp --preserve=mode "$RESEARCH_PLUGIN/agents/$a.md" "$stage/plugin/agents/$a.md"
  done
  echo "$sha" > "$stage/SOURCE_SHA"
  chmod -R u+rwX,go+rX,go-w "$stage"
  rm -rf "$OPT"
  mv "$stage" "$OPT"
  run chown -R root:root "$OPT"
}

# install_dirs: state, config, browser profile, projects and log dirs.
install_dirs() {
  local d m="$P/var/lib/engineer/mirrors" pr="$P/home/engineer/projects"
  make_dir "$P/var/lib/engineer" 0755 supervisor:supervisor
  for d in records approvals checks audit-clones; do
    make_dir "$P/var/lib/engineer/$d" 0755 supervisor:supervisor
  done
  make_dir "$P/var/lib/engineer/spool" 1770 supervisor:engineer
  # Bare mirrors: the broker's sync-mirror job writes them; run-task (engineer) reads them; setgid keeps group engineer.
  make_dir "$m" 2750 secretbroker:engineer
  # supervisor reads them too (records.ensure clones engineer-records from a mirror); never writes.
  # Set by the owner, with a physical walk (-P), so no symlink inside is followed.
  run runuser -u secretbroker -- setfacl -m u:supervisor:rX "$m"
  run runuser -u secretbroker -- setfacl -R -P -d -m u:supervisor:rX "$m"
  make_dir "$ETC" 0755
  make_dir "$P/home/engineer/.engineer" 0700 engineer:engineer
  make_dir "$P/home/engineer/.engineer/chrome-profile" 0700 engineer:engineer
  make_dir "$pr" 0755 engineer:engineer
  # The egress proxy (user egress) appends egress-denied.log; sticky, so it cannot remove others' logs.
  make_dir "$P/var/log/engineer" 1775 root:egress
  egress_log
  # supervisor reads (never writes) the projects; default ACLs cover files made later. engineer owns
  # the tree, so engineer sets the ACLs: root never walks a tree the model can write.
  run runuser -u engineer -- setfacl -m u:supervisor:x "$P/home/engineer"
  run runuser -u engineer -- setfacl -R -P -m u:supervisor:rX "$pr"
  run runuser -u engineer -- setfacl -R -P -d -m u:supervisor:rX "$pr"
}

# egress_log: the proxy's deny log, made by root in a dir egress can write, so never through a symlink.
egress_log() {
  local log="$P/var/log/engineer/egress-denied.log"
  fsafe check "$log" -
  [ -e "$log" ] || [ -L "$log" ] || printf '' | fsafe write "$log" 0640
  fsafe chmod "$log" 0640
  own egress:egress "$log"
}
