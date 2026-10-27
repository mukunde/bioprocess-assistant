"""One-pass paired S/F0 challenge. Default: static verification, never execution.

The method is locked before dataset authoring. Runtime receives only an arm's
input, never a reference, case ID, expected answer or source selection.
"""
import argparse
from copy import deepcopy
from decimal import Decimal
import importlib.metadata
import json
from pathlib import Path
import platform
import time
from uuid import uuid4

from experiments.cytiva.structured_evaluation import (
    ROOT, canonical, digest, dump, offline, read, require, score_case, semantic_result,
)

PACKAGE=Path('experiments/cytiva/free-text-v02-comparison-v01')
IDS=[f'FV{i:02d}' for i in range(1,13)]
DATA_FILES={'questions.json','submissions.json','references.json','review-template.json','REVIEW.md'}


def meaning(value):
    if isinstance(value,dict):
        if set(value)=={'value','unit'}:
            return {'value':str(Decimal(value['value']).normalize()),'unit':value['unit']}
        return {k:meaning(v) for k,v in value.items() if k!='reason'}
    return [meaning(x) for x in value] if isinstance(value,list) else value


def verify_method(root=ROOT, environment=False):
    root=Path(root);lock=read(root/PACKAGE/'method-lock.json')
    for name,h in lock['file_sha256_lf'].items():
        path=(root/name).resolve()
        require(path.is_relative_to(root.resolve()) and path.is_file() and digest(path)==h,'Frozen method changed: '+name)
    require(lock['excluded_source_ids']==['E118-I','E121-EQ'],'Quarantine policy changed')
    require(lock['root_limit']==6 and lock['context_token_limit']==2048,'Shared budgets changed')
    if environment:
        require(platform.python_version()==lock['environment']['python_version'],'Python version mismatch')
        for name,version in lock['environment']['dependencies'].items():
            require(importlib.metadata.version(name)==version,'Dependency mismatch: '+name)
        import hashlib
        asset=root/lock['environment']['tokenizer_asset_file']
        require(asset.is_file() and hashlib.sha256(asset.read_bytes()).hexdigest()==lock['environment']['tokenizer_asset_sha256'],'Offline tokenizer asset mismatch')
    return lock


