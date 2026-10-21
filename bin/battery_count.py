#!/usr/bin/env python3
"""Project the README stamp from the battery's registrations, without judging.

S.append is the registry, including its literal case tables, stdlib glob and
D65 generator. Only registration-bearing control flow is read. A new dynamic
registration shape refuses at its source address rather than guessing a count.
"""
import argparse
import ast
import glob
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
REPAIR = "python3 bin/battery_count.py"
STAMP = re.compile(r"(?m)^(tests/smoke\.py[ \t]+the battery: )(\d+)( checks this repository holds itself)$")


class RegistryError(ValueError):
    pass


class Registry:
    def __init__(self, root, swift=True):
        self.root, self.swift = Path(root), swift

    def count(self, file="tests/smoke.py", function="main", bindings=None, yielded=False):
        path = self.root / file
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=file)
        body = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
        assignments = [n for n in ast.walk(body) if isinstance(n, ast.Assign) and len(n.targets) == 1
                       and isinstance(n.targets[0], ast.Name)]

        def fail(node, reason):
            raise RegistryError(f"{file}:{node.lineno}: {reason}")

        def registration(n):
            return ((yielded and isinstance(n, ast.Yield))
                    or (not yielded and isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and isinstance(n.func.value, ast.Name) and n.func.value.id == "S"
                        and n.func.attr == "append"))

        def contains(n):
            return any(registration(c) for c in ast.walk(n))

        def value(n, env, before):
            if isinstance(n, ast.Constant):
                return n.value
            if isinstance(n, (ast.Tuple, ast.List)):
                return tuple(value(e, env, before) for e in n.elts)
            if isinstance(n, ast.Dict):
                return {value(k, env, before): value(v, env, before) for k, v in zip(n.keys, n.values)}
            if isinstance(n, ast.Name):
                if n.id in env:
                    return env[n.id]
                found = [a for a in assignments if a.targets[0].id == n.id and a.lineno < before]
                if found:
                    a = max(found, key=lambda a: a.lineno)
                    return value(a.value, env, a.lineno)
            if isinstance(n, ast.Subscript):
                return value(n.value, env, before)[value(n.slice, env, before)]
            if isinstance(n, ast.Call):
                name = ast.unparse(n.func)
                if name == "d65_checks":
                    spec = importlib.util.spec_from_file_location("battery_d65", self.root / "tests/d65.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return range(self.count("tests/d65.py", "checks",
                                            {"records": module.case_records(self.root)}, yielded=True))
                if isinstance(n.func, ast.Attribute) and n.func.attr == "items" and not n.args and not n.keywords:
                    table = n.func.value
                    if isinstance(table, ast.Name):
                        found = [a for a in assignments if a.targets[0].id == table.id and a.lineno < before]
                        if found:
                            table = max(found, key=lambda a: a.lineno).value
                    # The keys register cases; the world expressions remain
                    # the test's work. Their values do not affect this count.
                    if isinstance(table, ast.Dict):
                        return [(key, None) for key in dict.fromkeys(value(k, env, before) for k in table.keys)]
                readers = {"sorted": sorted, "enumerate": enumerate,
                           "_glob.glob": glob.glob, "os.path.join": lambda *p: str(Path(*p))}
                if name in readers and not n.keywords:
                    return readers[name](*(value(a, env, before) for a in n.args))
            fail(n, "registration cases need a readable literal table or a declared data reader")

        def bind(target, item, env):
            if isinstance(target, ast.Name):
                env[target.id] = item
            elif isinstance(target, (ast.Tuple, ast.List)) and len(target.elts) == len(item):
                for t, v in zip(target.elts, item):
                    bind(t, v, env)
            else:
                fail(target, "unsupported registration target")

        def walk(nodes, env):
            total = 0
            for n in nodes:
                if not contains(n):
                    continue
                if isinstance(n, ast.Expr) and registration(n.value):
                    total += 1
                elif isinstance(n, ast.For):
                    if any(isinstance(c, (ast.Break, ast.Continue, ast.Return)) for c in ast.walk(n)):
                        fail(n, "registration loop may exit before its cases are walked")
                    if n.orelse:
                        fail(n, "registration loop has an else branch")
                    for item in value(n.iter, env, n.lineno):
                        local = dict(env)
                        bind(n.target, item, local)
                        total += walk(n.body, local)
                elif isinstance(n, ast.If):
                    if ast.unparse(n.test) == "shutil.which('swiftc')":
                        total += walk(n.body if self.swift else n.orelse, env)
                    else:
                        yes, no = walk(n.body, env), walk(n.orelse, env)
                        if yes != no:
                            fail(n, "conditional registration changes the count")
                        total += yes
                elif isinstance(n, ast.Try) and not any(contains(h) for h in n.handlers):
                    total += walk(n.body + n.orelse + n.finalbody, env)
                else:
                    fail(n, "unsupported registration control flow")
            return total

        return walk(body.body, {"HERE": str(self.root), **(bindings or {})})


def projection(root=ROOT):
    registry = Registry(root)
    return registry.count()


def stamp(root=ROOT, check=False):
    root = Path(root)
    count = projection(root)
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    matches = list(STAMP.finditer(text))
    if len(matches) != 1:
        raise RegistryError("README.md: expected one battery stamp; restore its labelled row, then run " + REPAIR)
    current = int(matches[0][2])
    if check and current != count:
        raise RegistryError(f"README.md: battery stamp says {current}; registry has {count}. Repair: {REPAIR}")
    if not check and current != count:
        path.write_text(STAMP.sub(lambda m: m[1] + str(count) + m[3], text), encoding="utf-8")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="refuse a stale stamp without writing")
    args = parser.parse_args()
    try:
        count = stamp(check=args.check)
    except (RegistryError, SyntaxError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"battery: {count} registered checks; README stamp {'holds' if args.check else 'updated'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
