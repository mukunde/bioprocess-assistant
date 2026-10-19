"""Verify the curated documentary review; no model, database or publication calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from ingestion.claim_contract import ClaimExtraction, evaluate_conditions
from ingestion.claim_validation import validate_candidate

PACKAGE = Path(__file__).parent / 'reviewed-r2'
FILES = {'README.md', 'claims.json', 'review.json'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_digest(path):
    # Git may check these UTF-8 text files out as CRLF on Windows.
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def claim_digest(claim):
    encoded = json.dumps(claim, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence_refs(value):
    refs = set()
    if isinstance(value, dict):
        for key, item in value.items():
            refs.update(item if key == 'evidence_refs' else evidence_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(evidence_refs(item))
    return refs


def verify(package=PACKAGE, corpus_path=None):
    manifest = read(package / 'manifest.json')
    require(manifest['package_version'] == 1, 'Unsupported package version')
    require(manifest['package_hash_policy'] == 'sha256_utf8_lf', 'Unsupported package hash policy')
    require(set(manifest['files']) == FILES, 'Unexpected package file inventory')
    for name in FILES:
        require(package_digest(package / name) == manifest['files'][name], f'File digest mismatch: {name}')
    raw = read(package / 'claims.json')
    parsed = ClaimExtraction.model_validate(raw)
    review = read(package / 'review.json')
    require(review['candidate_sha256'] == package_digest(package / 'claims.json'), 'Review candidate mismatch')
    require(review['source_candidate_bytes_sha256'] == manifest['local_artifacts']['reviewed_candidate_bytes_sha256'],
            'Original candidate origin mismatch')
    require(review['source_journal_sha256'] == manifest['local_artifacts']['human_review_sha256'],
            'Review origin mismatch')
    claims = {c['id']: c for c in raw['claims']}
    entities = {e['id']: e for e in raw['entities']}
    require(len(claims) == len(raw['claims']) == 33, 'Expected 33 unique claims')
    require(len(entities) == len(raw['entities']) == 47, 'Expected 47 unique entities')
    decisions = {c['claim_id']: c for c in review['claims']}
    require(len(decisions) == len(review['claims']) == 33 and decisions.keys() == claims.keys(),
            'Review coverage mismatch')
    summary = dict(Counter(c['decision'] for c in decisions.values()))
    require(summary == {'validated': 19, 'validated_with_reservation': 14}, 'Unexpected decisions')
    require(review['summary'] == {**summary, 'pending': 0}, 'Review summary mismatch')
    require(manifest['counts'] == {'claims': 33, 'entities': 47, 'validated': 19,
                                 'validated_with_reservation': 14, 'pending': 0}, 'Manifest counts mismatch')
    require(review['review_complete'] is True and review['publication_allowed'] is False,
            'Review completion does not authorize publication')
    source_index = manifest['source']['evidence_index']
    require(evidence_refs(raw) == set(source_index), 'Evidence index mismatch')
    for cid, claim in claims.items():
        decision = decisions[cid]
        require(decision['claim_sha256'] == claim_digest(claim), f'Changed reviewed claim: {cid}')
        require(bool(decision['reservations']) == (decision['decision'] == 'validated_with_reservation'),
                f'Reservation mismatch: {cid}')
        require(decision['reviewer'] == 'user' and bool(decision['decided_at_utc']), 'Missing human decision')
        require(claim['disposition'] == 'review_required', 'Staging state must not be promoted')
        require(claim['subject_id'] in entities, 'Unknown claim subject')
        require(all(e in entities for e in claim['scope']['product_ids'] + claim['scope']['process_step_ids']),
                'Unknown scope entity')
    byid = {c.id: c for c in parsed.claims}
    for probe in manifest['checks']['condition_probes']:
        result = evaluate_conditions(byid[probe['claim_id']].condition_groups, probe['context'])
        require(result is probe['expected'], f'Condition probe failed: {probe["claim_id"]}')
    source_replayed = False
    if corpus_path is not None:
        require(digest(corpus_path) == manifest['source']['input_sha256'], 'Wrong source corpus')
        corpus = read(corpus_path)
        validation = validate_candidate(raw, corpus)
        require(validation['structural_pass'] and not validation['errors'], 'Source validation failed')
        require(validation['publication_allowed'] is False, 'Source validator unexpectedly allows publication')
        items = {e['item_ref']: e for e in corpus['elements']}
        for ref, entry in source_index.items():
            require(entry['text_sha256'] == hashlib.sha256(items[ref]['text'].encode('utf-8')).hexdigest(),
                    'Source text mismatch')
        source_replayed = True
    return {'status': 'passed', 'claims': 33, 'validated': 19, 'validated_with_reservation': 14,
            'pending': 0, 'publication_allowed': False, 'source_validation_replayed': source_replayed,
            'condition_probes': len(manifest['checks']['condition_probes'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, help='Optional original local input.json; exact hash required')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(corpus_path=args.corpus)))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'Package verification failed: {error}\n')


if __name__ == '__main__':
    main()
