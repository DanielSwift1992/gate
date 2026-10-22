#!/usr/bin/env python3
"""The published host's declared protocol must open its recorded worlds."""
import ast
import json
import itertools
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / 'bin/build-pages.py').read_text()
# Execute the actual emitted shim with a live-server capability snapshot.
tree = ast.parse(source)
shim = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'shim' for t in n.targets)
            and isinstance(n.value, ast.Constant))
read_worlds = re.search(r'async function readWorlds\(names\) \{.*?\n\}', (ROOT / 'web/ui.html').read_text(), re.S)[0]
files = ['page.swift', 'dictionary.swift', 'sub/space name.swift']
texts = {f: 'enum Recorded' + str(i) + ' {}\n' for i, f in enumerate(files)}
snapshot = {'/files': json.dumps({'files': files, 'batch_readings': True}),
            **{'/world?f=' + f: text for f, text in texts.items()}}
for context, policy in itertools.product([None, {'pin': 'pin', 'world': 'external'}],
                                         [None, 'reader-draft', 'read-only']):
    carried = dict(snapshot)
    if policy is not None:
        carried['/files'] = json.dumps({**json.loads(snapshot['/files']), 'save_policy': policy})
    script = shim
    for key, value in {'SNAP': carried, 'CONTEXT': context, 'STORAGE': 'probe.',
                       'FORMS': [], 'LAYOUT': None, 'ALL': files, 'WORLDS': [],
                       'COURT_WORKER_GLUE': '', 'COURT_WORKER_HANDLER': ''}.items():
        script = script.replace('__' + key + '__', json.dumps(value))
    # Court initialization precedes the snapshot closure and is unrelated to transport.
    script = script[script.index('(function () {'):script.rindex('</script>')]
    probe = '''
const assert = require('node:assert/strict');
const calls = [];
global.window = { fetch() { throw Error('recorded input escaped to the network'); } };
global.document = {addEventListener() {}};
global.localStorage = {getItem() {return null;}};
''' + script + '''
global.fetch = (...args) => {calls.push(args); return window.fetch(...args);};
''' + read_worlds + '''
(async () => {
    const fl = await (await fetch('/files')).json();
    global.batchReadings = fl.batch_readings === true;
    const names = ''' + json.dumps(files) + ''';
    const rows = await readWorlds(names);
    for (const [f, text] of Object.entries(''' + json.dumps(texts) + ''')) {
        assert.equal(rows.get(f).text, text);
        assert.equal(rows.get(f).status, 200);
    }
    assert.equal(fl.batch_readings, false);
    assert.equal(calls.filter(x => x[1]?.method === 'POST').length, 0);
    assert.equal(fl.save_policy, ''' + json.dumps(policy or 'reader-draft') + ''');
})().catch(e => {console.error(e); process.exitCode = 1;});
'''
    result = subprocess.run(['node', '-'], input=probe, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr[-2000:] or 'static reader did not answer')
print('STATIC READINGS GREEN: root and world, recorded bytes through the UI reader')
