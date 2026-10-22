"""A fixed wall clock for the composite, with its last phase on refusal."""
import json
import os
import signal
import subprocess


def progress(output):
    phase, active = 'before the first phase', []
    for line in output.splitlines():
        if line.startswith('PLAYGROUND BEGIN '):
            try:
                phase = json.loads(line[len('PLAYGROUND BEGIN '):])['phase']
                active = []
            except (ValueError, KeyError, TypeError):
                pass
        elif line.startswith('PLAYGROUND START '):
            active.append(line[len('PLAYGROUND START '):])
        elif line.startswith('PLAYGROUND PASS '):
            finished = line[len('PLAYGROUND PASS '):].rsplit(' ', 1)[0]
            active = [name for name in active if name != finished]
    return phase + ('; active: ' + ', '.join(active) if active else '')


def run_playground(command, timeout=1200):
    # One pipe preserves the order of phase boundaries and native/browser
    # diagnostics. All original child output travels, including tracebacks.
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, start_new_session=(os.name != 'nt')) as child:
        try:
            output, _ = child.communicate(timeout=timeout)
            return subprocess.CompletedProcess(command, child.returncode, output, '')
        except subprocess.TimeoutExpired:
            # Do not release the battery while descendants are still judging.
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            else:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            output, _ = child.communicate()
            reason = '\nplayground composite probe exceeded ' + str(timeout) + ' seconds; phase: ' + progress(output) + '\n'
            return subprocess.CompletedProcess(command, 124, output, reason)
