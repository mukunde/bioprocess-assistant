"""Explicit loopback UI for an existing active registry; never prepares or activates it."""
import argparse
import html
from http.server import ThreadingHTTPServer
import json
import logging
from pathlib import Path
import re

from demo.documentary_preview import handler_for as preview_handler
from serving.local_registry import Registry

LOGGER = logging.getLogger(__name__)


def source_html(view):
    esc = lambda value: html.escape(str(value), quote=True)
    prefix = ('<!doctype html><html lang="en"><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1">'
              '<title>Cytiva · Registered source</title><style>body{font:17px/1.6 system-ui;'
              'max-width:900px;margin:32px auto;padding:0 20px;color:#19343c}'
              'pre,blockquote{white-space:pre-wrap;overflow-wrap:anywhere}'
              'blockquote{border-left:4px solid #087b80;padding:16px;background:#eef8f7}'
              'a{color:#08656d}details{background:#f4f6f7;padding:12px}</style>'
              '<p>LOCAL REGISTRY · CURRENT WITHDRAWAL AUTHORITY CHECKED</p>'
              '<a href="/">Return to MabSelect registry</a>')
    if view.get('status') != 'available' or view.get('passage') is None:
        return (prefix+'<h1>Source held</h1><p>This source has no eligible scope under '
                'the current authority. No quotation is delivered.</p></html>').encode('utf-8')
    passage = view['passage']
    reviews = ''.join('<section><h2>'+esc(d['question_id'])+' · scoped review</h2><ul>'
                      + ''.join('<li>'+esc(s)+'</li>' for s in d['reservations'])
                      + '</ul><details><summary>Original decision and bindings</summary><pre>'
                      + esc(json.dumps(d, ensure_ascii=False, indent=2))+'</pre></details></section>'
                      for d in view['reviews'])
    return (prefix+'<h1>'+esc(passage['source_id'])+' · PDF page '
            +esc(passage['pdf_page_1based'])+'</h1><p>'+esc(passage['scope'])
            +'</p><blockquote>'+esc(passage['quote'])+'</blockquote><p>Release: '
            +esc(view['release_id'])+'. Original PDF is not served here. Documentary '
            'fidelity does not establish operational suitability.</p><details><summary>'
            'Page, offsets and source provenance</summary><pre>'
            +esc(json.dumps(passage, ensure_ascii=False, indent=2))+'</pre></details>'
            +reviews+'</html>').encode('utf-8')


def handler_for(registry):
    # Reuse the frozen HTTP request contract and loopback/origin protections.
    # The service supplied here is always Registry; no Handoff/preview fallback.
    class Handler(preview_handler(registry)):
        def end_headers(self):
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'")
            self.send_header('Referrer-Policy', 'no-referrer')
            super().end_headers()

        def do_GET(self):
            if not self.host_allowed():
                self.reply(403, {'error': 'Use the loopback registry UI'}); return
            if self.path == '/':
                self.reply(200, (Path(__file__).parent/'static/registry.html').read_bytes(),
                           'text/html; charset=utf-8'); return
            match = re.fullmatch(r'/reviewed/v1/releases/([A-Za-z0-9._-]+)/sources/([A-Za-z0-9._-]+)', self.path)
            if not match:
                self.reply(404, {'error': 'Unregistered page'}); return
            release_id, source_id = match.groups()
            try:
                view = registry.source(release_id, source_id)  # No candidate override.
                body = source_html(view)  # Render fully before sending any headers/body.
            except Exception as error:
                # A KeyError inside authority validation is not proof of an unknown source.
                unknown = False
                if isinstance(error, KeyError):
                    try:
                        with registry.lock:
                            current = registry._snapshot()
                            target = (current if current['release']['release_id'] == release_id
                                      else registry._load(release_id))
                            unknown = not any(p['source_id'] == source_id
                                              for p in target['sources']['passages'])
                    except Exception:
                        pass  # Unverifiable authority must remain unavailable.
                if unknown:
                    self.reply(404, {'error': 'Unregistered source'})
                else:
                    LOGGER.error('Registry UI source failure (%s)', type(error).__name__)
                    self.reply(503, {'error': 'Registry source unavailable; no quotation delivered'})
            else:
                self.reply(200, body, 'text/html; charset=utf-8')
    return Handler


def create_server(data_root, port=8784):
    if data_root is None:
        raise ValueError('An explicit server-side registry root is required')
    server = ThreadingHTTPServer(('127.0.0.1', port), handler_for(Registry(data_root)))
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry-root', type=Path, required=True,
                        help='Existing local authority directory; never created or activated here')
    parser.add_argument('--port', type=int, default=8784)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 to 65535')
    server = create_server(args.registry_root, args.port)
    print(f'Opt-in MabSelect registry UI: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
