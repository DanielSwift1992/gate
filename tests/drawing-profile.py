"""A manifest chooses a profile; the same reader answers live and static."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def run(cache, site):
    with tempfile.TemporaryDirectory(prefix='gate-profile-') as tmp:
        owner = Path(tmp) / 'HarborPaint'
        owner.mkdir();world=owner
        source=Path(cache)/'showcase'
        host=owner
        palette=owner/'Palette.swift';profile=owner/'DrawingProfile.swift';metrics=owner/'metrics.swift';bindings=owner/'Bindings.swift'
        shutil.copyfile(source/'Worlds/Playground/Site/Palette.swift',palette)
        shutil.copyfile(source/'Worlds/Playground/Site/DrawingBindings.swift',bindings)
        shutil.copyfile(source/'Worlds/Playground/Site/DrawingProfile.swift',profile)
        shutil.copyfile(source/'Sources/DocumentKit/GeneratedFontMetrics.swift',metrics)
        shutil.copyfile(source/'Assets/InterVariable.ttf',owner/'font.ttf')
        shutil.copyfile(source/'Assets/InterLicense.txt',owner/'license.txt')
        manifest=owner/'gate.manifest.swift'
        def own_row(name,kind,path):
            return 'public enum '+name+': Mine {\n    public typealias Kind = '+kind+'\n}\nextension '+name+' {\n    public static var typeName: String { "'+path+'" }\n}\n'
        text='public protocol Role {}\npublic protocol Mine {}\npublic enum FormsFile: Role {}\npublic enum DrawingProfileReaderV1: Role {}\npublic enum DrawingProfileFile: Role {\n    public typealias Reader = DrawingProfileReaderV1\n}\npublic enum CarriedFile: Role {}\n'
        for name,kind,path in [('ThePalette','FormsFile','Palette.swift'),('TheBindings','CarriedFile','Bindings.swift'),('TheMetrics','CarriedFile','metrics.swift'),('TheFont','CarriedFile','font.ttf'),('TheLicense','CarriedFile','license.txt')]:
            text+=own_row(name,kind,path)
        manifest.write_text(text)
        declared = subprocess.run([str(ROOT / 'gate'), 'mine', 'DrawingProfile.swift',
                                   '--role', 'drawing-profile'], cwd=world,
                                  capture_output=True, text=True)
        assert declared.returncode == 0, declared.stdout + declared.stderr
        assert manifest.read_text().count('public enum DrawingProfileFile: Role') == 1
        assert manifest.read_text().count('Kind = DrawingProfileFile') == 1
        p0,f0=palette.read_text(),profile.read_text();m0=metrics.read_text();b0=bindings.read_text()
        sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
        server = subprocess.Popen([str(ROOT / 'gate'), 'serve', str(port), '--no-open'], cwd=world,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        base = 'http://127.0.0.1:' + str(port)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(base + '/files').read(); break
                except OSError:
                    time.sleep(.1)
            def ask():
                plan = json.loads(urllib.request.urlopen(base + '/drawing-profile').read())
                answer = subprocess.run(['node', str(ROOT / 'bin/drawing-profile.js'), base],
                                        input=json.dumps(plan), capture_output=True, text=True)
                return plan, answer
            status = json.loads(subprocess.run([str(ROOT / 'gate'), 'status', '--json'], cwd=world, capture_output=True, text=True).stdout)
            assert any(r['kind'] == 'DrawingProfileFile' and r['reader'] == 'DrawingProfileReaderV1' for r in status['readers'])
            plan, answer = ask()
            assert answer.returncode == 0, answer.stderr
            first = json.loads(answer.stdout)
            assert first['status'] == 'not-compared' and len(first['witnesses']) == 17
            assert {b['theme'] for b in first['bindings']} == {'light', 'dark'}
            # The v2 resolver must fetch a local Git dependency by its full pin.
            # A cached byte hash never grants a different source_path.
            import hashlib
            dependency=Path(tmp)/'dependency';dependency.mkdir()
            shutil.copyfile(owner/'font.ttf',dependency/'font.ttf')
            shutil.copyfile(Path(cache)/'theory/Sources/VerificationIsIdentification/Primitive.swift',dependency/'Primitive.swift')
            shutil.copyfile(source/'Sources/DocumentKit/Spectrum.swift',dependency/'Spectrum.swift')
            for command in [['git','init','-q'],['git','add','.'],['git','-c','user.name=Fixture','-c','user.email=fixture@test','commit','-qm','declared inputs']]:
                subprocess.run(command,cwd=dependency,check=True)
            revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=dependency,text=True).strip()
            original_manifest=manifest.read_text()
            pinned=original_manifest.replace('public enum TheFont: Mine {','public enum TheFont: Theirs {\n    public typealias At = DependencyPin')
            pinned+='\npublic protocol Theirs {}\npublic enum DependencyPin: Role {}\nextension DependencyPin {\n    public static var typeName: String { "'+str(dependency)+'@'+revision+'" }\n}\n'
            entries=[]
            for name,path in [('TheFont','font.ttf'),('ThePrimitive','.gate/inputs/Primitive.swift'),('TheSpectrum','.gate/inputs/Spectrum.swift')]:
                filename=path.split('/')[-1]
                if name!='TheFont':
                    pinned+=own_row(name,'CarriedFile',path).replace(': Mine {',': Theirs {\n    public typealias At = DependencyPin')
                entries.append(dict(row=name,path=path,repository=str(dependency),revision=revision,source_path=filename,sha256=hashlib.sha256((dependency/filename).read_bytes()).hexdigest()))
            record=owner/'.gate/forms-definitions.json';record.parent.mkdir()
            spec=dict(format=2,files=entries,languages={'Types':dict(definitions=['ThePrimitive','TheSpectrum'],namespace='Owner')})
            manifest.write_text(pinned);record.write_text(json.dumps(spec))
            _,cold=ask();assert cold.returncode==0,cold.stderr
            shelf = json.loads(urllib.request.urlopen(base + '/shelf').read())
            assert not any(name.endswith('font.ttf') for name in shelf['modules']), 'binary resource became a text page'
            entry=entries[0]
            target=ROOT/'bin/.inputs'/hashlib.sha256(str(dependency).encode()).hexdigest()/revision/(hashlib.sha256(b'font.ttf').hexdigest()+'-'+entry['sha256'])
            cached=target.read_bytes();target.write_bytes(b'changed')
            try:
                _,bad=ask();assert bad.returncode!=0 and 'cached input bytes' in bad.stderr
            finally:
                target.write_bytes(cached)
            entry['source_path']='missing-font.ttf';record.write_text(json.dumps(spec))
            try:
                _,bad=ask();assert bad.returncode!=0 and ('source_path' in bad.stderr or 'Git source bytes' in bad.stderr)
            finally:
                entry['source_path']='font.ttf';record.write_text(json.dumps(spec))
            record.unlink();manifest.write_text(original_manifest)
            # A3: a different host, palette filename, colour and binding names.
            palette.write_text(p0.replace('SurfaceCardColour', 'HarborPaper'))
            bindings.write_text(b0.replace('SurfaceCardColour','HarborPaper').replace('BindSurfaceCard','BindHarbor').replace('ThePalette::','PaintInput::'))
            profile.write_text(f0.replace('BindSurfaceCard', 'BindHarbor').replace('\"Inter\"', '\"Harbor Face\"').replace('TheDrawingProfile', 'IslandDrawing').replace('MeasuredFace', 'TypefaceUsed').replace('MeasuredTable', 'TypeTable').replace('Palette = ThePalette', 'Palette = PaintInput').replace('ThePalette::', 'PaintInput::'))
            palette.rename(host / 'HarborInk.swift');palette = host / 'HarborInk.swift'
            hm = manifest;h0 = hm.read_text();hm.write_text(h0.replace('Palette.swift', 'HarborInk.swift').replace('ThePalette', 'PaintInput'))
            changed, answer = ask();assert answer.returncode == 0, answer.stderr
            renamed = json.loads(answer.stdout)
            assert renamed['font']['family']=='Harbor Face' and renamed['font']['cssFamily']==first['font']['cssFamily']
            assert [(b['role'], b['theme'], b['css']) for b in first['bindings']] == [(b['role'], b['theme'], b['css']) for b in renamed['bindings']]
            palette.rename(host/'Palette.swift');palette=host/'Palette.swift'
            palette.write_text(p0);profile.write_text(f0);bindings.write_text(b0);manifest.write_text(h0)
            def refused(label, status, apply, undo):
                apply()
                try:
                    _, a = ask();assert a.returncode != 0, label + ': accepted'
                    error = json.loads(a.stderr.strip().splitlines()[-1])
                    assert error['status'] == status and ':' in error['address'], (label, error)
                finally:
                    undo()
            refused('missing dark', 'refused', lambda:profile.write_text(f0.replace('BindingReference7, ', '', 1)), lambda:profile.write_text(f0))
            refused('unknown field', 'refused', lambda:profile.write_text(f0.replace('public typealias Reader = Port', 'public typealias Reader = Port\n    public typealias Unexpected = Port',1)), lambda:profile.write_text(f0))
            refused('duplicate field', 'refused', lambda:profile.write_text(f0.replace('public typealias Reader = Port', 'public typealias Reader = Port\n    public typealias Reader = Port',1)), lambda:profile.write_text(f0))
            refused('wrong Legible endpoint', 'refused', lambda:bindings.write_text(b0.replace('public typealias Foreground = BindTextLight', 'public typealias Foreground = BindMutedLight', 1)), lambda:bindings.write_text(b0))
            font_hash = plan['inputs']['TheFont']['sha256']
            refused('false font hash', 'refused', lambda:profile.write_text(f0.replace(font_hash, '0'*64)), lambda:profile.write_text(f0))
            refused('wrong metrics', 'unsupported', lambda:metrics.write_text(m0.replace('"2048"', '"2049"', 1)), lambda:metrics.write_text(m0))
            refused('unknown face', 'unsupported', lambda:profile.write_text(f0.replace('"default"', '"different-face"')), lambda:profile.write_text(f0))
            font_file=owner/'font.ttf';font_bytes=font_file.read_bytes();other=font_bytes+b'changed-font'
            font_file.write_bytes(other);profile.write_text(f0.replace(font_hash,hashlib.sha256(other).hexdigest()))
            try:
                _,a=ask();assert a.returncode!=0 and json.loads(a.stderr)['status']=='unsupported'
            finally:
                font_file.write_bytes(font_bytes);profile.write_text(f0)

            manifest0 = manifest.read_text()
            manifest.write_text(manifest0.replace('Kind = DrawingProfileFile', 'Kind = CarriedFile'))
            try:
                no_profile, a = ask();assert no_profile['status'] == 'none' and json.loads(a.stdout)['reason'] == 'Drawing without a profile'
            finally:
                manifest.write_text(manifest0)
            # Live and static both consumed the same owner bytes and installed reader.
            index = json.loads((Path(site) / '.drawing-profiles.json').read_text())
            stored = next(iter(index.values()))['receipt']
            assert [(b['role'], b['theme'], b['css']) for b in first['bindings']] == [(b['role'], b['theme'], b['css']) for b in stored['bindings']]
            assert first['font'] == stored['font'] and first['reader'] == stored['reader']
        finally:
            server.terminate();server.wait()
    sys.path.insert(0, str(ROOT / 'bin'))
    from drawing_profile import audit
    assert audit(site)
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
