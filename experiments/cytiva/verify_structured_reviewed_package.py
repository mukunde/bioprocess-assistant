"""Verify saved S01-S12 evidence using stdlib only; never execute the method."""
import json
from pathlib import Path
from experiments.cytiva import structured_evaluation as frozen

ROOT = frozen.ROOT
PACKAGE = Path('experiments/cytiva/reviewed-structured-control')
FILES = {'README.md', 'review.json', 'events.json', 'results.json', 'provenance.json'}
FREEZE_FILES = {'PROTOCOL.md', 'method-lock.json', 'manifest.json', 'questions.json',
                'submissions.json', 'references.json', 'review-template.json'}
EXTRA = {'experiments/cytiva/structured_evaluation.py', 'tests/test_structured_evaluation.py',
         'experiments/cytiva/verify_structured_reviewed_package.py',
         'tests/test_structured_reviewed_package.py',
         'docs/experiments/cytiva-structured-control-s-results.md',
         'docs/experiments/cytiva-structured-control-s-package.md'}


def native_hash(value):
    import hashlib
    return hashlib.sha256((json.dumps(value, ensure_ascii=False, indent=2,
                                     allow_nan=False) + '\n').encode('utf-8')).hexdigest()


def check_content(root, package):
    root, package = Path(root), Path(package)
    lock = frozen.read(root / frozen.PACKAGE / 'method-lock.json')
    preparation = frozen.read(root / frozen.PACKAGE / 'manifest.json')
    refs = {r['question_id']: r for r in frozen.read(root / frozen.PACKAGE / 'references.json')['references']}
    questions = {r['id']: r for r in frozen.read(root / frozen.PACKAGE / 'questions.json')['questions']}
    forms = {r['id']: r for r in frozen.read(root / frozen.PACKAGE / 'submissions.json')['submissions']}
    verified = {'manifest_sha256_lf': frozen.digest(root / frozen.PACKAGE / 'manifest.json'),
                'method_lock_sha256_lf': frozen.digest(root / frozen.PACKAGE / 'method-lock.json')}
    review = frozen.review_gate(package / 'review.json', verified, questions, forms, refs)
    require = frozen.require
    require(review['completed_human_reviews'] == 12 and review['pending_human_reviews'] == 0,
            'Review progress changed')
    require(review['review_status'] == 'complete_actual_human_review', 'Review status changed')
    excluded = {'E118-I', 'E121-EQ'}
    require(set(lock['excluded_source_ids']) == set(review['excluded_source_ids']) == excluded,
            'Source exclusions changed')
    require(preparation['method_lock_sha256_lf'] == verified['method_lock_sha256_lf'] and
            not preparation['evaluation_executed'], 'Preparation history changed')
    results = frozen.read(package / 'results.json')
    contexts, metrics = results['contexts'], results['metrics']
    require([(r['question_id'], r['language']) for r in contexts] ==
            [(qid, lang) for qid in frozen.IDS for lang in ('en', 'fr')], 'Saved grid changed')
    sources = {p['id']: p for p in frozen.read(root / lock['source_registry_file'])['passages']
               if p['id'] not in excluded}
    scores = []
    for row in contexts:
        require('runtime_error' not in row, 'Unexpected runtime error')
        require(isinstance(row['elapsed_ms'], (int, float)) and row['elapsed_ms'] >= 0, 'Timing changed')
        plan = row['result']['plan']
        require(not excluded & {p['id'] for p in plan['context']['source_passages']}, 'Quarantine leakage')
        grade = frozen.score_case(row['result'], refs[row['question_id']], sources)
        require(grade['passed'], 'Saved output fails frozen reference: ' + repr(grade['failures']))
        scores.append({'question_id': row['question_id'], 'language': row['language'], **grade})
    require(metrics['scores'] == scores, 'Recorded scores changed')
    pairs = [qid for qid in frozen.IDS if frozen.semantic_result(contexts[2*frozen.IDS.index(qid)]['result']) !=
             frozen.semantic_result(contexts[2*frozen.IDS.index(qid)+1]['result'])]
    require(not pairs and metrics['bilingual_semantic_failures'] == pairs, 'Bilingual semantics changed')
    require(metrics['planned_submissions'] == metrics['saved_submissions'] == metrics['passed_submissions'] == 24 and
            metrics['passed_scenarios_both_languages'] == 12 and metrics['gate'] == 'context_and_diagnostics_pass',
            'Frozen aggregate changed')
    require(metrics['evaluation_executed'] and not metrics['answer_quality_evaluated'] and
            not metrics['automatic_adoption'], 'Outcome scope changed')
    provenance = frozen.read(package / 'provenance.json')
    artifacts = {'contexts-unscored.json': contexts, 'metrics.json': metrics,
                 'human-review-snapshot.json': review, 'verification.json': provenance['verification'],
                 'reservation.json': provenance['reservation']}
    require(set(provenance['original_artifact_sha256_lf']) == set(artifacts), 'Artifact inventory changed')
    for name, value in artifacts.items():
        require(native_hash(value) == provenance['original_artifact_sha256_lf'][name], 'Native artifact changed: ' + name)
    require(provenance['reservation']['manifest_sha256_lf'] == verified['manifest_sha256_lf'] and
            provenance['reservation']['method_lock_sha256_lf'] == verified['method_lock_sha256_lf'],
            'Reservation freeze changed')
    require(provenance['verification']['review_sha256_canonical'] == frozen.canonical(review), 'Run review changed')
    safety = provenance['verification']
    require(safety['status'] == 'completed' and safety['network_attempts'] == [] and
            safety['frozen_files_unchanged'] and safety['earlier_files_unchanged'], 'Run preservation changed')
    events = frozen.read(package / 'events.json')
    require(events['decisions'] == review['decisions'], 'Decision events changed')
    amendment = events['S01_amendment']
    require(amendment['decision'] == review['decisions'][0], 'S01 decision changed')
    require(amendment['method_lock_sha256_lf'] == verified['method_lock_sha256_lf'] and
            amendment['manifest_sha256_lf_after'] == verified['manifest_sha256_lf'], 'S01 freeze binding changed')
    for name in ('manifest.json', 'submissions.json', 'review-template.json'):
        require(native_hash(amendment['before'][name]) == amendment['before_sha256_lf'][name], 'S01 prior artifact changed')
    require(amendment['before_sha256_lf']['manifest.json'] == amendment['manifest_sha256_lf_before'],
            'S01 prior manifest changed')
    previous = amendment['before']['manifest.json']
    require(previous['method_lock_sha256_lf'] == verified['method_lock_sha256_lf'], 'S01 previous method changed')
    for name in ('submissions.json', 'review-template.json'):
        require(previous['file_sha256_lf'][(frozen.PACKAGE / name).as_posix()] ==
                amendment['before_sha256_lf'][name], 'S01 previous input binding changed')
    original = amendment['before']['submissions.json']['submissions']
    require(original[1:] == list(forms.values())[1:], 'S01 amendment escaped its scope')
    corrected = json.loads(json.dumps(original[0]))
    addition = review['decisions'][0]['approved_form_amendment']
    for lang in ('en', 'fr'):
        task = next(t for t in corrected['input_' + lang]['tasks'] if t['task_id'] == 'B')
        task['exclusions'].append(addition)
    require(corrected == forms['S01'], 'S01 form correction changed')
    summary = provenance['recorded_summary']
    tokens = [r['result']['plan']['context_tokens'] for r in contexts]
    require(summary['saved_submissions'] == summary['passed_submissions'] == 24 and
            summary['passed_paired_scenarios'] == 12 and
            summary['context_tokens_min'] == min(tokens) and summary['context_tokens_max'] == max(tokens),
            'Export summary changed')
    require(provenance['source_pdf'] == frozen.read(root / frozen.PACKAGE / 'references.json')['source_pdf'],
            'Source document identity changed')
    return {'status': 'verified', 'human_decisions': 12, 'contexts': 24, 'passed_scenarios': 12,
            'excluded_sources': sorted(excluded), 'token_check': 'recorded_bounds_not_retokenized',
            'trial_executed_by_verifier': False, 'answer_quality_evaluated': False}