def verify(root=ROOT):
    """Only hash, schema, provenance and topology checks. No runtime creation."""
    from jsonschema import Draft202012Validator
    root=Path(root);lock=verify_method(root);folder=root/PACKAGE
    manifest=read(folder/'manifest.json')
    require(manifest['method_lock_sha256_lf']==digest(folder/'method-lock.json'),'Lock binding mismatch')
    require(set(manifest['dataset_sha256_lf'])==DATA_FILES,'Dataset inventory changed')
    for name,h in manifest['dataset_sha256_lf'].items():require(digest(folder/name)==h,'Dataset file changed: '+name)
    questions=read(folder/'questions.json')['questions'];forms=read(folder/'submissions.json')['submissions'];refs=read(folder/'references.json')
    require([q['id'] for q in questions]==[s['id'] for s in forms]==[r['id'] for r in refs['references']]==IDS,'Paired case inventory mismatch')
    schema=read(root/'docs/technical/task-request-v01.schema.json');validator=Draft202012Validator(schema)
    registry=read(root/lock['source_registry_file']);sources={p['id']:p for p in registry['passages']}
    require(refs['source_pdf']==registry['source'],'PDF identity mismatch')
    adapter=read(root/'docs/technical/task-request-source-adapter-v01.json')
    eligible=set(adapter['basis']['eligible_source_ids'])
    dependencies=read(root/adapter['basis']['policy_file'])['source_runtime_policy']['requires']
    def closure(pid,trail=()):
        require(pid in eligible and pid not in trail,'Invalid reference dependency')
        result={pid}
        for dep in dependencies[pid]:result|=closure(dep,trail+(pid,))
        return result
    for p in refs['source_passages']:require(p['id'] in eligible and p==sources[p['id']],'Source quote/provenance mismatch')
    require(set(refs['eligible_source_ids'])==eligible,'Eligible sources changed')
    for q,s,r in zip(questions,forms,refs['references']):
        require(set(q)=={'id','family','question_en','question_fr','authorship_note'},'Gold mixed into question envelope')
        require(r['human_review_status']=='pending','Preparation cannot invent human approval')
        require(r['expected_answer_en'] and r['expected_answer_fr'] and r['reservations'],'Missing review material')
        for lang in ('en','fr'):
            form=s['input_'+lang];validator.validate(form);require(form['language']==lang,'Language mismatch')
            text=q['question_'+lang];require(bool(text.strip()),'Empty question')
            require([u['task_id'] for u in r['documentary']['units']]==[t['task_id'] for t in form['tasks'] for i in t['items'] for _ in i['information']],'Gold unit owner/order mismatch')
            require([(u['item_id'],u['information']) for u in r['documentary']['units']]==[(i['item_id'],v) for t in form['tasks'] for i in t['items'] for v in i['information']],'Gold selectors/order mismatch')
            for origin in r['intent_origins'][lang]:
                require(text[origin['start']:origin['end']]==origin['quote'] and 0<=origin['start']<origin['end']<=len(text),'Invalid gold code-point origin')
                require(origin['text_sha256_utf8']==__import__('hashlib').sha256(text.encode('utf-8')).hexdigest(),'Gold text digest mismatch')
            for field in r['field_origins'][lang]:
                from ingestion.free_text_contract import resolve
                resolve(form,field['pointer'])
                require(set(field['origin_ids'])<={o['origin_id'] for o in r['intent_origins'][lang]},'Gold origin reference missing')
                require(field['origin_ids'] or field.get('application_rule'),'Unjustified gold field')
        for u in r['documentary']['units']:
            supported=u['expected']['state']=='supported'
            require(bool(u['required_source_sets'])==supported and (u['binding'] is not None)==supported,'Invalid support reference')
            for bundle in u['required_source_sets']:
                require(set(bundle)<=set(r['documentary']['acceptable_context_ids']),'Context scope mismatch')
                require(all(closure(pid)<=set(bundle) for pid in bundle),'Mandatory dependency missing')
        require(set(r['review_source_ids'])<={p['id'] for p in refs['source_passages']},'Missing review quote')
    require(not manifest['evaluation_executed'] and manifest['dataset_status']=='pending_human_pair_review','Preparation status changed')
    return {'method':'frozen','cases':12,'languages':24,'planned_arm_executions':48,
            'review_status':'pending','evaluation_executed_by_verifier':False,
            'method_lock_sha256_lf':digest(folder/'method-lock.json')}


def review_gate(review, lock_hash, questions, forms, references):
    require(review.get('method_lock_sha256_lf')==lock_hash,'Review belongs to another candidate')
    rows=review.get('decisions',[])
    require(len(rows)==12 and {r.get('case_id') for r in rows}==set(IDS),'All twelve human pair reviews required')
    for row in rows:
        cid=row['case_id']
        require(row.get('decision') in ('validated','validated_with_reservations') and isinstance(row.get('human_quote'),str) and row['human_quote'].strip(),'Actual human approval required')
        require(row.get('question_sha256_canonical')==canonical(questions[cid]) and row.get('submission_sha256_canonical')==canonical(forms[cid]) and row.get('reference_sha256_canonical')==canonical(references[cid]),'Reviewed pair content changed')
        require(row.get('retained_reservations')==references[cid]['reservations'],'Review reservations changed')
        from datetime import datetime
        at=datetime.fromisoformat(row['reviewed_at_utc'].replace('Z','+00:00'))
        require(at.tzinfo is not None and at.utcoffset().total_seconds()==0,'UTC human review timestamp required')


