"""Run the isolated, source-only cleaning retrieval development experiment."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time
import tracemalloc

from ingestion.local_passage_retrieval import BM25, assemble, closure
from experiments.cytiva.verify_cleaning_retrieval_package import verify, ROOT, PREPARATION
from experiments.cytiva.visual_validation import network_guard

SPEC = ROOT / 'experiments/cytiva/cleaning_source_context.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def build_corpus(evidence, spec):
    """Whitelist source fields; never accept questions, labels, answers or decisions."""
    source = evidence['passages']
    ids = {p['id'] for p in source}
    if len(ids) != len(source) or set(spec['requires']) != ids or not set(spec['quarantined_ids']) <= ids:
        raise ValueError('Source topology inventory mismatch')
    corpus = [{**{k: p[k] for k in ('id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
               'quote_sha256', 'page_text_start', 'page_text_end')},
               'requires': spec['requires'][p['id']], 'quarantined': p['id'] in spec['quarantined_ids']}
              for p in source]
    if 'searchable_ids' in spec:
        if not set(spec['searchable_ids']) <= ids:
            raise ValueError('Unknown searchable source ID')
        for p in corpus:
            p['searchable'] = p['id'] in spec['searchable_ids']
    for p in corpus:
        if hashlib.sha256(p['quote'].encode()).hexdigest() != p['quote_sha256']:
            raise ValueError('Source quote mismatch')
    indexed = {p['id']: p for p in corpus}
    for pid in indexed:
        closure(indexed, pid)
    return corpus


def token_counter():
    cache = ROOT / '.local-tools/tiktoken-cache'
    asset = cache / hashlib.sha1(b'https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken').hexdigest()
    if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != '223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7':
        raise ValueError('Missing/invalid local tokenizer cache; downloads forbidden')
    os.environ['TIKTOKEN_CACHE_DIR'] = str(cache)
    import tiktoken
    encoding = tiktoken.get_encoding('cl100k_base')
    return lambda text: len(encoding.encode(text, disallowed_special=())), {
        'name': encoding.name, 'tiktoken_version': importlib.metadata.version('tiktoken'),
        'asset_sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}


def coverage(ids, question):
    sets = question['required_evidence_sets']
    return max(len(set(ids) & set(s)) / len(s) for s in sets), any(set(s) <= set(ids) for s in sets)


def ranking_metrics(hits, question, k):
    relevant = set().union(*map(set, question['required_evidence_sets']))
    values = [int(h['passage_id'] in relevant) for h in hits]
    dcg = sum(value / math.log2(i + 2) for i, value in enumerate(values))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return {'precision_at_5': sum(values) / k,
            'mrr': next((1 / (i + 1) for i, value in enumerate(values) if value), 0),
            'ndcg_at_5': dcg / ideal if ideal else None}


def evaluate(index, questions, count_tokens, config):
    results = []
    # Plain baseline uses the same retrieved seeds and budget, without context expansion.
    plain = {pid: {**p, 'requires': []} for pid, p in index.passages.items()}
    for q in questions:
        for language in ('en', 'fr'):
            timings = []
            for _ in range(3):
                start = time.perf_counter()
                hits = index.search(q['question_' + language], top_k=config['retrieval']['top_k'])
                ranked_at = time.perf_counter()
                raw = assemble(plain, hits, count_tokens, config['context']['max_tokens'])
                raw_at = time.perf_counter()
                assembled = assemble(index.passages, hits, count_tokens, config['context']['max_tokens'])
                end = time.perf_counter()
                timings.append({'retrieval_ms': (ranked_at - start) * 1000,
                                'raw_assembly_ms': (raw_at - ranked_at) * 1000,
                                'expanded_assembly_ms': (end - raw_at) * 1000})
            ranked_ids = [h['passage_id'] for h in hits]
            ranked_recall, ranked_complete = coverage(ranked_ids, q)
            raw_recall, raw_complete = coverage(raw['ids'], q)
            recall, complete = coverage(assembled['ids'], q)
            required = set().union(*map(set, q['required_evidence_sets']))
            results.append({'question_id': q['id'], 'language': language, 'question': q['question_' + language],
                'expected_response_status': q['expected_status'], 'predicted_response_status': None,
                'response_status_evaluated': False, 'hits': hits, 'ranking': ranking_metrics(hits, q, config['retrieval']['top_k']),
                'ranked_reference_recall': ranked_recall, 'ranked_complete_evidence': ranked_complete,
                'raw': raw, 'raw_reference_recall': raw_recall, 'raw_complete_evidence': raw_complete,
                'assembled': assembled, 'assembled_reference_recall': recall, 'assembled_complete_evidence': complete,
                'missing_after_assembly': sorted(required - set(assembled['ids'])),
                'timings_ms': timings, 'timing_repetitions': 3,
                'exact_quote_preservation': all(index.passages[p]['quote_sha256'] == hashlib.sha256(
                    index.passages[p]['quote'].encode()).hexdigest() for p in assembled['ids']),
                'quarantine_leakage_count': sum(index.passages[p]['quarantined'] for p in assembled['ids'])})
    return results


def validate_result_grid(rows, expected_ids, complete_field):
    """Require exactly one boolean result per expected intent/language pair."""
    expected_ids = list(expected_ids)
    if not expected_ids or any(not isinstance(qid, str) or not qid for qid in expected_ids) or len(expected_ids) != len(set(expected_ids)):
        raise ValueError('Expected intent inventory must be nonempty and unique')
    expected = {(qid, language) for qid in expected_ids for language in ('en', 'fr')}
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Malformed result row')
        key = (row.get('question_id'), row.get('language'))
        if key not in expected:
            raise ValueError('Unexpected intent/language result: ' + repr(key))
        if key in seen:
            raise ValueError('Duplicate intent/language result: ' + repr(key))
        if type(row.get(complete_field)) is not bool:
            raise ValueError('Completeness flag must be boolean')
        seen.add(key)
    if seen != expected:
        raise ValueError('Missing intent/language results: ' + repr(sorted(expected - seen)))
    return expected_ids


def summarize(results, expected_ids=None):
    if expected_ids is None:
        expected_ids = [q['id'] for q in read(ROOT / PREPARATION / 'questions.json')['questions']]
    expected_ids = validate_result_grid(results, expected_ids, 'assembled_complete_evidence')
    output = {}
    for language in ('en', 'fr'):
        rows = [r for r in results if r['language'] == language]
        output[language] = {'formulations': len(rows),
            'raw_complete': sum(r['raw_complete_evidence'] for r in rows),
            'assembled_complete': sum(r['assembled_complete_evidence'] for r in rows),
            'mean_raw_reference_recall': statistics.mean(r['raw_reference_recall'] for r in rows),
            'mean_assembled_reference_recall': statistics.mean(r['assembled_reference_recall'] for r in rows),
            'mean_precision_at_5': statistics.mean(r['ranking']['precision_at_5'] for r in rows),
            'mean_mrr': statistics.mean(r['ranking']['mrr'] for r in rows),
            'mean_ndcg_at_5': statistics.mean(r['ranking']['ndcg_at_5'] for r in rows),
            'median_retrieval_ms': statistics.median(t['retrieval_ms'] for r in rows for t in r['timings_ms']),
            'median_expanded_assembly_ms': statistics.median(t['expanded_assembly_ms'] for r in rows for t in r['timings_ms']),
            'max_context_tokens': max(r['assembled']['tokens'] for r in rows),
            'over_budget_bundles': sum(len(r['assembled']['excluded']) for r in rows),
            'quarantine_leaks': sum(r['quarantine_leakage_count'] for r in rows)}
    output['intents_complete_both_languages'] = sum(all(r['assembled_complete_evidence'] for r in results
        if r['question_id'] == qid) for qid in expected_ids)
    output['semantic_answer_evaluation'] = 'not_run_no_answer_layer'
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--spec', type=Path, default=SPEC)
    args = parser.parse_args()
    # No mutation of serving data; all artifacts go in a new explicit directory.
    if args.output.exists():
        raise ValueError('Output exists; never overwrite a run')
    attempts = network_guard()
    started = time.perf_counter()
    verification = verify()
    spec = read(args.spec)
    count_tokens, tokenizer = token_counter()
    build_start = time.perf_counter()
    evidence = read(ROOT / PREPARATION / 'evidence.json')
    corpus = build_corpus(evidence, spec)
    index = BM25(corpus, spec['retrieval']['bilingual_aliases'], spec['retrieval']['k1'], spec['retrieval']['b'],
                 spec['retrieval'].get('index_context', False))
    build_ms = (time.perf_counter() - build_start) * 1000
    args.output.mkdir(parents=True, exist_ok=False)
    dump(args.output / 'corpus.json', {'source_pdf_sha256': evidence['source']['sha256'],
                                       'publication_allowed': False, 'passages': corpus})
    files = ['ingestion/local_passage_retrieval.py', 'experiments/cytiva/cleaning_retrieval.py',
             args.spec.resolve().relative_to(ROOT).as_posix(), str(PREPARATION / 'evidence.json'),
             str(PREPARATION / 'questions.json'), 'experiments/cytiva/reviewed-cleaning-retrieval/review.json']
    manifest = {'status': 'prepared_before_measurement', 'prepared_at_utc': datetime.now(timezone.utc).isoformat(),
        'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'code_and_input_sha256_lf': {f.replace('\\', '/'): digest(ROOT / f) for f in files},
        'config': spec, 'tokenizer': tokenizer, 'corpus_sha256_lf': digest(args.output / 'corpus.json'),
        'python': platform.python_version(), 'platform': platform.system(), 'index_build_ms': build_ms,
        'initialization_ms': (time.perf_counter() - started) * 1000,
        'scope': 'development, 17 curated source excerpts, manual topology; not whole-manual retrieval',
        'timing_note': 'three same-order repetitions; first may be colder; timings under tracemalloc, not production latency',
        'llm_calls': 0, 'api_calls': 0, 'publication_allowed': False}
    dump(args.output / 'manifest-before-run.json', manifest)
    # Reference file is read by evaluation only, after corpus/index/config have been frozen.
    questions = read(ROOT / PREPARATION / 'questions.json')['questions']
    tracemalloc.start()
    rows = evaluate(index, questions, count_tokens, spec)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    summary = summarize(rows, expected_ids=[q['id'] for q in questions])
    summary['peak_python_traced_bytes'] = peak
    summary['resource_limit'] = 'Python traced allocation peak only, not process/system peak RAM'
    dump(args.output / 'results.json', rows)
    dump(args.output / 'metrics.json', summary)
    with (args.output / 'results.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['question', 'language', 'raw_complete', 'assembled_complete', 'raw_recall', 'assembled_recall',
                         'context_tokens', 'missing_after_assembly'])
        for r in rows:
            writer.writerow([r['question_id'], r['language'], r['raw_complete_evidence'], r['assembled_complete_evidence'],
                r['raw_reference_recall'], r['assembled_reference_recall'], r['assembled']['tokens'],
                ' '.join(r['missing_after_assembly'])])
    if attempts:
        raise RuntimeError('Unexpected network attempt; run is invalid')
    manifest.update(status='completed', network_attempts=attempts,
        artifacts_sha256_lf={name: digest(args.output / name) for name in ('corpus.json', 'results.json', 'results.csv', 'metrics.json')})
    dump(args.output / 'manifest.json', manifest)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
