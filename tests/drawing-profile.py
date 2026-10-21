"""The delivered owner CSS keeps one resource and its exact consumers."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]


def run(cache, site):
    sys.path.insert(0, str(ROOT / 'bin'))
    from drawing_profile import audit
    assert audit(site)
    subprocess.run(['node',str(ROOT/'tests/drawing-status.js'),str(site)],check=True)
    index = json.loads((Path(site) / '.drawing-profiles.json').read_text())
    row = next(iter(index.values()))
    page = Path(site) / row['consumers'][0];text = page.read_text()
    def rejected(label, apply, undo):
        apply()
        try:
            try:
                audit(site)
            except ValueError:
                pass
            else:
                raise AssertionError(label + ': accepted')
        finally:
            undo()
    rejected('missing consumer', lambda:page.write_text(text.replace('data-drawing-profile href=', 'data-unused href=', 1)), lambda:page.write_text(text))
    rejected('extra consumer', lambda:page.write_text(text.replace('<link rel="stylesheet" data-drawing-profile', '<link rel="stylesheet" data-drawing-profile href="extra.css"><link rel="stylesheet" data-drawing-profile', 1)), lambda:page.write_text(text))
    font = next(a for a in row['receipt']['assets'] if a['name'] == 'font.ttf')
    src = Path(site) / 'assets/drawing' / font['sha256'] / 'font.ttf';duplicate = Path(site) / 'renamed-font.bin'
    rejected('renamed duplicate', lambda:shutil.copyfile(src, duplicate), lambda:duplicate.unlink())
    rejected('extra face', lambda:page.write_text(text + '<style>@font-face{font-family:var(--sans);src:url("existing.ttf")}</style>'), lambda:page.write_text(text))
    print('DRAWING PROFILE GREEN: ordinary serve, renamed owner/colour/bindings, both themes, endpoints, font/metrics and resource controls')


if __name__ == '__main__':
    run(*sys.argv[1:])
