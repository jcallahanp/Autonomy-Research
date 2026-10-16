"""Print a Markdown file's YAML frontmatter as JSON, plus "_lines" and "_body" (test helper).

Usage: python3 fm.py FILE   (exit 1 when the file has no frontmatter or it is not a mapping)
"""
import json
import sys

import yaml


def main(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        print(f"{path}: no frontmatter", file=sys.stderr)
        return 1
    end = text.find("\n---\n", 4)
    if end < 0:
        print(f"{path}: frontmatter not closed", file=sys.stderr)
        return 1
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        print(f"{path}: frontmatter is not a mapping", file=sys.stderr)
        return 1
    data["_lines"] = len(text.splitlines())
    data["_body"] = text[end + 5:]
    print(json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
