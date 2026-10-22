"""Run the world contracts with an explicit deadline and public phase receipt."""
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


def run_playground(command, timeout):
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


def summary(output, elapsed=None):
    """The beginning of an annotation must survive GitHub's short window."""
    phases, slow = [], []
    for line in output.splitlines():
        if line.startswith('PLAYGROUND PHASE '):
            try:
                row = json.loads(line[len('PLAYGROUND PHASE '):])
                phases.append(str(row['phase']) + ': ' + str(row.get('duration_seconds', row.get('seconds', '?'))) + 's')
            except (ValueError, KeyError, TypeError):
                pass
        elif line.startswith('PLAYGROUND PASS '):
            try:
                name, seconds = line[len('PLAYGROUND PASS '):].rsplit(' ', 1)
                slow.append((float(seconds[:-1] if seconds.endswith('s') else seconds), name))
            except (ValueError, TypeError):
                pass
    lines = ['playground: ' + (str(round(elapsed, 3)) + 's; ' if elapsed is not None else '') + progress(output)]
    lines += ['phase ' + phase[:240] for phase in phases]
    lines += ['slow ' + str(round(seconds, 3)) + 's ' + name[:180] for seconds, name in sorted(slow, reverse=True)[:5]]
    return '\n'.join(lines)


def annotation(output, elapsed=None):
    def escape(text):
        return text.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    def fit(text, budget, tail=False):
        used, chars = 0, []
        for char in (reversed(text) if tail else text):
            size = len(escape(char).encode('utf-8'))
            if used + size > budget:
                break
            chars.append(char); used += size
        return ''.join(reversed(chars) if tail else chars)
    prefix = '::error title=playground contracts::'
    head = fit(summary(output, elapsed), 2400)
    separator = '\nlast output:\n'
    budget = 4096 - len((prefix + escape(head + separator)).encode('utf-8'))
    tail = fit('\n'.join(output.split('\n')[-30:]), max(0, budget), tail=True)
    return prefix + escape(head + separator + tail)


def main():
    import argparse
    from pathlib import Path
    import sys
    import time
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, required=True)
    parser.add_argument('--log', type=Path, required=True)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    started = time.monotonic()
    answer = run_playground([sys.executable, str(Path(__file__).with_name('playground.py'))], args.timeout)
    elapsed = time.monotonic() - started
    output = answer.stdout + answer.stderr
    args.log.write_text(output, encoding='utf-8')
    print(output, end='', flush=True)
    print(summary(output, elapsed), flush=True)
    if answer.returncode:
        print(annotation(output, elapsed), flush=True)
    else:
        print('PASS the pinned playground worlds keep their drawings, courts and separate state', flush=True)
    return answer.returncode


if __name__ == '__main__':
    raise SystemExit(main())
