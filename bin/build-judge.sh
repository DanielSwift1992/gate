#!/bin/sh
# builds the judge from the public theory corpus and drops it into bin/
#
# AND WRITES DOWN WHICH REVISION IT CAME FROM. The judge's identity is its
# bytes, and that is what a reviewer reproduces — but bytes alone do not say
# what they were made from, so `we depend on the corpus` was stated as an opaque
# hash nobody could check without guessing the revision first. The commit is
# recorded beside the binary; anyone may build at it and compare.
set -e
PIN=${1:-main}
TMP=$(mktemp -d)
git clone --depth 50 https://github.com/DanielSwift1992/verification-is-identification "$TMP/vi"
cd "$TMP/vi" && git checkout "$PIN"
REV=$(git rev-parse HEAD)
swift build -c release --product Tools
OUT="$(cd "$(dirname "$0")" && pwd)"
cp .build/release/Tools "$OUT/gate-judge"
printf '%s\n' "$REV" > "$OUT/gate-judge.from"
echo "bin/gate-judge built from $PIN ($REV)"
