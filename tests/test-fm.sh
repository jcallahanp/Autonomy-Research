#!/bin/bash
# Self-test for the frontmatter parser in tests/lib.sh.
cd "$(dirname "$0")/.." || exit 1
. tests/lib.sh
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fails=0
expect() { # label file key want
  got=$(fm "$2" "$3")
  if [ "$got" = "$4" ]; then echo "ok   $1 $3"; else echo "FAIL $1 $3: want [$4] got [$got]"; fails=$((fails+1)); fi
}

printf -- '---\nname: foo\ndescription: Plain text here\n---\nbody\n' > "$tmp/plain.md"
printf -- '---\nname: "foo"\ndescription: '"'"'Single quoted'"'"'\n---\nbody\n' > "$tmp/quoted.md"
printf -- '---\nname: foo\ndescription: >-\n  Folded line one\n  and line two\nmodel: sonnet\n---\nbody\n' > "$tmp/folded.md"
printf -- '---\nname: foo\ndescription: |\n  Literal one\n  literal two\n---\nbody\n' > "$tmp/literal.md"
printf -- '---\r\nname: foo\r\ndescription: Crlf text\r\n---\r\nbody\r\n' > "$tmp/crlf.md"
printf -- '---\nname: foo\ndescription: No close\nbody text\nname: bar\n' > "$tmp/noclose.md"
printf -- 'name: foo\n---\n' > "$tmp/nostart.md"
printf -- '---\nname: foo\n---\ndescription: in body\n' > "$tmp/bodykey.md"

expect plain    "$tmp/plain.md"   name foo
expect plain    "$tmp/plain.md"   description "Plain text here"
expect quoted   "$tmp/quoted.md"  name foo
expect quoted   "$tmp/quoted.md"  description "Single quoted"
expect folded   "$tmp/folded.md"  description "Folded line one and line two"
expect folded   "$tmp/folded.md"  model sonnet
expect literal  "$tmp/literal.md" description "Literal one literal two"
expect crlf     "$tmp/crlf.md"    name foo
expect crlf     "$tmp/crlf.md"    description "Crlf text"
expect noclose  "$tmp/noclose.md" name ""
expect noclose  "$tmp/noclose.md" description ""
expect nostart  "$tmp/nostart.md" name ""
expect bodykey  "$tmp/bodykey.md" description ""

[ "$fails" -eq 0 ] && echo "test-fm.sh: all pass" || { echo "test-fm.sh: $fails failure(s)"; exit 1; }
