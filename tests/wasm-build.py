#!/usr/bin/env python3
"""Run the actual pinned recipe with compiler doubles: transport, not equivalence."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'bin/build-court-wasm.sh'
with tempfile.TemporaryDirectory(prefix='gate-wasm-build-') as temporary:
    base = Path(temporary)
    source = base/'owner with spaces'; source.mkdir()
    home = base/'home with spaces'; home.mkdir()
    tools = base/'tools'; tools.mkdir()
    sysroot = base/'toolchain with spaces'; libs=sysroot/'lib/rustlib/wasm32-unknown-unknown/lib';libs.mkdir(parents=True)
    (libs/'libcore.rlib').write_bytes(b'compiler input fixture')
    gate = base/'gate'; (gate/'bin').mkdir(parents=True);(gate/'tests').mkdir()
    shutil.copyfile(BUILDER,gate/'bin/build-court-wasm.sh')
    for name in ('build-court-wasm.py','publication_origin.py'):
        shutil.copyfile(ROOT/'bin'/name,gate/'bin'/name)
    for name in ('publication-boundary.py','publication-boundary.json'):
        shutil.copyfile(ROOT/'tests'/name,gate/'tests'/name)
    child=source/'Contracts/Court/rust-sample';child.mkdir(parents=True)
    (child/'Cargo.toml').write_text('[dependencies]\nwasm-bindgen = "=0.2.105"\n')
    (child/'Cargo.lock').write_text('# locked compiler fixture\n')
    (child/'lib.rs').write_text('// source fixture\n')
    def git(*args):
        return subprocess.check_output(['git','-C',str(source),*args],text=True).strip()
    git('init','-q');git('add','.')
    git('-c','user.name=Fixture','-c','user.email=fixture@test','commit','-qm','compiler input fixture')
    pin=git('rev-parse','HEAD')
    (child/'lib.rs').write_text('// uncommitted edit must not enter the recipe\n')
    (gate/'bin/court-wasm.from').write_text(pin+'\n')
    def tool(name,body):
        target=tools/name;target.write_text('#!'+sys.executable+'\n'+body);target.chmod(0o755)
    tool('which','import sys;sys.exit(99)\n')
    tool('rustc','import sys\nprint('+repr('rustc 1.83.0 (90b35a623 2024-11-26)')+' if "--version" in sys.argv else '+repr(str(sysroot))+')\n')
    tool('rustup','import sys\nprint("wasm32-unknown-unknown" if "target" in sys.argv else '+repr(str(tools/'rustc'))+')\n')
    tool('cargo', '''import os,sys,json
from pathlib import Path
if '--version' in sys.argv:print('cargo 1.83.0 fixture');sys.exit(0)
Path(os.environ['WASM_TEST_FLAGS']).write_text(json.dumps(os.environ['CARGO_ENCODED_RUSTFLAGS'].split(chr(31))))
p=Path(os.environ['CARGO_TARGET_DIR'])/'wasm32-unknown-unknown/release/vi_court.wasm';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(bytes([0,97,115,109,1,0,0,0]))
''')
    tool('wasm-bindgen', '''import sys
from pathlib import Path
if '--version' in sys.argv:print('wasm-bindgen 0.2.105');sys.exit(0)
p=Path(sys.argv[sys.argv.index('--out-dir')+1]);p.mkdir(parents=True,exist_ok=True)
(p/'vi_court_bg.wasm').write_bytes(bytes([0,97,115,109,1,0,0,0]));(p/'vi_court.js').write_text('// compiler fixture')
''')
    clean={k:v for k,v in os.environ.items() if k not in ('RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','VI_SOURCE','CARGO_HOME')}
    for extra,expected in [({'RUSTFLAGS':'--cfg first'},['--cfg','first']),
                           ({'RUSTFLAGS':'ignored','CARGO_ENCODED_RUSTFLAGS':'--cfg\x1fvalue with spaces'},['--cfg','value with spaces']),
                           ({'RUSTFLAGS':'ignored','CARGO_ENCODED_RUSTFLAGS':''},[])]:
        env=dict(clean,HOME=str(home),WASM_TEST_FLAGS=str(base/'flags.json'),PATH=str(tools)+os.pathsep+os.environ['PATH'],**extra)
        answer=subprocess.run(['sh',str(gate/'bin/build-court-wasm.sh'),pin,'--repository',str(source),'--offline'],env=env,capture_output=True,text=True)
        assert answer.returncode==0,answer.stdout+answer.stderr
        flags=json.loads((base/'flags.json').read_text())
        assert flags[:len(expected)]==expected,flags
        owned=flags[len(expected):]
        assert owned[-1]=='-Cstrip=debuginfo'
        assert all(f.startswith('--remap-path-prefix=') for f in owned[:-1])
        assert any(f=='--remap-path-prefix='+str(home.resolve())+'=/build-home' for f in owned)
        assert any(f=='--remap-path-prefix='+str(sysroot.resolve())+'=/rust-toolchain' for f in owned)
        assert any(f.endswith('=/vi/Contracts/Court/rust-sample') for f in owned)
        assert any(f.endswith('=/cargo') for f in owned)
        record=(gate/'bin/court-wasm.from').read_text()
        receipt=json.loads((gate/'bin/court-wasm.build.json').read_text())
        assert record.splitlines()[0]==pin and 'local Git objects' in record
        import hashlib
        assert receipt['source_files']['lib.rs']==hashlib.sha256(b'// source fixture\n').hexdigest()
        assert receipt['source_mode']=='local-git-objects' and receipt['extra_rustflags']==expected
        assert str(source) not in record and str(home) not in record
        assert str(source) not in json.dumps(receipt) and str(home) not in json.dumps(receipt)
    local=subprocess.run([sys.executable,str(gate/'tests/publication-boundary.py'),'--artifact',str(gate/'bin/court-wasm/node/vi_court_bg.wasm')],capture_output=True,text=True,env=env)
    assert local.returncode==1 and 'local source receipt' in local.stdout
    saved=(gate/'bin/court-wasm.build.json').read_bytes()
    private='/'+'home'+'/private-account/source'
    refused=subprocess.run(['sh',str(gate/'bin/build-court-wasm.sh'),pin,'--repository',str(source),'--offline'],env=dict(env,CARGO_ENCODED_RUSTFLAGS='--cfg'+chr(31)+'location='+private),capture_output=True,text=True)
    assert refused.returncode==2 and 'redacted' in refused.stderr and private not in refused.stderr
    assert (gate/'bin/court-wasm.build.json').read_bytes()==saved
    env=dict(env,VI_SOURCE=str(source))
    refused=subprocess.run(['sh',str(gate/'bin/build-court-wasm.sh'),pin],env=env,capture_output=True,text=True)
    assert refused.returncode==2 and 'VI_SOURCE' in refused.stderr and '--repository' in refused.stderr
print('WASM BUILD GREEN: spaces, encoded precedence, declared flags, committed source and explicit local provenance; VI_SOURCE refuses')
