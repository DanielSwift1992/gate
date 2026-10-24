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

# Mailboxes live in the predeclared complete-text class, never a substring
# carved out of instructions after a regex hit. Paths/names stay byte-wide.
mail = b'person@private-domain.net'
for payload in (mail, b'\0'+mail+b'\0', b'Text: '+mail+b'\n'):
    assert law.publication_content(policy,'text.bin',payload), payload
for payload in (b'\xff'+mail+b'\xfe', b'\x01'+mail+b'\x02'):
    assert not law.publication_content(policy,'instructions.bin',payload), payload
assert law.publication_content(policy,'instructions.bin',b'\xff'+home.encode()+b'\xfe')
assert law.publication_content(policy,'instructions.bin',b'\xff'+builder.encode()+b'\xfe',[builder])
print('EMAIL TEXT CLASS HOLDS: complete text refuses; binary substrings are outside; homes and names remain byte-wide')

# Many declared spans and invalid binary candidates used to multiply one
# another. Each span now meets its candidates once; the final real mailbox
# and path must still refuse at the same bytes, including through UTF-16.
import time
large = b'ordinary text\0' * 131072 + (b'\xffperson@private.mail\x01\0' * 512)
start = time.monotonic()
assert not law.publication_content(policy, 'large.bin', large)
for encoding in ('utf-8', 'utf-16le', 'utf-16be'):
    suffix = b'\0' + (mail.decode() + '\0' + home + '\0').encode(encoding)
    findings = law.publication_content(policy, 'large.bin', large + suffix)
    address = len(large) + 1 + len((mail.decode() + '\0').encode(encoding))
    label = 'large.bin' + ('' if encoding == 'utf-8' else ' [' + encoding.upper() + ']')
    assert any(label + ':byte ' + str(address) + ':' in line and 'absolute home' in line for line in findings), findings
    assert any('email address' in line for line in findings), findings
print('LARGE BYTE CLASS HOLDS:', len(large) + len(suffix), 'bytes;', round(time.monotonic()-start, 3), 'seconds; late path and mailbox retain their addresses')

import copy
sys.path.insert(0,str(ROOT/'bin'))
import publication_origin as origin
raw=b'\x7fELF'+b'owned-build-bytes'
prepared=dict(format=origin.FORMAT,inputs={'source.swift':origin.sha(b'source')},recipe_sha256=origin.sha(b'recipe'),compiler={'version':'fixture','executable_sha256':origin.sha(b'compiler')})
receipt=origin.seal(prepared,raw,['source=/build'],'strip-debug')
assert origin.verify(receipt,raw)
for label,mutate in (
    ('changed delivery',lambda r:r.update(sha256='0'*64)),
    ('missing inputs',lambda r:r.update(inputs={})),
    ('missing strip',lambda r:r.update(debug_metadata='none')),
    ('missing remap',lambda r:r.update(prefix_mappings=[])),
    ('foreign label without identity',lambda r:r['regions'][0].update(origin='swift-toolchain',lexical=False)),
    ('gap in partition',lambda r:r['regions'][0].update(size=len(raw)-1))):
    forged=copy.deepcopy(receipt);mutate(forged)
    try: origin.verify(forged,raw)
    except ValueError: pass
    else: raise AssertionError(label)
print('BUILD RECEIPT CONTROLS HOLD: delivery, inputs, mappings, stripping and complete lexical domain; no foreign-label waiver')

masked=law.publication_content(policy,'mail.txt',('author@prefix'+builder+'suffix.net').encode(),[builder])
assert masked and builder.lower() not in '\n'.join(masked).lower()
print('DOMAIN SAMPLE HOLDS: a private builder substring is redacted without widening the finding class')

for label in (builder+'.bin','author@private.net.bin'):
    messages=law.publication_content(policy,label,mail,[builder])
    assert messages and builder not in '\n'.join(messages) and 'author@' not in '\n'.join(messages)
print('SUBJECT ADDRESS MASK HOLDS: builder and mailbox local part do not leak through filenames')

with tempfile.TemporaryDirectory(prefix='origin-controls-') as tmp:
    tmp=Path(tmp);src=tmp/'inputs';src.mkdir();f=src/'a.swift';f.write_bytes(b'first')
    state=dict(inputs={'a.swift':origin.sha(f.read_bytes())})
    origin.unchanged(state,src)
    f.write_bytes(b'second')
    try:origin.unchanged(state,src)
    except ValueError:pass
    else:raise AssertionError('changed build inputs issued a receipt')
    product=tmp/'product';product.write_bytes(raw)
    sidecar=Path(str(product)+'.origin.json');sidecar.write_bytes(origin.encode(receipt))
    assert not law.delivered_origin(product,'product',raw)
    assert law.delivered_origin(product,'product',raw+b'changed')
    sidecar.unlink()
    assert law.delivered_origin(product,'product',raw)
print('ORIGIN TRANSPORT HOLDS: changed inputs/delivery and missing receipt refuse before lexical reading')

