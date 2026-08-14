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
# PAIR, half-held: the hash warrants the page, and the battery now holds the
# SUBJECT by tripwire (a weight floor against the dead-page class, this
# script's three guards by name). No guard reads the pixels; when the world
# in frame changes shape, rerun and look once with your own eyes.
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

# ── AND THE CAMERA REFUSES WITHOUT ITS SUBJECT. On a fresh clone the shim
# has no binary to stand for, `demo` below would meet its refusal, and the
# EXIT trap once croaked `SERVE: unbound variable` over it: a croak is not a
# refusal. The camera asks the shim first and hands over its own sentence.
if ! "$HERE/gate" --version >/dev/null 2>&1; then
    echo "shoot-bench: the camera needs its subject, and there is no runnable gate here:" >&2
    "$HERE/gate" --version >&2 || true
    exit 1
fi
SERVE=""

WORLD="$(mktemp -d "${TMPDIR:-/tmp}/gate-shoot-XXXXXX")"
trap 'kill $SERVE 2>/dev/null || true; wait $SERVE 2>/dev/null || true; rm -rf "$WORLD"' EXIT
"$HERE/gate" demo "$WORLD" >/dev/null

PORT="$(python3 - <<'EOF'
import socket
s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()
EOF
)"
# ── AND THE SERVER IS LAUNCHED THE WAY A PERSON LAUNCHES IT. This said
# `python3 gate serve`, which was true while the tool was python and became a
# corpse at the death commit: the shim is bash, python3 died on it instantly,
# the wait below timed out IN SILENCE, and Chrome photographed the refusal.
# The cover carried ERR_CONNECTION_REFUSED from the v0.2.0 bump onward, and
# the pair beside the picture stayed green, because it warrants the page, not
# the pixels. Found by an eye on the rendered cover, which no guard replaces.
(cd "$WORLD" && exec "$HERE/gate" serve "$PORT" --no-open >/dev/null 2>&1) &
SERVE=$!
UP=""
for _ in $(seq 40); do
    curl -s "http://127.0.0.1:$PORT/files" >/dev/null 2>&1 && UP=yes && break
    sleep 0.25
done
# a wait that runs out is a refusal, never a fallthrough to the camera
[ -n "$UP" ] || { echo "shoot-bench: the bench never came up on port $PORT, and a camera pointed at a dead port photographs the refusal" >&2; exit 1; }
# and the page in front of the camera is the bench, said by its own text
# grep -c, not -q: under pipefail a -q that quits at the first match kills
# curl with SIGPIPE and the pipeline fails ON success; -c reads to the end
curl -s "http://127.0.0.1:$PORT/" | grep -c "BENCH_FOR" >/dev/null \
    || { echo "shoot-bench: the page on $PORT does not read as the bench" >&2; exit 1; }

mkdir -p "$HERE/docs"
# ── AND THE CAMERA IS NOT ALLOWED TO FAIL QUIETLY. Chrome's stderr went to
# /dev/null and nothing asked whether a picture came out, while the stamp below
# is written either way: a failed shot left the OLD picture on disk with a
# fresh "taken from this ui.html" beside it, and the battery, which holds that
# stamp to the working copy, went green over a photograph of a page that no
# longer exists. The one thing this script exists to prevent.
# ── AND THE GUARD ASKS TODAY'S CAMERA, NOT YESTERDAY'S BYTES. This hashed
# the old picture and refused when the fresh one matched it, which is a
# proxy, and the proxy lied the day the page's holder changed with its
# pixels intact: a legitimate frame read as "nothing was taken". The direct
# question is whether THIS run wrote a frame, so the camera shoots into its
# own scratch, where no file existed, and installs what it can show.
SHOT="$WORLD/bench-shot.png"
SHOT_ERR="$(mktemp)"
if ! "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --window-size=1280,800 --force-device-scale-factor=2 --virtual-time-budget=4000 \
    --screenshot="$SHOT" \
    "http://127.0.0.1:$PORT/?f=ownership.swift:89&view=bare" 2>"$SHOT_ERR"; then
    echo "shoot-bench: the camera refused. What it said:" >&2
    tail -5 "$SHOT_ERR" >&2
    rm -f "$SHOT_ERR"
    exit 1
fi
rm -f "$SHOT_ERR"
[ -s "$SHOT" ] || { echo "shoot-bench: no picture was written" >&2; exit 1; }
# a one-pixel black frame, burned into the file: the cover renders on light
# and on dark pages, and a dark picture meeting a dark page with no seam
# reads as a hole. sips ships with macOS, so the frame costs no dependency;
# the shot is 2x, so two file pixels make one seen pixel.
if command -v sips >/dev/null; then
    W=$(sips -g pixelWidth  "$SHOT" | awk '/pixelWidth/  {print $2}')
    H=$(sips -g pixelHeight "$SHOT" | awk '/pixelHeight/ {print $2}')
    sips --padToHeightWidth $((H + 4)) $((W + 4)) --padColor 000000 \
        "$SHOT" >/dev/null
fi
mv "$SHOT" "$HERE/docs/bench.png"

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
