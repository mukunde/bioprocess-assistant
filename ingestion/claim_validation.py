"""Offline staging checks. Finding evidence is not semantic or human approval."""
from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal
from pathlib import Path

from ingestion.claim_contract import ClaimExtraction, decimals

ENDPOINTS = {
    "MAY_CAUSE": ("Cause", "Symptom"),
    "RECOMMENDED_FOR": ("Action", "Symptom"),
    "CAN_REMOVE": ("Action", "Cause"),
    "PREVENTS_BUILDUP_OF": ("Action", "Cause"),
}


def numbers(text):
    # Parse a scientific literal as one value, never as mantissa/exponent parts.
    text = text.replace('\u2212', '-')
    text = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}(?:\D|$))", "", text)
    literal = r'[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)'
    powers = re.compile(
        r'(?<![\w.])(' + literal + r')\s*[\u00d7x\u00b7]\s*10\s*'
        r'(?:\^\s*([+-]?\d+)|([\u2070\u00b9\u00b2\u00b3\u2074-\u2079\u207a\u207b]+))'
        r'(?![\w.])')
    superscripts = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻', '0123456789+-')
    result = set()
    def take_power(match):
        exponent = match.group(2) or match.group(3).translate(superscripts)
        result.update(decimals([match.group(1).replace(',', '.') + 'e' + exponent]))
        return ' '
    text = powers.sub(take_power, text)
    tokens = re.findall(r'(?<![\w.])' + literal + r'(?:[eE][+-]?\d+)?(?![\w.]|[.,]\d)', text)
    result.update(decimals([token.replace(',', '.') for token in tokens]))
    # Exact English numerals, not approximate duration or 'few' inference.
    for word, number in [('zero', 0), ('one', 1), ('two', 2), ('three', 3), ('four', 4),
                         ('five', 5), ('six', 6), ('seven', 7), ('eight', 8), ('nine', 9), ('ten', 10)]:
        if re.search(r'\b' + word + r'\b', text, re.IGNORECASE):
            result.add(Decimal(number))
    return result


def unit_present(unit, text):
    text = text.replace("μ", "µ")
    aliases = {
        "CV": r"(?:column\s+volumes?|CV)",
        "µL": r"(?:µL|microliters?|microlitres?)",
        "mL": r"(?:mL|milliliters?|millilitres?)",
        "µm": r"(?:µm|micrometers?|micrometres?)",
        "dimensionless": r".*",
        "× g": r"(?:×\s*g|x\s*g)",
    }
    pattern = aliases.get(unit.replace("μ", "µ"), re.escape(unit.replace("μ", "µ")))
    return bool(re.search(r"(?<![A-Za-z])" + pattern + r"(?![A-Za-z])", text))


