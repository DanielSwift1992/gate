"""Publish the site's declared tabs over the world's own manifest and sources."""
import hashlib
import html
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
    # Company is the generator's seed, not an invented tab. Site remains an
    # inspectable world, including Palette and its outstanding requirements.
    entries = tabs + [dict(id='company', world='Company', title='Company seed', group='source', caption='Seed source', generated=False),
                      dict(id='site', world='Site', title='Site', group='source', caption='Manifest and Palette', generated=False)]
    nav = '<nav id="world-tabs" aria-label="Playground worlds">'
    group = None
    for tab in tabs:
        if tab['group'] != group:
            group = tab['group']
            nav += '<span>' + html.escape(group) + ': </span>'
        nav += '<a href="../' + tab['id'] + '/index.html" title="' + html.escape(tab.get('shown', tab['world']) + ' · ' + tab['caption'], quote=True) + '">' + html.escape(tab['title']) + '</a>'
    nav += '</nav>'
    primitive = 'Sources/VerificationIsIdentification/Primitive.swift'
    compiler_sha = record['theory']['files'][primitive]
    judge_sha = record['judge']['primitive_sha256']
    provenance = '<div id="world-provenance">showcase ' + record['showcase']['revision']
    provenance += ' · compiler ' + record['theory']['revision'] + ' Primitive sha256 ' + compiler_sha
    provenance += ' · judge ' + record['judge']['revision'] + ' Primitive sha256 ' + judge_sha
    provenance += (' · same Primitive bytes' if compiler_sha == judge_sha else ' · DIFFERENT Primitive bytes')
    provenance += ' · page bodies: compiled at the source pin; edits have not been checked by Swift'
    provenance += ' · <a href="../../worlds.from">all input hashes</a> · <a href="../../worlds-source.json">public/local source</a>'
    provenance += ' · <a href="../company/index.html">company seed</a> · <a href="../site/index.html">site requirements</a></div>'
    definitions = [('Primitive.swift', cache / 'theory' / primitive),
                   ('Spectrum.swift', cache / 'showcase/Sources/DocumentKit/Spectrum.swift')]
    for tab in entries:
        with tempfile.TemporaryDirectory(prefix='gate-playground-') as temp:
            world = Path(temp) / tab['id']
            shutil.copytree(source / tab['world'], world)
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
            internal.mkdir()
            shutil.copyfile(cache / 'worlds.from', internal / 'worlds.from')
            paths, texts = [], []
            fragments = ([dict(path='Company.swift', marker='// gate-company-data')] if tab.get('generated') else
                [dict(path='Organization.swift', marker='// ── the data the page reads')] if tab['world'] == 'Organization' else [])
            for name, path in definitions:
                data = path.read_bytes()
                (internal / name).write_bytes(data)
                paths.append(dict(path='.gate/' + name, sha256=hashlib.sha256(data).hexdigest()))
                texts.append(dict(name=name, text=data.decode()))
            (internal / 'forms-definitions.json').write_text(json.dumps(dict(
                revision=record['theory']['revision'], files=paths, plain_fragments=fragments,
                shelf_overrides=False), indent=2) + '\n')
            context = dict(pin=record['showcase']['revision'], world=tab['id'], tab=tab,
                definitions=texts, carried=[], navigation=nav.replace('href="../' + tab['id'] + '/index.html"',
                    'aria-current="page" href="../' + tab['id'] + '/index.html"'), provenance_html=provenance,
                compiler=record['theory'], judge=record['judge'], plain_fragments=fragments)
            if tab.get('generated'):
                context['provenance_html'] = provenance.replace(
                    'page bodies: compiled at the source pin; edits have not been checked by Swift',
                    'generated source: not checked by Swift at these pins')
            # Carried paths are taken from /files by publish, not guessed here.
            publish(str(world), str(out / 'playground' / tab['id']), context)
    shutil.copyfile(cache / 'worlds.from', out / 'worlds.from')
    shutil.copyfile(cache / 'from', out / 'worlds-source.json')
    (out / 'playground').mkdir(exist_ok=True)
    cards, group = '', None
    for tab in tabs:
        if tab['group'] != group:
            if group is not None:
                cards += '</div></section>'
            group = tab['group']
            cards += '<section><h2>' + html.escape(group) + '</h2><div class="world-grid">'
        cards += ('<a class="world-card" href="' + tab['id'] + '/index.html"><h3>'
            + html.escape(tab['title']) + '</h3><p>' + html.escape(tab['caption'])
            + '</p><code>' + html.escape(tab.get('shown', tab['world'])) + '</code></a>')
    cards += '</div></section>'
    origin = '<dl>'
    for label, value in [('Showcase', record['showcase']['revision']),
            ('Compiler', record['theory']['revision']), ('Judge', record['judge']['revision']),
            ('Compiler Primitive · SHA-256', compiler_sha), ('Judge Primitive · SHA-256', judge_sha)]:
        origin += '<dt>' + label + '</dt><dd><code>' + html.escape(value) + '</code></dd>'
    origin += '</dl>'
    (out / 'playground/index.html').write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Playground · gate</title><link rel="stylesheet" href="../ladder.css">
<style>
:root{font-size:13px;--textline:1.45rem;--u:calc(var(--textline)/10)}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:var(--speech)}
main{max-width:1000px;margin:auto;padding:var(--wide)}
header{border-bottom:1px solid var(--line);padding-bottom:var(--wide)}
h1{font:var(--headline)}h2{font:var(--rubric);text-transform:uppercase;letter-spacing:.08em}
h3{font:var(--headsmall);margin:0}p{font:var(--speech);line-height:1.6}
a{color:var(--action)}code{font:var(--fact);overflow-wrap:anywhere}
section{margin:var(--wide) 0}.world-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:var(--apart)}
.world-card{display:block;padding:var(--wide);border:1px solid var(--line);border-radius:var(--apart);text-decoration:none}
.world-card p,.world-card code{color:var(--ink)}.world-card:hover,.world-card:focus-visible{background:var(--mist)}
footer{border-top:1px solid var(--line);padding-top:var(--wide)}
dt{font:var(--caption);margin-top:var(--apart)}dd{margin:var(--near) 0}
</style><main><header><p>gate · playground</p><h1>A world you can read, change and ask</h1>
<p>Each bench opens the pinned world's files. Your draft and its verdict stay in this browser, including refusals.</p></header>'''
        + cards + '<section><h2>Source worlds</h2><p><a href="company/index.html">Company seed</a> · '
        + '<a href="site/index.html">Manifest and Palette · 17 count readings</a></p></section>'
        + '<footer><h2>Where these worlds came from</h2>' + origin
        + '<p>Page bodies were compiled at the source pin. Reader edits and the generated company have not been checked by Swift.</p>'
        + '<p><a href="../worlds.from">All input hashes</a> · <a href="../worlds-source.json">Public/local source</a>'
        + ' · <a href="../index.html">The gate demo</a></p></footer></main></html>')
    (out / 'playground/tabs.json').write_text(json.dumps(tabs, indent=2) + '\n')
    index = out / 'index.html'
    index.write_text(index.read_text().replace('reset the demo</a>', 'reset the demo</a> · <a href="playground/index.html">playground worlds</a>', 1))
