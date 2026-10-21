#!/usr/bin/env python3
"""One company question spans declared WorldFiles and keeps each source address."""
from pathlib import Path
import json
import socket
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / 'gate'


def run():
    with tempfile.TemporaryDirectory(prefix='gate-company-parts-') as tmp:
        world = Path(tmp)
        for name in ('north', 'south', '.gate'):
            (world / name).mkdir()
        manifest = 'public protocol Role {}\npublic protocol Mine {}\npublic enum WorldFile: Role {}\n'
        for row, name in [('North', 'north/part.swift'), ('South', 'south/part.swift')]:
            manifest += 'public enum ' + row + ': Mine {\n    public typealias Kind = WorldFile\n}\nextension ' + row + ' { public static var typeName: String { "' + name + '" } }\n'
        (world / 'gate.manifest.swift').write_text(manifest)
        (world / '.gate/forms-definitions.json').write_text(json.dumps(dict(format=2, files=[], languages={}, plain_fragments=[], shelf_overrides=False)))
        first = 'public enum Alice: Employee {\n    public typealias Rank = Lead\n    public typealias Home = Bob.Home\n}\n'
        last = '''public enum Bob: Employee {
    public typealias Rank = Lead
    public typealias Home = Finance
}
public enum Both: Team {
    @StructureBuilder
    public static var body: some Structure {
        VerifiedInDepartment<
            Alice,
            Finance
        >.self;
    }
}
'''
        (world / 'north/part.swift').write_text(first)
        (world / 'south/part.swift').write_text(last)
        def status():
            result = subprocess.run([str(GATE), 'status', '--json'], cwd=world,
                                    capture_output=True, text=True, timeout=30)
            return result.returncode, json.loads(result.stdout)
        code, clean = status()
        assert code == 0 and clean['verdict'] == 'holds', clean
        # Ask the pinned raw court the same full set once, as an independent oracle.
        joined = world / 'whole.txt'; joined.write_text(first + '\n' + last)
        raw = subprocess.run([str(GATE), 'judge', str(joined)], cwd=world,
                             capture_output=True, text=True, timeout=30)
        import re
        counts = re.search(r'(\d+) declarations · (\d+) lookups · (\d+) premises', raw.stdout)
        assert raw.returncode == 0 and counts, raw
        assert clean['world'] == dict(zip(('declarations', 'lookups', 'premises'), map(int, counts.groups()))), clean
        changed = last.replace('Home = Finance', 'Home = Sales')
        line = next(i for i, s in enumerate(last.splitlines(), 1) if 'Alice,' in s)
        address = 'south/part.swift:' + str(line)
        (world / 'south/part.swift').write_text(changed)
        code, refused = status()
        assert code == 1 and refused['verdict'] == 'refused', refused
        assert [r['address'] for r in refused['refusals']] == [address], refused
        (world / 'south/part.swift').write_text(last)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        server = subprocess.Popen([str(GATE), 'serve', str(port), '--no-open'], cwd=world,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            def ask(path, text=None):
                request = urllib.request.Request(f'http://127.0.0.1:{port}' + path,
                                                 data=text.encode() if text is not None else None)
                return json.loads(urllib.request.urlopen(request, timeout=30).read())
            deadline = time.monotonic() + 30
            while True:
                try: ask('/files'); break
                except OSError:
                    assert time.monotonic() < deadline and server.poll() is None
                    time.sleep(0.1)
            live = ask('/verdict?f=south%2Fpart.swift', changed)
            assert live['verdict'] == 'refused' and [r['address'] for r in live['refusals']] == [address], live
            assert ask('/verdict?f=south%2Fpart.swift', last)['verdict'] == 'holds'
            neighbor = last.replace('    }\n}\n',
                '        VerifiedInDepartment<Alice, Sales>.self;\n    }\n}\n')
            neighbor_line = next(i for i, s in enumerate(neighbor.splitlines(), 1) if 'Alice, Sales' in s)
            neighbor_bad = ask('/verdict?f=south%2Fpart.swift', neighbor)
            assert [r['address'] for r in neighbor_bad['refusals']] == [
                'south/part.swift:' + str(neighbor_line)], neighbor_bad
            # A changed body still has its own addressed structural refusal.
            unfinished = last.replace('>.self;', '')
            bad_entry = ask('/verdict?f=south%2Fpart.swift', unfinished)
            assert bad_entry['verdict'] == 'refused' and any(
                'entry' in r['claim'] for r in bad_entry['refusals']), bad_entry
            assert ask('/verdict?f=south%2Fpart.swift', last)['verdict'] == 'holds'
            (world / 'south/part.swift').unlink()
            code, missing = status()
            assert code == 1 and missing['verdict'] == 'refused' and missing['refusals'], missing
        finally:
            server.terminate(); server.wait(timeout=10)
    print('COMPANY PARTS GREEN: one full question, forward reference, same basename, original address and missing input')


if __name__ == '__main__':
    run()
