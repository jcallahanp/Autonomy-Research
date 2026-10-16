"""RUN_STATUS.json: the night's state, always whole on disk (temp file, fsync, os.replace)."""
import json
import os
import tempfile
from pathlib import Path

from eng import schema
from supervisor.events import now_iso

ROOT = Path(__file__).resolve().parents[2]
TERMINAL = ("done", "blocked", "stopped_by_bound", "crashed")


def write(path, state: str, **fields) -> dict:
    """Validate against run-status.schema.json, then replace the file atomically; return the data."""
    data = {"state": state, **fields}
    data.setdefault("updated", now_iso())
    errors = schema.validate(data, schema.load(ROOT, "run-status"))
    if errors:
        raise ValueError("invalid RUN_STATUS: " + "; ".join(errors))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".RUN_STATUS.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    return data


def read(path) -> dict | None:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None
