#!/usr/bin/env python3
"""Lay the owner's Press suite from its revision; verify every warm-cache byte too."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]


def checked(root, files):
    for name, wanted in files.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != wanted:
            raise ValueError('press contract sha256 mismatch: ' + name)


def acquire(record, source=None):
    pin = record['revision']
    if not re.fullmatch('[0-9a-f]{40}', pin):
        raise ValueError('press contract needs a full revision')
    cache = HERE / 'bin/.court/press' / pin
    if cache.is_dir():
        checked(cache, record['files'])
        return cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='press-input-', dir=cache.parent) as temp:
        work = Path(temp)
        if source is None:
            repository = work / 'fetch'
            subprocess.run(['git', 'init', '-q', '--bare', str(repository)], check=True)
            subprocess.run(['git', '-C', str(repository), 'fetch', '-q', '--depth', '1', record['repository'], pin], check=True)
            provenance = 'public revision fetch'
        else:
            repository = Path(source).resolve()
            provenance = 'local committed git objects: ' + str(repository)
        staged = work / 'input'
        staged.mkdir()
        for name in record['files']:
            path = (staged / name).resolve()
            if not path.is_relative_to(staged.resolve()):
                raise ValueError('press contract path escapes input: ' + name)
            path.parent.mkdir(parents=True, exist_ok=True)
            # git show reads the committed bytes, independent of checkout line endings.
            path.write_bytes(subprocess.check_output(['git', '-C', str(repository), 'show', pin + ':' + name]))
        checked(staged, record['files'])
        (staged / 'from.json').write_text(json.dumps({'revision': pin, 'provenance': provenance, 'files': record['files']}, indent=2) + '\n')
        staged.rename(cache)
    return cache


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='explicit local committed-object source; recorded as local, never a public receipt')
    args = parser.parse_args()
    try:
        record = json.loads((HERE / 'bin/press-contract.from').read_text())
        print(acquire(record, args.source))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print('press contract input: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
