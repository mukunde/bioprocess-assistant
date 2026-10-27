"""Versioned coverage of validated unit evidence; no retrieval or inference."""
from collections import Counter
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from ingestion.structured_sources import ROOT, read


def summarize(known_keys, outcome_keys, *, supported_keys=(), eligible_keys=None,
              covered_keys=(), inventory_complete=True, assessment_complete=True,
              has_assessment_error=False):
    """Counts keep occurrence identity and never filter the request denominator.

    Evidence producers must validate provenance, bindings and eligibility first.
    No caller-provided flag, legacy aggregate or language guess is used here.
    """
    known=list(known_keys);outcomes=list(outcome_keys)
    requested=Counter(known);reported=Counter(outcomes);unique=set(requested)
    accounted={k for k in unique if requested[k]==reported[k]==1}
    exact=(len(unique)==len(known) and set(reported)==unique and
           all(v==1 for v in reported.values()) and len(accounted)==len(known))
    error=bool(has_assessment_error or not exact)
    support_input=set(supported_keys);covered_input=set(covered_keys)
    supported=support_input&accounted
    if support_input-accounted:error=True
    if eligible_keys is None:
        eligible=covered=None
        if covered_input:error=True
    else:
        eligible=set(eligible_keys);covered=covered_input
        # A supported unit necessarily has admitted eligible context. Do not
        # accept a second, unsupported set of success claims in the summary.
        if not covered<=eligible<=unique or covered!=supported:
            raise ValueError('Supported units must equal valid covered eligible units')
    assessed=bool(assessment_complete and eligible is not None)
    whole=bool(inventory_complete and exact and assessed and not error)
    scope='complete_request' if whole else 'known_units_only' if eligible is not None else 'unassessed'
    state=('error' if error else 'not_assessed' if not whole else 'not_applicable'
           if not eligible else 'complete' if covered==eligible else 'partial')
    full=bool(known) and whole and len(supported)==len(known) and state=='complete'
    return {'document_kind':'request_coverage_summary','contract_version':'coverage-0.3-proposed',
            'inventory_complete':bool(inventory_complete),'known_requested_units':len(known),
            'accounted_units':len(accounted),'all_known_units_accounted_for':exact,
            'assessment_complete':assessed,'has_assessment_error':error,
            'eligible_ready_context_coverage':{'state':state,'scope':scope,
                'eligible_ready_units':len(eligible) if eligible is not None else None,
                'covered_units':len(covered) if covered is not None else None},
            'request_support':{'supported_units':len(supported),'known_requested_units':len(known),
                               'all_requested_units_supported':full},
            'has_unserved_known_units':len(supported)<len(known),'full_service':full}


def validate_summary(summary, root=ROOT):
    """Validate the public encoding and cross-field invariants, not just shape."""
    Draft202012Validator(read(root/'docs/technical/coverage-summary-v03.schema.json')).validate(summary)
    k=summary['known_requested_units'];a=summary['accounted_units'];s=summary['request_support']['supported_units']
    cov=summary['eligible_ready_context_coverage'];e=cov['eligible_ready_units'];c=cov['covered_units']
    if not 0<=s<=a<=k or summary['request_support']['known_requested_units']!=k:
        raise ValueError('Invalid unit accounting')
    if (e is None)!=(c is None) or e is not None and not (0<=c<=e<=k and c==s):
        raise ValueError('Invalid eligible coverage')
    if summary['all_known_units_accounted_for'] and a!=k:raise ValueError('Incomplete accounting')
    if not summary['all_known_units_accounted_for'] and not summary['has_assessment_error']:
        raise ValueError('Accounting failure must remain an error')
    whole=(summary['inventory_complete'] and summary['all_known_units_accounted_for'] and
           summary['assessment_complete'] and not summary['has_assessment_error'])
    scope='complete_request' if whole else 'known_units_only' if e is not None else 'unassessed'
    state=('error' if summary['has_assessment_error'] else 'not_assessed' if not whole else
           'not_applicable' if e==0 else 'complete' if c==e else 'partial')
    if whole and e is None or cov['state']!=state or cov['scope']!=scope:
        raise ValueError('Coverage state/scope inconsistent with assessment')
    full=bool(k) and whole and s==k and state=='complete'
    if summary['full_service']!=full or summary['request_support']['all_requested_units_supported']!=full:
        raise ValueError('Whole-request service contradicts coverage')
    if summary['has_unserved_known_units']!=(s<k):raise ValueError('Unserved count mismatch')
    return summary


def validate_envelope(outcome, root=ROOT):
    coverage=read(root/'docs/technical/coverage-summary-v03.schema.json')
    schema=read(root/'docs/technical/control-v03-outcome.schema.json')
    registry=Registry().with_resources([(coverage['$id'],Resource.from_contents(coverage))])
    Draft202012Validator(schema,registry=registry).validate(outcome)
    validate_summary(outcome['coverage_summary'],root)
    return outcome
