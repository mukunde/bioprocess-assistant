"""Opt-in coverage boundary around the unchanged structured planner.

Pre-assembly eligibility is captured per call, not stored on an instance or
reconstructed from final supported states. Compatibility flags keep old semantics.
"""
from copy import deepcopy
import hashlib

from ingestion.coverage_v03 import summarize, validate_summary, validate_envelope
from ingestion.structured_request import StructuredControl
from ingestion.structured_sources import ROOT, SOURCE_FIELDS, compact, digest


def key(row):return (row['task_id'],row['item_id'],row['information'])


def system_identity(root, *, free_text=False):
    files=['ingestion/coverage_v03.py','ingestion/structured_request_v03.py',
           'ingestion/structured_request.py','ingestion/structured_sources.py',
           'ingestion/free_text_contract.py','docs/technical/coverage-summary-v03.schema.json',
           'docs/technical/control-v03-outcome.schema.json']
    if free_text:files+=['ingestion/free_text_interpreter_v03.py','ingestion/free_text_bridge_v03.py']
    return {'candidate':'v03','sha256_lf':hashlib.sha256(compact(
        {n:digest(root/n) for n in files},sort_keys=True).encode('utf-8')).hexdigest()}


class CoverageStructuredCore(StructuredControl):
    """Internal compatibility API used by the v03 bridge, one planner call."""
    def _assemble(self, units, count_tokens, request_id):
        basis={'known_keys':[],'eligible_keys':[],'assessment_complete':True,'admissible':[]}
        for u in units:
            identity=key(u.result);basis['known_keys'].append(list(identity))
            basis['assessment_complete'] &= u.result['documentary_support_state']!='not_assessed'
            if not u.blocked and u.result['interpretation_state']=='ready' and u.result['documentary_support_state']=='eligible':
                basis['eligible_keys'].append(list(identity))
                basis['admissible'].append({'key':list(identity),'candidates':[
                    {'binding':deepcopy(self._binding(u,c)),
                     'direct_support_ids':list(c['direct_support_source_ids']),
                     'root_ids':list(c['root_source_ids'])} for c in u.candidates]})
        plan,audit=super()._assemble(units,count_tokens,request_id)
        audit['coverage_basis_v03']=basis
        return plan,audit

    def validate_context(self, result):
        """Source and exact semantic binding checks against pre-assembly evidence."""
        plan=result['plan'];context=plan['context'];basis=result['audit']['coverage_basis_v03']
        self.validate(result['canonical_request'],'canonical_request');self.validate(plan,'plan_result')
        canonical=result['canonical_request'];audit=result['audit']
        input_hash=hashlib.sha256(compact(canonical['input_snapshot'],sort_keys=True).encode('utf-8')).hexdigest()
        if canonical['submission']!=canonical['input_snapshot'] or canonical['input_sha256']!=input_hash or audit['input_sha256']!=input_hash:
            raise ValueError('Input provenance changed')
        if canonical['system_versions']!=self.adapter.versions or audit['system_versions']!=self.adapter.versions:
            raise ValueError('Source versions changed')
        if canonical['request_id']!=plan['request_id']:raise ValueError('Request identity changed')
        wanted=[(t['task_id'],i['item_id'],info) for t in result['canonical_request']['input_snapshot']['tasks']
                for i in t['items'] for info in i['information']]
        if [tuple(k) for k in basis['known_keys']]!=wanted:raise ValueError('Eligibility inventory changed')
        actual=[key(u) for u in plan['units']]
        if len(actual)!=len(set(actual)) or set(actual)!=set(wanted):raise ValueError('Unit mapping changed')
        ids=[p['id'] for p in context['source_passages']]
        if len(ids)!=len(set(ids)) or not set(ids)<=self.adapter.eligible:raise ValueError('Ineligible or duplicate source')
        for passage in context['source_passages']:
            if passage!={k:self.adapter.passages[passage['id']][k] for k in SOURCE_FIELDS}:
                raise ValueError('Source provenance changed')
        roots=plan['selected_root_ids']
        policy=self.adapter.config['execution_policy']
        if len(roots)!=len(set(roots)) or len(roots)>min(6,policy['max_selected_distinct_roots']) or not set(roots)<=set(ids):raise ValueError('Invalid roots')
        tokens=self._count_tokens(compact(context))
        if tokens!=plan['context_tokens'] or tokens>min(2048,policy['max_serialized_context_tokens']):raise ValueError('Invalid context token accounting')
        if hashlib.sha256(compact(context).encode('utf-8')).hexdigest()!=result['audit']['context_sha256']:
            raise ValueError('Context audit mismatch')
        admissible={tuple(r['key']):r['candidates'] for r in basis['admissible']}
        bindings=context['bindings'];bound=[key(b) for b in bindings]
        if len(bound)!=len(set(bound)):raise ValueError('Duplicate binding')
        used=set();used_roots=set();supported=set()
        for unit in plan['units']:
            identity=key(unit);matches=[b for b in bindings if key(b)==identity]
            if unit['state']!='supported':
                if matches or unit['source_ids']:raise ValueError('Binding assigned to unserved unit')
                continue
            if len(matches)!=1:raise ValueError('Missing binding for supported unit')
            binding=matches[0]
            valid=[c for c in admissible.get(identity,[]) if c['binding']==binding and
                   set(c['direct_support_ids'])==set(unit['source_ids']) and
                   set(c['root_ids'])<=set(roots)]
            if not valid or not set(binding['source_ids'])<=set(ids):raise ValueError('Invalid unit support bundle')
            used_roots.update(valid[0]['root_ids'])
            used.update(binding['source_ids']);supported.add(identity)
        if used!=set(ids) or set(bound)!=supported:raise ValueError('Orphan context or binding')
        if used_roots!=set(roots):raise ValueError('Orphan selected root')
        return supported

    def coverage_for(self, result):
        basis=result['audit']['coverage_basis_v03'];known=[tuple(k) for k in basis['known_keys']]
        supported=self.validate_context(result)
        eligible={tuple(k) for k in basis['eligible_keys']}
        if not basis['assessment_complete'] and not eligible:eligible=None
        summary=summarize(known,[key(u) for u in result['plan']['units']],supported_keys=supported,
                          eligible_keys=eligible,covered_keys=supported,
                          assessment_complete=basis['assessment_complete'])
        return validate_summary(summary,self.adapter.root)


