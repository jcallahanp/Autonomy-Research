"""Protected-path guard: file tools and Bash write forms (Review Focus 5)."""
import os
import unittest

from hookfix import HookCase


class ProtectedTest(HookCase):
    def write_ev(self, path, tool="Write"):
        return self.pre(tool, {"file_path": str(path), "content": "x\n"})

    def test_protected_write_new_unit_test_allowed(self):
        self.assertAllowed(self.write_ev(self.proj / "tests/unit/test_new.py"))

    def test_protected_edit_existing_test_denied(self):
        r = self.pre("Edit", {"file_path": str(self.proj / "tests/unit/test_old.py"),
                              "old_string": "pass", "new_string": "assert 1"})
        self.assertDenied(r, "tests/**")

    def test_protected_write_acceptance_denied(self):
        self.assertDenied(self.write_ev(self.proj / "tests/acceptance/x.py"), "tests/acceptance/**")

    def test_protected_other_file_tools_denied(self):
        self.assertDenied(self.pre("MultiEdit", {"file_path": str(self.proj / ".claude/settings.json"),
                                                 "edits": []}))
        self.assertDenied(self.pre("NotebookEdit", {"notebook_path": str(self.proj / "tests/acceptance/n.ipynb"),
                                                    "new_source": "x"}))
        self.assertDenied(self.write_ev(self.proj / "CLAUDE.md"))

    def test_protected_symlink_into_acceptance_denied(self):
        os.symlink("tests/acceptance", self.proj / "link")
        self.assertDenied(self.write_ev(self.proj / "link/x.py"))
        self.assertDenied(self.bash("echo x > link/b.py"))
        self.assertDenied(self.bash("cp src/a.py link/"))

    def test_protected_symlink_out_of_project_denied(self):
        os.symlink(str(self.tmp), self.proj / "out")
        self.assertDenied(self.write_ev(self.proj / "out/x.py"), "outside project")

    def test_protected_parent_path_other_project_denied(self):
        other = self.make_project(self.proj.parent / "other")
        self.assertDenied(self.write_ev(self.proj / "../other/CLAUDE.md"), "outside project")
        self.assertDenied(self.write_ev(self.proj / "../other/src/new.py"), "outside project")
        self.assertDenied(self.bash("echo x > ../other/src/a.py"), "another project")
        self.assertDenied(self.bash(f"echo x > {other}/src/a.py"), "another project")
        self.assertDenied(self.bash("cd ../other && echo x > src/a.py"), "another project")

    def test_protected_absolute_path_other_project_denied(self):
        other = self.make_project(self.proj.parent / "other")
        self.assertDenied(self.write_ev(other / "src/a.py"), "outside project")
        self.assertDenied(self.write_ev(other / "tests/acceptance/a.py"), "outside project")

    def test_protected_relative_path_resolves_from_cwd(self):
        self.assertDenied(self.pre("Write", {"file_path": "tests/acceptance/r.py", "content": ""}))
        self.assertAllowed(self.pre("Write", {"file_path": "src/r.py", "content": ""}))

    def test_protected_git_dir_denied(self):
        self.assertDenied(self.write_ev(self.proj / ".git/config"), ".git")
        self.assertDenied(self.bash("echo '[core]' >> .git/config"), ".git")
        self.assertDenied(self.bash("cp hook .git/hooks/pre-commit"), ".git")

    def test_protected_bash_redirect_denied(self):
        self.assertDenied(self.bash("echo x > tests/acceptance/a.py"))
        self.assertDenied(self.bash("echo x>tests/acceptance/a.py"))
        self.assertDenied(self.bash("echo x >> tests/unit/test_old.py"))
        self.assertDenied(self.bash("ls && printf x 2>&1 > CLAUDE.md"))

    def test_protected_bash_write_commands_denied(self):
        cmds = ("cp src/a.py tests/acceptance/", "cp src/a.py tests/acceptance",
                    "rm -rf tests/acceptance", "rm -rf tests", "rm tests/unit/test_old.py",
                    "sed -i s/a/b/ tests/unit/test_old.py", "sed --in-place=.b s/a/b/ CLAUDE.md",
                    "echo x | tee .claude/settings.json", "mv src/a.py CLAUDE.md",
                    "ln -s /tmp tests/acceptance/y", "cp -t tests/acceptance src/a.py",
                    "ln -s src/a.py --target-directory=tests/acceptance", "install src/a.py CLAUDE.md", "chmod +x .github/workflows/x.yml",
                    "truncate -s0 tests/unit/test_old.py", "dd if=/dev/zero of=tests/unit/test_old.py",
                    "env FOO=1 cp src/a.py .github/x", "bash -c 'echo x > tests/acceptance/q.py'",
                    "touch src/z.py; rm -f tests/acceptance/a.py")
        for cmd, r in self.many(self.bash, cmds):
            with self.subTest(cmd=cmd):
                self.assertDenied(r)

    def test_protected_bash_reads_and_safe_writes_allowed(self):
        cmds = ("cat tests/acceptance/a.py", "cat tests/acceptance/a.py | head -5 > notes.txt",
                    "grep -r x tests/ > /dev/null 2>&1", "pytest tests/ > out.txt 2>&1",
                    "cp src/a.py src/b.py", "sed -n 1p tests/unit/test_old.py",
                    "cp src/a.py tests/unit/test_new.py", "rm -rf build", "mv src/a.py src/c.py",
                    "ln -sf ../src/a.py src/link.py", "cp tests/unit/test_old.py /tmp/copy.py",
                    "cp -t src tests/acceptance/a.py", "chmod 644 src/a.py",
                    "git commit -m \"$(cat <<'EOF'\nfix: don't touch tests\nEOF\n)\"")
        for cmd, r in self.many(self.bash, cmds):
            with self.subTest(cmd=cmd):
                self.assertAllowed(r)

    def test_protected_read_tool_allowed(self):
        self.assertAllowed(self.pre("Read", {"file_path": str(self.proj / "tests/acceptance/a.py")}))

    def test_protected_no_project_denied(self):
        outside = self.tmp / "loose"
        outside.mkdir(exist_ok=True)
        r = self.pre("Write", {"file_path": str(outside / "x.py"), "content": ""}, cwd=outside)
        self.assertDenied(r, "no project")


if __name__ == "__main__":
    unittest.main()
