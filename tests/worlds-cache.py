#!/usr/bin/env python3
"""Concurrent callers keep the complete pinned snapshot they were handed."""
import argparse
import hashlib
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'bin/playground-worlds.py'
SOURCES = [('showcase', 'fixture', 'SHOWCASE_SOURCE')]


def load(path):
    spec = importlib.util.spec_from_file_location('worlds_cache', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker(tool, source, record, cache, start, answers):
    try:
        module = load(tool)
        os.environ['SHOWCASE_SOURCE'] = source
        # A slow filesystem widens an existing publication window. No cache
        # byte or verdict is forged, and the processes have separate globals.
        copy = shutil.copyfile
        def delayed_copy(*args, **kwargs):
            time.sleep(.001)
            return copy(*args, **kwargs)
        shutil.copyfile = delayed_copy
        start.wait(timeout=20)
        raw = Path(record).read_bytes()
        files = json.loads(raw)['showcase']['files']
        path = module.materialize_record(Path(record), Path(cache), SOURCES)
        for _ in range(12):
            module.checked(path / 'showcase', files)
            assert (path / 'worlds.from').read_bytes() == raw, 'returned snapshot changed its record'
            time.sleep(.001)
        assert module.materialize_record(Path(record), Path(cache), SOURCES) == path
        answers.put(('ok', str(path)))
    except BaseException as error:
        answers.put(('error', type(error).__name__ + ': ' + str(error)))
        raise


def parallel(source, record, cache, rounds=3, callers=6):
    context = multiprocessing.get_context('spawn')
    for turn in range(rounds):
        start, answers = context.Barrier(callers), context.Queue()
        processes = [context.Process(target=worker, args=(str(TOOL), str(source), str(record),
                     str(cache / str(turn)), start, answers)) for _ in range(callers)]
        results = []
        try:
            for process in processes:
                process.start()
            deadline = time.monotonic() + 45
            for process in processes:
                process.join(max(0, deadline - time.monotonic()))
            for _ in processes:
                try:
                    results.append(answers.get(timeout=2))
                except queue.Empty:
                    break
            failures = [value for state, value in results if state != 'ok']
            assert len(results) == callers and not failures and all(p.exitcode == 0 for p in processes), (
                'parallel snapshot publication', turn, failures, [p.exitcode for p in processes])
            assert len({value for _, value in results}) == 1, 'one pin produced different snapshots'
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                process.join()
            answers.close()
            answers.join_thread()
    print(f'worlds cache: {rounds} cold races × {callers} processes; returned readers and warm hits hold')


def refused(action, address, reason):
    try:
        action()
    except (ValueError, OSError) as error:
        assert address in str(error) and reason in str(error), str(error)
    else:
        raise AssertionError('accepted damaged cache: ' + address)


def run():
    with tempfile.TemporaryDirectory(prefix='gate-worlds-race-') as temp:
        base = Path(temp)
        source = base / 'source'
        source.mkdir()
        contents = {'gate.manifest.swift': b'public enum Claims {}\n'}
        contents.update({f'parts/{i:03}.swift': (f'// part {i}\n' + 'x' * 1024 + '\n').encode() for i in range(64)})
        contents['.gate/forms-definitions.json'] = b'{"format":2,"files":[],"languages":{},"plain_fragments":[]}\n'
        for name, data in contents.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for args in [['init', '-q'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@test',
                     'commit', '-qm', 'one pinned world']]:
            subprocess.run(['git', '-C', str(source), *args], check=True)
        pin = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        spec = {'format': 1, 'showcase': {'revision': pin,
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}}}
        record = base / 'record.json'
        record.write_text(json.dumps(spec))
        parallel(source, record, base / 'parallel')
        module = load(TOOL)
        old = os.environ.get('SHOWCASE_SOURCE')
        os.environ['SHOWCASE_SOURCE'] = str(source)
        try:
            cache = base / 'snapshots'
            original_record = record.read_bytes()
            first = module.materialize_record(record, cache, SOURCES)
            spec['fixture_epoch'] = 2
            record.write_text(json.dumps(spec))
            second = module.materialize_record(record, cache, SOURCES)
            assert (first / 'worlds.from').read_bytes() == original_record, 'a new record invalidated an earlier reader'
            assert (second / 'worlds.from').read_bytes() == record.read_bytes()
            selected = second / 'showcase/parts/000.swift'
            original, metadata = selected.read_bytes(), selected.stat()
            selected.write_bytes(b'!' + original[1:])
            os.utime(selected, ns=(metadata.st_atime_ns, metadata.st_mtime_ns))
            refused(lambda: module.materialize_record(record, cache, SOURCES), str(selected), 'sha256')
            selected.write_bytes(original)
            selected.unlink()
            refused(lambda: module.materialize_record(record, cache, SOURCES), str(selected), 'missing recorded file')
            selected.write_bytes(original)
            provenance = second / 'worlds.from'
            provenance.write_bytes(b'{}')
            refused(lambda: module.materialize_record(record, cache, SOURCES), str(second), 'provenance record')
            provenance.write_bytes(record.read_bytes())
            note = (second / 'from').read_bytes()
            (second / 'from').write_text('{broken')
            refused(lambda: module.materialize_record(record, cache, SOURCES), str(second), 'provenance')
            (second / 'from').write_bytes(note)
            # A copy can fail after the source was checked. Those bytes must
            # never become a published snapshot or displace an earlier reader.
            before = set(cache.iterdir())
            spec['fixture_epoch'] = 3
            record.write_text(json.dumps(spec))
            copy = shutil.copyfile
            def damaged_copy(src, dst, *args, **kwargs):
                result = copy(src, dst, *args, **kwargs)
                if Path(src) == source / 'parts/000.swift':
                    Path(dst).write_bytes(b'!' + original[1:])
                return result
            try:
                shutil.copyfile = damaged_copy
                refused(lambda: module.materialize_record(record, cache, SOURCES), 'parts/000.swift', 'sha256')
            finally:
                shutil.copyfile = copy
            assert set(cache.iterdir()) == before, 'a damaged stage was published or left behind'
            assert (first / 'worlds.from').read_bytes() == original_record
            module.checked(second / 'showcase', spec['showcase']['files'])
        finally:
            if old is None:
                os.environ.pop('SHOWCASE_SOURCE', None)
            else:
                os.environ['SHOWCASE_SOURCE'] = old
    print('WORLDS CACHE GREEN: stable snapshots; byte corruption with restored mtime, loss, provenance and damaged stages refuse')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool', type=Path, default=TOOL, help='also exercise a recorded earlier materializer')
    TOOL = parser.parse_args().tool.resolve()
    run()