def verify(root=ROOT, package=None):
    root = Path(root).resolve()
    package = Path(package) if package is not None else root / PACKAGE
    manifest = frozen.read(package / 'manifest.json')
    lock = frozen.read(root / frozen.PACKAGE / 'method-lock.json')
    preparation = frozen.read(root / frozen.PACKAGE / 'manifest.json')
    expected_support = set(lock['file_sha256_lf']) | set(preparation['file_sha256_lf']) | EXTRA | {
        (frozen.PACKAGE / name).as_posix() for name in FREEZE_FILES}
    frozen.require(set(manifest['files']) == FILES and set(manifest['supporting_files']) == expected_support,
                   'Package inventory changed')
    frozen.require(manifest['status'] == 'completed_review_and_frozen_run', 'Package status changed')
    for base, hashes in [(package, manifest['files']), (root, manifest['supporting_files']),
                         (root, lock['file_sha256_lf']), (root, preparation['file_sha256_lf'])]:
        for name, checksum in hashes.items():
            path = (base / name).resolve()
            frozen.require(path.is_relative_to(base.resolve()) and path.is_file() and frozen.digest(path) == checksum,
                           'File missing/changed: ' + name)
    return check_content(root, package)


if __name__ == '__main__':
    print(json.dumps(verify()))
