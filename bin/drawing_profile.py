"""Static transport for the same DrawingProfileReaderV1 used by the live bench.

This does not read a palette or choose a profile. Serve supplies the declared
input plan. The shared browser reader supplies its CSS and evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request


def publish(here, site, page, plan, port):
    if plan['status'] == 'none':
        return None
    base = 'http://127.0.0.1:' + str(port)
    result = subprocess.run(['node', str(Path(here) / 'bin/drawing-profile.js'), base],
                            input=json.dumps(plan), capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip())
    profile = json.loads(result.stdout)
    css = profile.pop('css')
    assets = Path(site) / 'assets/drawing'
    for item in profile['assets']:
        data = urllib.request.urlopen(base + '/drawing-assets/' + item['sha256']).read()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('drawing input delivery changed: ' + item['sha256'])
        dest = assets / item['sha256'] / item['name']
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != data:
            raise ValueError(str(dest) + ': conflicting content address')
        dest.write_bytes(data)
    css_hash = hashlib.sha256(css.encode()).hexdigest()
    folder = assets / css_hash
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'drawing.css').write_text(css)
    (folder / 'profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    index_path = Path(site) / '.drawing-profiles.json'
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    index[css_hash] = dict(plan=plan, receipt=profile, consumers=[])
    index_path.write_text(json.dumps(index, indent=2) + '\n')
    plan['asset_urls'] = {item['sha256']: Path(os.path.relpath(assets / item['sha256'] / item['name'], page)).as_posix()
                          for item in profile['assets']}
    return dict(href=Path(os.path.relpath(folder / 'drawing.css', page)).as_posix(), css=css,
                receipt=profile, css_sha256=css_hash)



def begin(site):
    """Replace only the last publisher's known, hash-addressed output files."""
    import re
    site = Path(site);record = site / '.drawing-profiles.json'
    if not record.exists():
        return
    index = json.loads(record.read_text());managed = set()
    for key, row in index.items():
        if not re.fullmatch('[0-9a-f]{64}', key):
            raise ValueError('invalid previous drawing resource key')
        managed.update([site / 'assets/drawing' / key / 'drawing.css', site / 'assets/drawing' / key / 'profile.json'])
        for item in row['receipt']['assets']:
            if not re.fullmatch('[0-9a-f]{64}', item['sha256']) or item['name'] not in ('font.ttf', 'license.txt'):
                raise ValueError('invalid previous drawing asset')
            managed.add(site / 'assets/drawing' / item['sha256'] / item['name'])
    for path in managed:
        path.unlink(missing_ok=True)
    record.unlink()


def finish(site):
    """Relocate every consumer after ordinary publication aliases are laid out."""
    from bench_csp import stamp_csp
    import re
    site = Path(site)
    index = json.loads((site / '.drawing-profiles.json').read_text()) if (site / '.drawing-profiles.json').exists() else {}
    for row in index.values():
        row['consumers'] = []
    for page in site.rglob('*.html'):
        text = page.read_text()
        match = re.search(r'const SNAP = ([^\n]+);', text)
        if not match:
            continue
        snap = json.loads(match[1]);plan = json.loads(snap.get('/drawing-profile', '{"status":"none"}'))
        if plan.get('status') == 'none':
            continue
        options = [(key, row) for key, row in index.items() if row['plan']['profile']['sha256'] == plan['profile']['sha256']]
        if len(options) != 1:
            raise ValueError(str(page) + ': no unique drawing resource')
        key, row = options[0];profile = row['receipt']
        href = Path(os.path.relpath(site / 'assets/drawing' / key / 'drawing.css', page.parent)).as_posix()
        text = re.sub(r'(<link rel="stylesheet" data-drawing-profile href=")[^"]+(">)', lambda m:m[1]+href+m[2], text)
        plan['asset_urls'] = {item['sha256']: Path(os.path.relpath(site / 'assets/drawing' / item['sha256'] / item['name'], page.parent)).as_posix() for item in profile['assets']}
        snap['/drawing-profile'] = json.dumps(plan)
        from bench_csp import script_json
        match = re.search(r'const SNAP = ([^\n]+);', text)
        text = text[:match.start(1)] + script_json(snap) + text[match.end(1):]
        page.write_text(stamp_csp(text))
        if (page.parent / 'snapshots.json').exists():
            (page.parent / 'snapshots.json').write_text(json.dumps(snap, indent=2))
        row['consumers'].append(page.relative_to(site).as_posix())
    if index:
        (site / '.drawing-profiles.json').write_text(json.dumps(index, indent=2) + '\n')


