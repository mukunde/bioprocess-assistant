"""Selector-backed documentary staging preview: python -m demo.documentary_preview."""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re

from demo.documentary import Handoff, canonical


def source_html(view):
    p = view['passage']
    if p is None:
        return b'<!doctype html><title>Source held</title><h1>Source held in quarantine</h1><a href="/">Return to preview</a>'
    esc = lambda value: html.escape(str(value), quote=True)
    reviews = ''.join('<section><h2>'+esc(d['question_id'])+' — scoped documentary review</h2><ul>'+ ''.join('<li>'+esc(s)+'</li>' for s in d['reservations'])+'</ul><details><summary>Original decision and bindings</summary><pre>'+esc(json.dumps(d,ensure_ascii=False,indent=2))+'</pre></details></section>' for d in view['reviews'])
    return ('<!doctype html><meta charset="utf-8"><title>'+esc(p['source_id'])+' · Cytiva source</title>'
            '<style>body{font:17px/1.6 system-ui;max-width:900px;margin:32px auto;padding:0 20px}pre,blockquote{white-space:pre-wrap;overflow-wrap:anywhere}blockquote{border-left:4px solid teal;padding:16px;background:#f0f8f7}a{color:#08656d}details{background:#f5f5f5;padding:12px}</style>'
            '<p>DEVELOPMENT PREVIEW · NOT AN ACTIVATED SERVING RELEASE</p><a href="/">Return to preview</a><h1>'+esc(p['source_id'])+' · PDF page '+esc(p['pdf_page_1based'])+'</h1><p>'+esc(p['scope'])+'</p><blockquote>'+esc(p['quote'])+'</blockquote>'
            '<p>Original PDF is not served here. Excerpt identity is verified against the reviewed snapshot; this is not a new visual or scientific validation.</p><details><summary>Page, offsets and source provenance</summary><pre>'+esc(json.dumps(p,ensure_ascii=False,indent=2))+'</pre></details>'+reviews).encode('utf-8')


def handler_for(service):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_args):
            pass

        def reply(self, status, data, content_type='application/json; charset=utf-8'):
            body = data if isinstance(data, bytes) else canonical(data)
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def host_allowed(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

        def do_GET(self):
            if not self.host_allowed():
                self.reply(403, {'error':'Use the loopback preview'}); return
            if self.path == '/':
                self.reply(200, (Path(__file__).parent/'static/documentary.html').read_bytes(), 'text/html; charset=utf-8'); return
            match = re.fullmatch(r'/reviewed/v1/releases/([A-Za-z0-9._-]+)/sources/([A-Za-z0-9._-]+)', self.path)
            if not match:
                self.reply(404, {'error':'Unregistered page'}); return
            try:
                view = service.source(*match.groups())
                self.reply(200, source_html(view), 'text/html; charset=utf-8')
            except KeyError:
                self.reply(404, {'error':'Unregistered source'})
            except (OSError, ValueError):
                self.reply(503, {'error':'Staged source integrity unavailable; no quotation delivered'})

        def do_POST(self):
            expected = 'http://' + self.headers.get('Host', '')
            if not self.host_allowed() or self.headers.get('Origin', expected) != expected:
                self.reply(403, {'error':'Use the local preview'}); return
            if self.path != '/api/reviewed/v1/evaluate':
                self.reply(404, {'error':'Unknown endpoint'}); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 32768 or self.headers.get_content_type() != 'application/json':
                    raise ValueError('Send at most 32,768 bytes of JSON')
                def unique(pairs):
                    result = {}
                    for key, value in pairs:
                        if key in result: raise ValueError('Duplicate JSON key')
                        result[key] = value
                    return result
                def reject_constant(_): raise ValueError('Non-finite JSON number')
                data = json.loads(self.rfile.read(length).decode('utf-8'), object_pairs_hook=unique, parse_constant=reject_constant)
                result = service.evaluate(data)
                self.reply(400 if result['kind']=='reviewed_serving_validation_error/v1' else 200, result)
            except (ValueError, UnicodeError):
                self.reply(400, {'kind':'reviewed_serving_validation_error/v1','request_id':None,
                                 'errors':[{'code':'invalid_type','request_pointer':''}]})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8783)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535: parser.error('Choose a port from 1 to 65535')
    service = Handoff(preview=True)  # Explicit staging, not creation/activation of a serving release.
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(service))
    server.daemon_threads = True
    print(f'Documentary handoff staging preview: http://127.0.0.1:{server.server_port}/', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__':
    main()
