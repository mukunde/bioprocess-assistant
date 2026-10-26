"""CF01-CF12 conformance: typed fixtures, never prospective/gold questions.

Budget boundary fixtures inject an internal deterministic counter to exercise
exact branch limits. Integration checks also use the real pinned local tokenizer.
No model, API, historical trial runner or external source is used.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from ingestion.structured_request import (
    RequestValidationError, StructuredControl, compact, main, pointer,
)
from ingestion.structured_sources import (
    DECISION, ROOT, TECHNICAL, Catalog, IntegrityError, SourceAdapter,
    digest, local_token_counter, read,
)


def slot(value=None, state=None):
    return {'state': state or ('provided' if value is not None else 'not_supplied'), 'value': value}


def na():
    return {'state': 'not_applicable', 'value': None, 'reason': 'Not required for this documentary item.'}


def item(iid='A-wash', stage='washing', information=('flow_rate',), *, use=None,
         mode=None, syringe=None, techniques=None, compare=False):
    kind = ('preparation' if stage == 'buffer_preparation' else
            'general_topic' if stage in ('method_selection', 'product_applicability', 'operating_limits') else
            'operating_phase')
    return {'item_id': iid, 'stage': {'kind': kind, 'code': stage},
            'information': list(information),
            'answer_mode': 'compare_documented_alternatives' if compare else 'single_context',
            'techniques': slot(techniques) if techniques is not None else na(),
            'facets': {'buffer_use': slot(use) if use else na(),
                       'elution_mode': slot(mode) if mode else na(),
                       'syringe_query_mode': slot(syringe) if syringe else na()}}


def task(tid='A', items=None, product='HiTrap Blue HP', size='1', intent='documentary_procedure_lookup'):
    return {'task_id': tid, 'sample_ref': None, 'intent': intent,
            'product': slot(product) if product is not None else na(),
            'column': slot({'bed_volume': {'value': size, 'unit': 'mL'}}) if size else slot(state='unknown'),
            'facts': [], 'items': items or [item()], 'exclusions': []}


def request(*tasks):
    return {'document_kind': 'structured_submission', 'contract_version': 'task-request-0.1-tech-proposed',
            'input_mode': 'structured', 'language': 'en', 'tasks': list(tasks or (task(),))}


def exclusion(stage='washing', information='all', *, eid='exclude-1', tid='A', iid=None, use=None):
    owner = {'task_id': tid}
    if iid:
        owner['item_id'] = iid
    selector = {'kind': 'preparation' if stage == 'buffer_preparation' else 'operating_phase',
                'code': stage, 'information': information}
    if use:
        selector['buffer_use'] = use
    return {'exclusion_id': eid, 'scope': owner, 'selector': selector}


class StructuredConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control = StructuredControl()

    def setUp(self):
        self.network = patch('socket.socket.connect', side_effect=AssertionError('Network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.connection = patch('socket.create_connection', side_effect=AssertionError('Network forbidden'))
        self.connection.start()
        self.addCleanup(self.connection.stop)

    def run_request(self, value):
        original = deepcopy(value)
        result = self.control.evaluate(value)
        self.assertEqual(value, original)
        self.control.validate(result['canonical_request'], 'canonical_request')
        self.control.validate(result['plan'], 'plan_result')
        source_ids = {p['id'] for p in result['plan']['context']['source_passages']}
        self.assertFalse(source_ids & {'E118-I', 'E121-EQ'})
        self.assertLessEqual(result['plan']['context_tokens'], 2048)
        for binding in result['plan']['context']['bindings']:
            self.assertTrue(set(binding['source_ids']) <= source_ids)
        return result

    def units_for_scheduler(self, value):
        self.control.validate(value)
        return self.control._interpret(deepcopy(value), {'issues': [], 'resolved_fields': []})

    def test_cf01_strict_public_boundary_precedes_planning(self):
        cases = []
        bad = request(); bad['source_ids'] = ['E121-EQ']; cases.append(bad)
        bad = request(); bad['tasks'][0]['canonical_product'] = 'forged'; cases.append(bad)
        bad = request(); bad['tasks'][0]['column']['value']['bed_volume']['value'] = 1; cases.append(bad)
        cases.append({'document_kind': 'canonical_request'})
        with patch.object(self.control, '_assemble', side_effect=AssertionError('No planning')):
            for bad in cases:
                with self.subTest(bad=bad), self.assertRaises(RequestValidationError) as error:
                    self.control.evaluate(bad)
                self.assertIn('pointer', error.exception.errors[0])

    def test_cf01_preserves_four_states_false_and_zero(self):
        t = task(items=[item(information=('stopping_criteria',))], size=None)
        t['facts'] = [{'key': 'minor_contaminants_interfere', 'input_role': 'user_observation', 'value': slot(False)},
                      {'key': 'observed_flow', 'input_role': 'user_observation',
                       'value': slot({'value': '0', 'unit': 'mL/min'})},
                      {'key': 'loaded_volume', 'input_role': 'user_assumption', 'value': slot()}]
        r = self.run_request(request(t))
        self.assertEqual(r['canonical_request']['submission']['tasks'][0], t)
        self.assertFalse(r['canonical_request']['issues'])
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')
        self.assertEqual(r['canonical_request']['input_sha256'],
                         hashlib.sha256(compact(request(t), sort_keys=True).encode()).hexdigest())

    def test_cf01_every_structured_origin_resolves_to_preserved_input(self):
        r = self.run_request(request())['canonical_request']
        for entry in r['field_origins']:
            self.assertEqual(entry['origins'], [{'kind': 'form_field', 'pointer': entry['target_pointer']}])
            value = r['input_snapshot']
            for token in entry['target_pointer'].split('/')[1:]:
                token = token.replace('~1', '/').replace('~0', '~')
                value = value[int(token)] if isinstance(value, list) else value[token]
            self.assertNotIsInstance(value, (dict, list))
        self.assertEqual(pointer(['a/b', '~x']), '/a~1b/~0x')

    def test_cf02_wrong_units_zero_bed_and_unsupported_size(self):
        for quantity, code in [({'value': '1', 'unit': 'mL/min'}, 'invalid_unit_role'),
                               ({'value': '0', 'unit': 'mL'}, 'invalid_unit_role'),
                               ({'value': '2', 'unit': 'mL'}, 'unsupported_column_format')]:
            t = task(); t['column']['value']['bed_volume'] = quantity
            r = self.run_request(request(t))
            self.assertIn(code, [i['code'] for i in r['canonical_request']['issues']])
            self.assertFalse(r['plan']['context']['bindings'])

    def test_cf02_sample_volume_never_supplies_column_or_loaded_volume(self):
        t = task(size=None)
        t['facts'] = [{'key': 'sample_volume', 'input_role': 'user_observation',
                       'value': slot({'value': '1', 'unit': 'mL'})}]
        r = self.run_request(request(t))
        self.assertEqual(r['plan']['units'][0]['state'], 'needs_clarification')
        self.assertEqual(r['canonical_request']['submission']['tasks'][0]['facts'], t['facts'])

    def test_cf03_alias_size_is_explicit_and_conflict_never_last_wins(self):
        r = self.run_request(request(task(product='HiTrap Blue HP 5 mL', size=None)))
        self.assertEqual(r['plan']['context']['bindings'][0]['column']['value']['bed_volume']['value'], '5')
        self.assertEqual(r['canonical_request']['submission']['tasks'][0]['column']['state'], 'unknown')
        r = self.run_request(request(task(product='HiTrap Blue HP 5 mL', size='1')))
        self.assertEqual(r['plan']['units'][0]['state'], 'needs_clarification')
        self.assertIn('conflicting_input', [i['code'] for i in r['canonical_request']['issues']])

    def test_cf03_identity_states_and_french_aliases(self):
        for label, code, state in [('HiTrap', 'ambiguous_identity', 'needs_clarification'),
                                   ('HiTrap Phenyl HP', 'out_of_scope_product', 'out_of_scope'),
                                   ('HiTrapp Blue HP', 'unresolved_binding', 'needs_clarification')]:
            r = self.run_request(request(task(product=label)))
            self.assertEqual(r['plan']['units'][0]['state'], state)
            self.assertEqual(r['canonical_request']['issues'][0]['code'], code)
        cat = self.control.adapter.catalog
        self.assertEqual(cat.resolve('  HITRAP\tBlue HP  ')['refs'], ['product:hitrap_blue_hp'])
        self.assertEqual(cat.resolve('\u00e9change ionique', 'technique')['refs'], ['method:iex'])
        self.assertEqual(cat.resolve('echange ionique', 'technique')['refs'], ['method:iex'])
        self.assertEqual(cat.resolve("chromatographie d'exclusion st\u00e9rique", 'technique')['refs'], ['method:sec'])
        malformed = deepcopy(cat.config)
        malformed['ambiguous_labels'].append(' HITRAP BLUE HP ')
        with self.assertRaisesRegex(IntegrityError, 'collision'):
            Catalog(malformed)

    def test_cf04_exclusions_are_task_and_information_scoped(self):
        a = task(items=[item(information=('flow_rate', 'stopping_criteria'))])
        a['exclusions'] = [exclusion(information=['flow_rate'])]
        b = task('B', [item('B-wash')], size='5')
        r = self.run_request(request(a, b))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported', 'supported'])
        self.assertNotIn(('A', 'flow_rate'), [(x['task_id'], x['information']) for x in r['plan']['context']['bindings']])

    def test_cf04_preparation_is_distinct_from_operation(self):
        a = task(items=[item('A-prep', 'buffer_preparation', ('buffer_formulation',), use='elution')])
        a['exclusions'] = [exclusion('elution')]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')
        self.assertNotIn('E121-E', r['plan']['selected_root_ids'])

    def test_cf04_product_context_or_exclusion_does_not_activate_procedural_roles(self):
        a = task(items=[item('A-principle', 'method_selection', ('principle',), techniques=['IEX'])])
        a['exclusions'] = [{'exclusion_id': 'no-blue', 'scope': {'task_id': 'A'},
                            'selector': {'kind': 'product', 'label': 'HiTrap Blue HP'}}]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')
        self.assertEqual(r['plan']['selected_root_ids'], ['E118-M'])
        a = task()
        a['exclusions'] = [{'exclusion_id': 'no-phenyl', 'scope': {'task_id': 'A'},
                            'selector': {'kind': 'product', 'label': 'HiTrap Phenyl HP'}}]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')
        self.assertEqual(r['plan']['selected_root_ids'], ['E121-W'])

    def test_cf04_bad_owner_and_duplicate_ids_never_bind(self):
        a = task(); a['exclusions'] = [exclusion(tid='B')]
        r = self.run_request(request(a))
        self.assertFalse(r['plan']['context']['bindings'])
        r = self.run_request(request(task(), task()))
        self.assertTrue(all(u['state'] == 'needs_clarification' for u in r['plan']['units']))
        self.assertFalse(r['plan']['context']['bindings'])

    def test_cf04_all_operating_exclusion_keeps_preparation(self):
        a = task(items=[item(), item('A-prep', 'buffer_preparation', ('buffer_formulation',), use='binding')])
        a['exclusions'] = [{'exclusion_id': 'no-op', 'scope': {'task_id': 'A'},
                            'selector': {'kind': 'all_operating_information'}}]
        r = self.run_request(request(a))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported'])

    def test_cf05_contradictory_facts_are_preserved_not_split(self):
        a = task(items=[item('A-context', 'method_selection', ('clarification_context',))],
                 intent='context_clarification')
        a['facts'] = [{'key': 'minor_contaminants_interfere', 'input_role': 'user_observation',
                       'value': slot(v)} for v in (True, False)]
        r = self.run_request(request(a))
        self.assertEqual(r['canonical_request']['input_snapshot']['tasks'], [a])
        self.assertEqual(r['plan']['units'][0]['state'], 'needs_clarification')
        issue = next(i for i in r['canonical_request']['issues'] if i['code'] == 'conflicting_input')
        self.assertEqual(len(issue['origins']), 2)
        self.assertFalse(r['plan']['context']['bindings'])

    def test_cf05_explicitly_distinct_scenarios_do_not_conflict(self):
        tasks = []
        for tid, v in [('A', True), ('B', False)]:
            t = task(tid, [item(tid + '-ctx', 'method_selection', ('clarification_context',))],
                     intent='context_clarification')
            t['facts'] = [{'key': 'minor_contaminants_interfere', 'input_role': 'documentary_scenario', 'value': slot(v)}]
            tasks.append(t)
        r = self.run_request(request(*tasks))
        self.assertTrue(all(u['state'] == 'supported' for u in r['plan']['units']))
        self.assertFalse(r['canonical_request']['issues'])

    def test_cf06_unknown_column_blocks_only_flow(self):
        r = self.run_request(request(task(items=[item(information=('flow_rate', 'stopping_criteria'))], size=None)))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported'])
        self.assertEqual([b['information'] for b in r['plan']['context']['bindings']], ['stopping_criteria'])
        self.assertIn('E120-W', r['plan']['context']['bindings'][0]['source_ids'])

    def test_cf06_elution_flow_does_not_require_mode_but_single_quantity_does(self):
        r = self.run_request(request(task(items=[item(stage='elution', information=('flow_rate', 'column_volumes'))])))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['supported', 'needs_clarification'])
        r = self.run_request(request(task(items=[item(stage='elution', information=('column_volumes',), compare=True)], size=None)))
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')

    def test_cf07_quarantine_and_unknown_context_coexist(self):
        for size in (None, '1'):
            a = task(items=[item('A-eq', 'equilibration'), item('A-end', information=('stopping_criteria',))], size=size)
            r = self.run_request(request(a))
            eq = r['plan']['units'][0]
            self.assertEqual(eq['state'], 'quarantined')
            self.assertEqual(eq['documentary_support_state'], 'quarantined')
            self.assertEqual(eq['interpretation_state'], 'needs_clarification' if size is None else 'ready')
            self.assertEqual(r['plan']['units'][1]['state'], 'supported')
            self.assertEqual([b['item_id'] for b in r['plan']['context']['bindings']], ['A-end'])

    def test_cf08_bounded_absence_differs_from_ambiguous_or_unmapped_role(self):
        p = item('A-pressure', 'operating_limits', ('maximum_pressure',))
        r = self.run_request(request(task(items=[p], size=None)))
        self.assertEqual(r['plan']['units'][0]['state'], 'missing_source')
        self.assertIn('25 eligible excerpts', r['plan']['units'][0]['reason'])
        self.assertFalse(r['canonical_request']['issues'])
        r = self.run_request(request(task(items=[p], product='HiTrap')))
        self.assertEqual(r['plan']['units'][0]['documentary_support_state'], 'not_assessed')
        r = self.run_request(request(task(items=[item(information=('maximum_pressure',))])))
        self.assertEqual(r['plan']['units'][0]['state'], 'unsupported_selector')
        self.assertFalse(r['plan']['all_supported_ready_units_covered'])

    def test_cf08_cation_subtype_does_not_unlock_ph_pi_rule(self):
        t = task(items=[item('A-rule', 'method_selection', ('ph_vs_pi_condition', 'principle'),
                              techniques=['\u00e9change cationique'])], product=None, size=None)
        r = self.run_request(request(t))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['quarantined', 'supported'])
        self.assertEqual(r['plan']['selected_root_ids'], ['E118-M'])

    def test_cf08_incompatible_technique_is_not_forced_onto_a_known_source(self):
        a = task(items=[item('A-condition', 'method_selection', ('ph_vs_pi_condition',), techniques=['HIC'])])
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['documentary_support_state'], 'not_assessed')
        self.assertEqual(r['plan']['units'][0]['state'], 'unsupported_selector')
        a = task(items=[item(techniques=['IEX'])])
        r = self.run_request(request(a))
        self.assertFalse(r['plan']['context']['bindings'])
        self.assertEqual(r['plan']['units'][0]['state'], 'unsupported_selector')

    def test_example_is_valid_and_matches_the_specification(self):
        example = read(ROOT / 'examples/structured-control/washing-partial.json')
        r = self.run_request(example)
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported'])

    def test_cf04_invalid_exclusion_is_diagnosed_before_positive_intersection(self):
        a = task()
        a['exclusions'] = [exclusion('buffer_preparation', ['flow_rate'])]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'unsupported_selector')
        self.assertFalse(r['plan']['context']['bindings'])
        self.assertFalse(r['plan']['all_supported_ready_units_covered'])
        issue = r['canonical_request']['issues'][0]
        self.assertEqual(issue['code'], 'unsupported_selector')
        self.assertEqual(issue['origins'], [{'kind': 'form_field', 'pointer': '/tasks/0/exclusions/0'}])

    def test_cf04_invalid_mixed_selector_blocks_only_its_declared_owner(self):
        a = task(items=[item('A-first'), item('A-second')])
        a['exclusions'] = [exclusion(information=['flow_rate', 'maximum_pressure'], iid='A-first')]
        b = task('B', [item('B-wash')])
        r = self.run_request(request(a, b))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['unsupported_selector', 'supported', 'supported'])
        self.assertEqual({x['item_id'] for x in r['plan']['context']['bindings']}, {'A-second', 'B-wash'})

    def test_cf04_valid_nonintersecting_and_quarantined_selectors_remain_legal(self):
        for stage in ('elution', 'equilibration'):
            a = task(); a['exclusions'] = [exclusion(stage, ['flow_rate'])]
            r = self.run_request(request(a))
            self.assertEqual(r['plan']['units'][0]['state'], 'supported')
            self.assertFalse(r['canonical_request']['issues'])
        a = task(items=[item('A-binding', 'buffer_preparation', ('buffer_formulation',), use='binding')])
        a['exclusions'] = [exclusion('buffer_preparation', use='elution')]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'supported')

    def test_cf04_format_qualified_exclusions_do_not_expand_to_other_formats(self):
        for size, excluded in [('1', '5'), ('5', '1')]:
            a = task(size=size)
            a['exclusions'] = [{'exclusion_id': 'exclude-format', 'scope': {'task_id': 'A'},
                                'selector': {'kind': 'product', 'label': 'HiTrap Blue HP ' + excluded + ' mL'}}]
            r = self.run_request(request(a))
            self.assertEqual(r['plan']['units'][0]['state'], 'supported')
            self.assertFalse(r['canonical_request']['issues'])
            resolution = next(x for x in r['canonical_request']['resolved_fields']
                              if x['input_pointer'] == '/tasks/0/exclusions/0/selector/label')
            self.assertEqual(resolution['explicit_column_from_label']['value']['bed_volume'],
                             {'value': excluded, 'unit': 'mL'})
            self.assertEqual(resolution['origins'],
                             [{'kind': 'form_field', 'pointer': '/tasks/0/exclusions/0/selector/label'}])

    def test_cf04_matching_format_and_unqualified_product_exclusions_overlap(self):
        cases = [('1', 'HiTrap Blue HP 1 mL'), ('5.0', 'HiTrap Blue HP 5 mL'),
                 ('1', 'HiTrap Blue HP'), ('5', 'HiTrap Blue HP'), (None, 'HiTrap Blue HP')]
        for size, label in cases:
            a = task(size=size)
            a['exclusions'] = [{'exclusion_id': 'exclude-product', 'scope': {'task_id': 'A'},
                                'selector': {'kind': 'product', 'label': label}}]
            r = self.run_request(request(a))
            self.assertIn('conflicting_exclusion', [x['code'] for x in r['canonical_request']['issues']])
            self.assertFalse(r['plan']['context']['bindings'])

    def test_cf04_unknown_format_is_not_chosen_to_avoid_a_qualified_exclusion(self):
        for state in ('unknown', 'not_supplied', 'not_applicable'):
            a = task(items=[item(information=('stopping_criteria',))], size=None)
            a['column'] = na() if state == 'not_applicable' else slot(state=state)
            a['exclusions'] = [{'exclusion_id': 'exclude-five', 'scope': {'task_id': 'A'},
                                'selector': {'kind': 'product', 'label': 'HiTrap Blue HP 5 mL'}}]
            r = self.run_request(request(a))
            self.assertEqual(r['plan']['units'][0]['state'], 'needs_clarification')
            self.assertIn('unresolved_binding', [x['code'] for x in r['canonical_request']['issues']])
            self.assertFalse(r['plan']['context']['bindings'])
            self.assertEqual(r['canonical_request']['submission']['tasks'][0]['column'], a['column'])

    def test_cf04_exclusion_uses_explicit_positive_alias_size_but_not_conflicting_size(self):
        for size, expected in [(None, 'supported'), ('5', 'needs_clarification')]:
            a = task(product='HiTrap Blue HP 1 mL', size=size)
            a['exclusions'] = [{'exclusion_id': 'exclude-five', 'scope': {'task_id': 'A'},
                                'selector': {'kind': 'product', 'label': 'HiTrap Blue HP 5 mL'}}]
            r = self.run_request(request(a))
            self.assertEqual(r['plan']['units'][0]['state'], expected)
            if size:
                self.assertIn('conflicting_input', [x['code'] for x in r['canonical_request']['issues']])
                self.assertIn('unresolved_binding', [x['code'] for x in r['canonical_request']['issues']])
                self.assertFalse(r['plan']['context']['bindings'])

    def test_cf04_unsupported_but_explicit_format_is_not_reported_as_unknown(self):
        a = task(size='2')
        a['exclusions'] = [{'exclusion_id': 'exclude-five', 'scope': {'task_id': 'A'},
                            'selector': {'kind': 'product', 'label': 'HiTrap Blue HP 5 mL'}}]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'out_of_scope')
        self.assertEqual([x['code'] for x in r['canonical_request']['issues']], ['unsupported_column_format'])
        self.assertFalse(r['plan']['context']['bindings'])

    def test_cf04_qualified_exclusion_retains_item_scope(self):
        a = task(items=[item('A-restricted', information=('stopping_criteria',)),
                       item('A-unrestricted', information=('stopping_criteria',))], size=None)
        a['exclusions'] = [{'exclusion_id': 'exclude-five',
                            'scope': {'task_id': 'A', 'item_id': 'A-restricted'},
                            'selector': {'kind': 'product', 'label': 'HiTrap Blue HP 5 mL'}}]
        r = self.run_request(request(a))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported'])
        self.assertEqual([b['item_id'] for b in r['plan']['context']['bindings']], ['A-unrestricted'])

    def test_cf08_cf11_unmapped_interpretation_cannot_report_complete_coverage(self):
        a = task(items=[item('A-unmapped', techniques=['IEX']),
                       item('A-ready', 'buffer_preparation', ('buffer_formulation',), use='binding')])
        r = self.run_request(request(a))
        self.assertEqual([u['state'] for u in r['plan']['units']], ['unsupported_selector', 'supported'])
        self.assertEqual(r['plan']['units'][0]['documentary_support_state'], 'not_assessed')
        self.assertFalse(r['plan']['all_supported_ready_units_covered'])
        self.assertTrue(r['plan']['has_unserved_units'])
        self.assertTrue(r['plan']['all_requested_units_accounted_for'])

    def test_cf08_cf11_quarantine_summary_cannot_hide_an_invalid_selector(self):
        a = task(items=[item('A-eq', 'equilibration')])
        a['exclusions'] = [exclusion('buffer_preparation', ['flow_rate'])]
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'quarantined')
        self.assertIn('unsupported_selector', [d['code'] for d in r['plan']['units'][0]['diagnostics']])
        self.assertFalse(r['plan']['all_supported_ready_units_covered'])

    def test_cf08_cf11_normal_clarification_and_source_absence_keep_distinct_aggregates(self):
        cases = [task(size=None), task(items=[item('A-pressure', 'operating_limits', ('maximum_pressure',))])]
        for a in cases:
            r = self.run_request(request(a))
            self.assertTrue(r['plan']['all_supported_ready_units_covered'])
            self.assertTrue(r['plan']['has_unserved_units'])
            self.assertTrue(r['plan']['all_requested_units_accounted_for'])

    def test_cf12_compact_admissible_items_before_round_robin(self):
        a = task(items=[item('A-blocked'), item('A-ready', 'method_selection', ('clarification_context',))],
                 size=None, intent='context_clarification')
        b = task('B', [item('B-ready', 'sample_application')])
        r = self.run_request(request(a, b))
        self.assertEqual([x['item_id'] for x in r['audit']['selection_trace']], ['A-ready', 'B-ready'])
        self.assertEqual([u['state'] for u in r['plan']['units']], ['needs_clarification', 'supported', 'supported'])

    def test_cf12_compacted_priority_is_preserved_when_only_one_binding_fits(self):
        a = task(items=[item('A-blocked', information=('maximum_pressure',)),
                       item('A-ready', 'method_selection', ('principle',), techniques=['IEX'])])
        b = task('B', [item('B-ready', 'method_selection', ('clarification_context',))],
                 intent='context_clarification')
        def counter(text):
            count = len(json.loads(text)['bindings'])
            return 0 if not count else 2048 if count == 1 else 2049
        plan, audit = self.control._assemble(self.units_for_scheduler(request(a, b)), counter, 'test')
        self.assertEqual([x['item_id'] for x in audit['selection_trace']], ['A-ready', 'B-ready'])
        self.assertEqual([u['state'] for u in plan['units']], ['unsupported_selector', 'supported', 'budget_incomplete'])
        self.assertEqual([b['task_id'] for b in plan['context']['bindings']], ['A'])
        self.assertEqual(plan['selected_root_ids'], ['E118-M'])

    def test_cf12_partially_blocked_item_remains_in_admissible_item_order(self):
        a = task(items=[item('A-partial', information=('flow_rate', 'stopping_criteria')),
                       item('A-next', 'method_selection', ('principle',), techniques=['IEX'])], size=None)
        b = task('B', [item('B-ready')])
        r = self.run_request(request(a, b))
        self.assertEqual([x['item_id'] for x in r['audit']['selection_trace']], ['A-partial', 'B-ready', 'A-next'])
        self.assertEqual([b['information'] for b in r['plan']['context']['bindings'] if b['item_id'] == 'A-partial'],
                         ['stopping_criteria'])

    def test_cf09_two_buffer_items_keep_separate_bindings_and_exact_formulations(self):
        a = task(items=[item('A-binding', 'buffer_preparation', ('buffer_formulation',), use='binding', compare=True),
                       item('A-elution', 'buffer_preparation', ('buffer_formulation',), use='elution', compare=True)], size=None)
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['selected_root_ids'], ['E121-B'])
        self.assertEqual([b['facets']['buffer_use']['value'] for b in r['plan']['context']['bindings']], ['binding', 'elution'])
        source = next(p for p in r['plan']['context']['source_passages'] if p['id'] == 'E121-B')
        self.assertEqual(source['quote'], self.control.adapter.passages['E121-B']['quote'])
        self.assertNotIn('E121-E', [p['id'] for p in r['plan']['context']['source_passages']])

    def test_cf09_unknown_buffer_use_is_not_silently_comparison(self):
        a = task(items=[item(stage='buffer_preparation', information=('buffer_formulation',), compare=True)])
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['units'][0]['state'], 'needs_clarification')
        self.assertFalse(r['plan']['context']['bindings'])

    def test_cf10_workflow_warning_and_joint_clarification_bundle(self):
        a = task(items=[item('A-position', 'product_applicability', ('relative_position_in_workflow',))])
        r = self.run_request(request(a))
        self.assertEqual(r['plan']['selected_root_ids'], ['E120-A'])
        self.assertEqual([p['id'] for p in r['plan']['context']['source_passages']], ['E120-H', 'E120-A', 'E120-W'])
        self.assertIn('E120-W', r['plan']['context']['bindings'][0]['source_ids'])
        a = task(items=[item('A-context', 'method_selection', ('clarification_context',))], intent='context_clarification')
        r = self.run_request(request(a))
        self.assertEqual(set(r['plan']['selected_root_ids']), {'E118-USE', 'E118-C', 'E118-M'})

    def test_cf10_syringe_reference_is_lookup_not_interpolation(self):
        for size, flow, expected in [('1', '1', 'supported'), ('5', '5.0', 'supported'),
                                      ('1', '0.5', 'unsupported_transformation')]:
            a = task(items=[item(stage='sample_application', information=('syringe_correspondence',),
                                 syringe='reference_flow_check')], size=size)
            a['facts'] = [{'key': 'observed_flow', 'input_role': 'user_observation',
                           'value': slot({'value': flow, 'unit': 'mL/min'})}]
            r = self.run_request(request(a))
            self.assertEqual(r['plan']['units'][0]['state'], expected)
            if expected == 'supported':
                self.assertEqual(r['plan']['selected_root_ids'], ['E121-L'])
                self.assertIn('E121-F', r['plan']['context']['bindings'][0]['source_ids'])

    def test_cf10_corrupt_approved_catalog_is_operational_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [DECISION] + [TECHNICAL / n for n in ('task-request-v01.schema.json',
                                    'task-request-catalog-v01.json', 'task-request-source-adapter-v01.json')]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            with (root / TECHNICAL / 'task-request-catalog-v01.json').open('a', encoding='utf-8') as f:
                f.write(' ')
            with self.assertRaisesRegex(IntegrityError, 'artifact hash'):
                SourceAdapter(root)

    def test_cf10_tokenizer_never_downloads_or_uses_get_encoding(self):
        policy = self.control.adapter.config['execution_policy']['tokenizer']
        with patch('tiktoken.get_encoding', side_effect=AssertionError('No remote/cache loader')):
            counter = local_token_counter(ROOT, policy)
            self.assertGreater(counter('A small local context.'), 0)
            with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(IntegrityError, 'downloads forbidden'):
                local_token_counter(Path(tmp), policy)

    def test_cf11_zero_lexical_score_remains_admissible_and_ranking_is_lexicographic(self):
        candidate = deepcopy(self.control.adapter.config['roles'][2]['candidates'][0])
        rows = self.control.adapter.rank([(candidate, [object()])], [])
        self.assertEqual(rows[0][3]['bm25_raw'], 0)
        self.assertEqual(rows[0][3]['bm25_rounded'], '0E-12')
        more = deepcopy(candidate); more['candidate_id'] = 'more-coverage'
        more['scope_specificity']['product_grade'] = 1
        ranked = self.control.adapter.rank([(candidate, [1]), (more, [1, 2])], [])
        self.assertEqual(ranked[0][1]['candidate_id'], 'more-coverage')
        ranked = self.control.adapter.rank([(more, [1]), (candidate, [1])], [])
        self.assertEqual(ranked[0][1]['candidate_id'], candidate['candidate_id'])

    def test_cf11_reproducible_context_is_independent_of_json_key_order(self):
        def reverse_keys(x):
            if isinstance(x, dict):
                return {k: reverse_keys(v) for k, v in reversed(list(x.items()))}
            return [reverse_keys(v) for v in x] if isinstance(x, list) else x
        a = request()
        first, second = self.run_request(a), self.run_request(reverse_keys(a))
        self.assertEqual(first['audit']['context_sha256'], second['audit']['context_sha256'])
        self.assertEqual(first['canonical_request']['input_sha256'], second['canonical_request']['input_sha256'])
        self.assertEqual(first['audit']['selection_trace'], second['audit']['selection_trace'])

    def test_cf11_ineligible_bundle_is_rejected_before_admission(self):
        units = self.units_for_scheduler(request())
        units[0].candidates[0] = deepcopy(units[0].candidates[0])
        units[0].candidates[0]['required_guard_source_ids'].append('E121-EQ')
        with self.assertRaisesRegex(IntegrityError, 'Ineligible'):
            self.control._assemble(units, lambda _: 1, 'test')

    def test_cf12_exact_token_boundary_and_whole_bundle_rejection(self):
        for cost, expected in [(2048, 'supported'), (2049, 'budget_incomplete')]:
            units = self.units_for_scheduler(request())
            def synthetic_counter(text):
                return cost if json.loads(text)['source_passages'] else 0
            plan, audit = self.control._assemble(units, synthetic_counter, 'test')
            self.assertEqual(plan['units'][0]['state'], expected)
            if cost == 2049:
                self.assertEqual(plan['context'], {'source_passages': [], 'bindings': []})
                self.assertEqual(plan['selected_root_ids'], [])
                self.assertEqual(audit['selection_trace'][0]['reason'], 'token_budget')

    def test_cf12_six_root_cap_is_global_and_joint_candidate_costs_three(self):
        a = task(items=[item('A-ctx', 'method_selection', ('clarification_context',)),
                       item('A-wash'),
                       item('A-buffer', 'buffer_preparation', ('buffer_formulation',), use='binding'),
                       item('A-elute', 'elution', ('flow_rate',)),
                       item('A-position', 'product_applicability', ('relative_position_in_workflow',))],
                 intent='context_clarification')
        plan, audit = self.control._assemble(self.units_for_scheduler(request(a)), lambda _: 1, 'test')
        self.assertEqual(len(plan['selected_root_ids']), 6)
        self.assertEqual(plan['units'][-1]['state'], 'budget_incomplete')
        self.assertEqual(audit['selection_trace'][0]['candidate_distinct_roots'], 3)
        self.assertEqual(audit['selection_trace'][-1]['reason'], 'root_budget')
        self.assertFalse(plan['all_supported_ready_units_covered'])

    def test_cf12_round_robin_and_continue_after_oversized_candidate(self):
        a = task(items=[item('A-load', 'sample_application'),
                       item('A-buffer', 'buffer_preparation', ('buffer_formulation',), use='binding')])
        b = task('B', [item('B-wash'), item('B-elute', 'elution')])
        def counter(text):
            ids = {p['id'] for p in json.loads(text)['source_passages']}
            return 2049 if 'E121-L' in ids else 10
        plan, audit = self.control._assemble(self.units_for_scheduler(request(a, b)), counter, 'test')
        self.assertEqual([r['item_id'] for r in audit['selection_trace']], ['A-load', 'B-wash', 'A-buffer', 'B-elute'])
        self.assertEqual(plan['units'][0]['state'], 'budget_incomplete')
        self.assertEqual(len(plan['selected_root_ids']), 3)
        self.assertNotIn('E121-F', [p['id'] for p in plan['context']['source_passages']])

    def test_cf12_real_counter_includes_bindings_and_shared_sources_are_deduplicated(self):
        one = self.run_request(request())
        two = self.run_request(request(task(), task('B', [item('B-wash')])))
        self.assertEqual(one['plan']['context']['source_passages'], two['plan']['context']['source_passages'])
        self.assertEqual(two['plan']['selected_root_ids'], ['E121-W'])
        self.assertEqual(len(two['plan']['context']['bindings']), 2)
        self.assertGreater(two['plan']['context_tokens'], one['plan']['context_tokens'])
        self.assertEqual(two['plan']['context_tokens'], self.control._count_tokens(compact(two['plan']['context'])))

    def test_cli_exclusive_output_and_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'request.json'; output = root / 'result.json'
            source.write_text(json.dumps(request()), encoding='utf-8')
            main([str(source), '--output', str(output)])
            self.assertEqual(read(output)['plan']['units'][0]['state'], 'supported')
            before = output.read_bytes()
            with patch('ingestion.structured_request.StructuredControl', side_effect=AssertionError('No overwrite')), \
                    patch('sys.stderr'), self.assertRaises(SystemExit):
                main([str(source), '--output', str(output)])
            self.assertEqual(output.read_bytes(), before)
            source.write_text('{"tasks":[],"tasks":[1]}', encoding='utf-8')
            with patch('sys.stderr'), self.assertRaises(SystemExit):
                main([str(source), '--output', str(root / 'new.json')])
            self.assertFalse((root / 'new.json').exists())


if __name__ == '__main__':
    unittest.main()