class StructuredControlV03:
    """Public versioned envelope; legacy payload is never relabelled as v03."""
    def __init__(self, root=ROOT, *, core=None):
        self.core=core if core is not None else CoverageStructuredCore(root)
        self.root=self.core.adapter.root

    def evaluate(self, submission, request_id='structured-v03'):
        result=None;failure=None;known=[];unit_errors=[]
        try:
            self.core.validate(submission)
            expected_snapshot=deepcopy(submission)
            known=[(t['task_id'],i['item_id'],info) for t in submission['tasks'] for i in t['items'] for info in i['information']]
            result=self.core.evaluate(deepcopy(expected_snapshot),request_id=request_id)
            if result['canonical_request']['input_snapshot']!=expected_snapshot:
                raise ValueError('Core evaluated a different input')
            coverage=self.core.coverage_for(result)
        except Exception as exc:
            failure={'code':'assessment_error','type':type(exc).__name__}
            unit_errors=[{'task_id':k[0],'item_id':k[1],'information':k[2],
                          'state':'assessment_error','code':failure['code']} for k in known]
            outcomes=[key(u) for u in unit_errors]
            coverage=validate_summary(summarize(known,outcomes,eligible_keys=None,
                inventory_complete=bool(known),assessment_complete=False,has_assessment_error=True),self.root)
        return validate_envelope({'document_kind':'structured_control_v03_outcome','interface_version':'control-v03',
                'system_identity':system_identity(self.root),'compatibility_result':result,
                'coverage_summary':coverage,'failure':failure,'unit_errors':unit_errors},self.root)
