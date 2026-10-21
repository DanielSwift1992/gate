#!/usr/bin/env python3
"""N2 on an ordinary prepared source, with no application paths or overrides."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

HERE = Path(__file__).resolve().parent.parent
CLI = HERE / 'bin/gate-cli'


def scope_map(entries):
    return ('public enum GrammarScopes {\npublic static let format = "vi-scope-map/1"\n'
            'public static let entries: [(String, String)] = [\n'
            + ''.join('(' + json.dumps(a) + ', ' + json.dumps(b) + '),\n' for a, b in entries)
            + ']\n}\n')


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vi-tools', type=Path)
    ap.add_argument('--vi-theory', type=Path)
    ap.add_argument('--evidence', type=Path)
    args = ap.parse_args()
    if bool(args.vi_tools) != bool(args.vi_theory): ap.error('--vi-tools and --vi-theory are a pair')
    if args.vi_theory:
        law = json.loads((HERE / 'bin/grammar-law.from').read_text())
        revision = subprocess.check_output(['git', '-C', str(args.vi_theory), 'rev-parse', 'HEAD'], text=True).strip()
        assert revision == law['revision'], 'the owner tool must run at the declared law revision'
        for item in law['files'].values():
            assert hashlib.sha256((args.vi_theory / item['source_path']).read_bytes()).hexdigest() == item['sha256']
    evidence = []
    binary_sha256 = hashlib.sha256(CLI.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='gate-n2-') as temp:
        root = Path(temp)
        source, world = root / 'source', root / 'world'
        source.mkdir(); world.mkdir()
        (world / '.gate').mkdir()
        files = {
            'Definitions/One.swift': 'public enum One {}\npublic enum U512 {}\n',
            'Definitions/Two.swift': 'public enum Two {}\n',
            'Definitions/Three.swift': 'public enum Three {}\n',
            'Definitions/Fourth.swift': 'public enum Token {}\n',
            'Definitions/Other.swift': 'public enum Token {}\n',
            'Checks/scopes.swift': scope_map([('Definitions', 'SurfaceScope'), ('Pages', 'DemoScope')]),
        }
        for path, text in files.items():
            p = source / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        def git(*words):
            return subprocess.check_output(['git', '-C', str(source), *words], text=True).strip()
        git('init', '-q')
        def pin():
            git('add', '.')
            git('-c', 'user.name=Scope fixture', '-c', 'user.email=scope@fixture.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture: an owner declares its inputs')
            return git('rev-parse', 'HEAD')
        revision = pin()
        refs = {'DefOne': 'Definitions/One.swift', 'DefTwo': 'Definitions/Two.swift',
                'DefThree': 'Definitions/Three.swift', 'DefFourth': 'Definitions/Fourth.swift',
                'ScopeMap': 'Checks/scopes.swift'}
        imports = [dict(module=name, inputs=[ref], namespace=ns) for name, ref, ns in [
            ('VerificationIsIdentification', 'DefOne', 'One'), ('DocumentKit', 'DefTwo', 'Two'),
            ('Organization', 'DefThree', 'Three'), ('HarborShapes', 'DefFourth', 'Shapes')]]
        language = dict(definitions=['DefFourth'], namespace='Harbor', imports=imports, scope_map='ScopeMap')
        body = 'import HarborShapes\npublic protocol Reading { associatedtype Value }\npublic protocol Claim: Reading\nwhere Value == Token {}\npublic enum Same: Claim {\n    public typealias Value = Token\n}\npublic typealias Certificate = Same\n'
        pages = {'Pages/Main.swift': ('Main', 'HarborLanguage', body)}

        def write(contexts=None, selected=None, page_rows=None, kinds=None):
            for old in world.rglob('*.swift'):
                old.unlink()
            selected = selected or refs
            page_rows = page_rows or pages
            contexts = copy.deepcopy(contexts or {'HarborLanguage': language})
            record = dict(format=2, files=[], languages=contexts, shelf_overrides=False, plain_fragments=[])
            manifest = 'public protocol Mine {}\npublic protocol Theirs {}\npublic protocol Role {}\npublic enum FormsFile: Role {}\npublic enum DocumentFile: Role {}\npublic enum WorldFile: Role {}\npublic enum CarriedFile: Role {}\n'
            manifest += 'public enum Origin: Role {}\nextension Origin {\npublic static var typeName: String { ' + json.dumps(source.as_uri() + '@' + revision) + ' }\n}\n'
            for row, path in selected.items():
                local = 'vendor/' + row + '.swift'
                data = (source / path).read_bytes()
                view = world / local; view.parent.mkdir(parents=True, exist_ok=True); view.write_bytes(data)
                manifest += 'public enum ' + row + ': Theirs {\npublic typealias Kind = CarriedFile\npublic typealias At = Origin\n}\nextension ' + row + ' {\npublic static var typeName: String { ' + json.dumps(local) + ' }\n}\n'
                record['files'].append(dict(row=row, path=local, repository=source.as_uri(), revision=revision,
                                            source_path=path, sha256=hashlib.sha256(data).hexdigest()))
            for path, (row, lang, text) in page_rows.items():
                p = world / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
                p = source / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
                manifest += 'public enum ' + row + ': Mine {\npublic typealias Kind = ' + (kinds or {}).get(row, 'FormsFile') + '\n'
                if lang: manifest += 'public typealias Language = ' + lang + '\n'
                manifest += '}\nextension ' + row + ' {\npublic static var typeName: String { ' + json.dumps(path) + ' }\n}\n'
            manifest = manifest.replace('\npublic static var typeName', '\n    public static var typeName').replace('\npublic typealias', '\n    public typealias')
            (world / 'gate.manifest.swift').write_text(manifest)
            (world / '.gate/forms-definitions.json').write_text(json.dumps(record, indent=2) + '\n')

        def ask(label, expected='holds', reason=None):
            p = subprocess.run([str(CLI), 'status', '--json'], cwd=world, capture_output=True, text=True, timeout=90)
            try: answer = json.loads(p.stdout)
            except Exception: raise AssertionError((label, p.returncode, p.stdout[-1500:], p.stderr[-1000:]))
            assert answer.get('verdict') == expected, (label, answer)
            if reason:
                failures = answer.get('refusals', []) + answer.get('unsupported', [])
                assert any(reason in json.dumps(f) and ':' in f.get('address', '') for f in failures), (label, answer)
            evidence.append(dict(case=label, verdict=answer['verdict'], refusals=answer.get('refusals', []), unsupported=answer.get('unsupported', [])))
            return answer

        def plan():
            sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
            proc = subprocess.Popen([str(CLI), 'serve', str(port), '--no-open'], cwd=world,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(100):
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/grammar-contexts', timeout=2) as r:
                            return json.load(r)
                    except OSError:
                        assert proc.poll() is None, 'serve stopped before its context answer'
                        time.sleep(.05)
                raise AssertionError('serve did not answer')
            finally:
                proc.terminate(); proc.wait(timeout=10)

        def owner(label, expected):
            if not args.vi_tools: return
            receipt = root / 'owner.json'
            env = dict(os.environ, VI_THEORY_PATH=str(args.vi_theory))
            paths = list(dict.fromkeys([p for p in refs.values() if p.startswith('Definitions/')] + list(pages)))
            p = subprocess.run([str(args.vi_tools), 'grammar', '--scope-map', 'Checks/scopes.swift', '--receipt', str(receipt), *paths],
                               cwd=source, env=env, capture_output=True, text=True, timeout=300)
            assert p.returncode == expected, (label, p.stdout[-1800:])
            for line in p.stdout.splitlines():
                if line.startswith('scratch kept at '): shutil.rmtree(line.removeprefix('scratch kept at '), ignore_errors=True)
            entry = dict(case=label, owner_exit=p.returncode)
            if receipt.exists() and expected == 0:
                r = json.loads(receipt.read_text()); port_plan = plan()
                assert r['policy_sha256'] == port_plan['policy_sha256']
                selected = {u['source_path']: u['scope'] for c in port_plan['contexts'] for u in c['inputs']}
                assert r['files'] == selected, (r['files'], selected)
                assert all(u['scope_map_sha256'] == r['scope_map_sha256'] for c in port_plan['contexts'] for u in c['inputs'])
                assert all(u['source_sha256'] == r['source_sha256'][u['source_path']] for c in port_plan['contexts'] for u in c['inputs'])
                entry.update(owner=r, port=port_plan)
            evidence.append(entry)

        def publication_case(label, expected):
            # This is an ordinary Publication: the native builder, serve and
            # static browser transport consume the same resolved Language plan.
            publication = root / 'publication'
            if publication.exists(): shutil.rmtree(publication)
            publication.mkdir(); (publication / '.gate').mkdir()
            shutil.copytree(world, publication / 'Island')
            def atom(name, text):
                return 'public enum ' + name + ': Close {}\nextension ' + name + ' { public static var typeName: String { ' + json.dumps(text) + ' } }\n'
            catalog = 'public protocol Close {}\n'
            catalog += 'public enum Dock: Close {\n public typealias Id = DoorId\n public typealias Group = Group\n public typealias Title = Title\n public typealias Shown = Shown\n public typealias Reads = Island\n public typealias Caption = Caption\n}\n'
            catalog += 'public enum Island: Close {\n public typealias File = Directory\n public typealias Name = WorldName\n}\npublic enum Group: Close {\n public typealias Name = GroupName\n}\n'
            for name, text in [('DoorId', 'harbor'), ('Title', 'Harbor'), ('Shown', 'Pages/Main.swift'), ('Caption', 'Declared contexts'), ('Directory', 'Island'), ('WorldName', 'Island'), ('GroupName', 'Atlas')]:
                catalog += atom(name, text)
            (source / 'Doors.swift').write_text(catalog)
            catalog_revision = pin() if git('status', '--porcelain') else git('rev-parse', 'HEAD')
            manifest = 'public protocol Close {}\npublic protocol Role {}\npublic protocol Theirs {}\npublic protocol Publication {}\npublic enum CatalogFile: Role {}\n'
            manifest += 'public enum Book: Publication {\n public typealias Id = BookId\n public typealias Entry = Dock\n public typealias Catalog = Catalog\n public typealias DraftPolicy = ReadOnly\n public typealias DrawingProfile = NoDrawing\n public typealias Aliases = ()\n}\n'
            manifest += 'public enum Catalog: Theirs {\n public typealias Kind = CatalogFile\n public typealias At = Origin\n}\nextension Catalog { public static var typeName: String { ".gate/doors.swift" } }\n'
            manifest += atom('BookId', 'org.example.contexts') + atom('Origin', source.as_uri() + '@' + catalog_revision)
            (publication / 'gate.manifest.swift').write_text(manifest)
            record = dict(format=2, files=[dict(row='Catalog', path='.gate/doors.swift', repository=source.as_uri(), revision=catalog_revision, source_path='Doors.swift', sha256=hashlib.sha256(catalog.encode()).hexdigest())], languages={}, plain_fragments=[], shelf_overrides=False)
            (publication / '.gate/forms-definitions.json').write_text(json.dumps(record))
            subprocess.run(['git', 'init', '-q', str(publication)], check=True)
            subprocess.run(['git', '-C', str(publication), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(publication), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@test', 'commit', '-qm', 'declared publication'], check=True)
            installation = root / 'installation'; installation.mkdir(exist_ok=True)
            binary = installation / 'gate'; shutil.copy2(CLI, binary)
            site = root / ('site-' + expected)
            reply = subprocess.run([str(binary), 'publish', str(publication), '-o', str(site), '--json'], cwd=root, capture_output=True, text=True, timeout=90)
            assert reply.returncode == 0, (label, reply.stdout, reply.stderr)
            document = json.loads((site / 'read-plan.json').read_text())
            snapshot = json.loads((site / 'snapshots/harbor.json').read_text())['responses']
            answer = json.loads(snapshot['GET /status']['body'])
            assert answer['verdict'] == expected, (label, answer)
            contexts = json.loads(snapshot['GET /grammar-contexts']['body'])
            assert document['languages']['Island']['resolved'] == contexts and contexts['active']
            # Court coverage and transport must identify the actual same bytes.
            for context in contexts['contexts']:
                for unit in context['inputs']:
                    delivered = site / 'inputs' / unit['source_sha256']
                    assert delivered.exists() and hashlib.sha256(delivered.read_bytes()).hexdigest() == unit['source_sha256']
                    row = next(i for i in document['inputs'] if i['manifest'] == 'Island/gate.manifest.swift' and i['row'] == unit['row'])
                    assert row['sha256'] == unit['source_sha256']
                    if row['source'] == 'theirs': assert row['origin']['sha256'] == row['sha256']
            assert document['languages']['Island']['declared'] == json.loads((world / '.gate/forms-definitions.json').read_text())['languages']
            if len(contexts['contexts']) > 1:
                assert len(document['worlds'][0]['groups']) == len(contexts['contexts']), document['worlds']
            assert any(i['language'] == 'HarborLanguage' for i in document['inputs'] if i['manifest'] == 'Island/gate.manifest.swift')
            sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
            proc = subprocess.Popen([str(binary), 'serve', str(publication), str(port), '--no-open'], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(150):
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/read-plan.json', timeout=2) as r: live = json.load(r)
                        break
                    except OSError:
                        assert proc.poll() is None
                        time.sleep(.05)
                else: raise AssertionError('publication serve did not answer')
                assert live == document
                for path in ['/grammar-contexts', '/status']:
                    with urllib.request.urlopen('http://127.0.0.1:' + str(port) + path, timeout=10) as r:
                        assert r.read() == snapshot['GET ' + path]['body'].encode(), path
            finally:
                proc.terminate(); proc.wait(timeout=10)
            moved = root / 'relocated-publication'
            if moved.exists(): shutil.rmtree(moved)
            shutil.copytree(publication, moved)
            moved_site = root / 'relocated-site'
            reply = subprocess.run([str(binary), 'publish', str(moved), '-o', str(moved_site), '--json'], cwd=root, capture_output=True, text=True, timeout=90)
            assert reply.returncode == 0, reply.stderr
            assert json.loads((moved_site / 'read-plan.json').read_text()) == document
            subprocess.run(['node', str(HERE / 'tests/publication.js'), str(site), expected, 'Pages/Main.swift'], check=True, stdout=subprocess.DEVNULL)
            evidence.append(dict(case=label, verdict=expected, plan_id=document['plan_id'], contexts=contexts))

        write(); a = ask('declared fourth module'); assert a['forms']['equalities'] >= 1, a
        baseline = plan(); assert baseline['active'] and len(baseline['contexts'][0]['inputs']) == 5
        assert all(u['source_path'].startswith(('Definitions/', 'Pages/')) for u in baseline['contexts'][0]['inputs'])
        owner('same source and pinned scope bytes', 0)
        write(kinds={'Main': 'DocumentFile'})
        a = ask('DocumentFile uses the declared where context')
        assert a['forms']['equalities'] >= 1, a
        publication_case('DocumentFile is carried by the common ReadPlan', 'holds')
        doc_bad = {'Pages/Main.swift': ('Main', 'HarborLanguage', body.replace('Value = Token', 'Value = One'))}
        write(page_rows=doc_bad, kinds={'Main': 'DocumentFile'})
        ask('DocumentFile preserves a false equality', 'refused')
        doc_body = body + 'public enum Paper {\n    public static var body: some Structure {\n        UnknownDrawing<One>.self\n    }\n}\n'
        write(page_rows={'Pages/Main.swift': ('Main', 'HarborLanguage', doc_body)}, kinds={'Main': 'DocumentFile'})
        a = ask('DocumentReader keeps builder implementation outside the relation claim')
        assert a['forms']['equalities'] >= 1 and any('builder bodies are unchecked' in x['reason'] for x in a['unchecked']), a
        write(page_rows={'Pages/Main.swift': ('Main', 'HarborLanguage', doc_body.replace('Value = Token', 'Value = One'))}, kinds={'Main': 'DocumentFile'})
        ask('an unchecked body cannot hide a false declared equality', 'refused')
        wrong_doc = copy.deepcopy(language); wrong_doc['definitions'] = ['MissingDefinition']
        write({'HarborLanguage': wrong_doc}, kinds={'Main': 'DocumentFile'})
        ask('DocumentFile cannot lose a declared definition', 'refused', 'MissingDefinition')
        write(page_rows={'Pages/Main.swift': ('Main', 'HarborLanguage', body + '\n@Unknown public enum Mystery {}\n')}, kinds={'Main': 'DocumentFile'})
        ask('DocumentFile names unread syntax', 'unsupported', 'Language declaration reader')
        write()
        # A decoder's first/last-key preference cannot erase context fields.
        record_path = world / '.gate/forms-definitions.json'
        for label, level in [('duplicate Language root', 'root'), ('duplicate context name', 'context'), ('duplicate namespace', 'namespace')]:
            write(); text = record_path.read_text(); record = json.loads(text)
            if level == 'root':
                text = text.rstrip()[:-1] + ', "languages": {"HarborLanguage": {"reader": "IgnoredReader"}}}'
            elif level == 'context':
                contexts = json.dumps(record.pop('languages'))
                text = json.dumps(record)[:-1] + ', "languages": ' + contexts[:-1] + ', "HarborLanguage": {"reader": "IgnoredReader"}}}'
            else:
                text = text.replace('"namespace": "Harbor"', '"namespace": "Harbor", "namespace": "Other"', 1)
            record_path.write_text(text)
            ask(label + ' cannot hide data', 'refused', 'repeated field')
        write()

        publication_case('one ReadPlan carries the declared fourth module', 'holds')
        wrong = copy.deepcopy(language); wrong['imports'] = imports[:3]
        write({'HarborLanguage': wrong}); ask('undeclared fourth module', 'refused', "import 'HarborShapes'")
        publication_case('one ReadPlan carries the undeclared import refusal', 'refused')
        wrong = copy.deepcopy(language); wrong['definitions'] += ['MissingDefinition']
        write({'HarborLanguage': wrong}); ask('missing definition', 'refused', 'MissingDefinition')
        (source / 'Definitions/Fourth.swift').write_text('public enum Replacement {}\n')
        revision = pin(); write()
        ask('a module input must provide the referenced declaration', 'unsupported', "no declared definition for 'Token'")
        publication_case('one ReadPlan preserves a missing declaration as unsupported', 'unsupported')
        (source / 'Definitions/Fourth.swift').write_text(files['Definitions/Fourth.swift'])
        revision = pin()
        wrong = copy.deepcopy(language); wrong['profile'] = 'ASecondReader'
        write({'HarborLanguage': wrong}); ask('Kind alone chooses the reader', 'refused', "field 'profile'")
        wrong = copy.deepcopy(language); wrong['scope_map'] = 17
        write({'HarborLanguage': wrong}, page_rows={'Pages/Main.swift': ('Main', None, body)})
        ask('a malformed map cannot fall back without Language', 'refused', 'explicit Language')
        wrong = copy.deepcopy(language); wrong['profile'] = 'ASecondReader'
        write({'HarborLanguage': wrong}, page_rows={'Pages/Main.swift': ('Main', None, body)})
        ask('an unused reader override is still invalid', 'refused', "field 'profile'")
        write(kinds={'Main': 'WorldFile'})
        a = ask('WorldFile keeps its plain court', 'refused')
        assert 'forms' not in a, a
        write(kinds={'Main': 'UnpublishedKind'}); ask('unknown Kind', 'refused')
        write(page_rows={'Pages/Main.swift': ('Main', None, body)}); ask('missing Language axis', 'refused', 'explicit Language')

        duplicate = copy.deepcopy(language)
        duplicate['imports'] += [dict(module='OtherShapes', inputs=['DefOther'], namespace='Shapes')]
        more = dict(refs, DefOther='Definitions/Other.swift')
        write({'HarborLanguage': duplicate}, more); ask('same namespace conflicts with both addresses', 'refused', "conflicts on 'Token' with vendor/")
        other = copy.deepcopy(language); other['namespace'] = 'Elsewhere'
        other['definitions'] = ['DefOther']; other['imports'][-1] = dict(module='HarborShapes', inputs=['DefOther'], namespace='ElsewhereShapes')
        two = dict(pages, **{'Pages/Other.swift': ('OtherPage', 'OtherLanguage', body)})
        unassigned = dict(two); unassigned['Pages/Main.swift'] = ('Main', None, body)
        write({'HarborLanguage': language, 'OtherLanguage': other}, more, unassigned)
        ask('a mixed prepared context cannot omit a source Language', 'refused', 'every judged source')
        write({'HarborLanguage': language, 'OtherLanguage': other}, more, two)
        a = ask('equal names in separate contexts stay separate')
        publication_case('one ReadPlan keeps homonymous Language groups separate', 'holds')
        assert a['forms']['equalities'] == 2, a
        (source / 'Definitions/Fourth.swift').write_text('public enum Replacement {}\n')
        revision = pin(); write({'HarborLanguage': language, 'OtherLanguage': other}, more, two)
        a = ask('one namespace cannot borrow another namespace definition', 'partial', "no declared definition for 'Token'")
        assert a['forms']['equalities'] == 1, a
        (source / 'Definitions/Other.swift').write_text('public enum Replacement {}\n')
        revision = pin(); write({'HarborLanguage': language, 'OtherLanguage': other}, more, two)
        ask('every context reports its own missing declaration', 'unsupported', "no declared definition for 'Token'")
        (source / 'Definitions/Other.swift').write_text(files['Definitions/Other.swift'])
        (source / 'Definitions/Fourth.swift').write_text(files['Definitions/Fourth.swift'])
        revision = pin()


        # One input identity under two byte-distinct maps is a conflict even
        # when both happen to select the same scope for this source.
        (source / 'Checks/other.swift').write_text(files['Checks/scopes.swift'] + '// another map\n')
        revision = pin()
        more = dict(more, OtherMap='Checks/other.swift')
        other['scope_map'] = 'OtherMap'
        write({'HarborLanguage': language, 'OtherLanguage': other}, more, two)
        ask('one source cannot receive two maps', 'refused', 'conflicting scope maps')
        other['scope_map'] = 'ScopeMap'
        write({'HarborLanguage': language, 'OtherLanguage': other}, more, two)
        ask('identical map references combine')

        (source / 'Checks/scopes.swift').write_text(scope_map([('Pages', 'DemoScope')]))
        revision = pin(); write(); ask('uncovered source has its original path', 'refused', "uncovered source path 'Definitions/")
        owner('owner also refuses uncovered source', 1)
        (source / 'Checks/scopes.swift').write_text(scope_map([('Definitions', 'SurfaceScope'), ('Pages', 'DemoScope'), ('Pages', 'SurfaceScope')]))
        revision = pin(); write(); ask('conflicting equal prefixes', 'refused', 'conflicting equal prefixes')
        owner('owner also refuses conflicting prefixes', 1)
        (source / 'Checks/scopes.swift').write_text(files['Checks/scopes.swift'])
        revision = pin()
        pages['Pages/Main.swift'] = ('Main', 'HarborLanguage', body + 'public typealias Width = U512\n')
        write(); ask('DemoScope width stays refused', 'refused', 'U512Word')
        owner('owner also refuses width on a page', 1)
        (source / 'Checks/scopes.swift').write_text(scope_map([('Pages', 'DemoScope'), ('Definitions', 'SurfaceScope'), ('Pages/Main.swift', 'SurfaceScope')]))
        revision = pin(); write(); ask('owner changes the map without changing vi or gate')
        owner('longer source path wins for both consumers', 0)

        # These compare the owner's context/foreign/unknown-atom doors too;
        # the input stays an ordinary FormsFile, never a demo switch.
        grammar_vectors = [
            # A page with no declared applications is admitted, and says so as
            # empty: the grammar passed, and no relation was there to hold.
            ('builder context admits its separator', 'public enum Page {\n    public static var body: some Structure { Item.self; Item.self }\n}\n', 'empty'),
            ('plain context refuses that separator', 'public enum Page {\n    public static var body: Other { Item.self; Item.self }\n}\n', 'refused'),
            ('unregistered character', 'public typealias Snow = ' + chr(0x2603) + '\n', 'refused'),
            ('exemption does not register a character', 'public enum Page: GrammarExempt {\n' + chr(0x2603) + '\n}\n', 'refused'),
            ('a trailing pair-sensitive atom is addressed', 'public var', 'refused'),
        ]
        for label, text, expected in grammar_vectors:
            pages['Pages/Main.swift'] = ('Main', 'HarborLanguage', text)
            write(); ask(label, expected)
            owner(label + ' agrees with vi', 0 if expected in ('holds', 'empty') else 1)

        pages['Pages/Main.swift'] = ('Main', 'HarborLanguage', 'import enum HarborShapes.Token\n')
        write(); ask('an unsupported import form is named', 'unsupported', 'import syntax is not supported')
        pages['Pages/Main.swift'] = ('Main', 'HarborLanguage', 'import HarborShapes\npublic typealias Width = `Token`\n')
        write(); a = ask('unread syntax is not holds', 'unsupported', 'Language declaration reader')

    assert hashlib.sha256(CLI.read_bytes()).hexdigest() == binary_sha256, "the binary changed during N2"
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=2) + '\n')
    print('N2: ' + str(len(evidence)) + ' ordinary-source context, import, Kind, namespace and scope controls hold')


if __name__ == '__main__': run()
