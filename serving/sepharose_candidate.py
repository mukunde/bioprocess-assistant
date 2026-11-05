"""Separate, immutable Protein A/G documentary candidate. No activation API."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re

from demo import troubleshooting as journey

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'experiments/cytiva/reviewed-cleaning-retrieval'
PRODUCTS = ('protein_a', 'protein_g', 'unknown', 'mabselect')
CONTEXTS = ('unknown', 'precipitated_proteins', 'hydrophobic_deposits')
SCOPES = ('Q01', 'Q02', 'Q03', 'Q04', 'Q09')
REQUIRED = {
    'Q01': ['E166-H', 'E166-T'],
    'Q02': ['E166-H', 'E166-PH', 'E166-P'],
    'Q03': ['E166-H', 'E166-LH', 'E166-D'],
    'Q04': ['E166-H', 'E166-LH', 'E166-E', 'E166-W'],
    'Q09': ['E166-H', 'E166-T', 'E166-PH', 'E166-LH', 'E167-H', 'E167-PH', 'E167-SH', 'E167-LH'],
}
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z')
NOTICE = 'CANDIDATE ONLY — NOT ACTIVATED. Documentary fidelity is not operational authorization.'
REVIEW_MANIFEST_SHA = 'a3a6a66e1a7c0541603347264021e11eb3f146018ac3a55828446db95fa6d27c'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def read(path):
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise ValueError('Candidate artifact too large')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate candidate key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('Nonfinite candidate value')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique, parse_constant=invalid)


def material():
    # The existing review verifier anchors source hashes and literal human decisions.
    if sha(ROOT/PACKAGE/'manifest.json') != REVIEW_MANIFEST_SHA:
        raise ValueError('Reviewed package identity changed')
    journey.verify(root=ROOT, package=ROOT/PACKAGE)
    manifest = read(ROOT/PACKAGE/'manifest.json')
    names = {f'{PACKAGE}/manifest.json', 'demo/troubleshooting.py', 'serving/sepharose_candidate.py',
             'demo/chainlit_sepharose.py', 'demo/chainlit_mabselect.py', 'app.py'}
    names.update(manifest['supporting_files'])
    names.update(f'{PACKAGE}/{n}' for n in manifest['files'])
    pins = {name: sha(ROOT/name) for name in sorted(names)}
    evidence = read(ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json')
    review = read(ROOT/PACKAGE/'review.json')
    decisions = {d['question_id']: d for d in review['decisions'] if d['question_id'] in SCOPES}
    registered = set().union(*map(set, REQUIRED.values()))
    passages = {}
    for p in evidence['passages']:
        if p['id'] not in registered:
            continue
        if hashlib.sha256(p['quote'].encode('utf-8')).hexdigest() != p['quote_sha256']:
            raise ValueError('Original quotation changed')
        page = next(x for x in evidence['extraction']['pages'] if x['pdf_page_1based'] == p['pdf_page_1based'])
        passages[p['id']] = dict(deepcopy(p), source_id=p['id'],
            pdf_sha256=evidence['source']['sha256'], document_reference=evidence['source']['document_reference'],
            page_text_sha256=page['text_sha256'], printed_page_label=p['printed_page'],
            offset_unit='unicode_code_points', interval='start_inclusive_end_exclusive',
            extraction_version='pypdf-'+evidence['extraction']['pypdf_version'])
    for scope in SCOPES:
        d = decisions[scope]
        if d['decision'] not in ('validated', 'validated_with_reservation') or set(d['evidence_sha256']) != set(REQUIRED[scope]):
            raise ValueError('Scoped review incomplete')
    mapping = {scope: {'review_scope': scope, 'required_source_ids': REQUIRED[scope],
                      'role': 'clarification_context' if scope == 'Q09' else 'indication' if scope == 'Q01' else 'conditional_option',
                      'pressure_indication_dependency': None if scope in ('Q01', 'Q09') else 'Q01'}
               for scope in SCOPES}
    return pins, {'passages': passages, 'reviews': decisions}, mapping


def prepare(root, release_id='sepharose-backpressure-candidate-v01', *, withheld_sources=(), withheld_reviews=()):
    """Create a new directory only; preserve every existing candidate/authority."""
    if not isinstance(release_id, str) or not ID.fullmatch(release_id):
        raise ValueError('Invalid candidate identifier')
    root = Path(root).resolve()
    protected = [ROOT/'.local-tools/mabselect-registry-v02-runtime']
    if os.environ.get('MABSELECT_REGISTRY_ROOT'):
        protected.append(Path(os.environ['MABSELECT_REGISTRY_ROOT']).resolve())
    if any(root.is_relative_to(p.resolve()) or p.resolve().is_relative_to(root) for p in protected):
        raise ValueError('Candidate must be separate from private authority')
    if root.exists():
        raise ValueError('Candidate exists; choose a new directory')
    pins, sources, mapping = material()
    holds = {'source_ids': sorted(set(withheld_sources)), 'review_ids': sorted(set(withheld_reviews))}
    if not set(holds['source_ids']) <= set(sources['passages']) or not set(holds['review_ids']) <= set(SCOPES):
        raise ValueError('Unknown withdrawal simulation target')
    artifacts = {'sources.json': sources, 'mapping.json': mapping}
    release = {'kind': 'sepharose_documentary_candidate/v1', 'release_id': release_id,
               'stage': 'staged', 'activation': 'not_authorized', 'review_status': 'awaiting_user_review',
               'notice': NOTICE, 'pins_sha256_lf': pins, 'withdrawal_simulations': holds,
               'artifacts_sha256': {n: hashlib.sha256(canonical(v)).hexdigest() for n, v in artifacts.items()}}
    # An incomplete new directory is deliberately retained and refused, never repaired.
    root.mkdir(parents=True, exist_ok=False)
    for name, value in {**artifacts, 'release.json': release}.items():
        with (root/name).open('x', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    return root


def request(value):
    if not isinstance(value, dict) or set(value) != {'product', 'deposit_context', 'guidance', 'pressure'}:
        raise ValueError('Invalid candidate controls')
    if (type(value['product']) is not str or value['product'] not in PRODUCTS
            or type(value['deposit_context']) is not str or value['deposit_context'] not in CONTEXTS
            or any(type(value[k]) is not bool for k in ('guidance', 'pressure'))
            or not (value['guidance'] or value['pressure'])):
        raise ValueError('Invalid candidate controls')
    return deepcopy(value)


class Candidate:
    def __init__(self, root, *, preview=False):
        if root is None or type(preview) is not bool:
            raise ValueError('Explicit candidate root and preview flag required')
        self.root, self.preview = Path(root).resolve(), preview
        self._release_sha = None

    def _snapshot(self):
        if (self.root/'active.json').exists() or (self.root/'authority-log').exists():
            raise ValueError('An active authority is not a candidate')
        release = read(self.root/'release.json')
        release_sha = hashlib.sha256(canonical(release)).hexdigest()
        if self._release_sha is not None and self._release_sha != release_sha:
            raise ValueError('Immutable candidate changed; explicitly prepare and select another version')
        if (set(release) != {'kind', 'release_id', 'stage', 'activation', 'review_status', 'notice',
                            'pins_sha256_lf', 'withdrawal_simulations', 'artifacts_sha256'}
                or release['kind'] != 'sepharose_documentary_candidate/v1'
                or not isinstance(release['release_id'], str) or not ID.fullmatch(release['release_id'])
                or (release['stage'], release['activation'], release['review_status'], release['notice'])
                != ('staged', 'not_authorized', 'awaiting_user_review', NOTICE)):
            raise ValueError('Not a staged candidate')
        pins, sources, mapping = material()
        if release['pins_sha256_lf'] != pins:
            raise ValueError('Candidate dependencies changed; prepare another version')
        for name, expected in (('sources.json', sources), ('mapping.json', mapping)):
            actual = read(self.root/name)
            if actual != expected or hashlib.sha256(canonical(actual)).hexdigest() != release['artifacts_sha256'][name]:
                raise ValueError('Candidate material changed')
        holds = release['withdrawal_simulations']
        if (not isinstance(holds, dict) or set(holds) != {'source_ids', 'review_ids'}
                or any(not isinstance(holds[k], list) or any(type(x) is not str for x in holds[k])
                       or len(set(holds[k])) != len(holds[k]) for k in holds)
                or not set(holds['source_ids']) <= set(sources['passages']) or not set(holds['review_ids']) <= set(SCOPES)):
            raise ValueError('Invalid withdrawal simulation')
        fingerprint = hashlib.sha256(canonical({'release': release, 'sources': sources, 'mapping': mapping})).hexdigest()
        self._release_sha = release_sha
        return release, sources, fingerprint

    def _recheck(self, fingerprint):
        if self._snapshot()[2] != fingerprint:
            raise ValueError('Candidate changed during lookup')

    @staticmethod
    def eligible(scope, holds):
        scopes = [scope] + (['Q01'] if scope in ('Q02', 'Q03', 'Q04') else [])
        return not (set(scopes) & set(holds['review_ids']) or
                    set().union(*(set(REQUIRED[s]) for s in scopes)) & set(holds['source_ids']))

    def evaluate(self, value):
        out = {'kind': 'sepharose_candidate_response/v1', 'stage': 'staged', 'serving_activated': False,
               'notice': NOTICE, 'status': 'unavailable', 'bundles': [], 'citations': [], 'items': [],
               'release_id': None, 'limits': journey.LIMITS.copy()}
        try:
            selected = request(value)
        except ValueError:
            return dict(out, status='invalid_request')
        if not self.preview:
            return out
        try:
            release, sources, token = self._snapshot()
            original = journey.evaluate({'mode': 'troubleshooting', 'product': selected['product'],
                                         'deposit_context': selected['deposit_context']})
            scopes = original['review_scopes'] if selected['guidance'] else []
            holds = release['withdrawal_simulations']
            eligible = [d['question_id'] for d in scopes if self.eligible(d['question_id'], holds)]
            held = [d['question_id'] for d in scopes if d['question_id'] not in eligible]
            out['release_id'] = release['release_id']
            out['submitted'] = selected
            if selected['guidance']:
                state = ('abstained' if selected['product'] == 'mabselect'
                         else 'needs_clarification' if 'Q09' in eligible and original['state'] == 'needs_clarification'
                         else 'partial' if held and eligible else 'quarantined' if held
                         else 'supported')
                out['items'].append({'question': 'guidance', 'state': state, 'held_review_scopes': held})
                for scope in eligible:
                    ids = REQUIRED[scope]
                    option = next((o for o in original['options'] if set(o['source_ids']) == set(ids)), None)
                    # Each summary belongs to its own review; the original message
                    # combines indication and clarification and cannot be reused here.
                    if scope == 'Q01':
                        wording = ('For this product scope, the manual recommends cleaning when backpressure increases. '
                                   'It does not diagnose the cause.')
                    elif scope == 'Q09':
                        if selected['product'] == 'mabselect':
                            wording = ('MabSelect requires its own product-specific route; '
                                       'no Sepharose recipe is transferred.')
                        elif selected['product'] == 'unknown':
                            wording = ('Which exact product is involved? The manual distinguishes product-specific '
                                       'cleaning sections. No recipe has been selected.')
                        else:
                            wording = ('Which deposit context do you want to explore? '
                                       'An established diagnosis is not required, and none is assumed.')
                    else:
                        wording = option['title']
                    out['bundles'].append({'scope': scope, 'role': 'clarification_context' if scope == 'Q09'
                        else 'indication' if scope == 'Q01' else 'conditional_option',
                        'wording': wording,
                        'quote_ids': option['quote_ids'] if option else ['E166-T'] if scope == 'Q01' else [],
                        'required_source_ids': ids, 'review': deepcopy(sources['reviews'][scope]),
                        'passages': [deepcopy(sources['passages'][pid]) for pid in ids]})
            if selected['pressure']:
                out['items'].append({'question': 'pressure', 'state': 'abstained'})
            states = [i['state'] for i in out['items']]
            out['status'] = ('partial' if any(s in ('supported', 'partial') for s in states) and any(s != 'supported' for s in states)
                             else states[0] if len(set(states)) == 1 else 'needs_clarification'
                             if 'needs_clarification' in states else 'quarantined' if 'quarantined' in states else 'abstained')
            ids = sorted({pid for b in out['bundles'] for pid in b['required_source_ids']})
            out['citations'] = [{'release_id': release['release_id'], 'source_id': pid,
                                 'pdf_page_1based': sources['passages'][pid]['pdf_page_1based']} for pid in ids]
            self._recheck(token)
            return out
        except Exception:
            return dict(out, status='unavailable', bundles=[], citations=[], items=[], release_id=None)

    def source(self, release_id, source_id):
        out = {'kind': 'sepharose_candidate_source/v1', 'notice': NOTICE, 'stage': 'staged',
               'serving_activated': False, 'status': 'unavailable', 'passage': None, 'reviews': []}
        if not self.preview:
            return out
        try:
            release, sources, token = self._snapshot()
            if release_id != release['release_id'] or type(source_id) is not str or source_id not in sources['passages']:
                return out
            scopes = [s for s in SCOPES if source_id in REQUIRED[s] and self.eligible(s, release['withdrawal_simulations'])]
            if scopes:
                out.update(status='available', passage=deepcopy(sources['passages'][source_id]),
                           reviews=[deepcopy(sources['reviews'][s]) for s in scopes], release_id=release_id)
            else:
                out['status'] = 'quarantined'
            self._recheck(token)
            return out
        except Exception:
            return dict(out, status='unavailable', passage=None, reviews=[])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--release-id', default='sepharose-backpressure-candidate-v01')
    args = parser.parse_args(argv)
    prepare(args.output, args.release_id)
    print('Separate staged candidate prepared. No activation or approval performed.')


if __name__ == '__main__':
    main()
