"""Integrity of a frozen claim test, without conversion/runtime imports."""
import hashlib
import json
from pathlib import Path

from ingestion.claim_contract import ClaimExtraction, VERSION


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_bundle(output: Path):
    plan = json.loads((output / 'plan.json').read_text(encoding='utf8'))
    if plan.get('contract_version') != VERSION:
        raise ValueError('Wrong contract version')
    required = {'source.pdf', 'source-map.json', 'document.json', 'input.json', 'schema.json',
                'prompt.txt', 'manual-prompt.txt', 'conversion-profile.json', 'review-template.json'}
    if not required <= plan.get('files', {}).keys():
        raise ValueError('Incomplete test manifest')
    for name, expected in plan['files'].items():
        path = (output / name).resolve()
        if not path.is_relative_to(output.resolve()) or digest(path) != expected:
            raise ValueError(f'Changed prepared input: {name}')
    schema = json.loads((output / 'schema.json').read_text(encoding='utf8'))
    if schema != ClaimExtraction.model_json_schema():
        raise ValueError('Runtime contract differs from the frozen test schema')
    return plan
