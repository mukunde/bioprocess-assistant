"""Verify selected development A/B evidence using lot A; no retrieval/tokenizer."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.cytiva import verify_section_evaluation_package as h
from experiments.cytiva import section_navigation_retrieval as runtime

ROOT=h.ROOT
PACKAGE=Path('experiments/cytiva/section-navigation-v03-results')
FILES={'README.md','results.json','provenance.json'}
SUPPORT={'ingestion/scoped_passage_context.py','experiments/cytiva/section_navigation_v03.json',
    'experiments/cytiva/section_navigation_retrieval.py','tests/test_scoped_passage_context.py',
    'tests/test_section_navigation_runner.py','docs/experiments/cytiva-scoped-context-results.md',
    'experiments/cytiva/verify_section_navigation_package.py','tests/test_section_navigation_package.py'}


def no_tokenizer(text):
    raise ValueError('Offline selected verification must not require tokenization')


def check_input_versions(root,record):
    root=Path(root);m=record['run_manifest_without_private_inventory']
    overrides=record['archived_code_overrides']
    h.require(set(overrides)<=set(m['code_and_input_sha256_lf']),'Unknown archived code override')
    for name,expected in m['code_and_input_sha256_lf'].items():
        path=root/name
        h.require(path.resolve().is_relative_to(root.resolve()),'Unsafe code reference')
        data=overrides[name].encode() if name in overrides else path.read_bytes()
        actual=hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()
        h.require(actual==expected,'Archived input changed: '+name)
    h.require(m['network_attempts']==[] and m['pending_source_leakage']==0 and m['protected_files_unchanged'],'Recorded run safety failure')
    h.require(record['preservation_attestation']['checked_files']>0 and record['preservation_attestation']['unchanged'],'Invalid preservation attestation')


def check_run(name,selected,record,corpus,refs):
    rows=selected['rows'];metrics=selected['metrics'];keys=record['native_unscored_key_order']
    runtime.validate_grid(rows,[f'H{i:02d}' for i in range(1,11)]+[f'C{i:02d}' for i in range(1,11)])
    for row in rows:h.check_context(row,corpus)
    native=record['native_artifact_sha256_lf']
    h.require(h.native_hash(rows)==native['results.json'],'Native scored rows changed')
    h.require(h.native_hash(metrics)==native['metrics.json'],'Native metrics changed')
    contexts=[{key:row[key] for key in keys} for row in rows]
    h.require(h.native_hash(contexts)==native['contexts-unscored.json'],'Native unscored contexts changed')
    rescored=runtime.score_rows(contexts,refs,corpus,no_tokenizer)
    for expected,recorded in zip(rescored,rows):
        for key in ('complete_evidence','reference_coverage','missing_ids','expected_status','response_status_evaluated'):
            h.require(expected[key]==recorded[key],'Development reference score changed')
        if 'outside_acceptable_ids' in expected:
            h.require(recorded['outside_acceptable_ids']==expected['outside_acceptable_ids'],'H context noise proxy changed')
            h.require(recorded['outside_acceptable_subset_tokens']==0,'Unexpected H tokenization requirement')
    hrows=[r for r in rows if r['question_id'].startswith('H')];crows=[r for r in rows if r['question_id'].startswith('C')]
    h.require(runtime.summary(hrows)==metrics['H_new'] and runtime.summary(crows)==metrics['C_new'],'Development summary changed')
    h.require(metrics['H_new']['complete_both_languages']==10 and metrics['C_new']['complete_both_languages']==10,'Development outcome changed')
    for row in rows:
        if row['question_id']=='H10':
            h.require(any(x.get('role')=='equilibration' for x in row['unavailable_source_roles']),'Source-review boundary not reported')
            if name=='development-b':
                h.require(not {'E121-L','E121-W','E121-E','E121-EQ'} & set(row['assembled']['ids']),'Other phase leaked into revision B H10')


def verify(root=ROOT,package=None):
    root=Path(root);package=Path(package) if package is not None else root/PACKAGE
    m=h.check_files(root,package,FILES,SUPPORT)
    h.verify(root)
    results=h.frozen.read(package/'results.json');p=h.frozen.read(package/'provenance.json')
    h.require(p['dependency_H_export_manifest_sha256_lf']==h.frozen.digest(root/h.PACKAGE/'manifest.json'),'Wrong lot A dependency')
    hrefs=h.frozen.read(root/h.frozen.PACKAGE/'references.json')['references']
    cqueries=h.frozen.read(root/'experiments/cytiva/contaminants-pilot-v01/questions.json')['questions']
    refs={r['question_id']:r for r in hrefs};refs.update({q['id']:q for q in cqueries})
    corpus,candidate=h.source_corpus(root)
    h.require(p['source_corpus']['passages']==list(corpus.values()),'Source corpus changed')
    h.require(not {'E118-I','E121-EQ'} & set(p['source_corpus']['indexed_ids']),'Pending source indexed')
    selected_c=results['recorded_C_section_baseline']
    runtime.validate_grid(selected_c,[q['id'] for q in cqueries])
    h.require(h.canonical(selected_c)==p['recorded_C_baseline']['selected_rows_sha256_canonical'],'Selected historical C rows changed')
    for row in selected_c:h.check_context(row,corpus)
    c_summary=runtime.summary(runtime.score_rows(selected_c,refs,corpus,no_tokenizer))
    original_h=h.frozen.read(root/h.PACKAGE/'results.json')
    h_baseline=[]
    for context,scored in zip(original_h['contexts'],original_h['metrics']['rows']):
        h_baseline.append({**context,'complete_evidence':scored['complete_evidence'],
            'reference_coverage':scored['required_source_coverage'],
            'outside_acceptable_ids':scored['outside_acceptable_context_ids'],
            'outside_acceptable_subset_tokens':scored['outside_acceptable_subset_tokens']})
    h_summary=runtime.summary(h_baseline)
    for name,record in p['original_runs'].items():
        check_input_versions(root,record)
        native=record['native_artifact_sha256_lf'];run_manifest=record['run_manifest_without_private_inventory']
        h.require(h.native_hash(p['source_corpus'])==native['corpus.json'],'Native source corpus changed')
        h.require(h.native_hash(h.frozen.read(root/h.PACKAGE/'review.json'))==native['human-review-snapshot.json'],'Run human review changed')
        for artifact in ('results.json','metrics.json','corpus.json','contexts-unscored.json'):
            h.require(native[artifact]==run_manifest['artifact_sha256_lf'][artifact],'Native manifest/output link changed')
        check_run(name,results[name],record,corpus,refs)
        metrics=results[name]['metrics']
        h.require(metrics['H_recorded_section_only']==h_summary and metrics['C_recorded_section_only']==c_summary,'Historical baseline summary changed')
        h.require(metrics['H_coverage_regressions']==[],'Unexpected coverage regression record')
    h.require(set(results)=={'development-a','development-b','recorded_C_section_baseline'},'Run inventory changed')
    h.require(m['status']=='development_results_not_independent' and not m['publication_allowed'],'Scope changed')
    return {'status':'verified','development_runs':2,'measured_contexts':80,'selected_C_control_contexts':20,
        'H_bilingual_complete':10,'C_bilingual_complete':10,'token_counts':'recorded_bounds_not_retokenized',
        'independent_evaluation':False,'benchmark_executed_by_verifier':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    print(json.dumps(verify(),ensure_ascii=False))
