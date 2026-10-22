#!/bin/sh
# One recipe for the pinned wasm carrier and its byte receipt. Source bytes
# come from Git objects; no working-copy build is a publishable input.
set -eu
exec python3 "$(dirname "$0")/build-court-wasm.py" "$@"
