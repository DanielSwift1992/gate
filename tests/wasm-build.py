#!/usr/bin/env python3
"""Exercise the real builder's flag transport and local provenance, without Rust."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'bin/build-court-wasm.sh'
PIN = '1' * 40
with tempfile.TemporaryDirectory(prefix='gate-wasm-build-') as temporary:
    base = Path(temporary)
    source = base/'owner with spaces'; source.mkdir()
    home = base/'home with spaces'; home.mkdir()
    tools = base/'tools'; tools.mkdir()
    gate = base/'gate/bin'; gate.mkdir(parents=True)
    builder = gate/'build-court-wasm.sh'; shutil.copyfile(BUILDER, builder)
    child = source/'Contracts/Court/rust-sample'; child.mkdir(parents=True)
    program = child/'build-wasm.sh'
    program.write_text('#!'+sys.executable+'\n'+
        'import os,json,pathlib\n'+
        'root=pathlib.Path.cwd(); (root/"flags.json").write_text(json.dumps(os.environ.get("CARGO_ENCODED_RUSTFLAGS", "").split(chr(31)) if os.environ.get("CARGO_ENCODED_RUSTFLAGS") else []))\n'+
        'for target in ["node","no-modules"]:\n p=root/"Contracts/Court/rust-sample/pkg"/target; p.mkdir(parents=True,exist_ok=True); (p/"vi_court_bg.wasm").write_bytes(bytes([0,97,115,109,1,0,0,0])); (p/"vi_court.js").write_text("// compiler fixture")\n')
    program.chmod(0o755)
    for name, body in {'git': 'test "$1" = rev-parse || exit 91\nprintf "%s\\n" '+PIN+'\n',
                       'wasm-bindgen': 'printf "wasm-bindgen fixture\\n"\n',
                       'rustc': 'printf "rustc fixture\\n"\n'}.items():
        tool=tools/name;tool.write_text('#!/bin/sh\n'+body);tool.chmod(0o755)
    clean={k:v for k,v in os.environ.items() if k not in ('RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS')}
    for extra, expected in [({'RUSTFLAGS':'--cfg first'}, ['--cfg','first']),
                            ({'RUSTFLAGS':'ignored','CARGO_ENCODED_RUSTFLAGS':'--cfg\x1fvalue with spaces'}, ['--cfg','value with spaces']),
                            ({'RUSTFLAGS':'ignored','CARGO_ENCODED_RUSTFLAGS':''}, [])]:
        env=dict(clean, HOME=str(home), VI_SOURCE=str(source), PATH=str(tools)+os.pathsep+os.environ['PATH'], **extra)
        answer=subprocess.run(['sh',str(builder),PIN],env=env,capture_output=True,text=True)
        assert answer.returncode==0, answer.stderr
        flags=json.loads((source/'flags.json').read_text())
        assert flags==expected+['--remap-path-prefix='+str(home)+'=/build/home','--remap-path-prefix='+str(source.resolve())+'=/build/vi'], flags
        record=(gate/'court-wasm.from').read_text()
        assert record.splitlines()[0]==PIN and 'local checkout' in record
        assert str(source) not in record and str(home) not in record
        assert 'compiler source paths: HOME=/build/home; SOURCE=/build/vi' in record
print('WASM BUILD GREEN: source roots, spaces, encoded precedence and explicit local provenance')
