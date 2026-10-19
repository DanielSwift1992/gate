#!/usr/bin/env python3
# the count court's premise, written into the build: the corpus's Primitive at
# the judge's pin, carried by the binary as bytes it writes back out when the
# count court is asked. One writer for bin/build-cli.sh and for the battery's
# own builds of the vein, so the two cannot carry different premises.
import base64
import sys

data = base64.b64encode(open(sys.argv[1], "rb").read()).decode("ascii")
print("// the corpus's Primitive at the judge's pin, the premise `judge count` reads by")
print("import Foundation")
print("enum PinnedCorpus {")
print('    static let primitive = String(decoding: Data(base64Encoded: "' + data + '")!, as: UTF8.self)')
print("}")
