#!/bin/sh
# The company's plain court lives in the showcase, with the policy it reads
# (T-0028): this lays its source, its contract and the contract's driver for
# the showcase revision bin/organization-court.from names into
# bin/.court/organization/<pin>/, never committed, and prints that folder.
# The revision is fetched directly rather than by a shallow clone and a
# checkout, which loses an older pin, and the court file's SHA-256 on the
# record's second line is checked apart from the revision. SHOWCASE_SOURCE names a local checkout
# for development, and the folder's own `from` says so.
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
PIN="$(head -1 "$HERE/bin/organization-court.from" | tr -d '[:space:]')"
# the second line names the court file's own bytes, held apart from the revision
WANT="$(sed -n 's/^OrganizationJudge.swift //p' "$HERE/bin/organization-court.from" | tr -d '[:space:]')"
CACHE="$HERE/bin/.court/organization/$PIN"
if [ ! -f "$CACHE/OrganizationJudge.swift" ]; then
    rm -rf "$CACHE"
    if [ -n "${SHOWCASE_SOURCE:-}" ]; then
        SRC="$SHOWCASE_SOURCE"
        NOTE="laid from the local checkout $SHOWCASE_SOURCE, not from the public pin"
        [ "$(git -C "$SRC" rev-parse HEAD)" = "$PIN" ] || {
            echo "organization-court: $SRC is not at $PIN" >&2; exit 1; }
    else
        FETCH=$(mktemp -d)
        git -C "$FETCH" init -q
        # the bytes as committed: a platform that turns LF into CRLF on checkout
        # would hand over a different file than the SHA-256 below names
        git -C "$FETCH" config core.autocrlf false
        git -C "$FETCH" config core.eol lf
        git -C "$FETCH" fetch -q --depth 1 \
            https://github.com/DanielSwift1992/verification-is-identification-showcase "$PIN"
        git -C "$FETCH" checkout -q FETCH_HEAD
        SRC="$FETCH"
        NOTE="laid from the public showcase at $PIN"
    fi
    mkdir -p "$CACHE/Contracts" "$CACHE/Checks"
    cp "$SRC/Sources/Court/OrganizationJudge.swift" "$CACHE/"
    cp -R "$SRC/Contracts/OrganizationCourt" "$CACHE/Contracts/"
    cp "$SRC/Checks/organization-contract.py" "$CACHE/Checks/"
    printf '%s\n%s\n' "$PIN" "$NOTE" > "$CACHE/from"
    [ -n "${FETCH:-}" ] && rm -rf "$FETCH"
fi
GOT="$(shasum -a 256 "$CACHE/OrganizationJudge.swift" | cut -c1-64)"
if [ -n "$WANT" ] && [ "$GOT" != "$WANT" ]; then
    echo "organization-court: OrganizationJudge.swift at $PIN is $GOT, and bin/organization-court.from says $WANT" >&2
    exit 1
fi
echo "$CACHE"
