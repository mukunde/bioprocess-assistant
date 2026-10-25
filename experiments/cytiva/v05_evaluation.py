"""Frozen v05 prospective X01-X12: integrity only unless reviewed --run is requested."""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import time

from experiments.cytiva import v03b_evaluation as base

ROOT=base.ROOT
PACKAGE=Path('experiments/cytiva/v05-evaluation-v01')
IDS=[f'X{i:02d}' for i in range(1,13)]
PACKET_FILES={'method-lock.json','candidate.json','questions.json','references.json','PROTOCOL.md'}
EVALUATION_DEPENDENCIES={'experiments/cytiva/v03b_evaluation.py',*(str(base.PACKAGE/n).replace('\\','/') for n in PACKET_FILES|{'manifest.json'})}
read,dump,digest,canonical,require=base.read,base.dump,base.digest,base.canonical,base.require


def verify(root=ROOT):
    root=Path(root);p=root/PACKAGE;lock=read(p/'method-lock.json');manifest=read(p/'manifest.json')
    expected=set(lock['file_sha256_lf'])|{(PACKAGE/n).as_posix() for n in PACKET_FILES}|{'experiments/cytiva/v05_evaluation.py'}|EVALUATION_DEPENDENCIES
    require(set(manifest['file_sha256_lf'])==expected,'Freeze inventory changed')
    for name,h in manifest['file_sha256_lf'].items():
        path=root/name
        require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and digest(path)==h,'Frozen input missing/changed: '+name)
    for name,h in lock['file_sha256_lf'].items():require(digest(root/name)==h,'v05 method changed: '+name)
    base.verify(root)
    c=read(p/'candidate.json');old=read(root/base.PACKAGE/'candidate.json')
    require(c['method_lock_sha256_lf']==digest(p/'method-lock.json'),'Method lock binding changed')
    require(c['config']==read(root/'experiments/cytiva/section_navigation_v05.json'),'v05 config copy changed')
    require(c['config']['id']=='cytiva-compositional-section-navigation-v05' and (c['config']['top_k'],c['config']['max_tokens'],c['config']['fallback_relative_score'])==(6,2048,0.65),'Wrong candidate')
    require(c['source_runtime_policy']==old['source_runtime_policy'] and c['pending_source_ids']==['E118-I','E121-EQ'],'Source policy changed')
    require(c['timing_repetitions']==3 and c['run_directory']=='data/experiments/cytiva/v05-evaluation-v01/locked-run','Run protocol changed')
    require(not c['automatic_adoption'] and not c['publication_allowed'],'Candidate scope changed')
    q=read(p/'questions.json')['questions'];packet=read(p/'references.json');refs=packet['references']
    require([r['id'] for r in q]==IDS and [r['question_id'] for r in refs]==IDS,'Prospective grid changed')
    evidence=read(root/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    sources={s['id']:s for s in evidence['passages']};eligible=set(sources)-set(c['pending_source_ids'])
    require(packet['source_pdf']==evidence['source'],'PDF identity changed')
    require(set(packet['eligible_source_ids'])==eligible and packet['excluded_source_ids']==c['pending_source_ids'],'Reference source policy changed')
    require(len(packet['source_passages'])==25 and {s['id'] for s in packet['source_passages']}==eligible,'Exact source inventory changed')
    for s in packet['source_passages']:
        require(s==sources[s['id']] and hashlib.sha256(s['quote'].encode()).hexdigest()==s['quote_sha256'],'Source quote/provenance changed')
    require(packet['source_review_manifest_sha256_lf']==digest(root/'experiments/cytiva/reviewed-contaminant-questions/manifest.json'),'Source review binding changed')
    allowed_diagnostics={'navigation_complete','source_support_complete','phase_conflicts_contains','source_limitations_contains','unavailable_roles_contains','clarification_required'}
    for query,ref in zip(q,refs):
        require(set(query)=={'id','family','question_en','question_fr','synthetic_case'},'Reference data in runtime query')
        require(all(query['question_'+lang].strip() for lang in ('en','fr')) and type(query['synthetic_case']) is bool,'Invalid bilingual query')
        required=set().union(*map(set,ref['required_evidence_sets']));acceptable=set(ref['acceptable_context_ids']);banned=set(ref['unrequested_context_ids'])
        require(required and required<=acceptable<=eligible and banned<=eligible and not acceptable & banned,'Invalid reference source scope')
        from experiments.cytiva.verify_section_evaluation_package import closure
        registry={pid:dict(sources[pid],requires=c['source_runtime_policy']['requires'][pid]) for pid in sources}
        for bundle in ref['required_evidence_sets']:
            require(all(set(closure(registry,pid))<=set(bundle) for pid in bundle),'Required dependency closure changed')
        require(ref['source_seeds'] and set(ref['source_seeds'])<=required,'Reference seeds changed')
        require(ref['human_review_status']=='pending','Preparation cannot confer human approval')
        require(ref['expected_status'] in ('answer','clarify','source_ambiguity','answer_with_source_limit','refuse'),'Unknown reference status')
        require(set(ref['pending_source_ids_to_withhold'])<=set(c['pending_source_ids']),'Excluded-source boundary changed')
        diagnostics=ref['expected_diagnostics']
        require(set(diagnostics)<=allowed_diagnostics,'Unknown diagnostic criterion')
        for k,value in diagnostics.items():
            require((type(value) is bool) if k in ('navigation_complete','source_support_complete','clarification_required') else (isinstance(value,list) and value and all(isinstance(x,str) and x for x in value)),'Invalid diagnostic criterion')
        if 'absence_assertion' in ref:
            absence=ref['absence_assertion']
            require(set(absence['eligible_source_ids'])==eligible and not any('pressure' in sources[pid]['quote'].lower() for pid in eligible),'Pressure absence scope changed')
    require(manifest['status']=='frozen_pending_human_reference_review' and not manifest['benchmark_executed'],'Preparation state changed')
    return {'integrity':'verified','intents':12,'formulations':24,'pending_reference_reviews':12,
            'preparation_manifest_sha256_lf':digest(p/'manifest.json'),'method_lock_sha256_lf':digest(p/'method-lock.json'),
            'evaluation_executed_by_this_command':False}


def review_gate(path,verification,queries,refs):
    review=read(path)
    require(review.get('manifest_sha256_lf')==verification['preparation_manifest_sha256_lf'] and review.get('method_lock_sha256_lf')==verification['method_lock_sha256_lf'],'Human review bound to another freeze')
    rows=review.get('decisions',[])
    require(len(rows)==12 and {r.get('question_id') for r in rows}==set(IDS),'All twelve questions need human decisions')
    for row in rows:
        qid=row['question_id']
        require(row.get('decision') in ('validated','validated_with_reservation') and bool(row.get('human_quote','').strip()),'Missing/invalid human decision')
        require(row.get('question_sha256_canonical')==canonical(queries[qid]) and row.get('reference_sha256_canonical')==canonical(refs[qid]),'Human decision/reference binding changed')
        require(row.get('retained_reservations')==refs[qid]['reservations'],'Human reservations changed')
        at=datetime.fromisoformat(row.get('reviewed_at_utc','').replace('Z','+00:00'))
        require(at.tzinfo is not None and at.utcoffset().total_seconds()==0,'Review timestamp must be UTC')
    return review


def diagnostic_failures(result,expected):
    failures=[]
    observed={'phase_conflicts_contains':result.get('navigation_plan',{}).get('phase_mentions',{}).get('conflicts',[]),
              'source_limitations_contains':[r.get('role') for r in result.get('source_limitations',[])],
              'unavailable_roles_contains':[r.get('role') for r in result.get('unavailable_source_roles',[])]}
    for key,value in expected.items():
        if key=='clarification_required':
            if result.get('navigation_plan',{}).get(key) is not value:failures.append(key)
        elif key in observed:
            if not set(value)<=set(observed[key]):failures.append(key)
        elif result.get(key) is not value:failures.append(key)
    return failures


def score(contexts,references):
    keys=[(r['question_id'],r['language']) for r in contexts]
    require(len(keys)==len(set(keys)) and set(keys)=={(qid,lang) for qid in IDS for lang in ('en','fr')},'Incomplete/duplicate prospective grid')
    refs={r['question_id']:r for r in references};rows=[]
    for result in contexts:
        ref=refs[result['question_id']];ids=set(result['assembled']['ids']);alternatives=list(map(set,ref['required_evidence_sets']))
        best=max(alternatives,key=lambda s:len(s & ids)/len(s))
        rows.append({'question_id':result['question_id'],'language':result['language'],
            'complete_evidence':any(s<=ids for s in alternatives),'reference_coverage':len(best & ids)/len(best),
            'missing_ids':sorted(best-ids),'outside_acceptable_ids':sorted(ids-set(ref['acceptable_context_ids'])),
            'unrequested_context_ids_present':sorted(ids & set(ref['unrequested_context_ids'])),
            'diagnostic_failures':diagnostic_failures(result,ref['expected_diagnostics']),
            'expected_status':ref['expected_status'],'response_status_evaluated':False})
    both=sum(all(r['complete_evidence'] for r in rows if r['question_id']==qid) for qid in IDS)
    scope=sum(bool(r['unrequested_context_ids_present']) for r in rows);diagnostics=sum(bool(r['diagnostic_failures']) for r in rows)
    return {'rows':rows,'intents':12,'planned_formulations':24,'complete_both_languages':both,
        'complete_by_language':{lang:sum(r['complete_evidence'] for r in rows if r['language']==lang) for lang in ('en','fr')},
        'mean_reference_coverage':statistics.mean(r['reference_coverage'] for r in rows),
        'contexts_outside_acceptable_reference':sum(bool(r['outside_acceptable_ids']) for r in rows),
        'explicit_scope_failures':scope,'diagnostic_failure_formulations':diagnostics,
        'pilot_gate':'eligible_for_limited_end_to_end_consideration' if both==12 and scope==0 and diagnostics==0 else 'blocked_missing_evidence_scope_or_diagnostics',
        'answer_quality':'not_evaluated','automatic_adoption':False}


def make_runtime(root,candidate):
    from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
    from ingestion.polarity_passage_context import CompositionalContextIndex
    corpus=build_corpus(read(Path(root)/'experiments/cytiva/contaminants-pilot-v01/evidence.json'),candidate['source_runtime_policy'])
    index=CompositionalContextIndex(corpus,candidate['source_runtime_policy']['retrieval'],candidate['config'])
    require(not set(candidate['pending_source_ids']) & index.docs.keys(),'Excluded source indexed')
    counter,tokenizer=token_counter()
    return index,counter,tokenizer


def run(review_path,root=ROOT):
    root=Path(root).resolve();p=root/PACKAGE;verified=verify(root)
    queries=read(p/'questions.json')['questions'];refs=read(p/'references.json')['references']
    review_path=Path(review_path).resolve()
    review=review_gate(review_path,verified,{q['id']:q for q in queries},{r['question_id']:r for r in refs})
    lock=read(p/'method-lock.json');candidate=read(p/'candidate.json')
    require(platform.python_version()==lock['python_version'] and os.environ.get('PYTHONHASHSEED')=='0','Pinned Python/hash seed changed')
    require(importlib.metadata.version('tiktoken')==lock['tokenizer']['tiktoken_version'],'Pinned tokenizer changed')
    output=(root/candidate['run_directory']).resolve()
    require(output.is_relative_to((root/'data/experiments').resolve()),'Unexpected output location')
    if output.exists():raise ValueError('Existing evaluation output: preserve, no retry or overwrite')
    from experiments.cytiva.visual_validation import network_guard
    attempts=network_guard();output.mkdir(parents=True,exist_ok=False)
    review_hash=digest(review_path);contexts=[]
    dump(output/'reservation.json',{'status':'reserved_no_retry','at_utc':datetime.now(timezone.utc).isoformat(),
                                  'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],'review_sha256_lf':review_hash})
    try:
        (output/'human-review-snapshot.json').write_bytes(review_path.read_bytes())
        require(read(output/'human-review-snapshot.json')==review,'Review changed before snapshot')
        before=base.protected_files(root,output)
        manifest=read(p/'manifest.json')
        for n,h in manifest['file_sha256_lf'].items():
            require(digest(root/n)==h,'Frozen input changed before snapshot')
            target=output/'input-snapshot'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((root/n).read_bytes())
        target=output/'input-snapshot'/PACKAGE/'manifest.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((p/'manifest.json').read_bytes())
        start=time.perf_counter();index,counter,tokenizer=make_runtime(root,candidate)
        require(tokenizer==lock['tokenizer'],'Tokenizer identity changed')
        dump(output/'manifest-before-run.json',{'verification':verified,'candidate':candidate,'tokenizer':tokenizer,
            'initialization_ms':(time.perf_counter()-start)*1000,'protected_file_sha256_raw':before,
            'llm_calls':0,'api_calls':0,'automatic_adoption':False})
        for query in queries:
            for language in ('en','fr'):
                timings=[];first=None
                for _ in range(candidate['timing_repetitions']):
                    start=time.perf_counter();result=index.retrieve(query['question_'+language],counter)
                    timings.append((time.perf_counter()-start)*1000)
                    if first is None:first=canonical(result)
                    require(canonical(result)==first,'Repeated result changed; no best-repeat selection')
                base.validate_context(result,index.passages,counter,candidate['pending_source_ids'])
                contexts.append({'question_id':query['id'],'language':language,**result,'total_times_ms':timings})
                dump(output/'contexts-unscored.json',contexts)
        # References are used only after every unscored context has been saved.
        metrics=score(contexts,read(p/'references.json')['references'])
        metrics.update(mean_context_tokens=statistics.mean(r['assembled']['tokens'] for r in contexts),
            max_context_tokens=max(r['assembled']['tokens'] for r in contexts),
            excluded_bundles=sum(len(r['assembled']['excluded']) for r in contexts),
            unavailable_source_roles=sum(len(r['unavailable_source_roles']) for r in contexts),
            median_total_ms=statistics.median(t for r in contexts for t in r['total_times_ms']))
        require(not attempts,'Network attempted')
        for name,h in before.items():require((root/name).is_file() and hashlib.sha256((root/name).read_bytes()).hexdigest()==h,'Prior file changed: '+name)
        require(digest(review_path)==review_hash and digest(output/'human-review-snapshot.json')==review_hash,'Review changed during evaluation')
        verify(root)
        dump(output/'metrics.json',metrics)
        dump(output/'verification.json',{'status':'completed','evaluation_executed':True,'network_attempts':attempts,
            'pending_source_leakage':0,'earlier_files_unchanged':True,'automatic_adoption':False,
            'artifact_sha256_lf':{n:digest(output/n) for n in ('contexts-unscored.json','metrics.json')}})
        return metrics
    except Exception as exc:
        dump(output/'failure.json',{'status':'failed_preserve_no_retry','error':str(exc),'planned_formulations':24,
            'completed_formulations':len(contexts),'unexecuted_formulations':24-len(contexts),'pilot_gate':'blocked','network_attempts':attempts})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--review',type=Path)
    args=parser.parse_args()
    if args.run and args.review is None:parser.error('--run requires complete separate human review via --review')
    print(json.dumps(run(args.review) if args.run else verify(),ensure_ascii=False))
