#!/usr/bin/env python3
"""Cache identity follows effective bytes, not the presence of an editor overlay.

Compile the production key, lookup and SHA-256 functions. The counted reader is
an isolated stand-in: the separate Court controls judge the Swift statements.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
source = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else (ROOT / 'bin/gate-cli.swift').read_text()
def function(name):
    match = re.search(r'^func ' + name + r'\(.*?^}\n', source, re.M | re.S)
    assert match, name
    return match[0]
fixture = r'''
import Foundation
struct LayoutRow {
    var name: String? = "Facts"
    var path = "Facts.swift", source = "mine"
    var role: String? = "forms", kind: String? = "FormsFile", language: String? = "Demo"
    var from: String? = nil, written: String? = nil, opens: String? = nil
    var line = 1
    var drawingInputs: [String] = []
}
struct Layout { var manifest: String; var rows: [LayoutRow] }
struct WorldState { var root: String; var layout: Layout? }
struct TakenResolution { var bad: [String] = []; var paths: [String:String] = [:] }
struct FormResidue { var address: String; var id: String; var reason: String }
struct GrammarContexts {
    var bad: [(address:String,claim:String)] = []
    var unsupported: [FormResidue] = []
    var text: String
}
enum PinnedGrammarLaw { static var digest = "scope-law" }
var reader = "reader-pin"
func judgeFrom() -> String? { reader }
func layoutDir(_ w: WorldState) -> String? { w.root }
func joinPath(_ a: String, _ b: String) -> String { a + "/" + b }
func inputBytes(_ p: String) -> Data? { FileManager.default.contents(atPath:p) }
func takenInputs(_ w: WorldState) -> TakenResolution { TakenResolution() }
var calls = 0
func readGrammarContexts(_ w: WorldState, live: [String:String], resolved: TakenResolution?) -> GrammarContexts {
    calls += 1
    return GrammarContexts(text:live["Facts.swift"] ?? String(decoding:inputBytes(joinPath(w.root,"Facts.swift")) ?? Data(),as:UTF8.self))
}
var GRAMMAR_CONTEXT_PLAN: (key:String,value:GrammarContexts)? = nil
'''
checks = r'''
let root = CommandLine.arguments[1]
let file = root + "/Facts.swift", manifest = root + "/gate.manifest.swift", record = root + "/.gate/forms-definitions.json"
func write(_ path:String,_ text:String) { try! Data(text.utf8).write(to:URL(fileURLWithPath:path)) }
write(file,"enum A {}")
write(manifest,"manifest 1")
write(record,"record 1")
var world = WorldState(root:root,layout:Layout(manifest:manifest,rows:[LayoutRow()]))
func expect(_ condition:Bool,_ message:String) { if !condition { fatalError(message) } }
let first = grammarContexts(world)
expect(calls==1,"first read was not prepared once")
expect(grammarContexts(world,live:["Facts.swift":"enum A {}"]).text==first.text,"equal bytes changed the reply")
expect(calls==1,"equal editor and disk bytes parsed the context again")
_ = grammarContexts(world)
expect(calls==1,"switching from the editor back to disk parsed the same input again")
expect(grammarContexts(world,live:["Facts.swift":"enum B {}"]).text=="enum B {}","changed buffer reused the old value")
expect(calls==2,"changed buffer did not invalidate")
_ = grammarContexts(world,live:["Facts.swift":"enum B {}"])
expect(calls==2,"an identical changed buffer was prepared twice")
_ = grammarContexts(world)
expect(calls==3,"return to the original input did not replace the current plan")
let date = (try! FileManager.default.attributesOfItem(atPath:file))[.modificationDate]!
write(file,"enum B {}")
try! FileManager.default.setAttributes([.modificationDate:date],ofItemAtPath:file)
expect(grammarContexts(world).text=="enum B {}" && calls==4,"same length and mtime hid changed bytes")
_ = grammarContexts(world,live:["Facts.swift":"enum B {}"])
expect(calls==4,"new disk bytes did not share the equivalent editor input")
var last=calls
func changed(_ label:String) { _ = grammarContexts(world); expect(calls==last+1,label+" did not invalidate");last=calls }
write(manifest,"manifest 2");changed("manifest")
write(record,"record 2");changed("record")
world.layout!.rows[0].language="FourthModule";changed("language")
PinnedGrammarLaw.digest="another-law";changed("scope law")
reader="another-reader";changed("reader")
_ = grammarContexts(world,live:["undeclared.swift":"unresolved"])
expect(calls==last+1,"an undeclared overlay disappeared from the key")
last=calls
_ = grammarContexts(world,resolved:TakenResolution(bad:["damaged pin"]))
expect(calls==last+1,"a damaged input reused the last plan")
last=calls
try! FileManager.default.removeItem(atPath:file)
changed("missing source")
print("CONTEXT CACHE GREEN: equal overlays share one preparation; changed bytes, metadata and failures invalidate")
'''
if shutil.disk_usage('/').free < 5 * 2**30:
    raise SystemExit('context cache: fewer than 5 GiB before Swift compilation')
with tempfile.TemporaryDirectory(prefix='gate-context-cache-') as tmp:
    folder = Path(tmp); (folder/'.gate').mkdir()
    main = folder/'main.swift'
    main.write_text(fixture + '\n'.join(function(n) for n in ['sha256Hex','publicationJSON','grammarContextKey','grammarContexts']) + checks)
    compiled = subprocess.run(['swiftc', '-O', str(main), '-o', str(folder/'probe')], capture_output=True, text=True)
    if compiled.returncode:
        raise SystemExit(compiled.stdout + compiled.stderr)
    subprocess.run([str(folder/'probe'),str(folder)],check=True)
