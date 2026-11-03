"""Opt-in presentation v02; unchanged registry service, authority and source routes."""
from pathlib import Path
from . import registry_ui as baseline


def handler_for(registry):
    class Handler(baseline.handler_for(registry)):
        def do_GET(self):
            if self.path == '/' and self.host_allowed():
                self.reply(200, (Path(__file__).parent/'static/registry-v02.html').read_bytes(),
                           'text/html; charset=utf-8')
            else:
                super().do_GET()
    return Handler


def create_server(data_root, port=8785):
    if data_root is None:
        raise ValueError('An explicit server-side registry root is required')
    server = baseline.ThreadingHTTPServer(('127.0.0.1', port),
                                          handler_for(baseline.Registry(data_root)))
    server.daemon_threads = True
    return server


def main(argv=None):
    parser = baseline.argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry-root', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8785)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 to 65535')
    server = create_server(args.registry_root, args.port)
    print(f'Opt-in MabSelect presentation v02: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
