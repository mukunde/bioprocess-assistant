"""Offline startup checks and foreground server for the Windows launcher."""
import argparse
import hashlib
from http.server import HTTPServer
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

from experiments.cytiva.free_text_v03_freeze import ROOT, PACKAGE, verify


def check(root=ROOT):
    """Use metadata only: no model, package installation or tokenizer download."""
    root = Path(root).resolve()
    errors = []
    try:
        frozen = verify(root)
        lock = json.loads((root/PACKAGE/'method-lock.json').read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError) as exc:
        return {'ready': False, 'python': sys.executable,
                'errors': ['Frozen v03 baseline invalid: '+str(exc)],
                'remedy': 'Restore the pinned files from the reviewed commit; do not regenerate the lock.'}
    env = lock['environment']
    actual_python = platform.python_version()
    if actual_python != env['python_version']:
        errors.append(f"Python: expected {env['python_version']}, found {actual_python}.")
    for name, expected in env['dependencies'].items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f'Dependency {name}: expected {expected}, not installed.')
        else:
            if actual != expected:
                errors.append(f'Dependency {name}: expected {expected}, found {actual}.')
    asset = (root/env['tokenizer_asset_file']).resolve()
    if not asset.is_relative_to(root):
        errors.append('Tokenizer asset path is outside the project.')
    elif not asset.is_file():
        errors.append('Offline tokenizer cache missing: '+env['tokenizer_asset_file'])
    elif hashlib.sha256(asset.read_bytes()).hexdigest() != env['tokenizer_asset_sha256']:
        errors.append('Offline tokenizer cache hash does not match the freeze.')
    if not errors:
        try:
            frozen = verify(root, environment=True)
        except (OSError, ValueError, KeyError, importlib.metadata.PackageNotFoundError) as exc:
            errors.append('Environment verification failed: '+str(exc))
    return {'ready': not errors, 'python': sys.executable, 'python_version': actual_python,
            'dependency_count': len(env['dependencies']), 'freeze': frozen, 'errors': errors,
            'remedy': 'Use the prepared verification environment or restore the exact versions and offline cache recorded in '+str(PACKAGE/'method-lock.json')+'. Nothing is installed or downloaded automatically.'}


def serve(port):
    # Import the engine only after all read-only checks pass.
    try:
        from demo.cytiva import Demo, handler_for
        demo = Demo()
    except (ImportError, OSError, ValueError, RuntimeError) as exc:
        print('Local runtime could not start: '+type(exc).__name__+'. '
              'Check the recorded environment and offline cache. No server was started.', file=sys.stderr)
        return 3
    try:
        server = HTTPServer(('127.0.0.1', port), handler_for(demo))
    except OSError:
        print(f'Cannot listen on 127.0.0.1:{port}. The port may already be in use. '
              'Keep the existing server, stop it with Ctrl+C, or use -Port with another port.', file=sys.stderr)
        return 2
    print(f'Cytiva demo ready: http://127.0.0.1:{server.server_port}/\n'
          'Local only. No model or paid API. Leave this terminal open; Ctrl+C stops the demo.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535.')
    if args.json and not args.check:
        parser.error('--json requires --check.')
    report = check()
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print('Startup checks passed.' if report['ready'] else 'Startup checks failed.')
        for error in report['errors']:
            print(' - '+error)
        if not report['ready']:
            print(report['remedy'])
    if not report['ready']:
        return 1
    if args.check:
        return 0
    return serve(args.port)


if __name__ == '__main__':
    raise SystemExit(main())
