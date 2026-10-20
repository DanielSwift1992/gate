#!/usr/bin/env python3
"""Lay only the recorded bytes, and check them again on every cache hit."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent.parent
RECORD = HERE / 'bin/playground-worlds.from'
URL = 'https://github.com/DanielSwift1992/'


def checked(root, files, binary=()):
    for name, want in files.items():
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'{path}: missing recorded file')
        data = path.read_bytes()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            raise ValueError(f'{path}: sha256 {got}, expected {want}')
        if name not in binary and b'\r' in data:
            raise ValueError(f'{path}: the record names LF bytes')


def materialize():
    record = json.loads(RECORD.read_text())
    pin = record['showcase']['revision']
    cache = HERE / 'bin/.worlds/playground' / pin
    local = {k: os.path.abspath(os.environ[e]) if os.environ.get(e) else None
             for k, e in [('showcase', 'SHOWCASE_SOURCE'), ('theory', 'VI_THEORY_PATH'), ('baseline', 'PLAYGROUND_SOURCE')]}
    note = {'record_sha256': hashlib.sha256(RECORD.read_bytes()).hexdigest(),
            'sources': {k: ('local: ' + v if v else 'public pin') for k, v in local.items()}}
    if not cache.exists() or json.loads((cache / 'from').read_text()) != note:
        cache.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='gate-worlds-') as temp:
            stage = Path(temp) / 'cache'
            stage.mkdir()
            for kind, repo in [('showcase', 'verification-is-identification-showcase'),
                               ('theory', 'verification-is-identification'), ('baseline', 'typed-playground')]:
                spec = record[kind]
                if local[kind]:
                    source = Path(local[kind])
                    head = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
                    if head != spec['revision']:
                        raise ValueError(f'{source}: local HEAD {head}, expected {spec["revision"]}')
                else:
                    source = Path(temp) / kind
                    source.mkdir()
                    subprocess.run(['git', '-C', str(source), 'init', '-q'], check=True)
                    subprocess.run(['git', '-C', str(source), 'config', 'core.autocrlf', 'false'], check=True)
                    subprocess.run(['git', '-C', str(source), 'config', 'core.eol', 'lf'], check=True)
                    subprocess.run(['git', '-C', str(source), 'fetch', '-q', '--depth', '1',
                                    URL + repo, spec['revision']], check=True)
                    subprocess.run(['git', '-C', str(source), 'checkout', '-q', 'FETCH_HEAD'], check=True)
                checked(source, spec['files'], spec.get('binary', ()))
                for name in spec['files']:
                    dest = stage / kind / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source / name, dest)
            (stage / 'from').write_text(json.dumps(note, indent=2) + '\n')
            shutil.copyfile(RECORD, stage / 'worlds.from')
            if cache.exists():
                shutil.rmtree(cache)
            shutil.copytree(stage, cache)
    for kind in ('showcase', 'theory', 'baseline'):
        checked(cache / kind, record[kind]['files'], record[kind].get('binary', ()))
    if (cache / 'worlds.from').read_bytes() != RECORD.read_bytes():
        raise ValueError(f'{cache}: changed provenance record')
    return cache


if __name__ == '__main__':
    try:
        print(materialize())
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        raise SystemExit('playground-worlds: ' + str(e))
