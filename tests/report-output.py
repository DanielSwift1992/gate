#!/usr/bin/env python3
"""A report's refusal must survive before its output file is opened."""
import ast
import json
import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
source = ast.parse((ROOT / 'tests/smoke.py').read_text())
run = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
main = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
at = next(i for i, n in enumerate(main.body) if isinstance(n, ast.Assign)
          and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
          and n.value.func.id == 'run' and n.value.args
          and [getattr(a, 'value', None) for a in n.value.args] == ['report', '-o', 'audit.html'])
# Exercise the actual producer/guard/open sequence, not a second assertion.
read_page = compile(ast.Module(body=main.body[at:at + 3], type_ignores=[]),
                    'tests/smoke.py', 'exec')
namespace = dict(subprocess=subprocess, json=json, GATE=str(ROOT / 'gate'))
exec(compile(ast.Module(body=[run], type_ignores=[]), 'tests/smoke.py', 'exec'), namespace)

def read(folder):
    scope = dict(run=namespace['run'], os=os, json=json, grepo=str(folder))
    exec(read_page, scope)
    return scope['page']

def refused(folder, *words):
    try:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            read(folder)
    except AssertionError as error:
        message = str(error)
        assert all(word in message for word in words), message
        if 'expected exit' in message:
            assert output.getvalue().startswith('FAIL gate report -o audit.html'), output.getvalue()
        return message
    raise AssertionError('a failed producer was accepted before opening its output')

with tempfile.TemporaryDirectory(prefix='gate-report-output-') as temp:
    folder = Path(temp)
    (folder / 'tables').mkdir()
    for name in ('people.csv', 'grants.csv'):
        shutil.copyfile(ROOT / 'demo' / name, folder / 'tables' / name)
    subprocess.run([str(ROOT / 'gate'), 'status', '--json'], cwd=folder,
                   capture_output=True, text=True, check=True)
    assert '<h2>Verdict</h2>' in read(folder)
    (folder / 'audit.html').unlink()
    (folder / 'audit.html').mkdir()
    # A real native refusal, not a missing-file exception or a mocked court.
    refused(folder, 'expected exit 0, got 1', 'audit.html is a directory',
            'name a file inside it', 'stdout:', 'stderr:')
    (folder / 'audit.html').rmdir()
    fake = folder / 'carrier'
    fake.write_text('#!' + sys.executable + '\nimport sys\n'
                    'print(\'{"error": "stdout reason"}\')\n'
                    'print("x" * 300 + " full stderr reason", file=sys.stderr)\n'
                    'sys.exit(23)\n')
    fake.chmod(0o755)
    namespace['GATE'] = str(fake)
    refused(folder, 'expected exit 0, got 23', 'stdout reason', 'full stderr reason')
    # Even a carrier claiming success must actually deliver the file.
    fake.write_text('#!' + sys.executable + '\nprint(\'{"wrote": "audit.html"}\')\n')
    refused(folder, 'exit 0 without its output file', '"wrote": "audit.html"')
print('REPORT OUTPUT GREEN: real write/refusal, both channels, missing success output')
