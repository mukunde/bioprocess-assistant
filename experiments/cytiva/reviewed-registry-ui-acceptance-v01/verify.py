"""Verify the compact historical UI trial offline; never instantiate the runtime."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REL = Path('experiments/cytiva/reviewed-registry-ui-acceptance-v01')
PREP = Path('experiments/cytiva/registry-ui-acceptance-v01')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def verify(root=ROOT):
    root = Path(root); folder = root/REL; prep = root/PREP
    manifest = load(folder/'manifest.json')
    for path, expected in manifest['files_sha256_lf'].items():
        require(digest(folder/path) == expected, 'Package hash: '+path)
    for path, expected in manifest['preparation_files_sha256_lf'].items():
        require(digest(prep/path) == expected, 'Preparation hash: '+path)
    lock = load(prep/'method-lock.json')
    for path, expected in lock['files_sha256_lf'].items():
        require(digest(root/path) == expected, 'Baseline hash: '+path)
    review = load(prep/'review.json'); questions = load(prep/'questions.json')['cases']
    refs = load(prep/'references.json')['cases']; evidence = load(prep/'evidence.json')
    observations = load(folder/'observations.json'); result = load(folder/'results.json')
    history = load(folder/'assessment-history.json'); provenance = load(folder/'provenance.json')
    require(len(review['decisions']) == len(observations['cases']) == 8, 'Eight reviewed cases')
    require(provenance['review_sha256_lf'] == digest(prep/'review.json'), 'Review binding')
    require(provenance['method_lock_sha256_lf'] == digest(prep/'method-lock.json'), 'Method binding')
    sources = {p['source_id']:p for p in evidence['passages']}
    reviews = {r['review_id']:r for r in evidence['reviews']}
    for decision, question, ref, record, assessed in zip(review['decisions'], questions, refs,
                                                       observations['cases'], result['cases']):
        case = question['id']; response = record['response']
        require(decision['id'] == ref['id'] == record['id'] == assessed['id'] == case, 'Case identity')
        require(decision['decision'] == 'validated_with_reservations' and
                decision['original_human_message'] and decision['reservations'], 'Human approval')
        require(decision['question_sha256_canonical'] == canonical(question), 'Question binding')
        require(decision['reference_sha256_canonical'] == canonical(ref), 'Reference binding')
        require(record['request'] == question['expected_request_payload'], 'UI request projection')
        require(canonical(record['request']) == record['request_sha256_canonical'], 'Actual request digest')
        require(canonical(response) == record['response_sha256_canonical'], 'Actual response digest')
        require(response['status'] == ref['expected_aggregate_status'], 'Response status')
        require({i['requested_item']:i['state'] for i in response['items']} == ref['expected_item_states'], 'Item states')
        require({i['requested_item']:i['reason'] for i in response['items']} == ref['expected_item_reasons'], 'Item reasons')
        require(sorted(c['source_id'] for c in response['citation_refs']) == sorted(ref['expected_delivered_citation_source_ids']), 'Citations')
        require(all(p == sources[p['source_id']] for p in response['context']['passages']), 'Exact passages')
        require(all(r == reviews[r['review_id']] for r in response['context']['reviews']), 'Exact reviews')
        require(assessed['passed'] and all(assessed['checks'].values()), 'Preserved assessment checks')
        require(response['authority_digest'] == provenance['authority_digest'], 'Authority identity')
        require(not ({'E118-I','E121-EQ'} & {c['source_id'] for c in response['citation_refs']}), 'Excluded evidence')
    require(len(observations['opened_sources']) == 13, 'Thirteen opened sources')
    for opened in observations['opened_sources']:
        source = opened['passage']; sid = source['source_id']
        require(opened['http_status'] == 200 and source == sources[sid], 'Opened source')
        require(opened['quote'] == source['quote'], 'Opened quotation')
        require(all(r == reviews[r['review_id']] for r in opened['reviews']), 'Opened reviews')
    require(history['corrected']['case_outcomes_passed'] == result['case_outcomes_passed'] == 8, 'Historical outcomes')
    require(history['initial']['case_outcomes_passed'] == 5 and history['no_case_rerun'], 'Initial checker history')
    return {'status':'passed', 'reviewed_cases':8, 'preserved_case_outcomes_passed':8,
            'opened_sources_verified':13, 'historical_case_checks':sum(len(r['checks']) for r in result['cases']),
            'historical_source_checks':sum(len(r['checks']) for r in result['source_pages'].values()),
            'trial_reexecuted':False, 'network_or_registry_access':False}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
