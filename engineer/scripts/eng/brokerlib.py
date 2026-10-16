"""Helpers for secret-broker jobs (run as BROKER_USER through agent-run).

A secret value never goes on a command line, into a log line or into an error message.
"""
import datetime
import getpass
import os
import pwd
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from eng import conf as _conf

ROOT = Path(__file__).resolve().parents[2]
_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_JOB = re.compile(r"^[a-z][a-z0-9-]*$")
_USER = re.compile(r"^[a-z_][a-z0-9_-]*$")
_LOOPBACK = {"127.0.0.1", "localhost", "::1"}


def caller(conf: dict = None) -> str:
    """The user who asked: SUDO_USER when running as BROKER_USER, else the current user."""
    conf = conf if conf is not None else _conf.load(ROOT)
    effective = pwd.getpwuid(os.geteuid()).pw_name
    if effective == conf.get("BROKER_USER"):
        return os.environ.get("SUDO_USER") or effective
    return getpass.getuser()


def secret(conf: dict, name: str) -> str:
    """Decrypt one value from SECRETS_FILE with sops; raise ValueError on a bad name, RuntimeError on failure."""
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise ValueError("secret name must match ^[A-Z][A-Z0-9_]*$")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "SOPS_AGE_KEY_FILE": conf["AGE_KEY_FILE"]}
    proc = subprocess.run(["sops", "-d", "--extract", f'["{name}"]', conf["SECRETS_FILE"]],
                          capture_output=True, env=env, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"sops could not decrypt {name} (exit {proc.returncode})")
    return proc.stdout.decode().rstrip("\n")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects: urllib would resend auth headers to the new host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http(method: str, url: str, headers: dict, body, timeout: int = 30) -> tuple:
    """(status, body bytes). https only, except plain http to loopback (tests). Honours HTTPS_PROXY."""
    parts = urllib.parse.urlsplit(url)
    loopback = parts.hostname in _LOOPBACK
    if parts.scheme != "https" and not (parts.scheme == "http" and loopback):
        raise ValueError(f"refusing non-https URL for host {parts.hostname!r}")
    handlers = [_NoRedirect()]
    if loopback:
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, data=body, headers=dict(headers or {}), method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()
        finally:
            e.close()


def log(conf: dict, job: str, exit_code: int) -> None:
    """Append `ts caller job exit` to BROKER_STATE_DIR/agent-run.log (never arguments)."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    who = caller(conf)
    job = job if isinstance(job, str) and _JOB.fullmatch(job) else "invalid-job"
    state = Path(conf["BROKER_STATE_DIR"])
    state.mkdir(parents=True, exist_ok=True)
    with open(state / "agent-run.log", "a") as f:
        f.write(f"{ts} {who if _USER.fullmatch(who) else 'unknown'} {job} {int(exit_code)}\n")
