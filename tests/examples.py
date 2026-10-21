"""The one-file installation names its resources the same way on every host."""
import contextlib
import hashlib
import io
import json
import os
import re
from pathlib import Path
import runpy
import sys
from unittest.mock import patch
ROOT = Path(__file__).resolve().parent.parent


def run(script=ROOT / 'bin/shelf-into-swift.py'):
    script = Path(script)
    argv = [str(script), str(ROOT / 'stdlib'), (ROOT / 'bin/gate-judge.from').read_text().strip()]
    native_relpath = os.path.relpath
    def generated(windows=False):
        output = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        # Only the relative-path result changes; source bytes and filesystem
        # reads are real. This catches resource keys that work only on POSIX.
        reported = lambda *a, **k: native_relpath(*a, **k).replace('/', '\\') if windows else native_relpath(*a, **k)
        with patch.object(sys, 'argv', argv), patch.object(os.path, 'relpath', reported), contextlib.redirect_stdout(output):
            runpy.run_path(str(script), run_name='__main__')
        output.flush()
        return output.buffer.getvalue()
    normal = generated()
    windows = generated(True)
    assert b'"examples/index.json":' in normal
    recipes = json.loads((ROOT / 'examples/index.json').read_text())
    declared = {'examples/index.json'} | {'examples/' + recipe + '/' + name
        for recipe, files in recipes.items() for name in files}
    carried = {name.decode() for name in re.findall(rb'^    "(examples/[^\"]+)":', normal, re.M)}
    assert carried == declared, 'the binary must carry exactly the declared recipe inputs'
    assert windows == normal, 'Windows relative paths lost or renamed installed example resources'
    print('EXAMPLES GREEN: portable resource keys; shelf sha256 ' + hashlib.sha256(normal).hexdigest())

if __name__ == '__main__':
    run()
