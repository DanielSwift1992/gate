#!/usr/bin/env python3
"""Compare the browser grammar reading with the shipped, pinned Swift owner.

This is a finite comparison, not a new grant table. Unicode identifiers outside
this port's declared subset must remain unsupported, including after an edit.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'bin/grammar-law.from').read_text())
for name, item in PIN['files'].items():
    assert hashlib.sha256((ROOT / 'bin/grammar-law' / name).read_bytes()).hexdigest() == item['sha256'], name
policy = json.loads((ROOT / 'bin/grammar-law/policy.json').read_text())
fragments = [
    'public enum Unit {}\n',
    'public protocol Pair { associatedtype Left; associatedtype Right }\n',
    'public enum One { public typealias Value = Unit }\n',
    'public enum One { public static var body: some Structure { Unit() } }\n',
    'public enum One { public static var body: some Structure { Unit(); Unit() } }\n',
    'public enum One { public static var count: Int { 1 } }\n',
    'let x = 1, y = 2\n',
    'public func f() { var x = 0; x += 1 }\n',
    'public actor Worker {}\n',
    'public enum X {}\n€\n',
    'public func f() { € }\n',
    'public enum X {}\r\npublic actor Y {}\r\n',
    'public enum X {}\rpublic actor Y {}\r',
    '// public actor Ignored {}\npublic enum X {}\n',
    '/* public actor Ignored {} */\npublic enum X {}\n',
    'public enum Text { public static var typeName: String { "Café 👩‍🔬" } }\n',
    'public enum Text { public static var typeName: String { "a \\" quoted" } }\n',
    r'public enum Text { public static var typeName: String { "\(f("x"))" } }'+'\n',
    'public enum Unclosed {\npublic typealias Value = Unit\n',
    '@StructureBuilder public static var body: some Structure { Unit() }\n',
    'public enum X {}\nfor x in xs { if x { continue } }\n',
    'public enum X { public typealias Witness = Never }\n',
    'public enum X { public static var body: some Structure { 🛰️ } }\n',
]
cases = [dict(source=source, scope=scope) for scope in policy['scopes'] for source in fragments]
if shutil.disk_usage('/System/Volumes/Data' if Path('/System/Volumes/Data').exists() else ROOT).free < 5 * 1024 ** 3:
    raise SystemExit('less than 5 GiB free; grammar comparison not started')
with tempfile.TemporaryDirectory(prefix='gate-grammar-policy-') as directory:
    root = Path(directory)
    (root / 'cases.json').write_text(json.dumps(cases))
    (root / 'main.swift').write_text('''import Foundation
struct Case: Decodable { let source: String; let scope: String }
let args = CommandLine.arguments
let policy = try JSONDecoder().decode(GrammarPolicy.self, from: Data(contentsOf: URL(fileURLWithPath: args[1])))
let cases = try JSONDecoder().decode([Case].self, from: Data(contentsOf: URL(fileURLWithPath: args[2])))
let answers = try cases.map { try policy.findings($0.source, scope: $0.scope) }
FileHandle.standardOutput.write(try JSONEncoder().encode(answers))
''')
    command = ['swiftc', '-O', '-module-cache-path', str(root / 'modules'), '-o', str(root / 'owner'),
               str(ROOT / 'bin/grammar-law/GrammarPolicy.swift'), str(ROOT / 'bin/grammar-law/ScopeMap.swift'), str(root / 'main.swift')]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    expected = json.loads(subprocess.check_output([str(root / 'owner'), str(ROOT / 'bin/grammar-law/policy.json'), str(root / 'cases.json')], timeout=60))
    script = '''const fs=require('fs'),assert=require('assert');
const port=require(process.argv[1]),policy=JSON.parse(fs.readFileSync(process.argv[2]));
const cases=JSON.parse(fs.readFileSync(process.argv[3]));
const answers=cases.map(c=>port.findings(c.source,c.scope,policy));
for(const text of ['public enum Café {}','public enum e\\u0301 {}','public enum 𝕏 {}'])
    assert.throws(()=>port.findings(text,'SurfaceScope',policy),/outside this port/);
process.stdout.write(JSON.stringify(answers));'''
    env = {k: v for k, v in os.environ.items() if k != 'NODE_USE_SYSTEM_CA'}
    actual = json.loads(subprocess.check_output(['node', '-e', script, str(ROOT / 'bin/grammar-policy.js'), str(ROOT / 'bin/grammar-law/policy.json'), str(root / 'cases.json')], env=env, timeout=60))
    for index, (swift, browser) in enumerate(zip(expected, actual)):
        assert swift == browser, (cases[index], swift, browser)
    assert len(expected) == len(actual) == len(cases)
print('PASS:', len(cases), 'grammar readings match the pinned Swift policy; three Unicode identifier boundaries are unsupported')
