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
        author_email = 'private-pages-author' + '@' + 'mailbox.net'
        author_name = 'Pages "Fixture"'
        subprocess.run(['git','-C',str(source),'add','.'],check=True)
        subprocess.run(['git','-C',str(source),'-c','user.name='+author_name,'-c','user.email='+author_email,'commit','-qm','selected world history'],check=True)
        expected_commit = dict(zip(('short','when','subject','author'), subprocess.check_output(['git','-C',str(source),'log','-1','--format=%h%x1f%aI%x1f%s%x1f%an','--abbrev=8'],text=True).strip().split('\x1f')))
        answer = build('--source', str(source))
        assert answer.returncode == 0, (answer.stdout, answer.stderr)
        html = (out / 'index.html').read_text()
        assert local_email not in html, 'Pages retained local Git identity'
        assert author_email not in html, 'Pages retained historical author email'
        snapshots,_ = json.JSONDecoder().raw_decode(html.split('const SNAP = ',1)[1])
        journal = json.loads(snapshots['/log?n=1&scope=world'])
        assert 'me' not in journal and journal['commits']==[expected_commit], journal
        assert journal['next']=='Publish a new snapshot from the source repository to update this history.', journal
        files=json.loads(snapshots['/files']);personal=files['personal']
        assert personal and json.loads(snapshots['/gitstatus?f='+personal])['file']==personal
        print('PAGES GITSTATUS HOLDS: the personal snapshot names its bench file, never private storage')
        assert subprocess.check_output(['git','-C',str(source),'log','-1','--format=%ae'],text=True).strip()==author_email
        print('PAGES HISTORY HOLDS: same four-field Swift projection; repository author email intact')
        assert 'Rooms.swift' in html and 'roadtest=1' not in html and 'ROAD ALL GREEN' not in html
        assert not (source / 'CODEOWNERS').exists() and not (source / 'ownership.swift').exists()
        # A compound world under the account home must publish the same file
        # addresses as any other world, without copying its builder's directory.
        with tempfile.TemporaryDirectory(prefix='gate-publisher-home-', dir=Path.home()) as home:
            home_source = Path(home)
            (home_source / 'gate.manifest.swift').write_text('''public protocol Role {}
public enum WorldFile: Role {}
public protocol Mine {}
public enum First: Mine {
    public typealias Kind = WorldFile
}
extension First {
    public static var typeName: String { "First.swift" }
}
public enum Second: Mine {
    public typealias Kind = WorldFile
}
extension Second {
    public static var typeName: String { "Second.swift" }
}
''')
            for name in ('First', 'Second'):
                (home_source / (name + '.swift')).write_text('public enum ' + name + ' {}\n')
            home_out = root / 'home-site'
            result = subprocess.run([sys.executable, str(ROOT / 'bin/build-pages.py'), str(home_out),
                                     '--source', str(home_source)], capture_output=True, text=True, timeout=90)
            assert result.returncode == 0, (result.stdout, result.stderr)
            delivered = (home_out / 'index.html').read_text()
            snap, _ = json.JSONDecoder().raw_decode(delivered.split('const SNAP = ', 1)[1])
            reading = json.loads(snap['/status'])
            boundary = subprocess.run([sys.executable, str(ROOT / 'tests/publication-boundary.py'),
                                       '--publication-tree', str(home_out)], capture_output=True, text=True, timeout=60)
            assert boundary.returncode == 0, boundary.stdout + boundary.stderr
            assert set(reading['facts']) == {'First.swift', 'Second.swift'}, reading['facts']
            assert str(home_source) not in delivered
            print('PAGES HOME SNAPSHOT HOLDS: compound facts are world-relative; actual publication boundary accepts the delivery')
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
        # A public field containing a mailbox is not scrubbed. The same byte
        # law must refuse the emitted history at its address, without a stack
        # trace exposing the build directory.
        (source/'Rooms.swift').write_text(text+'\n')
        subprocess.run(['git','-C',str(source),'add','Rooms.swift'],check=True)
        subprocess.run(['git','-C',str(source),'-c','user.name='+author_name,'commit','-qm','contact '+author_email],check=True)
        refused = build('--source', str(source))
        assert refused.returncode != 0, 'historical subject email escaped the byte law'
        assert 'site/index.html' in refused.stdout and ':byte ' in refused.stdout and 'email address' in refused.stdout, refused.stdout
        assert 'Traceback' not in refused.stderr and 'publication byte boundary refused' in refused.stderr, refused.stderr
        assert author_email not in refused.stdout+refused.stderr
        print('PAGES HISTORY REFUSED: subject email has a byte address; no private bytes or traceback')
    print('PUBLISHER GREEN: explicit input, no implicit example or roadtest')

if __name__ == '__main__':
    run()
