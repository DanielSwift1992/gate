#!/usr/bin/env python3
"""Negative controls for acquisition; the law itself belongs to its owner."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch


def controls(owner):
    root = Path(__file__).resolve().parents[1]
    pin = owner.read_pin(root)
    inputs = owner.verified_inputs(root)
    with tempfile.TemporaryDirectory(prefix='boundary-input-controls-') as temporary:
        fixture = Path(temporary)
        (fixture / 'bin').mkdir()

        def write_pin(value):
            (fixture / owner.PIN).write_text(json.dumps(value) + '\n')

        def refuses(label, action, expected=None):
            try:
                action()
            except (ValueError, OSError, subprocess.SubprocessError) as error:
                message = owner.refusal(error)
                assert message.count(owner.PIN + ':1:') == 1, message
                assert str(fixture) not in message and 'CalledProcessError' not in message
                if expected:
                    assert expected in message, message
                print('CONTROL owner-' + label + ': refused\n  ' + message)
            else:
                raise AssertionError(label + ' acquired an undeclared owner')

        write_pin(pin)
        cache = fixture / 'bin/.inputs/boundary-law' / pin['revision']
        for name, raw in inputs.items():
            target = cache / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        assert owner.verified_inputs(fixture) == inputs
        print('CONTROL owner-verified-cache: holds')
        changed = copy.deepcopy(pin)
        changed['revision'] = 'main'
        write_pin(changed)
        refuses('moving-reference', lambda: owner.verified_inputs(fixture))
        changed = copy.deepcopy(pin)
        changed['files'].pop(owner.FILES[0])
        write_pin(changed)
        refuses('missing-input-row', lambda: owner.verified_inputs(fixture))
        write_pin(pin)
        target = cache / owner.FILES[0]
        target.write_bytes(inputs[owner.FILES[0]] + b'\n# altered bytes\n')
        refuses('corrupt-cache-no-fallback', lambda: owner.verified_inputs(fixture))
        target.write_bytes(inputs[owner.FILES[0]])
        unrelated = fixture / 'unrelated'
        subprocess.run(['git', 'init', '--quiet', str(unrelated)], check=True)
        refuses('missing-commit-no-worktree-fallback', lambda: owner.verified_inputs(fixture, unrelated), 'publish the declared owner commit or pass --repository')
        target.unlink()
        with patch.object(owner.subprocess, 'run', side_effect=subprocess.CalledProcessError(128, ['git', str(fixture)])):
            refuses('unavailable-public-commit', lambda: owner.verified_inputs(fixture), 'owner commit unavailable')
        (fixture / owner.PIN).unlink()
        refuses('missing-pin', lambda: owner.verified_inputs(fixture))
    print('OWNER INPUT CONTROLS GREEN')
