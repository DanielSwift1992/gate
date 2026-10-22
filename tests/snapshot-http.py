"""A broken local snapshot names its request and the selected server's output."""
import importlib.util
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
from snapshot_http import read, SnapshotFailure


def run():
    class Broken(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/answer':
                self.send_response(200); self.end_headers(); self.wfile.write(b'local')
            elif self.path == '/refusal':
                self.send_response(409); self.end_headers()
                self.wfile.write(b'Palette.swift:12: selected input refused')
            else:
                # Consume the declared POST body before the deliberate EOF.
                # Unread bytes can make close reset TCP instead of ending HTTP.
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                self.close_connection = True
        do_POST = do_GET
        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Broken)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    port = server.server_port
    try:
        ambient = {key: os.environ.get(key) for key in ['HTTP_PROXY', 'http_proxy', 'NO_PROXY', 'no_proxy']}
        try:
            os.environ.update(HTTP_PROXY='http://127.0.0.1:1', http_proxy='http://127.0.0.1:1', NO_PROXY='', no_proxy='')
            assert read(port, '/answer') == b'local', 'a snapshot must not depend on an ambient external proxy'
        finally:
            for key, value in ambient.items():
                if value is None: os.environ.pop(key, None)
                else: os.environ[key] = value
        for path, body, cause in [('/status', None, 'RemoteDisconnected'),
                                  ('/verdict?f=Page.swift', b'public enum A {}', 'RemoteDisconnected'),
                                  ('/drawing-assets/abc', None, 'RemoteDisconnected'),
                                  ('/refusal', None, 'Palette.swift:12')]:
            try:
                read(port, path, body)
            except SnapshotFailure as error:
                message = str(error)
                assert ('POST' if body is not None else 'GET') + ' http://127.0.0.1:' + str(port) + path in message
                assert cause in message, message
            else:
                raise AssertionError('a dropped or refused request became an answer')
    finally:
        server.shutdown(); server.server_close(); thread.join()

    spec = importlib.util.spec_from_file_location('pages_snapshot_test', ROOT / 'bin/build-pages.py')
    pages = importlib.util.module_from_spec(spec); spec.loader.exec_module(pages)
    with tempfile.TemporaryDirectory(prefix='snapshot-failed-server-') as directory:
        source = Path(directory)
        fake = source / 'gate'
        fake.write_text('#!' + sys.executable + '''
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
class Reader(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/files':
            self.send_response(200); self.end_headers(); self.wfile.write(b'{}')
        else:
            print('fixture: selected server dropped the request', file=sys.stderr, flush=True)
            self.close_connection = True
    def log_message(self, *args): pass
HTTPServer(('127.0.0.1', int(sys.argv[2])), Reader).serve_forever()
''')
        fake.chmod(0o755); pages.GATE = str(fake)
        out = source / 'site'
        try:
            pages.publish(str(source), str(out))
        except SnapshotFailure as error:
            message = str(error)
            assert str(source) in message and 'GET http://127.0.0.1:' in message and '/language' in message, message
            assert 'RemoteDisconnected' in message and 'fixture: selected server dropped the request' in message, message
            assert not out.exists(), 'a failed snapshot must not publish HTML'
        else:
            raise AssertionError('publication concealed its failed snapshot')
    print('SNAPSHOT HTTP GREEN: local GET, POST and assets name their failed address; publication keeps server diagnostics')


if __name__ == '__main__':
    run()
