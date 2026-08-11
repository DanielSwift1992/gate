#!/usr/bin/env bash
# Builds the Swift CLI vein binary beside the python CLI, with the court
# compiled in: the judge sources at the pin beside the judge binary
# (bin/gate-judge.from) are fetched the way bin/build-judge.sh fetches,
# cached per pin under bin/.court/<pin>/ (never committed), and compiled
# straight into the vein. No module artifact crosses a toolchain boundary:
# the cache is four source files, and a cache that matches the pin builds
# offline. The binary is not committed: a clone without swiftc runs the
# python side of every vein and judges through bin/gate-judge, losing
# nothing.
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

HERE="$(cd "$(dirname "$0")/.." && pwd)"
PIN="$(cat "$HERE/bin/gate-judge.from" | tr -d '[:space:]')"
CACHE="$HERE/bin/.court/$PIN"
if [ ! -d "$CACHE" ]; then
    TMP=$(mktemp -d)
    git clone --depth 50 -q https://github.com/DanielSwift1992/verification-is-identification "$TMP/vi"
    git -C "$TMP/vi" checkout -q "$PIN"
    mkdir -p "$CACHE"
    cp "$TMP/vi/Sources/Court/"*.swift "$CACHE/"
    rm -rf "$TMP"
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

if [ -n "$WINDOWS" ]; then
    # the same three places, spelled the way that toolchain reads them
    SAID="$(cd "$HERE" && pwd -W)"
    swiftc -O "$SAID/bin/.build/main.swift" "$SAID/bin/.court/$PIN"/*.swift $LINK \
        -o "$SAID/bin/gate-cli$EXT"
else
    swiftc -O "$BUILD/main.swift" "$CACHE"/*.swift -o "$HERE/bin/gate-cli$EXT"
fi
rm -rf "$BUILD"
echo "built bin/gate-cli$EXT (court at $(printf %.7s "$PIN"))"
