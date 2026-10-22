#!/usr/bin/env python3
"""A failed child keeps its traceback through the actual public CI reader."""
import ast
import contextlib
import io
from itertools import product
import json
import os
import shlex
import sys
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


# Exercise the Pages job's actual shell blocks, including tee, with failing
# children and an inert curl. No workflow command or network request escapes.
pages = workflow.split('\n  pages:\n', 1)[1].split('\n  action:\n', 1)[0]
assert 'PAGES_STEPS: ${{ toJSON(steps) }}' in pages
assert '- if: failure()\n        name: what pages said' in pages

def run_block(identifier):
    if identifier == 'diagnostic':
        block = pages.split('        name: what pages said\n', 1)[1]
    else:
        block = pages.split('        id: ' + identifier + '\n', 1)[1]
    body = block.split('        run: |\n', 1)[1].splitlines()
    lines = []
    for line in body:
        if line and not line.startswith('          '):
            break
        lines.append(line[10:] if line else '')
    assert lines, identifier + ': workflow run block missing'
    return '\n'.join(lines)

children = [('build_site', 'bin/build-pages.py'), ('roadtest', 'tests/roadtest.py'), ('build_cli', 'bin/build-cli.sh')]
for buffering, (identifier, path) in product((0, 8192, 131072), children):
    with tempfile.TemporaryDirectory(prefix='gate-pages-output-') as temp:
        root = Path(temp)
        (root / 'bin').mkdir()
        (root / 'tests').mkdir()
        (root / 'bin/ci-pages.py').write_bytes((ROOT / 'bin/ci-pages.py').read_bytes())
        child = root / path
        error = 'T0066 CONTROL: Traceback at selected-world/Page.swift:42\nactual % cause\r\n::error::quoted child text\nFINAL TAIL '+identifier+'\n'
        # stdout and stderr share the workflow pipe, but keep separate buffers.
        # Flush the preamble before the error so the error is the actual tail,
        # including when a carrier's stdout buffer holds the whole preamble.
        program = ('import io, sys\n'
                   f'sys.stdout = io.TextIOWrapper(open(sys.stdout.fileno(), "wb", buffering={buffering}, '
                   'closefd=False), encoding="utf-8", write_through=True)\n'
                   'print("preamble " + "x" * 20000, flush=True)\n'
                   'sys.stderr.write(' + repr(error) + ')\nsys.stderr.flush()\nsys.exit(23)\n')
        if identifier == 'build_cli':
            child.write_text('#!/bin/bash\nexec ' + shlex.quote(sys.executable) + ' -c ' + shlex.quote(program) + '\n')
            child.chmod(0o755)
        else:
            child.write_text(program)
        env = dict(os.environ, GH_TOKEN='control-only', GITHUB_REPOSITORY='control/repository', GITHUB_SHA='control-sha')
        # The source script is reached under exactly its workflow pathname.
        result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', run_block(identifier)], cwd=root, env=env, capture_output=True)
        assert result.returncode == 23, (identifier, 'tee masked the child status', result)
        assert result.stdout.endswith(error.encode()), (identifier, buffering, 'error is not the emitted tail', result.stdout[-600:])
        outcomes = {key: dict(outcome='skipped') for key in ['checkout','build_cli','build_site','roadtest','upload','site','deployment']}
        outcomes['checkout']['outcome'] = 'success'
        if identifier != 'build_cli': outcomes['build_cli']['outcome'] = 'success'
        if identifier == 'roadtest': outcomes['build_site']['outcome'] = 'success'
        outcomes[identifier]['outcome'] = 'failure'
        env['PAGES_STEPS'] = json.dumps(outcomes)
        fake_bin = root / 'fake-bin'
        fake_bin.mkdir()
        curl = fake_bin / 'curl'
        curl.write_text('#!/usr/bin/env python3\nfrom pathlib import Path\nimport sys\nvalue=sys.argv[sys.argv.index("-d")+1]\nassert value.startswith("@")\nPath("posted-status.json").write_bytes(Path(value[1:]).read_bytes())\n')
        curl.chmod(0o755)
        env['PATH'] = str(fake_bin) + os.pathsep + env['PATH']
        report = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', run_block('diagnostic')], cwd=root, env=env, capture_output=True, text=True)
        assert report.returncode == 0, report
        annotation = report.stdout.strip()
        expected = {'build_site':'build-pages.py','roadtest':'roadtest.py','build_cli':'gate binary build'}[identifier]
        assert annotation.startswith('::error title=what pages '+expected+' said::'), annotation
        assert 'selected-world/Page.swift:42' in annotation and 'FINAL TAIL '+identifier in annotation, (identifier, buffering, annotation)
        assert 'actual %25 cause%0D%0A' in annotation and '%0A::error::quoted child text' in annotation
        assert '\n' not in annotation and '\r' not in annotation and len(annotation) < 5000
        assert 'preamble' not in annotation
        status = json.loads((root / 'posted-status.json').read_text())
        assert status['state'] == 'failure' and status['context'] == 'pages-publish'
        assert status['description'].startswith(expected+' failed;') and len(status['description']) <= 138
        assert 'built and walked' not in status['description']
        assert 'site='+outcomes['build_site']['outcome'] in status['description']
        assert 'roadtest='+outcomes['roadtest']['outcome'] in status['description']
        # A failure without a log still names the missing diagnostic; a later
        # deployment failure must not quote an unrelated successful build log.
        for log in root.glob('pages-*.txt'): log.unlink()
        missing = subprocess.run([sys.executable, 'bin/ci-pages.py', '--context', 'pages-publish', '--status', 'missing.json'], cwd=root, env=env, capture_output=True, text=True)
        assert missing.returncode == 0 and 'did not write its log' in missing.stdout
        (root / 'pages-build.txt').write_text('PASS unrelated successful output\n')
        outcomes[identifier]['outcome'] = 'success'
        outcomes['build_site']['outcome'] = 'success'
        outcomes['roadtest']['outcome'] = 'success'
        outcomes['upload']['outcome'] = 'success'
        outcomes['site']['outcome'] = 'success'
        outcomes['deployment']['outcome'] = 'failure'
        env['PAGES_STEPS'] = json.dumps(outcomes)
        late = subprocess.run([sys.executable, 'bin/ci-pages.py', '--context', 'pages-publish', '--status', 'late.json'], cwd=root, env=env, capture_output=True, text=True)
        assert late.returncode == 0 and not late.stdout
        late_status = json.loads((root / 'late.json').read_text())
        assert late_status['description'].startswith('deployment failed; site=success; roadtest=success;')
print('CI OUTPUT GREEN: battery readers and Pages shell blocks retain escaped failure tails and truthful step outcomes')
