#!/bin/sh
# builds the wasm court from the public theory corpus at a pin and drops it
# into bin/court-wasm/: the certificate court (`judge where`) and the count
# court (`judge count`) for node and for the browser, the same judgement the
# corpus builds natively.
#
# AND WRITES DOWN WHICH REVISION AND WHICH BYTES. The module's identity is its
# bytes; bin/court-wasm.from records the revision it was built from, the tool
# that bound it and the SHA-256 of each module beside it, so anyone may build
# at that revision and compare. A module built from a working copy is a
# second, untracked pin: VI_SOURCE exists for development and says so in the
# record.
set -e
PIN=${1:-main}
OUT="$(cd "$(dirname "$0")" && pwd)"
if [ -n "${VI_SOURCE:-}" ]; then
    SRC="$VI_SOURCE"
    NOTE="built from a local checkout, not from the public pin"
else
    TMP=$(mktemp -d)
    git clone --depth 50 https://github.com/DanielSwift1992/verification-is-identification "$TMP/vi"
    cd "$TMP/vi" && git checkout "$PIN"
    SRC="$TMP/vi"
    NOTE="built from the public corpus at $PIN"
fi
cd "$SRC"
REV=$(git rev-parse HEAD)
# Compiler paths are delivery bytes too. Keep the user's flags, then name
# the two machine-specific roots without carrying their local spelling.
python3 - <<'PY'
import os
from pathlib import Path
import subprocess
env = dict(os.environ)
encoded = env.get('CARGO_ENCODED_RUSTFLAGS')
if encoded is not None:
    flags = encoded.split('\x1f') if encoded else []
else:
    flags = env.get('RUSTFLAGS', '').split()
flags += ['--remap-path-prefix=' + str(Path.home()) + '=/build/home',
          '--remap-path-prefix=' + str(Path.cwd()) + '=/build/vi']
env['CARGO_ENCODED_RUSTFLAGS'] = '\x1f'.join(flags)
subprocess.run(['Contracts/Court/rust-sample/build-wasm.sh'], env=env, check=True)
PY
PKG="$SRC/Contracts/Court/rust-sample/pkg"
mkdir -p "$OUT/court-wasm/node" "$OUT/court-wasm/web"
cp "$PKG/node/vi_court.js" "$PKG/node/vi_court_bg.wasm" "$OUT/court-wasm/node/"
cp "$PKG/no-modules/vi_court.js" "$OUT/court-wasm/web/vi_court.js"
# the page is opened from a file as well as served, and a file cannot fetch
# its neighbour: the module travels inside a classic script as base64
python3 - "$PKG/no-modules/vi_court_bg.wasm" "$OUT/court-wasm/web/vi_court_bytes.js" <<'PY'
import base64, sys
data = base64.b64encode(open(sys.argv[1], "rb").read()).decode("ascii")
with open(sys.argv[2], "w") as out:
    out.write("// the wasm court as bytes, for a page that cannot fetch its neighbour; see bin/court-wasm.from\n")
    out.write('var VI_COURT_WASM_BASE64 = "' + data + '";\n')
PY
cd "$OUT"
{
    echo "$REV"
    echo "$NOTE"
    echo "compiler source paths: HOME=/build/home; SOURCE=/build/vi"
    echo "wasm-bindgen $(wasm-bindgen --version | awk '{print $2}'); $(rustc --version)"
    shasum -a 256 court-wasm/node/vi_court_bg.wasm "$PKG/no-modules/vi_court_bg.wasm" | sed "s|$PKG/no-modules/|court-wasm/web/(as base64 in) |"
} > court-wasm.from
echo "bin/court-wasm built from $PIN ($REV)"
cat court-wasm.from
