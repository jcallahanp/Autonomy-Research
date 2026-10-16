# Shared helpers for tests/*.sh. Source this file; do not run it.

# fm FILE KEY: print the YAML frontmatter value for KEY, or nothing.
# Handles CRLF, quoted values, and block scalars (> >- | |- etc., joined with
# spaces). A file whose frontmatter has no closing --- counts as having none.
fm() {
  awk -v k="$2" '
    { sub(/\r$/, ""); line[NR] = $0 }
    END {
      if (line[1] != "---") exit
      close_at = 0
      for (i = 2; i <= NR; i++) if (line[i] == "---") { close_at = i; break }
      if (!close_at) exit
      for (i = 2; i < close_at; i++) {
        if (index(line[i], k ":") != 1) continue
        v = substr(line[i], length(k) + 2)
        sub(/^[ \t]+/, "", v); sub(/[ \t]+$/, "", v)
        if (v ~ /^[>|][+-]?$/) {
          v = ""
          for (j = i + 1; j < close_at && (line[j] ~ /^[ \t]/ || line[j] == ""); j++) {
            t = line[j]; sub(/^[ \t]+/, "", t); sub(/[ \t]+$/, "", t)
            if (t != "") v = (v == "" ? t : v " " t)
          }
        } else if (v ~ /^".*"$/ || v ~ /^\047.*\047$/) {
          v = substr(v, 2, length(v) - 2)
        }
        print v
        exit
      }
    }' "$1"
}
