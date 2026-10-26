"""Frozen structured-control challenge: verify only unless explicitly --run.

Verification and preparation never construct StructuredControl. Runtime receives
submitted JSON only; gold references score saved outputs after the whole grid.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('experiments/cytiva/structured-control-evaluation-v01')
IDS = [f'S{i:02d}' for i in range(1, 13)]
PACKET_FILES = {'questions.json', 'submissions.json', 'references.json', 'review-template.json', 'PROTOCOL.md'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                          encoding='utf-8', newline='\n')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def key(unit):
    return unit['task_id'], unit['item_id'], unit['information']


def slots(value):
    """Critical slot meaning; explanatory reason wording is not a metric."""
    if isinstance(value, dict):
        return {k: slots(v) for k, v in value.items() if k != 'reason'}
    return [slots(x) for x in value] if isinstance(value, list) else value


def verify(root=ROOT):
    """File integrity, static schema and reference topology; no planning."""
    from jsonschema import Draft202012Validator

    root = Path(root).resolve()
    folder = root / PACKAGE
    lock, manifest = read(folder / 'method-lock.json'), read(folder / 'manifest.json')
    require(manifest['method_lock_sha256_lf'] == digest(folder / 'method-lock.json'), 'Method lock binding changed')
    expected = set(lock['file_sha256_lf']) | {(PACKAGE / n).as_posix() for n in PACKET_FILES}
    require(set(manifest['file_sha256_lf']) == expected, 'Preparation inventory changed')
    for inventory in (lock['file_sha256_lf'], manifest['file_sha256_lf']):
        for name, checksum in inventory.items():
            path = (root / name).resolve()
            require(path.is_relative_to(root) and path.is_file() and digest(path) == checksum,
                    'Frozen file missing/changed: ' + name)
    require(not any(n.startswith('tests/') for n in lock['file_sha256_lf']), 'Active tests cannot be method dependencies')
    schema = read(root / lock['schema_file'])
    validator = Draft202012Validator(schema)
    questions, submissions, refs = (read(folder / name)[field] for name, field in (
        ('questions.json', 'questions'), ('submissions.json', 'submissions'), ('references.json', 'references')))
    require([q['id'] for q in questions] == IDS and
            [q['id'] for q in submissions] == IDS and [r['question_id'] for r in refs] == IDS,
            'Incomplete/duplicate challenge inventory')
    registry = read(root / lock['source_registry_file'])
    sources = {p['id']: p for p in registry['passages']}
    adapter = read(root / lock['adapter_file'])
    eligible = set(adapter['basis']['eligible_source_ids'])
    require(set(lock['excluded_source_ids']) == {'E118-I', 'E121-EQ'} == set(adapter['basis']['excluded_source_ids']),
            'Quarantine policy changed')
    reference_packet = read(folder / 'references.json')
    require(reference_packet['source_pdf'] == registry['source'], 'PDF identity changed')
    require(set(reference_packet['eligible_source_ids']) == eligible, 'Eligible source set changed')
    for source in reference_packet['source_passages']:
        require(source['id'] in eligible and source == sources[source['id']], 'Reference quote/provenance changed')
    dependency_policy = read(root / adapter['basis']['policy_file'])['source_runtime_policy']['requires']

    def closure(pid, trail=()):
        require(pid in eligible and pid not in trail, 'Invalid reference dependency')
        result = {pid}
        for dep in dependency_policy[pid]:
            result |= closure(dep, trail + (pid,))
        return result

    for question, submission, ref in zip(questions, submissions, refs):
        require(set(question) == {'id', 'family', 'question_en', 'question_fr', 'synthetic_scenario'},
                'Gold or runtime payload mixed into question text')
        require(set(submission) == {'id', 'input_en', 'input_fr'}, 'Gold fields in submission envelope')
        require(all(question['question_' + lang].strip() for lang in ('en', 'fr')), 'Missing bilingual wording')
        require(len(ref['units']) == len({key(u) for u in ref['units']}), 'Duplicate reference unit')
        for language in ('en', 'fr'):
            form = submission['input_' + language]
            validator.validate(form)
            require(form['language'] == language, 'Language binding changed')
            actual_keys = [(t['task_id'], i['item_id'], information) for t in form['tasks']
                           for i in t['items'] for information in i['information']]
            require(len(actual_keys) == len(set(actual_keys)) and set(actual_keys) == {key(u) for u in ref['units']},
                    'Reference unit inventory differs from submitted request')
        require(ref['human_review_status'] == 'pending', 'Preparation cannot approve references')
        require(ref['reservations'] and ref['expected_answer_en'] and ref['expected_answer_fr'], 'Incomplete human review reference')
        require(set(ref['acceptable_context_ids']) <= eligible, 'Noneligible acceptable context')
        for unit in ref['units']:
            require(unit['expected']['state'] in ('supported', 'needs_clarification', 'quarantined',
                    'missing_source', 'out_of_scope', 'unsupported_selector', 'unsupported_transformation'),
                    'Unsupported reference state')
            if unit['expected']['state'] == 'supported':
                require(unit['required_source_sets'] and unit['binding'] is not None, 'Missing supported-unit reference')
            else:
                require(not unit['required_source_sets'] and unit['binding'] is None, 'Blocked unit cannot require admission')
            for bundle in unit['required_source_sets']:
                require(set(bundle) <= set(ref['acceptable_context_ids']), 'Required sources outside allowed context')
                require(all(closure(pid) <= set(bundle) for pid in bundle), 'Missing mandatory inherited dependency')
        require(set(ref['review_source_ids']) <= {s['id'] for s in reference_packet['source_passages']}, 'Review passage missing')
    require(manifest['status'] == 'frozen_pending_human_reference_review' and not manifest['evaluation_executed'],
            'Preparation status changed')
    return {'integrity': 'verified', 'scenarios': 12, 'structured_submissions': 24,
            'pending_human_reviews': 12, 'manifest_sha256_lf': digest(folder / 'manifest.json'),
            'method_lock_sha256_lf': digest(folder / 'method-lock.json'),
            'evaluation_executed_by_this_command': False}


def review_gate(path, verified, questions, submissions, references):
    review = read(path)
    require(review.get('manifest_sha256_lf') == verified['manifest_sha256_lf'] and
            review.get('method_lock_sha256_lf') == verified['method_lock_sha256_lf'], 'Review belongs to another freeze')
    rows = review.get('decisions', [])
    require(len(rows) == len(IDS) and {r.get('question_id') for r in rows} == set(IDS), 'All twelve actual human decisions required')
    for row in rows:
        qid = row['question_id']
        require(row.get('decision') in ('validated', 'validated_with_reservation') and
                isinstance(row.get('human_quote'), str) and row['human_quote'].strip(), 'Missing actual human approval')
        for name, value in (('question', questions[qid]), ('submission', submissions[qid]), ('reference', references[qid])):
            require(row.get(name + '_sha256_canonical') == canonical(value), 'Human review content binding changed')
        require(row.get('retained_reservations') == references[qid]['reservations'], 'Review reservations changed')
        require(isinstance(row.get('reviewed_at_utc'), str), 'Missing review timestamp')
        at = datetime.fromisoformat(row['reviewed_at_utc'].replace('Z', '+00:00'))
        require(at.tzinfo is not None and at.utcoffset().total_seconds() == 0, 'Review timestamp must be UTC')
    return review


def score_case(result, reference, sources, count_tokens=None):
    """Score saved structured output, not generated answers or user prose."""
    failures = []
    plan = result['plan']
    units = plan['units']
    bindings = plan['context']['bindings']
    passages = plan['context']['source_passages']
    observed_keys = [key(u) for u in units]
    expected_keys = [key(u) for u in reference['units']]
    if len(observed_keys) != len(set(observed_keys)) or set(observed_keys) != set(expected_keys):
        failures.append('unit_inventory')
    observed = {key(u): u for u in units}
    source_ids = [p['id'] for p in passages]
    if len(source_ids) != len(set(source_ids)) or not set(source_ids) <= set(reference['acceptable_context_ids']):
        failures.append('source_scope')
    if (len(plan['selected_root_ids']) != len(set(plan['selected_root_ids'])) or len(plan['selected_root_ids']) > 6 or
            not set(plan['selected_root_ids']) <= set(source_ids) or not 0 <= plan['context_tokens'] <= 2048):
        failures.append('resource_invariant')
    if count_tokens is not None:
        actual_tokens = count_tokens(json.dumps(plan['context'], ensure_ascii=False, separators=(',', ':'), allow_nan=False))
        if actual_tokens != plan['context_tokens'] or actual_tokens > 2048:
            failures.append('token_accounting')
    for p in passages:
        fields = ('id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
                  'quote_sha256', 'page_text_start', 'page_text_end')
        if p['id'] not in sources or p != {k: sources[p['id']][k] for k in fields}:
            failures.append('source_integrity')
    wanted_bindings = []
    for ref in reference['units']:
        identity = key(ref)
        actual = observed.get(identity)
        if actual is None:
            continue
        prefix = '/'.join(identity)
        for name, value in ref['expected'].items():
            if actual.get(name) != value:
                failures.append(prefix + ':' + name)
        codes = {d['code'] for d in actual.get('diagnostics', [])}
        if not set(ref['required_diagnostic_codes']) <= codes:
            failures.append(prefix + ':diagnostics')
        matched = [b for b in bindings if key(b) == identity]
        if ref['binding'] is None:
            if matched or actual.get('source_ids'):
                failures.append(prefix + ':blocked_unit_assignment')
        else:
            wanted_bindings.append(identity)
            if len(matched) != 1:
                failures.append(prefix + ':binding_count')
                continue
            binding = matched[0]
            for name, value in ref['binding'].items():
                if slots(binding.get(name)) != slots(value):
                    failures.append(prefix + ':binding_' + name)
            if set(actual.get('source_ids', [])) != set(ref['direct_support_ids']):
                failures.append(prefix + ':direct_support')
            if not any(set(bundle) <= set(binding['source_ids']) <= set(source_ids)
                       for bundle in ref['required_source_sets']):
                failures.append(prefix + ':complete_support_bundle')
            if not set(binding['source_ids']) <= set().union(*map(set, ref['required_source_sets'])):
                failures.append(prefix + ':binding_source_scope')
    if len(bindings) != len(wanted_bindings) or {key(b) for b in bindings} != set(wanted_bindings):
        failures.append('binding_scope')
    for name, value in reference['expected_aggregates'].items():
        if plan.get(name) != value:
            failures.append('aggregate:' + name)
    return {'passed': not failures, 'failures': sorted(set(failures)), 'answer_quality_evaluated': False}


def semantic_result(result):
    plan = result['plan']
    return {'units': [{**{k: u[k] for k in ('task_id', 'item_id', 'information', 'state',
                     'interpretation_state', 'documentary_support_state', 'source_ids')},
                     'diagnostic_codes': sorted({d['code'] for d in u['diagnostics']})} for u in plan['units']],
            'bindings': slots(plan['context']['bindings']),
            'context_ids': [p['id'] for p in plan['context']['source_passages']],
            'roots': plan['selected_root_ids'],
            'aggregates': {k: plan[k] for k in ('all_requested_units_accounted_for',
                           'all_supported_ready_units_covered', 'has_interpretation_issues', 'has_unserved_units')}}


@contextmanager
def offline():
    attempts = []
    def blocked(*args, **kwargs):
        attempts.append('network_call')
        raise RuntimeError('Network forbidden in frozen structured evaluation')
    with patch.object(socket.socket, 'connect', blocked), patch.object(socket, 'create_connection', blocked), \
            patch.object(socket, 'getaddrinfo', blocked):
        yield attempts


def make_runtime(root):
    from ingestion.structured_request import StructuredControl
    return StructuredControl(root)


def protected_files(root):
    """Preserve tracked files and earlier private experimental outputs per run.

    This is not an immutable method dependency inventory: active test files can
    evolve outside a running trial without invalidating the method lock.
    """
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode('utf-8').split('\0')
    files = {root / n for n in tracked if n}
    earlier = root / 'data/experiments'
    if earlier.exists():
        files.update(p for p in earlier.rglob('*') if p.is_file())
    return {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files}


def run(review_path, root=ROOT):
    root = Path(root).resolve()
    verified = verify(root)
    folder = root / PACKAGE
    queries = {q['id']: q for q in read(folder / 'questions.json')['questions']}
    submissions = {q['id']: q for q in read(folder / 'submissions.json')['submissions']}
    references = {r['question_id']: r for r in read(folder / 'references.json')['references']}
    review_path = Path(review_path).resolve()
    review = review_gate(review_path, verified, queries, submissions, references)
    lock = read(folder / 'method-lock.json')
    require(platform.python_version() == lock['python_version'] and os.environ.get('PYTHONHASHSEED') == '0', 'Pinned Python/hash seed changed')
    for name, version in lock['dependency_versions'].items():
        require(importlib.metadata.version(name) == version, 'Pinned dependency changed: ' + name)
    asset = root / lock['tokenizer_asset_file']
    require(asset.is_file() and hashlib.sha256(asset.read_bytes()).hexdigest() == lock['tokenizer']['asset_sha256'],
            'Pinned local tokenizer asset unavailable; no run reserved and no download')
    raw_output = root / lock['run_directory']
    require(not raw_output.is_symlink(), 'Output symlink forbidden')
    output = raw_output.resolve()
    require(output.is_relative_to((root / 'data/experiments').resolve()), 'Output outside experiment directory')
    require(not output.exists() and not output.is_symlink(), 'Existing output: preserve, no retry or overwrite')
    # No directory or runtime is created until all human approvals are verified.
    protected = {n: digest(root / n) for n in read(folder / 'manifest.json')['file_sha256_lf']}
    prior_files = protected_files(root)
    output.mkdir(parents=True, exist_ok=False)
    contexts = []
    with offline() as attempts:
        try:
            dump(output / 'reservation.json', {'status': 'reserved_no_retry', **verified})
            dump(output / 'human-review-snapshot.json', review)
            inputs = list(protected) + [(PACKAGE / 'method-lock.json').as_posix(), (PACKAGE / 'manifest.json').as_posix()]
            for name in inputs:
                target = output / 'input-snapshot' / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((root / name).read_bytes())
            started = time.perf_counter()
            runtime = make_runtime(root)
            initialization_ms = (time.perf_counter() - started) * 1000
            for qid in IDS:
                for language in ('en', 'fr'):
                    before = time.perf_counter()
                    try:
                        result = runtime.evaluate(submissions[qid]['input_' + language], request_id=qid + '-' + language)
                        row = {'question_id': qid, 'language': language, 'result': result,
                               'elapsed_ms': (time.perf_counter() - before) * 1000}
                    except Exception as exc:
                        row = {'question_id': qid, 'language': language, 'runtime_error': str(exc),
                               'elapsed_ms': (time.perf_counter() - before) * 1000}
                    contexts.append(row)
                    dump(output / 'contexts-unscored.json', contexts)
            # Gold references cannot be passed into runtime.evaluate; scoring starts only now.
            sources = {p['id']: p for p in read(root / lock['source_registry_file'])['passages']
                       if p['id'] not in lock['excluded_source_ids']}
            from ingestion.structured_sources import local_token_counter
            counter = local_token_counter(root, lock['tokenizer'])
            scores = []
            for row in contexts:
                graded = ({'passed': False, 'failures': ['runtime_error'], 'answer_quality_evaluated': False}
                          if 'runtime_error' in row else score_case(row['result'], references[row['question_id']], sources, counter))
                scores.append({'question_id': row['question_id'], 'language': row['language'], **graded})
            paired_failures = []
            for qid in IDS:
                pair = [r for r in contexts if r['question_id'] == qid]
                if any('runtime_error' in r for r in pair) or semantic_result(pair[0]['result']) != semantic_result(pair[1]['result']):
                    paired_failures.append(qid)
            require(not attempts, 'Network attempted; preserve failure output')
            for name, checksum in protected.items():
                require(digest(root / name) == checksum, 'Frozen file changed during run: ' + name)
            require(read(review_path) == review, 'Review changed during run')
            for name, checksum in prior_files.items():
                require(hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum,
                        'Prior file changed during run: ' + name)
            verify(root)
            metrics = {'planned_submissions': 24, 'saved_submissions': len(contexts),
                       'passed_submissions': sum(s['passed'] for s in scores), 'scores': scores,
                       'passed_scenarios_both_languages': sum(all(s['passed'] for s in scores if s['question_id'] == qid) for qid in IDS),
                       'bilingual_semantic_failures': paired_failures,
                       'initialization_ms': initialization_ms, 'evaluation_executed': True,
                       'gate': 'context_and_diagnostics_pass' if all(s['passed'] for s in scores) and not paired_failures else 'blocked_failures',
                       'answer_quality_evaluated': False, 'automatic_adoption': False}
            dump(output / 'metrics.json', metrics)
            dump(output / 'verification.json', {'status': 'completed', 'network_attempts': attempts,
                                               'frozen_files_unchanged': True, 'earlier_files_unchanged': True,
                                               'review_sha256_canonical': canonical(review)})
            return metrics
        except Exception as exc:
            dump(output / 'failure.json', {'status': 'failed_preserve_no_retry', 'error': str(exc),
                                          'saved_submissions': len(contexts), 'network_attempts': attempts})
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--review', type=Path)
    args = parser.parse_args(argv)
    if args.run and args.review is None:
        parser.error('--run requires all actual human decisions via --review')
    print(json.dumps(run(args.review) if args.run else verify(), ensure_ascii=False))


if __name__ == '__main__':
    main()
