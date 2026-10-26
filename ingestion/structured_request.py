"""Deterministic structured request control, isolated from answering models.

Run: python -m ingestion.structured_request request.json --output NEW_FILE.json
The output contains a canonical request, source-context plan and audit trace.
It is documentary support, not a generated answer or laboratory authorization.
"""
import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
import hashlib
from itertools import zip_longest
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ingestion.structured_sources import (
    ROOT, SOURCE_FIELDS, IntegrityError, SourceAdapter, compact, local_token_counter,
    normalize_label,
)


class RequestValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('; '.join(row['pointer'] + ': ' + row['message'] for row in errors))


def pointer(parts):
    return ''.join('/' + str(p).replace('~', '~0').replace('/', '~1') for p in parts)


def supplied(slot):
    return slot['value'] if slot['state'] == 'provided' else None


def ordered_slot(slot):
    """Use declared slot/quantity order, independently of caller key ordering."""
    result = {k: deepcopy(slot[k]) for k in ('state', 'value', 'reason') if k in slot}
    if isinstance(result['value'], dict) and 'bed_volume' in result['value']:
        q = result['value']['bed_volume']
        result['value'] = {'bed_volume': {'value': q['value'], 'unit': q['unit']}}
    return result


@dataclass
class Unit:
    task_index: int
    item_index: int
    task: dict
    item: dict
    information: str
    input_pointer: str
    result: dict
    product_ref: str | None = None
    methods: list = field(default_factory=list)
    column: dict = field(default_factory=dict)
    column_usable: bool = True
    candidates: list = field(default_factory=list)
    blocked: bool = False


