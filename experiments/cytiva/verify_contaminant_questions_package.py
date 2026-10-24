"""Verify the C01-C10 documentary review using the standard library only."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent / 'reviewed-contaminant-questions'
PREPARATION = 'experiments/cytiva/contaminants-pilot-v01'
PDF_SHA = 'a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a'
FILES = {'README.md', 'events.json', 'review.json', 'provenance.json'}
SUPPORT = {PREPARATION + '/' + name for name in ('questions.json', 'evidence.json', 'source_context.json', 'manifest.json')}
SUPPORT |= {'docs/experiments/cytiva-contaminants-retrieval-pilot.md',
            'docs/experiments/cytiva-contaminants-human-review.md',
            'experiments/cytiva/verify_contaminant_questions_package.py',
            'tests/test_contaminant_questions_package.py'}
DEPENDENCIES = {'experiments/cytiva/cleaning_source_context_v05.json',
                'ingestion/local_passage_retrieval.py', 'ingestion/section_context.py'}


def read(path):
    return Path(path).read_text(encoding='utf-8')


def load(path):
    return json.loads(read(path))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    return digest(Path(path).read_bytes().replace(b'\r\n', b'\n'))


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def historical(value):
    return digest((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_closure(lookup, seed, active=()):
    require(seed in lookup and seed not in active, 'Missing/cyclic source dependency')
    result = []
    for parent in lookup[seed]['requires']:
        for pid in source_closure(lookup, parent, (*active, seed)):
            if pid not in result:
                result.append(pid)
    return result + [seed]


def verify(package=PACKAGE, root=ROOT, source_text_dir=None):
    package, root = Path(package), Path(root)
    m = load(package / 'manifest.json')
    require(set(m['files']) == FILES and set(m['supporting_files']) == SUPPORT and
            set(m['dependencies']) == DEPENDENCIES, 'Package inventory changed')
    for base, entries in ((package, m['files']), (root, m['supporting_files']), (root, m['dependencies'])):
        for name, expected in entries.items():
            require(file_digest(base / name) == expected, 'File digest changed: ' + name)
    require(m['source_pdf_sha256'] == PDF_SHA and m['publication_allowed'] is False and
            m['benchmark_executed'] is False and m['benchmark_results_human_validated'] is False,
            'Package scope promoted')
    p = root / PREPARATION
    prep, qdoc, edoc, policy = [load(p / name) for name in
                               ('manifest.json', 'questions.json', 'evidence.json', 'source_context.json')]
    require(prep['status'] == 'prepared_pending_human_reference_review_not_executed' and
            prep['reference_review_status'] == prep['source_scope_review_status'] == 'pending' and
            prep['benchmark_executed'] is False and prep['publication_allowed'] is False and
            prep['llm_calls'] == prep['api_calls'] == 0, 'Frozen preparation scope changed')
    require(set(prep['files_sha256_lf']) == {PREPARATION + '/' + name for name in
            ('questions.json', 'evidence.json', 'source_context.json')} |
            {'docs/experiments/cytiva-contaminants-retrieval-pilot.md'}, 'Preparation inventory changed')
    for f, expected in {**prep['files_sha256_lf'], **prep['method_frozen_from']}.items():
        require(file_digest(root / f) == expected, 'Preparation digest changed: ' + f)
    require(set(prep['method_frozen_from']) == DEPENDENCIES, 'Frozen method inventory changed')
    require(qdoc['status'] == 'pending_human_reference_review_not_executed' and
            qdoc['publication_allowed'] is False and qdoc['benchmark_executed'] is False,
            'Frozen question status promoted')
    questions = qdoc['questions']
    require([q['id'] for q in questions] == [f'C{i:02d}' for i in range(1, 11)] and
            qdoc['question_count'] == 10 and qdoc['formulation_count'] == 20 and
            len({q['question_' + lang] for q in questions for lang in ('en', 'fr')}) == 20,
            'Question inventory changed')
    require(Counter(q['expected_status'] for q in questions) == m['expected_response_counts'] ==
            prep['expected_response_counts'] == {'answer': 7, 'clarify': 1, 'refuse': 2},
            'Expected response counts changed')
    require(edoc['source']['sha256'] == prep['source_pdf_sha256'] == PDF_SHA and
            edoc['source']['pdf_page_count'] == 183 and edoc['publication_allowed'] is False,
            'Source identity/scope changed')
    lookup = {p['id']: p for p in edoc['passages']}
    require(len(lookup) == len(edoc['passages']) == 27 and set(policy['requires']) == set(lookup),
            'Source inventory changed')
    pages = {p['pdf_page_1based']: p for p in edoc['extraction']['pages']}
    require(set(pages) == set(prep['pages_1based']) == {118, 119, 120, 121}, 'Page scope changed')
    for pid, passage in lookup.items():
        number = passage['pdf_page_1based']
        require(number in pages and passage['pdf_page_index_0based'] == number - 1 and
                passage['printed_page'] == str(number), 'Source page mapping changed')
        require(digest(passage['quote'].encode()) == passage['quote_sha256'], 'Source quote digest changed')
        require(0 <= passage['page_text_start'] < passage['page_text_end'] <= pages[number]['text_length'] and
                passage['page_text_end'] - passage['page_text_start'] == len(passage['quote']),
                'Source span bounds changed')
        require(passage['requires'] == policy['requires'][pid] and passage['human_review_status'] == 'pending',
                'Frozen source topology/status changed')
        source_closure(lookup, pid)
    require(policy['publication_allowed'] is False and policy['quarantined_ids'] == [] and
            policy['retrieval'] == load(root / 'experiments/cytiva/cleaning_source_context_v05.json')['retrieval'] and
            policy['context']['max_tokens'] == 2048, 'Source policy/method changed')
    require(set(policy['searchable_ids']) <= lookup.keys(), 'Searchable source inventory changed')
    reachable = {pid for seed in policy['searchable_ids'] for pid in source_closure(lookup, seed)}
    required = {pid for q in questions for bundle in q['required_evidence_sets'] for pid in bundle}
    require(len(required) == 25 and required <= reachable and
            sorted(set(lookup) - required) == m['not_individually_reviewed_source_ids'] == ['E118-I', 'E121-EQ'],
            'Unreviewed source scope changed')
    journal, final, provenance = [load(package / name) for name in ('events.json', 'review.json', 'provenance.json')]
    state = deepcopy(journal['base_review'])
    history = {'review-initial.json'} | {f'{i:03d}-C{i:02d}.json' for i in range(1, 11)} | {
        f'review-after-{i:03d}.json' for i in range(1, 11)}
    require(set(m['historical_files']) == history and
            historical(state) == m['historical_files']['review-initial.json'], 'Initial/history changed')
    require(state['dataset_id'] == qdoc['id'] and state['preparation_manifest_sha256_lf'] == file_digest(p / 'manifest.json') and
            state['source_pdf_sha256'] == PDF_SHA and len(state['decisions']) == 10 and len(journal['events']) == 10,
            'Initial source binding changed')
    previous = None
    for i, (q, event) in enumerate(zip(questions, journal['events']), 1):
        require(q['reference_status'] == 'pending_human_review' and q['expected_answer_en'] and
                q['conditions_to_preserve'] and q['must_not_infer'], 'Frozen reference changed')
        require(event['event_id'] == f'{i:03d}-{q["id"]}' and event['question_id'] == q['id'], 'Event order changed')
        require(event['decision'] == 'validated_with_reservation' and event['reviewer'] == 'project_user_via_conversation' and
                bool(event['reservations']), 'Decision/reservations changed')
        require(event['question_sha256'] == canonical(q), 'Question binding changed')
        require(len(q['required_evidence_sets']) == 1 and set(event['evidence_sha256']) ==
                set(event['quote_sha256']) == set(q['required_evidence_sets'][0]), 'Required source binding changed')
        for pid, expected in event['evidence_sha256'].items():
            require(canonical(lookup[pid]) == expected and event['quote_sha256'][pid] == lookup[pid]['quote_sha256'],
                    'Evidence binding changed')
        require(historical(event) == m['historical_files'][event['event_id'] + '.json'], 'Original event/message changed')
        require(event['review_before_sha256'] == canonical(state) and event['previous_event_sha256'] == previous,
                'Event/state chain changed')
        d = state['decisions'][i - 1]
        require(d['question_id'] == q['id'] and d['decision'] == 'pending' and d['question_sha256'] == canonical(q),
                'Pending state changed')
        d.update(decision=event['decision'], event_id=event['event_id'], reservations=event['reservations'],
                 original_human_message=event['original_human_message'], evidence_sha256=event['evidence_sha256'])
        state.update(last_event_sha256=canonical(event), validated_intents=i, pending_intents=10-i)
        if i == 1:
            state['review_status'] = 'in_progress'
        if i == 10:
            state.update(review_status='completed_with_reservations', completed_at_utc=event['recorded_at_utc'])
        require(historical(state) == m['historical_files'][f'review-after-{i:03d}.json'], 'Replayed state changed')
        previous = canonical(event)
    require(state == final, 'Final state differs from replay')
    require(final['review_status'] == 'completed_with_reservations' and final['validated_intents'] == 10 and
            final['pending_intents'] == 0 and final['publication_allowed'] is False and
            final['benchmark_executed'] is False and final['benchmark_results_human_validated'] is False,
            'Final scope promoted')
    require(m['counts'] == {'intents': 10, 'formulations': 20, 'source_passages': 27,
                           'required_source_passages': 25, 'validated_with_reservation': 10, 'pending': 0},
            'Package counts changed')
    require(provenance['preparation_manifest'] == prep and
            provenance['preparation_manifest_sha256_lf'] == file_digest(p / 'manifest.json') and
            provenance['source'] == edoc['source'] and provenance['source_page_metadata'] == edoc['extraction']['pages'],
            'Preparation provenance changed')
    require(provenance['benchmark_executed'] is False and provenance['scientific_validation'] is False and
            provenance['production_retrieval_validated'] is False and provenance['publication_allowed'] is False and
            provenance['not_individually_reviewed_source_ids'] == m['not_individually_reviewed_source_ids'],
            'Provenance scope promoted')
    preflight, audit = provenance['preparation_verification'], provenance['final_review_verification']
    require(historical(preflight) == provenance['preparation_verification_sha256_lf'] and
            historical(audit) == provenance['final_review_verification_sha256_lf'], 'Original audit record changed')
    require(preflight['benchmark_executed'] is False and preflight['network_attempts'] == [] and
            preflight['llm_calls'] == preflight['api_calls'] == 0 and
            audit['benchmark_executed'] is False and audit['event_chain_verified'] == 10 and
            audit['validated_with_reservations'] == 10 and audit['pending'] == 0 and
            audit['not_individually_covered_by_question_reviews'] == ['E118-I', 'E121-EQ'],
            'Recorded verification scope changed')
    if source_text_dir is not None:
        for number, page in pages.items():
            text = read(Path(source_text_dir) / f'page-{number}.txt')
            require(digest(text.encode()) == page['text_sha256'], 'Local page text identity changed')
            for passage in lookup.values():
                if passage['pdf_page_1based'] == number:
                    require(text[passage['page_text_start']:passage['page_text_end']] == passage['quote'],
                            'Local source span changed')
    return {'status': 'passed', **m['counts'], 'event_chain_replayed': True,
            'source_text_replayed': source_text_dir is not None,
            'not_individually_reviewed_source_ids': m['not_individually_reviewed_source_ids'],
            'benchmark_executed': False, 'publication_allowed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--source-text-dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.package, source_text_dir=args.source_text_dir)))
