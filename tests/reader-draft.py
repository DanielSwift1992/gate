#!/usr/bin/env python3
"""Exercise the delivered draft transport, with and without a site context."""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'bin/build-pages.py'
tree = ast.parse(source.read_text())
shim = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'shim' for t in n.targets)
            and isinstance(n.value, ast.Constant))
subprocess.run(['node', str(ROOT / 'tests/reader-draft.js')], check=True, text=True,
               input=json.dumps(dict(store=(ROOT / 'web/reader-draft.js').read_text(), shim=shim, ui=(ROOT / 'web/ui.html').read_text())))
