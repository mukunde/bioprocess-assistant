"""Compare v02 and section-context v03 on old and frozen new development intents."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import time

from ingestion.local_passage_retrieval import BM25, assemble
from ingestion.section_context import assemble_sections
from experiments.cytiva.cleaning_retrieval import (
    build_corpus, read, dump, digest, token_counter, coverage, validate_result_grid)
from experiments.cytiva.verify_cleaning_retrieval_package import ROOT, PREPARATION, PACKAGE as BASE_REFERENCE_PACKAGE
from experiments.cytiva.verify_section_questions_package import (
    PACKAGE as SECTION_REFERENCE_PACKAGE, verify as verify_section_reference)
from experiments.cytiva.visual_validation import network_guard

SPEC = ROOT / 'experiments/cytiva/cleaning_source_context_v03.json'
NEW = ROOT / 'experiments/cytiva/cleaning_section_questions_v01.json'


def measure(index, question, language, count_tokens, spec, variant):
    samples = []
    for _ in range(3):
        start = time.perf_counter()
        hits = index.search(question['question_' + language], spec['retrieval']['top_k'])
        at = time.perf_counter()
        if variant == 'v02':
            assembled = assemble(index.passages, hits, count_tokens, spec['context']['max_tokens'])
        else:
            assembled = assemble_sections(index.passages, hits, question['question_' + language],
                count_tokens, spec['section_context'], spec['context']['max_tokens'])
        end = time.perf_counter()
        samples.append({'retrieval_ms': (at - start) * 1000, 'assembly_ms': (end - at) * 1000})
    recall, complete = coverage(assembled['ids'], question)
    return {'question_id': question['id'], 'language': language, 'variant': variant,
            'question': question['question_' + language], 'hits': hits, 'assembled': assembled,
            'reference_coverage': recall, 'complete_evidence': complete,
            'missing': sorted(set().union(*map(set, question['required_evidence_sets'])) - set(assembled['ids'])),
            'expected_response_status': question['expected_status'], 'response_status_evaluated': False,
            'reference_status_at_preparation': question['reference_status'], 'timings': samples}


def summarize(rows, expected_datasets=None):
    if expected_datasets is None:
        expected_datasets = {
            'reviewed': [q['id'] for q in read(ROOT / PREPARATION / 'questions.json')['questions']],
            'new_candidate': [q['id'] for q in read(NEW)['questions']]}
    if not expected_datasets:
        raise ValueError('Expected datasets cannot be empty')
    for row in rows:
        if row.get('dataset') not in expected_datasets or row.get('variant') not in ('v02', 'v03'):
            raise ValueError('Unexpected dataset/variant result')
    for dataset, expected_ids in expected_datasets.items():
        for variant in ('v02', 'v03'):
            group = [r for r in rows if r['dataset'] == dataset and r['variant'] == variant]
            validate_result_grid(group, expected_ids, 'complete_evidence')
    results = {}
    for dataset in expected_datasets:
        results[dataset] = {}
        for variant in ('v02', 'v03'):
            group = [r for r in rows if r['dataset'] == dataset and r['variant'] == variant]
            intents = {r['question_id'] for r in group}
            summary = {'intents': len(intents), 'formulations': len(group),
                'complete_both_languages': sum(all(r['complete_evidence'] for r in group
                    if r['question_id'] == qid) for qid in intents),
                'max_context_tokens': max(r['assembled']['tokens'] for r in group),
                'excluded_bundles': sum(len(r['assembled']['excluded']) for r in group),
                'median_retrieval_ms': statistics.median(t['retrieval_ms'] for r in group for t in r['timings']),
                'median_assembly_ms': statistics.median(t['assembly_ms'] for r in group for t in r['timings'])}
            for language in ('en', 'fr'):
                subset = [r for r in group if r['language'] == language]
                summary[language] = {'complete': sum(r['complete_evidence'] for r in subset),
                    'mean_reference_coverage': statistics.mean(r['reference_coverage'] for r in subset)}
            results[dataset][variant] = summary
    results['answer_correctness'] = 'not_evaluated_no_answer_layer'
    return results


def verified_reference_reviews():
    """Check both packages before tokenizer loading or measurement, then bind their reviews."""
    # The section verifier also verifies the earlier source/reference package.
    verify_section_reference(package=SECTION_REFERENCE_PACKAGE, root=ROOT)
    reviews, decisions = {}, {}
    for dataset, package in (('reviewed', BASE_REFERENCE_PACKAGE), ('new_candidate', SECTION_REFERENCE_PACKAGE)):
        review = read(package / 'review.json')
        accepted = {'validated', 'validated_with_reservation'}
        states = {d['question_id']: d['decision'] for d in review['decisions']}
        reviewed = bool(states) and all(value in accepted for value in states.values())
        if not reviewed:
            raise ValueError('Reference decisions are not fully reviewed: ' + dataset)
        reviews[dataset] = {
            'human_reference_reviewed': reviewed,
            'review_status': review['review_status'],
            'validated_intents': len(states),
            'review_path': (package / 'review.json').relative_to(ROOT).as_posix(),
            'review_sha256_lf': digest(package / 'review.json'),
            'package_manifest_sha256_lf': digest(package / 'manifest.json'),
            'publication_allowed': review['publication_allowed'],
            'benchmark_results_human_validated': review.get('benchmark_results_human_validated', False),
            'scope': review['scope']}
        decisions[dataset] = states
    return reviews, decisions


def run(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; prior runs must be preserved')
    attempts = network_guard()
    reference_reviews, reference_decisions = verified_reference_reviews()
    spec = read(SPEC)
    counter, tokenizer = token_counter()
    evidence = read(ROOT / PREPARATION / 'evidence.json')
    corpus = build_corpus(evidence, spec)
    index = BM25(corpus, spec['retrieval']['bilingual_aliases'], spec['retrieval']['k1'],
                 spec['retrieval']['b'], spec['retrieval']['index_context'])
    # Freeze code, policy, inputs and index before measuring any query.
    files = ['ingestion/local_passage_retrieval.py', 'ingestion/section_context.py',
        'experiments/cytiva/cleaning_retrieval.py', 'experiments/cytiva/section_retrieval.py',
        SPEC.relative_to(ROOT).as_posix(), NEW.relative_to(ROOT).as_posix(),
        (PREPARATION / 'evidence.json').as_posix(), (PREPARATION / 'questions.json').as_posix(),
        'experiments/cytiva/verify_cleaning_retrieval_package.py',
        'experiments/cytiva/verify_section_questions_package.py']
    for package in (BASE_REFERENCE_PACKAGE, SECTION_REFERENCE_PACKAGE):
        files += [(package / name).relative_to(ROOT).as_posix()
                  for name in ('review.json', 'manifest.json', 'events.json')]
    output.mkdir(parents=True, exist_ok=False)
    dump(output / 'corpus.json', {'source_pdf_sha256': evidence['source']['sha256'], 'passages': corpus})
    manifest = {'status': 'frozen_before_measurement', 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
        'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'config': spec, 'tokenizer': tokenizer, 'code_and_input_sha256_lf': {f: digest(ROOT / f) for f in files},
        'corpus_sha256_lf': digest(output / 'corpus.json'), 'llm_calls': 0, 'api_calls': 0,
        'publication_allowed': False,
        'new_references_human_reviewed': reference_reviews['new_candidate']['human_reference_reviewed'],
        'reference_reviews': reference_reviews,
        'timing_scope': 'in-process 3 repetitions; alternating v02/v03 order by intent; no tracemalloc; excludes initialization'}
    dump(output / 'manifest-before-run.json', manifest)
    for f in files:
        destination = output / 'input-snapshot' / f
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / f).read_bytes())
    datasets = [('reviewed', read(ROOT / PREPARATION / 'questions.json')['questions']),
                ('new_candidate', read(NEW)['questions'])]
    expected_datasets = {dataset: [q['id'] for q in questions] for dataset, questions in datasets}
    for dataset, ids in expected_datasets.items():
        if len(ids) != len(set(ids)) or set(ids) != set(reference_decisions[dataset]):
            raise ValueError('Question IDs do not match reviewed references')
    rows = []
    for dataset, questions in datasets:
        for i, question in enumerate(questions):
            for language in ('en', 'fr'):
                for variant in (('v02', 'v03') if i % 2 == 0 else ('v03', 'v02')):
                    result = measure(index, question, language, counter, spec, variant)
                    result['dataset'] = dataset
                    result['reference_review_decision'] = reference_decisions[dataset][question['id']]
                    rows.append(result)
    # Check a policy decision is identical for paired variants; only assembly differs.
    for dataset, questions in datasets:
        for q in questions:
            for language in ('en', 'fr'):
                pair = [r for r in rows if r['dataset'] == dataset and r['question_id'] == q['id'] and r['language'] == language]
                if len(pair) != 2 or pair[0]['hits'] != pair[1]['hits']:
                    raise ValueError('Retrieval changed between assembly variants')
    if attempts:
        raise RuntimeError('Unexpected network attempt')
    metrics = summarize(rows, expected_datasets=expected_datasets)
    dump(output / 'results.json', rows)
    dump(output / 'metrics.json', metrics)
    manifest.update(status='completed', network_attempts=attempts,
        artifact_sha256_lf={f: digest(output / f) for f in ['results.json', 'metrics.json', 'corpus.json']})
    dump(output / 'manifest.json', manifest)
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output), ensure_ascii=False))
