#!/usr/bin/env python3
"""Publication-law twins, addressed refusals, and fail-closed input selection."""
import base64
import importlib.util
import json
import os
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
personal = '../../../../../' + 'Users/account/.gate/me/worlds/world/my.swift'
email = 'private-author' + '@' + 'mailbox.net'
unicode_account = '\u0414\u0430\u043d\u0438\u0438\u043b'
unicode_windows = 'C:' + '\\' + 'Users' + '\\' + unicode_account + '\\source.swift'
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
    ('relative personal storage', personal),
    ('email sentence stop', email+'.'), ('email before HTML close', '<p>'+email+'.</p>'),
    ('email multi-label domain', 'a@b.com.au'), ('email beyond reserved label', 'a@b.test.au'),
    ('git mailbox without path', 'git@github.com'), ('git mailbox empty path', 'git@github.com:'),
    ('ordinary mailbox with colon', 'person@github.com:owner/repo.git'),
    ('Unicode windows home', unicode_windows),
    ('Unicode POSIX home', '/'+'home/'+unicode_account+'/source.swift'),
    ('Unicode macOS home', '/'+'Users/'+unicode_account+'/source.swift'),
    ('Unicode escaped home', unicode_windows.replace('\\', '\\\\')),
    ('Unicode UNC home', '\\\\server'+'\\'+'Users'+'\\'+unicode_account+'\\source.swift'),
    ('astral account letter', '/'+'home/'+'\U00010400'+'/source.swift'),
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
    'a@b.com.au.invalid.', 'person@example.com.', 'git@github.com:owner/repo.git',
    'git@code.example-corp.org:team/repo.git', 'git@host:repo',
    '/vi/'+unicode_account+'/source.swift', '/Users/Shared/'+unicode_account,
]
for text in ordinary:
    assert not law.publication_content(policy, 'ordinary.txt', text.encode(), [builder]), text
    print('ALLOWED:', text)
    count += 1

# Service identities do not turn ordinary product text into private names.
# Their home paths remain in the same refusal class, in every encoding above.
for account in policy['service_builder_accounts']:
    assert not law.publication_content(policy, 'product.bin', ('no toolchain on the '+account).encode(), [account])
    assert law.publication_content(policy, 'product.bin', ('/'+ 'home/'+account+'/file').encode(), [account])
    assert law.publication_content(policy, 'product.bin', ('C:'+'\\'+'Users'+'\\'+account+'\\file').encode(), [account])
    count += 3
    print('SERVICE ACCOUNT HOLDS:', account, 'product word allowed; home paths refused')

# An address is the first byte of the encoded path, even after non-ASCII text
# and at either UTF-16 alignment. The astral prefix occupies two code units.
prefix = '\u03bb\U00010400 '
for encoding in ('utf-8', 'utf-16le', 'utf-16be'):
    for alignment in (0, 1):
        payload = b'!'*alignment + (prefix+unicode_windows).encode(encoding)
        address = alignment + len(prefix.encode(encoding))
        findings = law.publication_content(policy, 'unicode.bin', payload)
        assert any('unicode.bin'+('' if encoding=='utf-8' else ' ['+encoding.upper()+']')+':byte '+str(address)+':' in x for x in findings), findings
        count += 1
        print('UNICODE ADDRESS HOLDS:', encoding, alignment, 'byte', address)

