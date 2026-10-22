#!/usr/bin/env python3
"""A foreign publication carries its owner's profile without a runtime tool."""
from pathlib import Path
import copy
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest()


def owner_repository(spec, local=None):
    if local:
        source=Path(local).resolve()
        head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        if head!=spec['revision']:
            raise ValueError(str(source)+': local owner source is not at the publication pin')
        return str(source)
    return 'https://github.com/DanielSwift1992/verification-is-identification-showcase'


def run(source):
    source=Path(source)
    request=json.loads((source/'Profiles/Playground/request.json').read_text())
    with tempfile.TemporaryDirectory(prefix='gate-owner-profile-') as tmp:
        base=Path(tmp);dep=base/'declared-input';dep.mkdir();owner=base/'HarborAtlas';(owner/'Island/.gate').mkdir(parents=True);(owner/'.gate').mkdir()
        # These are native owner readings of today's inputs, not frozen copies.
        # Swift/Python belong to this build-time control; the consumer below has
        # only git in PATH, exactly as an autonomous installation does.
        variants=base/'variants'
        host_env={k:v for k,v in os.environ.items() if not k.startswith('GATE_') and k not in ('PLAYGROUND_SOURCE','SHOWCASE_SOURCE','VI_THEORY_PATH','NODE_USE_SYSTEM_CA')}
        if shutil.disk_usage(source).free<5*1024**3:raise RuntimeError('owner profile control: less than 5 GiB free before the Swift build')
        subprocess.run([sys.executable,str(source/'Checks/profile-inputs.py'),'--export',str(variants)],cwd=source,env=host_env,check=True,timeout=600)
        def git(folder,*args):return subprocess.check_output(['git','-C',str(folder),*args],stderr=subprocess.STDOUT,text=True).strip()
        git(dep,'init','-q');git(owner,'init','-q')
        atom=lambda n,t:'public enum '+n+': Close {}\nextension '+n+' { public static var typeName: String { '+json.dumps(t)+' } }\n'
        catalog='public protocol Close {}\npublic enum Dock: Close {\n public typealias Id = DoorId\n public typealias Group = Group\n public typealias Title = Title\n public typealias Shown = Shown\n public typealias Reads = Island\n public typealias Caption = Caption\n}\npublic enum Group: Close {\n public typealias Name = GroupName\n}\npublic enum Island: Close {\n public typealias File = Directory\n public typealias Name = WorldName\n}\n'
        for n,t in [('DoorId','harbor'),('Title','Harbor chart'),('Shown','Facts.swift'),('Caption','The declared relation'),('Directory','Island'),('WorldName','Chart'),('GroupName','Atlas')]:catalog+=atom(n,t)
        facts='public protocol Choice {}\npublic protocol Paired {}\npublic enum Coral: Choice {}\npublic enum Pair<L: Choice, R: Choice> {}\nextension Pair: Paired where L == R {}\npublic typealias Same = Pair<Coral, Coral>\n'
        (owner/'Island/Facts.swift').write_text(facts)
        (owner/'Island/gate.manifest.swift').write_text('public protocol Role {}\npublic protocol Mine {}\npublic enum FormsFile: Role {}\npublic enum Facts: Mine {\n public typealias Kind = FormsFile\n}\nextension Facts { public static var typeName: String { "Facts.swift" } }\n')
        (owner/'Island/.gate/forms-definitions.json').write_text(json.dumps(dict(format=2,files=[],languages={},plain_fragments=[])))
        install=base/'installation';install.mkdir();binary=install/'gate';shutil.copy2(ROOT/'bin/gate-cli',binary)
        tools=base/'tools';tools.mkdir();(tools/'git').symlink_to(shutil.which('git'))
        env={k:v for k,v in os.environ.items() if not k.startswith('GATE_') and k not in ('PLAYGROUND_SOURCE','SHOWCASE_SOURCE','VI_THEORY_PATH','NODE_USE_SYSTEM_CA')};env['PATH']=str(tools)
        default={row:(source/path).read_bytes() for row,path in request['inputs'].items()}
        default['TheDrawing']=(source/'Profiles/Playground/receipt.json').read_bytes()
        default['TheDrawingCSS']=(source/'Profiles/Playground/drawing.css').read_bytes()
        default['DoorInput']=catalog.encode()
        site=base/'site'
        payload=None
        def commit(values, mine=False):
            nonlocal payload
            payload=copy.deepcopy(values)
            for p in dep.iterdir():
                if p.is_file():p.unlink()
            names={n:n+('.ttf' if n=='TheFont' else '.bin') for n in values}
            for n,b in values.items():(dep/names[n]).write_bytes(b)
            git(dep,'add','.');git(dep,'-c','user.name=Fixture','-c','user.email=fixture@test','commit','--allow-empty','-qm','the declared profile input')
            rev=git(dep,'rev-parse','HEAD')
            text='public protocol Role {}\npublic protocol Close {}\npublic protocol Theirs {}\npublic protocol Mine {}\npublic protocol Publication {}\npublic enum CarriedFile: Role {}\npublic enum CatalogFile: Role {}\npublic enum FormsFile: Role {}\npublic enum DrawingProfileFile: Role {\n public typealias Reader = DrawingProfileReaderV1\n}\npublic enum DrawingProfileReaderV1: Role {}\n'
            text+='public enum Book: Publication {\n public typealias Id = BookId\n public typealias Entry = Dock\n public typealias Catalog = DoorInput\n public typealias DraftPolicy = ReadOnly\n public typealias DrawingProfile = TheDrawing\n public typealias Aliases = ()\n}\n'+atom('BookId','HarborAtlas')+atom('InputPin',str(dep)+'@'+rev)
            entries=[]
            for name in values:
                is_mine=mine and name=='ThePalette'
                kind='CatalogFile' if name=='DoorInput' else 'DrawingProfileFile' if name=='TheDrawing' else 'FormsFile' if is_mine else 'CarriedFile'
                path='Palette.swift' if is_mine else 'Taken/'+names[name]
                text+='public enum '+name+(': Mine' if is_mine else ': Theirs')+' {\n public typealias Kind = '+kind+'\n'+('' if is_mine else ' public typealias At = InputPin\n')+'}\nextension '+name+' { public static var typeName: String { '+json.dumps(path)+' } }\n'
                if is_mine:(owner/path).write_bytes(values[name])
                else:entries.append(dict(row=name,path=path,repository=str(dep),revision=rev,source_path=names[name],sha256=sha(values[name])))
            if mine:
                # The live world has no Publication read-only policy.
                text=re.sub(r'public enum Book: Publication \{.*?\n\}\n','',text,flags=re.S)
            (owner/'gate.manifest.swift').write_text(text)
            (owner/'.gate/forms-definitions.json').write_text(json.dumps(dict(format=2,files=entries,languages={},plain_fragments=[])))
        def publish():return subprocess.run([str(binary),'publish',str(owner),'-o',str(site),'--json'],cwd=base,env=env,capture_output=True,text=True,timeout=90)
        def served(action):
            sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
            p=subprocess.Popen([str(binary),'serve',str(owner),str(port),'--no-open'],cwd=base,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            origin='http://127.0.0.1:'+str(port)
            try:
                for _ in range(150):
                    try:urllib.request.urlopen(origin+'/drawing-profile',timeout=2).read();break
                    except OSError:time.sleep(.1)
                else:raise AssertionError('autonomous serve did not open')
                return action(origin)
            finally:p.terminate();p.wait(timeout=10)
        def profile(origin):return json.loads(urllib.request.urlopen(origin+'/drawing-profile',timeout=30).read())
        commit(default);answer=publish();assert answer.returncode==0,(answer.stdout,answer.stderr)
        plan=json.loads((site/'read-plan.json').read_text());snapshot=json.loads((site/'snapshots/harbor.json').read_text())
        resolved=json.loads(snapshot['responses']['GET /drawing-profile']['body'])
        assert plan['drawing_profile']=='TheDrawing' and resolved['status']=='resolved'
        assert resolved['resolved']['origin']=='owner' and resolved['resolved']['contract_pin']['sha256']==json.loads((ROOT/'bin/drawing-contract.from').read_text())['sha256']
        assert resolved['resolved']['case_count']==22 and len(resolved['resolved']['witnesses'])==17
        assert served(profile)==resolved,'serve and publish must carry the same profile plan'
        for name in ['TheFont','TheLicense','TheDrawingCSS']:
            assert sum(p.read_bytes()==default[name] for p in site.rglob('*') if p.is_file())==1,name+' duplicated'
        for p in [site/'index.html',site/'harbor/index.html']:
            assert len(re.findall('data-drawing-profile href=',p.read_text()))==1
            assert len(re.findall('data-replies=',p.read_text()))==1,'the actual bench must load its transport'
        stable={str(p.relative_to(site)):sha(p.read_bytes()) for p in site.rglob('*') if p.is_file()}
        spec=json.loads((owner/'.gate/forms-definitions.json').read_text());font_entry=next(f for f in spec['files'] if f['row']=='TheFont')
        cache=base/'bin/.inputs'/sha(str(dep).encode())/font_entry['revision']/(sha(font_entry['source_path'].encode())+'-'+font_entry['sha256'])
        original_cache=cache.read_bytes()
        try:
            cache.write_bytes(b'different cached font');r=publish();assert r.returncode!=0 and 'cached input bytes' in r.stderr,(r.returncode,r.stdout,r.stderr)
        finally:cache.write_bytes(original_cache)
        font_entry['source_path']='missing-font.ttf';(owner/'.gate/forms-definitions.json').write_text(json.dumps(spec))
        try:
            r=publish();assert r.returncode!=0 and ('source_path' in r.stderr or 'Git source bytes' in r.stderr),(r.stdout,r.stderr)
        finally:
            font_entry['source_path']='TheFont.ttf';(owner/'.gate/forms-definitions.json').write_text(json.dumps(spec))
        def refused(label,values,status='refused'):
            commit(values);r=publish();assert r.returncode!=0,(label,r.stdout,r.stderr)
            error=json.loads(r.stderr);assert error['status']==status and error['address'],(label,error)
            assert stable=={str(p.relative_to(site)):sha(p.read_bytes()) for p in site.rglob('*') if p.is_file()},label+' replaced the old site'
        values=copy.deepcopy(default);values['TheBindings']+=b'\n// different input\n';refused('stale bindings',values)
        values=copy.deepcopy(default);values['TheDrawingCSS']+=b'\n';refused('wrong CSS hash',values)
        values=copy.deepcopy(default);values['TheDrawing']=b'{';refused('damaged owner receipt',values)
        values=copy.deepcopy(default);values['TheLicense']=b'';refused('lost license',values)
        values=copy.deepcopy(default);values['TheFont']=b'changed';refused('font bytes',values)
        def rebind(values):
            r=json.loads(values['TheDrawing'])
            for name in r['inputs']:r['inputs'][name]['sha256']=sha(values[name])
            values['TheDrawing']=json.dumps(r).encode();return r
        values=copy.deepcopy(default);values['TheContract']=values['TheContract'].replace(b'<svg',b'<svg ',1);rebind(values);refused('wrong contract output',values)
        values=copy.deepcopy(default);values['TheProfileSource']=values['TheProfileSource'].replace(b'Contract = TheContract',b'Contract = MissingInput');rebind(values);refused('missing contract row',values)
        for field in ['Unexpected','Reader']:
            values=copy.deepcopy(default);values['TheProfileSource']=values['TheProfileSource'].replace(b'public typealias Reader = Port',b'public typealias Reader = Port\n    public typealias '+field.encode()+b' = Port',1);rebind(values);refused('unknown/repeated metadata field '+field,values)
        values=copy.deepcopy(default);values['TheBindings']=values['TheBindings'].replace(b'Foreground = BindTextLight',b'Foreground = BindMutedLight',1);refused('stale Legible endpoint',values)
        values=copy.deepcopy(default);font_hash=sha(values['TheFont']);values['TheProfileSource']=values['TheProfileSource'].replace(font_hash.encode(),b'0'*64);rebind(values);refused('false SourceFontSHA256',values)
        values=copy.deepcopy(default);values['TheProfileSource']=values['TheProfileSource'].replace(b'"default"',b'"different-face"');r=rebind(values);r['result']['font']['face']='different-face';values['TheDrawing']=json.dumps(r).encode();refused('unknown face',values,'unsupported')
        values=copy.deepcopy(default);values['TheFont']+=b'different-font';new_hash=sha(values['TheFont']);values['TheProfileSource']=values['TheProfileSource'].replace(font_hash.encode(),new_hash.encode());values['TheDrawingCSS']=values['TheDrawingCSS'].replace(font_hash.encode(),new_hash.encode());r=rebind(values);r['css']['sha256']=sha(values['TheDrawingCSS']);r['result']['font']['sha256']=new_hash
        for item in r['result']['assets']:
            if item['name']=='font.ttf':item['sha256']=new_hash
        values['TheDrawing']=json.dumps(r).encode();refused('intact unknown font',values,'unsupported')
        values=copy.deepcopy(default);r=json.loads(values['TheDrawing']);r['inputs'].pop('TheBindings');values['TheDrawing']=json.dumps(r).encode();refused('missing bound input',values)
        values=copy.deepcopy(default);r=json.loads(values['TheDrawing']);r['result']['bindings']=[b for b in r['result']['bindings'] if not(b['theme']=='dark' and b['role']=='text-primary')];values['TheDrawing']=json.dumps(r).encode();refused('missing dark role',values)
        values=copy.deepcopy(default);values['TheMetrics']=values['TheMetrics'].replace(b'"2048"',b'"2049"');r=json.loads(values['TheDrawing']);r['inputs']['TheMetrics']['sha256']=sha(values['TheMetrics']);r['result']['font']['metrics_sha256']=sha(values['TheMetrics']);r['result']['font']['units']=2049;values['TheDrawing']=json.dumps(r).encode();refused('intact unknown metrics',values,'unsupported')
        for name in ['renamed','other-palette']:
            variant=variants/name;values=copy.deepcopy(default);receipt=json.loads((variant/'receipt.json').read_text())
            for row,entry in receipt['inputs'].items():
                p=variant/Path(entry['path']).name
                if p.exists():values[row]=p.read_bytes()
            values={k:v for k,v in values.items() if k in set(receipt['inputs'])|{'DoorInput','TheDrawing','TheDrawingCSS'}}
            values['TheDrawing']=(variant/'receipt.json').read_bytes();values['TheDrawingCSS']=(variant/'drawing.css').read_bytes()
            commit(values);r=publish();assert r.returncode==0,(name,r.stdout,r.stderr)
            snap=json.loads((site/'snapshots/harbor.json').read_text());other=json.loads(snap['responses']['GET /drawing-profile']['body'])
            assert other['resolved']['origin']=='owner' and served(profile)==other
            assert (other['css_sha256']==resolved['css_sha256'])==(name=='renamed')
        # A new, well-delivered candidate does not inherit acceptance by shape.
        values=copy.deepcopy(default);contract=json.loads(values['TheContract']);contract['candidate']='unaccepted';values['TheContract']=json.dumps(contract).encode()
        r=json.loads(values['TheDrawing']);r['inputs']['TheContract']['sha256']=sha(values['TheContract']);values['TheDrawing']=json.dumps(r).encode()
        commit(values);r=publish();assert r.returncode==0,r.stderr
        value=json.loads(json.loads((site/'snapshots/harbor.json').read_text())['responses']['GET /drawing-profile']['body'])['resolved']
        assert value['status']=='not-compared' and value['contract_pin'] is None and value['case_count']==0 and value['reason'] and re.fullmatch('[a-f0-9]{64}',value['inputSHA256'])
        def normalized(value):
            env_node=dict(os.environ);env_node.pop('NODE_USE_SYSTEM_CA',None)
            script="const p=require('./bin/drawing-profile.js');let s='';process.stdin.on('data',b=>s+=b);process.stdin.on('end',async()=>console.log(JSON.stringify(await p.compare(JSON.parse(s),[{file:'Facts.swift',text:"+json.dumps(facts)+"}],{canvases:[],refusals:[]}))));"
            answer=subprocess.run(['node','-e',script],input=json.dumps(value),capture_output=True,text=True,cwd=ROOT,env=env_node,check=True)
            c=json.loads(answer.stdout);assert c['status']=='not-compared' and c['contract_pin'] is None and c['case_count']==0 and c['reason'] and re.fullmatch('[a-f0-9]{64}',c['inputs_digest'])
        normalized(value)
        values=copy.deepcopy(default);values.pop('TheContract');values['TheProfileSource']=values['TheProfileSource'].replace(b'Contract = TheContract',b'Contract = NoContract')+b'\npublic enum NoContract: Word {}\nextension NoContract { public static var typeName: String { "" } }\n'
        r=json.loads(values['TheDrawing']);r['inputs'].pop('TheContract');r['inputs']['TheProfileSource']['sha256']=sha(values['TheProfileSource']);r['contract_row']=None;r['result']['contract']=None;values['TheDrawing']=json.dumps(r).encode()
        commit(values);answer=publish();assert answer.returncode==0,answer.stderr
        value=json.loads(json.loads((site/'snapshots/harbor.json').read_text())['responses']['GET /drawing-profile']['body'])['resolved'];normalized(value)
        # Only a MINE palette in a live world can request the existing JS port.
        commit(default,mine=True)
        def live(origin):
            original=profile(origin);assert original['status']=='resolved' and original['port_allowed']
            changed=default['ThePalette'].decode()
            for channel in ['Red','Green','Blue']:changed=re.sub(r'^public typealias SurfaceTrackLit'+channel+r' = .+$','public typealias SurfaceTrackLit'+channel+' = U1',changed,flags=re.M)
            request=urllib.request.Request(origin+'/drawing-profile',data=json.dumps(dict(path='Palette.swift',text=changed)).encode(),headers={'Content-Type':'application/json'})
            value=json.loads(urllib.request.urlopen(request,timeout=30).read());assert value['status']=='declared' and value['origin']=='port' and value['owner_receipt']['status']=='stale'
            host_env=dict(os.environ);host_env.pop('NODE_USE_SYSTEM_CA',None)
            port=subprocess.run(['node',str(ROOT/'bin/drawing-profile.js'),origin],input=json.dumps(value),capture_output=True,text=True,env=host_env,timeout=60)
            assert port.returncode==0,port.stderr
            compiled=json.loads(port.stdout);assert compiled['origin']=='port' and compiled['owner_receipt']['status']=='stale'
            owner_css=(variants/'other-palette/drawing.css').read_text()
            roles=lambda css:re.findall(r'--vi-([a-z-]+)\s*:\s*([^;{}]+)',css)
            assert roles(compiled['css'])==roles(owner_css),'the live port colours differ from the genuine owner A4 reading'
            assert (owner/'Palette.swift').read_bytes()==default['ThePalette'],'unsaved reading wrote the source'
            manifest=owner/'gate.manifest.swift';text=manifest.read_text();manifest.write_text(text.replace('Kind = DrawingProfileFile','Kind = CarriedFile'))
            try:assert profile(origin)['status']=='none'
            finally:manifest.write_text(text)
        served(live)
        host_env=dict(os.environ);host_env.pop('NODE_USE_SYSTEM_CA',None)
        subprocess.run(['node',str(ROOT/'tests/owner-profile-ui.js')],env=host_env,check=True)
    print('OWNER PROFILE GREEN: autonomous A1, exact input set, shared resources, N4, A3/A4, unaccepted contract and labelled live MINE port')


if __name__=='__main__':
    if len(sys.argv)>1:run(Path(sys.argv[1]).resolve())
    else:
        # Only the control needs the owner's build tools. Do not add its SwiftPM
        # build inputs to the worlds shipped to every published bench.
        spec=json.loads((ROOT/'bin/playground-worlds.from').read_text())['showcase']
        # Use the same explicit local-source option as the worlds door during
        # a cross-repository review. It still supplies a committed pin: fetch a
        # clean snapshot, never copy the caller's build or uncommitted files.
        repository=owner_repository(spec,os.environ.get('SHOWCASE_SOURCE'))
        with tempfile.TemporaryDirectory(prefix='gate-profile-owner-reader-') as tmp:
            source=Path(tmp)
            def git(*args):subprocess.run(['git','-C',str(source),*args],check=True)
            git('init','-q');git('config','core.autocrlf','false');git('config','core.eol','lf')
            git('fetch','-q','--depth','1',repository,spec['revision'])
            git('checkout','-q','FETCH_HEAD')
            for name,want in spec['files'].items():assert sha((source/name).read_bytes())==want,name+': owner input differs from the publication pin'
            assert owner_repository(spec,source)==str(source.resolve())
            try:owner_repository(dict(revision='0'*40),source)
            except ValueError:pass
            else:raise AssertionError('a local owner source at another revision was accepted')
            run(source)
