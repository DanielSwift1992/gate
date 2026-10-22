#!/usr/bin/env python3
"""The transferred vectors, and the actual published benches that read them."""
import importlib.util
import hashlib
from html.parser import HTMLParser
import json
import os
import runpy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent.parent


def run():
    runpy.run_path(str(HERE / 'tests/examples.py'))['run']()
    runpy.run_path(str(HERE / 'tests/publisher.py'))['run']()
    runpy.run_path(str(HERE / 'tests/inputs-kind.py'))['run']()
    runpy.run_path(str(HERE / 'tests/publication.py'))['run']()
    cache = Path(subprocess.check_output([str(HERE / 'bin/playground-worlds.sh')], text=True).strip())
    subprocess.run(['node', str(HERE / 'tests/drawing.js'), str(cache)], check=True)
    spec = importlib.util.spec_from_file_location('worlds', HERE / 'bin/playground-worlds.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = json.loads((cache / 'worlds.from').read_text())
    with tempfile.TemporaryDirectory(prefix='gate-worlds-check-') as temp:
        # A corrupt warm cache must refuse before a builder gets its path.
        # Keep the shared cache intact; this is the very checker the door calls.
        root = Path(temp) / 'corrupt'
        selected = next(iter(record['showcase']['files']))
        target = root / selected
        target.parent.mkdir(parents=True)
        shutil.copyfile(cache / 'showcase' / selected, target)
        module.checked(root, {selected: record['showcase']['files'][selected]})
        target.write_bytes(target.read_bytes() + b' ')
        try:
            module.checked(root, {selected: record['showcase']['files'][selected]})
            raise AssertionError('a changed cached file was accepted')
        except ValueError as e:
            assert 'sha256' in str(e)
        scale_input = 'Worlds/Playground/Scale/Company.swift'
        try:
            module.checked(Path(temp) / 'missing-scale', {scale_input: record['showcase']['files'][scale_input]})
            raise AssertionError('a missing materialized input was regenerated or accepted')
        except ValueError as e:
            assert scale_input in str(e) and 'missing recorded file' in str(e)
        catalog = cache / 'showcase/Worlds/Playground/Site/Manifest.swift'
        legacy = Path(temp) / 'legacy-catalog.swift'
        legacy.write_text(catalog.read_text().replace('Reads = ScaleWorld', 'Reads = GeneratedText'))
        result = subprocess.run(['node', str(HERE / 'bin/playground-site.js'), str(legacy)], capture_output=True, text=True)
        assert result.returncode != 0 and 'unreadable tab ScaleTab' in result.stderr
        assert not (HERE / 'bin/playground-company.js').exists()
        # Exercise the whole local door with an isolated git, including a
        # warm hit and a wrong HEAD. No user's checkout is changed for this.
        local = Path(temp) / 'local'
        local.mkdir()
        subprocess.run(['git', '-C', str(local), 'init', '-q'], check=True)
        (local / 'sample.swift').write_bytes(b'public enum Sample {}\n')
        subprocess.run(['git', '-C', str(local), 'add', 'sample.swift'], check=True)
        subprocess.run(['git', '-C', str(local), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@test',
                        'commit', '-qm', 'fixture: one recorded file'], check=True)
        pin = subprocess.check_output(['git', '-C', str(local), 'rev-parse', 'HEAD'], text=True).strip()
        fixture = Path(temp) / 'door'
        (fixture / 'bin').mkdir(parents=True)
        test_record = {kind: dict(revision=pin, files={'sample.swift': hashlib.sha256((local / 'sample.swift').read_bytes()).hexdigest()})
                       for kind in ('showcase', 'theory')}
        (fixture / 'bin/playground-worlds.from').write_text(json.dumps(test_record))
        old_here, old_record, env = module.HERE, module.RECORD, dict(os.environ)
        try:
            module.HERE, module.RECORD = fixture, fixture / 'bin/playground-worlds.from'
            for key in ('SHOWCASE_SOURCE', 'VI_THEORY_PATH'):
                os.environ[key] = str(local)
            laid = module.materialize()
            assert all(v.startswith('local: ') for v in json.loads((laid / 'from').read_text())['sources'].values())
            assert module.materialize() == laid
            (laid / 'showcase/sample.swift').write_bytes(b'corrupted\n')
            try:
                module.materialize()
                raise AssertionError('the local door accepted changed cached bytes')
            except ValueError as e:
                assert 'sha256' in str(e)
            shutil.rmtree(laid)
            test_record['showcase']['revision'] = '0' * 40
            module.RECORD.write_text(json.dumps(test_record))
            try:
                module.materialize()
                raise AssertionError('the local door accepted a different HEAD')
            except ValueError as e:
                assert 'local HEAD' in str(e)
        finally:
            module.HERE, module.RECORD = old_here, old_record
            os.environ.clear()
            os.environ.update(env)
        owner_records = list((cache / 'showcase/Worlds/Playground').glob('*/.gate/forms-definitions.json'))
        assert len(owner_records) == 12
        assert all(json.loads(p.read_text())['plain_fragments'] == [] for p in owner_records)
        def prepared(name):
            workspace = Path(temp) / ('native-' + name)
            shutil.copytree(cache / 'showcase', workspace)
            world = workspace / 'Worlds/Playground' / name
            internal = world / '.gate'
            internal.mkdir(exist_ok=True)
            shutil.copyfile(cache / 'worlds.from', internal / 'worlds.from')
            return world
        def status(world):
            answer = subprocess.run([str(HERE / 'gate'), 'status', '--json'], cwd=world,
                                    capture_output=True, text=True, check=False)
            return json.loads(answer.stdout)
        light = prepared('Light')
        assert status(light)['verdict'] == 'holds'
        declaration = light / 'Dictionary/Light.swift'
        original = declaration.read_text()
        declaration.write_text(original.replace('public typealias HalfFact =', 'public typealias budget =').replace(
            '    public typealias Vertical = Twice<Lit1>\n}', '    public typealias Vertical = Lit1\n}'))
        named = status(light)
        assert named['verdict'] == 'refused' and not named.get('unsupported')
        assert any('budget' in r['claim'] for r in named['refusals'])
        declaration.write_text(original)
        spec_path = light / '.gate/forms-definitions.json'
        spec = json.loads(spec_path.read_text())
        next(r for r in spec['files'] if r['row'] == 'ThePrimitive')['sha256'] = '0' * 64
        spec_path.write_text(json.dumps(spec, indent=2) + '\n')
        broken = status(light)
        assert broken['verdict'] == 'refused' and any(r['address'].startswith('.gate/forms-definitions.json:') for r in broken['refusals'])
        (light / '.gate/forms-definitions.json').unlink()
        assert status(light)['verdict'] == 'refused'
        organization = prepared('Organization')
        assert status(organization)['verdict'] == 'holds'
        source = organization / 'Organization.swift'
        original_data = source.read_text()
        source.write_text(original_data.replace('public typealias Home = Finance', 'public typealias Home = Sales', 1))
        lie = status(organization)
        assert lie['verdict'] == 'refused' and all(r['address'].startswith('Organization.swift:') for r in lie['refusals'])
        # A pure WorldFile needs no page/data delimiter. Preserve the company
        # negative above, then remove the now descriptive comment only.
        source.write_text(original_data.replace('// ── the data the page reads', '// data follows'))
        assert status(organization)['verdict'] == 'holds'
        assert json.loads((organization / '.gate/forms-definitions.json').read_text())['plain_fragments'] == []
        # The new palette preserves the old integer relations and each of its
        # seventeen slack+1 controls refuses in the native court.
        subprocess.run([sys.executable, str(cache / 'showcase/Checks/Playground/palette-count.py'),
                        '--theory', str(cache / 'theory'), '--judge', str(HERE / 'bin/gate-judge')], check=True)
        site = Path(temp) / 'site'
        # A historical checkout is deliberately unavailable to the product.
        # This also refuses an accidental return of the old mandatory local door.
        clean_build = dict(os.environ, PLAYGROUND_SOURCE=str(Path(temp) / 'no-historical-checkout'))
        subprocess.run([sys.executable, str(HERE / 'bin/build-pages.py'), str(site),
                        '--source', str(HERE / 'examples/codeowners'), '--worlds'], check=True, env=clean_build)
        assert 'baseline' not in record and not (cache / 'baseline').exists()
        assert 'baseline' not in json.loads((site / 'worlds-source.json').read_text())['sources']
        for page in site.rglob('*.html'):
            assert 'roadtest=1' not in page.read_text() and 'ROAD ALL GREEN' not in page.read_text(), page
        # Only migration tests ask for the historical source. The finished
        # site's current guards and lint are read from its delivered assets.
        history = runpy.run_path(str(HERE / 'tests/playground-baseline.py'))['materialize']()
        csp_spec = importlib.util.spec_from_file_location('bench_csp', HERE / 'bin/bench_csp.py')
        csp = importlib.util.module_from_spec(csp_spec)
        csp_spec.loader.exec_module(csp)
        class Handlers(HTMLParser):
            def handle_starttag(self, tag, attrs):
                assert not any(key.lower().startswith('on') for key, _ in attrs), (tag, attrs)
        for page in site.rglob('*.html'):
            html = page.read_text()
            assert csp.stamp_csp(html) == html, str(page) + ': CSP must cover the final programs'
            assert "script-src-attr 'none'" in html
            Handlers().feed(html)
        subprocess.run(['node', str(HERE / 'tests/playground.js'), str(cache), str(site), str(history)], check=True)
        subprocess.run(['node', str(HERE / 'tests/playground-storage.js'), str(site)], check=True)
        scale = json.loads((cache / 'showcase/Checks/Playground/scale-generation.json').read_text())
        assert scale['storage'] == 'versioned' and scale['parameters'] == dict(count=12800, seed=0, part_size=200)
        for output in scale['outputs']:
            data = (cache / 'showcase' / output['path']).read_bytes()
            assert len(data) == output['bytes'] and hashlib.sha256(data).hexdigest() == output['sha256']
        scale_snap = json.loads((site / 'playground/scale/snapshots.json').read_text())
        for name in ('Company.swift', 'ScalePages.swift', 'Dictionary/Design.swift', 'gate.manifest.swift'):
            assert scale_snap['/world?f=' + name] == (cache / 'showcase/Worlds/Playground/Scale' / name).read_text(), name
        for part in scale['company_files']:
            name = str(Path(part).relative_to('Worlds/Playground/Scale'))
            assert scale_snap['/world?f=' + name] == (cache / 'showcase' / part).read_text(), name
        scale_context = json.loads((site / 'playground/scale/world.json').read_text())
        assert scale_context['tab']['world'] == 'Scale' and scale_context['tab']['reads'] == 'ScaleWorld'
        assert 'plain_fragments' not in scale_context
        subprocess.run(['node', str(HERE / 'tests/playground-scale.js'), str(site), str(cache / 'showcase')], check=True)
        subprocess.run(['node', str(HERE / 'tests/playground-ui.js'), str(site)], check=True)
        door = (site / 'playground/index.html').read_bytes()
        import re
        canonical = (site / 'playground/readme/index.html').read_text()
        def normal_alias(text):
            text = re.sub(r'(?:\.\./)*assets/drawing/', 'ASSETS/', text)
            return re.sub(r"'sha256-[^']+'", 'HASH', text)
        assert normal_alias(door.decode()) == normal_alias(canonical)
        # Gate owns its root; the showcase entry is confined to playground/.
        # Read the actual delivery, not a second expected template.
        root_page = (site / 'index.html').read_text()
        root_snap = json.loads(re.search(r'const SNAP = ([^\n]+);', root_page)[1])
        root_files = json.loads(root_snap['/files'])
        assert 'ownership.swift' in root_files['forms']
        assert root_snap['/world?f=ownership.swift'] == (HERE / 'examples/codeowners/ownership.swift').read_text()
        root_verdict = json.loads(root_snap['/verdict?f=ownership.swift'])
        assert len(root_verdict['refusals']) == 1 and root_verdict['refusals'][0]['address'] == 'ownership.swift:89'
        assert 'const CONTEXT = null;' in root_page
        assert b'world-card' not in door and b'id="worldlist"' not in door
        sys.path.insert(0, str(HERE / 'bin'))
        from bench_styles import audit_site
        ladder = (site / 'ladder.css').read_text()
        assert audit_site(site, ladder)['pages'] == 14
        layout_law = runpy.run_path(str(HERE / 'tests/bench-layout.py'))
        layout_law['run'](site)
        profile_law = runpy.run_path(str(HERE / 'tests/drawing-profile.py'))
        profile_law['run'](cache, site)
        # The same law must refuse a second palette on EACH finished page.
        # Font and gap controls exercise the CSS branch independently.
        def refused(path, addition):
            original = path.read_text()
            try:
                path.write_text(original + addition)
                try:
                    audit_site(site, ladder)
                except ValueError as e:
                    assert str(path.relative_to(site)) in str(e), str(e)
                else:
                    raise AssertionError(str(path) + ': a private interface value was accepted')
            finally:
                path.write_text(original)
        for page in site.rglob('*.html'):
            refused(page, '<style>.probe{color:#123456}</style>')
        for value in ['font:17px fantasy', 'line-height:1.6', 'padding:7px', 'padding:7PX', 'COLOR:RED', 'color:oklch(50% .1 90)', 'color:rebeccapurple', 'background:CanvasText', 'text-decoration:underline oklch(50% .1 90)', 'column-rule:1px solid rebeccapurple', 'filter:drop-shadow(0 0 1px oklch(50% .1 90))', '-webkit-text-stroke:1px oklch(50% .1 90)', 'font:var(--not-a-register)']:
            refused(site / 'playground/basics/codemirror.css', '.probe{' + value + '}')
        refused(site / 'playground/basics/ladder.css', ':root{--ink:#123456}')
        tabs = json.loads((site / 'playground/tabs.json').read_text())
        assert [t['id'] for t in tabs] == ['readme', 'organization', 'scale', 'basics', 'writer', 'buttons', 'light', 'atom', 'rules', 'faq', 'company', 'site']
        assert (site / 'worlds.from').read_bytes() == (HERE / 'bin/playground-worlds.from').read_bytes()
        assert record['theory']['files']['Sources/VerificationIsIdentification/Primitive.swift'] == record['judge']['primitive_sha256']
        assert all((site / 'playground' / t['id'] / 'index.html').is_file() for t in tabs)
    print('PLAYGROUND ALL GREEN: pinned inputs, twelve worlds, native/wasm, snapshots and isolated storage')


if __name__ == '__main__':
    run()
