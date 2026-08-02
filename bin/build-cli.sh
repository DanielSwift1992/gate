#!/usr/bin/env bash
# Builds the Swift CLI vein binary beside the python CLI. One file in, one
# binary out, not committed: a clone without swiftc runs the python side of
# every vein and loses nothing. The battery builds this on every run where
# a toolchain exists and holds both CLIs to the same bytes.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
swiftc -O "$HERE/bin/gate-cli.swift" -o "$HERE/bin/gate-cli"
echo "built bin/gate-cli"
