"""Portable selected v05 A-B development checks; no retrieval or tokenizer."""
import json
from pathlib import Path
import statistics
from experiments.cytiva import verify_v04_reviewed_package as a
from experiments.cytiva import v03b_evaluation as frozen
from experiments.cytiva.verify_section_evaluation_package import require,native_hash,check_files,check_context

ROOT=frozen.ROOT
PACKAGE=Path('experiments/cytiva/polarity-navigation-v05-results')
FILES={'README.md','results.json','provenance.json'}
SUPPORT={'docs/experiments/cytiva-polarity-context-results.md',
    'ingestion/polarity_passage_context.py','experiments/cytiva/section_navigation_v05.json',
    'experiments/cytiva/polarity_navigation_retrieval.py','tests/test_polarity_passage_context.py',
    'experiments/cytiva/verify_polarity_navigation_package.py','tests/test_polarity_navigation_package.py'}


def check_run(record,provenance,sources,suites,root):
    contexts=record['contexts'];metrics=record['metrics']
    expected={(suite,q['id'],lang) for suite,(qs,refs) in suites.items() for q in qs for lang in ('en','fr')}
    keys=[(r['suite'],r['question_id'],r['language']) for r in contexts]
    require(len(keys)==len(set(keys)) and set(keys)==expected,'Development grid changed')
    for row in contexts:check_context(row,sources)
    for artifact,value in [('contexts-unscored.json',contexts),('metrics.json',metrics)]:
        require(native_hash(value)==provenance['verification']['artifact_sha256_lf'][artifact],'Native development artifact changed')
    v=provenance['verification']
    require(v['status']=='completed' and not v['network_attempts'] and v['pending_source_leakage']==0 and v['earlier_artifacts_unchanged'],'Development safety changed')
    require(metrics['dataset_role']=='development_known_questions' and not metrics['automatic_adoption'] and metrics['answer_quality']=='not_evaluated','Development scope changed')
    require(set(provenance['archived_input_overrides'])<=set(provenance['reservation']['inputs_sha256_lf']),'Unknown historical input override')
    for name,h in provenance['reservation']['inputs_sha256_lf'].items():
        override=provenance['archived_input_overrides'].get(name)
        value=override.encode() if override is not None else (root/name).read_bytes()
        import hashlib
        require(hashlib.sha256(value.replace(b'\r\n',b'\n')).hexdigest()==h,'Archived development input changed: '+name)
    for suite,(qs,refs) in suites.items():
        records=[r for r in contexts if r['suite']==suite];refmap={r['question_id']:r for r in refs};rows=[]
        for r in records:
            ref=refmap[r['question_id']];ids=set(r['assembled']['ids'])
            rows.append({'question_id':r['question_id'],'language':r['language'],
                'complete_evidence':any(set(s)<=ids for s in ref['required_evidence_sets']),
                'unrequested_ids':sorted(ids & set(ref.get('unrequested_context_ids',[]))),
                'outside_acceptable_ids':sorted(ids-set(ref.get('acceptable_context_ids',ids)))})
        m=metrics['suites'][suite];require(m['rows']==rows,'Per-query development metric changed')
        require(m['intents']==len(qs) and m['complete_both_languages']==sum(all(r['complete_evidence'] for r in rows if r['question_id']==q['id']) for q in qs),'Development completeness changed')
        for key,rowkey,refkey in [('formulations_with_unrequested_context','unrequested_ids','unrequested_context_ids'),('formulations_outside_acceptable_context','outside_acceptable_ids','acceptable_context_ids')]:
            count=sum(bool(r[rowkey]) for r in rows)
            # Missing reference annotations remain unavailable, not zero errors.
            if not all(refkey in r for r in refs):count=None
            require(m[key]==count,'Annotated development scope changed')
        require(m['mean_context_tokens']==statistics.mean(r['assembled']['tokens'] for r in records) and m['max_context_tokens']==max(r['assembled']['tokens'] for r in records),'Development token summary changed')
    require(metrics['v_reference_metrics']==frozen.score([r for r in contexts if r['suite']=='V'],suites['V'][1]),'V development score changed')
    require(metrics['w_reference_metrics']==a.frozen.score([r for r in contexts if r['suite']=='W'],suites['W'][1]),'W development score changed')
    require(metrics['median_warm_ms']==statistics.median(r['total_time_ms'] for r in contexts),'Development timing summary changed')


def verify(root=ROOT,package=None):
    root=Path(root);package=Path(package) if package is not None else root/PACKAGE
    manifest=check_files(root,package,FILES,SUPPORT);a.verify(root)
    require(manifest['status']=='development_not_independent' and not manifest['publication_allowed'],'Export scope changed')
    p=frozen.read(package/'provenance.json');results=frozen.read(package/'results.json')
    require(p['v04_export_manifest_sha256_lf']==frozen.digest(root/a.PACKAGE/'manifest.json'),'Wrong lot A dependency')
    require(manifest['v04_export_manifest_sha256_lf']==p['v04_export_manifest_sha256_lf'],'Manifest lot A binding changed')
    qs=frozen.read(root/frozen.PACKAGE/'questions.json')['questions'];refs=frozen.read(root/frozen.PACKAGE/'references.json')['references']
    h=root/'experiments/cytiva/section-evaluation-v01'
    cq=frozen.read(root/'experiments/cytiva/contaminants-pilot-v01/questions.json')['questions']
    w=root/a.frozen.PACKAGE
    suites={'W':(frozen.read(w/'questions.json')['questions'],frozen.read(w/'references.json')['references']),'V':(qs,refs),'H':(frozen.read(h/'questions.json')['questions'],frozen.read(h/'references.json')['references']),
            'C':(cq,[dict(q,question_id=q['id']) for q in cq])}
    require(set(results)==set(p['runs'])=={'attempt-a','attempt-b'},'Development trial inventory changed')
    sources=a.corpus(root)
    for name,record in results.items():
        prov=p['runs'][name]
        require(prov['reservation']['v03b_manifest_sha256_lf']==frozen.digest(root/frozen.PACKAGE/'manifest.json'),'Development freeze binding changed')
        require(prov['reservation']['review_sha256_lf']==frozen.digest(root/'experiments/cytiva/reviewed-v03b-evaluation/review.json'),'Development review binding changed')
        check_run(record,prov,sources,suites,root)
    final=results['attempt-b']['metrics']['suites']
    require([final[k]['complete_both_languages'] for k in ('W','V','H','C')]==[12,12,10,10],'Final development result changed')
    require(results['attempt-a']['metrics']['suites']['C']['complete_both_languages']==9,'Intermediate C02 regression lost')
    return {'status':'verified','development_runs':2,'contexts':176,'final_W':12,'final_V':12,'final_H':10,'final_C':10,
        'independent_evaluation':False,'retrieval_executed':False,'tokens':'recorded_bounds_not_retokenized'}


if __name__=='__main__':print(json.dumps(verify()))
