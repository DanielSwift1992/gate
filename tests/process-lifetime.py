#!/usr/bin/env python3
"""A Process handler is published before launch and never replaced afterwards.

The extracted shipping helper is compiled against a lifecycle witness: run()
marks publication and a handler write after it is an immediate failure. This
checks the ordering relation, including completion inside run(), not the chance
of seeing a crash in repeated native runs. The source guard covers this file's
zero-argument run/launch calls and Process's convenience launch spellings.
"""
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
source = (ROOT / 'bin/gate-cli.swift').read_text()
start = source.index('func startProcess(')
end = source.index('\nfunc runGitBytes', start)
helper = source[start:end].strip()


def one_launch(text):
    calls = list(re.finditer(r'\.\s*(?:run|launch)\s*\(\s*\)', text))
    assert len(calls) == 1 and start <= calls[0].start() < end, 'Process launch outside startProcess'
    assert not re.search(r'Process\s*\.\s*(?:run|launchedProcess)\s*\(', text), 'Process convenience launch bypasses startProcess'
    writes = list(re.finditer(r'\.terminationHandler\s*=', text))
    assert len(writes) == 1 and start <= writes[0].start() < end, 'handler written outside startProcess'


one_launch(source)
for mutation in ('\np.run()\n', '\np.launch()\n', '\nProcess.run(url, arguments: [])\n',
                 '\np.terminationHandler = nil\n'):
    try:
        one_launch(source + mutation)
    except AssertionError:
        pass
    else:
        raise AssertionError('launch/handler bypass escaped the source guard')

witness = r'''
import Dispatch

enum LaunchError: Error { case refused }
final class Process {
    enum Completion { case insideRun, afterRun, failedRun }
    let completion: Completion
    var published = false
    var writes = 0
    var terminationHandler: (@Sendable (Process) -> Void)? {
        willSet {
            precondition(!published, "handler changed after publication")
            writes += 1
        }
    }
    init(_ completion: Completion) { self.completion = completion }
    func run() throws {
        precondition(terminationHandler != nil, "launch before handler")
        published = true
        if completion == .failedRun { throw LaunchError.refused }
        if completion == .insideRun { terminationHandler!(self) }
    }
    func finish() { terminationHandler!(self) }
}
'''
checks = r'''
for schedule: Process.Completion in [.insideRun, .afterRun] {
    let p = Process(schedule)
    let done = try startProcess(p)
    if schedule == .afterRun { p.finish() }
    precondition(done.wait(timeout: .now() + 1) == .success, "completion lost")
    precondition(p.writes == 1, "handler replaced")
}
let failed = Process(.failedRun)
do {
    _ = try startProcess(failed)
    preconditionFailure("launch refusal lost")
} catch LaunchError.refused {
    precondition(failed.writes == 1)
}
'''
variants = {
    'shipping': helper,
    'launch-before-handler': helper.replace('    try p.run()\n', '').replace(
        '    let done = DispatchSemaphore(value: 0)', '    try p.run()\n    let done = DispatchSemaphore(value: 0)'),
    'reset-after-launch': helper.replace('    return done', '    p.terminationHandler = nil\n    return done'),
}
with tempfile.TemporaryDirectory(prefix='gate-process-lifetime-') as temp:
    folder = Path(temp)
    for name, body in variants.items():
        swift = folder / 'main.swift'
        swift.write_text(witness + '\n' + body + '\n' + checks)
        binary = folder / ('witness.exe' if os.name == 'nt' else 'witness')
        built = subprocess.run(['swiftc', str(swift), '-o', str(binary)], capture_output=True, text=True)
        assert built.returncode == 0, built.stdout + built.stderr
        ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
        if name == 'shipping':
            assert ran.returncode == 0, ran.stdout + ran.stderr
        else:
            reason = 'launch before handler' if name == 'launch-before-handler' else 'handler changed after publication'
            assert ran.returncode != 0 and reason in ran.stderr, name + ': witness did not refuse ordering mutation'
print('PROCESS LIFETIME GREEN: pre-launch handler; early/late/failed launch; no replacement or bypass')
