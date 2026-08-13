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
import os, sys


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
    print("\n".join(out))


main()
