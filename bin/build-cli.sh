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
BUILD=$(mktemp -d)
cp "$HERE/bin/gate-cli.swift" "$BUILD/main.swift"
swiftc -O "$BUILD/main.swift" "$CACHE"/*.swift -o "$HERE/bin/gate-cli"
rm -rf "$BUILD"
echo "built bin/gate-cli (court at $(printf %.7s "$PIN"))"
