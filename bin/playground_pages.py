"""Publish the site's declared tabs over the world's own manifest and sources."""
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile


def build_worlds(here, out, publish):
    here, out = Path(here), Path(out)
    cache = Path(subprocess.check_output([str(here / 'bin/playground-worlds.sh')], text=True).strip())
    record = json.loads((cache / 'worlds.from').read_text())
    compiler_pin = re.search(r'let theoryRevision = "([0-9a-f]+)"',
                             (cache / 'showcase/Package.swift').read_text())
    if not compiler_pin or compiler_pin[1] != record['theory']['revision']:
        raise ValueError('the showcase package and the world record name different compiler pins')
    if (here / 'bin/gate-judge.from').read_text().strip() != record['judge']['revision']:
        raise ValueError('the world record and the native judge pin differ')
    if (here / 'bin/court-wasm.from').read_text().splitlines()[0] != record['wasm']['revision']:
        raise ValueError('the world record and the wasm court pin differ')
    for name, want in record['wasm']['files'].items():
        if hashlib.sha256((here / name).read_bytes()).hexdigest() != want:
            raise ValueError(name + ': wasm bytes differ from the world record')
    source = cache / 'showcase/Worlds/Playground'
    tabs = json.loads(subprocess.check_output(['node', str(here / 'bin/playground-site.js'),
                                              str(source / 'Site/Manifest.swift')], text=True))
    # Source worlds are records in the same catalog, never a publisher's second list.
    entries = tabs
    catalog = dict(file='Site/Manifest.swift', revision=record['showcase']['revision'],
        sha256=record['showcase']['files']['Worlds/Playground/Site/Manifest.swift'],
        text=(source / 'Site/Manifest.swift').read_text(),
        destinations={tab['record']: tab['id'] for tab in tabs})
    # Both the catalog record and the world it Reads have a door. Seeds name a
    # source world, not the generated world's identity (CompanyWorld -> company).
    catalog['destinations'].update({tab['reads']: tab['id'] for tab in tabs if not tab['generated']})
    primitive = 'Sources/VerificationIsIdentification/Primitive.swift'
    guard_sources = [str(cache / 'theory' / name) for name in record['theory']['files']]
    guard_sources += [str(cache / 'showcase' / name) for name in record['showcase']['files']
                     if name.startswith('Sources/') and name.endswith('.swift')]
    guard_names = json.loads(subprocess.check_output(['node', str(here / 'bin/playground-site.js'),
                             '--names', *guard_sources], text=True))
    provenance = dict(showcase=record['showcase']['revision'], compiler=record['theory']['revision'],
        judge=record['judge']['revision'], compiler_primitive=record['theory']['files'][primitive],
        judge_primitive=record['judge']['primitive_sha256'])
    definitions = [('Primitive.swift', cache / 'theory' / primitive),
                   ('Spectrum.swift', cache / 'showcase/Sources/DocumentKit/Spectrum.swift')]
    for tab in entries:
        with tempfile.TemporaryDirectory(prefix='gate-playground-') as temp:
            workspace = Path(temp) / 'source'
            shutil.copytree(cache / 'showcase', workspace)
            world = workspace / 'Worlds/Playground' / tab['world']
            if tab['world'] == 'Site':
                # Manifest is this world's pinned input too, not a second editable copy.
                (world / 'Manifest.swift').unlink()
            if tab.get('generated'):
                # The generator reads the pinned organization page, and its
                # geometry stays in that world's dictionary after the split.
                generated = subprocess.check_output(['node', str(here / 'bin/playground-site.js'),
                    str(source / 'Organization/Organization.swift'), '--company'])
                (world / 'Company.swift').write_bytes(generated)
                shutil.copytree(source / 'Organization/Dictionary', world / 'Dictionary')
                manifest = (world / 'gate.manifest.swift').read_text()
                manifest += '\npublic enum CarriedFile: Role {}\npublic enum TheGeometry: Mine {\n    public typealias Kind = CarriedFile\n}\nextension TheGeometry {\n    public static var typeName: String { "Dictionary/Design.swift" }\n}\n'
                (world / 'gate.manifest.swift').write_text(manifest)
            internal = world / '.gate'
            internal.mkdir(exist_ok=True)
            shutil.copyfile(cache / 'worlds.from', internal / 'worlds.from')
            paths, texts = [], []
            fragments = ([dict(path='Company.swift', marker='// gate-company-data')] if tab.get('generated') else
                [dict(path='Organization.swift', marker='// ── the data the page reads')] if tab['world'] == 'Organization' else [])
            for name, path in definitions:
                data = path.read_bytes()
                (internal / name).write_bytes(data)
                paths.append(dict(path='.gate/' + name, sha256=hashlib.sha256(data).hexdigest()))
                texts.append(dict(name=name, text=data.decode()))
            definitions_record = internal / 'forms-definitions.json'
            if definitions_record.exists() and json.loads(definitions_record.read_text()).get('format') == 2:
                authored = json.loads(definitions_record.read_text())
                authored['plain_fragments'] = fragments
                definitions_record.write_text(json.dumps(authored, indent=2) + '\n')
            else:
                definitions_record.write_text(json.dumps(dict(
                    revision=record['theory']['revision'], files=paths, plain_fragments=fragments,
                    shelf_overrides=False), indent=2) + '\n')
            context = dict(pin=record['showcase']['revision'], world=tab['id'], tab=tab,
                definitions=texts, carried=[], catalog=catalog, provenance=provenance, guard_names=guard_names,
                compiler=record['theory'], judge=record['judge'], plain_fragments=fragments,
                drawing=dict(case_id=tab['id']),
                generated_from='Organization/Organization.swift' if tab.get('generated') else None)
            # Carried paths are taken from /files by publish, not guessed here.
            publish(str(world), str(out / 'playground' / tab['id']), context)
    shutil.copyfile(cache / 'worlds.from', out / 'worlds.from')
    shutil.copyfile(cache / 'from', out / 'worlds-source.json')
    (out / 'playground').mkdir(exist_ok=True)
    # The door is the same bench on Read me, including its complete assets and
    # storage scope. No catalog, no second page template, no strip of tabs.
    for path in (out / 'playground/readme').iterdir():
        target = out / 'playground' / path.name
        if path.is_dir():
            shutil.copytree(path, target, dirs_exist_ok=True)
        else:
            shutil.copyfile(path, target)
    (out / 'playground/tabs.json').write_text(json.dumps(tabs, indent=2) + '\n')
