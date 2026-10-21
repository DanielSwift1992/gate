"""Migration evidence only. Never imported by the publisher."""
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def materialize():
    spec = importlib.util.spec_from_file_location('worlds_history', ROOT / 'bin/playground-worlds.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    record = ROOT / 'tests/fixtures/playground-baseline.from'
    pin = json.loads(record.read_text())['baseline']['revision']
    return module.materialize_record(record, ROOT / 'bin/.worlds/history' / pin,
        [('baseline', 'typed-playground', 'PLAYGROUND_SOURCE')]) / 'baseline'
