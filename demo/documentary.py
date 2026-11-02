"""Minimal, opt-in staging handoff for the existing reviewed MabSelect selector.

No activation, model, graph write or new source approval. Standard library only.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import logging
from pathlib import Path
import re

from demo import mabselect as selector

ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger(__name__)
ITEMS = ('cleaning_options', 'restricted_sequence', 'followup_buffer_pH', 'pressure_limit', 'solvent_hold_time')
KEYS = dict(zip(('Q05', 'Q06', 'N06', 'N07', 'Q09'), (
    'mabselect.precipitated.general', 'mabselect.precipitated.restricted',
    'mabselect.hydrophobic.detergent', 'mabselect.hydrophobic.solvent', 'mabselect.context.clarify')))
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z')
DECISIONS = {
    'docs/technical/reviewed-dossier-serving-decisions-v01.json': '6dbe3937da292bf4cd9d10ef6ed58ee57fa13b8fff14188be02195728a0f9487',
    'docs/technical/reviewed-dossier-serving-technical-decisions-v01.json': '9f2545b6c50dae75de211fe478092ed64b6969849d97b13c6bb2eeddae915773',
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


class RequestError(ValueError):
    def __init__(self, code, pointer=''):
        self.code, self.pointer = code, pointer
        super().__init__(code)


def validate_request(value):
    if not isinstance(value, dict):
        raise RequestError('invalid_type')
    if any(not isinstance(k, str) for k in value):
        raise RequestError('invalid_type')
    allowed = {'kind', 'request_id', 'language', 'tasks'}
    if set(value) - allowed:
        raise RequestError('unknown_authority_field', '/' + sorted(set(value) - allowed)[0])
    if set(value) != allowed:
        raise RequestError('required_field_missing')
    if value['kind'] != 'reviewed_serving_request/v1' or value['language'] not in ('en', 'fr'):
        raise RequestError('unknown_selector')
    if not isinstance(value['request_id'], str) or not ID.fullmatch(value['request_id']):
        raise RequestError('invalid_type', '/request_id')
    tasks = value['tasks']
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 8:
        raise RequestError('max_tasks_exceeded', '/tasks')
    seen = set()
    for i, task in enumerate(tasks):
        pointer = f'/tasks/{i}'
        required = {'task_id', 'product', 'deposit_context', 'requested_items'}
        if not isinstance(task, dict) or not required <= set(task) or set(task) - required - {'excluded_items', 'input_label'}:
            raise RequestError('unknown_field', pointer)
        tid = task['task_id']
        if not isinstance(tid, str) or not ID.fullmatch(tid):
            raise RequestError('invalid_type', pointer + '/task_id')
        if tid in seen:
            raise RequestError('duplicate_task_id', pointer + '/task_id')
        seen.add(tid)
        for name, catalogue in [('product', selector.PRODUCTS), ('deposit_context', selector.CONTEXTS)]:
            if not isinstance(task[name], str) or task[name] not in catalogue:
                raise RequestError('unknown_selector', pointer + '/' + name)
        for name in ('requested_items', 'excluded_items'):
            values = task.get(name, [])
            if (not isinstance(values, list) or (name == 'requested_items' and not values)
                    or len(values) > 5 or any(not isinstance(x, str) or x not in ITEMS for x in values)
                    or len(set(values)) != len(values)):
                raise RequestError('unknown_selector', pointer + '/' + name)
        if 'input_label' in task and (not isinstance(task['input_label'], str) or len(task['input_label']) > 2048):
            raise RequestError('invalid_type', pointer + '/input_label')
    try:
        size = len(canonical(value))
    except (UnicodeError, ValueError):
        raise RequestError('invalid_type') from None
    if size > 32768:
        raise RequestError('request_too_large')
    return deepcopy(value)


def validation_error(value, error):
    rid = value.get('request_id') if isinstance(value, dict) else None
    rid = rid if isinstance(rid, str) and ID.fullmatch(rid) else None
    return {'kind': 'reviewed_serving_validation_error/v1', 'request_id': rid,
            'errors': [{'code': error.code, 'request_pointer': error.pointer}]}


class Handoff:
    """Explicit development preview; never writes an active release pointer."""
    def __init__(self, *, preview=False, context_bytes=65536, withdrawn=()):
        if type(preview) is not bool or type(context_bytes) is not int or context_bytes < len(canonical({'bundles':[], 'passages':[], 'reviews':[]})):
            raise ValueError('Use explicit preview and a positive server-side context budget')
        if any(key not in KEYS.values() for key in withdrawn):
            raise ValueError('Unknown staged withdrawal key')
        self.preview, self.context_bytes, self.withdrawn = preview, context_bytes, frozenset(withdrawn)
        self._evidence, self._decisions = selector._load()  # Existing portable approval/source checks.
        paths = set(DECISIONS)
        for name, expected in DECISIONS.items():
            if digest(ROOT / name) != expected:
                raise ValueError('Serving design decision changed')
            decision = json.loads((ROOT / name).read_text(encoding='utf-8'))
            for material, sha in decision['approved_materials_sha256_lf'].items():
                if digest(ROOT / material) != sha:
                    raise ValueError('Accepted serving design changed')
                paths.add(material)
        paths.update(('demo/mabselect.py', 'demo/documentary.py', 'demo/documentary_preview.py', 'demo/static/documentary.html', 'docs/technical/mabselect-cleaning-approved-contract-v01.md',
                      'docs/technical/mabselect-cleaning-review-v01.json',
                      'docs/technical/mabselect-cleaning-sources-v01.json',
                      'experiments/cytiva/retrieval-pilot-v01/evidence.json'))
        for package in ('reviewed-cleaning-retrieval', 'reviewed-section-questions'):
            paths.update(f'experiments/cytiva/{package}/{file}' for file in ('manifest.json', 'review.json'))
        self._pins = {name: digest(ROOT / name) for name in sorted(paths)}
        self.authority_digest = hashlib.sha256(canonical({'pins': self._pins, 'withdrawn': sorted(self.withdrawn),
                                                         'context_bytes': context_bytes})).hexdigest()
        self.release_id = 'staging-' + self.authority_digest[:20]
        self._passages = {p['id']: p for p in self._evidence['passages']}
        self._registered = set().union(*(set(ids) for ids in selector.REQUIRED.values()))

    def _check(self):
        if any(digest(ROOT / name) != sha for name, sha in self._pins.items()):
            raise ValueError('Staged authority changed; explicitly restage after review')

    def _passage(self, pid):
        p = self._passages[pid]
        if hashlib.sha256(p['quote'].encode('utf-8')).hexdigest() != p['quote_sha256']:
            raise ValueError('Quote binding mismatch')
        page = next(x for x in self._evidence['extraction']['pages'] if x['pdf_page_1based'] == p['pdf_page_1based'])
        return {'source_id': pid, 'corpus_id': self._evidence['id'],
                'pdf_sha256': self._evidence['source']['sha256'],
                'document_reference': self._evidence['source']['document_reference'],
                'edition_metadata_origin': self._evidence['source']['edition_metadata_origin'],
                'printed_page_label': p['printed_page'], 'pdf_page_1based': p['pdf_page_1based'],
                'pdf_page_index_0based': p['pdf_page_index_0based'],
                'extraction_version': 'pypdf-' + self._evidence['extraction']['pypdf_version'],
                'page_text_sha256': page['text_sha256'], 'offset_unit': 'unicode_code_points',
                'interval': 'start_inclusive_end_exclusive', 'page_text_start': p['page_text_start'],
                'page_text_end': p['page_text_end'], 'scope': p['scope'], 'quote': p['quote'],
                'quote_sha256': p['quote_sha256'], 'source_artifact': self._binding('experiments/cytiva/retrieval-pilot-v01/evidence.json')}

    def _binding(self, name):
        return {'artifact_id': Path(name).parent.name + '-' + Path(name).name.replace('.', '-'),
                'sha256': self._pins[name], 'hash_convention': 'sha256_lf'}

    def _review(self, scope):
        d = self._decisions[scope]
        package = 'reviewed-section-questions' if scope.startswith('N') else 'reviewed-cleaning-retrieval'
        return {'review_id': scope, 'kind': 'scoped_documentary_review', 'question_id': scope,
                'event_id': d['event_id'], 'decision': d['decision'], 'original_decision_date': d['decided_at_utc'],
                'original_human_message': d['original_human_message'], 'reservations': deepcopy(d['reservations']),
                'evidence_record_sha256': deepcopy(d['evidence_sha256']),
                'review_artifact': self._binding(f'experiments/cytiva/{package}/review.json')}

    def _bundle(self, scope, task, selected):
        ids = selector.REQUIRED[scope].copy()
        delivered = {p['id']: p for p in selected['passages']}
        if not set(ids) <= set(delivered):
            raise ValueError('Missing indispensable source')
        for pid in ids:
            if delivered[pid]['quote'] != self._passages[pid]['quote'] or delivered[pid]['quote_sha256'] != self._passages[pid]['quote_sha256']:
                raise ValueError('Selector source changed')
        reviewed = next(d for d in selected['review_scopes'] if d['question_id'] == scope)
        if reviewed['reservations'] != self._decisions[scope]['reservations']:
            raise ValueError('Review reservations changed')
        if scope == 'Q09':
            options = [{'option_id': 'Q09-context', 'role': 'clarification_context', 'alternative_group_id': None,
                        'sequence_id': None, 'wording': selected['message'], 'source_ids': ids, 'steps': [], 'warnings': []}]
        else:
            option = next(x for x in selected['options'] if x['source_ids'] == ids)
            quote_ids = option['quote_ids']
            if quote_ids != {'Q05':['E167-P'], 'Q06':['E167-SH','E167-S'], 'N06':['E167-D'], 'N07':['E167-E','E167-W']}[scope]:
                raise ValueError('Incomplete option quotation set')
            # Original numbered blocks stay verbatim, including conditions and quantities.
            steps = []
            for pid in quote_ids:
                if pid in ('E167-SH', 'E167-W'):
                    continue
                quote = self._passages[pid]['quote']
                chunks = [s for s in re.split(r'(?m)(?=^[123](?:\.\s|\s))', quote) if s]
                if pid == 'E167-E':
                    first, marker, tail = quote.partition('Wash immediately')
                    chunks = [first, marker + tail] if marker else [quote]
                for number, wording in enumerate(chunks, 1):
                    phase = 'followup_wash' if 'Immediately wash' in wording or wording.startswith('Wash immediately') else ('conditioning' if pid == 'E167-S' and number == 1 else 'cleaning')
                    step_id = f'{pid}-{number}'
                    steps.append({'step_id': step_id, 'order': len(steps)+1, 'phase': phase, 'wording': wording,
                                  'force_text': ('Immediately wash' if 'Immediately wash' in wording else
                                                 'Wash immediately' if wording.startswith('Wash immediately') else 'Wash'),
                                  'source_ids': [pid], 'quantities': [],
                                  'immediate_after_step_id': steps[-1]['step_id'] if phase == 'followup_wash' and steps else None})
            options = [{'option_id': scope + '-block', 'role': 'procedure',
                        'alternative_group_id': 'hydrophobic-routes' if scope.startswith('N') else ('general-formulations' if scope == 'Q05' else None),
                        'sequence_id': scope + '-original-sequence', 'wording': option['title'], 'source_ids': ids,
                        'steps': steps, 'warnings': [{'wording': self._passages[pid]['quote'], 'source_ids': [pid]}
                                                  for pid in ('E167-E', 'E167-W') if pid in ids]}]
        notes = [] if scope=='Q09' else ['Application note: '+n for n in option.get('notes', [])]
        explanation = selected['message'] + (' '+selected['options_intro'] if selected.get('options_intro') else '')
        return {'bundle_key': KEYS[scope], 'mapping_version': 'staging-v1', 'review_scope': scope,
                'product': task['product'], 'deposit_context': task['deposit_context'], 'required_source_ids': ids,
                'review_ids': [scope], 'conditions': ({'kind':'source_text','text':self._passages['E167-H']['quote'],'source_ids':['E167-H']} if scope=='Q09' else
                               {'kind':'all_of','children':[{'kind':'product_in','values':['sure','sure_lx'] if scope=='Q06' else ['mabselect','sure','sure_lx'],'source_ids':['E167-SH'] if scope=='Q06' else ['E167-H']},
                                                           {'kind':'category_in','values':[task['deposit_context']],'source_ids':['E167-PH'] if scope.startswith('Q') else ['E167-LH']}]}),
                'applicability': 'unknown' if scope == 'Q09' else 'true', 'condition_explanation': explanation,
                'options': options, 'visible_reservations': deepcopy(reviewed['reservations']) + notes, 'suitability': 'not_established'}

    def _base(self, request):
        return {'kind': 'reviewed_documentary_bundle/v1', 'contract_version': '1', 'request_id': request['request_id'],
                'release_id': self.release_id if self.preview else None,
                'authority_digest': self.authority_digest if self.preview else None,
                'status': 'unavailable', 'response_reason': 'release_not_activated' if not self.preview else 'item_outcomes',
                'items': [], 'context': {'bundles': [], 'passages': [], 'reviews': []}, 'citation_refs': [],
                'coverage': {s: 0 for s in ('supported','needs_clarification','abstained','quarantined','unavailable','excluded')},
                'context_measure': {'convention': 'utf8_json_sorted_keys_compact_unicode_preserved_no_nan',
                                    'delivered_bytes': 0, 'limit_bytes': self.context_bytes},
                'limits': {'diagnosis_established': False, 'operational_suitability': 'not_established',
                           'operational_authorization': False, 'absence_scope': 'selected_release_bundles_only'}}

    def evaluate(self, value):
        try:
            request = validate_request(value)
        except RequestError as error:
            return validation_error(value, error)
        response = self._base(request)
        if not self.preview:
            return self._finish(response)
        try:
            self._check()
            for i, task in enumerate(request['tasks']):
                selected = None
                selection_failed = False
                for item in task['requested_items']:
                    outcome = {'task_id': task['task_id'], 'requested_item': item, 'state': 'excluded', 'reason': 'excluded_by_request',
                               'field_origins': [{'field': name, 'request_pointer': f'/tasks/{i}/{name}'} for name in ('product', 'deposit_context')] +
                                                [{'field': 'requested_item', 'request_pointer': f'/tasks/{i}/requested_items/{task["requested_items"].index(item)}'}],
                               'bundle_refs': [],
                               'bundle_keys': [], 'withheld_bundle_keys': [], 'clarification_targets': [], 'absence_scope': None}
                    if item not in task.get('excluded_items', []):
                        if selected is None and not selection_failed:
                            try:
                                selected = selector.evaluate({'mode':'mabselect','product':task['product'],'deposit_context':task['deposit_context']})
                            except (ValueError, OSError, KeyError, StopIteration):
                                raise  # Shared selector authority failures invalidate the entire request.
                            except Exception as error:
                                LOGGER.error('MabSelect selector failed (%s)', type(error).__name__)
                                selection_failed = True
                        if selection_failed:
                            outcome.update(state='unavailable', reason='required_dependency_unavailable')
                            response['items'].append(outcome)
                            continue
                        try:
                            self._item(response, outcome, task, selected)
                        except Exception as error:
                            LOGGER.error('MabSelect item assembly failed (%s)', type(error).__name__)
                            outcome.update(state='unavailable', reason='required_dependency_unavailable',
                                           bundle_keys=[], bundle_refs=[], clarification_targets=[])
                    else:
                        outcome['field_origins'].append({'field':'exclusion', 'request_pointer':f'/tasks/{i}/excluded_items/{task["excluded_items"].index(item)}'})
                    response['items'].append(outcome)
            self._check()  # No stale staged authority after assembly.
        except Exception as error:
            LOGGER.error('MabSelect authority unavailable (%s)', type(error).__name__)
            response = self._base(request)
            response.update(status='unavailable', response_reason='invalid_authority')
        return self._finish(response)

    def _item(self, response, outcome, task, selected):
        item = outcome['requested_item']
        if selected['state'] == 'outside_scope':
            outcome.update(state='abstained', reason='outside_release_scope', absence_scope=selected['corpus_scope']); return
        if selected['state'] == 'needs_clarification':
            fields = []
            if task['product'] in ('unknown','family_unknown','contradictory'): fields.append('product')
            if task['deposit_context'] in ('unknown','mixed_other'): fields.append('deposit_context')
            reason = 'product_and_context_unknown' if len(fields)==2 else ('product_unknown' if fields==['product'] else 'context_unknown')
            scopes = ['Q09']
            outcome.update(state='needs_clarification', reason=reason, clarification_targets=fields)
        elif item in ('pressure_limit','solvent_hold_time'):
            outcome.update(state='abstained', reason='not_in_selected_excerpts', absence_scope='Selected edition-bound MabSelect blocks only; not the entire manual.'); return
        elif item == 'restricted_sequence':
            if task['product'] not in ('sure','sure_lx') or task['deposit_context']!='precipitated_substances':
                outcome.update(state='abstained', reason='outside_release_scope', absence_scope='Q06 is restricted to SuRe/SuRe LX in the precipitated/denatured context; no general incompatibility is inferred.'); return
            scopes = ['Q06']
        else:
            scopes = [d['question_id'] for d in selected['review_scopes']]
        keys = [KEYS[s] for s in scopes]
        if any(k in self.withdrawn for k in keys):
            outcome.update(state='quarantined', reason='review_withdrawn', withheld_bundle_keys=keys, clarification_targets=[]); return
        trial = deepcopy(response['context'])
        refs = []
        for scope in scopes:
            bundle = self._bundle(scope, task, selected)
            if bundle not in trial['bundles']: trial['bundles'].append(bundle)
            refs.append(f'/context/bundles/{trial["bundles"].index(bundle)}')
            for pid in selector.REQUIRED[scope]:
                if not any(p['source_id']==pid for p in trial['passages']): trial['passages'].append(self._passage(pid))
            if not any(d['review_id']==scope for d in trial['reviews']): trial['reviews'].append(self._review(scope))
        if len(canonical(trial)) > self.context_bytes:
            outcome.update(state='unavailable', reason='context_budget_incomplete', withheld_bundle_keys=keys, clarification_targets=[]); return
        response['context'] = trial
        outcome['bundle_refs'] = refs  # Exact task-bound objects, including Q09 clarification context.
        if scopes != ['Q09']:
            outcome.update(state='supported', reason='documentary_support', bundle_keys=keys)

    def _finish(self, response):
        counts = Counter(x['state'] for x in response['items'])
        response['coverage'].update(counts)
        if response['response_reason']=='item_outcomes':
            active = [x for x in response['items'] if x['state']!='excluded']
            supported = counts['supported']
            response['status'] = ('supported' if active and supported==len(active) else 'partial' if supported else
                                  'unavailable' if counts['unavailable'] else 'needs_clarification' if counts['needs_clarification'] else 'abstained')
            if not active: response['response_reason']='no_requested_item'
        response['context_measure']['delivered_bytes'] = len(canonical(response['context']))
        response['citation_refs'] = [{'source_id':p['source_id'],'release_id':self.release_id,
                                     'href':f'/reviewed/v1/releases/{self.release_id}/sources/{p["source_id"]}'} for p in response['context']['passages']]
        return response

    def source(self, release_id, source_id):
        if not self.preview or release_id != self.release_id or source_id not in self._registered:
            raise KeyError('Unregistered source')
        self._check()
        scopes = [s for s, ids in selector.REQUIRED.items() if source_id in ids and KEYS[s] not in self.withdrawn]
        result = {'kind':'reviewed_serving_source_view/v1','release_id':self.release_id,'source_id':source_id,
                  'authority_digest':self.authority_digest,'status':'available' if scopes else 'quarantined',
                  'reason':'registered_excerpt' if scopes else 'review_withdrawn','pdf_available':False,
                  'passage':self._passage(source_id) if scopes else None,
                  'reviews':[self._review(s) for s in scopes], 'scientific_validation_established':False}
        self._check()
        return result