class StructuredControl:
    def __init__(self, root=ROOT):
        self.adapter = SourceAdapter(root)
        self.schema = self.adapter.schema
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(self.schema)
        self._count_tokens = None

    def validate(self, value, definition=None):
        validator = self.validator if definition is None else Draft202012Validator(
            {'$ref': '#/$defs/' + definition, '$defs': self.schema['$defs']})
        errors = sorted(validator.iter_errors(value), key=lambda e: str(list(e.absolute_path)))
        if errors:
            raise RequestValidationError([
                {'pointer': pointer(e.absolute_path), 'message': e.message} for e in errors[:8]])

    def evaluate(self, submission, request_id='structured-control'):
        self.validate(submission)
        # Round trip refuses non-JSON values/NaN and protects the caller's input.
        snapshot = json.loads(compact(submission))
        canonical = {
            'document_kind': 'canonical_request', 'request_id': request_id,
            'contract_version': snapshot['contract_version'], 'input_snapshot': snapshot,
            'input_sha256': hashlib.sha256(compact(snapshot, sort_keys=True).encode('utf-8')).hexdigest(),
            'submission': deepcopy(snapshot), 'system_versions': deepcopy(self.adapter.versions),
            'field_origins': [], 'resolved_fields': [], 'issues': [],
        }

        def origins(value, parts=()):
            if isinstance(value, dict):
                for k, v in value.items():
                    origins(v, (*parts, k))
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    origins(v, (*parts, i))
            else:
                loc = pointer(parts)
                canonical['field_origins'].append(
                    {'target_pointer': loc, 'origins': [{'kind': 'form_field', 'pointer': loc}]})
        origins(snapshot)
        units = self._interpret(snapshot, canonical)
        self.validate(canonical, 'canonical_request')
        if self._count_tokens is None:
            self._count_tokens = local_token_counter(
                self.adapter.root, self.adapter.config['execution_policy']['tokenizer'])
        plan, audit = self._assemble(units, self._count_tokens, request_id)
        plan['has_interpretation_issues'] = bool(canonical['issues'])
        self.validate(plan, 'plan_result')
        audit.update({'system_versions': deepcopy(self.adapter.versions),
                      'input_sha256': canonical['input_sha256'],
                      'applicability': 'Not established; documentary support only.',
                      'excluded_source_ids': sorted(self.adapter.excluded)})
        return {'canonical_request': canonical, 'plan': plan, 'audit': audit}

    def _resolution(self, canonical, task_id, loc, kind, slot):
        value = supplied(slot)
        resolution = (self.adapter.catalog.resolve(value, kind) if value is not None else
                      {'status': 'not_needed' if slot['state'] == 'not_applicable' else 'unresolved',
                       'refs': [], 'volume': None})
        column = ({'state': 'provided', 'value': {'bed_volume': resolution['volume']}}
                  if resolution['volume'] else {'state': 'not_supplied', 'value': None})
        canonical['resolved_fields'].append({
            'input_pointer': loc, 'task_id': task_id, 'entity_kind': kind,
            'status': resolution['status'], 'canonical_refs': resolution['refs'],
            'explicit_column_from_label': column,
            'origins': [{'kind': 'form_field', 'pointer': loc}],
        })
        return resolution, column

    @staticmethod
    def _issue(canonical, task, item, information, code, detail, locations, blocking=True):
        issue_id = 'issue-' + str(len(canonical['issues']) + 1)
        canonical['issues'].append({
            'issue_id': issue_id, 'code': code, 'task_id': task['task_id'],
            'item_id': item['item_id'] if item else None, 'information': information,
            'origins': [{'kind': 'form_field', 'pointer': p} for p in locations],
            'detail': detail, 'blocking': blocking,
        })
        return issue_id

    def _block(self, unit, canonical, code, detail, locations=None, state='needs_clarification'):
        issue = self._issue(canonical, unit.task, unit.item, unit.information, code, detail,
                            locations or [unit.input_pointer])
        unit.result['issue_ids'].append(issue)
        unit.result['diagnostics'].append({'dimension': 'interpretation', 'code': code, 'detail': detail})
        unit.result['interpretation_state'] = ('out_of_scope' if state == 'out_of_scope'
                                                else 'needs_clarification')
        unit.result['state'], unit.result['reason'], unit.blocked = state, detail, True

    @staticmethod
    def _selector_matches(selector, item, information):
        return (selector['stage_kind'] == item['stage']['kind'] and
                selector['stage_code'] == item['stage']['code'] and
                information in selector['information'])

    def _interpret(self, snapshot, canonical):
        units = []
        task_counts = Counter(t['task_id'] for t in snapshot['tasks'])
        id_counts = Counter(x for t in snapshot['tasks'] for x in
                            [i['item_id'] for i in t['items']] +
                            [e['exclusion_id'] for e in t['exclusions']])
        for ti, task in enumerate(snapshot['tasks']):
            tp = '/tasks/' + str(ti)
            product, alias_column = self._resolution(
                canonical, task['task_id'], tp + '/product', 'product', task['product'])
            exclusion_resolutions = {}
            for ei, exclusion in enumerate(task['exclusions']):
                if exclusion['selector']['kind'] == 'product':
                    resolved, _ = self._resolution(
                        canonical, task['task_id'], tp + '/exclusions/' + str(ei) + '/selector/label',
                        'product', {'state': 'provided', 'value': exclusion['selector']['label']})
                    exclusion_resolutions[ei] = resolved
            column = deepcopy(task['column'])
            if column['state'] != 'provided' and alias_column['state'] == 'provided':
                column = deepcopy(alias_column)
            column_errors = []
            if column['state'] == 'provided':
                q = column['value']['bed_volume']
                if q['unit'] != 'mL' or Decimal(q['value']) <= 0:
                    column_errors.append(('invalid_unit_role', 'Column bed volume must be positive mL.'))
                elif product['refs']:
                    formats = self.adapter.catalog.entities[product['refs'][0]]['supported_bed_volumes']
                    if not any(Decimal(v['value']) == Decimal(q['value']) and v['unit'] == q['unit'] for v in formats):
                        column_errors.append(('unsupported_column_format', 'Supplied bed volume is outside the supported formats.'))
                if (task['column']['state'] == 'provided' and alias_column['state'] == 'provided' and
                        (Decimal(q['value']) != Decimal(alias_column['value']['bed_volume']['value']) or q['unit'] != 'mL')):
                    column_errors.append(('conflicting_input', 'Qualified product label and explicit column disagree.'))
            facts = {}
            fact_errors = []
            for fi, fact in enumerate(task['facts']):
                fp = tp + '/facts/' + str(fi)
                facts.setdefault(fact['key'], []).append((fact, fp))
                val = supplied(fact['value'])
                if isinstance(val, dict):
                    expected = 'mL/min' if fact['key'] == 'observed_flow' else 'mL'
                    if val['unit'] != expected:
                        fact_errors.append((fact['key'], 'invalid_unit_role', 'Invalid unit for ' + fact['key'], [fp]))
            for key, assertions in facts.items():
                if len(assertions) > 1:
                    fact_errors.append((key, 'conflicting_input', 'Repeated/contradictory fact assertions preserved: ' + key,
                                        [p for _, p in assertions]))
            for ii, item in enumerate(task['items']):
                ip = tp + '/items/' + str(ii)
                methods = []
                method_bad = False
                if item['techniques']['state'] == 'provided':
                    for mi, label in enumerate(item['techniques']['value']):
                        resolved, _ = self._resolution(canonical, task['task_id'],
                            ip + '/techniques/value/' + str(mi), 'technique', {'state': 'provided', 'value': label})
                        methods.extend(resolved['refs'])
                        method_bad |= not bool(resolved['refs'])
                for ni, info in enumerate(item['information']):
                    result = {'task_id': task['task_id'], 'item_id': item['item_id'], 'information': info,
                              'state': 'unsupported_selector', 'reason': 'No reviewed role mapping.', 'source_ids': [],
                              'interpretation_state': 'ready', 'documentary_support_state': 'not_assessed',
                              'issue_ids': [], 'diagnostics': []}
                    unit = Unit(ti, ii, task, item, info, ip + '/information/' + str(ni), result,
                                product['refs'][0] if product['refs'] else None, methods, column,
                                column_usable=not any(code in ('invalid_unit_role', 'conflicting_input')
                                                      for code, _ in column_errors))
                    units.append(unit)
                    roles = [r for r in self.adapter.config['roles'] if self._selector_matches(r['selector'], item, info)]
                    unavailable = [r for r in self.adapter.config['unavailable_selectors']
                                   if self._selector_matches(r['selector'], item, info)]
                    product_needed = any(r.get('product_scope') for r in roles + unavailable)
                    # Bounded absence needs no invented size, but an explicitly ambiguous product is not resolved.
                    product_needed |= bool(unavailable and info == 'maximum_pressure' and task['product']['state'] == 'provided')
                    if task_counts[task['task_id']] > 1 or id_counts[item['item_id']] > 1:
                        self._block(unit, canonical, 'duplicate_identifier', 'Ambiguous task/item identifier.', [tp, ip])
                    if product_needed:
                        if product['status'] == 'out_of_scope':
                            self._block(unit, canonical, 'out_of_scope_product', 'Identified product is outside initial scope.',
                                        [tp + '/product'], state='out_of_scope')
                        elif not product['refs']:
                            self._block(unit, canonical, 'ambiguous_identity' if product['status'] == 'ambiguous' else 'unresolved_binding',
                                        'Exact product identity required; no guessed product.', [tp + '/product'])
                        for code, detail in column_errors:
                            self._block(unit, canonical, code, detail, [tp + '/product', tp + '/column'],
                                        state='out_of_scope' if code == 'unsupported_column_format' else 'needs_clarification')
                    if any(r.get('method_scope') for r in roles + unavailable):
                        if method_bad or not methods:
                            self._block(unit, canonical, 'unresolved_binding', 'Explicit recognized technique context required.',
                                        [ip + '/techniques'])
                        elif any(m not in r['method_scope'] for r in roles + unavailable for m in methods):
                            self._block(unit, canonical, 'unsupported_selector', 'Technique is not supported by this role.',
                                        [ip + '/techniques'], state='unsupported_selector')
                    for facet, slot in item['facets'].items():
                        allowed = (facet == 'buffer_use' and item['stage']['kind'] == 'preparation' or
                                   facet == 'elution_mode' and item['stage']['code'] == 'elution' or
                                   facet == 'syringe_query_mode' and item['stage']['code'] == 'sample_application' and
                                   'syringe_correspondence' in item['information'])
                        if slot['state'] == 'provided' and not allowed:
                            self._block(unit, canonical, 'unsupported_selector', 'Facet incompatible with requested stage: ' + facet,
                                        [ip + '/facets/' + facet], state='unsupported_selector')
                    for key, code, detail, locations in fact_errors:
                        relevant = (task['intent'] == 'documentary_applicability' or
                                    info == 'clarification_context' and key in ('minor_contaminants_interfere', 'residual_identity', 'intended_application') or
                                    info == 'syringe_correspondence' and supplied(item['facets']['syringe_query_mode']) == 'reference_flow_check' and key == 'observed_flow')
                        if relevant:
                            self._block(unit, canonical, code, detail, locations)
                    joint_scope_known = True
                    if product_needed and item['techniques']['state'] == 'provided':
                        joint_scope_known = False
                        self._block(unit, canonical, 'unsupported_selector',
                                    'No reviewed joint product/technique role for this procedural item.',
                                    [ip + '/techniques'], state='unsupported_selector')
                    self._exclusions(unit, canonical, tp, id_counts, product_needed, exclusion_resolutions)
                    # A role can be identified independently of missing size; never guess a product/method.
                    scope_known = joint_scope_known and (not product_needed or bool(product['refs']) and not column_errors)
                    if any(r.get('method_scope') for r in roles + unavailable):
                        scope_known &= (bool(methods) and not method_bad and all(
                            m in r['method_scope'] for r in roles + unavailable
                            if r.get('method_scope') for m in methods))
                    if not scope_known:
                        continue
                    if unavailable:
                        row = unavailable[0]
                        state = 'missing_source' if row['state'] == 'missing' else 'quarantined'
                        detail = row.get('scope', 'Relevant source remains excluded: ' + ', '.join(row.get('excluded_source_ids', [])))
                        result['documentary_support_state'] = state
                        result['diagnostics'].append({'dimension': 'documentary_support', 'code': state, 'detail': detail})
                        if row['matrix_row'] == 'M12' and column['state'] != 'provided':
                            self._block(unit, canonical, 'missing_context',
                                        'Column unresolved; supplying it cannot unlock quarantined support.', [tp + '/column'])
                        result['state'], result['reason'] = state, detail
                        continue
                    matching = []
                    for role in roles:
                        facets = role['selector'].get('facet') or {}
                        if all(supplied(item['facets'][key]) == val for key, val in facets.items()):
                            matching.append(role)
                    if roles and not matching:
                        self._block(unit, canonical, 'missing_context', 'Specify the requested buffer use as a separate item.', [ip + '/facets/buffer_use'])
                        continue
                    if not roles:
                        result['documentary_support_state'] = 'unsupported_selector'
                        result['diagnostics'].append({'dimension': 'documentary_support', 'code': 'unsupported_selector', 'detail': 'No reviewed adapter role for this stage/information combination.'})
                        continue
                    for role in matching:
                        if role['product_scope'] and unit.product_ref not in role['product_scope']:
                            continue
                        result['documentary_support_state'] = 'eligible'
                        for requirement in role['required_context']:
                            missing = (requirement == 'supported_column' and column['state'] != 'provided' or
                                requirement == 'provided_elution_mode_or_explicit_comparison' and
                                supplied(item['facets']['elution_mode']) is None and item['answer_mode'] != 'compare_documented_alternatives' or
                                requirement == 'provided_syringe_query_mode' and supplied(item['facets']['syringe_query_mode']) is None or
                                requirement == 'intent=context_clarification' and task['intent'] != 'context_clarification')
                            if missing:
                                self._block(unit, canonical, 'missing_context', 'Missing required context: ' + requirement,
                                            [tp + '/column' if requirement == 'supported_column' else ip])
                        if (info == 'syringe_correspondence' and supplied(item['facets']['syringe_query_mode']) == 'reference_flow_check' and not unit.blocked):
                            observations = facts.get('observed_flow', [])
                            flow = supplied(observations[0][0]['value']) if len(observations) == 1 else None
                            if flow is None:
                                self._block(unit, canonical, 'missing_context', 'Provide the observed flow for an exact reference check.', [tp + '/facts'])
                            elif (flow['unit'] != 'mL/min' or Decimal(flow['value']) != self.adapter.syringe_reference_flow(Decimal(column['value']['bed_volume']['value']))):
                                self._block(unit, canonical, 'unsupported_transformation', 'Only a literal documented flow reference can be repeated; no interpolation.',
                                            [observations[0][1]], state='unsupported_transformation')
                        if not unit.blocked:
                            unit.candidates.extend(role['candidates'])
            # Preserve task-level fact problems even when they do not affect documentary identification.
            for _, code, detail, locations in fact_errors:
                if not any(i['origins'] == [{'kind': 'form_field', 'pointer': p} for p in locations]
                           for i in canonical['issues']):
                    self._issue(canonical, task, None, None, code, detail, locations, blocking=False)
        return units

    def _exclusion_selector_error(self, selector):
        """Validate restrictions independently of positive-item intersection.

        Registered unavailable selectors are legitimate restrictions too; this
        check describes vocabulary/shape semantics, not source admissibility.
        """
        if selector['kind'] in ('product', 'all_operating_information'):
            return None
        registered = []
        for role in self.adapter.config['roles'] + self.adapter.config['unavailable_selectors']:
            candidate = role['selector']
            if (candidate['stage_kind'] == selector['kind'] and
                    candidate['stage_code'] == selector['code']):
                facet = candidate.get('facet') or {}
                if 'buffer_use' not in selector or not facet or facet.get('buffer_use') == selector['buffer_use']:
                    registered.append(candidate)
        allowed = {info for candidate in registered for info in candidate['information']}
        requested = selector['information']
        if not allowed or requested != 'all' and not set(requested) <= allowed:
            return 'Unregistered exclusion stage/information/facet combination; clarify the restriction.'
        return None

    def _exclusions(self, unit, canonical, tp, counts, product_needed, resolutions):
        task, item = unit.task, unit.item
        for ei, exclusion in enumerate(task['exclusions']):
            ep = tp + '/exclusions/' + str(ei)
            scope = exclusion['scope']
            if (counts[exclusion['exclusion_id']] > 1 or scope['task_id'] != task['task_id'] or
                    'item_id' in scope and scope['item_id'] not in {i['item_id'] for i in task['items']}):
                self._block(unit, canonical, 'duplicate_identifier' if counts[exclusion['exclusion_id']] > 1 else 'unresolved_binding',
                            'Invalid/ambiguous exclusion owner; no cross-task effect.', [ep])
                continue
            if 'item_id' in scope and scope['item_id'] != item['item_id']:
                continue
            selector = exclusion['selector']
            error = self._exclusion_selector_error(selector)
            if error:
                self._block(unit, canonical, 'unsupported_selector', error, [ep], state='unsupported_selector')
                continue
            kind = selector['kind']
            overlap = False
            if kind == 'all_operating_information':
                overlap = item['stage']['kind'] == 'operating_phase'
            elif kind == 'product':
                if not product_needed:
                    continue
                # Resolve only the explicit exclusion label, never activate it as positive context.
                res = resolutions[ei]
                overlap = bool(unit.product_ref and unit.product_ref in res['refs'])
                if overlap and res['volume'] is not None:
                    if unit.column['state'] != 'provided' or not unit.column_usable:
                        self._block(unit, canonical, 'unresolved_binding',
                                    'Format-qualified exclusion requires a resolved column; retain its stated size without broadening it.',
                                    [ep, tp + '/column'])
                        continue
                    volume = unit.column['value']['bed_volume']
                    overlap = (volume['unit'] == res['volume']['unit'] and
                               Decimal(volume['value']) == Decimal(res['volume']['value']))
                if not res['refs']:
                    literal = supplied(task['product'])
                    overlap = literal is not None and normalize_label(literal) == normalize_label(selector['label'])
                    if res['status'] in ('unresolved', 'ambiguous') and not overlap:
                        self._block(unit, canonical, 'unresolved_binding', 'Exclusion product identity cannot be scoped reliably.', [ep])
            else:
                overlap = (kind == item['stage']['kind'] and selector['code'] == item['stage']['code'] and
                           (selector['information'] == 'all' or unit.information in selector['information']))
                if overlap and 'buffer_use' in selector:
                    use = supplied(item['facets']['buffer_use'])
                    if use is None:
                        self._block(unit, canonical, 'unresolved_binding', 'Cannot scope buffer-use exclusion without requested use.', [ep])
                    overlap = use == selector['buffer_use']
            if overlap:
                self._block(unit, canonical, 'conflicting_exclusion', 'Same-task request and exclusion overlap; clarify affected information.', [unit.input_pointer, ep])

    def _binding(self, unit, candidate):
        return {'task_id': unit.task['task_id'], 'item_id': unit.item['item_id'],
                'information': unit.information, 'stage': {k: unit.item['stage'][k] for k in ('kind', 'code')},
                'source_ids': self.adapter.bundle(candidate),
                'product_ref': unit.product_ref if candidate['scope_specificity']['product_grade'] else None,
                'column': ordered_slot(unit.column),
                'facets': {k: ordered_slot(unit.item['facets'][k]) for k in
                           ('buffer_use', 'elution_mode', 'syringe_query_mode')}}

    def _assemble(self, units, count_tokens, request_id):
        """Whole-bundle admission; injected counter is internal test seam only."""
        context = {'source_passages': [], 'bindings': []}
        selected, considered, bindings = [], set(), {}
        trace = []
        groups = {}
        for u in units:
            groups.setdefault((u.task_index, u.item_index), []).append(u)
        task_items = {}
        for key, group in groups.items():
            if any(u.candidates and not u.blocked for u in group):
                task_items.setdefault(key[0], []).append(key)
        # First compact each task's admissible item list, then interleave it.
        # Keep this order for subsequent rounds; a blocked original A1 must not
        # give B's first admissible item precedence over A's first admissible one.
        order = [key for row in zip_longest(*task_items.values()) for key in row if key is not None]
        limits = self.adapter.config['execution_policy']
        while True:
            progress = False
            for group_key in order:
                group = groups[group_key]
                ready = [u for u in group if u.candidates and u.result['state'] != 'supported']
                pool = {}
                for u in ready:
                    for candidate in u.candidates:
                        cid = candidate['candidate_id']
                        if (group_key, cid) not in considered:
                            pool.setdefault(cid, (candidate, []))[1].append(u)
                if not pool:
                    continue
                progress = True
                parts = [c['lexical_terms'] for c, _ in pool.values()]
                parts += [group[0].item['stage']['code']] + [u.information for u in ready]
                for u in ready:
                    if any(c['scope_specificity']['product_grade'] for c in u.candidates):
                        parts.append(self.adapter.catalog.entities[u.product_ref]['canonical_label'])
                    parts.extend(self.adapter.catalog.entities[m]['canonical_label'] for m in u.methods)
                    parts.extend(slot['value'] for slot in u.item['facets'].values() if slot['state'] == 'provided')
                ranked = self.adapter.rank(list(pool.values()), parts)
                _, candidate, covered, components = ranked[0]
                cid = candidate['candidate_id']
                considered.add((group_key, cid))
                bundle = self.adapter.bundle(candidate)
                ids = [p['id'] for p in context['source_passages']]
                ids += [sid for sid in bundle if sid not in ids]
                roots = selected + [sid for sid in candidate['root_source_ids'] if sid not in selected]
                proposed_bindings = dict(bindings)
                for u in covered:
                    proposed_bindings[units.index(u)] = self._binding(u, candidate)
                proposed = {'source_passages': [{k: self.adapter.passages[sid][k] for k in SOURCE_FIELDS} for sid in ids],
                            'bindings': [proposed_bindings[k] for k in sorted(proposed_bindings)]}
                before, after = count_tokens(compact(context)), count_tokens(compact(proposed))
                fits = len(roots) <= limits['max_selected_distinct_roots'] and after <= limits['max_serialized_context_tokens']
                trace.append({'task_id': covered[0].task['task_id'], 'item_id': covered[0].item['item_id'],
                              'candidate_id': cid, 'gates': 'eligible_role_and_complete_scope',
                              'ranking': components, 'ranked_candidates': [r[1]['candidate_id'] for r in ranked],
                              'ranked_candidate_scores': [{'candidate_id': r[1]['candidate_id'],
                                                           **r[3]} for r in ranked],
                              'root_source_ids': list(candidate['root_source_ids']), 'bundle_source_ids': bundle,
                              'candidate_context_tokens': after, 'marginal_context_tokens': after - before,
                              'candidate_distinct_roots': len(roots), 'admitted': fits,
                              'reason': 'admitted' if fits else 'root_budget' if len(roots) > limits['max_selected_distinct_roots'] else 'token_budget'})
                if fits:
                    context, selected, bindings = proposed, roots, proposed_bindings
                    for u in covered:
                        u.result.update(state='supported', reason='Complete eligible bundle admitted.',
                                        source_ids=list(candidate['direct_support_source_ids']))
                        # An earlier oversized alternative is audit history, not a remaining failure.
                        u.result['diagnostics'] = [d for d in u.result['diagnostics'] if d['dimension'] != 'assembly']
                else:
                    for u in covered:
                        u.result.update(state='budget_incomplete', reason='Complete candidate bundle exceeds global budget.')
                        u.result['diagnostics'].append({'dimension': 'assembly', 'code': 'budget_incomplete',
                                                        'detail': trace[-1]['reason'] + ': ' + cid})
            if not progress:
                break
        plan = {'document_kind': 'task_context_plan', 'request_id': request_id,
                'units': [u.result for u in units], 'context': context,
                'context_tokens': count_tokens(compact(context)), 'selected_root_ids': selected,
                'all_requested_units_accounted_for': True,
                'all_supported_ready_units_covered': all(
                    u.result['state'] == 'supported' for u in units
                    if u.result['interpretation_state'] == 'ready' and u.result['documentary_support_state'] == 'eligible'),
                'has_interpretation_issues': False,
                'has_unserved_units': any(u.result['state'] != 'supported' for u in units)}
        # An unmapped selector must never masquerade as complete coverage.
        if any(u.result['state'] == 'unsupported_selector' or
               u.result['documentary_support_state'] == 'unsupported_selector' or
               any(d['code'] == 'unsupported_selector' for d in u.result['diagnostics']) for u in units):
            plan['all_supported_ready_units_covered'] = False
        audit = {'selection_trace': trace,
                 'unit_gates': [{'task_id': u.task['task_id'], 'item_id': u.item['item_id'],
                                'information': u.information, 'interpretation_state': u.result['interpretation_state'],
                                'documentary_support_state': u.result['documentary_support_state'],
                                'issue_ids': list(u.result['issue_ids'])} for u in units],
                 'context_sha256': hashlib.sha256(compact(context).encode('utf-8')).hexdigest()}
        return plan, audit


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise RequestValidationError([{'pointer': '', 'message': 'Duplicate JSON object key: ' + key}])
        obj[key] = value
    return obj


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New file only; existing files are never overwritten.')
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error('Output already exists; preserve the previous result and choose a new path.')
    try:
        request = json.loads(args.request.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
        result = StructuredControl().evaluate(request)
        # Exclusive creation also protects against a race after the initial existence check.
        with args.output.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
