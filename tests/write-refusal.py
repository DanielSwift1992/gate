#!/usr/bin/env python3
"""Unsupported writes refuse; a native failed write cannot claim it landed."""
import ast
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent.parent


def run():
    tree = ast.parse((HERE / 'bin/build-pages.py').read_text())
    shim = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'shim' for t in n.targets)
                and isinstance(n.value, ast.Constant))
    if '--native-only' not in sys.argv:
        subprocess.run(['node', str(HERE / 'tests/write-refusal.js')], check=True, text=True,
                       input=json.dumps(dict(store=(HERE / 'web/reader-draft.js').read_text(), shim=shim, ui=(HERE / 'web/ui.html').read_text())))
    # Atomic replacement must fail even when the file itself is readable. This
    # is the real host, not a stub returning the answer the test wants to see.
    with tempfile.TemporaryDirectory(prefix='gate-write-refusal-') as temp:
        root = Path(temp)
        (root / 'gate.swift').write_text('public enum Sales: Department {}\n')
        mine = root / 'values.swift'
        mine.write_text('// role: forms\npublic typealias Width = Unit\n')
        subprocess.run([str(HERE / 'gate'), 'mine', str(mine), '--role', 'forms'],
                       cwd=root, check=True, capture_output=True)
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        host = subprocess.Popen([str(HERE / 'gate'), 'serve', '--port', str(port), '--no-open'],
                                cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        def request(route, body=None):
            req = urllib.request.Request(f'http://127.0.0.1:{port}' + route, data=body,
                                         method='GET' if body is None else 'PUT')
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return r.status, r.read()
            except urllib.error.HTTPError as e:
                return e.code, e.read()
        try:
            for _ in range(150):
                try:
                    if request('/files')[0] == 200:
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise AssertionError('native serve did not start')
            before = mine.read_bytes()
            os.chmod(root, 0o555)
            for route in ['/world?f=values.swift', '/value?name=Width&to=2']:
                code, body = request(route, b'not written')
                said = json.loads(body or b'{}')
                assert code == 409, (route, code, said)
                assert said['address'] == 'values.swift' and said['reason'] and said['next']
                assert mine.read_bytes() == before
                assert request('/files')[0] == 200, 'the host remains available after a refusal'
            os.chmod(root, 0o755)
            code, body = request('/value?name=Width&to=2', b'')
            assert code == 200 and json.loads(body)['file'] == 'values.swift'
            assert mine.read_bytes() != before
        finally:
            os.chmod(root, 0o755)
            host.terminate()
            host.communicate(timeout=30)
    print('NATIVE WRITE REFUSAL GREEN: failed world/value writes refuse; retry writes')


if __name__ == '__main__':
    run()
