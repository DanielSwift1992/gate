#!/usr/bin/env python3
"""Exercise the stamp through a real merge, drift and a short registry."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "bin/battery_count.py"
spec = importlib.util.spec_from_file_location("battery_count", TOOL)
count = importlib.util.module_from_spec(spec)
spec.loader.exec_module(count)


def run(root, *args, ok=0):
    result = subprocess.run(args, cwd=root, capture_output=True, text=True)
    assert result.returncode == ok, (args, result.returncode, result.stdout, result.stderr)
    return result.stdout + result.stderr


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def command(root, *args, ok=0):
    return run(root, sys.executable, "bin/battery_count.py", *args, ok=ok)


def main():
    with tempfile.TemporaryDirectory(prefix="battery-count-") as scratch:
        root = Path(scratch)
        (root / "bin").mkdir()
        shutil.copyfile(TOOL, root / "bin/battery_count.py")
        # The fixture has one worktree. Both branches stamp the same next
        # number; git merges the README cleanly while merging both new checks.
        source = '''import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
from battery_count import Registry, stamp
def main():
    root = Path(__file__).resolve().parent.parent
    stamp(root, check=True)
    S = []
    S.append(("base left", True))
    # LEFT
'''
        source += "\n" * 12
        source += '''    S.append(("base right", True))
    # RIGHT
    assert len(S) == Registry(root).count()
    assert all(ok for _, ok in S)
    print("ALL GREEN", len(S))
main()
'''
        write(root, "tests/smoke.py", source)
        write(root, "README.md", "tests/smoke.py   the battery: 0 checks this repository holds itself\n")
        assert "2 registered" in command(root)
        original = (root / "README.md").read_bytes()
        command(root)
        assert original == (root / "README.md").read_bytes()
        run(root, "git", "init", "-q")
        run(root, "git", "config", "user.name", "Battery Fixture")
        run(root, "git", "config", "user.email", "battery@example.invalid")
        run(root, "git", "config", "commit.gpgsign", "false")
        run(root, "git", "config", "core.hooksPath", str(root / "no-hooks"))
        run(root, "git", "add", "README.md", "tests/smoke.py", "bin/battery_count.py")
        run(root, "git", "commit", "-qm", "tests: base registry")
        base = run(root, "git", "rev-parse", "HEAD").strip()
        for branch, marker in (("left", "LEFT"), ("right", "RIGHT")):
            run(root, "git", "checkout", "-qb", branch, base)
            write(root, "tests/smoke.py", source.replace("    # " + marker,
                  f'    S.append(("new {branch}", True))\n    # {marker}'))
            assert "3 registered" in command(root)
            run(root, "git", "add", "README.md", "tests/smoke.py")
            run(root, "git", "commit", "-qm", "tests: add " + branch)
        run(root, "git", "checkout", "-q", "left")
        run(root, "git", "merge", "-q", "--no-edit", "right")
        merged = (root / "tests/smoke.py").read_text()
        assert "new left" in merged and "new right" in merged
        assert "registry has 4" in command(root, "--check", ok=1)
        assert "4 registered" in command(root)  # the single repair command
        assert "ALL GREEN 4" in run(root, sys.executable, "tests/smoke.py")
        print("PASS two real branches merge; one stamp repairs 3 to 4; battery green")

        good = (root / "README.md").read_text()
        write(root, "README.md", good.replace("4 checks", "900 checks"))
        before = (root / "README.md").read_bytes()
        assert count.REPAIR in command(root, "--check", ok=1)
        assert before == (root / "README.md").read_bytes()
        command(root)
        assert (root / "README.md").read_text() == good
        for invalid in ("no stamp\n", good + good):
            write(root, "README.md", invalid)
            assert "expected one battery stamp" in command(root, ok=1)
        write(root, "README.md", good)
        print("PASS manual, absent and duplicate stamps refuse with a repair address")

        write(root, "tests/smoke.py", '''import shutil
def main():
    S = []
    for label in ["a", "b", "c"]:
        S.append((label, True))
    if shutil.which("swiftc"):
        S.append(("native", True))
    if optional_reader:
        S.append(("reader", True))
    else:
        S.append(("reader", False))
''')
        assert count.Registry(root).count() == 5
        assert count.Registry(root, swift=False).count() == 4
        write(root, "tests/smoke.py", 'def main():\n    for case in unknown():\n        S.append(case)\n')
        assert "tests/smoke.py:2:" in command(root, ok=1)
        write(root, "tests/smoke.py", 'def main():\n    if dynamic:\n        S.append(("hidden", True))\n')
        assert "conditional registration changes the count" in command(root, ok=1)
        write(root, "tests/smoke.py", 'def main():\n    for case in [1, 2]:\n        S.append(case)\n        break\n')
        assert "may exit" in command(root, ok=1)
        print("PASS case tables and short registration; unreadable control flow refuses")

        # The actual battery must reject a manual stamp before a compiler or
        # court is needed. Carry only the files its registry reads, no binary.
        shutil.copyfile(ROOT / "tests/smoke.py", root / "tests/smoke.py")
        shutil.copyfile(ROOT / "tests/d65.py", root / "tests/d65.py")
        shutil.copytree(ROOT / "stdlib", root / "stdlib")
        (root / "tests/fixtures").mkdir()
        name = "bench-palette-before-dag.swift"
        shutil.copyfile(ROOT / "tests/fixtures" / name, root / "tests/fixtures" / name)
        write(root, "README.md", good.replace("4 checks", "900 checks"))
        said = run(root, sys.executable, "tests/smoke.py", ok=1)
        assert "FAIL README.md:" in said and count.REPAIR in said and "RED" in said
        assert "building" not in said
        # The footer still refuses a short run and states what was omitted.
        text = (ROOT / "tests/smoke.py").read_text()
        footer = text[text.index('    # A short run names'):text.index('    # the names have been printed')]
        env = dict(Registry=count.Registry, HERE=str(ROOT), S=[])
        env["shutil"] = type("NoSwift", (), {"which": staticmethod(lambda _: None)})
        import contextlib
        import io
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile("if True:\n" + footer, "smoke-short-footer", "exec"), env)
        assert "this run is short" in output.getvalue()
        assert env["S"][0][1] is False
        print("PASS real battery rejects drift before build; short footer says it was short")
    print("BATTERY COUNT GREEN")


if __name__ == "__main__":
    main()
