"""Replay the approved MabSelect design using only portable, immutable artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = {
    'contract': ('docs/technical/mabselect-cleaning-approved-contract-v01.md', '1506c3e1d3045d97b0fa0ee53e81b4a4bb3dbad92093f00e2d0ac6752de61f9c'),
    'dossier': ('docs/technical/mabselect-cleaning-sources-v01.json', 'd536bc2755325c5c5617462d4b5cf3485776703c27eb7ff521c34d5161eb7bf1'),
    'review': ('docs/technical/mabselect-cleaning-review-v01.json', '2386cb3d6d19e454a61c945a7946891e5f269fd133488b2e4335bbedea1627ed'),
}


def verify(root=ROOT):
    root = Path(root).resolve()
    loaded = {}
    for role, (name, expected) in ARTIFACTS.items():
        path = (root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Approved design artifact unavailable: '+role)
        raw = path.read_bytes().replace(b'\r\n', b'\n')
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Approved design artifact changed: '+role)
        loaded[role] = raw
    review = json.loads(loaded['review'])
    if (review['contract_before_review_sha256_lf'] != ARTIFACTS['contract'][1]
            or review['source_dossier_sha256_lf'] != ARTIFACTS['dossier'][1]):
        raise ValueError('Approved design cross-reference mismatch')
    decisions = review['decisions']
    expected_ids = {f'MS{i:02}' for i in range(1,9)} | {f'C{i}' for i in range(1,5)}
    if (len(decisions) != 12 or {d['id'] for d in decisions} != expected_ids
            or any(d['decision'] != 'validated' for d in decisions)):
        raise ValueError('Approved design decision inventory changed')
    ms = dict(re.findall(r'^\| (MS\d\d) \| (.+) \|$', loaded['contract'].decode('utf-8'), re.M))
    if any(ms[d['id']] != d['statement'] for d in decisions if d['id'].startswith('MS')):
        raise ValueError('Approved design statement mismatch')
    return {'status': 'passed', 'decisions': 12, 'portable_artifacts': 3,
            'review_sha256_lf': ARTIFACTS['review'][1],
            'contract_sha256_lf': ARTIFACTS['contract'][1],
            'source_dossier_sha256_lf': ARTIFACTS['dossier'][1],
            'scope': 'application design only; no source or operational approval'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root), indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, str(exc)+'\n')


if __name__ == '__main__':
    main()
