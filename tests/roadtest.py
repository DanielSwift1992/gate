#!/usr/bin/env python3
"""Walk a selected example in a disposable delivery, never in the product HTML."""
import argparse
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bin'))
from bench_csp import stamp_csp


def run(browser=None, site=None):
    browser = browser or next((p for p in [shutil.which('google-chrome'), shutil.which('chromium-browser'),
        shutil.which('chromium'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] if p and Path(p).is_file()), None)
    if not browser:
        raise SystemExit('roadtest: headless Chrome/Chromium is required')
    with tempfile.TemporaryDirectory(prefix='gate-road-') as temp:
        root = Path(temp); original = Path(site) if site else None; site = root / 'site'
        if original:
            shutil.copytree(original, site)
        else:
            subprocess.run([sys.executable, str(ROOT / 'bin/build-pages.py'), str(site),
                            '--source', str(ROOT / 'examples/codeowners')], check=True)
        page = site / 'index.html'; text = page.read_text()
        assert 'roadtest=1' not in text and 'ROAD ALL GREEN' not in text
        marker = '    /* the wipe and the reload'
        assert text.count(marker) == 1
        # Inject inside the snapshot closure only in this disposable harness.
        # No debug endpoint or test globals are added to a delivered page.
        text = text.replace(marker, (ROOT / 'tests/roadtest.js').read_text() + marker)
        page.write_text(stamp_csp(text))
        result = subprocess.run([browser, '--headless', '--disable-gpu', '--no-sandbox',
            '--user-data-dir=' + str(root / 'chrome'), '--virtual-time-budget=15000', '--dump-dom',
            page.as_uri() + '?f=ownership.swift:84&roadtest=1'], capture_output=True, text=True, timeout=90)
        if result.returncode or 'ROAD ALL GREEN' not in result.stdout or 'ROADFAIL' in result.stdout.split('<pre id="roadtest-report">')[-1]:
            print(result.stderr[-2000:], file=sys.stderr)
            start = result.stdout.rfind('<pre id="roadtest-report">')
            print(result.stdout[start:start+4000] if start >= 0 else 'roadtest: no report', file=sys.stderr)
            raise SystemExit('roadtest: the example did not reach ROAD ALL GREEN')
        report = result.stdout.rsplit('<pre id="roadtest-report">', 1)[-1].split('</pre>', 1)[0]
        print(report.replace('\\n', '\n'))
        print('ROAD ALL GREEN (external harness)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--browser');parser.add_argument('--site')
    args = parser.parse_args();run(args.browser, args.site)
