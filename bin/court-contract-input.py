#!/usr/bin/env python3
"""Materialize the owner's byte-bound Court contracts at both carriers' pin."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent

def materialize():
    record = json.loads((HERE / 'court-contract.from').read_text())
    if record['format'] != 'vi-court-contract-input/1':
        raise ValueError('unknown contract input format')
    revision = record['revision']
    if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
        raise ValueError('expected a full source revision')
    for name in ('gate-judge.from', 'court-wasm.from'):
        if (HERE / name).read_text().splitlines()[0] != revision:
            raise ValueError(name + ': court and contract revisions differ')
    names = record['files']
    suites = record['suites']
    if not isinstance(suites, list) or not suites or len(set(suites)) != len(suites):
        raise ValueError('expected a nonempty unique suite roster')
    if 'Checks/court-contract.py' not in names or any(
            not isinstance(s, str) or '/' in s or '\\' in s or
            'Contracts/Court/' + s + '/contract.json' not in names for s in suites):
        raise ValueError('suite roster and bound owner inputs differ')
    for name in names:
        path = PurePosixPath(name)
        if not path.parts or path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise ValueError('source path escapes contract input: ' + name)
    cache = HERE / '.court' / 'contracts' / revision
    missing = [name for name in names if not (cache / name).is_file()]
    if missing:
        with tempfile.TemporaryDirectory(prefix='gate-court-contract-') as tmp:
            subprocess.run(['git', '-C', tmp, 'init', '-q'], check=True)
            subprocess.run(['git', '-C', tmp, 'fetch', '-q', '--depth', '1', record['repository'], revision], check=True)
            # Git object bytes are independent of checkout line-ending settings.
            for name in missing:
                data = subprocess.check_output(['git', '-C', tmp, 'show', revision + ':' + name])
                if hashlib.sha256(data).hexdigest() != names[name]:
                    raise ValueError(name + ': source hash differs at ' + revision)
                target = cache / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    for name, expected in names.items():
        if hashlib.sha256((cache / name).read_bytes()).hexdigest() != expected:
            raise ValueError(name + ': cached input hash differs at ' + revision)
    return cache

if __name__ == '__main__':
    try:
        print(materialize())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print('court-contract.from: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
