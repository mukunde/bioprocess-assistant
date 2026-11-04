"""Separate local guidance/source/trace entry; never prepares or activates authority."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import uuid

from . import registry_ui_v02, registry_tracing, trace_summary

PANEL = b'''<aside class="panel"><strong>Request &rarr; source &rarr; trace</strong>
<p>After submitting guidance or opening a citation,
<a href="/demo/traces">view the local trace summary</a>. Only metadata is shown;
source views have separate traces. Refresh after exports arrive.</p></aside>'''


def check_authority(data_root):
    """Use the registry's own read-only validator, not synthetic approvals."""
    registry = registry_ui_v02.baseline.Registry(data_root)
    with registry.lock:
        registry._snapshot()


def create_server(data_root, trace_file, port=8786, *, tracing=None):
    if data_root is None:
        raise ValueError('An explicit approved authority root is required')
    authority = Path(data_root).resolve()
    filename = Path(trace_file).resolve()
    if filename.is_relative_to(authority):
        raise ValueError('Trace session must be outside authority')
    server = registry_ui_v02.create_server(data_root, port=port, tracing=tracing)
    original = server.RequestHandlerClass

    class Handler(original):
        def reply(self, status, data, content_type='application/json; charset=utf-8'):
            if self.command == 'GET' and self.path == '/' and status == 200 and isinstance(data, bytes):
                data = data.replace(b'<div class="grid">', PANEL+b'<div class="grid">', 1)
            return super().reply(status, data, content_type)

        def do_GET(self):
            if self.path != '/demo/traces':
                return super().do_GET()
            if not self.host_allowed():
                self.reply(403, {'error': 'Use the loopback demo'})
                return
            try:
                body = trace_summary.html_summary(trace_summary.read_summary(filename))
            except Exception:
                # View failures never mutate authority or interrupt later guidance.
                self.reply(503, trace_summary.html_summary(unavailable=True), 'text/html; charset=utf-8')
                return
            self.reply(200, body, 'text/html; charset=utf-8')

    server.RequestHandlerClass = Handler
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry-root', type=Path, required=True)
    parser.add_argument('--trace-dir', type=Path, default=Path('.local-tools/telemetry'))
    parser.add_argument('--port', type=int, default=8786)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 to 65535')
    authority, directory = args.registry_root.resolve(), args.trace_dir.resolve()
    if directory.is_relative_to(authority):
        parser.error('Choose a trace directory outside authority')
    try:
        check_authority(authority)
    except Exception:
        print('Approved local authority unavailable or invalid. Nothing was activated or repaired.')
        return 2
    try:
        importlib.metadata.version('opentelemetry-sdk')
    except importlib.metadata.PackageNotFoundError:
        print('Optional OpenTelemetry SDK missing; guidance will run without traces. See the demo guide.')
    except Exception:
        print('Optional SDK metadata unavailable; continuing with the safe tracing configuration.')
    filename = directory / ('registry-demo-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                            +'-'+uuid.uuid4().hex[:12]+'.jsonl')
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        print('Trace directory unavailable; guidance will continue without a local summary.')
    tracing = registry_tracing.configure(trace_file=filename, protected_root=authority)
    try:
        server = create_server(authority, filename, port=args.port, tracing=tracing)
    except Exception:
        tracing.close()
        print('Demo could not bind the local server. Check the port and retry.')
        return 2
    print(f'Local guidance: http://127.0.0.1:{server.server_port}/', flush=True)
    print(f'Trace summary: http://127.0.0.1:{server.server_port}/demo/traces', flush=True)
    print(f'Local session: {filename}', flush=True)
    print('No model calls. No activation. Ctrl+C stops the demo.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        tracing.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
