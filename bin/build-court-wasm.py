#!/usr/bin/env python3
"""Build the pinned court from Git bytes with machine-independent source paths."""
import argparse
import base64
import getpass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORPUS = 'https://github.com/DanielSwift1992/verification-is-identification'
CRATE = 'Contracts/Court/rust-sample'
RUSTC = 'rustc 1.83.0 (90b35a623 2024-11-26)'
BINDGEN = 'wasm-bindgen 0.2.105'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def output(argv, **kwargs):
    return subprocess.check_output(argv, **kwargs).decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pin', nargs='?', default=(ROOT/'bin/court-wasm.from').read_text().splitlines()[0])
    parser.add_argument('--repository', type=Path, help='read committed Git objects from this local repository, never its working files')
    parser.add_argument('--output', type=Path, default=ROOT/'bin', help='directory receiving court-wasm/ and its receipts')
    parser.add_argument('--offline', action='store_true', help='require local Git objects and the existing Cargo registry cache')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.pin):
        raise ValueError('pin must be a full commit SHA, not a moving branch')
    if args.offline and not args.repository:
        raise ValueError('--offline requires --repository')
    for command, expected in [('rustc',RUSTC),('wasm-bindgen',BINDGEN)]:
        actual = output([command,'--version'])
        if actual != expected:
            raise ValueError(command+' version differs; expected '+expected+', got '+actual)
    if 'wasm32-unknown-unknown' not in output(['rustup','target','list','--installed']).splitlines():
        raise ValueError('wasm32-unknown-unknown is not installed; no installation is performed')
    cargo_home = Path(os.environ.get('CARGO_HOME',str(Path.home()/'.cargo'))).resolve()
    for name in ('config','config.toml'):
        if (cargo_home/name).exists():
            raise ValueError('Cargo user configuration is not an input to this recipe; use an unconfigured registry cache')
    sysroot = Path(output(['rustc','--print','sysroot'])).resolve()
    spec = importlib.util.spec_from_file_location('boundary',ROOT/'tests/publication-boundary.py')
    law = importlib.util.module_from_spec(spec);spec.loader.exec_module(law)
    policy = law.load()
    with tempfile.TemporaryDirectory(prefix='gate-court-wasm-') as temporary:
        work = Path(temporary).resolve()
        if shutil.disk_usage(work).free < 5 * 1024**3:
            raise ValueError('fewer than 5 GiB free before the wasm build')
        repository = args.repository.resolve() if args.repository else work/'repository'
        if not args.repository:
            subprocess.run(['git','clone','--filter=blob:none','--no-checkout','--quiet',CORPUS,str(repository)],check=True)
        revision = output(['git','-C',str(repository),'rev-parse',args.pin+'^{commit}'])
        if revision != args.pin:
            raise ValueError('resolved commit differs from pin')
        source = work/'source'; source.mkdir()
        paths = output(['git','-C',str(repository),'ls-tree','-r','--name-only',revision,'--',CRATE]).splitlines()
        inputs = {}
        for name in paths:
            relative = Path(name).relative_to(CRATE)
            raw = subprocess.check_output(['git','-C',str(repository),'show',revision+':'+name])
            target = source/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            inputs[str(relative)] = sha(raw)
        if not inputs or 'Cargo.lock' not in inputs:
            raise ValueError('pinned crate or Cargo.lock is missing')
        if not re.search(r'^wasm-bindgen = "=0\.2\.105"$',(source/'Cargo.toml').read_text(),re.M):
            raise ValueError('pinned crate and wasm-bindgen executable versions differ')
        # Explicit target makes these flags apply to target dependencies, too.
        # Unit separators preserve spaces in host paths. Last matching mapping
        # wins, so the general home mapping precedes the specific source/cache.
        mappings = [(Path.home().resolve(),'/build-home'),(work,'/build'),
                    (source,'/vi/'+CRATE),(cargo_home,'/cargo'),(sysroot,'/rust-toolchain')]
        flags = []
        for host, virtual in mappings:
            for spelling in dict.fromkeys([str(host),str(host).replace('\\','/')]):
                flags.append('--remap-path-prefix='+spelling+'='+virtual)
        environment = {key:value for key,value in os.environ.items()
                       if not key.startswith(('RUST','CARGO_')) and key not in ('VI_SOURCE','SOURCE_DATE_EPOCH')}
        environment.update(CARGO_HOME=str(cargo_home), CARGO_TARGET_DIR=str(work/'target'),
                           CARGO_ENCODED_RUSTFLAGS='\x1f'.join(flags), CARGO_INCREMENTAL='0',
                           RUSTC_WRAPPER='', RUSTC_WORKSPACE_WRAPPER='', SOURCE_DATE_EPOCH='0')
        # Rustup's toolchain selection is part of the checked environment.
        # Removing it after --version could silently build with another default.
        for key in ('RUSTUP_HOME','RUSTUP_TOOLCHAIN'):
            if key in os.environ:
                environment[key] = os.environ[key]
        if output(['rustc','--version'], env=environment) != RUSTC:
            raise ValueError('effective compilation environment selects another rustc')
        argv = ['cargo','build','--locked','--release','--lib','--target','wasm32-unknown-unknown']
        if args.offline:
            argv.append('--offline')
        subprocess.run(argv,cwd=source,env=environment,check=True)
        raw_wasm = work/'target/wasm32-unknown-unknown/release/vi_court.wasm'
        for target in ('nodejs','no-modules'):
            subprocess.run(['wasm-bindgen','--target',target,'--out-dir',str(work/target),str(raw_wasm)],check=True)
        contents = {
            'court-wasm/node/vi_court.js':(work/'nodejs/vi_court.js').read_bytes(),
            'court-wasm/node/vi_court_bg.wasm':(work/'nodejs/vi_court_bg.wasm').read_bytes(),
            'court-wasm/web/vi_court.js':(work/'no-modules/vi_court.js').read_bytes(),
            'court-wasm/web/vi_court_bytes.js':(
                '// the wasm court as bytes, for a page that cannot fetch its neighbour; see bin/court-wasm.from\n'
                'var VI_COURT_WASM_BASE64 = "'+base64.b64encode((work/'no-modules/vi_court_bg.wasm').read_bytes()).decode()+'";\n').encode(),
        }
        errors = [message for name,raw in contents.items()
                  for message in law.publication_content(policy,'bin/'+name,raw,[getpass.getuser()])]
        if errors:
            raise ValueError('\n'.join(errors))
        node_hash = sha(contents['court-wasm/node/vi_court_bg.wasm'])
        web_hash = sha((work/'no-modules/vi_court_bg.wasm').read_bytes())
        receipt = {'format':'gate-court-wasm-build/1','repository':CORPUS,'revision':revision,
                   'recipe_sha256':sha(Path(__file__).read_bytes()),'rustc':RUSTC,'cargo':output(['cargo','--version']),
                   'wasm_bindgen':BINDGEN,'target':'wasm32-unknown-unknown','cargo_locked':True,
                   'source_files':inputs,'path_mappings':['user-home=/build-home','build-root=/build','source=/vi/'+CRATE,'cargo-home=/cargo','sysroot=/rust-toolchain'],
                   'outputs':{name:sha(raw) for name,raw in contents.items()},'web_decoded_sha256':web_hash,
                   'reproducibility_scope':'Same pinned sources, lockfile, recipe and toolchain; independent clean builds must be compared. No cross-toolchain claim.'}
        contents['court-wasm.build.json'] = (json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode()
        contents['court-wasm.from'] = (revision+'\nbuilt from committed corpus '+revision+'; locked dependencies; remapped source paths; see court-wasm.build.json\n'+BINDGEN+'; '+RUSTC+'\n'+node_hash+'  court-wasm/node/vi_court_bg.wasm\n'+web_hash+'  court-wasm/web/(as base64 in) vi_court_bg.wasm\n').encode()
        for name,raw in contents.items():
            destination = args.output/name;destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(raw)
        print('built court wasm at '+revision+'\nnode sha256 '+node_hash+'\nweb sha256 '+web_hash)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        print('build-court-wasm: '+str(error),file=sys.stderr)
        sys.exit(2)
