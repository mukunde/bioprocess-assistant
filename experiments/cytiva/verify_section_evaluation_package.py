"""Portable selected H review/result verification; standard library, no retrieval."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import statistics
from experiments.cytiva import section_evaluation as frozen

ROOT=frozen.ROOT
PACKAGE=Path('experiments/cytiva/reviewed-section-evaluation')
FILES={'README.md','review.json','events.json','results.json','provenance.json'}
SUPPORT={
    'docs/experiments/cytiva-section-evaluation-results.md',
    'experiments/cytiva/section_evaluation.py','tests/test_section_evaluation.py',
    'experiments/cytiva/verify_section_evaluation_package.py','tests/test_section_evaluation_package.py',
    *('experiments/cytiva/section-evaluation-v01/'+n for n in
      ('PROTOCOL.md','candidate.json','questions.json','references.json','manifest.json'))}


def require(ok,message):
    if not ok:raise ValueError(message)


def canonical(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def native_hash(value):
    return hashlib.sha256((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()


def check_files(root,package,files,support):
    root,package=Path(root),Path(package)
    m=frozen.read(package/'manifest.json')
    require(set(m['files'])==set(files) and set(m['supporting_files'])==set(support),'Export file inventory changed')
    for name,h in m['files'].items():
        path=package/name
        require(path.resolve().is_relative_to(package.resolve()) and frozen.digest(path)==h,'Export file digest mismatch: '+name)
    for name,h in m['supporting_files'].items():
        path=root/name
        require(path.resolve().is_relative_to(root.resolve()) and frozen.digest(path)==h,'Supporting file digest mismatch: '+name)
    return m


def source_corpus(root):
    candidate=frozen.read(Path(root)/frozen.PACKAGE/'candidate.json')
    policy=candidate['source_runtime_policy']
    evidence=frozen.read(Path(root)/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    fields=('id','pdf_page_1based','pdf_page_index_0based','scope','quote','quote_sha256','page_text_start','page_text_end')
    corpus={p['id']:{**{k:p[k] for k in fields},'requires':policy['requires'][p['id']],
        'quarantined':p['id'] in policy['quarantined_ids'],'searchable':p['id'] in policy['searchable_ids']} for p in evidence['passages']}
    return corpus,candidate


def closure(corpus,pid,active=()):
    require(pid in corpus and pid not in active,'Missing/cyclic source link')
    ids=[]
    for parent in corpus[pid]['requires']:
        for item in closure(corpus,parent,(*active,pid)):
            if item not in ids:ids.append(item)
    return ids+[pid]


def check_context(result,corpus,max_tokens=2048):
    a=result['assembled'];ids=a['ids']
    require(len(ids)==len(set(ids)) and set(ids)<=corpus.keys(),'Duplicate/unknown context source')
    require(not any(corpus[pid]['quarantined'] for pid in ids),'Excluded source leaked')
    fields=('id','pdf_page_1based','pdf_page_index_0based','scope','quote','quote_sha256','page_text_start','page_text_end')
    expected=json.dumps({'source_passages':[{k:corpus[pid][k] for k in fields} for pid in ids]},ensure_ascii=False,separators=(',',':'))
    require(a['context']==expected,'Exact context quote/provenance changed')
    require(a['context_sha256']==hashlib.sha256(expected.encode()).hexdigest(),'Context string hash changed')
    require(type(a['tokens']) is int and 0<=a['tokens']<=max_tokens,'Recorded token bound invalid')
    for seed in a['accepted_seeds']:
        require(set(closure(corpus,seed))<=set(ids),'Atomic dependency lost')
    for pid in ids:
        require(hashlib.sha256(corpus[pid]['quote'].encode()).hexdigest()==corpus[pid]['quote_sha256'],'Source quote hash changed')


def check_review(review,events,questions,references,manifest_digest):
    require(review['manifest_sha256_lf']==manifest_digest,'Wrong frozen reference version')
    require(review['pending_question_ids']==[] and review['status']=='completed_with_reservations','Incomplete current review')
    require(len(events)==10 and len(review['decisions'])==10,'Wrong human decision count')
    previous=None
    for i,event in enumerate(events,1):
        require(event['sequence']==i and event['previous_event_sha256']==previous,'Broken event order/link')
        require(event['manifest_sha256_lf']==manifest_digest,'Event references wrong package')
        require(event['event_sha256_canonical']==canonical({k:v for k,v in event.items() if k!='event_sha256_canonical'}),'Event content changed')
        previous=event['event_sha256_canonical']
        d=event['decision'];qid=d['question_id']
        require(qid==f'H{i:02d}' and d==review['decisions'][i-1],'Review/event disagreement')
        require(d['question_sha256_canonical']==canonical(questions[qid]) and d['reference_sha256_canonical']==canonical(references[qid]),'Question/reference binding changed')
        require(d['retained_reservations']==references[qid]['reservations'],'Human reservations changed')
        require(d['decision']=='validated_with_reservation' and bool(d['human_quote']),'Human decision changed')
    require(previous==review['last_event_sha256_canonical'],'Wrong final event link')


def check_h_results(results,corpus,refs):
    contexts=results['contexts'];metrics=results['metrics']
    for row in contexts:check_context(row,corpus)
    recalculated=frozen.score(contexts,refs)
    for key,value in recalculated.items():
        if key!='rows':require(metrics[key]==value,'Metric changed: '+key)
    for expected,recorded in zip(recalculated['rows'],metrics['rows']):
        require(all(recorded[k]==v for k,v in expected.items()),'Per-question score changed')
    summary=results['summary']
    require(summary['complete_both_languages']==8 and summary['complete_by_language']=={'en':9,'fr':8},'Frozen outcome changed')
    require(summary['max_context_tokens']==max(r['assembled']['tokens'] for r in contexts),'Token maximum changed')
    require(summary['mean_context_tokens']==statistics.mean(r['assembled']['tokens'] for r in contexts),'Token mean changed')
    require(summary['mean_required_source_coverage']==statistics.mean(r['required_source_coverage'] for r in metrics['rows']),'Coverage mean changed')
    require(summary['contexts_with_nonreference_ids']==sum(bool(r['outside_acceptable_context_ids']) for r in metrics['rows']),'Noise proxy changed')
    diagnostics=results['diagnostics']['rows']
    require(len(diagnostics)==len(contexts),'Missing ranking diagnostics')
    for context,diagnostic,scored in zip(contexts,diagnostics,metrics['rows']):
        require((context['question_id'],context['language'])==(diagnostic['question_id'],diagnostic['language']),'Diagnostic identity changed')
        require(diagnostic['full_ranking'][:6]==context['hits'],'Ranking prefix changed')
        require({r['missing_source'] for r in diagnostic['missing_source_diagnostics']}==set(scored['missing_ids']),'Missing-source diagnosis changed')
    require(metrics['pilot_gate']=='blocked_incomplete_evidence' and metrics['answer_quality']=='not_evaluated','Frozen acceptance limit changed')


def verify(root=ROOT,package=None):
    root=Path(root);package=Path(package) if package is not None else root/PACKAGE
    m=check_files(root,package,FILES,SUPPORT)
    frozen_check=frozen.verify(root)
    refs=frozen.read(root/frozen.PACKAGE/'references.json')['references']
    questions=frozen.read(root/frozen.PACKAGE/'questions.json')['questions']
    review=frozen.read(package/'review.json');events=frozen.read(package/'events.json')
    check_review(review,events,{q['id']:q for q in questions},{r['question_id']:r for r in refs},frozen_check['manifest_sha256_lf'])
    results=frozen.read(package/'results.json');provenance=frozen.read(package/'provenance.json')
    corpus,candidate=source_corpus(root)
    check_h_results(results,corpus,refs)
    for name,value in [('review',review),('contexts',results['contexts']),('metrics',results['metrics']),('diagnostics',results['diagnostics']),('summary',results['summary'])]:
        require(native_hash(value)==provenance['original_artifacts'][name]['sha256_lf'],'Native selected artifact changed: '+name)
    native_events=''.join(json.dumps(e,ensure_ascii=False,separators=(',',':'))+'\n' for e in events)
    require(hashlib.sha256(native_events.encode()).hexdigest()==provenance['original_artifacts']['events_jsonl']['sha256_lf'],'Native event lines changed')
    require(provenance['review_at_run']==review,'Run used another human review')
    require(provenance['frozen_manifest_sha256_lf']==frozen_check['manifest_sha256_lf'],'Frozen manifest lineage changed')
    require(provenance['verification']['network_attempts']==[] and provenance['verification']['pending_source_leakage']==0,'Recorded safety failure')
    require(m['status']=='completed_review_and_run_gate_blocked' and not m['publication_allowed'],'Export scope changed')
    return {'status':'verified','human_decisions':10,'intents':10,'formulations':20,'bilingual_complete':8,'pending_sources_excluded':candidate['pending_source_ids'],'token_counts':'recorded_bounds_not_retokenized','benchmark_executed_by_verifier':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    print(json.dumps(verify(),ensure_ascii=False))
