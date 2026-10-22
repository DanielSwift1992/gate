#!/usr/bin/env python3
"""A failed child keeps its traceback through the actual public CI reader."""
import ast
import contextlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
source = ast.parse((ROOT / 'tests/smoke.py').read_text())
function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'failed_output')
checks = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == 'Checks')
namespace = {'time': time, 'json': json}
exec(compile(ast.Module(body=[function, checks], type_ignores=[]), 'smoke.py', 'exec'), namespace)
main = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
statements = [node for node in main.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
              and any(isinstance(child, ast.Name) and child.id == '_owner_profile' for child in ast.walk(node))]
assert len(statements) == 2, 'exercise both the registration and its failure output in their source order'

with tempfile.TemporaryDirectory(prefix='gate-ci-output-') as temp:
    log = Path(temp) / 'smoke.txt'
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        namespace['S'] = namespace['Checks'](time.monotonic())
        namespace['_owner_profile'] = subprocess.CompletedProcess([], 1,
            'INPUT RECORD LOSS: ' + 'x' * 8000 + '\n',
            'Traceback (most recent call last):\n  source.py:42\nValueError: the actual % cause\r\n'
            'build-pages: /selected/world: POST http://127.0.0.1:1234/verdict?f=Page.swift: '
            'RemoteDisconnected: Remote end closed connection without response; output=server diagnostic\n')
        exec(compile(ast.Module(body=statements, type_ignores=[]), 'owner-profile handoff', 'exec'), namespace)
        print('PASS the next check')
        namespace['failed_output']('success', subprocess.CompletedProcess([], 0, '', ''))
    log.write_text(captured.getvalue())
    timing = next(line for line in captured.getvalue().splitlines() if line.startswith('TIMING '))
    assert json.loads(timing[7:])['seconds'] >= 0
    workflow = (ROOT / '.github/workflows/battery.yml').read_text()
    readers = re.findall(r"python3 -c '(import sys; t=open\(.*?\n.*?replace\(.*?\)\))'", workflow, re.S)
    assert len(readers) == 2, 'the macOS and Linux public annotation readers must be exercised'
    for reader in readers:
        lines = reader.splitlines()
        indent = len(lines[1]) - len(lines[1].lstrip())
        reader = lines[0] + '\n' + '\n'.join(line[indent:] for line in lines[1:])
        reader = reader.replace('"/tmp/smoke-out.txt"', repr(str(log)))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(compile(reader, 'battery annotation', 'exec'), {})
        annotation = output.getvalue().strip()
        assert annotation.startswith('::error title=what the battery said::')
        assert "FAIL the owner's resolved profile" in annotation
        assert 'Traceback (most recent call last):' in annotation
        assert 'ValueError: the actual %25 cause' in annotation
        assert 'POST http://127.0.0.1:1234/verdict?f=Page.swift: RemoteDisconnected' in annotation
        assert '/selected/world' in annotation and 'output=server diagnostic' in annotation
        assert '%0A' in annotation and '\n' not in annotation and '\r' not in annotation
        assert 'PASS the next check' not in annotation and 'success' not in annotation
        assert 'TIMING' not in annotation, 'telemetry must not break the failure/traceback pair'
        assert len(annotation) < 5000
print('CI OUTPUT GREEN: both public readers retain the named failure and escaped traceback tail')
