#!/usr/bin/env python3
"""Pinned bytes and installed readers, through the public status door."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def run():
    with tempfile.TemporaryDirectory(prefix='gate-inputs-kind-') as tmp:
        base = Path(tmp)
        dependency = base / 'dictionary'; dependency.mkdir()
        forms = '''public protocol Choice {}
public protocol Paired {}
public enum Pair<Left: Choice, Right: Choice> {}
extension Pair: Paired where Left == Right {}
public typealias Input_agrees = Pair<InputAtom, Coral>
'''
        for name, data in [('Forms.swift', forms.encode()), ('Types.swift', b'public enum Coral: Choice {}\npublic typealias InputAtom = Coral\n'),
                           ('world.swift', b'public enum Sales: Department {}\n'), ('asset.bin', b'\x00\xffdeclared bytes')]:
            (dependency / name).write_bytes(data)
        for args in [['init', '-q'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@test', 'commit', '-qm', 'pinned compiler inputs']]:
            subprocess.run(['git', *args], cwd=dependency, check=True)
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=dependency, text=True).strip()
        assert revision != (ROOT / 'bin/gate-judge.from').read_text().strip()
        owner = base / 'CoralAtlas'; (owner / '.gate').mkdir(parents=True)
        manifest = owner / 'gate.manifest.swift'; record = owner / '.gate/forms-definitions.json'
        text = 'public protocol Role {}\npublic protocol Theirs {}\n'
        for kind in ('FormsFile', 'WorldFile', 'CarriedFile'):
            text += 'public enum ' + kind + ': Role {}\n'
        text += 'public enum SourcePin: Role {}\nextension SourcePin {\n    public static var typeName: String { "' + str(dependency) + '@' + revision + '" }\n}\n'
        entries = []
        for row, kind, source in [('Claims', 'FormsFile', 'Forms.swift'), ('Vocabulary', 'CarriedFile', 'Types.swift'),
                                  ('Company', 'WorldFile', 'world.swift'), ('Asset', 'CarriedFile', 'asset.bin')]:
            path = '.gate/inputs/' + source
            text += 'public enum ' + row + ': Theirs {\n    public typealias Kind = ' + kind + '\n    public typealias At = SourcePin\n}\nextension ' + row + ' {\n    public static var typeName: String { "' + path + '" }\n}\n'
            entries.append(dict(row=row, path=path, repository=str(dependency), revision=revision,
                                source_path=source, sha256=hashlib.sha256((dependency / source).read_bytes()).hexdigest()))
        spec = dict(format=2, files=entries, languages={'Types': dict(definitions=['Vocabulary'])}, shelf_overrides=False)
        manifest.write_text(text)
        def write(value=spec):
            record.write_text(json.dumps(value, indent=2) + '\n')
        def status(executable=ROOT / 'gate'):
            reply = subprocess.run([str(executable), 'status', '--json'], cwd=owner, capture_output=True, text=True, timeout=30)
            return json.loads(reply.stdout or reply.stderr)
        def refused(label, value=None, field=None, claim=None):
            if value is not None: write(value)
            answer = status()
            assert answer['verdict'] == 'refused', (label, answer)
            errors = answer['refusals']
            assert errors and all(':' in e['address'] for e in errors), (label, answer)
            if field:
                error = next(e for e in errors if field in e['claim'])
                # The diagnostic names the actual source line, not a blanket :1.
                assert error['address'].startswith('.gate/forms-definitions.json:'), (label, error)
                line = int(error['address'].rsplit(':', 1)[1])
                assert line > 1 and field.rsplit('/', 1)[-1] in record.read_text().splitlines()[line-1], (label, error)
            if claim: assert any(claim in e['claim'] for e in errors), (label, answer)
            write(); manifest.write_text(text)
            return answer
        cache = ROOT / 'bin/.inputs' / hashlib.sha256(str(dependency).encode()).hexdigest()
        try:
            write()
            assert not cache.exists()
            missing = str(base / 'lost-repository')
            manifest.write_text(text.replace(str(dependency), missing))
            changed = copy.deepcopy(spec)
            for item in changed['files']: item['repository'] = missing
            refused('cold lost repository', changed, claim='cannot fetch the declared input revision')
            cold = status()
            assert cold['verdict'] == 'holds' and cold['forms']['equalities'] == 1, cold
            readers = {r['row']: (r['kind'], r['reader']) for r in cold['readers']}
            assert readers == dict(Claims=('FormsFile', 'FormsReaderV1'), Vocabulary=('CarriedFile', 'CarriedReaderV1'),
                                   Company=('WorldFile', 'OrganizationReaderV1'), Asset=('CarriedFile', 'CarriedReaderV1')), readers
            # Local copies are neither the source nor a fallback for Theirs.
            for entry in entries:
                path = owner / entry['path']; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(b'forged local copy')
            assert status()['verdict'] == 'holds'
            entry = entries[1]
            target = cache / revision / (hashlib.sha256(entry['source_path'].encode()).hexdigest() + '-' + entry['sha256'])
            original = target.read_bytes(); target.write_bytes(b'corrupt warm cache')
            refused('warm corruption', field='/files/1/sha256', claim='cached input bytes')
            target.write_bytes(original)
            assert status()['verdict'] == 'holds'
            for label, field, value in [('path', 'path', '.gate/other.swift'), ('At', 'revision', '0'*40),
                                        ('sha syntax', 'sha256', 'bad'), ('wrong bytes', 'sha256', '0'*64),
                                        ('missing source', 'source_path', 'missing.swift'), ('outside source', 'source_path', '../Types.swift'),
                                        ('absolute source', 'source_path', 'C:/Types.swift')]:
                changed = copy.deepcopy(spec); changed['files'][0][field] = value
                refused(label, changed, field='/files/0/' + field)
            changed = copy.deepcopy(spec); changed['files'].append(dict(entries[0], row='Extra'))
            refused('extra input', changed, field='/files/4/row', claim='exactly one Theirs')
            changed = copy.deepcopy(spec); changed['files'].append(entries[0])
            refused('repeat input row', changed, field='/files/4/row', claim='repeated row')
            changed = copy.deepcopy(spec); changed['files'].pop(0)
            refused('missing input row', changed, claim='Claims: a v2 taken row has no input record')
            changed = copy.deepcopy(spec); changed['files'][0]['reader'] = 'ForeignReader'
            refused('unknown input field', changed, field='/files/0/reader')
            changed = copy.deepcopy(spec); del changed['files'][0]['sha256']
            refused('missing hash field', changed, claim='/files/0/sha256: a string is required')
            changed = copy.deepcopy(spec); changed['files'][0]['sha256'] = 123
            refused('wrong field type', changed, field='/files/0/sha256')
            record.write_text(record.read_text().replace('"row": "Claims",', '"row": "Claims",\n      "row": "Claims",', 1))
            refused('duplicate JSON field', claim='repeated field')
            changed = copy.deepcopy(spec); changed['surprise'] = True
            refused('unknown root field', changed, field='/surprise')
            changed = copy.deepcopy(spec); changed['format'] = 3
            refused('unknown version', changed, field='/format')
            record.write_text('{broken'); refused('broken JSON', claim='JSON object')
            record.unlink(); lost = refused('lost record', claim='pinned input record')
            # The old publisher left this note beside its definitions. A lost
            # declared input must refuse through N1 with or without that note.
            legacy_note = owner / '.gate/worlds.from'
            historical = ROOT / 'tests/fixtures/legacy-worlds-note.from'
            provenance = json.loads(historical.with_suffix('.source.json').read_text())
            assert hashlib.sha256(historical.read_bytes()).hexdigest() == provenance['sha256']
            legacy_note.write_bytes(historical.read_bytes())
            record.unlink(); noted = refused('lost record with legacy note', claim='pinned input record')
            legacy_note.unlink()
            for answer in (lost, noted):
                assert any(e['address'].startswith('gate.manifest.swift:') and 'Claims:' in e['claim']
                           and 'pinned input record' in e['claim'] for e in answer['refusals']), answer
            assert lost['refusals'] == noted['refusals'], (lost, noted)
            print('INPUT RECORD LOSS: ' + json.dumps([dict(legacy_note=flag,refusals=answer['refusals'])
                  for flag,answer in [(False,lost),(True,noted)]]))
            manifest.write_text(text + text[text.index('public enum Claims:'):text.index('public enum Vocabulary:')])
            refused('repeated manifest row', claim='repeated manifest row')
            manifest.write_text(text.replace('    public typealias Kind = FormsFile', '    public static var role: String { "forms" }'))
            refused('v2 Kind required', claim='a v2 input row must declare Kind')
            manifest.write_text(text.replace('public enum FormsFile: Role {}', 'public enum FormsFile: Role {\n    public typealias Reader = CarriedReaderV1\n}'))
            refused('local reader override', claim='cannot replace')
            # Renaming a row changes references, not gate's reader code.
            manifest.write_text(text.replace('Claims', 'EntryRenamed'))
            changed = copy.deepcopy(spec); changed['files'][0]['row'] = 'EntryRenamed'; write(changed)
            assert status()['verdict'] == 'holds'
            manifest.write_text(text); write()
            manifest.write_text(text.replace('Kind = FormsFile', 'Kind = DocumentFile') + '\npublic enum DocumentFile: Role {}\n')
            answer = status()
            assert answer['verdict'] == 'holds' and answer['forms']['equalities'] > 0, answer
            assert next(r for r in answer['readers'] if r['row'] == 'Claims')['reader'] == 'DocumentReaderV1', answer
            changed = copy.deepcopy(spec); changed['files'][0]['sha256'] = '0' * 64
            refused('DocumentFile cannot substitute unverified input', changed)
            write()
            for kind in ('FutureDocumentFile', 'CatalogFile'):
                manifest.write_text(text.replace('Kind = FormsFile', 'Kind = ' + kind) + ('\npublic enum CatalogFile: Role {}\n' if kind == 'CatalogFile' else ''))
                answer = status()
                assert answer['verdict'] in ('partial', 'unsupported') and any(kind in r['reason'] for r in answer['unsupported']), answer
            manifest.write_text(text.replace('Kind = FormsFile', 'Kind = CarriedFile'))
            answer = status()
            assert not answer.get('forms') and not answer['refusals'], answer
            assert next(r for r in answer['readers'] if r['row'] == 'Claims')['reader'] == 'CarriedReaderV1'
            # An installed shelf selects the code reader; a world cannot do so.
            # Exercise another installation without changing this checkout.
            manifest.write_text(text); write()
            installed = base / 'installation'
            (installed / 'bin').mkdir(parents=True); (installed / 'stdlib').mkdir()
            executable = installed / 'bin/gate-cli'
            shutil.copy2(ROOT / 'bin/gate-cli', executable)
            shelf = (ROOT / 'stdlib/manifest.swift').read_text()
            (installed / 'stdlib/manifest.swift').write_text(shelf.replace('Reader = FormsReaderV1', 'Reader = CarriedReaderV1'))
            answer = status(executable)
            assert not answer.get('forms') and next(r for r in answer['readers'] if r['row'] == 'Claims')['reader'] == 'CarriedReaderV1', answer
            (installed / 'stdlib/manifest.swift').write_text(shelf.replace('Reader = FormsReaderV1', 'Reader = FutureReaderV9'))
            answer = status(executable)
            assert answer['verdict'] in ('partial', 'unsupported') and any('FutureReaderV9' in r['reason'] for r in answer['unsupported']), answer
            # A self-contained world declares no taken inputs. An old publisher
            # note is evidence, not a new requirement for an external record.
            plain = base / 'SelfContained'; (plain / '.gate').mkdir(parents=True)
            (plain / 'gate.manifest.swift').write_text('''public protocol Role {}
public protocol Mine {}
public enum FormsFile: Role {}
public enum Claims: Mine {
    public typealias Kind = FormsFile
}
extension Claims { public static var typeName: String { "Claims.swift" } }
''')
            (plain / 'Claims.swift').write_text(forms + (dependency / 'Types.swift').read_text())
            def plain_status():
                r = subprocess.run([str(ROOT/'bin/gate-cli'),'status','--json'],cwd=plain,capture_output=True,text=True,timeout=30)
                return json.loads(r.stdout)
            without_note = plain_status()
            assert without_note['verdict'] == 'holds' and without_note['forms']['equalities'] == 1, without_note
            (plain / '.gate/worlds.from').write_bytes(historical.read_bytes())
            with_note = plain_status()
            assert with_note['verdict'] == 'holds' and with_note['forms'] == without_note['forms'], with_note
            assert not with_note['refusals'] and not with_note.get('unsupported'), with_note
            print('SELF-CONTAINED LEGACY NOTE: ' + json.dumps(dict(without_note=without_note,with_note=with_note)))
            print('INPUTS/KIND ALL GREEN: cold/warm bytes, schema, source addresses and installed readers')
        finally:
            shutil.rmtree(cache, ignore_errors=True)
            shutil.rmtree(ROOT / 'bin/.inputs' / hashlib.sha256(str(base / 'lost-repository').encode()).hexdigest(), ignore_errors=True)


if __name__ == '__main__':
    run()
