#!/usr/bin/env bash
# The cover's picture of the bench, taken the same way every time: a fresh
# demo world, `gate serve` on a free port, one headless Chrome shot of the
# door /ui?f=ownership.swift:82 - the file and line of the demo's one
# refusal. Beside the image it writes docs/bench.png.from with the sha256
# of ui.html as it was in front of the camera: the battery holds that hash
# to the ui.html in the working copy, so a picture of a page that no
# longer exists goes red there, and running this script is the whole fix.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"

CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "$(command -v google-chrome || true)" \
         "$(command -v chromium || true)" \
         "$(command -v chromium-browser || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
done
if [ -z "$CHROME" ]; then
    echo "shoot-bench: no Chrome or Chromium on this machine, and the shot is taken with one." >&2
    echo "  install one, or take the picture on a machine that has it: bash bin/shoot-bench.sh" >&2
    exit 1
fi

WORLD="$(mktemp -d "${TMPDIR:-/tmp}/gate-shoot-XXXXXX")"
trap 'kill $SERVE 2>/dev/null || true; wait $SERVE 2>/dev/null || true; rm -rf "$WORLD"' EXIT
"$HERE/gate" demo "$WORLD" >/dev/null

PORT="$(python3 - <<'EOF'
import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()
EOF
)"
(cd "$WORLD" && exec python3 "$HERE/gate" serve "$PORT" --no-open >/dev/null 2>&1) &
SERVE=$!
for _ in $(seq 40); do
    curl -s "http://127.0.0.1:$PORT/files" >/dev/null 2>&1 && break
    sleep 0.25
done

mkdir -p "$HERE/docs"
"$CHROME" --headless --disable-gpu --hide-scrollbars \
    --window-size=1280,800 --force-device-scale-factor=2 --virtual-time-budget=4000 \
    --screenshot="$HERE/docs/bench.png" \
    "http://127.0.0.1:$PORT/ui?f=ownership.swift:82" 2>/dev/null

python3 - "$HERE" <<'EOF'
import hashlib, sys, os
here = sys.argv[1]
h = hashlib.sha256(open(os.path.join(here, "ui.html"), "rb").read()).hexdigest()
open(os.path.join(here, "docs", "bench.png.from"), "w").write(
    "ui.html sha256:" + h + "\n"
    "door /ui?f=ownership.swift:82 over `gate demo`, 1280x800 at 2x\n"
    "retake: bash bin/shoot-bench.sh\n")
print("docs/bench.png over ui.html", h[:12])
EOF
