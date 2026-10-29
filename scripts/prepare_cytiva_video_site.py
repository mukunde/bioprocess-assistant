"""Prepare a three-file static site from the approved exports, without re-rendering."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def prepare(output):
    output = output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('Choose a new or empty output directory; existing files are preserved')
    package = ROOT / 'media/cytiva-onboarding-v05'
    decision = json.loads((package / 'decisions/human-decision-005.json').read_text(encoding='utf-8'))
    exports = []
    if decision['status'] != 'human_approved':
        raise ValueError('The export must be human-approved')
    for kind in ('video', 'poster'):
        record = decision[kind]
        source = package / 'exports' / record['file']
        if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Approved export hash mismatch: ' + kind)
        exports.append(source)
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'site/cytiva-video/index.html', output / 'index.html')
    for source in exports:
        shutil.copyfile(source, output / 'assets' / source.name)
    return {'status': 'prepared', 'files': ['index.html', 'assets/onboarding.mp4', 'assets/onboarding.jpg'],
            'bytes': sum(p.stat().st_size for p in output.rglob('*') if p.is_file())}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-tools/cytiva-video-site')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.output)))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')
