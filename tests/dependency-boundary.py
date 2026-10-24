#!/usr/bin/env python3
"""Apply the pinned owner law to this repository's declared policy."""
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'tests/dependency-boundary.json'
POLICY_SHA256 = 'a46622847bb081317515c9bc6ec34acc096f0faff308d21b2f9be34003dfa9dd'
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