def validate_candidate(raw, corpus):
    value = ClaimExtraction.model_validate(raw)
    items = {i["item_ref"]: i for i in corpus["elements"]}
    if len(items) != len(corpus["elements"]):
        raise ValueError("Duplicate source item IDs")
    flags = corpus.get("source_flags", [])
    if len({f['id'] for f in flags}) != len(flags):
        raise ValueError("Duplicate application source flag IDs")
    for flag in flags:
        if not flag['evidence_refs'] or not set(flag['evidence_refs']) <= items.keys():
            raise ValueError("Invalid application source flag evidence")
    errors = []
    entity_ids = [e.id for e in value.entities]
    claim_ids = [c.id for c in value.claims]
    issue_ids = [s.id for s in value.source_issues]
    for label, ids in [('entity', entity_ids), ('claim', claim_ids), ('issue', issue_ids)]:
        if len(ids) != len(set(ids)):
            errors.append(f'duplicate_{label}_ids')
    entities = {e.id: e for e in value.entities}
    issues = {s.id: s for s in value.source_issues}

    def check_refs(refs, label):
        if not refs or not set(refs) <= items.keys():
            errors.append(f'{label}:invalid_evidence')

    for entity in value.entities:
        check_refs(entity.evidence_refs, f'entity:{entity.id}')
    for issue in value.source_issues:
        check_refs(issue.evidence_refs, f'issue:{issue.id}')
        if not set(issue.affected_claim_ids) <= set(claim_ids):
            errors.append(f'issue:{issue.id}:unknown_claim')

    rows = []
    for claim in value.claims:
        cid = claim.id
        local = []
        subject = entities.get(claim.subject_id)
        obj = entities.get(claim.object_id)
        if claim.predicate in ('PROCEDURE', 'DESCRIPTIVE'):
            valid = subject and subject.kind == 'Action' and claim.object_id is None
        else:
            valid = subject and obj and (subject.kind, obj.kind) == ENDPOINTS[claim.predicate]
        if not valid:
            local.append('invalid_endpoints')
        if claim.predicate == 'MAY_CAUSE' and claim.force != 'possible':
            local.append('causality_must_remain_possible')
        if claim.predicate == 'RECOMMENDED_FOR':
            if claim.force != 'recommended' or claim.symptom_context != 'observed_trigger':
                local.append('recommendation_requires_observed_trigger')
            if not claim.condition_groups or any(
                    not any(c.role == 'trigger' for c in g.all_of)
                    for g in claim.condition_groups):
                local.append('recommendation_missing_trigger_condition')
        if claim.predicate == 'DESCRIPTIVE' and claim.force != 'descriptive':
            local.append('descriptive_statement_is_not_an_instruction')
        if claim.force == 'prohibited' and claim.predicate != 'PROCEDURE':
            local.append('prohibition_must_be_a_procedure')
        for eid in claim.scope.product_ids:
            if eid not in entities or entities[eid].kind != 'Product':
                local.append('invalid_product_scope')
        for eid in claim.scope.process_step_ids:
            if eid not in entities or entities[eid].kind != 'ProcessStep':
                local.append('invalid_process_scope')
        if claim.scope.status == 'resolved' and not claim.scope.product_ids:
            local.append('resolved_scope_without_product')
        refs = set(claim.evidence_refs + claim.scope.evidence_refs)
        check_refs(claim.evidence_refs, cid)
        check_refs(claim.scope.evidence_refs, cid + ':scope')
        nested = [*claim.purposes, *claim.parameters]
        nested += [c for g in claim.condition_groups for c in g.all_of]
        nested += [q for p in claim.parameters for q in p.quantities]
        for part in nested:
            refs.update(part.evidence_refs)
            check_refs(part.evidence_refs, cid + ':nested')
        for group in claim.condition_groups:
            for condition in group.all_of:
                if condition.value_kind != 'decimal':
                    continue
                source = '\n'.join(items[r]['text'] for r in condition.evidence_refs if r in items)
                if not set(decimals(condition.values)) <= numbers(source):
                    local.append(f'condition:{condition.field}:number_not_in_evidence')
                if not unit_present(condition.unit, source):
                    local.append(f'condition:{condition.field}:unit_not_in_evidence')
        parameter_ids = [p.id for p in claim.parameters]
        if len(parameter_ids) != len(set(parameter_ids)):
            local.append('duplicate_parameter_ids')
        if claim.parameters and claim.parameter_logic == 'not_applicable':
            local.append('missing_parameter_logic')
        if not claim.parameters and claim.parameter_logic != 'not_applicable':
            local.append('parameter_logic_without_parameters')
        for param in claim.parameters:
            for quantity in param.quantities:
                source = '\n'.join(items[r]['text'] for r in quantity.evidence_refs if r in items)
                found = numbers(source)
                if not set(decimals(quantity.values)) <= found:
                    local.append(f'{param.id}:quantity_number_not_in_evidence')
                if not unit_present(quantity.unit, source):
                    local.append(f'{param.id}:quantity_unit_not_in_evidence')
                if quantity.denominator:
                    d = quantity.denominator
                    # Implicit unit denominator is supported only by explicit per or slash wording.
                    implicit = Decimal(d.value) == 1 and bool(re.search(r'\bper\b|/', source))
                    if Decimal(d.value) not in found and not implicit:
                        local.append(f'{param.id}:denominator_number_not_in_evidence')
                    if not unit_present(d.unit, source):
                        local.append(f'{param.id}:denominator_unit_not_in_evidence')
        blockers = []
        if claim.disposition == 'quarantine':
            blockers.append('model_quarantine')
        if claim.scope.status == 'unresolved':
            blockers.append('unresolved_scope')
        for iid in claim.issue_ids:
            if iid not in issues:
                local.append('unknown_source_issue')
            elif cid not in issues[iid].affected_claim_ids:
                local.append('inconsistent_issue_link')
            blockers.append(f'candidate_source_issue:{iid}')
        for issue in value.source_issues:
            if cid in issue.affected_claim_ids:
                blockers.append(f'affected_by_source_issue:{issue.id}')
                if issue.id not in claim.issue_ids or claim.disposition != 'quarantine':
                    local.append('source_issue_requires_linked_quarantine')
        for flag in flags:
            if refs.intersection(flag['evidence_refs']):
                blockers.append(f'application_source_flag:{flag["id"]}')
                # This remains blocked even if the candidate conceals the issue.
                if claim.disposition != 'quarantine' or flag['id'] not in claim.issue_ids:
                    local.append('application_source_flag_not_acknowledged')
        if claim.scope.status == 'unresolved' and claim.disposition != 'quarantine':
            local.append('unresolved_scope_requires_quarantine')
        if claim.disposition == 'quarantine' and not claim.issue_ids:
            local.append('quarantine_requires_documented_issue')
        errors.extend(f'{cid}:{e}' for e in local)
        rows.append({
            'claim_id': cid,
            'staging_status': 'invalid' if local else 'quarantined' if blockers else 'pending_manual_review',
            'blockers': sorted(set(blockers)),
            'errors': local,
            'condition_evaluation_without_user_context': None,
            'eligible_for_publication': False,
            'source_items': [items[r] for r in sorted(refs) if r in items],
        })
    # A broken entity, issue or reference invalidates the full batch: no partial silent acceptance.
    if errors:
        for row in rows:
            row['staging_status'] = 'invalid'
    reviewable = [r['claim_id'] for r in rows if r['staging_status'] == 'pending_manual_review']
    quarantine = [r['claim_id'] for r in rows if r['blockers']]
    return {
        'schema_version': '0.2', 'structural_pass': not errors,
        'candidate_status': 'invalid' if errors else 'empty_candidate' if not rows else 'staged_for_review',
        'errors': errors, 'claims': rows, 'review_queue_ids': reviewable,
        'quarantine_ids': quarantine, 'publication_allowed': False,
        'semantic_validation': 'not_performed', 'human_approval': False,
        'quantity_check_limit': 'Numbers and unit mentions only; association, comparators, missing values and meaning still need documentary review.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new report file; never overwrite a review or candidate')
    if args.output.resolve() in (args.candidate.resolve(), args.corpus.resolve()):
        parser.error('Output must be a separate file')
    if args.corpus.name != 'input.json':
        parser.error('Use the frozen input.json listed in the test manifest')
    try:
        from ingestion.claim_bundle import verify_bundle
        verify_bundle(args.corpus.parent)
        report = validate_candidate(
            json.loads(args.candidate.read_text(encoding='utf-8-sig')),
            json.loads(args.corpus.read_text(encoding='utf-8-sig')),
        )
    except ValueError as exc:
        report = {'structural_pass': False, 'candidate_status': 'invalid',
                  'errors': [str(exc)], 'publication_allowed': False, 'human_approval': False}
    with args.output.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'claims'}, ensure_ascii=False))
    raise SystemExit(0 if report['structural_pass'] else 1)


if __name__ == '__main__':
    main()
