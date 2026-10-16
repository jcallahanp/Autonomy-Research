"""run-task's run of one argv: the run-result fields from its exit code, output and (claude) JSON result line."""
import json
import subprocess
from pathlib import Path

from runtask import worktree

TAIL_LINES = 200


def run(profile: str, argv: list, wt: Path, env: dict, base_ref: str) -> dict:
    p = subprocess.run(argv, cwd=wt, env=env, stdin=subprocess.DEVNULL, capture_output=True)
    out, err = p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")
    lines = (out + ("\n" if out and not out.endswith("\n") else "") + err).splitlines()
    res = {"profile": profile, "exit_code": p.returncode, "timed_out": p.returncode in (124, 137),
           "session_id": None, "cost_usd": None, "num_turns": None, "subtype": None,
           "is_error": p.returncode != 0, "output_tail": "\n".join(lines[-TAIL_LINES:]), "permission_denials": []}
    if profile != "check":
        last = next((ln for ln in reversed(out.splitlines()) if ln.strip()), "")
        try:
            r = json.loads(last)
        except ValueError:
            r = None
        if isinstance(r, dict):
            res.update(session_id=r.get("session_id"), cost_usd=r.get("total_cost_usd"),
                       num_turns=r.get("num_turns"), subtype=r.get("subtype"),
                       permission_denials=r.get("permission_denials") or [])
            if isinstance(r.get("structured_output"), dict):
                res["structured_output"] = r["structured_output"]
            res["is_error"] = bool(r.get("is_error")) or p.returncode != 0
        else:
            res["is_error"] = True
    res.update(worktree.shas(wt, base_ref))
    return res
