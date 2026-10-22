#!/usr/bin/env python3
"""Acquire the declared owner law by commit and byte hash, without a fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PIN = 'bin/boundary-law.from'
FILES = ('Checks/boundary-law.py', 'Checks/boundary-controls.py')


def refusal(error):
    if isinstance(error, ValueError) and str(error).startswith(PIN + ':1:'):
        return str(error)
    return PIN + ':1: owner input refused: cannot read or validate the declared input; check the pin and its files'


def read_pin(root):
    data = json.loads((root / PIN).read_text(encoding='utf-8'))
    if data.get('format') != 'vi.boundary.input/1':
        raise ValueError(PIN + ':1: unsupported owner input format')
    if not re.fullmatch('[0-9a-f]{40}', data.get('revision', '')):
        raise ValueError(PIN + ':1: owner revision must be a full commit hash')
    if data.get('repository') != 'https://github.com/DanielSwift1992/verification-is-identification':
        raise ValueError(PIN + ':1: undeclared owner repository')
    if set(data.get('files', {})) != set(FILES):
        raise ValueError(PIN + ':1: owner input file set differs')
    for name, checksum in data['files'].items():
        if not re.fullmatch('[0-9a-f]{64}', checksum):
            raise ValueError(PIN + ':1: invalid SHA-256 for ' + name)
    return data


def verified_inputs(root, repository=None):
    data = read_pin(root)
    cache = root / 'bin/.inputs/boundary-law' / data['revision']
    inputs = {}
    missing = []
    for name in FILES:
        path = cache / name
        if path.exists():
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != data['files'][name]:
                raise ValueError(PIN + ':1: cached owner bytes differ for ' + name + '; remove the corrupt cache and acquire the declared input again')
            inputs[name] = raw
        else:
            missing.append(name)
    if missing or repository is not None:
        with tempfile.TemporaryDirectory(prefix='boundary-owner-') as temporary:
            source = Path(repository).resolve() if repository is not None else Path(temporary) / 'objects'
            try:
                if repository is None:
                    subprocess.run(['git', 'init', '--bare', '--quiet', str(source)], check=True, capture_output=True, timeout=30)
                    subprocess.run(['git', '-C', str(source), 'fetch', '--quiet', '--depth=1', data['repository'], data['revision']], check=True, capture_output=True, timeout=120)
                resolved = subprocess.check_output(['git', '-C', str(source), 'rev-parse', data['revision'] + '^{commit}'], stderr=subprocess.PIPE, timeout=30).decode().strip()
            except (OSError, subprocess.SubprocessError) as error:
                raise ValueError(PIN + ':1: owner commit unavailable: publish the declared owner commit or pass --repository to a Git repository containing it; revision ' + data['revision']) from error
            if resolved != data['revision']:
                raise ValueError(PIN + ':1: owner commit differs from the declared revision')
            for name in FILES:
                try:
                    raw = subprocess.check_output(['git', '-C', str(source), 'show', data['revision'] + ':' + name], stderr=subprocess.PIPE, timeout=30)
                except (OSError, subprocess.SubprocessError) as error:
                    raise ValueError(PIN + ':1: owner commit lacks the declared input ' + name) from error
                if hashlib.sha256(raw).hexdigest() != data['files'][name]:
                    raise ValueError(PIN + ':1: owner SHA-256 differs for ' + name)
                inputs[name] = raw
            for name, raw in inputs.items():
                target = cache / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
                    output.write(raw)
                    candidate = Path(output.name)
                candidate.replace(target)
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, help='explicitly acquire committed owner bytes from a local Git repository')
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        inputs = verified_inputs(root, arguments.repository)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(refusal(error))
    print('OWNER INPUT VERIFIED: ' + read_pin(root)['revision'] + '; ' + str(len(inputs)) + ' files')


if __name__ == '__main__':
    main()
