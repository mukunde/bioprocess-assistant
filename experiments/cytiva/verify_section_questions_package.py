"""Verify eight reviewed section questions without retrieval/runtime dependencies."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from experiments.cytiva.verify_cleaning_retrieval_package import (
    ROOT, PDF_SHA, read, digest, file_digest, canonical, historical, require,
    verify as verify_base)

PACKAGE = Path(__file__).parent / 'reviewed-section-questions'
QUESTIONS = 'experiments/cytiva/cleaning_section_questions_v01.json'
EVIDENCE = 'experiments/cytiva/retrieval-pilot-v01/evidence.json'
BASE = 'experiments/cytiva/reviewed-cleaning-retrieval'
FILES = {'README.md', 'events.json', 'review.json', 'provenance.json'}
SUPPORT = {QUESTIONS, 'docs/experiments/cytiva-section-questions-human-review.md',
           'experiments/cytiva/verify_section_questions_package.py',
           'tests/test_section_questions_package.py'}
DEPENDENCIES = {EVIDENCE, BASE + '/manifest.json', 'experiments/cytiva/verify_cleaning_retrieval_package.py'}


def raw_checkout_digest(path, crlf=False):
    data = path.read_bytes().replace(b'\r\n', b'\n')
    return digest(data.replace(b'\n', b'\r\n') if crlf else data)


def verify_provenance(p, qpath, epath):
    require(p['questions_original_line_endings'] == 'LF' and
            p['source_evidence_original_line_endings'] == 'CRLF', 'Historical input format changed')
    require(p['questions_original_sha256'] == raw_checkout_digest(qpath) and
            p['source_evidence_original_sha256'] == raw_checkout_digest(epath, crlf=True),
            'Original input bytes changed')
    freeze = p['reference_freeze']
    freeze_digest = digest(json.dumps(freeze, indent=2).replace('\n', '\r\n').encode())
    require(freeze_digest == p['reference_freeze_sha256'], 'Original freeze changed')
    require(freeze['measurements_started'] is False and freeze['human_review'] == 'pending',
            'Historical freeze promoted')
    require(freeze['files'][QUESTIONS] == p['questions_original_sha256'], 'Question freeze changed')
    exp = p['experiment']; run = exp['original_manifest']; metrics = exp['metrics']
    require(historical(run) == exp['original_manifest_sha256'], 'Original run manifest changed')
    require(historical(metrics) == run['artifact_sha256_lf']['metrics.json'], 'Recorded metrics changed')
    require(run['status'] == 'completed' and run['network_attempts'] == [] and
            run['llm_calls'] == run['api_calls'] == 0 and run['publication_allowed'] is False and
            run['new_references_human_reviewed'] is False, 'Historical experiment scope promoted')
    policy = run['config']
    policy_path = 'experiments/cytiva/cleaning_source_context_v03.json'
    require(historical(policy) == freeze['files'][policy_path], 'Frozen policy provenance changed')
    require(run['code_and_input_sha256_lf'][QUESTIONS] == file_digest(qpath) and
            run['code_and_input_sha256_lf'][EVIDENCE] == file_digest(epath), 'Measured input changed')
    require(run['config']['context']['max_tokens'] == 2048, 'Recorded budget changed')
    for variant in ('v02', 'v03'):
        require(metrics['new_candidate'][variant]['complete_both_languages'] == 7 and
                metrics['new_candidate'][variant]['intents'] == 8, 'Historical coverage changed')
    failures = exp['n05_outcomes']
    require(len(failures) == 4 and {(f['language'], f['variant']) for f in failures} ==
            {(lang, variant) for lang in ('en', 'fr') for variant in ('v02', 'v03')}, 'N05 inventory changed')
    for failure in failures:
        require(failure['question_id'] == 'N05' and failure['complete_evidence'] is False and
                failure['response_status_evaluated'] is False and
                failure['missing'] == ['E166-P', 'E166-PH'] and
                failure['reference_coverage'] == 5 / 7, 'N05 failure erased or promoted')


def verify(package=PACKAGE, root=ROOT, source_text_dir=None, run_dir=None):
    package, root = Path(package), Path(root)
    m = read(package / 'manifest.json')
    require(set(m['files']) == FILES and set(m['supporting_files']) == SUPPORT and
            set(m['dependencies']) == DEPENDENCIES, 'Package inventory changed')
    for base, entries in ((package, m['files']), (root, m['supporting_files']), (root, m['dependencies'])):
        for name, expected in entries.items():
            require(file_digest(base / name) == expected, 'File digest changed: ' + name)
    verify_base(package=root / BASE, root=root, source_text_dir=source_text_dir)
    require(m['source_pdf_sha256'] == PDF_SHA and m['publication_allowed'] is False and
            m['benchmark_results_human_validated'] is False, 'Package scope promoted')
    p = read(package / 'provenance.json')
    qpath, epath = root / QUESTIONS, root / EVIDENCE
    verify_provenance(p, qpath, epath)
    qdoc, edoc = read(qpath), read(epath)
    questions = qdoc['questions']; lookup = {item['id']: item for item in edoc['passages']}
    require(qdoc['status'] == 'candidate_references_frozen_before_measurement_pending_human_review' and
            qdoc['new_intents'] == 8 and qdoc['formulations'] == 16, 'Frozen preparation changed')
    require([q['id'] for q in questions] == [f'N{i:02d}' for i in range(1, 9)], 'Question inventory changed')
    require(Counter(q['expected_status'] for q in questions) == m['expected_response_counts'] ==
            {'answer': 3, 'clarify': 1, 'refuse': 4}, 'Response reference counts changed')
    refs = {eid for q in questions for bundle in q['required_evidence_sets'] for eid in bundle}
    require(len(refs) == 16 and refs <= lookup.keys(), 'Source coverage changed')
    journal, final = read(package / 'events.json'), read(package / 'review.json')
    state = deepcopy(journal['base_review'])
    expected_history = {'review-initial.json'} | {f'{i:03d}-N{i:02d}.json' for i in range(1, 9)} | {
        f'review-after-{i:03d}.json' for i in range(1, 9)}
    require(set(m['historical_files']) == expected_history and
            historical(state) == m['historical_files']['review-initial.json'], 'Initial/history changed')
    require(len(journal['events']) == len(journal['state_metadata']) == len(state['decisions']) == 8,
            'Journal inventory changed')
    previous = None
    for i, (event, metadata, q) in enumerate(zip(journal['events'], journal['state_metadata'], questions), 1):
        require(q['reference_status'] == 'assistant_candidate_pending_human_review' and
                q['dataset_role'] == 'additional_development_not_held_out' and
                q['question_en'] and q['question_fr'], 'Frozen question scope changed')
        require(event['event_id'] == f'{i:03d}-N{i:02d}' and event['question_id'] == q['id'], 'Event order changed')
        require(event['decision'] == 'validated_with_reservation' and event['reviewer'] ==
                'project_user_via_conversation' and bool(event['reservations']), 'Decision/reservations changed')
        require(event['question_sha256'] == canonical(q), 'Question binding changed')
        require(event['source_pdf_sha256'] == PDF_SHA and
                event['questions_file_sha256'] == p['questions_original_sha256'] and
                event['source_evidence_file_sha256'] == p['source_evidence_original_sha256'] and
                event['reference_freeze_file_sha256'] == p['reference_freeze_sha256'], 'Event source changed')
        require(len(q['required_evidence_sets']) == 1 and set(event['evidence_sha256']) ==
                set(q['required_evidence_sets'][0]), 'Indispensable evidence changed')
        for eid, expected in event['evidence_sha256'].items():
            require(canonical(lookup[eid]) == expected, 'Evidence binding changed')
        require(historical(event) == m['historical_files'][event['event_id'] + '.json'],
                'Original event/quotation/reservations changed')
        require(event['previous_review_file_sha256'] == historical(state), 'Previous state changed')
        if previous is not None:
            require(event['previous_event_sha256'] == historical(previous), 'Event chain changed')
        decision = state['decisions'][i - 1]
        require(decision['decision'] == 'pending' and decision['question_id'] == q['id'] and
                decision['question_sha256'] == canonical(q), 'Pending state changed')
        decision.update(decision=event['decision'], reviewer=event['reviewer'],
            decided_at_utc=event['recorded_at_utc'], original_human_message=event['original_human_message'],
            reservations=event['reservations'], event_id=event['event_id'], evidence_sha256=event['evidence_sha256'])
        require(metadata['publication_allowed'] is False and metadata['benchmark_results_human_validated'] is False and
                metadata['retrieval_benchmark_previously_executed'] is True and
                metadata['counts'] == {'validated_with_reservation': i, 'pending': 8 - i} and
                metadata['last_event_sha256'] == historical(event), 'Review scope/counts changed')
        state.update(metadata)
        require(historical(state) == m['historical_files'][f'review-after-{i:03d}.json'], 'Replayed state changed')
        previous = event
    require(state == final, 'Final state differs from replay')
    require(final['review_status'] == 'documentary_reference_review_completed_with_reservations' and
            final['scientific_validation'] is False and final['production_retrieval_validated'] is False,
            'Final approval scope changed')
    require(m['counts'] == {'intents': 8, 'formulations': 16, 'required_source_passages': 16,
                            'validated_with_reservation': 8, 'pending': 0}, 'Final counts changed')
    if run_dir is not None:
        run_dir = Path(run_dir); exp = p['experiment']
        require(read(run_dir / 'manifest.json') == exp['original_manifest'], 'Local run manifest changed')
        for name, expected in exp['original_manifest']['artifact_sha256_lf'].items():
            require(file_digest(run_dir / name) == expected, 'Local run artifact changed')
        rows = read(run_dir / 'results.json')
        fields = ['question_id', 'language', 'variant', 'reference_coverage', 'complete_evidence', 'missing', 'response_status_evaluated']
        require([{k: r[k] for k in fields} for r in rows if r['question_id'] == 'N05'] ==
                exp['n05_outcomes'], 'Local N05 projection changed')
    return {'status': 'passed', **m['counts'], 'event_chain_replayed': True, 'prior_source_package_verified': True,
            'source_text_replayed': source_text_dir is not None, 'local_run_replayed': run_dir is not None,
            'n05_incomplete_preserved': True, 'publication_allowed': False, 'benchmark_results_human_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--source-text-dir', type=Path)
    parser.add_argument('--run-dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.package, source_text_dir=args.source_text_dir, run_dir=args.run_dir)))


if __name__ == '__main__':
    main()
