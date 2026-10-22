#!/usr/bin/env python3
"""Quote failed Pages steps and describe the outcomes the runner recorded."""
import argparse
import json
import os
from pathlib import Path

# These IDs belong to the pages job; source commands and logs are named there.
STEPS = (
    ('checkout', 'checkout', None),
    ('build_cli', 'gate binary build', 'pages-cli.txt'),
    ('build_site', 'build-pages.py', 'pages-build.txt'),
    ('roadtest', 'roadtest.py', 'pages-roadtest.txt'),
    ('upload', 'artifact upload', None),
    ('site', 'Pages configuration', None),
    ('deployment', 'deployment', None),
)


def escaped(text):
    return text.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')


def failure_report(steps, directory):
    outcomes = {key: steps.get(key, {}).get('outcome', 'not recorded') for key, _, _ in STEPS}
    failed = [(key, name, log) for key, name, log in STEPS if outcomes[key] == 'failure']
    annotations = []
    for key, name, log in failed:
        if log:
            path = directory / log
            if path.is_file():
                # Read the tail in bytes as well: a verbose child cannot make
                # the diagnostic reader allocate its entire build transcript.
                with path.open('rb') as stream:
                    stream.seek(0, 2)
                    stream.seek(max(0, stream.tell() - 16000))
                    tail = ''.join(stream.read().decode('utf-8', errors='replace').splitlines(keepends=True)[-40:])[-4000:]
                text = tail or log + ': the failed step wrote no output'
            else:
                text = log + ': the failed step did not write its log'
            annotations.append('::error title=what pages ' + name + ' said::' + escaped(text))
    first = failed[0][1] if failed else 'unrecorded step'
    description = (first + ' failed; site=' + outcomes['build_site'] + '; roadtest=' + outcomes['roadtest']
                   + '; upload=' + outcomes['upload'] + '; deploy=' + outcomes['deployment'])[:138]
    return annotations, dict(state='failure', description=description)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--status', required=True, type=Path)
    args = parser.parse_args()
    # This command is called only by the workflow's failure() step.
    annotations, status = failure_report(json.loads(os.environ['PAGES_STEPS']), Path.cwd())
    status['context'] = args.context
    for annotation in annotations:
        print(annotation)
    args.status.write_text(json.dumps(status) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
