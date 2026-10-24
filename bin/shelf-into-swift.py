#!/usr/bin/env python3
# The shelf, written as Swift the compiler can take in. The tool reads
# stdlib/ off the disk beside it, which is true in a clone and false for
# anybody who downloaded one binary; this writes the same pages into the
# build so the binary carries them. Text in, text out: every line here is
# readable, and nothing is encoded past what Swift needs escaped.
#
# The snapshot is a SECOND record of the pages, which is the shape this
# whole tool exists to refuse. So it is never edited by hand, never
# committed, and the battery holds it byte for byte against stdlib/.
import base64, json, os, sys


def swift_string(line):
    said = line.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + said + '"'


def main():
    where = sys.argv[1]
    # the revision the court compiled into this build came from: written in
    # beside the pages, because a binary somebody downloaded has no
    # bin/gate-judge.from next to it and used to answer "not recorded" about
    # its own one dependency, while the release shipped that revision in a
    # file it was not looking for
    pin = (sys.argv[2] if len(sys.argv) > 2 else "").strip()
    names = sorted(f for f in os.listdir(where) if f.endswith(".swift"))
    out = ["// Written by bin/shelf-into-swift.py at build time, from stdlib/.",
           "// Not committed, not edited: the pages themselves are in stdlib/,",
           "// and the battery holds this against them.",
           "let SHELF_EMBEDDED: [(name: String, text: String)] = ["]
    for f in names:
        text = open(os.path.join(where, f), encoding="utf-8").read()
        out.append('    (name: %s, text: [' % swift_string(f[:-6]))
        for line in text.split("\n"):
            out.append("        " + swift_string(line) + ",")
        out.append('    ].joined(separator: "\\n")),')
    out.append("]")
    out.append("let COURT_PIN_BUILT_IN = " + swift_string(pin))
    # Runtime bytes travel with the shelf so every build of the CLI, including
    # the battery's mutant, carries the same delivery. Development still reads
    # the files beside the binary first.
    runtime = ["web/ui.html", "web/codemirror.js", "web/codemirror.css", "web/publication.js", "web/reader-draft.js",
               "bin/world-court.js", "bin/grammar-policy.js", "bin/court-contexts.js",
               "bin/judge.js", "bin/renderer.js", "bin/press.js", "bin/drawing-profile.js",
               "bin/drawing-fonts.json", "bin/drawing-contract.from", "bin/drawing.from", "bin/press-contract.from", "bin/court-wasm.from", "bin/court-wasm.build.json",
               "bin/court-wasm/web/vi_court.js", "bin/court-wasm/web/vi_court_bytes.js",
               "bin/organization-court.from", "LICENSE", "docs/NOTICE.md"]
    # Example inputs remain inspectable data; a one-file installation carries the same recipes.
    example_root = os.path.join(os.path.dirname(os.path.abspath(where)), 'examples')
    with open(os.path.join(example_root, 'index.json'), encoding='utf-8') as f:
        recipes = json.load(f)
    inputs = {'examples/index.json'} | {'examples/' + recipe + '/' + name
        for recipe, files in recipes.items() for name in files}
    for folder, _, files in os.walk(example_root):
        runtime.extend(name for f in sorted(files)
            if (name := os.path.relpath(os.path.join(folder, f), os.path.dirname(example_root)).replace("\\", "/")) in inputs)
    runtime.sort()
    out.append("let RUNTIME_EMBEDDED: [String: String] = [")
    for relative in runtime:
        path = os.path.join(os.path.dirname(os.path.abspath(where)), relative)
        if not os.path.isfile(path):
            continue
        encoded = base64.b64encode(open(path, "rb").read()).decode("ascii")
        chunks = [swift_string(encoded[i:i+4096]) for i in range(0, len(encoded), 4096)]
        out.append("    " + swift_string(relative) + ": [" + ",\n".join(chunks) + "].joined(),")
    out.append("]")
    # ── AND THE BYTES LEAVE HERE AS UTF-8, WHATEVER THE CONSOLE THINKS. The
    # pages carry `·` and `─`; printed through a console whose encoding is
    # cp1252, python raises UnicodeEncodeError and the build dies with it.
    # The stream is written as bytes, in the one encoding these files are in.
    sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))


main()
