#!/bin/sh
# The worlds have one home. This fetches the two revisions their record names;
# the builder and the battery both read the checked cache this door prints.
set -eu
HERE="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$HERE/bin/playground-worlds.py"
