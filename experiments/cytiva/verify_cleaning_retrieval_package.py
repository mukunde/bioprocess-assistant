"""Verify the reviewed cleaning reference offline, using the standard library only."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent / 'reviewed-cleaning-retrieval'
PREPARATION = Path('experiments/cytiva/retrieval-pilot-v01')
PDF_SHA = 'a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a'
FILES = {'README.md', 'events.json', 'review.json'}
SUPPORT = {str(PREPARATION / n).replace('\\', '/') for n in ('questions.json', 'evidence.json', 'manifest.json')}
SUPPORT |= {'docs/experiments/cytiva-cleaning-retrieval-pilot.md',
            'docs/experiments/cytiva-cleaning-retrieval-human-review.md',
            'experiments/cytiva/verify_cleaning_retrieval_package.py',
            'tests/test_cleaning_retrieval_package.py'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    return digest(path.read_bytes().replace(b'\r\n', b'\n'))


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def historical(value):
    return digest((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(package=PACKAGE, root=ROOT, source_text_dir=None):
    package, root = Path(package), Path(root)
    m = read(package / 'manifest.json')
    require(set(m['files']) == FILES and set(m['supporting_files']) == SUPPORT, 'File inventory changed')
    for base, entries in ((package, m['files']), (root, m['supporting_files'])):
        for name, expected in entries.items():
            require(file_digest(base / name) == expected, 'File digest changed: ' + name)
    require(m['source_pdf_sha256'] == PDF_SHA, 'PDF identity changed')
    require(m['publication_allowed'] is False and m['benchmark_executed'] is False, 'Scope promoted')
    prep = read(root / PREPARATION / 'manifest.json')
    for name, expected in prep['files'].items():
        require(file_digest(root / name) == expected, 'Preparation digest changed')
    qdoc = read(root / PREPARATION / 'questions.json')
    edoc = read(root / PREPARATION / 'evidence.json')
    questions, passages = qdoc['questions'], edoc['passages']
    require(edoc['source']['sha256'] == PDF_SHA and edoc['source']['pdf_page_count'] == 183, 'Source changed')
    require(qdoc['dataset_role'] == 'development_not_held_out' and qdoc['publication_allowed'] is False,
            'Reference scope changed')
    require(qdoc['status'] == 'pending_human_reference_review_not_executed', 'Frozen preparation promoted')
    require([q['id'] for q in questions] == [f'Q{i:02d}' for i in range(1, 11)], 'Question inventory changed')
    require(len(passages) == len({p['id'] for p in passages}) == 17, 'Passage inventory changed')
    require(Counter(q['expected_status'] for q in questions) == m['expected_response_counts'] ==
            {'answer': 7, 'clarify': 1, 'refuse': 2}, 'Expected response counts changed')
    lookup = {p['id']: p for p in passages}
    pages = {p['pdf_page_1based']: p for p in edoc['extraction']['pages']}
    require(set(pages) == {166, 167}, 'Page scope changed')
    for p in passages:
        number = p['pdf_page_1based']
        require(number in pages and p['pdf_page_index_0based'] == number - 1 and
                p['printed_page'] == str(number), 'Page mapping changed')
        require(digest(p['quote'].encode()) == p['quote_sha256'], 'Quote digest changed')
        require(0 <= p['page_text_start'] < p['page_text_end'] <= pages[number]['text_length'] and
                p['page_text_end'] - p['page_text_start'] == len(p['quote']), 'Quote offsets changed')
        require(p['human_review_status'] == 'pending', 'Frozen evidence promoted')
    if source_text_dir is not None:
        for number, page in pages.items():
            # Text-mode newline conversion tolerates a Windows checkout; offsets are Unicode-based.
            text = (Path(source_text_dir) / f'page-{number}.txt').read_text(encoding='utf-8')
            require(digest(text.encode()) == page['text_sha256'], 'Source text identity changed')
            for p in passages:
                if p['pdf_page_1based'] == number:
                    require(text[p['page_text_start']:p['page_text_end']] == p['quote'], 'Source span mismatch')
    journal = read(package / 'events.json')
    final = read(package / 'review.json')
    state = deepcopy(journal['base_review'])
    expected_history = {'review-initial.json'} | {f'{i:03d}-Q{i:02d}.json' for i in range(1, 11)} | {
        f'review-after-{i:03d}.json' for i in range(1, 11)}
    require(set(m['historical_files']) == expected_history, 'Historical inventory changed')
    require(historical(state) == m['historical_files']['review-initial.json'], 'Initial state changed')
    require(len(journal['events']) == len(journal['state_metadata']) == 10, 'Event inventory changed')
    previous_event = None
    for i, (event, metadata, question) in enumerate(zip(journal['events'], journal['state_metadata'], questions), 1):
        require(question['reference_status'] == 'pending_human_review' and question['question_en'] and
                question['question_fr'], 'Frozen question changed')
        require(event['event_id'] == f'{i:03d}-Q{i:02d}' and event['question_id'] == question['id'], 'Event order changed')
        require(event['decision'] == 'validated_with_reservation' and event['reviewer'] ==
                'project_user_via_conversation' and bool(event['reservations']), 'Decision or reservations changed')
        require(event['question_sha256'] == canonical(question), 'Question binding changed')
        require(event['preparation_manifest_sha256'] == file_digest(root / PREPARATION / 'manifest.json') and
                event['source_pdf_sha256'] == PDF_SHA, 'Event source changed')
        require(len(question['required_evidence_sets']) == 1 and set(event['evidence_sha256']) ==
                set(question['required_evidence_sets'][0]), 'Indispensable evidence changed')
        for eid, expected in event['evidence_sha256'].items():
            require(eid in lookup and canonical(lookup[eid]) == expected, 'Evidence binding changed')
        require(historical(event) == m['historical_files'][event['event_id'] + '.json'],
                'Original event/quotation/reservations changed')
        require(event['previous_review_file_sha256'] == historical(state), 'Previous state changed')
        if previous_event is not None:
            require(event['previous_event_sha256'] == historical(previous_event), 'Event chain changed')
        decision = state['decisions'][i - 1]
        require(decision['question_id'] == question['id'] and decision['decision'] == 'pending' and
                decision['question_sha256'] == canonical(question), 'Pending state changed')
        decision.update(decision=event['decision'], reviewer=event['reviewer'],
                        decided_at_utc=event['recorded_at_utc'], original_human_message=event['original_human_message'],
                        reservations=event['reservations'], event_id=event['event_id'],
                        evidence_sha256=event['evidence_sha256'])
        require(metadata['publication_allowed'] is False and metadata['benchmark_executed'] is False and
                metadata['counts'] == {'validated_with_reservation': i, 'pending': 10 - i} and
                metadata['last_event_sha256'] == historical(event), 'State scope/counts changed')
        state.update(metadata)
        require(historical(state) == m['historical_files'][f'review-after-{i:03d}.json'], 'Replayed state changed')
        previous_event = event
    require(state == final, 'Final review differs from replay')
    require(final['review_status'] == 'documentary_reference_review_completed_with_reservations' and
            final['production_retrieval_validated'] is False and final['scientific_validation'] is False,
            'Final approval scope changed')
    require(m['counts'] == {'intents': 10, 'formulations': 20, 'passages': 17,
                            'validated_with_reservation': 10, 'pending': 0}, 'Package counts changed')
    return {'status': 'passed', **m['counts'], 'event_chain_replayed': True,
            'source_text_replayed': source_text_dir is not None, 'benchmark_executed': False,
            'publication_allowed': False, 'production_retrieval_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--source-text-dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.package, source_text_dir=args.source_text_dir)))


if __name__ == '__main__':
    main()
