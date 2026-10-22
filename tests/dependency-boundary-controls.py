#!/usr/bin/env python3
"""Exercise the pinned owner controls against this repository's policy."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
specification = importlib.util.spec_from_file_location('boundary', ROOT / 'tests/dependency-boundary.py')
law = importlib.util.module_from_spec(specification)
specification.loader.exec_module(law)
exec(compile(law.OWNER_INPUTS['Checks/boundary-controls.py'], 'vi:Checks/boundary-controls.py', 'exec'), globals())

if __name__ == '__main__':
    controls(law)
    specification = importlib.util.spec_from_file_location('owner_controls', ROOT / 'tests/boundary-owner.py')
    owner_controls = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(owner_controls)
    owner_controls.controls(law.owner)
