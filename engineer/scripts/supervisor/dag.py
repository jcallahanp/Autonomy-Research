"""tasks.json as a DAG: load and validate, find a cycle, list the ready tasks in file order."""
import json
from pathlib import Path

from eng import schema

ROOT = Path(__file__).resolve().parents[2]


def load(path) -> list:
    """Read and validate docs/plan/tasks.json; raise ValueError listing every error."""
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise ValueError(f"tasks.json unreadable: {type(e).__name__}: {e}") from None
    errors = schema.validate(data, schema.load(ROOT, "tasks"))
    if not errors:
        seen = set()
        for t in data["tasks"]:
            if t["id"] in seen:
                errors.append(f"duplicate task id {t['id']!r}")
            seen.add(t["id"])
    if errors:
        raise ValueError("tasks.json invalid: " + "; ".join(errors[:10]))
    return data["tasks"]


def _graph(tasks) -> dict:
    ids = {t["id"] for t in tasks}
    graph = {}
    for t in tasks:
        unknown = [d for d in t["depends_on"] if d not in ids]
        if unknown:
            raise ValueError(f"task {t['id']} depends on unknown task(s): {', '.join(unknown)}")
        graph[t["id"]] = list(t["depends_on"])
    return graph


def find_cycle(tasks) -> list | None:
    """Return one cycle as [a, b, ..., a], or None. Unknown depends_on ids raise ValueError."""
    graph = _graph(tasks)
    colour = {tid: 0 for tid in graph}  # 0 new, 1 on stack, 2 finished
    for start in graph:
        if colour[start]:
            continue
        stack = [(start, iter(graph[start]))]
        path = [start]
        colour[start] = 1
        while stack:
            node, deps = stack[-1]
            nxt = next(deps, None)
            if nxt is None:
                colour[node] = 2
                stack.pop()
                path.pop()
            elif colour[nxt] == 1:
                return path[path.index(nxt):] + [nxt]
            elif colour[nxt] == 0:
                colour[nxt] = 1
                stack.append((nxt, iter(graph[nxt])))
                path.append(nxt)
    return None


def ready(tasks, done: set, blocked: set, running: set) -> list:
    """Ids whose dependencies are all done and which are not done, blocked or running, in file order."""
    graph = _graph(tasks)
    skip = set(done) | set(blocked) | set(running)
    return [tid for tid, deps in graph.items() if tid not in skip and all(d in done for d in deps)]
