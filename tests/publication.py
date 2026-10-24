#!/usr/bin/env python3
"""The ordinary publication travels with one binary and one shared read plan."""
from pathlib import Path
import copy
import hashlib
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent.parent


def run():
    with tempfile.TemporaryDirectory(prefix='gate-publication-') as tmp:
        base=Path(tmp); dependency=base/'catalog-source'; dependency.mkdir()
        def atom(name,text):
            return 'public enum '+name+': Close {}\nextension '+name+' { public static var typeName: String { '+json.dumps(text)+' } }\n'
        catalog='public protocol Close {}\n'
        catalog+='public enum Dock: Close {\n    public typealias Id = DoorId\n    public typealias Group = Group\n    public typealias Title = Title\n    public typealias Shown = Shown\n    public typealias Reads = IslandWorld\n    public typealias Caption = Caption\n}\n'
        catalog+='public enum IslandWorld: Close {\n    public typealias File = Directory\n    public typealias Name = WorldName\n}\npublic enum Group: Close {\n    public typealias Name = GroupName\n}\n'
        for n,t in [('DoorId','harbor'),('Title','Coral Atlas'),('Shown','Facts.swift'),('Caption','The declared relations'),('Directory','Island'),('WorldName','Coral'),('GroupName','Atlas')]:catalog+=atom(n,t)
        (dependency/'Doors.swift').write_text(catalog)
        note=b'Owner material at this pin.\r\n'
        (dependency/'Notes.md').write_bytes(note)
        def git(folder,*args):return subprocess.check_output(['git','-C',str(folder),*args],stderr=subprocess.STDOUT,text=True).strip()
        git(dependency,'init','-q');git(dependency,'add','.')
        git(dependency,'-c','user.name=Fixture','-c','user.email=fixture@test','commit','-qm','a pinned catalog')
        revision=git(dependency,'rev-parse','HEAD')
        owner=base/'CoralAtlas';(owner/'Island/.gate').mkdir(parents=True);(owner/'.gate').mkdir()
        root='public protocol Role {}\npublic protocol Close {}\npublic protocol Theirs {}\npublic protocol Publication {}\npublic protocol PublicationAlias {}\npublic enum CatalogFile: Role {}\n'
        root+='public enum AtlasBook: Publication {\n    public typealias Id = BookId\n    public typealias Entry = Dock\n    public typealias Catalog = DoorInput\n    public typealias DraftPolicy = ReadOnly\n    public typealias DrawingProfile = NoDrawing\n    public typealias Aliases = OldDoor\n}\n'
        root+='public enum OldDoor: PublicationAlias {\n    public typealias Path = OldPath\n    public typealias To = Dock\n}\n'
        root+='public enum DoorInput: Theirs {\n    public typealias Kind = CatalogFile\n    public typealias At = CatalogPin\n}\n'
        root+=atom('BookId','org.example.coral')+atom('CatalogPin',str(dependency)+'@'+revision)+atom('DoorInput','.gate/inputs/doors.swift')+atom('OldPath','archive/start')
        # A row's literal belongs to the row itself; atom() also emitted its enum.
        root=root.replace('public enum DoorInput: Close {}\n','')
        (owner/'gate.manifest.swift').write_text(root)
        record=dict(format=2,files=[dict(row='DoorInput',repository=str(dependency),revision=revision,source_path='Doors.swift',path='.gate/inputs/doors.swift',sha256=hashlib.sha256(catalog.encode()).hexdigest())],languages={},plain_fragments=[],shelf_overrides=False)
        root_record=owner/'.gate/forms-definitions.json';root_record.write_text(json.dumps(record,indent=2)+'\n')
        world_manifest='public protocol Role {}\npublic protocol Mine {}\npublic enum FormsFile: Role {}\npublic enum Facts: Mine {\n    public typealias Kind = FormsFile\n}\nextension Facts { public static var typeName: String { "Facts.swift" } }\n'
        world_manifest+='public protocol Theirs {}\npublic enum CarriedFile: Role {}\npublic enum Evidence: Theirs {\n public typealias Kind = CarriedFile\n public typealias At = SourcePin\n}\nextension Evidence { public static var typeName: String { "Evidence.md" } }\npublic enum SourcePin {}\nextension SourcePin { public static var typeName: String { '+json.dumps(str(dependency)+'@'+revision)+' } }\n'
        (owner/'Island/gate.manifest.swift').write_text(world_manifest)
        (owner/'Island/Hidden.txt').write_text('NOT_AN_INPUT')
        (owner/'Island/Hidden.bin').write_bytes(b'BINARY_NOT_AN_INPUT\0')
        facts='public protocol Choice {}\npublic protocol Paired {}\npublic enum Coral: Choice {}\npublic enum Other: Choice {}\npublic enum Pair<L: Choice, R: Choice> {}\nextension Pair: Paired where L == R {}\npublic typealias Same = Pair<Coral, Coral>\n'
        (owner/'Island/Facts.swift').write_text(facts)
        (owner/'Island/.gate/forms-definitions.json').write_text(json.dumps(dict(format=2,files=[dict(row='Evidence',path='Evidence.md',repository=str(dependency),revision=revision,source_path='Notes.md',sha256=hashlib.sha256(note).hexdigest())],languages={},plain_fragments=[],shelf_overrides=False)))
        author_name = 'History "Fixture"'
        author_email = 'private-history-author' + '@' + 'mailbox.net'
        git(owner,'init','-q');git(owner,'add','.');git(owner,'-c','user.name='+author_name,'-c','user.email='+author_email,'commit','-qm','a declared publication')
        expected_commit = dict(zip(('short','when','subject','author'), git(owner,'log','-1','--format=%h%x1f%aI%x1f%s%x1f%an','--abbrev=8').split('\x1f')))
        local_email = 'private-publisher' + '@' + 'mailbox.net'
        git(owner,'config','user.email',local_email)
        installed=base/'installation/bin';installed.mkdir(parents=True)
        binary=installed/'gate-cli';shutil.copy2(ROOT/'bin/gate-cli',binary)
        # The child has no Python, Node, Swift or neighbouring gate source files.
        tools=base/'tools';tools.mkdir();(tools/'git').symlink_to(shutil.which('git'))
        env={k:v for k,v in os.environ.items() if not k.startswith('GATE_') and k not in ('PLAYGROUND_SOURCE','SHOWCASE_SOURCE','VI_THEORY_PATH')}
        env['PATH']=str(tools)
        site=base/'site'
        def publish(destination=site,repository=owner):
            return subprocess.run([str(binary),'publish',str(repository),'-o',str(destination),'--json'],cwd=base,env=env,capture_output=True,text=True,timeout=90)
        answer=publish();assert answer.returncode==0,(answer.stdout,answer.stderr)
        plan=json.loads((site/'read-plan.json').read_text())
        journal=json.loads(json.loads((site/'snapshots/harbor.json').read_text())['responses']['GET /log']['body'])
        assert 'me' not in journal, 'publication must not include local Git identity'
        assert journal['commits']==[expected_commit], journal
        assert journal['next']=='Publish a new snapshot from the source repository to update this history.', journal
        for path in site.rglob('*'):
            if path.is_file():
                assert local_email.encode() not in path.read_bytes(), path
                assert author_email.encode() not in path.read_bytes(), path
        # The projection changes the delivered reading, not Git's objects or
        # the ordinary local journal's identity semantics.
        local_log=json.loads(subprocess.check_output([str(binary),'log','--json'],cwd=owner,env=env))
        assert local_log['me']==local_email and local_log['commits'][0]['email']==author_email
        assert git(owner,'log','-1','--format=%ae')==author_email
        print('PUBLICATION HISTORY HOLDS: four Git fields retained; local and author emails absent; repository history intact')
        assert plan['format']=='publication/1' and plan['drawing_profile']=='NoDrawing' and plan['draft_policy']=='ReadOnly'
        assert plan['coverage'][0]['verdict']=='holds' and plan['coverage'][0]['forms']['equalities']==1,plan['coverage']
        assert (site/'index.html').exists() and (site/'harbor/index.html').exists() and (site/'archive/start/index.html').exists()
        assert (site/'assets/vi_court_bytes.js').stat().st_size>1000000
        for path,hash in plan['resources'].items():assert hashlib.sha256((site/path).read_bytes()).hexdigest()==hash,path
        assert any((site/path).read_bytes()==catalog.encode() for path in plan['resources'] if path.startswith('inputs/'))
        # Source relocation and output paths do not change the semantic plan.
        moved=base/'Relocated';shutil.copytree(owner,moved)
        second=base/'second';r=publish(second,moved);assert r.returncode==0,r.stderr
        assert json.loads((second/'read-plan.json').read_text())==plan
        sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
        process=subprocess.Popen([str(binary),'serve',str(owner),str(port),'--no-open'],cwd=base,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        origin='http://127.0.0.1:'+str(port)
        def get(path):return urllib.request.urlopen(origin+path,timeout=30).read()
        try:
            for _ in range(150):
                try:live=json.loads(get('/read-plan.json'));break
                except OSError:time.sleep(.1)
            else:raise AssertionError('cold serve did not open')
            assert live==plan
            snapshot=json.loads((site/'snapshots/harbor.json').read_text())
            assert json.loads(get('/snapshots/harbor.json'))==snapshot
            for key,item in snapshot['responses'].items():
                if key.startswith('GET '):
                    assert get(key[4:])==item['body'].encode(),key
            for f in ('Facts.swift','gate.manifest.swift'):
                text=snapshot['responses']['GET /world?f='+f]['body']
                req=urllib.request.Request(origin+'/verdict?f='+f,data=text.encode(),method='POST')
                assert urllib.request.urlopen(req).read()==snapshot['responses']['POST /verdict?f='+f]['body'].encode()
            listed=json.loads(get('/files'))
            assert set(listed['files'])=={'Facts.swift','Evidence.md','gate.manifest.swift'}
            assert listed['theirs']['Evidence.md']['sha256']==hashlib.sha256(note).hexdigest()
            assert get('/world?f=Evidence.md')==note
            for hidden in ('Hidden.txt','Hidden.bin'):
                try:get('/world?f='+hidden);raise AssertionError('undeclared input exposed')
                except urllib.error.HTTPError as e:assert e.code==404
            assert get('/assets/vi_court_bytes.js')==(site/'assets/vi_court_bytes.js').read_bytes()
            req=urllib.request.Request(origin+'/world?f=gate.manifest.swift',data=b'changed',method='PUT')
            try:urllib.request.urlopen(req);raise AssertionError('structural write accepted')
            except urllib.error.HTTPError as e:assert e.code==409
            # Losing a required input invalidates the live plan and its verdict.
            (owner/'Island/Facts.swift').unlink()
            try:get('/status');raise AssertionError('missing input retained holds')
            except urllib.error.HTTPError as e:assert json.loads(e.read())['verdict']=='refused'
            (owner/'Island/Facts.swift').write_text(facts)
        finally:
            process.terminate();process.wait()
        before={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
        # Every refusal leaves the previous output intact.
        def refused(label,change,undo,status='refused'):
            change()
            try:
                r=publish();assert r.returncode!=0,(label,r.stdout)
                assert json.loads(r.stderr)['status']==status,(label,r.stderr)
                if label.startswith('reserved fragments'):
                    failure=json.loads(r.stderr)
                    assert '.gate/forms-definitions.json:' in failure['address'],failure
                    assert 'split the file into data and page' in failure['reason'],failure
                after={str(p.relative_to(site)):hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
                assert after==before,label
            finally:undo()
        manifest=owner/'gate.manifest.swift'
        refused('no Publication',lambda:manifest.write_text(root.replace(': Publication {',': Close {',1)),lambda:manifest.write_text(root))
        refused('missing input',lambda:(owner/'Island/Facts.swift').unlink(),lambda:(owner/'Island/Facts.swift').write_text(facts))
        refused('unknown publication field',lambda:manifest.write_text(root.replace('typealias Entry = Dock','typealias Unexpected = Dock\n    public typealias Entry = Dock')),lambda:manifest.write_text(root))
        refused('unknown draft policy',lambda:manifest.write_text(root.replace('DraftPolicy = ReadOnly','DraftPolicy = Unpromised')),lambda:manifest.write_text(root),'unsupported')
        refused('profile is not delivered here',lambda:manifest.write_text(root.replace('DrawingProfile = NoDrawing','DrawingProfile = AProfile')),lambda:manifest.write_text(root),'unsupported')
        refused('context operation',lambda:(owner/'Island/Facts.swift').write_text('import FourthModule\n'+facts),lambda:(owner/'Island/Facts.swift').write_text(facts),'unsupported')
        # An explicit Language request is never erased to get a green subset.
        world_record=owner/'Island/.gate/forms-definitions.json';saved_record=world_record.read_text()
        for target in (root_record,world_record):
            saved=target.read_text(); malformed=json.loads(saved)
            malformed['plain_fragments']=[dict(path='Facts.swift',marker='// data follows')]
            refused('reserved fragments '+str(target.relative_to(owner)),
                    lambda:target.write_text(json.dumps(malformed,indent=2)),lambda:target.write_text(saved))
        with_context=json.loads(saved_record);with_context['languages']={'Local':{'definitions':[],'namespace':'Local','imports':[]}}
        refused('declared context',lambda:world_record.write_text(json.dumps(with_context)),lambda:world_record.write_text(saved_record),'unsupported')
        refused('implicit count input',lambda:(owner/'Island/Facts.swift').write_text((ROOT/'stdlib/bench-metrics.swift').read_text()),lambda:(owner/'Island/Facts.swift').write_text(facts),'unsupported')
        # A supported negative relation remains readable as a refusal.
        (owner/'Island/Facts.swift').write_text(facts.replace('Pair<Coral, Coral>','Pair<Coral, Other>'))
        red=base/'red';r=publish(red);assert r.returncode==0,r.stderr
        assert json.loads((red/'read-plan.json').read_text())['coverage'][0]['verdict']=='refused'
        (owner/'Island/Facts.swift').write_text(facts)
        missing= subprocess.run([str(binary),'publish','-o',str(base/'not-a-demo')],cwd=base,env=env,capture_output=True,text=True)
        assert missing.returncode!=0 and not (base/'not-a-demo').exists()
        # Test the actual static browser transport with Node as a test tool.
        subprocess.run(['node',str(ROOT/'tests/publication.js'),str(site)],check=True)
        # DraftPolicy is the owner's permission, shared by the live and static
        # browser carriers. It does not permit a native disk write.
        manifest.write_text(root.replace('DraftPolicy = ReadOnly','DraftPolicy = ReaderDraft'))
        (owner/'Island/Notes.swift').write_text('// another owned input\n')
        (owner/'Island/gate.manifest.swift').write_text(world_manifest+'public enum Notes: Mine {\n    public typealias Kind = FormsFile\n}\nextension Notes { public static var typeName: String { "Notes.swift" } }\n')
        drafts=base/'reader-drafts';r=publish(drafts);assert r.returncode==0,r.stderr
        draft_plan=json.loads((drafts/'read-plan.json').read_text())
        assert draft_plan['draft_policy']=='ReaderDraft'
        draft_files=json.loads(json.loads((drafts/'snapshots/harbor.json').read_text())['responses']['GET /files']['body'])
        assert draft_files['capabilities']['write']==['Facts.swift','Notes.swift'],draft_files
        republished=base/'republished-drafts'
        (owner/'Island/Facts.swift').write_text(facts+'// a new owner snapshot\n')
        r=publish(republished);assert r.returncode==0,r.stderr
        (owner/'Island/Facts.swift').write_text(facts)
        process=subprocess.Popen([str(binary),'serve',str(owner),str(port),'--no-open'],cwd=base,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(150):
                try:live=json.loads(get('/read-plan.json'));break
                except OSError:time.sleep(.1)
            else:raise AssertionError('ReaderDraft serve did not open')
            assert live==draft_plan
            assert b'data-draft-policy="ReaderDraft"' in get('/')
            req=urllib.request.Request(origin+'/world?f=Facts.swift',data=b'changed',method='PUT')
            try:urllib.request.urlopen(req);raise AssertionError('browser policy granted disk write')
            except urllib.error.HTTPError as e:assert e.code==409
            assert (owner/'Island/Facts.swift').read_text()==facts
            subprocess.run(['node',str(ROOT/'tests/publication.js'),str(drafts),'holds','Facts.swift',str(republished)],check=True)
        finally:
            process.terminate();process.wait();manifest.write_text(root)
        print('PUBLICATION ALL GREEN: cold binary, declared ReadOnly/ReaderDraft, red browser drafts and atomic refusal')


if __name__=='__main__':run()
