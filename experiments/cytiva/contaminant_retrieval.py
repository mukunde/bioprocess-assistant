"""Offline C01-C10 adapter: paired top-five/top-six atomic passage retrieval."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import time

from ingestion.local_passage_retrieval import BM25, assemble, closure, serialize
from experiments.cytiva.cleaning_retrieval import (
    build_corpus, coverage, digest, dump, read, token_counter, validate_result_grid)
from experiments.cytiva.verify_contaminant_questions_package import (
    ROOT, PACKAGE, PREPARATION, FILES, SUPPORT, DEPENDENCIES, verify as verify_reference)
from experiments.cytiva.visual_validation import network_guard

RUNS = ROOT / 'data/experiments/cytiva/contaminants-pilot-v01/runs'
VARIANTS = {'top5': 5, 'top6': 6}


def protected_files():
    """Keep earlier tracked files, review journals and retrieval runs byte-identical."""
    paths = [ROOT / name for name in subprocess.check_output(
        ['git', 'ls-files'], cwd=ROOT).decode().splitlines()]
    for folder in (ROOT / 'data/experiments/cytiva/retrieval-pilot-v01/runs', RUNS,
                   ROOT / 'data/experiments/cytiva/contaminants-pilot-v01/human-review'):
        paths.extend(p for p in folder.rglob('*') if p.is_file())
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def runtime_policy(spec, pending_ids):
    """Only source-review eligibility changes; frozen source files stay untouched."""
    if len(pending_ids) != len(set(pending_ids)) or not set(pending_ids) <= set(spec['requires']):
        raise ValueError('Invalid pending source inventory')
    result = deepcopy(spec)
    result['quarantined_ids'] = sorted(set(spec['quarantined_ids']) | set(pending_ids))
    result['searchable_ids'] = [pid for pid in spec['searchable_ids'] if pid not in pending_ids]
    return result


def check_context(passages, assembled, count_tokens, max_tokens, pending_ids):
    ids = assembled['ids']
    if len(ids) != len(set(ids)) or set(ids) & set(pending_ids):
        raise ValueError('Duplicate or pending source leaked')
    if any(passages[pid]['quarantined'] for pid in ids):
        raise ValueError('Quarantined source leaked')
    if assembled['context'] != serialize(passages, ids):
        raise ValueError('Context quote/provenance serialization changed')
    if count_tokens(assembled['context']) != assembled['tokens'] or assembled['tokens'] > max_tokens:
        raise ValueError('Context token budget changed')
    for seed in assembled['accepted_seeds']:
        if not set(closure(passages, seed)) <= set(ids):
            raise ValueError('Atomic source dependency lost')


def retrieve(index, text, count_tokens, top_k, max_tokens):
    """Runtime boundary: no question ID, answer, required sources or review message."""
    samples = []
    for _ in range(3):
        start = time.perf_counter()
        hits = index.search(text, top_k)
        at = time.perf_counter()
        assembled = assemble(index.passages, hits, count_tokens, max_tokens)
        end = time.perf_counter()
        samples.append({'retrieval_ms': (at-start)*1000, 'assembly_ms': (end-at)*1000})
    return {'hits': hits, 'assembled': assembled, 'timings': samples}


def missing_diagnostics(index, ranking, assembled, required):
    """Post-retrieval evaluation only; never used to change selection."""
    selected_seeds = {h['passage_id'] for h in assembled['hits']}
    exclusions = {e['seed']: e['reason'] for e in assembled['assembled']['excluded'] if 'seed' in e}
    details = []
    for pid in sorted(required - set(assembled['assembled']['ids'])):
        support = [{'seed': h['passage_id'], 'rank': i+1} for i, h in enumerate(ranking)
                   if pid in closure(index.passages, h['passage_id'])]
        ranked = [x for x in support if x['seed'] in selected_seeds]
        reason = 'selected_bundle_excluded' if ranked else 'below_top_k' if support else 'no_positive_supporting_hit'
        details.append({'passage_id': pid, 'reason': reason, 'supporting_seed_ranks': support,
                        'excluded_support': {x['seed']: exclusions.get(x['seed']) for x in ranked}})
    return details


def summarize(rows, expected_ids):
    if any(r.get('variant') not in VARIANTS for r in rows):
        raise ValueError('Unexpected variant')
    output = {}
    for variant in VARIANTS:
        group = [r for r in rows if r['variant'] == variant]
        ids = validate_result_grid(group, expected_ids, 'complete_evidence')
        output[variant] = {
            'intents': len(ids), 'formulations': len(group),
            'complete_both_languages': sum(all(r['complete_evidence'] for r in group
                if r['question_id'] == qid) for qid in ids),
            'mean_reference_coverage': statistics.mean(r['reference_coverage'] for r in group),
            'mean_context_tokens': statistics.mean(r['assembled']['tokens'] for r in group),
            'max_context_tokens': max(r['assembled']['tokens'] for r in group),
            'excluded_bundles': sum(len(r['assembled']['excluded']) for r in group),
            'median_retrieval_ms': statistics.median(t['retrieval_ms'] for r in group for t in r['timings']),
            'median_assembly_ms': statistics.median(t['assembly_ms'] for r in group for t in r['timings'])}
        for language in ('en', 'fr'):
            subset = [r for r in group if r['language'] == language]
            output[variant][language] = {
                'complete': sum(r['complete_evidence'] for r in subset),
                'mean_reference_coverage': statistics.mean(r['reference_coverage'] for r in subset)}
    pairs = []
    for qid in ids:
        for lang in ('en', 'fr'):
            pair = {r['variant']: r for r in rows if (r['question_id'], r['language']) == (qid, lang)}
            a, b = pair['top5'], pair['top6']
            if b['hits'][:len(a['hits'])] != a['hits']:
                raise ValueError('Paired ranking prefix changed')
            if not set(a['assembled']['ids']) <= set(b['assembled']['ids']):
                raise ValueError('Top-six context lost top-five evidence')
            pairs.append((a, b))
    output['paired'] = {
        'contexts_changed': sum(a['assembled']['context'] != b['assembled']['context'] for a,b in pairs),
        'mean_added_context_tokens': statistics.mean(b['assembled']['tokens']-a['assembled']['tokens'] for a,b in pairs),
        'coverage_regressions': sum(b['reference_coverage'] < a['reference_coverage'] for a,b in pairs)}
    output['answer_correctness'] = 'not_evaluated_no_answer_layer'
    return output


def run(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; previous runs must be preserved')
    attempts = network_guard()
    before = protected_files()
    verified = verify_reference(package=PACKAGE, root=ROOT)
    review, package_manifest = read(PACKAGE / 'review.json'), read(PACKAGE / 'manifest.json')
    spec = read(ROOT / PREPARATION / 'source_context.json')
    pending = package_manifest['not_individually_reviewed_source_ids']
    policy = runtime_policy(spec, pending)
    count_tokens, tokenizer = token_counter()
    evidence = read(ROOT / PREPARATION / 'evidence.json')
    corpus = build_corpus(evidence, policy)
    cfg = policy['retrieval']
    index = BM25(corpus, cfg['bilingual_aliases'], cfg['k1'], cfg['b'], cfg['index_context'])
    if set(pending) & set(index.docs):
        raise ValueError('Pending source indexed')
    files = sorted(SUPPORT | DEPENDENCIES | {
        (PACKAGE / name).relative_to(ROOT).as_posix() for name in FILES | {'manifest.json'}} | {
        'experiments/cytiva/contaminant_retrieval.py', 'tests/test_contaminant_retrieval.py',
        'experiments/cytiva/cleaning_retrieval.py', 'experiments/cytiva/visual_validation.py'})
    output.mkdir(parents=True, exist_ok=False)
    dump(output/'corpus.json', {'source_pdf_sha256': evidence['source']['sha256'], 'passages': corpus,
                               'pending_source_ids': pending, 'indexed_ids': list(index.docs)})
    manifest = {'status': 'frozen_before_measurement', 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
        'base_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT).decode().strip(),
        'source_pdf_sha256': evidence['source']['sha256'], 'runtime_policy': policy,
        'variants': VARIANTS, 'assembler': 'generic atomic dependencies; no cleaning-section expansion',
        'reference_verification': verified, 'reference_review_sha256_lf': digest(PACKAGE/'review.json'),
        'reference_package_manifest_sha256_lf': digest(PACKAGE/'manifest.json'),
        'pending_source_ids': pending, 'pending_source_policy': 'Excluded from index and context; no status promotion',
        'tokenizer': tokenizer, 'code_and_input_sha256_lf': {f:digest(ROOT/f) for f in files},
        'corpus_sha256_lf': digest(output/'corpus.json'), 'protected_file_sha256_raw': before,
        'llm_calls': 0, 'api_calls': 0, 'publication_allowed': False,
        'benchmark_results_human_validated': False,
        'scope': 'First paired measurement of the known-method, human-reviewed new-section development references; not independently blind',
        'timing_scope': '3 repetitions, alternating variant order by intent; excludes initialization'}
    dump(output/'manifest-before-run.json', manifest)
    for f in files:
        target = output/'input-snapshot'/f
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/f).read_bytes())
    # Load evaluation rows for scoring after freezing; preflight only verified their integrity.
    questions = read(ROOT / PREPARATION / 'questions.json')['questions']
    decisions = {d['question_id']: d['decision'] for d in review['decisions']}
    if set(decisions) != {q['id'] for q in questions}:
        raise ValueError('Question inventory differs from reviewed decisions')
    rows = []
    for i, q in enumerate(questions):
        for lang in ('en', 'fr'):
            text = q['question_' + lang]
            ranking = index.search(text, len(index.docs))
            for variant in (('top5','top6') if i % 2 == 0 else ('top6','top5')):
                result = retrieve(index, text, count_tokens, VARIANTS[variant], policy['context']['max_tokens'])
                check_context(index.passages, result['assembled'], count_tokens, policy['context']['max_tokens'], pending)
                recall, complete = coverage(result['assembled']['ids'], q)
                required = set().union(*map(set, q['required_evidence_sets']))
                rows.append({**result, 'question_id':q['id'], 'question':text, 'language':lang, 'variant':variant,
                    'full_ranking_diagnostic':ranking, 'reference_coverage':recall, 'complete_evidence':complete,
                    'missing': sorted(required-set(result['assembled']['ids'])),
                    'missing_diagnostics': missing_diagnostics(index, ranking, result, required),
                    'reference_status_at_preparation':q['reference_status'], 'reference_review_decision':decisions[q['id']],
                    'expected_response_status':q['expected_status'], 'response_status_evaluated':False})
    metrics = summarize(rows, [q['id'] for q in questions])
    after = protected_files()
    if any(after.get(f) != h for f,h in before.items()):
        raise ValueError('Earlier tracked file, review journal or run changed')
    if any(digest(ROOT/f) != h for f,h in manifest['code_and_input_sha256_lf'].items()):
        raise ValueError('Frozen input changed during measurement')
    if attempts:
        raise RuntimeError('Unexpected network attempt')
    dump(output/'results.json', rows)
    dump(output/'metrics.json', metrics)
    manifest.update(status='completed', benchmark_executed=True, network_attempts=attempts,
                    protected_files_unchanged=True, pending_source_leakage=0,
                    artifact_sha256_lf={f:digest(output/f) for f in ('corpus.json','results.json','metrics.json')})
    dump(output/'manifest.json', manifest)
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output), ensure_ascii=False))
