#!/usr/bin/env python3
"""Run the pinned owner's driver against the very applier the bench carries."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('press_input', HERE / 'bin/press-contract.py')
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
record = json.loads((HERE / 'bin/press-contract.from').read_text())
cache = door.acquire(record)
with tempfile.TemporaryDirectory(prefix='gate-press-contract-') as temp:
    report = Path(temp) / 'report.json'
    subprocess.run([sys.executable, str(cache / 'Checks/press-contract.py'), '--manifest', str(cache / record['contract']),
        '--command-json', json.dumps([shutil.which('node'), str(HERE / 'bin/press-contract-cli.js')]),
        '--implementation-id', 'gate bin/press.js through JSON transport', '--report', str(report)], check=True)
    assert json.loads(report.read_text())['passed']
    # A warm hit is still a hash check. Corrupt a disposable copy, not the shared input.
    copied = Path(temp) / 'input'
    shutil.copytree(cache, copied)
    selected = 'Contracts/Press/v0.1/fixtures/cases.json'
    with (copied / selected).open('ab') as stream:
        stream.write(b' ')
    try:
        door.checked(copied, record['files'])
        raise AssertionError('corrupt cache passed')
    except ValueError as exc:
        assert selected in str(exc)
    # The cold door fetches the named revision, not the repository's newer HEAD.
    repository = Path(temp) / 'repository'
    repository.mkdir()
    subprocess.run(['git', 'init', '-q', str(repository)], check=True)
    (repository / 'sample').write_bytes(b'original\n')
    subprocess.run(['git', '-C', str(repository), 'add', '.'], check=True)
    commit = ['git', '-C', str(repository), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@test', 'commit', '-qm']
    subprocess.run(commit + ['first'], check=True)
    pin = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
    import hashlib
    wanted = hashlib.sha256((repository / 'sample').read_bytes()).hexdigest()
    (repository / 'sample').write_bytes(b'newer HEAD\n')
    subprocess.run(['git', '-C', str(repository), 'add', '.'], check=True)
    subprocess.run(commit + ['second'], check=True)
    fixture = {'revision': pin, 'repository': repository.as_uri(), 'files': {'sample': wanted}}
    original_here = door.HERE
    try:
        door.HERE = Path(temp) / 'door'
        cold = door.acquire(fixture)
        assert (cold / 'sample').read_bytes() == b'original\n'
        assert door.acquire(fixture) == cold
        (cold / 'sample').write_bytes(b'bad warm cache')
        try:
            door.acquire(fixture)
            raise AssertionError('warm door returned corrupt bytes')
        except ValueError:
            pass
    finally:
        door.HERE = original_here
    # Removing the platform Character reader must give an addressed nonanswer,
    # never silently resume slicing UTF-16 units. No browser is opened here.
    probe = r'''
const fs = require("fs"), vm = require("vm"), assert = require("assert");
const context = { module: { exports: {} }, Intl: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), context);
const state = 'extension Words {\n public static var typeName: String { "𐐀" }\n}\n';
const result = context.module.exports.apply(["rubout", "Words"], state, "");
assert.equal(result.state, state); assert.equal(result.changed, false);
assert.equal(result.refusal.address, "state.swift#Words");
assert.ok(result.refusal.reason.startsWith("unsupported:"));
'''
    subprocess.run(['node', '-e', probe, str(HERE / 'bin/press.js')], check=True)
print('PASS cold revision, warm-cache corruption and missing Character reader controls')
