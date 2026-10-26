"""Offline schema registry and cross-record invariants for the EN/FR bridge."""
from copy import deepcopy
from decimal import Decimal
import hashlib
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from ingestion.structured_request import pointer
from ingestion.structured_sources import ROOT, compact, digest, read, normalize_label

VERSION = 'free-text-interface-0.1-draft'
POLICY = Path('docs/technical/free-text-runtime-policy-v01.json')


def canonical_hash(value):
    return hashlib.sha256(compact(value, sort_keys=True).encode('utf-8')).hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8', errors='strict')).hexdigest()


def resolve(value, loc):
    for part in loc.split('/')[1:]:
        key = part.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def leaves(value, parts=()):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from leaves(v, (*parts, k))
    elif isinstance(value, list):
        for k, v in enumerate(value):
            yield from leaves(v, (*parts, k))
    else:
        yield pointer(parts), value


class FreeTextValidationError(ValueError):
    pass


class Contracts:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        names = ('task-request', 'free-text-input', 'free-text-interpretation', 'free-text-outcome')
        self.docs = [read(self.root/'docs/technical'/f'{n}-v01.schema.json') for n in names]
        registry = Registry().with_resources((d['$id'], Resource.from_contents(d)) for d in self.docs)
        self.validators = {}
        for n, d in zip(('submission', 'input', 'ledger', 'outcome'), self.docs):
            Draft202012Validator.check_schema(d)
            self.validators[n] = Draft202012Validator(d, registry=registry)

    def validate(self, kind, value):
        errors = list(self.validators[kind].iter_errors(value))
        if errors:
            raise FreeTextValidationError('; '.join(pointer(e.absolute_path)+': '+e.message for e in errors[:5]))

    def identities(self, core):
        versions = core.adapter.versions
        files = {'interpreter': 'ingestion/free_text_interpreter.py',
                 'bridge': 'ingestion/free_text_bridge.py', 'policy': POLICY.as_posix()}
        hashes = {'schema': canonical_hash([digest(self.root/'docs/technical'/f'{n}-v01.schema.json')
                                           for n in ('task-request', 'free-text-input', 'free-text-interpretation', 'free-text-outcome')]),
                  'catalog': versions['catalog_sha256_lf'], 'adapter': versions['adapter_sha256_lf'],
                  'source_review': versions['corpus_manifest_sha256_lf']}
        hashes.update({k: digest(self.root/p) for k, p in files.items()})
        # Shared validation code is part of both executable component identities.
        shared=digest(self.root/'ingestion/free_text_contract.py')
        for key in ('interpreter','bridge'):
            hashes[key]=canonical_hash({'component':hashes[key],'shared_contract':shared})
        return {k: {'status': 'pinned', 'sha256_lf': v} for k, v in hashes.items()}

    def check_ledger(self, ledger, identity):
        self.validate('ledger', ledger)
        if ledger['system_identity'] != identity:
            raise FreeTextValidationError('Component identity mismatch')
        text = ledger['input_snapshot']['text']; h = text_hash(text)
        if h != ledger['input_sha256_utf8']:
            raise FreeTextValidationError('Input UTF-8 digest mismatch')
        indexes = {}
        for table, key in (('origins','origin_id'), ('assertions','assertion_id'), ('tasks','task_id'),
                           ('requested_units','unit_id'), ('issues','issue_id'),
                           ('exclusions','exclusion_id'), ('unresolved_fragments','fragment_id')):
            rows = ledger[table]; indexes[table] = {r[key]: r for r in rows}
            if len(indexes[table]) != len(rows):
                raise FreeTextValidationError('Duplicate '+key)
        def refs(ids, table):
            if not set(ids) <= set(indexes[table]):
                raise FreeTextValidationError('Unresolved '+table+' reference')
        for o in ledger['origins']:
            if o['input_sha256_utf8'] != h:
                raise FreeTextValidationError('Origin hash mismatch')
            if o['kind'] == 'text_span' and not (0 <= o['start'] < o['end'] <= len(text) and text[o['start']:o['end']] == o['quote']):
                raise FreeTextValidationError('Origin interval/quote mismatch')
            if o['kind'] == 'not_stated':
                refs(o['checked_scope_origin_ids'], 'origins')
                if not o['reason'].startswith('/'):
                    raise FreeTextValidationError('Absence origin must name its field')
        for row in ledger['field_origins']:
            refs(row['origin_ids'], 'origins')
            if row['target_document'] == 'ledger':
                resolve(ledger, row['target_pointer'])
        for a in ledger['assertions']:
            refs(a['origin_ids'], 'origins'); refs(a['subject_candidates'], 'tasks')
            spans = [indexes['origins'][i]['quote'] for i in a['origin_ids'] if indexes['origins'][i]['kind']=='text_span']
            if a['raw_lexeme'] not in spans:
                raise FreeTextValidationError('Assertion literal has no exact text origin')
            if a['role']=='product' and (not isinstance(a['normalized_value'],str) or normalize_label(a['raw_lexeme'])!=normalize_label(a['normalized_value'])):
                raise FreeTextValidationError('Product assertion changed the literal identity')
            value=a['normalized_value']
            if isinstance(value,dict) and 'unit' in value:
                quantities=[(Decimal(m.group(1).replace(',','.')),m.group(2).casefold())
                            for m in re.finditer(r'(?<![\d.,])(\d+(?:[.,]\d+)?)\s*(ml/min|ml)\b',a['raw_lexeme'],re.IGNORECASE)]
                if (Decimal(value['value']),value['unit'].casefold()) not in quantities:
                    raise FreeTextValidationError('Quantity assertion changed its literal value or unit')
        for task in ledger['tasks']:
            refs(task['assertion_ids'], 'assertions')
            for key in ('product','column'):
                if task[key]['state']=='provided':
                    assertions=[indexes['assertions'][i] for i in task['assertion_ids'] if indexes['assertions'][i]['role']==key]
                    expected=task[key]['value'] if key=='product' else task[key]['value']['bed_volume']
                    if not any(a['normalized_value']==expected for a in assertions):
                        raise FreeTextValidationError('Supplied context lacks its literal assertion')
            for fi,fact in enumerate(task['facts']):
                ti=ledger['tasks'].index(task);prefix=f'/tasks/{ti}/facts/{fi}/'
                origins={o for f in ledger['field_origins'] if f['target_document']=='ledger' and f['target_pointer'].startswith(prefix) for o in f['origin_ids']}
                assertions=[indexes['assertions'][i] for i in task['assertion_ids'] if indexes['assertions'][i]['role']=='fact' and origins&set(indexes['assertions'][i]['origin_ids'])]
                if not any(a['normalized_value']==fact['value']['value'] for a in assertions):
                    raise FreeTextValidationError('Fact value disagrees with its scoped literal assertion')
        units = indexes['requested_units']
        for u in units.values():
            refs(u['origin_ids'], 'origins'); refs(u['assertion_ids'], 'assertions'); refs(u['issue_ids'], 'issues')
            owner=u['owner']; refs(owner['candidate_task_ids'], 'tasks')
            if owner['state']=='resolved': refs([owner['task_id']], 'tasks')
            assertions=[indexes['assertions'][i] for i in u['assertion_ids']]
            requested=[a for a in assertions if a['role']=='requested_information']
            if not requested or any(a['normalized_value']!=u['information'] for a in requested):
                raise FreeTextValidationError('Unit selector disagrees with its literal assertion')
            stages=[a for a in assertions if a['role']=='stage']
            if stages and (u['stage'] is None or any(a['normalized_value']!=u['stage']['code'] for a in stages)):
                raise FreeTextValidationError('Unit phase disagrees with its literal assertion')
            for aid in u['assertion_ids']:
                assertion=indexes['assertions'][aid]
                subjects=assertion['subject_candidates']
                if owner['state']=='resolved' and subjects and owner['task_id'] not in subjects:
                    raise FreeTextValidationError('Unit owner disagrees with assertion subject')
            if u['dispatch']=='preblock' and not any(indexes['issues'][i]['blocking'] and u['unit_id'] in indexes['issues'][i]['affected_unit_ids'] for i in u['issue_ids']):
                raise FreeTextValidationError('Preblocked unit without scoped blocking issue')
            if u['dispatch']=='project' and any(indexes['issues'][i]['blocking'] for i in u['issue_ids']):
                raise FreeTextValidationError('Blocked issue projected')
        for row in ledger['issues']:
            refs(row['origin_ids'],'origins');refs(row['affected_unit_ids'],'requested_units');refs(row['affected_fragment_ids'],'unresolved_fragments')
            if row['blocking'] and any(row['issue_id'] not in units[u]['issue_ids'] or units[u]['dispatch']!='preblock' for u in row['affected_unit_ids']):
                raise FreeTextValidationError('Blocking issue lost from dependent unit')
        for row in ledger['unresolved_fragments']:
            refs(row['origin_ids'],'origins');refs(row['issue_ids'],'issues')
        if ledger['inventory_complete'] and any(f['may_contain_request'] for f in ledger['unresolved_fragments']):
            raise FreeTextValidationError('Unknown request fragment in complete inventory')
        item_ids={u['item_id'] for u in units.values() if u['item_id'] is not None}
        for x in ledger['exclusions']:
            refs(x['origin_ids'],'origins');refs(x['candidate_task_ids'],'tasks')
            if x['task_id'] is not None:refs([x['task_id']],'tasks')
            if not set(x['target_item_ids']) <= item_ids:
                raise FreeTextValidationError('Unknown exclusion item')
        return indexes


