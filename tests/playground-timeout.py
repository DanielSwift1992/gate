#!/usr/bin/env python3
"""A real hung descendant must die; the full last phase must reach the failure."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time
from playground_runner import run_playground

success = run_playground([sys.executable, '-c', 'print("a complete reply")'], timeout=3)
assert success.returncode == 0 and success.stdout.strip() == 'a complete reply' and not success.stderr
failure = run_playground([sys.executable, '-c', 'import sys; print("an addressed refusal", file=sys.stderr); sys.exit(23)'], timeout=3)
assert failure.returncode == 23 and 'an addressed refusal' in failure.stdout
with tempfile.TemporaryDirectory(prefix='gate-playground-timeout-') as temp:
    heartbeat = Path(temp) / 'heartbeat'
    grandchild = ('import pathlib,time\np=pathlib.Path(' + repr(str(heartbeat)) + ')\n'
                  'while True:\n with p.open("ab") as f: f.write(b"x"); f.flush()\n time.sleep(.02)\n')
    program = ('import subprocess,sys,time,json\n'
               'print(\'PLAYGROUND BEGIN \' + json.dumps({"phase":"browser courts and draft storage"}), flush=True)\n'
               'print("PLAYGROUND START finished control", flush=True)\n'
               'print("PLAYGROUND PASS finished control 0.001s", flush=True)\n'
               'subprocess.Popen([sys.executable,"-c",' + repr(grandchild) + '])\n'
               'print("PLAYGROUND START hanging source.swift:17", file=sys.stderr, flush=True)\n'
               'time.sleep(60)\n')
    started = time.monotonic()
    answer = run_playground([sys.executable, '-c', program], timeout=1)
    assert time.monotonic() - started < 10, 'the deadline failed to stop the child tree'
    assert answer.returncode == 124 and 'exceeded 1 seconds' in answer.stderr
    assert 'phase: browser courts and draft storage; active: hanging source.swift:17' in answer.stderr, answer
    assert 'finished control' not in answer.stderr, 'a completed case was reported as active'
    assert heartbeat.is_file() and heartbeat.stat().st_size > 0, 'the descendant never ran'
    size = heartbeat.stat().st_size
    time.sleep(.2)
    assert heartbeat.stat().st_size == size, 'the descendant survived the timeout'
print('PLAYGROUND DEADLINE GREEN: phase, active address, exit status and descendant termination')
