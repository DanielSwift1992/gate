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
# resolved before any cd: `dirname $0` is relative when the script is
# called as bin/build-judge.sh, and it stops naming this folder the moment
# the shell stands in the clone
OUT="$(cd "$(dirname "$0")" && pwd)"
JUDGE_BUILD=$(mktemp -d "${TMPDIR:-/tmp}/gate-judge.XXXXXX")
trap 'rm -rf "$JUDGE_BUILD"' EXIT HUP INT TERM
# the whole history without file contents: a pin older than any fixed depth
# is still reached, and only the pin's own files are fetched
git clone --filter=blob:none --no-checkout https://github.com/DanielSwift1992/verification-is-identification "$JUDGE_BUILD/vi"
cd "$JUDGE_BUILD/vi" && git checkout "$PIN"
REV=$(git rev-parse HEAD)
python3 "$OUT/publication_origin.py" prepare Sources "$OUT/build-judge.sh" "$JUDGE_BUILD/origin-inputs.json"
swift build -c release --product Tools \
    -Xswiftc -file-prefix-map -Xswiftc "$(pwd -P)=/vi" \
    -Xswiftc -debug-prefix-map -Xswiftc "$(pwd -P)=/vi"
# Prefix maps cover compiler output, but ld64 adds absolute object paths to
# its N_OSO debug map after compilation. Remove debug metadata before the
# publication law reads the actual bytes that will be copied.
case "$(uname -s)" in
    Darwin) strip -S .build/release/Tools; DEBUG_KIND=strip-S ;;
    *) strip --strip-debug .build/release/Tools; DEBUG_KIND=strip-debug ;;
esac
python3 "$OUT/publication_origin.py" seal "$JUDGE_BUILD/origin-inputs.json" .build/release/Tools --mapping source=/vi --debug "$DEBUG_KIND" --inputs-root Sources
python3 "$OUT/../tests/publication-boundary.py" --artifact .build/release/Tools
cp .build/release/Tools "$OUT/gate-judge"
cp .build/release/Tools.origin.json "$OUT/gate-judge.origin.json"
printf '%s\n' "$REV" > "$OUT/gate-judge.from"
echo "bin/gate-judge built from $PIN ($REV)"
