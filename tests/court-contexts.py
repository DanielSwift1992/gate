#!/usr/bin/env python3
"""Declared context/2 fields and complete source coverage through gate's door."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import tempfile
import socket
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / 'bin/gate-cli'
LAW = '''import HarborShapes
public protocol Reading {
    associatedtype Value
}
public protocol Law: Reading
where Value == Token {}
public enum Claim: Law {
    public typealias Value = Token
}
public typealias Proof = Claim
'''
INTRINSIC = [dict(namespace='Swift', version='vi.court.intrinsic-swift/2', exports=['Never', 'String'])]


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix='gate-context2-') as tmp:
        root = Path(tmp); source = root / 'source'; world = root / 'world'
        source.mkdir(); world.mkdir(); (world / '.gate').mkdir()
        sources = {
            'Definitions.swift': 'public enum Token {}\npublic enum Other {}\n',
            'False.swift': 'public protocol BadReading {\n associatedtype Value\n}\npublic protocol BadLaw: BadReading\nwhere Value == A {}\npublic enum A {}\npublic enum B {}\npublic enum Bad: BadLaw {\n public typealias Value = B\n}\npublic typealias BadProof = Bad\n',
            'Scopes.swift': 'public enum GrammarScopes {\n public static let format = "vi-scope-map/1"\n public static let entries: [(String, String)] = [("Definitions.swift", "SurfaceScope"), ("False.swift", "SurfaceScope"), ("Page.swift", "DemoScope"), ("Other.swift", "DemoScope")]\n}\n',
        }
        for path, text in sources.items(): (source / path).write_text(text)
        subprocess.run(['git', 'init', '-q', str(source)], check=True)
        subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(source), '-c', 'user.name=Context fixture', '-c', 'user.email=context@fixture.invalid', 'commit', '-qm', 'frozen context inputs'], check=True)
        pin = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        language = dict(module='Harbor', namespace='Own', intrinsics=INTRINSIC, definitions=[],
                        imports=[dict(module='HarborShapes', namespace='Shapes', inputs=['Definitions'])], scope_map='Scopes')

        def write(text=LAW, *, context=None, second=None, kind='FormsFile', duplicate=False):
            if second is None and (world / 'Other.swift').exists(): (world / 'Other.swift').unlink()
            entries = [('Definitions', 'Definitions.swift', 'CarriedFile'), ('Scopes', 'Scopes.swift', 'CarriedFile')]
            if duplicate: entries += [('BorrowedBad', 'False.swift', 'CarriedFile'), ('OwnBad', 'False.swift', 'FormsFile')]
            doc = copy.deepcopy(context if context is not None else language)
            if duplicate: doc['definitions'].append('BorrowedBad')
            manifest = 'public protocol Role {}\npublic protocol Mine {}\npublic protocol Theirs {}\n'
            manifest += ''.join('public enum ' + k + ': Role {}\n' for k in ('FormsFile', 'DocumentFile', 'CarriedFile'))
            manifest += 'public enum Origin: Role {}\nextension Origin { public static var typeName: String { ' + json.dumps(source.as_uri() + '@' + pin) + ' } }\n'
            files = []
            for row, original, entry_kind in entries:
                path = 'vendor/' + row + '.swift'; body = sources[original].encode()
                manifest += 'public enum ' + row + ': Theirs {\n public typealias Kind = ' + entry_kind + '\n public typealias At = Origin\n'
                if entry_kind == 'FormsFile': manifest += ' public typealias Language = Context\n'
                manifest += '}\nextension ' + row + ' { public static var typeName: String { ' + json.dumps(path) + ' } }\n'
                files.append(dict(row=row, path=path, repository=source.as_uri(), revision=pin, source_path=original, sha256=hashlib.sha256(body).hexdigest()))
            pages = [('Main', 'Page.swift', text)]
            if second is not None: pages.append(('OtherPage', 'Other.swift', second))
            for row, path, body in pages:
                manifest += 'public enum ' + row + ': Mine {\n public typealias Kind = ' + kind + '\n public typealias Language = Context\n}\nextension ' + row + ' { public static var typeName: String { ' + json.dumps(path) + ' } }\n'
                (world / path).write_text(body)
            (world / 'gate.manifest.swift').write_text(manifest)
            (world / '.gate/forms-definitions.json').write_text(json.dumps(dict(format=2, files=files, languages={'Context': doc}, plain_fragments=[], shelf_overrides=False), indent=2) + '\n')

        def ask(case, expected=None, forbidden=None):
            p = subprocess.run([str(GATE), 'status', '--json'], cwd=world, capture_output=True, text=True, timeout=90)
            try: answer = json.loads(p.stdout)
            except ValueError: raise AssertionError((case, p.returncode, p.stdout[-1500:], p.stderr[-1500:]))
            if expected is not None: assert answer['verdict'] == expected, (case, answer)
            if forbidden is not None: assert answer['verdict'] != forbidden, (case, answer)
            results.append(dict(case=case, verdict=answer['verdict']))
            return answer

        write(); a = ask('module and namespace are different declared facts', 'holds')
        assert {r['path'] for q in a['court_readings'] for r in q['results']} == {'Page.swift'}
        for bad in (None, 42, ''):
            context = copy.deepcopy(language); context['module'] = bad
            write(context=context); ask('malformed module is never replaced by namespace: ' + repr(bad), 'refused')
        write(text='import Swift\n' + LAW); ask('closed intrinsic supplies an explicit Swift import', 'holds')
        context = copy.deepcopy(language); context['intrinsics'] = []
        write(text='import Swift\n' + LAW, context=context); ask('missing intrinsic is not manufactured', 'refused')
        false = 'import HarborShapes\npublic enum FalseClaim: Law {\n public typealias Value = Other\n}\npublic typealias FalseProof = FalseClaim\n'
        write(second=false); a = ask('the other own file is judged', 'refused')
        assert {r['path'] for q in a['court_readings'] for r in q['results']} == {'Page.swift', 'Other.swift'}
        write(text='public protocol Empty {}\n', kind='DocumentFile'); ask('zero checked is empty', 'empty')
        write(text=LAW + '#if FLAG\npublic enum Hidden {}\n#endif\n')
        a = ask('conditional exclusion keeps its source address', 'holds')
        assert any('Page.swift:' in x['address'] and 'conditional' in x['address'] for x in a['unchecked']), a
        write(duplicate=True); ask('a borrowed alias never consumes an own source path', forbidden='holds')

        write()
        with socket.socket() as sock: sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        with tempfile.TemporaryFile() as log:
            server = subprocess.Popen([str(GATE), 'serve', str(port), '--no-open'], cwd=world, stdout=log, stderr=log)
            try:
                plan = None
                for _ in range(200):
                    if server.poll() is not None: raise AssertionError('context receipt server exited')
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/grammar-contexts', timeout=20) as response: plan = json.load(response)
                        break
                    except urllib.error.URLError: time.sleep(.05)
                assert plan and not plan['refusals'] and not plan['unsupported'], plan
                def status():
                    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status', timeout=30) as response: return json.load(response)
                assert status()['verdict']=='holds'
                assert status()['verdict']=='holds'
                (world/'Page.swift').write_text(LAW.replace('Value = Token','Value = Other'))
                assert status()['verdict']=='refused'
                results.append(dict(case='warm plan reads changed own bytes',verdict='refused'))
                (world/'Page.swift').write_text(LAW)
                assert status()['verdict']=='holds'
                record_path=world/'.gate/forms-definitions.json';record=record_path.read_bytes();changed=json.loads(record)
                changed['files'][0]['sha256']='0'*64;record_path.write_text(json.dumps(changed))
                assert status()['verdict']=='refused'
                results.append(dict(case='warm plan cannot hide an invalid input pin',verdict='refused'))
                record_path.write_bytes(record)
                (world/'Page.swift').unlink()
                assert status()['verdict']!='holds'
                results.append(dict(case='warm plan cannot retain a missing own source',verdict='not-holds'))
                (world/'Page.swift').write_text(LAW)
                assert status()['verdict']=='holds'
            finally:
                server.terminate()
                try: server.wait(timeout=5)
                except subprocess.TimeoutExpired: server.kill(); server.wait()
        request = next(c for c in plan['contexts'] if c['language']=='Context')['requests'][0]
        canonical = lambda value: json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        request_hash = hashlib.sha256(canonical(request).encode()).hexdigest()
        with tempfile.TemporaryDirectory(prefix='receipt-answer-') as tmp:
            for file in request['files']:
                target=Path(tmp)/file['name'];target.parent.mkdir(parents=True,exist_ok=True);target.write_text(file['text'])
            p=subprocess.run([str(GATE),'judge']+request['arguments'],cwd=tmp,capture_output=True,text=True,check=True)
        clean=dict(exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
        def install(response):
            write()
            payload=dict(schema='gate.court.receipts/1',receipts=[dict(schema='gate.court.receipt/1',request_sha256=request_hash,response=response)])
            raw=(canonical(payload)+'\n').encode();(source/'Receipt.json').write_bytes(raw)
            subprocess.run(['git','-C',str(source),'add','Receipt.json'],check=True)
            subprocess.run(['git','-C',str(source),'-c','user.name=Context fixture','-c','user.email=context@fixture.invalid','commit','--allow-empty','-qm','frozen receipt input'],check=True)
            revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
            manifest=world/'gate.manifest.swift'
            manifest.write_text(manifest.read_text()+'public enum ReceiptOrigin: Role {}\nextension ReceiptOrigin { public static var typeName: String { '+json.dumps(source.as_uri()+'@'+revision)+' } }\npublic enum CourtReceipt: Theirs {\n public typealias Kind = CarriedFile\n public typealias At = ReceiptOrigin\n}\nextension CourtReceipt { public static var typeName: String { "Receipt.json" } }\n')
            record=world/'.gate/forms-definitions.json';data=json.loads(record.read_text())
            data['files'].append(dict(row='CourtReceipt',path='Receipt.json',repository=source.as_uri(),revision=revision,source_path='Receipt.json',sha256=hashlib.sha256(raw).hexdigest()))
            data['languages']['Context']['receipts']=['CourtReceipt'];record.write_text(json.dumps(data,indent=2)+'\n')
        install(clean);ask('complete owner receipt is admitted', 'holds')
        bad=copy.deepcopy(clean);bad['exit']=False;install(bad);ask('boolean exit is not an integer', forbidden='holds')
        for label,value in [('boolean',True),('unsafe',9007199254740992)]:
            bad=copy.deepcopy(clean);report=json.loads(bad['stdout']);report['results'][0]['memberships']=value;bad['stdout']=canonical(report)+'\n'
            install(bad);ask(label+' checked count is refused', forbidden='holds')
        bad=copy.deepcopy(clean);report=json.loads(bad['stdout']);report['inputs'][0]['sha256']='0'*64;bad['stdout']=canonical(report)+'\n'
        install(bad);ask('receipt cannot replace an input hash', forbidden='holds')
        install(clean)
        (world/'Page.swift').write_text(LAW.replace('Value = Token','Value = Other'))
        ask('changed source retires its holding receipt', 'refused')
    print(json.dumps(results))


if __name__ == '__main__': main()
