"""Opt-in presentation v02; unchanged registry service, authority and source routes."""
from pathlib import Path
from . import registry_ui as baseline
from . import registry_tracing


def handler_for(registry, tracing=None):
    tracing = tracing or registry_tracing.Tracing()
    observed = registry_tracing.ObservedRegistry(registry, tracing)

    class Handler(baseline.handler_for(observed)):
        def end_headers(self):
            trace_id = tracing.current().trace_id()
            if trace_id is not None:
                self.send_header('X-Trace-Id', trace_id)
            super().end_headers()

        def reply(self, status, data, content_type='application/json; charset=utf-8'):
            span = tracing.current()
            span.attributes({'http.response.status_code': status})
            if status >= 500:
                span.attributes({'bioprocess.outcome': 'unavailable'})
                span.error('http_server_error')
            elif status >= 400:
                span.attributes({'bioprocess.outcome': 'invalid_request'})
            return super().reply(status, data, content_type)

        def do_GET(self):
            with tracing.span('GET ' + registry_tracing.route(self.path), root=True,
                              attributes={'http.request.method': 'GET',
                                          'http.route': registry_tracing.route(self.path)}):
                self.serve_get()

        def do_POST(self):
            with tracing.span('POST ' + registry_tracing.route(self.path), root=True,
                              attributes={'http.request.method': 'POST',
                                          'http.route': registry_tracing.route(self.path)}):
                super().do_POST()

        def serve_get(self):
            if self.path == '/' and self.host_allowed():
                self.reply(200, (Path(__file__).parent/'static/registry-v02.html').read_bytes(),
                           'text/html; charset=utf-8')
            else:
                super().do_GET()
    return Handler


def create_server(data_root, port=8785, *, tracing=None):
    if data_root is None:
        raise ValueError('An explicit server-side registry root is required')
    server = baseline.ThreadingHTTPServer(('127.0.0.1', port),
                                          handler_for(baseline.Registry(data_root), tracing))
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = baseline.argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry-root', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8785)
    parser.add_argument('--trace-file', type=Path,
                        help='Optional new local metadata-only JSONL file; never overwritten')
    parser.add_argument('--trace-otlp-endpoint',
                        help='Optional literal-loopback OTLP/HTTP URL ending in /v1/traces')
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 to 65535')
    tracing = registry_tracing.configure(trace_file=args.trace_file,
                                         otlp_endpoint=args.trace_otlp_endpoint,
                                         protected_root=args.registry_root)
    try:
        server = create_server(args.registry_root, args.port, tracing=tracing)
    except BaseException:
        tracing.close()
        raise
    print(f'Opt-in MabSelect presentation v02: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        tracing.close()


if __name__ == '__main__':
    main()
