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


def materialize_record(record_path, cache, sources):
    raw = record_path.read_bytes()
    record = json.loads(raw)
    local = {k: os.path.abspath(os.environ[e]) if os.environ.get(e) else None
             for k, repo, e in sources}
    note = {'record_sha256': hashlib.sha256(raw).hexdigest(),
            'repositories': {k: URL + repo for k, repo, _ in sources},
            'sources': {k: ('local: ' + v if v else 'public pin') for k, v in local.items()}}
    # A caller keeps the snapshot it was handed, including when another call
    # selects a new record at the same showcase pin. Never replace that path.
    key = hashlib.sha256(json.dumps(note, sort_keys=True).encode()).hexdigest()
    cache = cache / key

    def verify(root):
        if root.is_symlink():
            raise ValueError(f'{root}: a snapshot must not be a symlink')
        try:
            provenance = json.loads((root / 'from').read_text())
        except (ValueError, OSError) as error:
            raise ValueError(f'{root / "from"}: cannot read provenance: {error}') from error
        if provenance != note:
            raise ValueError(f'{root / "from"}: changed provenance note')
        for kind, _, _ in sources:
            checked(root / kind, record[kind]['files'], record[kind].get('binary', ()))
        if (root / 'worlds.from').read_bytes() != raw:
            raise ValueError(f'{root}: changed provenance record')

    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        # Stage beside the destination so publication is one filesystem rename.
        # Concurrent losers check the complete winner; nobody removes it.
        with tempfile.TemporaryDirectory(prefix='.gate-worlds-', dir=cache.parent) as temp:
            stage = Path(temp) / 'cache'
            stage.mkdir()
            for kind, repo, _ in sources:
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
            (stage / 'worlds.from').write_bytes(raw)
            verify(stage)
            try:
                stage.rename(cache)
            except OSError:
                if not cache.exists():
                    raise
    verify(cache)
    return cache


def materialize():
    record = json.loads(RECORD.read_text())
    return materialize_record(RECORD, HERE / 'bin/.worlds/playground' / record['showcase']['revision'],
        [('showcase', 'verification-is-identification-showcase', 'SHOWCASE_SOURCE'),
         ('theory', 'verification-is-identification', 'VI_THEORY_PATH')])


if __name__ == '__main__':
    try:
        print(materialize())
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        raise SystemExit('playground-worlds: ' + str(e))