# Diagnostics identify the byte class without publishing the matched identity.
# A domain can itself contain the current private builder name.
diagnostics = [
    (home, 'sample', '/home/<redacted>', ['account', 'source.swift']),
    ('/'+'Users/'+unicode_account+'/private-project/file', 'sample', '/Users/<redacted>', [unicode_account, 'private-project']),
    (private, 'sample', '/private/var/folders/<redacted>/<redacted>', ['accountid', '/ab/', 'source.swift']),
    (private.removeprefix('/private'), 'sample', '/var/folders/<redacted>/<redacted>', ['accountid', '/ab/']),
    (windows, 'sample', r'C:\Users\<redacted>', ['account', 'source.swift']),
    ('\\\\server' + '\\' + 'Users' + '\\account\\private-project', 'sample', r'\\<redacted>\Users\<redacted>', ['server', 'account', 'private-project']),
    ('/'+'root/private-project/file', 'sample', '/root/<redacted>', ['private-project']),
    (builder, 'sample', '<redacted>', [builder]),
    (email, 'domain', 'mailbox.net', ['private-author']),
    ('private-author@'+builder+'.mail.net', 'domain', '<redacted>.mail.net', ['private-author', builder.lower()]),
]
for text, field, expected, private_parts in diagnostics:
    for encoding in ('utf-8', 'utf-16le', 'utf-16be', 'base64'):
        payload = (b'var VI_COURT_WASM_BASE64 = "'+base64.b64encode(text.encode())+b'";'
                   if encoding=='base64' else text.encode(encoding))
        findings = law.publication_content(policy, 'diagnostic.bin', payload, [builder])
        assert any(field+'='+json.dumps(expected) in line for line in findings), findings
        assert all(part.lower() not in line.split('; ', 1)[1].lower()
                   for part in private_parts for line in findings), findings
        count += 1
        print('MASKED DIAGNOSTIC HOLDS:', encoding, field+'='+json.dumps(expected))

with tempfile.TemporaryDirectory(prefix='publication-boundary-controls-') as temporary:
    tree = Path(temporary)/'site'; tree.mkdir()
    path = tree/'snapshot.json'; path.write_text(json.dumps({'commits': [{'email': email}]}))
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
    # The actual snapshot transport nests the JSON endpoint body in JSON;
    # HTML carries that same snapshot map. Both must refuse a leaked path.
    for address in (personal, '../../../../../' + 'home/runner/.gate/me/worlds/world/my.swift'):
        snapshot = {'/gitstatus?f=my.swift': json.dumps({'file': address, 'git': 'untracked'})}
        (tree/'snapshots.json').write_text(json.dumps(snapshot))
        (tree/'index.html').write_text('<script>const SNAP = '+json.dumps(snapshot)+';</script>')
        refusal = subprocess.run(command, capture_output=True, text=True)
        assert refusal.returncode == 1, refusal.stdout
        for name in ('index.html','snapshots.json'):
            assert 'site/'+name+':byte ' in refusal.stdout, refusal.stdout
        assert address not in refusal.stdout and str(tree) not in refusal.stdout
        print('REFUSED: private gitstatus snapshot in index.html and snapshots.json ->', refusal.stdout.strip())
        count += 1
    snapshot['/gitstatus?f=my.swift'] = json.dumps({'file': 'my.swift', 'git': 'untracked'})
    (tree/'snapshots.json').write_text(json.dumps(snapshot))
    (tree/'index.html').write_text('<script>const SNAP = '+json.dumps(snapshot)+';</script>')
    assert subprocess.run(command, capture_output=True).returncode == 0
    count += 1
    artifact = Path(temporary)/'product.bin'
    artifact_command = [sys.executable, str(ROOT/'tests/publication-boundary.py'), '--artifact', str(artifact)]
    for account in (*policy['service_builder_accounts'], builder):
        environment = {key:value for key,value in os.environ.items() if key not in ('LOGNAME','LNAME','USERNAME')}
        environment['USER'] = account
        artifact.write_text('no toolchain on the '+account)
        result = subprocess.run(artifact_command, env=environment, capture_output=True, text=True)
        expected = 0 if account in policy['service_builder_accounts'] else 1
        assert result.returncode == expected, (account, result.stdout, result.stderr)
        if expected:assert 'product.bin:byte ' in result.stdout and 'local builder name' in result.stdout
        print('USER CONTROL:', account, 'exit', result.returncode)
        artifact.write_text('/'+'home/'+account+'/file')
        result = subprocess.run(artifact_command, env=environment, capture_output=True, text=True)
        assert result.returncode == 1 and 'absolute home or account-temporary path' in result.stdout, result.stdout
        count += 2
        print('USER HOME REFUSED:', account, '->', result.stdout.strip())
print('PUBLICATION CONTROLS HOLD:', count, 'twins and addressed input controls')