def intent_score(outcome, form):
    ledger=outcome.get('interpretation_ledger');fail=[];task_map={};item_map={}
    if ledger is None:return {'passed':False,'failures':['missing_ledger']},task_map,item_map
    if not ledger['inventory_complete']:fail.append('incomplete_intent_inventory')
    if len(ledger['tasks'])!=len(form['tasks']):fail.append('task_inventory')
    for actual,expected in zip(ledger['tasks'],form['tasks']):
        task_map[actual['task_id']]=expected['task_id']
        for key in ('product','column','facts'):
            if meaning(actual[key])!=meaning(expected[key]):fail.append('task:'+key)
        units=[u for u in ledger['requested_units'] if u['owner']['state']=='resolved' and u['owner']['task_id']==actual['task_id']]
        wanted=[(i,v) for i in expected['items'] for v in i['information']]
        if len(units)!=len(wanted):fail.append('task_unit_inventory')
        for u,(item,info) in zip(units,wanted):
            if u['stage']!=item['stage'] or u['information']!=info:fail.append('stage_or_information')
            if u['item_id'] in item_map and item_map[u['item_id']]!=item['item_id']:fail.append('inconsistent_item_bijection')
            item_map[u['item_id']]=item['item_id']
    if len(set(task_map.values()))!=len(task_map) or len(set(item_map.values()))!=len(item_map):fail.append('nonbijective_ids')
    if len(ledger['requested_units'])!=sum(len(i['information']) for t in form['tasks'] for i in t['items']):fail.append('whole_request_denominator')
    try:
        mapped=[]
        for x in ledger['exclusions']:
            if not x['active']:continue
            for target in x['target_item_ids'] or [None]:
                scope={'task_id':task_map[x['task_id']]}
                if target is not None:scope['item_id']=item_map[target]
                mapped.append({'scope':scope,'selector':x['selector']})
        wanted=[{'scope':x['scope'],'selector':x['selector']} for t in form['tasks'] for x in t['exclusions']]
        if mapped!=wanted:fail.append('active_exclusion_scope_or_order')
        submission=outcome['projection']['submission']
        if submission is None:fail.append('missing_projection')
        else:
            # Compare all submitted semantics after the same ID bijection; ID
            # spelling and explanatory reason prose are the only ignored fields.
            clone=deepcopy(submission)
            for t in clone['tasks']:
                t['task_id']=task_map[t['task_id']]
                for item in t['items']:item['item_id']=item_map[item['item_id']]
                for x in t['exclusions']:
                    x['scope']['task_id']=task_map[x['scope']['task_id']]
                    if 'item_id' in x['scope']:x['scope']['item_id']=item_map[x['scope']['item_id']]
            gold=deepcopy(form)
            for doc in (clone,gold):
                for t in doc['tasks']:
                    for x in t['exclusions']:x.pop('exclusion_id')
            if meaning(clone)!=meaning(gold):fail.append('submitted_intent')
    except (KeyError,TypeError):fail.append('unrepresentable_or_preblocked_intent')
    return {'passed':not fail,'failures':list(dict.fromkeys(fail))},task_map,item_map


def renamed_core(core, task_map, item_map):
    clone=deepcopy(core)
    for row in clone['plan']['units']+clone['plan']['context']['bindings']:
        row['task_id']=task_map[row['task_id']];row['item_id']=item_map[row['item_id']]
    return clone


def score_saved(records, forms, references, sources, count_tokens):
    scores=[]
    for cid in IDS:
        for lang in ('en','fr'):
            srow=records[(cid,lang,'S')];frow=records[(cid,lang,'F0')]
            result={'case_id':cid,'language':lang,'S':{'passed':False,'failures':['execution_error']},'F0_intent':{'passed':False,'failures':['execution_error']},'F0_context':{'passed':False,'failures':['execution_error']},'paired_semantics_equal':False}
            ref=references[cid]['documentary']
            if srow.get('output') is not None:result['S']=score_case(srow['output'],ref,sources,count_tokens)
            if frow.get('output') is not None:
                output=frow['output'];intent,tm,im=intent_score(output,forms[cid]['input_'+lang]);result['F0_intent']=intent
                if output['core_result'] is not None and intent['passed']:
                    normalized=renamed_core(output['core_result'],tm,im)
                    # Token counts bind the actual original serialized context;
                    # renamed diagnostic copies are never retokenized or run.
                    check=score_case(normalized,ref,sources)
                    actual=output['core_result']['plan']
                    if count_tokens(json.dumps(actual['context'],ensure_ascii=False,separators=(',',':'),allow_nan=False))!=actual['context_tokens']:
                        check={'passed':False,'failures':check['failures']+['actual_F0_token_accounting']}
                    result['F0_context']=check
                    if srow.get('output') is not None:result['paired_semantics_equal']=semantic_result(normalized)==semantic_result(srow['output'])
            result['passed']=result['S']['passed'] and result['F0_intent']['passed'] and result['F0_context']['passed'] and result['paired_semantics_equal']
            scores.append(result)
    return {'observations':scores,'passed_observations':sum(r['passed'] for r in scores),'observation_denominator':24,
            'passed_bilingual_pairs':sum(all(r['passed'] for r in scores if r['case_id']==cid) for cid in IDS),
            'pair_denominator':12,'answer_quality_evaluated':False,'latency_claim':'descriptive only; no p95/p99 estimate'}


