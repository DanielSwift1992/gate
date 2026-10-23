#!/usr/bin/env python3
"""A real hung descendant must die; the full last phase must reach the failure."""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import time
from playground_runner import run_playground, summary, annotation

def required_job(job):
    lines = [line for line in job.splitlines() if line.strip() and not line.lstrip().startswith('#')]
    indent = min(len(line) - len(line.lstrip()) for line in lines)
    for line in lines:
        if len(line) - len(line.lstrip()) != indent:
            continue
        assert not re.match(r"(?:['\"]?)(?:if|continue-on-error)(?:['\"]?)\s*:", line.strip()), \
            '.github/workflows/battery.yml:playground: the world-contract job cannot be conditional or optional'


def required_runner(job):
    # This is a finite check of our declared workflow spelling, not a YAML
    # or shell interpreter. The runner step has one direct command; only its
    # display name and comments may vary. Optional upload steps are separate.
    active = '\n'.join(line for line in job.splitlines()
                       if line.strip() and not line.lstrip().startswith('#'))
    steps = re.split(r'(?m)(?=^      - )', active)[1:]
    runners = [step for step in steps if any(
        line.strip().startswith(('run:', '- run:')) and 'tests/playground_runner.py' in line
        for line in step.splitlines())]
    address = '.github/workflows/battery.yml:playground:runner'
    assert len(runners) == 1, address + ': one direct world-runner step is required'
    lines = [line.strip() for line in runners[0].splitlines()]
    if lines[0].startswith('- name:'):
        lines = lines[1:]
    else:
        lines[0] = lines[0].removeprefix('- ')
    assert lines == ['run: python3 tests/playground_runner.py --timeout 2100 --log "$RUNNER_TEMP/playground-out.txt"'], \
        address + ': the entire world-runner step must be a required direct command'


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
# Public annotations are a small surface: put phase/cost before the tail,
# preserve source addresses, and count escaped UTF-8 bytes, not Python chars.
output = ('PLAYGROUND PHASE {"phase":"fresh world site","seconds":410,"duration_seconds":400}\n'
          'PLAYGROUND BEGIN {"phase":"browser courts and draft storage","seconds":410}\n'
          'PLAYGROUND START storage: source.swift:17\n'
          'PLAYGROUND PASS all palette readings 213.456s\n' + 'filler % \u044f' * 6000 + '\n'
          'Traceback: source.swift:17: the actual % cause\r\n')
public = annotation(output, 1200)
assert len(public.encode('utf-8')) <= 4096
assert public.startswith('::error title=playground contracts::playground: 1200s; browser courts and draft storage')
assert public.index('phase fresh world site') < public.index('last output:')
assert 'slow 213.456s all palette readings' in public
assert 'source.swift:17' in public and 'the actual %25 cause%0D' in public
assert '\n' not in public and '\r' not in public
assert '%0A' in public
notice = annotation(output, 1200, level='notice')
assert notice.startswith('::notice title=playground contracts::playground:')
assert len(notice.encode('utf-8')) <= 4096 and 'phase fresh world site' in notice
assert 'slow 213.456s all palette readings' in notice and '\n' not in notice
assert 'last output:' not in notice, 'a success notice needs the summary, not the log tail'

# Run the actual CLI as CI does; the fixture is only its child, not a second
# runner. A failed child keeps its exit and complete log plus a bounded summary.
with tempfile.TemporaryDirectory(prefix='gate-playground-job-') as temp:
    root = Path(temp)
    runner = root / 'playground_runner.py'
    runner.write_bytes(Path(__file__).with_name('playground_runner.py').read_bytes())
    (root/'playground.py').write_text('print("PLAYGROUND PHASE {\\"phase\\":\\"fixture\\",\\"seconds\\":0.01}")\nprint("source.swift:17: refused")\nraise SystemExit(23)\n')
    log = root/'complete.txt'
    reply = subprocess.run([sys.executable,str(runner),'--timeout','3','--log',str(log)],capture_output=True,text=True)
    assert reply.returncode == 23, reply
    assert 'source.swift:17: refused' in log.read_text()
    assert '::error title=playground contracts::playground:' in reply.stdout
    assert reply.stdout.index('phase fixture') < reply.stdout.index('last output:')
    (root/'playground.py').write_text('print("fixture complete")\n')
    reply = subprocess.run([sys.executable,str(runner),'--timeout','3','--log',str(log)],capture_output=True,text=True)
    assert reply.returncode == 0, reply
    assert 'PASS the pinned playground worlds keep their drawings, courts and separate state' in reply.stdout
    assert '::error' not in reply.stdout
    assert '::notice title=playground contracts::playground:' in reply.stdout
    external = root/'operator-me'
    (root/'playground.py').write_text('import os,pathlib\np=pathlib.Path(os.environ["GATE_ME"])\nassert str(p) != ' + repr(str(external)) + '\np.mkdir(parents=True,exist_ok=True)\n(p/"wrote").write_text("isolated")\nprint("isolated child")\n')
    import os
    reply = subprocess.run([sys.executable,str(runner),'--timeout','3','--log',str(log)],env=dict(os.environ,GATE_ME=str(external)),capture_output=True,text=True)
    assert reply.returncode == 0 and 'isolated child' in log.read_text(), reply
    assert not external.exists(), 'runner touched the operator personal directory'

workflow = Path(__file__).resolve().parents[1].joinpath('.github/workflows/battery.yml').read_text()
job = workflow.split('\n  playground:\n',1)[1].split('\n  windows-vein:\n',1)[0]
required_job(job)
for key in ['if', 'continue-on-error', '"if"', "'continue-on-error'"]:
    try:
        required_job('    '+key+': true\n'+job)
    except AssertionError as error:
        assert '.github/workflows/battery.yml:playground' in str(error)
    else:
        raise AssertionError('the world job accepted '+key)
required_job(job+'\n      - if: always()\n        continue-on-error: false\n')

required_runner(job)
run_line = '        run: python3 tests/playground_runner.py --timeout 2100 --log "$RUNNER_TEMP/playground-out.txt"'
for changed in [run_line + ' || true', run_line + '; exit 0',
                '        continue-on-error: true\n' + run_line,
                '        "continue-on-error" : true\n' + run_line,
                '        if: false\n' + run_line]:
    try:
        required_runner(job.replace(run_line, changed))
    except AssertionError as error:
        assert '.github/workflows/battery.yml:playground:runner' in str(error)
    else:
        raise AssertionError('the world runner accepted a conditional or masked exit')
required_runner(job + '\n      - if: always()\n        name: "continue-on-error: true"\n        run: echo "a neighbouring step" || true\n')
required_runner(job.replace(run_line, '        # if: continue-on-error: || true\n' + run_line)
                .replace('name: the complete published world contracts','name: another display label'))

assert 'GATE_ME=$RUNNER_TEMP/gate-playground/me' in job
assert 'os: [ubuntu-24.04, macos-latest]' in job and 'fail-fast: false' in job
assert 'timeout-minutes: 45' in job
assert 'tests/playground_runner.py --timeout 2100 --log' in job
for build in ['bin/build-judge.sh','bin/build-organization-judge.sh','bin/build-cli.sh']:
    assert build in job, build
assert 'if: always()' in job and 'playground-out.txt' in job
smoke = Path(__file__).with_name('smoke.py').read_text()
assert 'run_playground(' not in smoke, 'the composite must not also consume the ordinary battery deadline'
print('PLAYGROUND DEADLINE GREEN: dedicated job, phase/cost before bounded tail, child exit and descendant termination')
