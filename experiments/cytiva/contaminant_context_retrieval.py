"""Four-arm offline vocabulary/section ablation after the first C01-C10 run."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import subprocess
import time

from ingestion.local_passage_retrieval import assemble
from ingestion.lexical_section_context import VocabularyIndex, assemble_overviews
from experiments.cytiva import contaminant_retrieval as base
from experiments.cytiva.cleaning_retrieval import (
    build_corpus, coverage, digest, dump, read, token_counter, validate_result_grid)
from experiments.cytiva.visual_validation import network_guard

ROOT, PACKAGE, PREPARATION = base.ROOT, base.PACKAGE, base.PREPARATION
CONFIG = ROOT / 'experiments/cytiva/contaminant_context_v02.json'
VARIANTS = {'baseline': (False, False), 'vocabulary': (True, False),
            'section': (False, True), 'combined': (True, True)}


def retrieve(index, text, counter, config, sections):
    timings = []
    for _ in range(3):
        start = time.perf_counter()
        hits = index.search(text, config['top_k'])
        at = time.perf_counter()
        if sections:
            context = assemble_overviews(index.passages, hits, text, counter, config, config['max_tokens'])
        else:
            context = assemble(index.passages, hits, counter, config['max_tokens'])
        end = time.perf_counter()
        timings.append({'retrieval_ms': (at-start)*1000, 'assembly_ms': (end-at)*1000})
    return {'hits': hits, 'assembled': context, 'timings': timings}


def summarize(rows, expected_ids):
    if any(r.get('variant') not in VARIANTS for r in rows):
        raise ValueError('Unknown ablation variant')
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
            'unavailable_overviews': sum(r['assembled'].get('overview_status') == 'unavailable' for r in group),
            'median_retrieval_ms': statistics.median(t['retrieval_ms'] for r in group for t in r['timings']),
            'median_assembly_ms': statistics.median(t['assembly_ms'] for r in group for t in r['timings'])}
        for lang in ('en', 'fr'):
            subset = [r for r in group if r['language'] == lang]
            output[variant][lang] = {'complete': sum(r['complete_evidence'] for r in subset),
                'mean_reference_coverage': statistics.mean(r['reference_coverage'] for r in subset)}
        regressions, delta = [], []
        for r in group:
            baseline = next(b for b in rows if (b['variant'], b['question_id'], b['language']) ==
                            ('baseline', r['question_id'], r['language']))
            if r['reference_coverage'] < baseline['reference_coverage']:
                regressions.append({'question_id':r['question_id'], 'language':r['language']})
            delta.append(r['assembled']['tokens']-baseline['assembled']['tokens'])
        output[variant].update(coverage_regressions=regressions, mean_added_context_tokens=statistics.mean(delta))
    for qid in ids:
        for lang in ('en', 'fr'):
            group = {r['variant']:r for r in rows if (r['question_id'],r['language']) == (qid,lang)}
            for a,b in (('baseline','section'),('vocabulary','combined')):
                if group[a]['hits'] != group[b]['hits']:
                    raise ValueError('Section assembly changed paired retrieval')
    output['answer_correctness'] = 'not_evaluated_no_answer_layer'
    return output


def compare_previous(rows, previous):
    old = [r for r in previous if r['variant'] == 'top6']
    current = [r for r in rows if r['variant'] == 'baseline']
    validate_result_grid(old, [f'C{i:02d}' for i in range(1,11)], 'complete_evidence')
    for r in current:
        prior = next(p for p in old if (p['question_id'],p['language']) == (r['question_id'],r['language']))
        if r['assembled']['context'] != prior['assembled']['context'] or r['complete_evidence'] != prior['complete_evidence']:
            raise ValueError('Historical baseline context changed')
        if [h['passage_id'] for h in r['hits']] != [h['passage_id'] for h in prior['hits']]:
            raise ValueError('Historical baseline ranking changed')
        if any(not math.isclose(a['score'],b['score'],rel_tol=1e-12,abs_tol=1e-12)
               for a,b in zip(r['hits'],prior['hits'])):
            raise ValueError('Historical score changed beyond summation tolerance')


def run(output, baseline_run=None):
    output = Path(output)
    if output.exists():
        raise ValueError('Output already exists; earlier runs must remain intact')
    attempts = network_guard()
    protected = base.protected_files()
    verified = base.verify_reference(package=PACKAGE, root=ROOT)
    package_manifest, review = read(PACKAGE/'manifest.json'), read(PACKAGE/'review.json')
    config = read(CONFIG)
    spec = read(ROOT/PREPARATION/'source_context.json')
    if config['top_k'] != 6 or config['max_tokens'] != spec['context']['max_tokens']:
        raise ValueError('Frozen result depth/budget changed')
    pending = package_manifest['not_individually_reviewed_source_ids']
    policy = base.runtime_policy(spec, pending)
    corpus = build_corpus(read(ROOT/PREPARATION/'evidence.json'), policy)
    indices = {flag:VocabularyIndex(corpus, policy['retrieval'], config['vocabulary'] if flag else None)
               for flag in (False,True)}
    if any(set(pending) & set(index.docs) for index in indices.values()):
        raise ValueError('Pending source indexed')
    counter, tokenizer = token_counter()
    previous_files = {}
    if baseline_run is not None:
        baseline_run = Path(baseline_run).resolve()
        previous_files = {(baseline_run/name).relative_to(ROOT).as_posix():digest(baseline_run/name)
                          for name in ('manifest.json','metrics.json','results.json')}
    files = sorted(base.SUPPORT | base.DEPENDENCIES | {
        (PACKAGE/name).relative_to(ROOT).as_posix() for name in base.FILES | {'manifest.json'}} | {
        'ingestion/lexical_section_context.py','experiments/cytiva/contaminant_context_retrieval.py',
        'experiments/cytiva/contaminant_retrieval.py','tests/test_contaminant_context.py',
        'tests/test_contaminant_retrieval.py','experiments/cytiva/cleaning_retrieval.py',
        'experiments/cytiva/visual_validation.py',CONFIG.relative_to(ROOT).as_posix()})
    output.mkdir(parents=True,exist_ok=False)
    dump(output/'corpus.json', {'passages':corpus,'pending_source_ids':pending})
    dump(output/'lexical-indices.json', {str(flag):{pid:dict(tf) for pid,tf in ix.docs.items()}
                                       for flag,ix in indices.items()})
    manifest = {'status':'frozen_before_measurement','prepared_at_utc':datetime.now(timezone.utc).isoformat(),
        'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        'config':config,'source_runtime_policy':policy,'variants':VARIANTS,'tokenizer':tokenizer,
        'pending_source_ids':pending,'reference_verification':verified,
        'reference_review_sha256_lf':digest(PACKAGE/'review.json'),
        'reference_package_manifest_sha256_lf':digest(PACKAGE/'manifest.json'),
        'code_and_input_sha256_lf':{f:digest(ROOT/f) for f in files},
        'previous_baseline_sha256_lf':previous_files,
        'corpus_sha256_lf':digest(output/'corpus.json'),'indices_sha256_lf':digest(output/'lexical-indices.json'),
        'protected_file_sha256_raw':protected,'llm_calls':0,'api_calls':0,'publication_allowed':False,
        'benchmark_results_human_validated':False,
        'scope':'Development ablation designed after C03-C06 failures; navigation rules are not new human-validated source facts',
        'timing_scope':'3 repetitions; rotating variant order by intent; excludes initialization'}
    dump(output/'manifest-before-run.json',manifest)
    for f in files:
        p=output/'input-snapshot'/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/f).read_bytes())
    questions=read(ROOT/PREPARATION/'questions.json')['questions']
    decisions={d['question_id']:d['decision'] for d in review['decisions']}
    if set(decisions)!={q['id'] for q in questions}:
        raise ValueError('Reference question inventory changed')
    rows=[]
    for i,q in enumerate(questions):
        order=list(VARIANTS);order=order[i%4:]+order[:i%4]
        for lang in ('en','fr'):
            text=q['question_'+lang]
            for variant in order:
                vocab,sections=VARIANTS[variant];index=indices[vocab]
                result=retrieve(index,text,counter,config,sections)
                base.check_context(index.passages,result['assembled'],counter,config['max_tokens'],pending)
                recall,complete=coverage(result['assembled']['ids'],q)
                ranking=index.search(text,len(index.docs));required=set().union(*map(set,q['required_evidence_sets']))
                rows.append({**result,'question_id':q['id'],'question':text,'language':lang,'variant':variant,
                    'full_ranking_diagnostic':ranking,'reference_coverage':recall,'complete_evidence':complete,
                    'missing':sorted(required-set(result['assembled']['ids'])),
                    'missing_diagnostics':base.missing_diagnostics(index,ranking,result,required),
                    'reference_status_at_preparation':q['reference_status'],'reference_review_decision':decisions[q['id']],
                    'expected_response_status':q['expected_status'],'response_status_evaluated':False})
    metrics=summarize(rows,[q['id'] for q in questions])
    if baseline_run is not None:
        compare_previous(rows,read(baseline_run/'results.json'))
    after=base.protected_files()
    if any(after.get(f)!=h for f,h in protected.items()):
        raise ValueError('Earlier tracked file, journal or run changed')
    if any(digest(ROOT/f)!=h for f,h in {**manifest['code_and_input_sha256_lf'],**previous_files}.items()):
        raise ValueError('Frozen input or prior baseline changed')
    if attempts:
        raise RuntimeError('Unexpected network attempt')
    dump(output/'results.json',rows);dump(output/'metrics.json',metrics)
    manifest.update(status='completed',benchmark_executed=True,network_attempts=attempts,
        historical_baseline_reproduced=baseline_run is not None,protected_files_unchanged=True,pending_source_leakage=0,
        artifact_sha256_lf={f:digest(output/f) for f in ('results.json','metrics.json','corpus.json','lexical-indices.json')})
    dump(output/'manifest.json',manifest)
    return metrics


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline-run',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.output,args.baseline_run),ensure_ascii=False))
