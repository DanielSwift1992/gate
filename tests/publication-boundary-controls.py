#!/usr/bin/env python3
"""Publication-law twins, addressed refusals, and fail-closed input selection."""
import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
specification = importlib.util.spec_from_file_location('publication', ROOT/'tests/publication-boundary.py')
law = importlib.util.module_from_spec(specification)
specification.loader.exec_module(law)
policy = law.load()
builder = 'BoundaryBuilder'
home = '/' + 'home' + '/account/source.swift'
windows = 'C:' + '\\' + 'Users' + '\\account\\source.swift'
private = '/' + 'private/var/folders/ab/accountid/T/source.swift'
email = 'private-author' + '@' + 'mailbox.net'
cases = [
    ('posix home', home), ('macOS home', '/' + 'Users/account/source.swift'),
    ('account temp', private), ('non-private temp spelling', private.removeprefix('/private')),
    ('windows home', windows), ('windows lower case', windows.lower()),
    ('unc home', '\\\\server' + '\\' + 'Users' + '\\account\\source.swift'),
    ('json slashes', home.replace('/', '\\/')), ('json windows', windows.replace('\\', '\\\\')),
    ('hostname at', builder+'@MacBook-Pro.local'), ('hostname dash', builder+'-MacBook-Pro.local'),
    ('hostname dot', builder+'.local'), ('underscore', '_'+builder), ('name alone', builder),
    ('root account', '/'+'root/.config/cache'), ('email', email),
    ('file URL', 'file://'+home), ('assignment', 'file='+home), ('relative climb', '../..'+home),
]
count = 0
for label, text in cases:
    raw = text.encode()
    variants = [('raw', raw), ('UTF-16LE', text.encode('utf-16le')), ('UTF-16BE', text.encode('utf-16be')),
                ('base64', b'var VI_COURT_WASM_BASE64 = "'+base64.b64encode(raw)+b'";')]
    for encoding, payload in variants:
        findings = law.publication_content(policy, 'fixture.bin', payload, [builder])
        assert findings, (label, encoding)
        assert all(item.startswith('fixture.bin') and ':byte ' in item for item in findings), findings
        assert all(text not in item for item in findings), 'private bytes were echoed'
        print('REFUSED:', label, encoding, '->', findings[0])
        count += 1

ordinary = [
    'GET /users/42', 'https://api.github.com/users/octocat/repos', "'/home/:id'",
    'https://example.com/home/index.html', '/Users/Shared/file', 'the /root/ of the tree',
    'cd ~/gate', '/vi/Sources/Court/File.swift', '/rustc/toolchain/library/file.rs',
    'prefix'+builder, builder+'suffix', 'builderBoundaryBuilder2',
    'x'+home, '_'+home, '-'+home, 'person@example.com', 'fixture@localhost', 'person@domain.test', 'owner/repo@v0.2.5',
]
for text in ordinary:
    assert not law.publication_content(policy, 'ordinary.txt', text.encode(), [builder]), text
    print('ALLOWED:', text)
    count += 1

with tempfile.TemporaryDirectory(prefix='publication-boundary-controls-') as temporary:
    tree = Path(temporary)/'site'; tree.mkdir()
    path = tree/'snapshot.json'; path.write_text(json.dumps({'me': email}))
    command = [sys.executable, str(ROOT/'tests/publication-boundary.py'), '--publication-tree', str(tree)]
    refusal = subprocess.run(command, capture_output=True, text=True)
    assert refusal.returncode == 1 and 'site/snapshot.json:byte ' in refusal.stdout
    assert email not in refusal.stdout and str(tree) not in refusal.stdout
    print('REFUSED: publication tree email ->', refusal.stdout.strip())
    path.write_text('{"commits": []}')
    assert subprocess.run(command, capture_output=True).returncode == 0
    missing = subprocess.run([sys.executable, str(ROOT/'tests/publication-boundary.py'), '--artifact', str(tree/'missing')], capture_output=True)
    assert missing.returncode != 0 and b'missing:byte 0' in missing.stdout
    count += 3
print('PUBLICATION CONTROLS HOLD:', count, 'twins and addressed input controls')
