#!/usr/bin/env python3
"""Both delivered carriers answer the owner's pinned suites, including raw CRLF."""
from pathlib import Path
import json
import base64
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = subprocess.run([sys.executable, str(ROOT/'bin/court-contract-input.py')], capture_output=True, text=True)
assert source.returncode == 0, source.stdout + source.stderr
owner = Path(source.stdout.strip())
record = json.loads((ROOT/'bin/court-contract.from').read_text())
# The receipt binds every delivered carrier, including the encoded browser
# module, to one recipe and source pin. This is byte provenance, not a proof
# that arbitrary compiler/toolchain versions reproduce those bytes.
build = json.loads((ROOT/'bin/court-wasm.build.json').read_text())
assert build['format'] == 'gate-court-wasm-build/1'
assert build['revision'] == record['revision'], 'court-wasm.build.json: source pin differs'
assert build['recipe_sha256'] == hashlib.sha256((ROOT/'bin/build-court-wasm.py').read_bytes()).hexdigest(), 'court-wasm.build.json: recipe differs'
expected_files = {'court-wasm/node/vi_court.js', 'court-wasm/node/vi_court_bg.wasm',
                  'court-wasm/web/vi_court.js', 'court-wasm/web/vi_court_bytes.js'}
assert set(build['outputs']) == expected_files, 'court-wasm.build.json: incomplete carrier roster'
for name, digest in build['outputs'].items():
    assert hashlib.sha256((ROOT/'bin'/name).read_bytes()).hexdigest() == digest, name + ': hash differs'
encoded = (ROOT/'bin/court-wasm/web/vi_court_bytes.js').read_bytes()
match = re.search(rb'VI_COURT_WASM_BASE64 = "([A-Za-z0-9+/=]+)"', encoded)
assert match, 'court-wasm/web/vi_court_bytes.js: missing module'
web_hash = hashlib.sha256(base64.b64decode(match[1], validate=True)).hexdigest()
assert web_hash == build['web_decoded_sha256'], 'court-wasm.build.json: decoded web hash differs'
receipt = (ROOT/'bin/court-wasm.from').read_text().splitlines()
assert receipt[0] == record['revision'] and receipt[3].split()[0] == build['outputs']['court-wasm/node/vi_court_bg.wasm'] and receipt[4].split()[0] == web_hash, 'court-wasm.from: carrier receipt differs'
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
