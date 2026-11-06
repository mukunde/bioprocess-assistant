"""Prepare the video players and recorded Flowshot tour from allowlisted assets."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW_FILES = ('index.html', 'demo.json', 'flowshot.js', 'FLOWShot-LICENSE.txt',
              'CREDITS.md', 'shots/01-problem.jpg', 'shots/02-result.jpg',
              'shots/03-citation.jpg', 'shots/04-clarification.jpg')

SEPHAROSE_EXPORTS = {
    'sepharose-chainlit-continuous.mp4': 'b88535ec24223b57c1ca8cf6b3c97811c00d66a497c5470d41ac184d76e14c64',
    'sepharose-chainlit-poster.jpg': '7d77685f03aabee4ea1fcdd6f124a5c974dbffb93d03e0dc3e7d4cabe6be148b',
}


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
    sepharose = ROOT / 'media/chainlit-sepharose-continuous/exports'
    sepharose_files = {'index.html': ROOT / 'site/cytiva-video/sepharose/index.html'}
    for name, digest in SEPHAROSE_EXPORTS.items():
        source = sepharose / name
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise ValueError('Sepharose export hash mismatch: ' + name)
        sepharose_files[name] = source
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
    (output / 'sepharose').mkdir()
    for name, source in sepharose_files.items():
        shutil.copyfile(source, output / 'sepharose' / name)
    files = ['index.html', 'assets/onboarding.mp4', 'assets/onboarding.jpg']
    files += ['flowshot/' + name for name in FLOW_FILES]
    files += ['sepharose/' + name for name in sepharose_files]
    return {'status': 'prepared', 'files': files,
            'bytes': sum(p.stat().st_size for p in output.rglob('*') if p.is_file())}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.local-tools/cytiva-video-site')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.output)))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')
