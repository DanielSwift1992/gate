#!/usr/bin/env python3
"""Both delivered carriers answer the owner's pinned suites, including raw CRLF."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = subprocess.run([sys.executable, str(ROOT/'bin/court-contract-input.py')], capture_output=True, text=True)
assert source.returncode == 0, source.stdout + source.stderr
owner = Path(source.stdout.strip())
record = json.loads((ROOT/'bin/court-contract.from').read_text())
native = ROOT/'bin/gate-cli'
if not native.exists():
    native = native.with_suffix('.exe')
with tempfile.TemporaryDirectory(prefix='gate-court-laws-') as tmp:
    tmp = Path(tmp)
    for version in record['suites']:
        for carrier, command in [('native', [str(native), 'judge']),
                                 ('wasm', [shutil.which('node'), str(ROOT/'bin/judge-wasm.js'), 'judge'])]:
            report = tmp/(version+'-'+carrier+'.json')
            run = subprocess.run([sys.executable, str(owner/'Checks/court-contract.py'),
                                  '--manifest', str(owner/'Contracts/Court'/version/'contract.json'),
                                  '--command-json', json.dumps(command), '--implementation-id', 'gate '+carrier,
                                  '--report', str(report)], capture_output=True, text=True)
            assert run.returncode == 0, run.stdout + run.stderr
            result = json.loads(report.read_text())
            assert result['passed'] and result['results'] and all(x['matched'] for x in result['results'])
            print(version, carrier, len(result['results']), 'matched')
    # A changed cache or a carrier at another pin never supplies a replacement law.
    fake = tmp/'bin';fake.mkdir()
    for name in ('court-contract-input.py', 'court-contract.from', 'gate-judge.from', 'court-wasm.from'):
        shutil.copyfile(ROOT/'bin'/name, fake/name)
    cache = fake/'.court/contracts'/record['revision']
    shutil.copytree(owner, cache)
    driver = cache/'Checks/court-contract.py';driver.write_bytes(driver.read_bytes()+b'\n# changed\n')
    bad = subprocess.run([sys.executable, str(fake/'court-contract-input.py')], capture_output=True, text=True)
    assert bad.returncode == 2 and 'Checks/court-contract.py' in bad.stderr and 'hash differs' in bad.stderr
    (fake/'gate-judge.from').write_text('0'*40+'\n')
    bad = subprocess.run([sys.executable, str(fake/'court-contract-input.py')], capture_output=True, text=True)
    assert bad.returncode == 2 and 'gate-judge.from' in bad.stderr and 'revisions differ' in bad.stderr
    (fake/'gate-judge.from').write_text(record['revision']+'\n')
    empty = dict(record, suites=[])
    (fake/'court-contract.from').write_text(json.dumps(empty))
    bad = subprocess.run([sys.executable, str(fake/'court-contract-input.py')], capture_output=True, text=True)
    assert bad.returncode == 2 and 'nonempty' in bad.stderr
print('COURT CONTRACT GREEN: both carriers follow the owner; changed bytes, split pins and empty roster refuse')
