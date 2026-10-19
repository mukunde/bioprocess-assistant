"""Offline structural/evidence checks, not semantic approval or an LLM judge."""
import json
import sys
from pathlib import Path
import jsonschema

from experiments.cytiva.paths import V01 as HERE
ALLOWED={'MAY_CAUSE':('Cause','Symptom'),'RECOMMENDED_FOR':('Action','Symptom'),
         'CAN_REMOVE':('Action','Cause'),'PREVENTS_BUILDUP_OF':('Action','Cause')}

def check(value, schema, corpus):
    jsonschema.validate(value,schema)
    issues=[]
    items={e['item_ref']:e for e in corpus['elements']}
    ids=[e['id'] for e in value['entities']]
    if len(ids)!=len(set(ids)): issues.append('duplicate_entity_ids')
    entities={e['id']:e for e in value['entities']}
    claims=value['claims']
    if not claims: issues.append('empty_claims')
    if len({c['id'] for c in claims})!=len(claims): issues.append('duplicate_claim_ids')
    resolved=[]
    for claim in claims:
        cid=claim['id']; subject=entities.get(claim['subject_id']); target=entities.get(claim['object_id'])
        if claim['predicate']=='PROCEDURE':
            valid=subject and subject['kind']=='Action' and claim['object_id'] is None
        else:
            valid=subject and target and (subject['kind'],target['kind'])==ALLOWED[claim['predicate']]
        if not valid: issues.append(f'{cid}:invalid_endpoints_or_direction')
        groups=[claim['evidence_refs'],claim['scope_refs']]
        groups += [x['evidence_refs'] for x in claim['conditions']+claim['parameters']]
        for refs in groups:
            if not refs: issues.append(f'{cid}:missing_evidence')
            for ref in refs:
                if ref not in items: issues.append(f'{cid}:unknown_evidence:{ref}')
        resolved.append(dict(claim_id=cid,evidence=[items[r] for r in claim['evidence_refs'] if r in items],
                             scope=[items[r] for r in claim['scope_refs'] if r in items],review_status='pending'))
    return dict(structural_pass=not issues,issues=issues,claims=len(claims),resolved=resolved,
                semantic_validation='not_performed',manual_approval=False)

if __name__=='__main__':
    result=check(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')),
                 json.loads((HERE/'schema.json').read_text(encoding='utf-8')),
                 json.loads((HERE/'input.json').read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['structural_pass'] else 1)
