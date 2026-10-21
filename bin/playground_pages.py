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
    # Both the catalog record and the ordinary world it Reads have a door.
    catalog['destinations'].update({tab['reads']: tab['id'] for tab in tabs})
    primitive = 'Sources/VerificationIsIdentification/Primitive.swift'
    guard_sources = [str(cache / 'theory' / name) for name in record['theory']['files']]
    guard_sources += [str(cache / 'showcase' / name) for name in record['showcase']['files']
                     if name.startswith('Sources/') and name.endswith('.swift')]
    guard_names = json.loads(subprocess.check_output(['node', str(here / 'bin/playground-site.js'),
                             '--names', *guard_sources], text=True))
    provenance = dict(showcase=record['showcase']['revision'], compiler=record['theory']['revision'],
        judge=record['judge']['revision'], compiler_primitive=record['theory']['files'][primitive],
        judge_primitive=record['judge']['primitive_sha256'])
    for tab in entries:
        with tempfile.TemporaryDirectory(prefix='gate-playground-') as temp:
            workspace = Path(temp) / 'source'
            shutil.copytree(cache / 'showcase', workspace)
            world = workspace / 'Worlds/Playground' / tab['world']
            internal = world / '.gate'
            internal.mkdir(exist_ok=True)
            shutil.copyfile(cache / 'worlds.from', internal / 'worlds.from')
            # The owner already declared the source composition. Publication
            # takes that record without writing definitions or choosing a suffix.
            authored = json.loads((internal / 'forms-definitions.json').read_text())
            inputs = {f['row']: f for f in authored['files']}
            references = list(dict.fromkeys(ref for language in authored.get('languages', {}).values()
                                             for ref in language.get('definitions', [])))
            definition_paths = [inputs[ref]['path'] for ref in references]
            catalog_input = next(f for f in authored['files']
                                 if f['source_path'] == 'Worlds/Playground/Site/Manifest.swift')
            own_catalog = dict(catalog, revision=catalog_input['revision'], sha256=catalog_input['sha256'],
                               source=catalog_input['path'])
            context = dict(pin=record['showcase']['revision'], world=tab['id'], tab=tab,
                definition_paths=definition_paths, carried=[], catalog=own_catalog, provenance=provenance, guard_names=guard_names,
                compiler=record['theory'], judge=record['judge'],
                drawing=dict(case_id=tab['id']))
            # Carried paths are taken from /files by publish, not guessed here.
            ladder = publish(str(world), str(out / 'playground' / tab['id']), context)
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
    return ladder
