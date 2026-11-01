"""Prepare the video player and recorded Flowshot tour from allowlisted assets."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW_FILES = ('index.html', 'demo.json', 'flowshot.js', 'FLOWShot-LICENSE.txt',
              'CREDITS.md', 'shots/01-problem.jpg', 'shots/02-result.jpg',
              'shots/03-citation.jpg', 'shots/04-clarification.jpg')


def flowshot_assets():
    package = ROOT / 'media/cytiva-flowshot-pilot-v02'
    manifest = json.loads((package / 'package-manifest.json').read_text(encoding='utf-8'))
    for name in FLOW_FILES:
        source = package / name
        raw = source.read_bytes()
        digest = hashlib.sha256(raw if name.endswith('.jpg') else raw.replace(b'\r\n', b'\n')).hexdigest()
        if digest != manifest['files_sha256_lf_or_raw'][name]:
            raise ValueError('Flowshot asset hash mismatch: ' + name)
    return package


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
    flowshot = flowshot_assets()
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'site/cytiva-video/index.html', output / 'index.html')
    for source in exports:
        shutil.copyfile(source, output / 'assets' / source.name)
    for name in FLOW_FILES:
        destination = output / 'flowshot' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if name == 'index.html':
            html = (flowshot / name).read_text(encoding='utf-8')
            html = html.replace('BIOPROCESS ASSISTANT · LOCAL PILOT', 'BIOPROCESS ASSISTANT · RECORDED WALKTHROUGH')
            html = html.replace('Four-screen evaluation only · not published', 'Four-screen recorded walkthrough')
            html = html.replace('<footer>', '<footer><a href="../">Watch the video</a> · <a href="CREDITS.md">Credits and provenance</a><br>')
            destination.write_text(html, encoding='utf-8')
        else:
            shutil.copyfile(flowshot / name, destination)
    return {'status': 'prepared', 'files': ['index.html', 'assets/onboarding.mp4', 'assets/onboarding.jpg'] + ['flowshot/' + name for name in FLOW_FILES],
            'bytes': sum(p.stat().st_size for p in output.rglob('*') if p.is_file())}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-tools/cytiva-video-site')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.output)))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')
