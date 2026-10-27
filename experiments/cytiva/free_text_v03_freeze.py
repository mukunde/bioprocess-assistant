"""Read-only v03 runtime freeze verifier; never constructs an interpreter."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('experiments/cytiva/free-text-v03-freeze-v01')
PINNED = (
    'ingestion/__init__.py', 'ingestion/coverage_v03.py',
    'ingestion/structured_request_v03.py', 'ingestion/free_text_bridge_v03.py',
    'ingestion/free_text_interpreter_v03.py', 'ingestion/free_text_contract.py',
    'ingestion/structured_request.py', 'ingestion/structured_sources.py',
    'ingestion/local_passage_retrieval.py', 'ingestion/free_text_bridge.py',
    'ingestion/free_text_interpreter.py',
    'docs/technical/free-text-input-v01.schema.json',
    'docs/technical/free-text-interpretation-v01.schema.json',
    'docs/technical/free-text-outcome-v01.schema.json',
    'docs/technical/free-text-runtime-policy-v01.json',
    'docs/technical/task-request-v01.schema.json',
    'docs/technical/task-request-catalog-v01.json',
    'docs/technical/task-request-source-adapter-v01.json',
    'docs/technical/coverage-summary-v03.schema.json',
    'docs/technical/control-v03-outcome.schema.json',
    'docs/technical/coverage-summary-v03-examples.json',
    'docs/technical/COVERAGE-CONTRACT-V03-ENCODING.md',
    'docs/technical/TASK-REQUEST-TECHNICAL-SPEC-V01.md',
    'docs/technical/FREE-TEXT-CANDIDATE-V03-REVIEW-FIXES.md',
    'docs/decisions/2026-10-25-task-request-technical-review.json',
    'docs/decisions/2026-10-27-coverage-contract-CC-review.json',
    'experiments/cytiva/contaminants-pilot-v01/evidence.json',
    'experiments/cytiva/v05-evaluation-v01/candidate.json',
    'experiments/cytiva/reviewed-contaminant-questions/manifest.json',
    'experiments/__init__.py', 'experiments/cytiva/__init__.py',
    'requirements-structured.txt',
    'experiments/cytiva/free_text_v03_freeze.py',
    'experiments/cytiva/free-text-v03-freeze-v01/METHOD.md',
    'experiments/cytiva/free-text-v03-freeze-v01/README.md',
    'experiments/cytiva/free-text-v03-freeze-v01/freeze-decision.json',
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def verify(root=ROOT, *, environment=False):
    root = Path(root).resolve()
    lock = json.loads((root/PACKAGE/'method-lock.json').read_text(encoding='utf-8'))
    if (lock['id'] != 'free-text-v03-corrected-runtime-freeze-v01'
            or set(lock['file_sha256_lf']) != set(PINNED)):
        raise ValueError('Unexpected freeze or dependency inventory')
    for name, expected in lock['file_sha256_lf'].items():
        path = (root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or digest(path) != expected:
            raise ValueError('Frozen component changed: '+name)
    if lock['runtime_entry_points'] != {
        'structured': 'ingestion.structured_request_v03.StructuredControlV03',
        'free_text': 'ingestion.free_text_bridge_v03.FreeTextControlV03',
    }:
        raise ValueError('Entry points changed')
    if lock['scope'] != 'runtime_only_no_prospective_trial' or lock['evaluation_executed']:
        raise ValueError('A runtime freeze cannot certify a trial')
    adapter = json.loads((root/'docs/technical/task-request-source-adapter-v01.json').read_text(encoding='utf-8'))
    if (lock['excluded_source_ids'] != ['E118-I', 'E121-EQ']
            or lock['eligible_source_ids'] != adapter['basis']['eligible_source_ids']
            or len(lock['eligible_source_ids']) != 25
            or lock['root_limit'] != 6 or lock['context_token_limit'] != 2048
            or lock['max_core_calls'] != 1):
        raise ValueError('Frozen source policy or budgets changed')
    if environment:
        env = lock['environment']
        if platform.python_version() != env['python_version']:
            raise ValueError('Python version mismatch')
        for name, version in env['dependencies'].items():
            if importlib.metadata.version(name) != version:
                raise ValueError('Dependency mismatch: '+name)
        asset = (root/env['tokenizer_asset_file']).resolve()
        if (not asset.is_relative_to(root) or not asset.is_file()
                or hashlib.sha256(asset.read_bytes()).hexdigest() != env['tokenizer_asset_sha256']):
            raise ValueError('Offline tokenizer asset mismatch')
    return {'id': lock['id'], 'status': 'frozen', 'pinned_files': len(PINNED),
            'method_lock_sha256_lf': digest(root/PACKAGE/'method-lock.json'),
            'environment_verified': environment, 'runtime_instantiated': False,
            'prospective_trial_executed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(environment=args.environment), indent=2))
    except (ValueError, KeyError, OSError, importlib.metadata.PackageNotFoundError) as exc:
        parser.exit(1, 'Freeze verification failed: '+str(exc)+'\n')


if __name__ == '__main__':
    main()
