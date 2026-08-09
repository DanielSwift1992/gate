#!/usr/bin/env bash
# The cover's picture of the bench, taken the same way every time: a fresh
# demo world, `gate serve` on a free port, one headless Chrome shot of the
# door /?f=ownership.swift:89&view=bare - the file and line of the demo's
# one refusal, in the view the bench opens on: the record without ceremony,
# with the refusing rows marked where they stand. The full Swift is a tab
# away in the same picture, which is the point being made. Beside the image it writes docs/bench.png.from with the sha256
# of ui.html as it was in front of the camera: the battery holds that hash
# to the ui.html in the working copy, so a picture of a page that no
# longer exists goes red there, and running this script is the whole fix.
# PAIR, held by hand: the hash warrants the page, not the world in frame.
# That the shot shows the demo's refusal at its line is this script's doing
# (fresh demo, the door below) and no guard reads the pixels; if the demo's
# world changes shape, rerun and look once with your own eyes.
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
# ── AND THE CAMERA IS NOT ALLOWED TO FAIL QUIETLY. Chrome's stderr went to
# /dev/null and nothing asked whether a picture came out, while the stamp below
# is written either way: a failed shot left the OLD picture on disk with a
# fresh "taken from this ui.html" beside it, and the battery, which holds that
# stamp to the working copy, went green over a photograph of a page that no
# longer exists. The one thing this script exists to prevent.
BEFORE=""
[ -f "$HERE/docs/bench.png" ] && BEFORE="$(shasum -a 256 "$HERE/docs/bench.png" | cut -d' ' -f1)"
SHOT_ERR="$(mktemp)"
if ! "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --window-size=1280,800 --force-device-scale-factor=2 --virtual-time-budget=4000 \
    --screenshot="$HERE/docs/bench.png" \
    "http://127.0.0.1:$PORT/?f=ownership.swift:89&view=bare" 2>"$SHOT_ERR"; then
    echo "shoot-bench: the camera refused. What it said:" >&2
    tail -5 "$SHOT_ERR" >&2
    rm -f "$SHOT_ERR"
    exit 1
fi
rm -f "$SHOT_ERR"
[ -f "$HERE/docs/bench.png" ] || { echo "shoot-bench: no picture was written" >&2; exit 1; }
AFTER="$(shasum -a 256 "$HERE/docs/bench.png" | cut -d' ' -f1)"
if [ -n "$BEFORE" ] && [ "$BEFORE" = "$AFTER" ]; then
    echo "shoot-bench: the picture on disk did not change, so nothing was taken" >&2
    exit 1
fi

# a one-pixel black frame, burned into the file: the cover renders on light
# and on dark pages, and a dark picture meeting a dark page with no seam
# reads as a hole. sips ships with macOS, so the frame costs no dependency;
# the shot is 2x, so two file pixels make one seen pixel.
if command -v sips >/dev/null; then
    W=$(sips -g pixelWidth  "$HERE/docs/bench.png" | awk '/pixelWidth/  {print $2}')
    H=$(sips -g pixelHeight "$HERE/docs/bench.png" | awk '/pixelHeight/ {print $2}')
    sips --padToHeightWidth $((H + 4)) $((W + 4)) --padColor 000000 \
        "$HERE/docs/bench.png" >/dev/null
fi

python3 - "$HERE" <<'EOF'
import hashlib, sys, os
here = sys.argv[1]
h = hashlib.sha256(open(os.path.join(here, "web", "ui.html"), "rb").read()).hexdigest()
open(os.path.join(here, "docs", "bench.png.from"), "w").write(
    "web/ui.html sha256:" + h + "\n"
    "door /?f=ownership.swift:89&view=bare over `gate demo`, 1280x800 at 2x\n"
    "retake: bash bin/shoot-bench.sh\n")
print("docs/bench.png over web/ui.html", h[:12])
EOF
