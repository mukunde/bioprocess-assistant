"""Local v04 development measurement on already inspected V/C/H questions."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import statistics
import time

from experiments.cytiva.v03b_evaluation import ROOT,PACKAGE,digest,dump,read,review_gate,score,verify
from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
from experiments.cytiva.contaminant_retrieval import check_context
from experiments.cytiva.visual_validation import network_guard
from ingestion.compositional_passage_context import CompositionalContextIndex


def annotated_count(rows,refs,row_key,reference_key):
    """Missing scope annotation is not an observed zero-error result."""
    if not all(reference_key in ref for ref in refs):return None
    return sum(bool(row[row_key]) for row in rows)


def run(output):
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'data/experiments/cytiva/scoped-navigation-v04').resolve()):
        raise ValueError('Output must be inside the v04 development directory')
    if output.exists():raise ValueError('Existing development run: preserve, never overwrite')
    verified=verify();candidate=read(ROOT/PACKAGE/'candidate.json')
    queries=read(ROOT/PACKAGE/'questions.json')['questions']
    references=read(ROOT/PACKAGE/'references.json')['references']
    review_path=ROOT/'data/experiments/cytiva/v03b-evaluation-v01/human-review.json'
    review_gate(review_path,verified,{q['id']:q for q in queries},{r['question_id']:r for r in references})
    preservation=read(ROOT/'data/experiments/cytiva/scoped-navigation-v04/preserved-before.json')
    for name,h in preservation.items():
        if digest(ROOT/name)!=h:raise ValueError('Earlier artifact changed: '+name)
    preservation.update({p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'data/experiments').rglob('*') if p.is_file()})
    files=['ingestion/compositional_passage_context.py','experiments/cytiva/section_navigation_v04.json',
           'experiments/cytiva/compositional_navigation_retrieval.py','tests/test_compositional_passage_context.py']
    inputs={name:digest(ROOT/name) for name in files}
    output.mkdir(parents=True,exist_ok=False)
    dump(output/'reservation.json',{'at_utc':datetime.now(timezone.utc).isoformat(),
        'role':'development_after_inspecting_V_results_not_prospective',
        'inputs_sha256_lf':inputs,'v03b_manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],
        'review_sha256_lf':digest(review_path)})
    attempts=network_guard();contexts=[]
    try:
        config=read(ROOT/'experiments/cytiva/section_navigation_v04.json')
        corpus=build_corpus(read(ROOT/'experiments/cytiva/contaminants-pilot-v01/evidence.json'),candidate['source_runtime_policy'])
        index=CompositionalContextIndex(corpus,candidate['source_runtime_policy']['retrieval'],config)
        counter,tokenizer=token_counter()
        (output/'input-snapshot').mkdir()
        for name in files:
            target=output/'input-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        suites=[('V',queries,references),
            ('H',read(ROOT/'experiments/cytiva/section-evaluation-v01/questions.json')['questions'],
                 read(ROOT/'experiments/cytiva/section-evaluation-v01/references.json')['references'])]
        c=read(ROOT/'experiments/cytiva/contaminants-pilot-v01/questions.json')['questions']
        suites.append(('C',c,[dict(q,question_id=q['id']) for q in c]))
        # Retrieval receives query text only. References are applied after all
        # contexts have been saved; expected answers never enter the index.
        for suite,questions,refs in suites:
            for q in questions:
                for lang in ('en','fr'):
                    start=time.perf_counter()
                    result=index.retrieve(q['question_'+lang],counter)
                    result.update(question_id=q['id'],language=lang,suite=suite,
                                  total_time_ms=(time.perf_counter()-start)*1000)
                    check_context(index.passages,result['assembled'],counter,2048,{'E118-I','E121-EQ'})
                    contexts.append(result)
                    dump(output/'contexts-unscored.json',contexts)
        metrics={}
        for suite,questions,refs in suites:
            records=[x for x in contexts if x['suite']==suite]
            byid={r['question_id']:r for r in refs}
            rows=[]
            for x in records:
                ref=byid[x['question_id']];ids=set(x['assembled']['ids'])
                rows.append({'question_id':x['question_id'],'language':x['language'],
                    'complete_evidence':any(set(s)<=ids for s in ref['required_evidence_sets']),
                    'unrequested_ids':sorted(ids & set(ref.get('unrequested_context_ids',[]))),
                    'outside_acceptable_ids':sorted(ids-set(ref.get('acceptable_context_ids',ids)))})
            metrics[suite]={'intents':len(questions),'rows':rows,
                'complete_both_languages':sum(all(x['complete_evidence'] for x in rows if x['question_id']==q['id']) for q in questions),
                'formulations_with_unrequested_context':annotated_count(rows,refs,'unrequested_ids','unrequested_context_ids'),
                'formulations_outside_acceptable_context':annotated_count(rows,refs,'outside_acceptable_ids','acceptable_context_ids'),
                'mean_context_tokens':statistics.mean(x['assembled']['tokens'] for x in records),
                'max_context_tokens':max(x['assembled']['tokens'] for x in records)}
        vscore=score([x for x in contexts if x['suite']=='V'],references)
        dump(output/'metrics.json',{'dataset_role':'development_known_questions','suites':metrics,
            'v_reference_metrics':vscore,'automatic_adoption':False,'tokenizer':tokenizer,
            'answer_quality':'not_evaluated','median_warm_ms':statistics.median(x['total_time_ms'] for x in contexts)})
        for name,h in {**preservation,**inputs}.items():
            if digest(ROOT/name)!=h:raise ValueError('Input or earlier file changed: '+name)
        if attempts:raise ValueError('Network attempted')
        verify()
        dump(output/'verification.json',{'status':'completed','pending_source_leakage':0,
            'network_attempts':attempts,'earlier_artifacts_unchanged':True,
            'artifact_sha256_lf':{name:digest(output/name) for name in ('contexts-unscored.json','metrics.json')}})
        return {s:{k:v for k,v in m.items() if k!='rows'} for s,m in metrics.items()}
    except Exception as exc:
        dump(output/'failure.json',{'status':'failed_preserve_no_overwrite','error':str(exc),
             'completed_formulations':len(contexts),'network_attempts':attempts})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    import json
    print(json.dumps(run(args.output)))
