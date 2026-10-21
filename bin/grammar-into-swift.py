#!/usr/bin/env python3
"""Carry the owner's grammar census; refuse changed bytes before compiling."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
record = json.loads((root / "grammar-law.from").read_text())
assert record["format"] == "vi-grammar-port/1"
assert len(record["revision"]) == 40
assert set(record["files"]) == {"ScopeMap.swift", "GrammarPolicy.swift", "policy.json"}
for name, source in record["files"].items():
    data = (root / "grammar-law" / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == source["sha256"], "changed vi grammar input: " + name

def swift_string(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'

print("import Foundation\nenum PinnedGrammarLaw {")
print("static let revision = " + swift_string(record["revision"]))
print("static let digest = " + swift_string(record["files"]["policy.json"]["sha256"]))
policy = (root / "grammar-law/policy.json").read_text()
assert '\"\"\"#' not in policy
print('static let bytes = Data(#\"\"\"\n' + policy.rstrip('\n') + '\n\"\"\"#.utf8) + Data([10])')
print("static let policy = try! JSONDecoder().decode(GrammarPolicy.self, from: bytes)\n}")
