"""Portable reviewed V01-V12 result checks; no retrieval, tokenizer or local runs."""
import json
from pathlib import Path
import statistics
from experiments.cytiva import v03b_evaluation as frozen
from experiments.cytiva import verify_section_evaluation_package as common

ROOT=frozen.ROOT
PACKAGE=Path('experiments/cytiva/reviewed-v03b-evaluation')
FILES={'README.md','review.json','results.json','provenance.json'}
SUPPORT={'docs/experiments/cytiva-v03b-prospective-results.md',
         'experiments/cytiva/verify_v03b_reviewed_package.py','tests/test_v03b_reviewed_package.py',
         'experiments/cytiva/v03b_evaluation.py','tests/test_v03b_evaluation.py',
         *('experiments/cytiva/v03b-evaluation-v01/'+n for n in
           ('method-lock.json','candidate.json','questions.json','references.json','PROTOCOL.md','manifest.json'))}


def corpus(root):
    candidate=frozen.read(Path(root)/frozen.PACKAGE/'candidate.json')
    source=frozen.read(Path(root)/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    from experiments.cytiva.cleaning_retrieval import build_corpus
    return {p['id']:p for p in build_corpus(source,candidate['source_runtime_policy'])}


def check_results(results,sources,refs):
    contexts=results['contexts'];metrics=results['metrics']
    for row in contexts:common.check_context(row,sources)
    for k,v in frozen.score(contexts,refs).items():common.require(metrics[k]==v,'Frozen metric changed: '+k)
    expected={'mean_context_tokens':statistics.mean(r['assembled']['tokens'] for r in contexts),
        'max_context_tokens':max(r['assembled']['tokens'] for r in contexts),
        'excluded_bundles':sum(len(r['assembled']['excluded']) for r in contexts),
        'unavailable_source_roles':sum(len(r['unavailable_source_roles']) for r in contexts),
        'median_total_ms':statistics.median(t for r in contexts for t in r['total_times_ms'])}
    for k,v in expected.items():common.require(metrics[k]==v,'Recorded operational metric changed: '+k)
    common.require(all(len(r['total_times_ms'])==3 and all(t>=0 for t in r['total_times_ms']) for r in contexts),'Timing grid changed')
    strict=sum(all(r['complete_evidence'] and not r['unrequested_context_ids_present'] for r in metrics['rows'] if r['question_id']==qid) for qid in frozen.IDS)
    common.require(strict==3,'Strict frozen result changed')
    common.require(metrics['complete_both_languages']==6 and metrics['explicit_scope_failures']==6,'Frozen outcome changed')


def verify(root=ROOT,package=None):
    root=Path(root);package=Path(package) if package is not None else root/PACKAGE
    manifest=common.check_files(root,package,FILES,SUPPORT)
    common.require(manifest['status']=='completed_review_and_blocked_frozen_run' and not manifest['publication_allowed'],'Export scope changed')
    verified=frozen.verify(root)
    questions=frozen.read(root/frozen.PACKAGE/'questions.json')['questions']
    refs=frozen.read(root/frozen.PACKAGE/'references.json')['references']
    frozen.review_gate(package/'review.json',verified,{q['id']:q for q in questions},{r['question_id']:r for r in refs})
    review=frozen.read(package/'review.json');results=frozen.read(package/'results.json');p=frozen.read(package/'provenance.json')
    check_results(results,corpus(root),refs)
    for name,value in [('human-review-snapshot.json',review),('contexts-unscored.json',results['contexts']),('metrics.json',results['metrics'])]:
        common.require(common.native_hash(value)==p['original_artifact_sha256_lf'][name],'Native selected artifact changed: '+name)
    common.require(p['original_artifact_sha256_lf']['human-review-snapshot.json']==p['reservation']['review_sha256_lf'],'Run review binding changed')
    common.require(p['reservation']['manifest_sha256_lf']==verified['preparation_manifest_sha256_lf'],'Reservation freeze changed')
    v=p['verification']
    common.require(v['status']=='completed' and v['network_attempts']==[] and v['pending_source_leakage']==0 and v['earlier_files_unchanged'],'Run safety changed')
    for name in ('contexts-unscored.json','metrics.json'):
        common.require(v['artifact_sha256_lf'][name]==p['original_artifact_sha256_lf'][name],'Run verification hash changed')
    common.require(p['preservation_attestation']['checked_files']==1379 and p['preservation_attestation']['unchanged'],'Preservation attestation changed')
    return {'status':'verified','human_decisions':12,'contexts':24,'complete_both_languages':6,
        'strict_complete_and_scoped_intents':3,'source_exclusions':['E118-I','E121-EQ'],
        'tokens':'recorded_bounds_not_retokenized','retrieval_executed':False}


if __name__=='__main__':print(json.dumps(verify()))
