"""A publication must name its input; a sample is never an implicit dependency."""
import json
import runpy
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parent.parent

def run():
    runpy.run_path(str(ROOT / 'tests/snapshot-http.py'))['run']()
    with tempfile.TemporaryDirectory(prefix='gate-publisher-') as tmp:
        root = Path(tmp); out = root / 'site'; source = root / 'a-different-repository'
        def build(*args):
            return subprocess.run([sys.executable, str(ROOT / 'bin/build-pages.py'), str(out), *args], capture_output=True, text=True, timeout=90)
        missing = build()
        assert missing.returncode == 2 and '--source' in missing.stderr and not out.exists(), missing.stderr
        missing_source = build('--worlds', '--source', str(source))
        assert missing_source.returncode != 0 and str(source) in missing_source.stderr and not out.exists(), missing_source.stderr
        # Nothing in this selected input is CODEOWNERS, Alice or a sample name.
        source.mkdir()
        (source / 'gate.manifest.swift').write_text('''public protocol Role {}
public enum FormsFile: Role {}
public protocol Mine {}
public enum MyInput: Mine { public typealias Kind = FormsFile }
extension MyInput { public static var typeName: String { "Rooms.swift" } }
''')
        text = 'public enum A {}\npublic enum B {}\npublic enum Claim where A == B {}\n'
        (source / 'Rooms.swift').write_text(text)
        subprocess.run(['git', '-C', str(source), 'init', '-q'], check=True)
        local_email = 'private-pages-builder' + '@' + 'mailbox.net'
        subprocess.run(['git','-C',str(source),'config','user.email',local_email],check=True)
        answer = build('--source', str(source))
        assert answer.returncode == 0, (answer.stdout, answer.stderr)
        html = (out / 'index.html').read_text()
        assert local_email not in html, 'Pages retained local Git identity'
        print('PAGES IDENTITY HOLDS: configured email is absent from the publication')
        assert 'Rooms.swift' in html and 'roadtest=1' not in html and 'ROAD ALL GREEN' not in html
        assert not (source / 'CODEOWNERS').exists() and not (source / 'ownership.swift').exists()
        # An explicitly selected example still goes through the same generic door.
        example = root / 'selected-example'
        subprocess.run([str(ROOT / 'gate'), 'demo', str(example)], capture_output=True, check=True)
        selected = build('--source', str(example))
        assert selected.returncode == 0, (selected.stdout, selected.stderr)
        assert 'ownership.swift' in (out / 'index.html').read_text()
        # The same declared recipes travel with a one-file installation.
        binary = root / 'standalone' / 'gate-cli'; binary.parent.mkdir()
        shutil.copy2(ROOT / 'bin/gate-cli', binary)
        recipes = json.loads((ROOT / 'examples/index.json').read_text())
        for kind, argv in [('codeowners', []), ('seam', ['seam']), ('organization', ['org'])]:
            target = root / ('installed-' + kind)
            result = subprocess.run([str(binary), 'demo', *argv, str(target), '--json'], cwd=root,
                                    capture_output=True, text=True, timeout=90)
            assert result.returncode == 0, (kind, result.stdout, result.stderr)
            for file in recipes[kind]:
                assert (target / file).read_bytes() == (ROOT / 'examples' / kind / file).read_bytes(), (kind, file)
        for name in ['people.csv', 'grants.csv']:
            assert (ROOT / 'examples/organization/tables' / name).read_bytes() == (ROOT / 'demo' / name).read_bytes()
    print('PUBLISHER GREEN: explicit input, no implicit example or roadtest')

if __name__ == '__main__':
    run()
