"""Prospective v03b package: verify by default; no measurement before human review."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path('experiments/cytiva/v03b-evaluation-v01')
IDS=[f'V{i:02d}' for i in range(1,13)]
PACKET_FILES={'method-lock.json','candidate.json','questions.json','references.json','PROTOCOL.md'}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def dump(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def require(ok,message):
    if not ok:raise ValueError(message)


def verify(root=ROOT):
    root=Path(root);p=root/PACKAGE
    manifest=read(p/'manifest.json');lock=read(p/'method-lock.json')
    expected=set(lock['file_sha256_lf'])|{(PACKAGE/n).as_posix() for n in PACKET_FILES}|{'experiments/cytiva/v03b_evaluation.py','tests/test_v03b_evaluation.py'}
    require(set(manifest['file_sha256_lf'])==expected,'Freeze inventory changed')
    for n,h in manifest['file_sha256_lf'].items():
        path=root/n
        require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and digest(path)==h,'Frozen file missing/changed: '+n)
    for n,h in lock['file_sha256_lf'].items():require(digest(root/n)==h,'v03b method changed: '+n)
    candidate=read(p/'candidate.json');config=candidate['config']
    require(candidate['method_lock_sha256_lf']==digest(p/'method-lock.json'),'Method lock binding changed')
    require(config==read(root/'experiments/cytiva/section_navigation_v03.json'),'v03b config copy changed')
    require(config['id']=='cytiva-scoped-section-navigation-v03b' and (config['top_k'],config['max_tokens'],config['fallback_relative_score'])==(6,2048,0.65),'Wrong candidate')
    pending={'E118-I','E121-EQ'}
    require(set(candidate['pending_source_ids'])==pending,'Excluded-source inventory changed')
    policy=read(root/'experiments/cytiva/contaminants-pilot-v01/source_context.json')
    policy['quarantined_ids']=sorted(set(policy['quarantined_ids'])|pending)
    policy['searchable_ids']=[pid for pid in policy['searchable_ids'] if pid not in pending]
    require(candidate['source_runtime_policy']==policy,'Source eligibility/dependencies changed')
    queries=read(p/'questions.json')['questions'];packet=read(p/'references.json');refs=packet['references']
    require([q['id'] for q in queries]==IDS and [r['question_id'] for r in refs]==IDS,'Prospective question grid changed')
    evidence=read(root/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    lookup={s['id']:s for s in evidence['passages']}
    eligible=set(lookup)-pending
    require(set(packet['eligible_source_ids'])==eligible and set(packet['excluded_source_ids'])==pending,'Reference source registry changed')
    require(packet['source_pdf']==evidence['source'],'PDF/version identity changed')
    require(len(packet['source_passages'])==len(eligible) and {s['id'] for s in packet['source_passages']}==eligible,'Incomplete source review packet')
    for source in packet['source_passages']:
        require(source==lookup[source['id']],'Verbatim source/provenance changed')
        require(hashlib.sha256(source['quote'].encode()).hexdigest()==source['quote_sha256'],'Quote hash changed')
    from experiments.cytiva.verify_contaminant_questions_package import verify as source_verify
    source_verify(root=root,package=root/'experiments/cytiva/reviewed-contaminant-questions')
    require(packet['source_review_manifest_sha256_lf']==digest(root/'experiments/cytiva/reviewed-contaminant-questions/manifest.json'),'Existing source-review binding changed')
    for query,ref in zip(queries,refs):
        require(set(query)=={'id','family','question_en','question_fr','synthetic_case'},'Gold data in runtime query row')
        require(all(query['question_'+lang].strip() for lang in ('en','fr')),'Empty language formulation')
        required=set().union(*map(set,ref['required_evidence_sets']))
        acceptable=set(ref['acceptable_context_ids']);unrequested=set(ref['unrequested_context_ids'])
        require(required and required<=acceptable<=eligible and unrequested<=eligible and not acceptable & unrequested,'Invalid source/reference scope')
        require(ref['human_review_status']=='pending','Preparation cannot confer approval')
        require(ref['expected_status'] in ('answer','clarify','refuse','source_ambiguity'),'Unknown expected response status')
        require(set(ref['pending_source_ids_to_withhold'])<=pending,'Wrong pending-source reference')
        if 'absence_assertion' in ref:
            absence=ref['absence_assertion']
            require(set(absence['eligible_source_ids'])==eligible,'Absence scope changed')
            require(not any('pressure' in lookup[pid]['quote'].lower() for pid in eligible),'Pressure absence claim needs renewed reference review')
    require(manifest['status']=='frozen_pending_human_reference_review' and not manifest['benchmark_executed'],'Preparation state changed')
    return {'integrity':'verified','intents':12,'formulations':24,'pending_reference_reviews':12,
        'preparation_manifest_sha256_lf':digest(p/'manifest.json'),'method_lock_sha256_lf':digest(p/'method-lock.json'),
        'evaluation_executed_by_this_command':False}


def review_gate(path,verification,queries,refs):
    review=read(path)
    require(review.get('manifest_sha256_lf')==verification['preparation_manifest_sha256_lf'] and review.get('method_lock_sha256_lf')==verification['method_lock_sha256_lf'],'Human review bound to another freeze')
    rows=review.get('decisions',[])
    require(len(rows)==len(IDS) and {r.get('question_id') for r in rows}==set(IDS),'All twelve questions need human decisions')
    for row in rows:
        qid=row['question_id']
        require(row.get('decision') in ('validated','validated_with_reservation') and bool(row.get('human_quote','').strip()),'Pending/rejected or undocumented human decision')
        require(row.get('question_sha256_canonical')==canonical(queries[qid]) and row.get('reference_sha256_canonical')==canonical(refs[qid]),'Human decision/reference binding changed')
        require(row.get('retained_reservations')==refs[qid]['reservations'],'Review reservations differ from frozen references')
        at=datetime.fromisoformat(row.get('reviewed_at_utc','').replace('Z','+00:00'))
        require(at.tzinfo is not None and at.utcoffset().total_seconds()==0,'Review timestamp must be UTC')
    return review


def score(contexts,references):
    keys=[(r['question_id'],r['language']) for r in contexts]
    require(len(keys)==len(set(keys)) and set(keys)=={(qid,lang) for qid in IDS for lang in ('en','fr')},'Incomplete/duplicate prospective result grid')
    refs={r['question_id']:r for r in references};rows=[]
    for result in contexts:
        ref=refs[result['question_id']];present=set(result['assembled']['ids'])
        alternatives=list(map(set,ref['required_evidence_sets']))
        best=max(alternatives,key=lambda s:len(s & present)/len(s))
        rows.append({'question_id':result['question_id'],'language':result['language'],
            'complete_evidence':any(s<=present for s in alternatives),'reference_coverage':len(best & present)/len(best),
            'missing_ids':sorted(best-present),'outside_acceptable_ids':sorted(present-set(ref['acceptable_context_ids'])),
            'unrequested_context_ids_present':sorted(present & set(ref['unrequested_context_ids'])),
            'expected_status':ref['expected_status'],'response_status_evaluated':False})
    both=sum(all(r['complete_evidence'] for r in rows if r['question_id']==qid) for qid in IDS)
    scope_failures=sum(bool(r['unrequested_context_ids_present']) for r in rows)
    return {'rows':rows,'intents':12,'planned_formulations':24,'complete_both_languages':both,
        'complete_by_language':{lang:sum(r['complete_evidence'] for r in rows if r['language']==lang) for lang in ('en','fr')},
        'mean_reference_coverage':statistics.mean(r['reference_coverage'] for r in rows),
        'contexts_outside_acceptable_reference':sum(bool(r['outside_acceptable_ids']) for r in rows),
        'explicit_scope_failures':scope_failures,
        'pilot_gate':'eligible_for_limited_end_to_end_consideration' if both==12 and scope_failures==0 else 'blocked_missing_evidence_or_scope',
        'answer_quality':'not_evaluated','automatic_adoption':False}


def make_runtime(root,candidate):
    from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
    from ingestion.scoped_passage_context import ScopedContextIndex
    evidence=read(Path(root)/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    corpus=build_corpus(evidence,candidate['source_runtime_policy'])
    index=ScopedContextIndex(corpus,candidate['source_runtime_policy']['retrieval'],candidate['config'])
    require(not set(candidate['pending_source_ids']) & index.docs.keys(),'Pending source indexed')
    counter,tokenizer=token_counter()
    return index,counter,tokenizer


def validate_context(result,passages,counter,pending):
    from experiments.cytiva.contaminant_retrieval import check_context
    check_context(passages,result['assembled'],counter,2048,pending)


def protected_files(root,output):
    root=Path(root);output=Path(output).resolve()
    paths={root/n for n in subprocess.check_output(['git','ls-files'],cwd=root).decode().splitlines()}
    paths|={p for p in (root/'data/experiments').rglob('*') if p.is_file() and not p.resolve().is_relative_to(output)}
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}


def run(review_path,root=ROOT):
    root=Path(root).resolve();p=root/PACKAGE
    verified=verify(root)
    queries=read(p/'questions.json')['questions'];refs=read(p/'references.json')['references']
    review_path=Path(review_path).resolve()
    review=review_gate(review_path,verified,{q['id']:q for q in queries},{r['question_id']:r for r in refs})
    lock=read(p/'method-lock.json');candidate=read(p/'candidate.json')
    require(platform.python_version()==lock['python_version'] and os.environ.get('PYTHONHASHSEED')=='0','Pinned Python/hash-seed environment changed')
    require(importlib.metadata.version('tiktoken')==lock['tokenizer']['tiktoken_version'],'Pinned tokenizer version changed')
    output=(root/candidate['run_directory']).resolve()
    require(output.is_relative_to((root/'data/experiments').resolve()),'Unexpected output location')
    if output.exists():raise ValueError('Existing evaluation output: do not retry or overwrite this frozen ID')
    from experiments.cytiva.visual_validation import network_guard
    attempts=network_guard()
    output.mkdir(parents=True,exist_ok=False)
    review_hash=digest(review_path)
    dump(output/'reservation.json',{'status':'reserved_no_retry','at_utc':datetime.now(timezone.utc).isoformat(),
        'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],'review_sha256_lf':review_hash})
    contexts=[]
    try:
        (output/'human-review-snapshot.json').write_bytes(review_path.read_bytes())
        require(read(output/'human-review-snapshot.json')==review,'Human review changed before measurement')
        before=protected_files(root,output)
        manifest=read(p/'manifest.json')
        for n,h in manifest['file_sha256_lf'].items():
            require(digest(root/n)==h,'Frozen input changed before snapshot')
            target=output/'input-snapshot'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/n).read_bytes())
        target=output/'input-snapshot'/PACKAGE/'manifest.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((p/'manifest.json').read_bytes())
        at=time.perf_counter();index,counter,tokenizer=make_runtime(root,candidate)
        require(tokenizer==lock['tokenizer'],'Tokenizer identity changed')
        initialization_ms=(time.perf_counter()-at)*1000
        dump(output/'manifest-before-run.json',{'verification':verified,'candidate':candidate,'tokenizer':tokenizer,
            'initialization_ms':initialization_ms,'human_review_sha256_lf':review_hash,
            'protected_file_sha256_raw':before,'llm_calls':0,'api_calls':0,'automatic_adoption':False})
        for query in queries:
            for language in ('en','fr'):
                timings=[];first=None
                for _ in range(candidate['timing_repetitions']):
                    at=time.perf_counter();result=index.retrieve(query['question_'+language],counter)
                    timings.append((time.perf_counter()-at)*1000)
                    if first is None:first=result['assembled']['context']
                    require(result['assembled']['context']==first,'Repeated context changed; no best-repeat selection allowed')
                validate_context(result,index.passages,counter,candidate['pending_source_ids'])
                contexts.append({'question_id':query['id'],'language':language,**result,'total_times_ms':timings})
                dump(output/'contexts-unscored.json',contexts)
        # Gold is used only after all contexts have been persisted.
        metrics=score(contexts,read(p/'references.json')['references'])
        metrics.update(mean_context_tokens=statistics.mean(r['assembled']['tokens'] for r in contexts),
            max_context_tokens=max(r['assembled']['tokens'] for r in contexts),
            excluded_bundles=sum(len(r['assembled']['excluded']) for r in contexts),
            unavailable_source_roles=sum(len(r['unavailable_source_roles']) for r in contexts),
            median_total_ms=statistics.median(t for r in contexts for t in r['total_times_ms']))
        require(not attempts,'Network attempted')
        for n,h in before.items():require((root/n).is_file() and hashlib.sha256((root/n).read_bytes()).hexdigest()==h,'Earlier file changed: '+n)
        require(digest(review_path)==review_hash and digest(output/'human-review-snapshot.json')==review_hash,'Human review changed during evaluation')
        verify(root)
        dump(output/'metrics.json',metrics)
        dump(output/'verification.json',{'status':'completed','evaluation_executed':True,'network_attempts':attempts,
            'pending_source_leakage':0,'earlier_files_unchanged':True,'automatic_adoption':False,
            'artifact_sha256_lf':{n:digest(output/n) for n in ('contexts-unscored.json','metrics.json')}})
        return metrics
    except Exception as exc:
        dump(output/'failure.json',{'status':'failed_no_retry','error':str(exc),'planned_formulations':24,
            'completed_formulations':len(contexts),'unexecuted_formulations':24-len(contexts),'pilot_gate':'blocked',
            'network_attempts':attempts})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--review',type=Path)
    args=parser.parse_args()
    if args.run and args.review is None:parser.error('--run requires complete separate human review via --review')
    print(json.dumps(run(args.review) if args.run else verify(),ensure_ascii=False))
