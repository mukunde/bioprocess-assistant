"""Development v03 comparison on opened H/C references; no independent score claim."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
import platform
from pathlib import Path
import statistics
import subprocess
import time

from experiments.cytiva import section_evaluation as frozen
from experiments.cytiva import contaminant_retrieval as source
from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
from experiments.cytiva.visual_validation import network_guard
from ingestion.scoped_passage_context import ScopedContextIndex

ROOT=frozen.ROOT
CONFIG=ROOT/'experiments/cytiva/section_navigation_v03.json'


def validate_grid(rows,expected_ids):
    keys=[(r['question_id'],r['language']) for r in rows]
    if len(keys)!=len(set(keys)) or set(keys)!={(qid,lang) for qid in expected_ids for lang in ('en','fr')}:
        raise ValueError('Missing or duplicate expected formulation')


def summary(rows):
    ids=sorted({r['question_id'] for r in rows})
    keys=[(r['question_id'],r['language']) for r in rows]
    if len(keys)!=len(set(keys)) or set(keys)!={(qid,lang) for qid in ids for lang in ('en','fr')} or not ids:
        raise ValueError('Incomplete/duplicate development result grid')
    return {'intents':len(ids),'formulations':len(rows),
        'complete_both_languages':sum(all(r['complete_evidence'] for r in rows if r['question_id']==qid) for qid in ids),
        'complete_by_language':{lang:sum(r['complete_evidence'] for r in rows if r['language']==lang) for lang in ('en','fr')},
        'mean_context_tokens':statistics.mean(r['assembled']['tokens'] for r in rows),
        'max_context_tokens':max(r['assembled']['tokens'] for r in rows),
        'contexts_outside_acceptable_reference':sum(bool(r.get('outside_acceptable_ids')) for r in rows) if all('outside_acceptable_ids' in r for r in rows) else None,
        'mean_outside_acceptable_subset_tokens':statistics.mean(r['outside_acceptable_subset_tokens'] for r in rows) if all('outside_acceptable_subset_tokens' in r for r in rows) else None,
        'unavailable_roles':sum(len(r.get('unavailable_source_roles',[])) for r in rows),
        'excluded_bundles':sum(len(r['assembled']['excluded']) for r in rows)}


def score_rows(contexts,refs,passages,counter):
    output=[]
    for result in contexts:
        ref=refs[result['question_id']];present=set(result['assembled']['ids'])
        sets=list(map(set,ref['required_evidence_sets']))
        best=max(sets,key=lambda s:len(s & present)/len(s))
        row={**result,'complete_evidence':any(s<=present for s in sets),
            'reference_coverage':len(best & present)/len(best),'missing_ids':sorted(best-present),
            'answer_quality':'not_evaluated','expected_status':ref['expected_status'],
            'response_status_evaluated':False}
        if 'acceptable_context_ids' in ref:
            from ingestion.local_passage_retrieval import serialize
            outside=[pid for pid in result['assembled']['ids'] if pid not in ref['acceptable_context_ids']]
            row['outside_acceptable_ids']=outside
            row['outside_acceptable_subset_tokens']=counter(serialize(passages,outside)) if outside else 0
        output.append(row)
    summary(output)
    return output


def inventory():
    names=subprocess.check_output(['git','ls-files'],cwd=ROOT).decode().splitlines()
    paths={ROOT/n for n in names}
    paths|={p for p in (ROOT/'data/experiments').rglob('*') if p.is_file()}
    paths|={ROOT/n for n in frozen.read(ROOT/frozen.PACKAGE/'manifest.json')['file_sha256_lf']}
    paths.add(ROOT/frozen.PACKAGE/'manifest.json')
    paths.add(ROOT/'docs/experiments/cytiva-section-evaluation-results.md')
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}


def run(output,review_path,c_baseline=None):
    output=Path(output).resolve()
    review_path=Path(review_path).resolve()
    if c_baseline is not None:c_baseline=Path(c_baseline).resolve()
    if output.exists():raise ValueError('Output exists; do not overwrite an earlier trial')
    if os.environ.get('PYTHONHASHSEED')!='0':raise ValueError('Use PYTHONHASHSEED=0 for reproducible development comparison')
    attempts=network_guard()
    verified=frozen.verify()
    human=frozen.review_gate(review_path,verified['manifest_sha256_lf'])
    before=inventory()
    candidate=frozen.read(ROOT/frozen.PACKAGE/'candidate.json')
    config=frozen.read(CONFIG)
    if (config['top_k'],config['max_tokens'])!=(6,2048):raise ValueError('Unexpected depth/budget')
    started=time.perf_counter()
    corpus=build_corpus(frozen.read(ROOT/source.PREPARATION/'evidence.json'),candidate['source_runtime_policy'])
    index=ScopedContextIndex(corpus,candidate['source_runtime_policy']['retrieval'],config)
    pending=candidate['pending_source_ids']
    if set(pending) & index.docs.keys():raise ValueError('Pending source indexed')
    counter,tokenizer=token_counter()
    initialization_ms=(time.perf_counter()-started)*1000
    h_baseline=ROOT/candidate['run_directory']/'contexts-unscored.json'
    if not h_baseline.is_file():raise ValueError('Preserved H baseline required; never rerun it here')
    inputs=set(frozen.read(ROOT/frozen.PACKAGE/'manifest.json')['file_sha256_lf'])|{
        CONFIG.relative_to(ROOT).as_posix(),'ingestion/scoped_passage_context.py',
        'experiments/cytiva/section_navigation_retrieval.py','tests/test_scoped_passage_context.py',
        'tests/test_section_navigation_runner.py',(ROOT/frozen.PACKAGE/'manifest.json').relative_to(ROOT).as_posix()}
    fingerprints={n:frozen.digest(ROOT/n) for n in inputs}
    previous={h_baseline.relative_to(ROOT).as_posix():frozen.digest(h_baseline)}
    if c_baseline is not None:previous[Path(c_baseline).relative_to(ROOT).as_posix()]=frozen.digest(c_baseline)
    output.mkdir(parents=True,exist_ok=False)
    manifest={'status':'inputs_frozen_before_development_measurement','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Post-H failure development tuning; H/C are known references, not an independent evaluation',
        'code_and_input_sha256_lf':fingerprints,'previous_result_sha256_lf':previous,
        'protected_file_sha256_raw':before,'review_sha256_lf':frozen.digest(review_path),
        'tokenizer':tokenizer,'python_version':platform.python_version(),'python_hash_seed':'0','config':config,'initialization_ms':initialization_ms,
        'llm_calls':0,'api_calls':0,'automatic_adoption':False,'pending_source_ids':pending}
    frozen.dump(output/'manifest-before-run.json',manifest)
    for n in inputs:
        dest=output/'input-snapshot'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    frozen.dump(output/'human-review-snapshot.json',human)
    frozen.dump(output/'corpus.json',{'passages':corpus,'indexed_ids':list(index.docs),'pending_source_ids':pending})
    contexts=[]
    try:
        # Strip C references from runtime rows before handing text to retrieval.
        h=frozen.read(ROOT/frozen.PACKAGE/'questions.json')['questions']
        c=frozen.read(ROOT/source.PREPARATION/'questions.json')['questions']
        queries=[{k:q[k] for k in ('id','question_en','question_fr')} for q in h+c]
        for q in queries:
            for lang in ('en','fr'):
                timings=[]
                for _ in range(3):
                    at=time.perf_counter();result=index.retrieve(q['question_'+lang],counter)
                    timings.append((time.perf_counter()-at)*1000)
                source.check_context(index.passages,result['assembled'],counter,2048,pending)
                contexts.append({'question_id':q['id'],'language':lang,**result,'total_times_ms':timings})
                frozen.dump(output/'contexts-unscored.json',contexts)
        validate_grid(contexts,[q['id'] for q in queries])
        # Reference IDs and answers enter only after all contexts are on disk.
        refs={r['question_id']:r for r in frozen.read(ROOT/frozen.PACKAGE/'references.json')['references']}
        refs.update({q['id']:q for q in c})
        scored=score_rows(contexts,refs,index.passages,counter)
        hrows=[r for r in scored if r['question_id'].startswith('H')]
        crows=[r for r in scored if r['question_id'].startswith('C')]
        old_h=score_rows(frozen.read(h_baseline),refs,index.passages,counter)
        validate_grid(old_h,[q['id'] for q in h])
        comparison={'H_new':summary(hrows),'H_recorded_section_only':summary(old_h),'C_new':summary(crows),
                    'scope':'Development comparison only; old timings are not causally comparable'}
        if c_baseline is not None:
            old_c=[r for r in frozen.read(c_baseline) if r['variant']=='section']
            validate_grid(old_c,[q['id'] for q in c])
            comparison['C_recorded_section_only']=summary(score_rows(old_c,refs,index.passages,counter))
        regressions=[]
        for row in scored:
            prior=next((p for p in old_h if (p['question_id'],p['language'])==(row['question_id'],row['language'])),None)
            if prior and row['reference_coverage']<prior['reference_coverage']:regressions.append((row['question_id'],row['language']))
        comparison['H_coverage_regressions']=regressions
        if attempts:raise ValueError('Network attempted')
        for n,hsh in before.items():
            if not (ROOT/n).is_file() or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=hsh:raise ValueError('Earlier file changed: '+n)
        for n,hsh in fingerprints.items():
            if frozen.digest(ROOT/n)!=hsh:raise ValueError('Candidate input changed: '+n)
        for n,hsh in previous.items():
            if frozen.digest(ROOT/n)!=hsh:raise ValueError('Previous result changed: '+n)
        frozen.verify()
        frozen.dump(output/'results.json',scored);frozen.dump(output/'metrics.json',comparison)
        manifest.update(status='completed',network_attempts=attempts,protected_files_unchanged=True,pending_source_leakage=0,
            artifact_sha256_lf={n:frozen.digest(output/n) for n in ('contexts-unscored.json','results.json','metrics.json','corpus.json')})
        frozen.dump(output/'manifest.json',manifest)
        return comparison
    except Exception as exc:
        frozen.dump(output/'failure.json',{'error':str(exc),'completed_formulations':len(contexts),'planned_formulations':40,'status':'failed_preserve_artifacts'})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--review',type=Path,required=True)
    parser.add_argument('--c-baseline',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.output,args.review,args.c_baseline),ensure_ascii=False))
