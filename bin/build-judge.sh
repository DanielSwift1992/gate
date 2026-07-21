#!/bin/sh
# builds the judge from the public theory corpus and drops it into bin/
set -e
PIN=${1:-main}
TMP=$(mktemp -d)
git clone --depth 50 https://github.com/DanielSwift1992/verification-is-identification "$TMP/vi"
cd "$TMP/vi" && git checkout "$PIN"
swift build -c release --product Tools
cp .build/release/Tools "$(dirname "$0")/gate-judge"
echo "bin/gate-judge built from $PIN"