# Identity is a byte relation, not a list of permitted runtime spellings.
import io
import hashlib
import tarfile
from unittest.mock import patch
import publication_identity as identity

def ar_member(name,body):
    header=(name+'/').encode().ljust(16)+b'0'.ljust(12)+b'0'.ljust(6)+b'0'.ljust(6)+b'100644'.ljust(8)+str(len(body)).encode().ljust(10)+b'`\n'
    return header+body+(b'\n' if len(body)%2 else b'')

def refuses(label,call):
    try:call()
    except (origin.Refusal,OSError,ValueError):return
    raise AssertionError('identity accepted '+label)

with tempfile.TemporaryDirectory(prefix='origin-identity-controls-') as temporary:
    cache=Path(temporary);(cache/'objects').mkdir()
    text=(home+' in supplier object').encode();raw=b'\x7fELF\0'+text+b'\0'
    own=b'our remapped object';digest=origin.sha(own);(cache/'objects'/digest).write_bytes(own)
    archive=b'!<arch>\n'+ar_member('runtime.o',b'prefix\0'+text+b'\0end')
    package=cache/'package.tar.gz';path='usr/lib/declared.a'
    def write_package(body=archive, repeated=False):
        with tarfile.open(package,'w:gz') as tar:
            for _ in range(2 if repeated else 1):
                entry=tarfile.TarInfo('toolchain/'+path);entry.size=len(body);tar.addfile(entry,io.BytesIO(body))
    write_package()
    inputs=dict(boundary=identity.BOUNDARY,objects=[digest],package='declared-fixture',archive_hashes={path:origin.sha(archive)})
    authenticate=lambda url,root:(package,dict(source='fixture, not a supplier authentication claim',sha256=origin.sha(package.read_bytes())))
    bounds=[(5,5+len(text)),(6,9)]
    proof=identity.attest(raw,inputs,bounds,cache,authenticate)
    assert len(proof['certificates'])==1 and len(proof['occurrences'])==2
    c=proof['certificates'][0];assert c['offset']==5 and c['size']==len(text) and c['member']=='runtime.o' and c['member_offset']==7
    assert identity.covered(proof,6,9) and not identity.covered(proof,4,9)
    assert identity.attest(raw,inputs,bounds,cache,authenticate,existing=proof)==proof
    for field,value in [('member_offset',8),('ordinal',99),('archive_offset',0),('sha256','0'*64),('size',len(text)-1),('member','other.o')]:
        forged=copy.deepcopy(proof);forged['certificates'][0][field]=value
        refuses('forged identity '+field,lambda:identity.attest(raw,inputs,bounds,cache,authenticate,existing=forged))
    # A requested substring cannot choose shorter identity boundaries.
    unmatched=identity.attest(b'\x7fELF\0changed-prefix '+text+b'\0',inputs,[(20,24)],cache,authenticate)
    assert unmatched['certificates']==[]
    owned_digest=origin.sha(b'longer '+text+b' suffix');(cache/'objects'/owned_digest).write_bytes(b'longer '+text+b' suffix')
    both=dict(inputs,objects=[owned_digest]);assert identity.attest(raw,both,bounds,cache,authenticate)['certificates']==[]
    (cache/'objects'/digest).write_bytes(b'damaged')
    refuses('changed own objects',lambda:identity.attest(raw,inputs,bounds,cache,authenticate))
    (cache/'objects'/digest).write_bytes(own)
    refuses('missing own objects',lambda:identity.attest(raw,dict(inputs,objects=['0'*64]),bounds,cache,authenticate))
    refuses('malformed own digest',lambda:identity.attest(raw,dict(inputs,objects=['../other']),bounds,cache,authenticate))
    refuses('changed supplier archive',lambda:identity.attest(raw,dict(inputs,archive_hashes={path:'0'*64}),bounds,cache,authenticate))
    refuses('missing supplier archive',lambda:identity.attest(raw,dict(inputs,archive_hashes={'missing.a':'0'*64}),bounds,cache,authenticate))
    write_package(repeated=True);refuses('repeated supplier archive',lambda:identity.attest(raw,inputs,bounds,cache,authenticate));write_package()
    second=raw+b'new '+(home+'/unmatched').encode()+b'\0'
    partial=identity.attest(second,inputs,bounds+[(len(raw),len(second)-1)],cache,authenticate)
    assert identity.covered(partial,5,9) and not identity.covered(partial,len(raw),len(second)-1)
    utf=home.encode('utf-16le');assert identity.segment(utf,0,len(utf)) is None
    refuses('undeclared byte boundary',lambda:identity.attest(raw,dict(inputs,boundary='around a match'),bounds,cache,authenticate))
    refuses('truncated ar',lambda:list(identity.members(archive[:-3])))
    # GNU/BSD names and duplicate member spellings retain a physical address.
    names=b'very-long-member-name.o/\n'
    def header_name(name,body):
        return name.encode().ljust(16)+b'0'.ljust(12)+b'0'.ljust(6)+b'0'.ljust(6)+b'100644'.ljust(8)+str(len(body)).encode().ljust(10)+b'`\n'+body+(b'\n' if len(body)%2 else b'')
    gnu=b'!<arch>\n'+header_name('//',names)+header_name('/0',b'abc')
    assert list(identity.members(gnu))[0][0]['member']=='very-long-member-name.o'
    bsd=b'!<arch>\n'+header_name('#1/9',b'long-name'+b'abc')
    assert list(identity.members(bsd))[0][1]==b'abc'
    # Cached packages still need the published checksum and real signature.
    url='https://download.swift.org/swift-0.0-release/ubuntu2404/swift-0.0-RELEASE/swift-0.0-RELEASE-ubuntu24.04.tar.gz'
    folder=cache/'supplier'/origin.sha(url.encode());folder.mkdir(parents=True)
    (folder/'toolchain.tar.gz').write_bytes(b'fixture');(folder/'download.json').write_bytes(origin.encode(dict(url=url,etag='0'*32)))
    with patch.object(identity,'supplier_checksum',return_value=hashlib.md5(b'fixture').hexdigest()):
        refuses('wrong supplier checksum',lambda:identity.authenticated_package(url,cache))
        (folder/'download.json').write_bytes(origin.encode(dict(url=url,etag=hashlib.md5(b'fixture').hexdigest())))
        (folder/'keys').write_bytes(b'not a key');(folder/'signature').write_bytes(b'not a signature')
        with patch.object(identity.subprocess,'run',return_value=subprocess.CompletedProcess([],1,b'',b'')):
            refuses('bad supplier signature',lambda:identity.authenticated_package(url,cache))
        good_status=('[GNUPG:] VALIDSIG '+'0'*40+' invalid-signer\n').encode()
        with patch.object(identity.subprocess,'run',return_value=subprocess.CompletedProcess([],0,good_status,b'')):
            refuses('wrong supplier key',lambda:identity.authenticated_package(url,cache))
    with patch.object(identity,'supplier_checksum',return_value='0'*32):
        refuses('cache invents its own checksum',lambda:identity.authenticated_package(url,cache))
    refuses('arbitrary supplier URL',lambda:identity.authenticated_package('https://example.com/compiler.tar.gz',cache))

