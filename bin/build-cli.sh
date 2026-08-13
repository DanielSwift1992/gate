#!/usr/bin/env bash
# Builds the tool: one binary, from one Swift file, with the court compiled
# in. The judge sources at the pin beside the judge binary
# (bin/gate-judge.from) are fetched the way bin/build-judge.sh fetches,
# cached per pin under bin/.court/<pin>/ (never committed), and compiled
# straight into the vein. No module artifact crosses a toolchain boundary:
# the cache is four source files, and a cache that matches the pin builds
# offline. The shelf is written into the build beside them, so the binary
# carries its own pages. It is not committed, because every executable line
# in this repository stays text: a clone without swiftc takes one from the
# releases, and `gate` says so in a sentence when it finds neither.
set -euo pipefail

# ── AND THE PATHS ARE THE PLATFORM'S OWN. This script runs under a shell that
# speaks posix paths, and on windows it drives a compiler that does not: given
# `/tmp/tmp.XXXX/main.swift` the toolchain reads what it can and then the linker
# cannot create its own scratch file, which is what `cannot open file
# lnk{...}.tmp` means. Nothing is wrong with the source at that point. So on
# that platform the paths are asked for in its own spelling, and the build
# directory is made inside the clone rather than in a temp the compiler cannot
# find.
WINDOWS=""
EXT=""
LINK=""
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        WINDOWS="yes"
        EXT=".exe"
        # the bench's socket calls live in winsock, and the linker is told the
        # library by name
        LINK="-lws2_32"
        ;;
esac

# ── AND THE COMPILER IS HANDED A TEMP IT CAN OPEN. The shell here keeps `TMP`
# in its own spelling (`/tmp`), the linker takes that at its word, and it fails
# to create `lnk{...}.tmp` in a directory that does not exist for it. Measured
# rather than guessed: the job printed `TMP=/tmp TEMP=/tmp` beside 147G free and
# a temp that exists, which named the spelling as the whole of the problem.
if [ -n "$WINDOWS" ] && command -v cygpath >/dev/null 2>&1; then
    NATIVE_TMP="$(cygpath -w "${RUNNER_TEMP:-${TMP:-/tmp}}" 2>/dev/null || true)"
    if [ -n "$NATIVE_TMP" ]; then
        export TMP="$NATIVE_TMP"
        export TEMP="$NATIVE_TMP"
    fi
fi

HERE="$(cd "$(dirname "$0")/.." && pwd)"
PIN="$(cat "$HERE/bin/gate-judge.from" | tr -d '[:space:]')"
CACHE="$HERE/bin/.court/$PIN"
if [ ! -d "$CACHE" ]; then
    # ── AND THE FETCH DOES NOT TAKE THE COMPILER'S NAME. This directory was
    # called `TMP`, which is the variable the linker reads for its own scratch:
    # on a runner, where the cache is never warm, the fetch overwrote the
    # spelling handed over above and the link failed exactly as before. One
    # name, two meanings, and the second one silent.
    FETCH=$(mktemp -d)
    git clone --depth 50 -q https://github.com/DanielSwift1992/verification-is-identification "$FETCH/vi"
    git -C "$FETCH/vi" checkout -q "$PIN"
    mkdir -p "$CACHE"
    cp "$FETCH/vi/Sources/Court/"*.swift "$CACHE/"
    rm -rf "$FETCH"
fi

# top-level statements are legal only in a file named main.swift when more
# than one file is compiled, so the vein's source keeps its name in the
# tree and wears main.swift for the length of the build
if [ -n "$WINDOWS" ]; then
    BUILD="$HERE/bin/.build"
    rm -rf "$BUILD"
    mkdir -p "$BUILD"
else
    BUILD=$(mktemp -d)
fi
cp "$HERE/bin/gate-cli.swift" "$BUILD/main.swift"

# ── AND THE SHELF TRAVELS INSIDE THE BINARY. The tool reads stdlib/ off the
# disk beside it, which is true in a clone and false for everybody who
# downloads one file: `gate demo` there asks for stdlib/manifest.swift and
# stops, holding half a directory it already made. The pages are written into
# the build as text and compiled in, so the sentence "one binary" is literal.
# A clone still reads the disk first, so editing a page is still editing a
# page; the snapshot is the fallback, and the battery holds the two equal.
python3 "$HERE/bin/shelf-into-swift.py" "$HERE/stdlib" "$PIN" > "$BUILD/shelf.swift"

if [ -n "$WINDOWS" ]; then
    # the same three places, spelled the way that toolchain reads them
    SAID="$(cd "$HERE" && pwd -W)"
    swiftc -O "$SAID/bin/.build/main.swift" "$SAID/bin/.build/shelf.swift" \
        "$SAID/bin/.court/$PIN"/*.swift $LINK \
        -o "$SAID/bin/gate-cli$EXT"
else
    swiftc -O "$BUILD/main.swift" "$BUILD/shelf.swift" "$CACHE"/*.swift \
        -o "$HERE/bin/gate-cli$EXT"
fi
rm -rf "$BUILD"
echo "built bin/gate-cli$EXT (court at $(printf %.7s "$PIN"))"
