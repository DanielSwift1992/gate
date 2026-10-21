#!/usr/bin/env python3
"""The Drawing closure is declared by row identity, independent of file names."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

CLI = Path(__file__).resolve().parents[1] / 'bin/gate-cli'


def run():
    with tempfile.TemporaryDirectory(prefix='gate-drawing-inputs-') as tmp:
        root = Path(tmp)
        header = '\n'.join('public protocol ' + n + ' {}' for n in ['Role', 'Mine', 'Theirs']) + '\n'
        header += '\n'.join('public enum ' + n + ': Role {}' for n in ['DocumentFile', 'WorldFile', 'CarriedFile']) + '\n'
        rows = [('Page', 'DocumentFile', 'A.swift', 'Data'),
                ('Data', 'WorldFile', 'B.swift', 'Support'),
                ('Support', 'CarriedFile', 'C.swift', ''),
                ('Unused', 'CarriedFile', 'DrawingInput.swift', '')]
        for _, _, path, _ in rows:
            (root / path).write_text('public enum Leaf {}\n')

        def write(selected):
            text = header
            for name, kind, path, dependencies in selected:
                text += 'public enum ' + name + ': Mine {\n    public typealias Kind = ' + kind + '\n'
                if dependencies:
                    text += '    public typealias DrawingInputs = ' + dependencies + '\n'
                text += '}\nextension ' + name + ' {\n    public static var typeName: String { ' + json.dumps(path) + ' }\n}\n'
            (root / 'gate.manifest.swift').write_text(text)

        sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
        write(rows)
        proc = subprocess.Popen([str(CLI), 'serve', str(port), '--no-open'], cwd=root,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            def read():
                for attempt in range(100):
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/files', timeout=5) as response:
                            return json.load(response)
                    except OSError:
                        assert proc.poll() is None
                        if attempt == 99: raise
                        time.sleep(.03)
            answer = read()
            assert answer['documents'] == ['A.swift'], answer
            assert answer['drawing_inputs'] == ['A.swift', 'B.swift', 'C.swift'], answer
            assert answer['world_files'] == ['B.swift'], answer
            assert answer['drawing_input_refusals'] == [], answer
            # Any name/path works; a plausible filename does not add an input.
            renamed = [('Picture', 'DocumentFile', 'A.swift', 'Facts'),
                       ('Facts', 'WorldFile', 'B.swift', 'Support'), *rows[2:]]
            write(renamed)
            assert read()['drawing_inputs'] == answer['drawing_inputs']
            controls = [
                ('missing', [('Page', 'DocumentFile', 'A.swift', 'Absent'), *rows[1:]], 'missing'),
                ('repeated', [('Page', 'DocumentFile', 'A.swift', '(Data, Data)'), *rows[1:]], 'repeats'),
                ('cycle', [rows[0], ('Data', 'WorldFile', 'B.swift', 'Page'), *rows[2:]], 'cycle'),
                ('expression', [('Page', 'DocumentFile', 'A.swift', 'Other<Data>'), *rows[1:]], 'needs one manifest row'),
                ('duplicate axis', [('Page', 'DocumentFile', 'A.swift', 'Data\n    public typealias DrawingInputs = Support'), *rows[1:]], 'declared once'),
                ('ambiguous row', [*rows, ('Data', 'CarriedFile', 'Other.swift', '')], 'ambiguous'),
            ]
            for label, selected, expected in controls:
                write(selected)
                failures = read()['drawing_input_refusals']
                assert any(expected in f['claim'] and f['address'].startswith('gate.manifest.swift:') for f in failures), (label, failures)
            write(rows[1:])
            assert read()['drawing_inputs'] == []
        finally:
            proc.terminate(); proc.wait(timeout=10)
    print('DRAWING INPUTS GREEN: declared transitive closure, stable Kind, no filename selection, six addressed refusals')


if __name__ == '__main__':
    run()