def audit(site):
    """Recompute the shared CSS from recorded input bytes and the same reader."""
    import re
    site = Path(site);record = site / '.drawing-profiles.json'
    if not record.exists():
        return {}
    index = json.loads(record.read_text());expected = {};used = set();asset_files = set()
    here = Path(__file__).resolve().parent.parent
    for key, row in index.items():
        result = subprocess.run(['node', str(here / 'bin/drawing-profile.js'), '--assets', str(site / 'assets/drawing')], input=json.dumps(row['plan']), capture_output=True, text=True)
        if result.returncode:
            raise ValueError('drawing profile: ' + result.stderr.strip())
        profile = json.loads(result.stdout);css = profile['css']
        if hashlib.sha256(css.encode()).hexdigest() != key:
            raise ValueError(str(record) + ': regenerated CSS differs')
        sheet = site / 'assets/drawing' / key / 'drawing.css'
        if not sheet.exists() or sheet.read_text() != css:
            raise ValueError(str(sheet.relative_to(site)) + ': differs from the declared drawing profile')
        expected[sheet.resolve()] = css
        asset_files.update([sheet.resolve(), (sheet.parent / 'profile.json').resolve()])
        for item in profile['assets']:
            asset = site / 'assets/drawing' / item['sha256'] / item['name']
            if not asset.exists() or hashlib.sha256(asset.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError(str(asset.relative_to(site)) + ': resource hash differs')
            asset_files.add(asset.resolve())
        for name in row['consumers']:
            page = site / name
            if not page.exists():
                raise ValueError(name + ': missing drawing consumer')
            href = Path(os.path.relpath(sheet, page.parent)).as_posix()
            links = re.findall(r'<link rel="stylesheet" data-drawing-profile href="([^"]+)">', page.read_text())
            if links != [href] or name in used:
                raise ValueError(name + ': missing or extra drawing consumer')
            used.add(name)
    for page in site.rglob('*.html'):
        for name in ('drawing-profile.js', 'drawing-fonts.json'):
            asset = page.parent / name
            if not asset.exists() or asset.read_bytes() != (here / 'bin' / name).read_bytes():
                raise ValueError(str(asset.relative_to(site)) + ': differs from the installed profile reader')
        if 'data-drawing-profile href=' in page.read_text() and page.relative_to(site).as_posix() not in used:
            raise ValueError(str(page.relative_to(site)) + ': extra drawing consumer')
    actual = {p.resolve() for p in (site / 'assets/drawing').rglob('*') if p.is_file()}
    if actual != asset_files:
        raise ValueError('assets/drawing: missing or extra resource')
    # A renamed duplicate elsewhere on the site is still the same resource twice.
    named = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in asset_files}
    protected = {h for p, h in named.items() if p.name in ('font.ttf', 'license.txt')}
    found = {h: 0 for h in protected}
    for path in site.rglob('*'):
        if path.is_file():
            h = hashlib.sha256(path.read_bytes()).hexdigest()
            if h in found:
                found[h] += 1
    if any(n != 1 for n in found.values()):
        raise ValueError('drawing resources: font/license must occur once by their bytes')
    from bench_styles import Styles
    sheets = [p.read_text() for p in site.rglob('*.css')]
    for page in site.rglob('*.html'):
        styles = Styles(); styles.feed(page.read_text())
        sheets.extend(styles.rules)
    faces = sum(len(re.findall(r'@font-face\b', re.sub(r'/\*.*?\*/', '', css, flags=re.S), re.I)) for css in sheets)
    font_hashes = {item['sha256'] for row in index.values() for item in row['receipt']['assets'] if item['name'] == 'font.ttf'}
    if faces != len(font_hashes):
        raise ValueError('drawing resources: @font-face must occur once per font hash')
    return expected
