"""Opt-in candidate v02; versioned snapshot preserving the frozen v01 bridge.

No serving endpoint is activated. Use FreeTextControlV02.evaluate({language, text}).
evaluate_ledger is an internal boundary for reviewed preclassified test fixtures;
it is intentionally not selectable through the public caller envelope.
"""
from copy import deepcopy
import re
from time import perf_counter
from uuid import uuid4

from ingestion.free_text_contract import (
    Contracts, FreeTextValidationError, LedgerBuilder, VERSION, canonical_hash,
    leaves, na, resolve, slot,
)
from ingestion.free_text_interpreter_v02 import DeterministicInterpreter, MappedText, instruction_spans
from ingestion.structured_request import StructuredControl, pointer
from ingestion.structured_sources import ROOT, compact


class FreeTextControlV02:
    def __init__(self, root=ROOT, *, core=None):
        self.core=core if core is not None else StructuredControl(root)
        self.contracts=Contracts(root)
        self.identity=self.contracts.identities(self.core)
        # Bind the snapshot and its inherited/shared dependencies separately
        # from v01; ledgers cannot be silently replayed across candidates.
        from ingestion.free_text_contract import digest
        for component, path in (
            ('interpreter', 'ingestion/free_text_interpreter_v02.py'),
            ('bridge', 'ingestion/free_text_bridge_v02.py'),
        ):
            self.identity[component] = {
                'status': 'pinned',
                'sha256_lf': canonical_hash({
                    'candidate': 'free-text-v02',
                    'base_component': self.identity[component]['sha256_lf'],
                    'component_sha256_lf': digest(self.contracts.root / path),
                }),
            }
        self.interpreter=DeterministicInterpreter(self.core,self.contracts)

    def evaluate(self, envelope):
        request_id='ft-'+uuid4().hex;start=perf_counter()
        try:
            ledger=self.interpreter.interpret(envelope,request_id,self.identity)
        except (FreeTextValidationError, UnicodeError, TypeError, ValueError) as exc:
            return self._rejected(request_id,start,'input','invalid_input',type(exc).__name__)
        return self._run(ledger,start,(perf_counter()-start)*1000)

    def evaluate_ledger(self, ledger):
        """Internal already-classified boundary; never accept it as caller input."""
        start=perf_counter();snapshot=deepcopy(ledger)
        request_id=snapshot.get('request_id','ft-'+uuid4().hex)
        try:self.contracts.check_ledger(snapshot,self.identity)
        except (FreeTextValidationError, KeyError, TypeError, ValueError, UnicodeError):
            return self._rejected(request_id,start,'interpretation','invalid_ledger','Invalid ledger references, origins or component identity.')
        return self._run(snapshot,start,None)

    def _rejected(self, request_id, start, stage, code, detail):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]{0,63}',str(request_id)):request_id='ft-'+uuid4().hex
        out=self._base(request_id,None)
        out['failure']={'stage':stage,'code':code,'detail':detail}
        out['request_summary']=self._summary(None,[],out['failure'])
        out['timings']['total_ms']=(perf_counter()-start)*1000
        self.contracts.validate('outcome',out);return out

    @staticmethod
    def _base(request_id,ledger):
        return {'document_kind':'free_text_bridge_outcome','interface_version':VERSION,'record_status':'runtime_record',
                'request_id':request_id,'interpretation_ledger':ledger,
                'projection':{'status':'not_built','submission':None,'sha256_canonical':None,'reason':'No projection reached.'},
                'projection_mapping':[],'core_result':None,'core_result_sha256_canonical':None,'core_calls':0,
                'unit_outcomes':[],'request_summary':{},'failure':None,'rejection_audit':None,
                'timings':{'interpretation_ms':None,'projection_ms':None,'core_ms':None,'total_ms':None}}

    def _project(self, ledger):
        """Return a candidate without validation; caller must validate before dispatch."""
        b=LedgerBuilder(ledger['input_snapshot'],ledger['request_id'],self.identity);b.value=ledger
        submission={'document_kind':'structured_submission','contract_version':self.core.schema['$defs']['submission']['properties']['contract_version']['const'],
                    'input_mode':'structured','language':ledger['input_snapshot']['language'],'tasks':[]}
        mapping=[]
        def metadata(reason):return [b.origin(rule='projection-shape',reason=reason)]
        def field(value,path,origins):b.fields(value,path,origins,'projection_submission')
        def source_origins(path):
            found=[o for f in ledger['field_origins'] if f['target_document']=='ledger' and (f['target_pointer']==path or f['target_pointer'].startswith(path+'/')) for o in f['origin_ids']]
            if not found:raise FreeTextValidationError('No justified ledger origin for '+path)
            return list(dict.fromkeys(found))
        for li,task in enumerate(ledger['tasks']):
            units=[u for u in ledger['requested_units'] if u['dispatch']=='project' and u['owner']['task_id']==task['task_id']]
            if not units:continue
            ti=len(submission['tasks']);tp=f'/tasks/{ti}'
            general=all(u['stage']['kind']=='general_topic' and u['information']=='principle' for u in units)
            target={'task_id':task['task_id'],'sample_ref':None,
                    'intent':'mechanism_explanation' if general else 'documentary_procedure_lookup',
                    'product':deepcopy(task['product']),'column':deepcopy(task['column']),
                    'facts':deepcopy(task['facts']),'items':[],'exclusions':[]}
            for key in ('product','column','facts'):
                if target[key]:field(target[key],tp+'/'+key,source_origins(f'/tasks/{li}/{key}'))
            for key in ('task_id','sample_ref','intent'):field(target[key],tp+'/'+key,metadata('Generated projection '+key+'; documentary selector policy.'))
            groups={}
            for u in units:
                item_id=u['item_id']
                if item_id not in groups:
                    ii=len(target['items']);ip=tp+f'/items/{ii}';stage=deepcopy(u['stage'])
                    item={'item_id':item_id,'stage':stage,'information':[], 'answer_mode':'single_context',
                          'techniques':na(),'facets':{'buffer_use':na(),'elution_mode':na(),'syringe_query_mode':na()}}
                    # Facets require explicit focused source text; never derive them from an exclusion.
                    origins={o['origin_id']:o for o in ledger['origins']}
                    text=ledger['input_snapshot']['text']
                    spans=[origins[i] for i in u['origin_ids'] if origins[i]['kind']=='text_span']
                    loc=min((o['start'] for o in spans),default=0)
                    # Use the unit's actual selector occurrence, not the earlier task scope.
                    req=[a for a in ledger['assertions'] if a['assertion_id'] in u['assertion_ids'] and a['role']=='requested_information']
                    if req:
                        ao=origins[req[0]['origin_ids'][0]];loc=ao.get('start',loc)
                    mapped=MappedText(text)
                    bounds=[mapped.span(a,z) for a,z in instruction_spans(mapped.text)]
                    left,right=next(((a,z) for a,z in bounds if a<=loc<z),(0,len(text)))
                    segment=MappedText(text[left:right])
                    if stage['code']=='buffer_preparation':
                        candidates=list(re.finditer(r'\b(binding|fixation|liaison|elution)\b',segment.text))
                        uses={('binding' if m.group()!='elution' else 'elution') for m in candidates}
                        if len(uses)==1:
                            use=next(iter(uses));item['facets']['buffer_use']=slot(use)
                            match=candidates[0];a,z=segment.span(*match.span());oid=b.origin(left+a,left+z)
                            field(item['facets']['buffer_use'],ip+'/facets/buffer_use',[oid])
                        else:
                            item['facets']['buffer_use']=slot()
                    if stage['kind']=='general_topic' and u['information']=='principle':
                        found=[]
                        for label in self.core.adapter.catalog.methods:
                            for match in re.finditer(r'(?<!\w)'+re.escape(MappedText(label).text)+r'(?!\w)',segment.text):
                                found.append((match,label))
                        # Same canonical method may have overlapping aliases. Choose longest
                        # non-overlapping spelling, without selecting a different entity.
                        refs={self.core.adapter.catalog.resolve(label,'technique')['refs'][0] for _,label in found}
                        if len(refs)==1:
                            match,label=max(found,key=lambda p:len(p[1]));a,z=segment.span(*match.span());oid=b.origin(left+a,left+z)
                            item['techniques']=slot([text[left+a:left+z]])
                            field(item['techniques'],ip+'/techniques',[oid])
                        else:item['techniques']=slot()
                    field(item['stage'],ip+'/stage',u['origin_ids'])
                    for key in ('item_id','answer_mode'):field(item[key],ip+'/'+key,metadata('Generated item identity or single-context answer mode.'))
                    existing={f['target_pointer'] for f in ledger['field_origins'] if f['target_document']=='projection_submission'}
                    for key in ('techniques','facets'):
                        for suffix,val in leaves(item[key]):
                            p=ip+'/'+key+suffix
                            if p not in existing:
                                oid=b.origin(rule='selector-facet-default',reason=p+': not required for this selector or not explicitly supplied.') if val is None or 'not_applicable' in str(item[key]) else b.origin(rule='selector-facet-default',reason=p+': application-side facet slot state.')
                                field(val,p,[oid])
                    target['items'].append(item);groups[item_id]=(ii,item)
                ii,item=groups[item_id]
                if item['stage']!=u['stage']:raise FreeTextValidationError('Conflicting stages on the same item')
                if u['information'] in item['information']:raise FreeTextValidationError('Repeated selector occurrence cannot collapse silently')
                ni=len(item['information']);item['information'].append(u['information'])
                loc=tp+f'/items/{ii}/information/{ni}';field(u['information'],loc,u['origin_ids'])
                mapping.append({'unit_id':u['unit_id'],'core_task_id':task['task_id'],'core_item_id':item_id,
                                'information':u['information'],'projection_pointer':loc})
            surviving=set(groups)
            for x in ledger['exclusions']:
                if not x['active'] or x['task_id']!=task['task_id']:continue
                if x['selector'] is None:raise FreeTextValidationError('Unrepresentable active restriction')
                targets=x['target_item_ids']
                for iid in targets if targets else [None]:
                    if iid is not None and iid not in surviving:continue
                    exclusion={'exclusion_id':x['exclusion_id']+(('-'+str(len(target['exclusions']))) if len(targets)>1 else ''),
                               'scope':{'task_id':task['task_id']},'selector':deepcopy(x['selector'])}
                    if iid is not None:exclusion['scope']['item_id']=iid
                    ei=len(target['exclusions']);target['exclusions'].append(exclusion)
                    field(exclusion,tp+f'/exclusions/{ei}',x['origin_ids'])
            submission['tasks'].append(target)
        for key in ('document_kind','contract_version','input_mode'):field(submission[key],'/'+key,metadata('Unchanged structured submission envelope.'))
        oid=b.origin(rule='caller-language',reason='Language copied from validated caller envelope.')
        ledger['origins'][-1]['input_envelope_pointer']='/language';field(submission['language'],'/language',[oid])
        return submission,mapping

    def _check_projection(self, ledger, candidate, mapping):
        self.contracts.check_ledger(ledger,self.identity)
        if not candidate['tasks']:
            if mapping or any(u['dispatch']=='project' for u in ledger['requested_units']):
                raise FreeTextValidationError('Empty projection with dispatchable units')
            return True
        self.contracts.validate('submission',candidate)
        if candidate['language']!=ledger['input_snapshot']['language']:
            raise FreeTextValidationError('Projection language changed')
        expected_tasks=[t for t in ledger['tasks'] if any(u['dispatch']=='project' and u['owner']['task_id']==t['task_id'] for u in ledger['requested_units'])]
        if [t['task_id'] for t in candidate['tasks']]!=[t['task_id'] for t in expected_tasks]:
            raise FreeTextValidationError('Projection task inventory/order changed')
        for target,source in zip(candidate['tasks'],expected_tasks):
            if any(target[k]!=source[k] for k in ('product','column','facts')):
                raise FreeTextValidationError('Projection context changed from the ledger')
            units=[u for u in ledger['requested_units'] if u['dispatch']=='project' and u['owner']['task_id']==source['task_id']]
            item_ids=list(dict.fromkeys(u['item_id'] for u in units))
            if [i['item_id'] for i in target['items']]!=item_ids:
                raise FreeTextValidationError('Projection item inventory/order changed')
            for item in target['items']:
                item_units=[u for u in units if u['item_id']==item['item_id']]
                if item['information']!=[u['information'] for u in item_units] or any(item['stage']!=u['stage'] for u in item_units):
                    raise FreeTextValidationError('Projection phase/selectors changed')
            expected_exclusions=[]
            for x in ledger['exclusions']:
                if not x['active'] or x['task_id']!=source['task_id']:continue
                if x['selector'] is None:
                    raise FreeTextValidationError('Unrepresentable restriction on projected task')
                for iid in x['target_item_ids'] or [None]:
                    if iid is not None and iid not in item_ids:continue
                    e={'exclusion_id':x['exclusion_id']+('-'+str(len(expected_exclusions)) if len(x['target_item_ids'])>1 else ''),
                       'scope':{'task_id':source['task_id']},'selector':x['selector']}
                    if iid is not None:e['scope']['item_id']=iid
                    expected_exclusions.append(e)
            if target['exclusions']!=expected_exclusions:
                raise FreeTextValidationError('Projection exclusions were changed, removed or widened')
        # All generated leaves require resolving, non-empty provenance; references
        # alone are not substantive proof (human entailment remains separate).
        linked={f['target_pointer']:f['origin_ids'] for f in ledger['field_origins'] if f['target_document']=='projection_submission'}
        for loc,_ in leaves(candidate):
            if loc not in linked:raise FreeTextValidationError('Projection field without origin: '+loc)
        for loc in linked:resolve(candidate,loc)
        projected={u['unit_id']:u for u in ledger['requested_units'] if u['dispatch']=='project'}
        if len(mapping)!=len(projected) or {m['unit_id'] for m in mapping}!=set(projected):
            raise FreeTextValidationError('Projection mapping inventory mismatch')
        for m in mapping:
            u=projected[m['unit_id']];parts=m['projection_pointer'].split('/')
            task=candidate['tasks'][int(parts[2])];item=task['items'][int(parts[4])]
            if (task['task_id'],item['item_id'],resolve(candidate,m['projection_pointer']))!=(u['owner']['task_id'],u['item_id'],u['information']):
                raise FreeTextValidationError('Projection owner/item/information mismatch')
        return True

    def _run(self, ledger, start, interpretation_ms):
        out=self._base(ledger['request_id'],ledger);out['timings']['interpretation_ms']=interpretation_ms
        stage_start=perf_counter();candidate=None
        try:
            self.contracts.check_ledger(ledger,self.identity)
            candidate,mapping=self._project(ledger)
            self._check_projection(ledger,candidate,mapping)
            out['projection_mapping']=mapping
            if candidate['tasks']:
                out['projection']={'status':'available','submission':deepcopy(candidate),'sha256_canonical':canonical_hash(candidate)}
            else:out['projection']={'status':'empty','submission':None,'sha256_canonical':None,'reason':'No faithfully dispatchable task; no dummy task is submitted.'}
        except (FreeTextValidationError,KeyError,TypeError,ValueError) as exc:
            out['projection']={'status':'invalid','submission':None,'sha256_canonical':None,'reason':'Projection rejected before planner invocation.'}
            out['failure']={'stage':'projection','code':'projection_error','detail':type(exc).__name__}
            errors=list(self.contracts.validators['submission'].iter_errors(candidate)) if candidate is not None else []
            if candidate is not None:
                out['rejection_audit']={'candidate_value':deepcopy(candidate),'candidate_sha256_canonical':canonical_hash(candidate),
                    'validation_errors':[{'pointer':pointer(e.absolute_path),'code':e.validator,'detail':e.message} for e in errors[:8]] or [{'pointer':'','code':'semantic_projection_error','detail':str(exc)}]}
        out['timings']['projection_ms']=(perf_counter()-stage_start)*1000
        if out['projection']['status']=='available':
            core_start=perf_counter();out['core_calls']=1
            try:
                result=self.core.evaluate(deepcopy(candidate),request_id=ledger['request_id'])
                # Validate without changing anything returned by the core.
                self.core.validate(result['canonical_request'],'canonical_request');self.core.validate(result['plan'],'plan_result')
                if result['canonical_request']['input_snapshot']!=candidate:raise FreeTextValidationError('Core input snapshot mismatch')
                expected={(m['core_task_id'],m['core_item_id'],m['information']) for m in out['projection_mapping']}
                actual=[(u['task_id'],u['item_id'],u['information']) for u in result['plan']['units']]
                if len(actual)!=len(expected) or set(actual)!=expected:
                    raise FreeTextValidationError('Core result does not account for projected units')
                if any(p['id'] in self.core.adapter.excluded for p in result['plan']['context']['source_passages']):
                    raise FreeTextValidationError('Core context contains an excluded source')
                out['core_result']=result;out['core_result_sha256_canonical']=canonical_hash(result)
            except Exception as exc:
                out['failure']={'stage':'runtime','code':'runtime_error','detail':type(exc).__name__}
            finally:out['timings']['core_ms']=(perf_counter()-core_start)*1000
        units=ledger['requested_units'];result=out['core_result']
        by_key={(u['task_id'],u['item_id'],u['information']):u for u in result['plan']['units']} if result else {}
        mappings={m['unit_id']:m for m in out['projection_mapping']}
        for u in units:
            row={'unit_id':u['unit_id'],'issue_ids':list(u['issue_ids']),'core_unit_key':None,'binding_index':None,'source_ids':[]}
            if u['dispatch']=='preblock':
                row.update(status='preblocked',interpretation_state='needs_clarification',documentary_support_state='not_assessed_by_planner',summary_state='preblocked')
            elif result:
                m=mappings[u['unit_id']];key=(m['core_task_id'],m['core_item_id'],m['information']);actual=by_key[key]
                bindings=result['plan']['context']['bindings'];bi=next((i for i,b in enumerate(bindings) if (b['task_id'],b['item_id'],b['information'])==key),None)
                row.update(status='planner_evaluated',core_unit_key=dict(zip(('task_id','item_id','information'),key)),binding_index=bi,
                           source_ids=list(actual['source_ids']),interpretation_state=actual['interpretation_state'],documentary_support_state=actual['documentary_support_state'],summary_state=actual['state'])
            else:row.update(status='not_evaluated_due_to_error',interpretation_state='not_assessed_due_to_error',documentary_support_state='not_assessed_by_planner',summary_state='error')
            out['unit_outcomes'].append(row)
        out['request_summary']=self._summary(ledger,out['unit_outcomes'],out['failure'])
        out['timings']['total_ms']=(perf_counter()-start)*1000
        self.contracts.validate('outcome',out)
        return out

    @staticmethod
    def _summary(ledger,rows,failure):
        inventory=ledger['inventory_complete'] if ledger else False
        known=len(ledger['requested_units']) if ledger else 0
        evaluated=sum(r['status']=='planner_evaluated' for r in rows);preblocked=sum(r['status']=='preblocked' for r in rows);errors=sum(r['status']=='not_evaluated_due_to_error' for r in rows)
        served=bool(known) and all(r['summary_state']=='supported' for r in rows) and len(rows)==known and inventory and not failure
        status='error' if failure and ledger else 'rejected' if failure else 'incomplete_inventory' if not inventory else 'complete' if served else 'blocked' if preblocked==known else 'partial'
        core_issues=any(r['status']=='planner_evaluated' and r['interpretation_state']!='ready' for r in rows)
        return {'inventory_complete':inventory,'known_unit_count':known,'evaluated_count':evaluated,'preblocked_count':preblocked,'error_count':errors,
                'all_known_units_accounted_for':len(rows)==known,'any_unit_unserved':not served,'has_interpretation_issues':bool(ledger and ledger['issues']) or core_issues,
                'full_service':served,'status':status}


def projection_bytes(outcome):
    """Canonical exact submitted JSON bytes; matches projection.sha256_canonical."""
    if outcome['projection']['status']!='available':return None
    return compact(outcome['projection']['submission'],sort_keys=True).encode('utf-8')


def record_sizes(outcome):
    """Separate metadata accounting; these are byte sizes, never token estimates."""
    ledger=outcome['interpretation_ledger']
    return {'ledger_utf8_bytes':len(compact(ledger).encode('utf-8')) if ledger else 0,
            'projection_utf8_bytes':len(projection_bytes(outcome) or b''),
            'complete_record_utf8_bytes':len(compact(outcome).encode('utf-8'))}
