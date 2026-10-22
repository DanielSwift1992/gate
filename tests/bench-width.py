#!/usr/bin/env python3
"""Measure finished benches, keeping overflowing source inside its scroll surface.

An iframe supplies the exact viewport: headless Chrome's outer window may have
a platform minimum width. The harness and its mutation never ship in the site.
"""
import functools
import html
import http.server
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]


def run(site):
    site = Path(site).resolve()
    browser = next((p for p in [shutil.which('google-chrome'), shutil.which('chromium-browser'),
        shutil.which('chromium'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
        if p and Path(p).is_file()), None)
    assert browser, 'bench width: headless Chrome/Chromium is required'
    pages = ['/' + p.relative_to(site).as_posix().removesuffix('index.html')
             for p in sorted(site.rglob('index.html'))]
    assert '/' in pages and '/playground/basics/' in pages, 'measure the root and showcase delivery'
    harness = ('<!doctype html><iframe id="bench" style="border:0;height:800px"></iframe>'
               '<pre id="width-report"></pre><script>const pages = ' + json.dumps(pages) + ';\n'
               + (ROOT / 'tests/bench-width.js').read_text() + '</script>')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/__bench_width__':
                body = harness.encode()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
        functools.partial(Handler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix='gate-width-chrome-') as temp:
            result = subprocess.run([browser, '--headless', '--disable-gpu', '--no-sandbox',
                '--user-data-dir=' + temp, '--virtual-time-budget=60000', '--dump-dom',
                'http://127.0.0.1:%d/__bench_width__' % server.server_port],
                capture_output=True, text=True, timeout=120)
            match = re.search(r'<pre id="width-report">(.*?)</pre>', result.stdout, re.S)
            assert result.returncode == 0 and match and match[1], (
                'bench width: no completed geometry report\n' + result.stderr[-2000:])
            report = json.loads(html.unescape(match[1]))
            assert not report.get('error'), 'bench width: ' + report.get('error', '')
            assert report['pages'] == len(pages) and report['negative']['detected'], report
            print('BENCH WIDTH GREEN: ' + json.dumps(report, sort_keys=True))
            return report
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    import sys
    run(sys.argv[1])
