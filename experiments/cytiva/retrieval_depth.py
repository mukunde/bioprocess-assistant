"""Offline top-five/top-six development comparison; no source or runtime default changes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

from ingestion.local_passage_retrieval import BM25
from experiments.cytiva.cleaning_retrieval import build_corpus, digest, dump, read, token_counter, validate_result_grid
from experiments.cytiva.section_retrieval import (
    SPEC as BASELINE, NEW, BASE_REFERENCE_PACKAGE, SECTION_REFERENCE_PACKAGE,
    measure, verified_reference_reviews)
from experiments.cytiva.verify_cleaning_retrieval_package import ROOT, PREPARATION
from experiments.cytiva.visual_validation import network_guard

SPEC = ROOT / 'experiments/cytiva/cleaning_source_context_v05.json'
RUNS = ROOT / 'data/experiments/cytiva/retrieval-pilot-v01/runs'


def previous_runs():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(RUNS.rglob('*')) if p.is_file()}


def validate_specs(baseline, candidate):
    """One variable only: no alias, source topology, budget or section-policy tuning."""
    ignored = {'id', 'variant_note', 'development_status', 'baseline_spec'}
    left = {k: v for k, v in baseline.items() if k not in ignored}
    right = {k: v for k, v in candidate.items() if k not in ignored}
    # Copy nested dictionaries before comparing; never change the actual specs.
    right = json.loads(json.dumps(right))
    if left['retrieval']['top_k'] != 5 or right['retrieval']['top_k'] != 6:
        raise ValueError('Expected top-five/top-six comparison')
    right['retrieval']['top_k'] = 5
    if left != right:
        raise ValueError('Only retrieval depth may differ')


def summarize(rows, expected):
    if not expected or any(r.get('dataset') not in expected or r.get('variant') not in ('v03', 'v05') for r in rows):
        raise ValueError('Unexpected or empty dataset/variant inventory')
    result = {}
    for dataset, ids in expected.items():
        result[dataset] = {}
        for variant in ('v03', 'v05'):
            group = [r for r in rows if r['dataset'] == dataset and r['variant'] == variant]
            validate_result_grid(group, ids, 'complete_evidence')
            result[dataset][variant] = {
                'intents': len(ids), 'formulations': len(group),
                'complete_both_languages': sum(all(r['complete_evidence'] for r in group
                    if r['question_id'] == qid) for qid in ids),
                'mean_reference_coverage': statistics.mean(r['reference_coverage'] for r in group),
                'max_context_tokens': max(r['assembled']['tokens'] for r in group),
                'mean_context_tokens': statistics.mean(r['assembled']['tokens'] for r in group),
                'excluded_bundles': sum(len(r['assembled']['excluded']) for r in group),
                'median_retrieval_ms': statistics.median(t['retrieval_ms'] for r in group for t in r['timings']),
                'median_assembly_ms': statistics.median(t['assembly_ms'] for r in group for t in r['timings'])}
        pairs = []
        for qid in ids:
            for language in ('en', 'fr'):
                pair = {r['variant']: r for r in rows if (r['dataset'], r['question_id'], r['language']) == (dataset, qid, language)}
                a, b = pair['v03'], pair['v05']
                if b['hits'][:len(a['hits'])] != a['hits']:
                    raise ValueError('Paired ranking prefix changed')
                pairs.append((a, b))
        result[dataset]['paired'] = {
            'contexts_changed': sum(a['assembled']['context'] != b['assembled']['context'] for a, b in pairs),
            'mean_added_context_tokens': statistics.mean(b['assembled']['tokens'] - a['assembled']['tokens'] for a, b in pairs),
            'max_added_context_tokens': max(b['assembled']['tokens'] - a['assembled']['tokens'] for a, b in pairs),
            'coverage_regressions': sum(b['reference_coverage'] < a['reference_coverage'] for a, b in pairs)}
    result['answer_correctness'] = 'not_evaluated_no_answer_layer'
    return result


def run(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; previous runs must be preserved')
    attempts = network_guard()
    before = previous_runs()
    reviews, decisions = verified_reference_reviews()
    specs = {'v03': read(BASELINE), 'v05': read(SPEC)}
    validate_specs(specs['v03'], specs['v05'])
    counter, tokenizer = token_counter()
    evidence = read(ROOT / PREPARATION / 'evidence.json')
    corpus = build_corpus(evidence, specs['v03'])
    cfg = specs['v03']['retrieval']
    index = BM25(corpus, cfg['bilingual_aliases'], cfg['k1'], cfg['b'], cfg['index_context'])
    files = ['ingestion/local_passage_retrieval.py', 'ingestion/section_context.py',
             'experiments/cytiva/retrieval_depth.py', 'experiments/cytiva/cleaning_retrieval.py',
             'experiments/cytiva/section_retrieval.py', 'experiments/cytiva/visual_validation.py',
             'experiments/cytiva/verify_cleaning_retrieval_package.py',
             'experiments/cytiva/verify_section_questions_package.py', 'tests/test_retrieval_depth.py',
             BASELINE.relative_to(ROOT).as_posix(), SPEC.relative_to(ROOT).as_posix(),
             NEW.relative_to(ROOT).as_posix(), (PREPARATION / 'evidence.json').as_posix(),
             (PREPARATION / 'questions.json').as_posix()]
    for package in (BASE_REFERENCE_PACKAGE, SECTION_REFERENCE_PACKAGE):
        files += [(package / name).relative_to(ROOT).as_posix() for name in ('review.json', 'manifest.json', 'events.json')]
    output.mkdir(parents=True, exist_ok=False)
    dump(output / 'corpus.json', {'source_pdf_sha256': evidence['source']['sha256'], 'passages': corpus})
    manifest = {'status': 'frozen_before_measurement', 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
                'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                'configs': specs, 'tokenizer': tokenizer, 'reference_reviews': reviews,
                'code_and_input_sha256_lf': {f: digest(ROOT / f) for f in files},
                'corpus_sha256_lf': digest(output / 'corpus.json'), 'previous_run_sha256_raw': before,
                'llm_calls': 0, 'api_calls': 0, 'publication_allowed': False,
                'scope': 'Known development questions, tuned after N05; not held-out validation or answer evaluation',
                'timing_scope': '3 repetitions, alternating variant order; excludes initialization'}
    dump(output / 'manifest-before-run.json', manifest)
    for f in files:
        target = output / 'input-snapshot' / f
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / f).read_bytes())
    datasets = {'reviewed': read(ROOT / PREPARATION / 'questions.json')['questions'],
                'new_candidate': read(NEW)['questions']}
    expected = {dataset: [q['id'] for q in questions] for dataset, questions in datasets.items()}
    for dataset, ids in expected.items():
        if len(ids) != len(set(ids)) or set(ids) != set(decisions[dataset]):
            raise ValueError('Question inventory differs from reviewed references')
    rows = []
    for dataset, questions in datasets.items():
        for i, question in enumerate(questions):
            for language in ('en', 'fr'):
                for variant in (('v03', 'v05') if i % 2 == 0 else ('v05', 'v03')):
                    # Both use exactly the existing section assembler; only top_k differs.
                    row = measure(index, question, language, counter, specs[variant], 'v03')
                    row.update(variant=variant, dataset=dataset,
                               full_ranking_diagnostic=index.search(question['question_' + language], len(index.docs)),
                               reference_review_decision=decisions[dataset][question['id']])
                    rows.append(row)
    metrics = summarize(rows, expected)
    after = previous_runs()
    if any(after.get(f) != value for f, value in before.items()):
        raise ValueError('Previous run changed')
    if attempts:
        raise RuntimeError('Unexpected network attempt')
    dump(output / 'results.json', rows)
    dump(output / 'metrics.json', metrics)
    manifest.update(status='completed', network_attempts=attempts, previous_runs_unchanged=True,
                    artifact_sha256_lf={f: digest(output/f) for f in ('results.json', 'metrics.json', 'corpus.json')})
    dump(output / 'manifest.json', manifest)
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output), ensure_ascii=False))
