#!/usr/bin/env python3
"""Retired suffix requests refuse at their record; complete files keep addresses."""
from pathlib import Path
import json
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
HINT = 'split the file into data and page'


def run():
    with tempfile.TemporaryDirectory(prefix='gate-reserved-fragments-') as tmp:
        world = Path(tmp)
        (world / '.gate').mkdir()
        (world / 'gate.manifest.swift').write_text('''public protocol Role {}
public protocol Mine {}
public enum WorldFile: Role {}
public enum Company: Mine {
    public typealias Kind = WorldFile
}
extension Company { public static var typeName: String { "Company.swift" } }
''')
        # Historical request shape: gate@1678c4c bin/playground_pages.py.
        # The marker is ordinary owner text after retirement of that reader.
        marker = '// the company below'
        source = '''public enum Alice: Employee {
    public typealias Rank = Lead
    public typealias Home = Finance
}
public enum MustHold: Team {
    @StructureBuilder
    public static var body: some Structure {
        VerifiedInDepartment<Alice, Sales>.self;
    }
}
''' + marker + '\n'
        company = world / 'Company.swift'
        company.write_text(source)
        record = world / '.gate/forms-definitions.json'
        base = dict(format=2, files=[], languages={}, shelf_overrides=False)

        def status():
            r = subprocess.run([str(ROOT / 'gate'), 'status', '--json'], cwd=world,
                               capture_output=True, text=True, timeout=30)
            return r.returncode, json.loads(r.stdout)

        def encoded(value):
            return json.dumps(dict(base, plain_fragments=value), indent=2) + '\n'

        empty = encoded([])
        record.write_text(empty)
        code, original = status()
        address = 'Company.swift:8'
        assert code == 1 and original['verdict'] == 'refused', original
        assert [r['address'] for r in original['refusals']] == [address], original
        record.write_text(json.dumps(base))
        absent_code, absent = status()
        assert absent_code == code
        for field in ('verdict', 'refusals', 'world', 'forms', 'unsupported'):
            assert absent.get(field) == original.get(field), (field, absent, original)
        company.write_text(source.replace('Alice, Sales', 'Alice, Finance'))
        assert status()[1]['verdict'] == 'holds'

        cases = [encoded([dict(path='Company.swift', marker=marker)]),
                 encoded('not a list'), encoded(None), encoded({})]
        cases += [empty.replace('"plain_fragments": []',
                                '"plain_fragments": [{"path":"Company.swift"}],\n  "plain_fragments": []')]
        for text in cases:
            record.write_text(text)
            line = next(i for i, s in enumerate(text.splitlines(), 1) if '"plain_fragments"' in s)
            # A duplicate is addressed at the repeated declaration.
            if text.count('"plain_fragments"') == 2:
                line = max(i for i, s in enumerate(text.splitlines(), 1) if '"plain_fragments"' in s)
            code, answer = status()
            assert code == 1 and answer['verdict'] == 'refused', answer
            assert any(r['address'] == f'.gate/forms-definitions.json:{line}'
                       and HINT in r['claim'] for r in answer['refusals']), answer

        record.write_text(empty)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        server = subprocess.Popen([str(ROOT / 'gate'), 'serve', str(port), '--no-open'],
                                  cwd=world, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            def ask(path, text=None):
                req = urllib.request.Request(f'http://127.0.0.1:{port}' + path,
                                             data=text.encode() if text is not None else None)
                try:
                    with urllib.request.urlopen(req, timeout=30) as r:
                        return r.status, json.loads(r.read())
                except urllib.error.HTTPError as e:
                    return e.code, json.loads(e.read())
            deadline = time.monotonic() + 30
            while True:
                try: assert ask('/status')[1]['verdict'] == 'holds'; break
                except OSError:
                    assert time.monotonic() < deadline and server.poll() is None
                    time.sleep(0.1)
            live = ask('/verdict?f=Company.swift', source)[1]
            assert live['verdict'] == 'refused' and [r['address'] for r in live['refusals']] == [address], live
            record.write_text(cases[0])
            for path in ('/status', '/verdict?f=Company.swift'):
                code, answer = ask(path, source if path.startswith('/verdict') else None)
                assert answer['verdict'] == 'refused', (path, code, answer)
                assert HINT in json.dumps(answer) and '.gate/forms-definitions.json:' in json.dumps(answer), answer
        finally:
            server.terminate(); server.wait(timeout=10)
        subprocess.run(['node', str(ROOT / 'tests/plain-fragments.js')], check=True)
        print('RESERVED FRAGMENTS GREEN: absent/empty, nonempty/type/duplicate record addresses, live refusal and complete-file addresses')


if __name__ == '__main__':
    run()