# An undeclared supplier blocks certification, not the local compiler.
with tempfile.TemporaryDirectory(prefix='origin-local-build-controls-') as temporary:
    root=Path(temporary);sources=root/'sources';objects=root/'objects';sources.mkdir();objects.mkdir()
    (sources/'main.swift').write_text('print(42)\n');(objects/'0.o').write_bytes(b'our mapped object')
    output_map=sources/'outputs.json';output_map.write_bytes(origin.encode({str((sources/'main.swift').resolve()):dict(object=str((objects/'0.o').resolve()))}))
    prepared_local=dict(inputs={'main.swift':origin.sha((sources/'main.swift').read_bytes()),'outputs.json':origin.sha(output_map.read_bytes())},compiler=dict(version='Swift version 6.4.1',static_archives={},target='x86_64-unknown-linux-gnu'))
    target=origin.encode(dict(paths=dict(runtimeResourcePath=str(root/'toolchain/usr/lib/swift'))))
    original_read_text=Path.read_text
    def host_text(path,*args,**kwargs):
        if str(path)=='/etc/os-release': return 'ID=declared-other-host\nVERSION_ID=1\n'
        return original_read_text(path,*args,**kwargs)
    with patch.object(identity,'CACHE',root/'cache'),patch.object(identity.subprocess,'check_output',return_value=target),patch.object(Path,'read_text',host_text):
        captured=identity.capture(prepared_local,objects,output_map)
    assert 'package' not in captured and captured['objects']==[origin.sha(b'our mapped object')]
    # Supply an archive roster only to reach the missing-provider boundary.
    captured['archive_hashes']={'declared.a':'0'*64}
    refuses('unavailable supplier grants no publication waiver',lambda:identity.attest(b'\0private supplier bytes\0',captured,[(1,8)],root/'cache'))
print('LOCAL BUILD HOLDS: an undeclared supplier gives no identity certificate; local construction still succeeds')

# Structured ranges preserve every diagnostic/address in all former views,
# including multibyte UTF-16 ends; decoded carriers get no physical waiver.
for label,text in cases:
    for raw in (text.encode(),text.encode('utf-16le'),text.encode('utf-16be')):
        events=[];a=law.publication_content(policy,'fixture',raw,[builder],events=events)
        assert a==law.publication_content(policy,'fixture',raw,[builder])
        assert all(0<=start<end<=len(raw) for _,start,end in events),(label,events)
print('ORIGIN IDENTITY HOLDS: maximal runs, archive/member addresses, own-object ambiguity, complete occurrences, checksums and signatures; fixtures are regression observations')
