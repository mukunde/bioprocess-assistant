"""Explicit installation step; the launcher and frozen engine stay offline."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import tempfile
import urllib.request
import venv

from experiments.cytiva.free_text_v03_freeze import ROOT, PACKAGE, verify

TOKENIZER_URL = 'https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken'
MAX_TOKENIZER_BYTES = 4 * 1024 * 1024


def run(args, *, root=ROOT):
    subprocess.run([str(x) for x in args], cwd=root, check=True)


def validate_requirements(root, environment):
    requirements = root / 'demo/requirements-windows.lock'
    entries = {}
    for line in requirements.read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([\w-]+)==([^ ]+) --hash=sha256:([0-9a-f]{64})', line)
        if not match or match[1] in entries:
            raise ValueError('Invalid or duplicate dependency in demo requirements lock')
        entries[match[1]] = match[2]
    if entries != environment['dependencies']:
        raise ValueError('Demo dependencies differ from frozen v03')
    return requirements


def prepare_tokenizer(root, environment, *, offline=False, source=None):
    target = (root / environment['tokenizer_asset_file']).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Tokenizer destination is outside the clone')
    expected = environment['tokenizer_asset_sha256']
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Existing tokenizer is corrupt; inspect/remove it before retrying')
        return 'already_verified'
    if source:
        data = Path(source).read_bytes()
    elif offline:
        raise ValueError('Offline setup needs --tokenizer-file when the cache is absent')
    else:
        with urllib.request.urlopen(TOKENIZER_URL, timeout=60) as response:
            data = response.read(MAX_TOKENIZER_BYTES + 1)
    if len(data) > MAX_TOKENIZER_BYTES or hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Tokenizer content/hash mismatch; no cache was published')
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.replace(temporary, target)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return 'copied_verified' if source else 'downloaded_verified'


def install(root=ROOT, *, offline=False, wheelhouse=None, tokenizer_file=None):
    root = Path(root).resolve()
    verify(root)  # Check the source freeze before creating anything.
    environment = json.loads((root/PACKAGE/'method-lock.json').read_text(encoding='utf-8'))['environment']
    if (os.name != 'nt' or platform.machine().lower() not in ('amd64', 'x86_64')
            or struct.calcsize('P') != 8 or platform.python_version() != environment['python_version']):
        raise ValueError('This installer requires Windows x64 and CPython '+environment['python_version'])
    requirements = validate_requirements(root, environment)
    if wheelhouse and not Path(wheelhouse).is_dir():
        raise ValueError('Wheelhouse directory not found')
    target = root / '.venv-demo'
    if target.is_symlink() or target.is_junction():
        raise ValueError('Demo environment must not be a link to another environment')
    python = target / 'Scripts/python.exe'
    if target.exists():
        config = target / 'pyvenv.cfg'
        if (not config.is_file() or not python.is_file()
                or not re.search(r'^include-system-site-packages\s*=\s*false\s*$',
                                 config.read_text(), re.M | re.I)):
            raise ValueError('Existing .venv-demo is not an isolated venv; it was not changed')
        probe = subprocess.check_output([str(python), '-c', 'import platform; print(platform.python_version())'], text=True).strip()
        if probe != environment['python_version']:
            raise ValueError('Existing .venv-demo has the wrong Python; it was not changed')
    else:
        venv.EnvBuilder(with_pip=True).create(target)
    probe = subprocess.run([str(python), '-m', 'demo.launch', '--check', '--json'],
                           cwd=root, capture_output=True, text=True, check=False)
    if probe.returncode == 0:
        print('Already ready. Existing isolated environment and cache verified.')
        return
    # All dependencies, including transitives, are explicit; do not resolve extras.
    args = [python, '-m', 'pip', '--isolated', '--disable-pip-version-check', 'install',
            '--require-hashes', '--only-binary=:all:', '--no-deps', '-r', requirements]
    if offline or wheelhouse:
        if not wheelhouse:
            raise ValueError('Offline dependency installation needs --wheelhouse')
        args += ['--no-index', '--find-links', Path(wheelhouse).resolve()]
    else:
        args += ['--index-url', 'https://pypi.org/simple']
    run(args, root=root)
    run([python, '-m', 'pip', '--isolated', '--disable-pip-version-check', 'check'], root=root)
    state = prepare_tokenizer(root, environment, offline=offline, source=tokenizer_file)
    run([python, '-m', 'demo.launch', '--check', '--json'], root=root)
    print('Setup complete. Tokenizer: '+state+'. Run .\\Start-CytivaDemo.ps1')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--wheelhouse', type=Path)
    parser.add_argument('--tokenizer-file', type=Path)
    args = parser.parse_args(argv)
    try:
        install(offline=args.offline, wheelhouse=args.wheelhouse, tokenizer_file=args.tokenizer_file)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print('Setup failed: '+str(exc)+'. Frozen v03 was not changed.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
