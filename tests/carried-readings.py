#!/usr/bin/env python3
"""Declared taken bytes: real HTTP, cold pins, and attempted writes."""
from pathlib import Path
import copy,hashlib,json,os,socket,subprocess,tempfile,time,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
 with tempfile.TemporaryDirectory(prefix='gate-carried-reading-') as tmp:
  base=Path(tmp);owner=base/'owner';world=base/'world';owner.mkdir();(world/'.gate').mkdir(parents=True)
  samples={'source.md':b'# Read <this> "source"\r\n\r\n'+ 'Где закон? 🧭'.encode(), 'facts.json':b'{"value": "actual bytes"}\n', 'without-extension':b'Plain\ttext\n', 'empty':b'', 'bad-utf8':b'\xff\xfehello', 'asset':b'font\0binary', 'control':b'a\x01b', 'Forms.swift':b'public protocol Mark {}\npublic enum Stamp: Mark {}\n'}
  for name,body in samples.items():(owner/name).write_bytes(body)
  def git(*args):return subprocess.check_output(['git','-C',str(owner),*args],text=True).strip()
  git('init','-q');git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@test','commit','-qm','pinned readings');pin=git('rev-parse','HEAD')
  source='public protocol Role {}\npublic protocol Mine {}\npublic protocol Theirs {}\npublic protocol Close {}\npublic enum FormsFile: Role {}\npublic enum CarriedFile: Role {}\npublic enum Facts: Mine {\n public typealias Kind = FormsFile\n}\nextension Facts { public static var typeName: String { "Facts.swift" } }\n'
  source+='public enum Owner: Close {}\nextension Owner { public static var typeName: String { '+json.dumps(str(owner)+'@'+pin)+' } }\n'
  entries=[]
  for i,(name,body) in enumerate(samples.items()):
   row='Taken'+str(i);path='materials/'+name;kind='FormsFile' if name=='Forms.swift' else 'CarriedFile'
   source+='public enum '+row+': Theirs {\n public typealias Kind = '+kind+'\n public typealias At = Owner\n}\nextension '+row+' { public static var typeName: String { '+json.dumps(path)+' } }\n'
   entries.append(dict(row=row,path=path,repository=str(owner),revision=pin,source_path=name,sha256=sha(body)))
  record=dict(format=2,files=entries,languages={},plain_fragments=[],shelf_overrides=False)
  manifest=world/'gate.manifest.swift';manifest.write_text(source)
  descriptor=world/'.gate/forms-definitions.json';descriptor.write_text(json.dumps(record,indent=2))
  (world/'Facts.swift').write_text('public protocol Ground {}\npublic enum Fact: Ground {}\n')
  (world/'materials').mkdir();(world/'materials/source.md').write_text('FORGED local mirror')
  (world/'secret.txt').write_text('UNDECLARED_SECRET')
  sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
  process=subprocess.Popen([str(ROOT/'bin/gate-cli'),'serve',str(world),str(port),'--no-open'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  def ask(path,method='GET',body=None):
   request=urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=body,method=method)
   try:
    with urllib.request.urlopen(request,timeout=90) as response:return response.status,response.read()
   except urllib.error.HTTPError as e:return e.code,e.read()
  try:
   for _ in range(100):
    try:
     with socket.create_connection(('127.0.0.1',port),timeout=1):pass
     break
    except OSError:time.sleep(.05)
   else:raise AssertionError('server did not start')
   status,body=ask('/files');assert status==200;files=json.loads(body)
   for entry in entries:
    name=entry['path'];binary=entry['source_path'] in ('bad-utf8','asset','control')
    assert (name in files['files']) != binary,(name,files)
    if binary:
     code,body=ask('/world?f='+name);assert code==409 and 'unsupported text reading' in body.decode();continue
    assert files['theirs'][name]['verified'] and all(files['theirs'][name][k]==v for k,v in entry.items())
    assert files['theirs'][name]['record_address'].startswith('.gate/forms-definitions.json:')
    code,body=ask('/world?f='+name);assert code==200 and body==samples[entry['source_path']],name
    code,body=ask('/world?f='+name,'PUT',b'forged edit');assert code==409 and 'read-only' in body.decode()
    assert ask('/world?f='+name)[1]==samples[entry['source_path']]
    assert ask('/verdict?f='+name,'POST',b'forged edited reading')[0]==409
   batch=json.loads(ask('/world','POST',json.dumps([e['path'] for e in entries]+['secret.txt']).encode())[1])
   for entry in entries:
    item=batch[entry['path']]
    if entry['source_path'] in ('bad-utf8','asset','control'):
     assert item['status']==409
    else:assert item['status']==200 and item['text'].encode()==samples[entry['source_path']]
   assert batch['secret.txt']['status']==404
   assert 'Facts.swift' not in files['theirs'] and 'secret.txt' not in files['files']
   assert ask('/world?f=secret.txt')[0]==404
   assert ask('/world?f=Facts.swift','PUT',b'public protocol MineStillWorks {}\n')[0]==200
   assert (world/'Facts.swift').read_bytes()==b'public protocol MineStillWorks {}\n'
   assert (world/'materials/source.md').read_text()=='FORGED local mirror'
   clash='public enum Clash: Mine {\n public typealias Kind = FormsFile\n}\nextension Clash { public static var typeName: String { "materials/source.md" } }\n'
   manifest.write_text(source.replace('public enum Taken0:',clash+'public enum Taken0:',1))
   code,body=ask('/world?f=materials/source.md')
   assert code==409 and b'FORGED local mirror' not in body, ('conflicting path delivered an unverified local body',code,body)
   assert ask('/world?f=materials/facts.json')[1]==samples['facts.json']
   manifest.write_text(source)
   variants=[]
   bad=copy.deepcopy(record);bad['files'][0]['sha256']='0'*64;variants.append(('wrong hash',bad,source))
   bad=copy.deepcopy(record);
   for e in bad['files']:e['revision']='1'*40
   variants.append(('missing pin',bad,source.replace(pin,'1'*40)))
   bad=copy.deepcopy(record);bad['files']=bad['files'][1:];variants.append(('missing row',bad,source))
   variants.append(('lost record',None,source))
   for label,changed,said in variants:
    manifest.write_text(said)
    if changed is None:descriptor.unlink()
    else:descriptor.write_text(json.dumps(changed,indent=2))
    code,body=ask('/world?f=materials/source.md');refusal=json.loads(body)
    assert code==409 and ':' in refusal['address'] and refusal['reason'] and b'FORGED' not in body,(label,code,body)
    if label in ('wrong hash','missing pin'):
     assert 'Taken0' in refusal['reason'] and 'gate.manifest.swift:' in refusal['reason']
     assert changed['files'][0]['repository']+'@'+changed['files'][0]['revision']+':source.md' in refusal['reason']
    fl=json.loads(ask('/files')[1]);assert 'materials/source.md' in fl['unavailable'],label
    assert ask('/world?f=materials/source.md','PUT',b'write despite lost pin')[0]==409
   manifest.write_text(source);descriptor.write_text(json.dumps(record,indent=2))
   assert ask('/world?f=materials/source.md')[1]==samples['source.md']
   # Every HTTP response reauthenticates its inputs. A prior successful read
   # must not cover a cache byte changed between requests.
   entry=entries[0]
   cached=ROOT/'bin/.inputs'/sha(str(owner).encode())/pin/(sha(b'source.md')+'-'+entry['sha256'])
   original=cached.read_bytes()
   try:
    cached.write_bytes(b'corrupted after the first read')
    code,body=ask('/world?f=materials/source.md')
    assert code==409 and 'cached input bytes differ' in json.loads(body)['reason'],(code,body)
   finally:cached.write_bytes(original)
   assert ask('/world?f=materials/source.md')[1]==original
   # A stat cache cannot authorize these bytes: inode, length and mtime stay.
   before=cached.stat();changed=bytes([original[0]^1])+original[1:]
   for atomic in (False,True):
    try:
     if atomic:
      replacement=cached.with_name(cached.name+'.replace');replacement.write_bytes(changed)
      os.utime(replacement,ns=(before.st_atime_ns,before.st_mtime_ns));replacement.replace(cached)
     else:
      with cached.open('r+b') as f:f.write(changed)
      os.utime(cached,ns=(before.st_atime_ns,before.st_mtime_ns))
      assert cached.stat().st_ino==before.st_ino
     assert cached.stat().st_size==before.st_size and cached.stat().st_mtime_ns==before.st_mtime_ns
     # Reading another resource never rehashes or admits this unrelated
     # input. A whole-world answer must still refuse it.
     assert ask('/world?f=materials/facts.json')[1]==samples['facts.json']
     other=json.loads(ask('/world','POST',b'["materials/facts.json"]')[1])['materials/facts.json']
     assert other['status']==200 and other['text'].encode()==samples['facts.json']
     assert json.loads(ask('/status')[1])['verdict']=='refused'
     code,body=ask('/world?f=materials/source.md');assert code==409 and json.loads(body)['address'].startswith('.gate/forms-definitions.json:')
     packet=json.loads(ask('/world','POST',b'["materials/source.md"]')[1])['materials/source.md']
     assert packet['status']==409 and json.loads(packet['text'])['address'].startswith('.gate/forms-definitions.json:')
    finally:cached.write_bytes(original)
    assert ask('/world?f=materials/source.md')[1]==original
   # Removing a cache entry rehydrates the pin with a fresh hash, like a cold
   # cache. Losing the declared input itself refuses; no held packet survives.
   saved=descriptor.read_bytes();stat=descriptor.stat()
   try:
    descriptor.unlink()
    packet=json.loads(ask('/world','POST',b'["materials/source.md"]')[1])['materials/source.md']
    assert packet['status']==409 and 'address' in json.loads(packet['text'])
   finally:descriptor.write_bytes(saved);os.utime(descriptor,ns=(stat.st_atime_ns,stat.st_mtime_ns))
   cached.unlink();assert ask('/world?f=materials/source.md')[1]==original
  finally:process.terminate();process.wait(timeout=10)
 print('CARRIED READINGS GREEN: exact UTF-8/CRLF/empty bytes, provenance, binary exclusion, no fallback, read-only Theirs and writable Mine')
if __name__=='__main__':run()
