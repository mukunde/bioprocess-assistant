"""Verify/replay a separate MabSelect documentary freeze; standard library only."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('experiments/cytiva/mabselect-handoff-freeze-v01')
FREEZE_ID = 'mabselect-documentary-handoff-corrected-freeze-v01'
ROOTS = (
    'demo/__init__.py', 'demo/documentary.py', 'demo/documentary_preview.py',
    'demo/static/documentary.html', 'demo/mabselect.py',
    'experiments/__init__.py', 'experiments/cytiva/__init__.py',
    'experiments/cytiva/verify_mabselect_design.py',
    'experiments/cytiva/verify_cleaning_retrieval_package.py',
    'experiments/cytiva/verify_section_questions_package.py',
    'docs/technical/mabselect-cleaning-approved-contract-v01.md',
    'docs/technical/mabselect-cleaning-review-v01.json',
    'docs/technical/mabselect-cleaning-sources-v01.json',
    'docs/technical/reviewed-dossier-serving-decisions-v01.json',
    'docs/technical/reviewed-dossier-serving-technical-decisions-v01.json',
    'experiments/cytiva/reviewed-cleaning-retrieval/manifest.json',
    'experiments/cytiva/reviewed-section-questions/manifest.json',
    'experiments/cytiva/mabselect_handoff_freeze.py',
    'tests/test_mabselect_handoff_freeze.py',
    str(PACKAGE/'README.md'), str(PACKAGE/'METHOD.md'),
    str(PACKAGE/'freeze-decision.json'),
) + tuple('docs/schemas/reviewed-serving-v1/'+n+'.schema.json' for n in (
    'common', 'request', 'response', 'validation-error', 'mapping', 'source-index',
    'source-view', 'release', 'authority'))
EXAMPLES = 'docs/technical/reviewed-dossier-serving-interface-examples-v01.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def inventory(root):
    """All runtime/approval inputs, including files read by the Q/N verifiers."""
    root = Path(root).resolve()
    pending = [p.replace('\\', '/') for p in ROOTS]
    found = set()
    while pending:
        name = pending.pop()
        path = (root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Missing/unsafe freeze dependency: '+name)
        if name in found:
            continue
        found.add(name)
        if path.suffix != '.json':
            continue
        data = read(path)
        for section in ('approved_materials_sha256_lf', 'supporting_files', 'dependencies'):
            pending.extend(data.get(section, {}))
        if name.endswith('/manifest.json'):
            for child in data.get('files', {}):
                # Preparation manifests use repository paths; review manifests use local names.
                pending.append(child if '/' in child else (Path(name).parent/child).as_posix())
    return sorted(found)


def verify(root=ROOT, *, environment=False):
    root = Path(root).resolve()
    lock = read(root/PACKAGE/'method-lock.json')
    if (lock.get('id') != FREEZE_ID or lock.get('status') != 'frozen'
            or lock.get('scope') != 'local_documentary_runtime_and_accepted_case_replay_no_activation'
            or lock.get('roots') != [p.replace('\\', '/') for p in ROOTS]
            or lock.get('entry_points') != {'service':'demo.documentary.Handoff', 'preview':'demo.documentary_preview.main'}
            or lock.get('policy') != {'preview_only':True, 'serving_activated':False,
                                      'context_bytes':65536, 'request_bytes':32768, 'max_tasks':8,
                                      'excluded_source_ids':['E118-I','E121-EQ'], 'prospective_evaluation':False}):
        raise ValueError('Freeze identity, scope or policy changed')
    names = inventory(root)
    if set(names) != set(lock['file_sha256_lf']):
        raise ValueError('Freeze dependency inventory changed')
    for name, expected in lock['file_sha256_lf'].items():
        if digest(root/name) != expected:
            raise ValueError('Frozen component changed: '+name)
    if environment:
        if lock['environment'] != {'python_implementation':platform.python_implementation(),
                                    'python_version':platform.python_version(), 'runtime_dependencies':{}}:
            raise ValueError('Frozen Python environment mismatch')
    return {'id':FREEZE_ID, 'status':'frozen', 'pinned_files':len(names),
            'method_lock_sha256_lf':digest(root/PACKAGE/'method-lock.json'),
            'environment_verified':environment, 'runtime_instantiated':False,
            'serving_activated':False, 'prospective_evaluation':False}


def check_case(case, out):
    """Check every accepted projection, not just the aggregate status."""
    expected = case['expected']
    if 'validation_error' in expected:
        if out['kind'] != 'reviewed_serving_validation_error/v1' or out['errors'][0]['code'] != expected['validation_error']:
            raise ValueError(case['id']+': validation mismatch')
        return
    if out['status'] != expected['status']:
        raise ValueError(case['id']+': status mismatch')
    bundles = out['context']['bundles']
    for row in expected.get('item_states', []):
        actual = next(i for i in out['items'] if i['task_id']==row['task_id'] and i['requested_item']==row['item'])
        if actual['state'] != row['state']:
            raise ValueError(case['id']+': item mismatch')
    if 'bundle_keys' in expected and [b['bundle_key'] for b in bundles] != expected['bundle_keys']:
        raise ValueError(case['id']+': bundle mismatch')
    if expected.get('no_restricted_block') and any(b['review_scope']=='Q06' for b in bundles):
        raise ValueError('Restricted block leaked')
    if 'clarification_target' in expected and out['items'][0]['clarification_targets'] != [expected['clarification_target']]:
        raise ValueError('Wrong clarification target')
    if 'procedure_cards' in expected and sum(o['role']=='procedure' for b in bundles for o in b['options']) != expected['procedure_cards']:
        raise ValueError('Procedure supplied during clarification')
    if expected.get('technical_context_empty') and any(out['context'].values()):
        raise ValueError('Unexpected technical context')
    if 'reason' in expected and out['response_reason'] != expected['reason']:
        raise ValueError('Wrong response reason')
    if 'clarification_task' in expected:
        a = next(i for i in out['items'] if i['task_id']==expected['clarification_task'])
        b = next(i for i in out['items'] if i['task_id']==expected['supported_task'])
        if (a['state'] != 'needs_clarification' or b['state'] != 'supported'
                or a['clarification_targets'] != ['product','deposit_context']):
            raise ValueError('Cross-task clarification mismatch')


def replay():
    verified = verify(environment=True)  # Before runtime import or output creation.
    cases = read(ROOT/EXAMPLES)['examples']
    if [c['id'] for c in cases] != [f'SX{i:02}' for i in range(1,7)]:
        raise ValueError('Accepted case inventory changed')
    rows = []
    attempts = []
    def blocked(*_args, **_kwargs):
        attempts.append('socket_operation')
        raise RuntimeError('Network forbidden during frozen replay')
    with ExitStack() as stack:
        for target in ('socket.socket', 'socket.create_connection', 'socket.getaddrinfo'):
            stack.enter_context(patch(target, side_effect=blocked))
        from demo.documentary import Handoff
        from demo import mabselect as selector
        service = Handoff(preview=True)
        for case in cases:
            request = deepcopy(case['request'])
            with patch.object(selector, 'evaluate', wraps=selector.evaluate) as lookup:
                out = service.evaluate(request)
            if request != case['request']:
                raise ValueError('Request mutated')
            check_case(case, out)
            if case['expected'].get('lookup_executed') is False and lookup.call_count:
                raise ValueError('Unauthorized lookup')
            citations = []
            if out['kind'] == 'reviewed_documentary_bundle/v1':
                if out['context_measure']['delivered_bytes'] != len(canonical(out['context'])):
                    raise ValueError('Context measurement mismatch')
                for item in out['items']:
                    task = next(t for t in request['tasks'] if t['task_id']==item['task_id'])
                    for ref in item['bundle_refs']:
                        bundle = out['context']['bundles'][int(ref.rsplit('/',1)[1])]
                        if bundle['product'] != task['product'] or bundle['deposit_context'] != task['deposit_context']:
                            raise ValueError('Cross-task context inherited')
                        if bundle['suitability'] != 'not_established':
                            raise ValueError('Suitability promoted')
                    if item['state'] in ('abstained','excluded','unavailable','quarantined') and item['bundle_refs']:
                        raise ValueError('Nonserved item received context')
                for ref in out['citation_refs']:
                    view = service.source(ref['release_id'], ref['source_id'])
                    passage = next(p for p in out['context']['passages'] if p['source_id']==ref['source_id'])
                    if view['status']!='available' or view['passage']!=passage:
                        raise ValueError('Citation resolution mismatch')
                    citations.append({'href':ref['href'], 'source_id':ref['source_id'],
                                      'quote_sha256':passage['quote_sha256'], 'status':'available'})
                # Numerical pressure is deliberately not represented as a supported value.
                if any(i['requested_item']=='pressure_limit' and i['state']=='supported' for i in out['items']):
                    raise ValueError('Invented pressure support')
            rows.append({'case_id':case['id'], 'status':'passed', 'selector_calls':lookup.call_count,
                         'request':request, 'response':out, 'resolved_citations':citations,
                         'response_sha256':hashlib.sha256(canonical(out)).hexdigest()})
    if attempts:
        raise ValueError('Blocked network attempt during replay')
    if verify(environment=True) != verified:
        raise ValueError('Freeze changed during replay')
    return {'id':FREEZE_ID+'-accepted-case-replay', 'freeze':verified,
            'scope':'known_accepted_examples_not_independent_answer_or_scientific_validation',
            'status':'passed', 'cases':rows, 'network_attempts':attempts,
            'llm_calls':0, 'paid_api_calls':0, 'serving_activated':False,
            'prospective_evaluation':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', action='store_true')
    parser.add_argument('--replay', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and not args.replay:
        parser.error('--output requires --replay')
    try:
        if args.output and args.output.exists():
            raise ValueError('Output already exists; nothing overwritten')
        result = replay() if args.replay else verify(environment=args.environment)
        if args.output:
            # Exclusive creation after successful checks, preserving every earlier run.
            with args.output.open('x', encoding='utf-8', newline='\n') as out:
                out.write(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='cases'} | ({'case_results':{c['case_id']:c['status'] for c in result['cases']}} if args.replay else {}), indent=2))
    except (ValueError, KeyError, OSError, StopIteration, RuntimeError) as error:
        parser.exit(1, 'MabSelect freeze/replay failed: '+str(error)+'\n')


if __name__ == '__main__':
    main()
