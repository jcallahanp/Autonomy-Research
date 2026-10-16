#!/usr/bin/env python3
"""Filesystem steps for setup-root.sh that never follow a symlink planted by a non-root user.

Usage: fsafe.py ROOT OP PATH [ARG]
  ROOT   the trusted top (the --prefix, or /); PATH must be ROOT itself or under it
  mkdir PATH MODE        make PATH and any missing parents (0755), then chmod MODE
  chmod PATH MODE        chmod an existing PATH (file or directory)
  chown PATH USER:GROUP  chown an existing PATH (file or directory)
  check PATH -           refuse when an existing component of PATH is an untrusted symlink
  write PATH MODE        write stdin to PATH atomically with MODE (a temp file made O_EXCL beside it)
Each component below ROOT is opened relative to its parent's descriptor with O_NOFOLLOW, and the
mode or owner is set on the final descriptor, so a component swapped for a symlink between a check
and the change cannot redirect it. A symlink is followed only when it and the directory holding it
are owned by root and that directory is not group- or world-writable (as /lib -> usr/lib is).
Exit 0 done, 1 refused (an untrusted symlink, or not a directory where one is needed), 2 usage.
"""
import errno
import grp
import os
import pwd
import stat
import sys

DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def refuse(msg):
    print(f"setup-root: {msg}; refusing", file=sys.stderr)
    sys.exit(1)


def trusted_link(parent_fd, name):
    """True when name is a root-owned symlink in a root-owned, not group/world-writable directory."""
    p, link = os.fstat(parent_fd), os.lstat(name, dir_fd=parent_fd)
    return (stat.S_ISLNK(link.st_mode) and link.st_uid == 0 and p.st_uid == 0
            and not p.st_mode & (stat.S_IWGRP | stat.S_IWOTH))


def step(parent_fd, name, where, flags=DIR_FLAGS):
    """Open name under parent_fd without following an untrusted symlink."""
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except OSError as e:
        if e.errno not in (errno.ELOOP, errno.ENOTDIR, errno.EMLINK):
            raise
        if flags & os.O_DIRECTORY and trusted_link(parent_fd, name):
            return os.open(name, flags & ~os.O_NOFOLLOW, dir_fd=parent_fd)
        refuse(f"{where} is a symlink or not a directory")


def walk(root, path, make):
    """(fd of the parent of the last component, last name); creates missing directories if make."""
    rel = os.path.relpath(path, root)
    if rel == ".":
        return os.open(root, DIR_FLAGS & ~os.O_NOFOLLOW), "."
    parts = rel.split("/")
    if rel.startswith("..") or os.path.isabs(rel) or "" in parts:
        print(f"setup-root: {path} is not under {root}", file=sys.stderr)
        sys.exit(2)
    fd, where = os.open(root, DIR_FLAGS & ~os.O_NOFOLLOW), root.rstrip("/")
    for i, name in enumerate(parts[:-1] if not make else parts):
        where += "/" + name
        if make:
            try:
                os.mkdir(name, 0o755, dir_fd=fd)
            except FileExistsError:
                pass
        nfd = step(fd, name, where)
        os.close(fd)
        fd = nfd
    if make:
        return fd, "."
    return fd, parts[-1]


def check(root, path):
    """Walk the existing components of path; a missing one ends the walk."""
    parts = os.path.relpath(path, root).split("/")
    if parts[0] == "..":
        print(f"setup-root: {path} is not under {root}", file=sys.stderr)
        sys.exit(2)
    fd, where = os.open(root, DIR_FLAGS & ~os.O_NOFOLLOW), root.rstrip("/")
    names = [p for p in parts if p != "."]
    for i, name in enumerate(names):
        where += "/" + name
        try:
            st = os.lstat(name, dir_fd=fd)
        except FileNotFoundError:
            break
        if i == len(names) - 1 and not stat.S_ISLNK(st.st_mode):
            break  # the last component may be a file
        nfd = step(fd, name, where)
        os.close(fd)
        fd = nfd
    os.close(fd)
    return 0


def open_final(parent, name, where):
    if name == ".":
        return os.dup(parent)
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    return step(parent, name, where, flags)


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    root, op, path, arg = argv
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    if op == "write":
        parent, name = walk(root, path, make=False)
        if name == ".":
            refuse(f"{path} is the root")
        tmp = name + ".setup-root.tmp"
        try:
            os.unlink(tmp, dir_fd=parent)
        except FileNotFoundError:
            pass
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                     dir_fd=parent)
        with os.fdopen(fd, "wb") as f:
            f.write(sys.stdin.buffer.read())
            os.fchmod(f.fileno(), int(arg, 8))
        os.replace(tmp, name, src_dir_fd=parent, dst_dir_fd=parent)
        return 0
    if op == "check":
        return check(root, path)
    if op not in ("mkdir", "chmod", "chown"):
        print(f"fsafe.py: unknown op {op}", file=sys.stderr)
        return 2
    parent, name = walk(root, path, make=op == "mkdir")
    fd = open_final(parent, name, path)
    try:
        if op == "chown":
            user, _, group = arg.partition(":")
            os.fchown(fd, pwd.getpwnam(user).pw_uid, grp.getgrnam(group or user).gr_gid)
        else:
            os.fchmod(fd, int(arg, 8))
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
