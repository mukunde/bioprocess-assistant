"""Frozen section-only challenge: integrity by default; human review gates measurement."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('experiments/cytiva/section-evaluation-v01')
IDS = [f'H{i:02d}' for i in range(1, 11)]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def verify(root=ROOT):
    root=Path(root)
    package=root/PACKAGE
    manifest=read(package/'manifest.json')
    for name, expected in manifest['file_sha256_lf'].items():
        path=root/name
        if not path.resolve().is_relative_to(root.resolve()) or not path.is_file() or digest(path)!=expected:
            raise ValueError('Frozen file missing or changed: '+name)
    candidate=read(package/'candidate.json')
    if (candidate['config']['top_k'],candidate['config']['max_tokens'],candidate['origin_retrieve_arguments']) != (6,2048,{'sections':True,'vocabulary':None}):
        raise ValueError('Wrong frozen section-only variant')
    pending=set(candidate['pending_source_ids'])
    if pending!={'E118-I','E121-EQ'}:
        raise ValueError('Pending source policy changed')
    questions=read(package/'questions.json')['questions']
    refs=read(package/'references.json')
    if [q['id'] for q in questions]!=IDS or [r['question_id'] for r in refs['references']]!=IDS:
        raise ValueError('Question/reference inventory changed')
    evidence=read(root/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    lookup={p['id']:p for p in evidence['passages']}
    for q in questions:
        if set(q)!={'id','family','question_en','question_fr'} or not all(q['question_'+lang].strip() for lang in ('en','fr')):
            raise ValueError('Runtime queries must not include references')
    for r in refs['references']:
        required=set().union(*map(set,r['required_evidence_sets']))
        acceptable=set(r['acceptable_context_ids'])
        if not required or not required<=acceptable<=lookup.keys() or acceptable & pending:
            raise ValueError('Invalid/pending source in reference')
        if r['human_review_status']!='pending':
            raise ValueError('Preparation must not invent human approval')
    expected_sources=set(p for r in refs['references'] for p in r['acceptable_context_ids'])
    if len(refs['source_passages'])!=len(expected_sources) or {p['id'] for p in refs['source_passages']}!=expected_sources:
        raise ValueError('Incomplete source review packet')
    for p in refs['source_passages']:
        if p!=lookup[p['id']] or hashlib.sha256(p['quote'].encode()).hexdigest()!=p['quote_sha256']:
            raise ValueError('Copied source provenance changed')
    from experiments.cytiva.verify_contaminant_questions_package import verify as source_verify
    source_verify(root=root,package=root/'experiments/cytiva/reviewed-contaminant-questions')
    return {'integrity':'verified','intents':len(questions),'formulations':2*len(questions),
        'reference_review':'pending_separate_decisions_required','benchmark_executed':False,
        'manifest_sha256_lf':digest(package/'manifest.json')}


def review_gate(path, manifest_digest):
    review=read(path)
    if review.get('manifest_sha256_lf')!=manifest_digest:
        raise ValueError('Human review not bound to this frozen package')
    rows=review.get('decisions',[])
    if len(rows)!=len(IDS) or {r.get('question_id') for r in rows}!=set(IDS):
        raise ValueError('All ten new questions need separate human decisions')
    for row in rows:
        if row.get('decision') not in ('validated','validated_with_reservation') or not row.get('human_quote','').strip():
            raise ValueError('Pending/rejected or undocumented human decision')
        date=datetime.fromisoformat(row.get('reviewed_at_utc','').replace('Z','+00:00'))
        if date.tzinfo is None or date.utcoffset().total_seconds()!=0:
            raise ValueError('Human decision needs a UTC timestamp')
    return review


def score(contexts, references):
    keys=[(r['question_id'],r['language']) for r in contexts]
    if len(keys)!=len(set(keys)) or set(keys)!={(qid,lang) for qid in IDS for lang in ('en','fr')}:
        raise ValueError('Incomplete or duplicate result grid')
    refs={r['question_id']:r for r in references}
    rows=[]
    for result in contexts:
        ref=refs[result['question_id']]
        present=set(result['assembled']['ids'])
        sets=list(map(set,ref['required_evidence_sets']))
        best=max(sets,key=lambda required:len(present & required)/len(required))
        rows.append({'question_id':result['question_id'],'language':result['language'],
            'complete_evidence':any(required<=present for required in sets),
            'required_source_coverage':len(present & best)/len(best),'missing_ids':sorted(best-present),
            'outside_acceptable_context_ids':sorted(present-set(ref['acceptable_context_ids'])),
            'expected_status':ref['expected_status'],'response_status_evaluated':False})
    both=sum(all(r['complete_evidence'] for r in rows if r['question_id']==qid) for qid in IDS)
    return {'rows':rows,'complete_both_languages':both,'intents':len(IDS),
        'complete_by_language':{lang:sum(r['complete_evidence'] for r in rows if r['language']==lang) for lang in ('en','fr')},
        'pilot_gate':'eligible_for_end_to_end_consideration' if both==len(IDS) else 'blocked_incomplete_evidence',
        'answer_quality':'not_evaluated','automatic_adoption':False}


def run(review_path, root=ROOT):
    root=Path(root)
    verified=verify(root)
    review=review_gate(review_path,verified['manifest_sha256_lf'])
    candidate=read(root/PACKAGE/'candidate.json')
    if platform.python_version()!=candidate['python_version'] or importlib.metadata.version('tiktoken')!=candidate['tokenizer']['tiktoken_version'] or os.environ.get('PYTHONHASHSEED')!='0':
        raise ValueError('Pinned Python/tokenizer/hash-seed environment changed')
    from experiments.cytiva import contaminant_context_retrieval as method
    output=root/candidate['run_directory']
    output.mkdir(parents=True,exist_ok=False)
    dump(output/'reservation.json',{'status':'reserved_no_retry','manifest_sha256_lf':verified['manifest_sha256_lf'],
        'review_sha256_lf':digest(review_path),'reserved_at_utc':datetime.now(timezone.utc).isoformat()})
    contexts=[]
    review_hash=digest(review_path)
    attempts=method.network_guard()
    try:
        (output/'review-snapshot.json').write_bytes(Path(review_path).read_bytes())
        if read(output/'review-snapshot.json')!=review:
            raise ValueError('Human review changed before measurement')
        start=time.perf_counter()
        before=method.base.protected_files()
        policy=candidate['source_runtime_policy']
        corpus=method.build_corpus(read(root/'experiments/cytiva/contaminants-pilot-v01/evidence.json'),policy)
        index=method.VocabularyIndex(corpus,policy['retrieval'],None)
        if set(candidate['pending_source_ids']) & index.docs.keys():
            raise ValueError('Pending source indexed')
        counter,tokenizer=method.token_counter()
        if tokenizer!=candidate['tokenizer']:
            raise ValueError('Tokenizer identity changed')
        initialization_ms=(time.perf_counter()-start)*1000
        dump(output/'manifest-before-run.json',{'candidate':candidate,'verification':verified,'human_review':review,
            'initialization_ms':initialization_ms,'benchmark_executed':False})
        for query in read(root/PACKAGE/'questions.json')['questions']:
            for language in ('en','fr'):
                result=method.retrieve(index,query['question_'+language],counter,candidate['config'],True)
                method.base.check_context(index.passages,result['assembled'],counter,2048,candidate['pending_source_ids'])
                contexts.append({'question_id':query['id'],'language':language,**result})
                dump(output/'contexts-unscored.json',contexts)
        # Persist every context before scoring. References never reach the runtime.
        refs=read(root/PACKAGE/'references.json')['references']
        metrics=score(contexts,refs)
        for result,scored in zip(contexts,metrics['rows']):
            noise=set(scored['outside_acceptable_context_ids'])
            # Diagnostic subset includes its JSON wrapper; not marginal token cost.
            scored['outside_acceptable_subset_tokens']=counter(method.base.serialize(index.passages,[pid for pid in result['assembled']['ids'] if pid in noise])) if noise else 0
        if attempts:raise ValueError('Network attempted')
        after=method.base.protected_files()
        if any(after.get(f)!=h for f,h in before.items()):
            raise ValueError('Earlier file changed during run')
        verify(root)
        if digest(review_path)!=review_hash or digest(output/'review-snapshot.json')!=review_hash:
            raise ValueError('Human review changed during measurement')
        dump(output/'metrics.json',metrics)
        dump(output/'verification.json',{'status':'completed','benchmark_executed':True,'network_attempts':attempts,
            'earlier_files_unchanged':True,'pending_source_leakage':0,'automatic_adoption':False})
        return metrics
    except Exception as exc:
        dump(output/'failure.json',{'status':'failed_no_retry','error':str(exc),'completed_formulations':len(contexts),
            'unexecuted_formulations':20-len(contexts),'network_attempts':attempts,'pilot_gate':'blocked'})
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--review',type=Path)
    args=parser.parse_args()
    if args.run and args.review is None:parser.error('--run requires separate --review; no approvals inferred')
    print(json.dumps(run(args.review) if args.run else verify(),ensure_ascii=False))
