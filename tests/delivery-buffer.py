#!/usr/bin/env python3
"""Compile the shipped delivery builder against a file replaced after resolution."""
from pathlib import Path
import os, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'bin/gate-cli.swift').read_text()
def function(name):
 a=src.index('func '+name+'(');return src[a:src.index('\n}\n',a)+2]
with tempfile.TemporaryDirectory(prefix='gate-delivery-buffer-') as scratch:
 p=Path(scratch)
 program='''import Foundation
struct LayoutRow { var name: String?; var path: String; var source: String; var kind: String? = "CarriedFile" }
struct Layout { var rows: [LayoutRow] }
struct WorldState { var layout: Layout? }
struct TakenResolution { var inputs: [String: [String: String]]; var addresses: [String: String]; var bytes: [String: Data] }
let path = CommandLine.arguments[1]
let original = Data("verified before resolution".utf8)
func benchTakenRefusal(_ w: WorldState, _ n: String, resolved: TakenResolution, files: [(String,String)]) -> (address: String, claim: String)? { nil }
func servePick(_ w: WorldState, _ q: [String:String], files: [(String,String)]) -> String? { path }
func inputBytes(_ p: String) -> Data? { original }
func personalTemplate() -> String { "" }
func publicationJSON(_ object: [String: Any]) -> Data { try! JSONSerialization.data(withJSONObject: object, options: [.sortedKeys]) }
'''+function('sha256Hex')+'\n'+function('worldReading')+'''
let row = LayoutRow(name: "Source", path: "source.md", source: "theirs")
let world = WorldState(layout: Layout(rows: [row]))
let taken = TakenResolution(inputs: ["Source": ["sha256": sha256Hex(original), "repository": "owner", "revision": "pin", "source_path": "source.md"]], addresses: ["Source": ".gate/forms-definitions.json:9"], bytes: [path: original])
try! original.write(to: URL(fileURLWithPath: path))
let good = worldReading(world, "source.md", taken, [("source.md",path)])
precondition(good.code == 200 && good.data == original)
try! Data("tampered after resolution!".utf8).write(to: URL(fileURLWithPath: path))
let changed = worldReading(world, "source.md", taken, [("source.md",path)])
let refusal = try! JSONSerialization.jsonObject(with: changed.data) as! [String: Any]
precondition(changed.code == 409 && refusal["address"] as? String == ".gate/forms-definitions.json:9")
try! FileManager.default.removeItem(atPath: path)
let missing = worldReading(world, "source.md", taken, [("source.md",path)])
precondition(missing.code == 409)
print("DELIVERY BUFFER GREEN: shipped builder refuses changed and missing bytes after resolution")
'''
 (p/'main.swift').write_text(program)
 tool=shutil.which('swiftc');assert tool,'swiftc is required for the delivery buffer control'
 build=subprocess.run([tool,str(p/'main.swift'),'-o',str(p/'probe')],capture_output=True,text=True)
 assert build.returncode==0,build.stderr
 subprocess.run([str(p/'probe'),str(p/'source')],check=True)
