#!/bin/sh
# builds the company's plain court, the showcase's OrganizationCourt at the pin
# bin/organization-court.from names, into one binary, bin/organization-judge,
# and writes down which revision and which bytes. The door speaks the words
# ShowcaseTools judge and the node port speak: `organization-judge judge FILE…`.
# One file of Foundation and a door, so the build takes seconds and needs
# neither the showcase package nor the theory's.
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$("$HERE/bin/organization-court.sh")"
BUILD=$(mktemp -d)
cat > "$BUILD/main.swift" <<'SWIFT'
import Foundation

// `organization-judge judge FILE…` and `organization-judge judge parse FILE…`:
// the company's plain court, behind the door its other carriers answer to
let arguments = Array(CommandLine.arguments.dropFirst())
guard arguments.first == "judge" else {
    FileHandle.standardError.write(Data("usage: organization-judge judge [parse] FILE…\n".utf8))
    exit(2)
}
OrganizationJudge.run(Array(arguments.dropFirst()))
SWIFT
swiftc -O "$BUILD/main.swift" "$CACHE/OrganizationJudge.swift" -o "$HERE/bin/organization-judge"
rm -rf "$BUILD"
{
    cat "$CACHE/from"
    echo "$(swiftc --version 2>&1 | head -1)"
    (cd "$HERE" && shasum -a 256 bin/organization-judge)
} > "$HERE/bin/organization-judge.from"
echo "bin/organization-judge built from the showcase at $(head -1 "$CACHE/from")"
