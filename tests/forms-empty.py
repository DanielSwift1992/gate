#!/usr/bin/env python3
"""Remove the sole application through the same doors a user reads."""
from pathlib import Path
import json
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / 'gate'
BASE = '''public protocol Choice {}
public protocol Paired {}
public enum Coral: Choice {}
public enum Other: Choice {}
public enum Pair<L: Choice, R: Choice> {}
extension Pair: Paired where L == R {}
'''
APPLICATION = 'public typealias Same = Pair<Coral, Coral>\n'
REASON = 'no declared applications'


def run():
    with tempfile.TemporaryDirectory(prefix='gate-empty-forms-') as tmp:
        owner = Path(tmp)
        (owner / '.gate').mkdir()
        (owner / 'gate.manifest.swift').write_text('''public protocol Role {}
public protocol Mine {}
public enum FormsFile: Role {}
public enum Claims: Mine {
    public typealias Kind = FormsFile
}
extension Claims { public static var typeName: String { "Claims.swift" } }
''')
        (owner / '.gate/forms-definitions.json').write_text(json.dumps(dict(
            format=2, files=[], languages={}, plain_fragments=[], shelf_overrides=False)))
        forms = owner / 'Claims.swift'
        forms.write_text(BASE + APPLICATION)

        def command(*args):
            return subprocess.run([str(GATE), *args], cwd=owner, capture_output=True,
                                  text=True, timeout=30)

        def status(expected, code, *args):
            answer = command('status', *args, '--json')
            data = json.loads(answer.stdout)
            assert answer.returncode == code and data['verdict'] == expected, (answer, data)
            return data

        held = status('holds', 0)
        assert held['forms']['equalities'] == 1, held
        forms.write_text(BASE)
        empty = status('empty', 2)
        assert empty['forms']['equalities'] == 0 and empty['reason'] == REASON, empty
        assert not empty['refusals'] and not empty.get('unsupported'), empty
        assert command('status').stdout.startswith('status: empty · ' + REASON)
        fsck = command('fsck', '--json')
        assert fsck.returncode == 2 and json.loads(fsck.stdout)['verdict'] == 'empty', fsck
        hook = status('empty', 0, '--hook')
        assert hook['reason'] == REASON and hook['forms'] == empty['forms'], hook
        judge = subprocess.run([str(ROOT / 'bin/gate-judge'), 'judge', 'where', str(forms)],
                               capture_output=True, text=True, timeout=30)
        assert judge.returncode == 2 and 'no equalities or memberships were judged' in judge.stderr, judge

        # Exercise the shipped hook in git: an empty request may be saved.
        subprocess.run(['git', 'init', '-q', str(owner)], check=True)
        (owner / '.githooks').mkdir()
        shutil.copy2(ROOT / '.githooks/pre-commit', owner / '.githooks/pre-commit')
        (owner / 'gate').symlink_to(ROOT / 'bin/gate-cli')
        subprocess.run(['git', 'config', 'core.hooksPath', '.githooks'], cwd=owner, check=True)
        subprocess.run(['git', 'add', '.'], cwd=owner, check=True)
        commit = subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@test',
                                 'commit', '-qm', 'save an empty request'], cwd=owner,
                                capture_output=True, text=True, timeout=30)
        assert commit.returncode == 0 and 'status: empty · ' + REASON in commit.stdout + commit.stderr, commit

        badge = command('badge', '-o', 'empty.svg', '--json')
        data = json.loads(badge.stdout)
        assert badge.returncode == 2 and data['verdict'] == 'empty' and data['reason'] == REASON, data
        assert REASON in (owner / 'empty.svg').read_text() and '#007D36' not in (owner / 'empty.svg').read_text()

        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        server = subprocess.Popen([str(GATE), 'serve', str(port), '--no-open'], cwd=owner,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            def request(path, body=None):
                req = urllib.request.Request(f'http://127.0.0.1:{port}' + path,
                                             data=body.encode() if body is not None else None)
                return json.loads(urllib.request.urlopen(req, timeout=30).read())
            deadline = time.monotonic() + 30
            while True:
                try:
                    request('/files')
                    break
                except OSError:
                    assert server.poll() is None and time.monotonic() < deadline, 'serve did not start'
                    time.sleep(0.1)
            served = request('/status')
            assert served['verdict'] == 'empty' and served['reason'] == REASON, served
            live = request('/verdict?f=Claims.swift', BASE)
            assert live['verdict'] == 'empty' and live['reason'] == REASON and live['checked'] == 0, live
            restored = request('/verdict?f=Claims.swift', BASE + APPLICATION)
            assert restored['verdict'] == 'holds' and restored['checked'] == 1, restored
            refused = request('/verdict?f=Claims.swift', BASE + APPLICATION.replace('Coral, Coral', 'Coral, Other'))
            assert refused['verdict'] == 'refused' and refused['refusals'], refused
            assert any(r['address'].startswith('Claims.swift:') for r in refused['refusals']), refused
            membership = '''public protocol Allowed {}
public protocol Admitted {}
public enum Yes: Allowed {}
public enum Uses<T> {}
extension Uses: Admitted where T: Allowed {}
public typealias Membership = Uses<Yes>
'''
            forms.write_text(membership)
            member = status('holds', 0)
            assert member['forms']['equalities'] == 0 and member['forms']['memberships'] == 1, member
            assert request('/verdict?f=Claims.swift', membership)['verdict'] == 'holds'
            forms.unlink()
            missing = status('refused', 1, '--hook')
            assert missing['refusals'], missing
            # Render the real chip implementation against the real server answers.
            chip = subprocess.run(['node', str(ROOT / 'tests/forms-empty.js')],
                                  input=json.dumps([live, restored, refused]), capture_output=True,
                                  text=True, timeout=30)
            assert chip.returncode == 0, chip.stdout + chip.stderr
            print(json.dumps(dict(one_application=held, removed_application=empty,
                                  hook=hook, live_empty=live, live_restored=restored,
                                  live_refused=refused, membership_only=member,
                                  missing_input=missing), sort_keys=True))
        finally:
            server.terminate()
            server.communicate(timeout=10)
    print('empty/holds/refused, membership-only, missing input, hook commit and live bench: PASS')


if __name__ == '__main__':
    run()
