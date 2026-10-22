#!/usr/bin/env python3
"""Apply the pinned owner law to this repository's declared policy."""
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'tests/dependency-boundary.json'
POLICY_SHA256 = 'ef9e6a741c8bbfd4a72a1381137d50c6313b6334c2f86379ef00a84c9a1d7c08'
specification = importlib.util.spec_from_file_location('boundary_owner', ROOT / 'bin/boundary-owner.py')
owner = importlib.util.module_from_spec(specification)
specification.loader.exec_module(owner)
try:
    OWNER_INPUTS = owner.verified_inputs(ROOT)
except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
    raise SystemExit(owner.refusal(error))
exec(compile(OWNER_INPUTS['Checks/boundary-law.py'], 'vi:Checks/boundary-law.py', 'exec'), globals())

if __name__ == '__main__':
    sys.exit(run())