class LedgerBuilder:
    def __init__(self, envelope, request_id, identity):
        self.text=envelope['text'];self.h=text_hash(self.text)
        self.value={'document_kind':'free_text_interpretation','interface_version':VERSION,
                    'request_id':request_id,'input_snapshot':deepcopy(envelope),'input_sha256_utf8':self.h,
                    'system_identity':identity, **{k:[] for k in ('assertions','tasks','requested_units','exclusions','issues','origins','field_origins','unresolved_fragments')},
                    'inventory_complete':True,'interpretation_status':'ready'}

    def origin(self, start=None, end=None, *, reason=None, rule=None, scope=None):
        oid='o'+str(len(self.value['origins'])+1)
        row={'origin_id':oid,'input_sha256_utf8':self.h}
        if start is not None:
            row.update(kind='text_span',start=start,end=end,quote=self.text[start:end])
        elif scope:
            row.update(kind='not_stated',checked_scope_origin_ids=scope,reason=reason)
        else:
            row.update(kind='application_metadata',policy_rule=rule or 'generated-record-identity',reason=reason or 'Application-generated identifier/order.')
        self.value['origins'].append(row);return oid

    def fields(self, value, prefix, origins, document='ledger'):
        for suffix, _ in leaves(value):
            self.value['field_origins'].append({'target_document':document,'target_pointer':prefix+suffix,'origin_ids':list(origins)})

    def assertion(self, role, owners, oid, value):
        o=next(o for o in self.value['origins'] if o['origin_id']==oid)
        row={'assertion_id':'a'+str(len(self.value['assertions'])+1),'role':role,'subject_candidates':list(owners),
             'raw_lexeme':o['quote'],'normalized_value':deepcopy(value),'origin_ids':[oid]}
        self.value['assertions'].append(row);return row['assertion_id']

    def issue(self, code, detail, origins, units=(), fragment_ids=(), blocking=True):
        row={'issue_id':'i'+str(len(self.value['issues'])+1),'code':code,'blocking':blocking,
             'affected_unit_ids':[u['unit_id'] for u in units],'affected_fragment_ids':list(fragment_ids),'origin_ids':list(origins),'detail':detail}
        self.value['issues'].append(row)
        for u in units:
            u['issue_ids'].append(row['issue_id'])
            if blocking:u['dispatch']='preblock'
        return row['issue_id']


def slot(value=None, state=None):
    return {'state':state or ('provided' if value is not None else 'not_supplied'),'value':value}


def na():
    return {'state':'not_applicable','value':None,'reason':'Not required for this declared documentary selector.'}
