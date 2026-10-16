"""A small JSON Schema checker for the engineer's own schema files (no $ref).

Supports: type (string or list), required, properties, additionalProperties (false or a schema),
enum, items, minimum, minLength, maxLength, maxItems, pattern (re.search, as in JSON Schema).
"""
import json
import re
from pathlib import Path

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def load(root: Path, name: str) -> dict:
    """Read <root>/templates/schemas/<name>.schema.json."""
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise ValueError(f"bad schema name: {name!r}")
    return json.loads((Path(root) / "templates" / "schemas" / f"{name}.schema.json").read_text())


def validate(instance, schema: dict) -> list:
    """Return a list of error lines; empty means valid."""
    errors = []
    _check(instance, schema, "$", errors)
    return errors


def _check(v, s: dict, at: str, errors: list) -> None:
    if "type" in s:
        types = s["type"] if isinstance(s["type"], list) else [s["type"]]
        if not any(_TYPES[t](v) for t in types):
            errors.append(f"{at}: expected {'|'.join(types)}, got {type(v).__name__}")
            return
    if "enum" in s and not any(v == e and type(v) is type(e) for e in s["enum"]):
        errors.append(f"{at}: {v!r} not one of {s['enum']}")
    if isinstance(v, str):
        if "minLength" in s and len(v) < s["minLength"]:
            errors.append(f"{at}: shorter than {s['minLength']}")
        if "maxLength" in s and len(v) > s["maxLength"]:
            errors.append(f"{at}: longer than {s['maxLength']}")
        if "pattern" in s and not re.search(s["pattern"], v):
            errors.append(f"{at}: does not match {s['pattern']}")
    if _TYPES["number"](v) and "minimum" in s and v < s["minimum"]:
        errors.append(f"{at}: below minimum {s['minimum']}")
    if isinstance(v, list):
        if "maxItems" in s and len(v) > s["maxItems"]:
            errors.append(f"{at}: more than {s['maxItems']} items")
        if "items" in s:
            for i, item in enumerate(v):
                _check(item, s["items"], f"{at}[{i}]", errors)
    if isinstance(v, dict):
        _check_object(v, s, at, errors)


def _check_object(v: dict, s: dict, at: str, errors: list) -> None:
    for key in s.get("required", []):
        if key not in v:
            errors.append(f"{at}: missing required {key!r}")
    props = s.get("properties", {})
    extra = s.get("additionalProperties", True)
    for key, item in v.items():
        if key in props:
            _check(item, props[key], f"{at}.{key}", errors)
        elif extra is False:
            errors.append(f"{at}: unexpected property {key!r}")
        elif isinstance(extra, dict):
            _check(item, extra, f"{at}.{key}", errors)