def make_runtimes(root):
    from ingestion.structured_request import StructuredControl
    from ingestion.free_text_bridge_v02 import FreeTextControlV02
    return StructuredControl(root),FreeTextControlV02(root)


def run(review_path,root=ROOT):
    root=Path(root);folder=root/PACKAGE
    verified=verify(root);lock=verify_method(root,environment=True)
    questions={q['id']:q for q in read(folder/'questions.json')['questions']}
    forms={s['id']:s for s in read(folder/'submissions.json')['submissions']}
    refs_packet=read(folder/'references.json');refs={r['id']:r for r in refs_packet['references']}
    review=read(review_path)
    review_gate(review,verified['method_lock_sha256_lf'],questions,forms,refs)
    output=root/lock['run_directory']
    require(not output.exists(),'Output exists; do not overwrite/retry')
    output.mkdir(parents=True)
    dump(output/'attempt.json',{'method_lock_sha256_lf':verified['method_lock_sha256_lf'],'review_sha256_canonical':canonical(review),'dataset_sha256_lf':read(folder/'manifest.json')['dataset_sha256_lf'],'status':'started'})
    saved={}
    with offline() as attempts:
        try:
            start=time.perf_counter();structured,free=make_runtimes(root);initialization_ms=(time.perf_counter()-start)*1000
            for index,cid in enumerate(IDS):
                for lang in ('en','fr'):
                    for arm in (('S','F0') if index%2==0 else ('F0','S')):
                        row={'case_id':cid,'language':lang,'arm':arm,'output':None,'error':None}
                        start=time.perf_counter()
                        try:
                            if arm=='S':row['output']=structured.evaluate(deepcopy(forms[cid]['input_'+lang]),request_id='pair-'+uuid4().hex)
                            else:row['output']=free.evaluate({'language':lang,'text':questions[cid]['question_'+lang]})
                        except Exception as exc:row['error']=type(exc).__name__
                        row['elapsed_ms']=(time.perf_counter()-start)*1000
                        dump(output/f'{cid}-{lang}-{arm}.json',row);saved[cid,lang,arm]=row
            require(not attempts,'Network attempt detected; preserve outputs and stop')
            # All 48 arm outputs are durable before any reference scoring.
            from ingestion.structured_sources import local_token_counter
            tokenizer=local_token_counter(root,structured.adapter.config['execution_policy']['tokenizer'])
            scores=score_saved(saved,forms,refs,{p['id']:p for p in refs_packet['source_passages']},tokenizer)
            dump(output/'scores.json',scores)
            dump(output/'completion.json',{'outputs':48,'initialization_ms':initialization_ms,'network_attempts':attempts,'status':'completed_no_retry'})
            return scores
        except Exception as exc:
            dump(output/'failure.json',{'type':type(exc).__name__,'outputs_saved':len(saved),'network_attempts':attempts,'retry_allowed':False})
            raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true');parser.add_argument('--review',type=Path)
    args=parser.parse_args(argv)
    if args.run:
        parser.error('--review with all twelve actual approvals is required') if args.review is None else None
        result=run(args.review)
    else:result=verify()
    print(json.dumps(result,ensure_ascii=False));return 0


if __name__=='__main__':raise SystemExit(main())
