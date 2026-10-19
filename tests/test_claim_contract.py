"""Regression cases from the audit, using synthetic evidence, without model calls."""
import unittest
import json
import tempfile
from decimal import Decimal
from pathlib import Path

from pydantic import ValidationError

from ingestion.claim_contract import ClaimExtraction, ConditionGroup, evaluate_conditions
from ingestion.claim_validation import validate_candidate


def fixture():
    refs = ['#/texts/0']
    source = {'elements': [
        {'item_ref': refs[0], 'text': 'Product Alpha. If pressure increases, clean the column. Add 60 to 200 µL of 1 M Tris per milliliter of fraction.', 'original_pages': [1]},
    ], 'source_flags': []}
    entity = lambda eid, kind, name: dict(id=eid, kind=kind, name=name,
        product_kind='prepacked_column' if kind == 'Product' else None, evidence_refs=refs)
    claim = dict(id='cl1', subject_id='a', predicate='PROCEDURE', object_id=None,
        statement='Prepare collection tubes with the stated neutralizing addition.',
        force='required', source_role='protocol', symptom_context='not_applicable',
        scope=dict(product_ids=['p'], process_step_ids=[], status='resolved', evidence_refs=refs),
        condition_groups=[], purposes=[dict(text='Preserve sensitive material activity', evidence_refs=refs)],
        parameters=[dict(id='q', name='addition', value_text='60 to 200 µL per milliliter of fraction',
            quantities=[dict(comparator='range', values=['60', '200'], unit='µL',
                denominator=dict(value='1', unit='mL'), material='Tris', evidence_refs=refs)], evidence_refs=refs)],
        parameter_logic='all', evidence_refs=refs, disposition='review_required', issue_ids=[])
    candidate = dict(schema_version='0.2', entities=[entity('p', 'Product', 'Product Alpha'),
        entity('a', 'Action', 'Prepare tubes'), entity('s', 'Symptom', 'Pressure increase')],
        claims=[claim], source_issues=[])
    return candidate, source


class ClaimContractTests(unittest.TestCase):
    def test_scientific_numbers_are_whole_values_not_components(self):
        from ingestion.claim_validation import numbers
        for text, expected in [('1e-3 M', '0.001'), ('1E+3 M', '1000'),
                               ('2.5e-2 M', '0.025'), ('1 × 10^-3 M', '0.001'),
                               ('2 × 10⁻³ M', '0.002'), ('0,1e-2 M', '0.001'),
                               ('−2e−3 M', '-0.002')]:
            with self.subTest(text=text):
                self.assertEqual(numbers(text), {Decimal(expected)})
        self.assertEqual(numbers('0.1-0.5 M'), {Decimal('0.1'), Decimal('0.5')})

    def test_scientific_quantity_rejects_mantissa_and_accepts_actual_value(self):
        candidate, corpus = fixture()
        corpus['elements'][0]['text'] = 'Product Alpha. Use 1e-3 M NaOH.'
        quantity = candidate['claims'][0]['parameters'][0]['quantities'][0]
        quantity.update(comparator='eq', values=['1'], unit='M', denominator=None, material='NaOH')
        report = validate_candidate(candidate, corpus)
        self.assertIn('cl1:q:quantity_number_not_in_evidence', report['errors'])
        self.assertEqual(report['review_queue_ids'], [])
        quantity['values'] = ['0.001']
        self.assertTrue(validate_candidate(candidate, corpus)['structural_pass'])

    def condition_candidate(self, source, values, unit='pH', operator='between'):
        candidate, corpus = fixture()
        ref = '#/texts/1'
        corpus['elements'].append(dict(item_ref=ref, text=source, original_pages=[1]))
        candidate['claims'][0]['condition_groups'] = [dict(all_of=[dict(
            field='sample_measurement', role='trigger', operator=operator,
            value_kind='decimal', values=values, unit=unit,
            source_text=source, evidence_refs=[ref])])]
        return candidate, corpus

    def test_invented_numeric_condition_is_not_reviewable(self):
        candidate, corpus = self.condition_candidate('If pressure increases', ['999'], 'bar', 'gte')
        report = validate_candidate(candidate, corpus)
        self.assertIn('cl1:condition:sample_measurement:number_not_in_evidence', report['errors'])
        self.assertIn('cl1:condition:sample_measurement:unit_not_in_evidence', report['errors'])
        self.assertEqual(report['review_queue_ids'], [])
        self.assertIsNone(report['claims'][0]['condition_evaluation_without_user_context'])
        self.assertFalse(report['publication_allowed'])

    def test_numeric_condition_checks_its_own_values_and_units(self):
        for source, values, unit, expected in [
            ('sample pH between 6 and 9', ['6', '9'], 'pH', None),
            ('sample pH between 6 and 9', ['6', '10'], 'pH', 'number_not_in_evidence'),
            ('volume between 6 and 9 mL', ['6', '9'], 'pH', 'unit_not_in_evidence'),
            # The parent item contains 1 M, but it is not this condition's evidence.
            ('concentration at least 1e-3 M', ['1'], 'M', 'number_not_in_evidence'),
            ('concentration at least 1e-3 M', ['0.001'], 'M', None),
            ('concentration at least 1 mM', ['1'], 'M', 'unit_not_in_evidence'),
        ]:
            with self.subTest(source=source, values=values, unit=unit):
                operator = 'between' if len(values) == 2 else 'gte'
                candidate, corpus = self.condition_candidate(source, values, unit, operator)
                report = validate_candidate(candidate, corpus)
                if expected:
                    self.assertIn('cl1:condition:sample_measurement:' + expected, report['errors'])
                    self.assertEqual(report['review_queue_ids'], [])
                else:
                    self.assertTrue(report['structural_pass'])
                    self.assertEqual(report['review_queue_ids'], ['cl1'])

    def recommendation_candidate(self):
        candidate, corpus = fixture()
        candidate['claims'][0].update(predicate='RECOMMENDED_FOR', object_id='s',
                                     force='recommended', symptom_context='observed_trigger')
        leaf = dict(field='mode', role='applicability', operator='equals',
                    value_kind='categorical', values=['A'], unit=None,
                    source_text='Mode A', evidence_refs=['#/texts/0'])
        trigger = dict(field='pressure_state', role='trigger', operator='equals',
                       value_kind='categorical', values=['high'], unit=None,
                       source_text='If pressure increases', evidence_refs=['#/texts/0'])
        candidate['claims'][0]['condition_groups'] = [dict(all_of=[leaf, trigger]),
                                                     dict(all_of=[{**leaf, 'values': ['B']}])]
        return candidate, corpus, trigger

    def test_recommendation_cannot_hide_trigger_in_only_one_or_branch(self):
        candidate, corpus, _ = self.recommendation_candidate()
        report = validate_candidate(candidate, corpus)
        self.assertIn('cl1:recommendation_missing_trigger_condition', report['errors'])
        self.assertEqual(report['review_queue_ids'], [])
        self.assertFalse(report['publication_allowed'])

    def test_valid_recommendation_branches_need_observed_symptom(self):
        candidate, corpus, trigger = self.recommendation_candidate()
        candidate['claims'][0]['condition_groups'][1]['all_of'].append(trigger)
        self.assertTrue(validate_candidate(candidate, corpus)['structural_pass'])
        groups = ClaimExtraction.model_validate(candidate).claims[0].condition_groups
        for mode in ('A', 'B'):
            context = dict(mode=dict(value=mode, unit=None))
            self.assertIsNone(evaluate_conditions(groups, context))
            context['pressure_state'] = dict(value='normal', unit=None)
            self.assertFalse(evaluate_conditions(groups, context))
            context['pressure_state']['value'] = 'high'
            self.assertTrue(evaluate_conditions(groups, context))

    def test_purpose_does_not_filter_general_instruction(self):
        candidate, corpus = fixture()
        report = validate_candidate(candidate, corpus)
        self.assertTrue(report['structural_pass'])
        self.assertEqual(report['review_queue_ids'], ['cl1'])
        self.assertFalse(report['publication_allowed'])
        self.assertFalse(report['human_approval'])
        self.assertTrue(evaluate_conditions(ClaimExtraction.model_validate(candidate).claims[0].condition_groups, {}))

    def test_model_cannot_approve_itself(self):
        candidate, _ = fixture()
        candidate['claims'][0]['disposition'] = 'approved'
        with self.assertRaises(ValidationError): ClaimExtraction.model_validate(candidate)

    def test_model_cannot_hide_purpose_in_condition_role(self):
        candidate, _ = fixture()
        candidate['claims'][0]['condition_groups'] = [dict(all_of=[dict(field='purpose',
            role='stated_purpose_context', operator='equals', value_kind='text', values=['preservation'],
            unit=None, source_text='to preserve activity', evidence_refs=['#/texts/0'])])]
        with self.assertRaises(ValidationError): ClaimExtraction.model_validate(candidate)

    def test_no_preventive_recommendation_as_observed_remedy(self):
        candidate, corpus = fixture()
        c = candidate['claims'][0]
        c.update(predicate='RECOMMENDED_FOR', object_id='s', force='recommended', symptom_context='potential_risk')
        report = validate_candidate(candidate, corpus)
        self.assertIn('cl1:recommendation_requires_observed_trigger', report['errors'])
        self.assertEqual(report['review_queue_ids'], [])

    def test_cause_cannot_be_recommendation_target(self):
        candidate, corpus = fixture()
        candidate['entities'][2]['kind'] = 'Cause'
        candidate['claims'][0].update(predicate='RECOMMENDED_FOR', object_id='s')
        self.assertIn('cl1:invalid_endpoints', validate_candidate(candidate, corpus)['errors'])

    def test_flag_blocks_claim_even_when_model_conceals_it(self):
        candidate, corpus = fixture()
        corpus['source_flags'] = [dict(id='f1', evidence_refs=['#/texts/0'], kind='source_conflict', description='Contradictory buffer')]
        report = validate_candidate(candidate, corpus)
        self.assertFalse(report['structural_pass'])
        self.assertEqual(report['review_queue_ids'], [])
        self.assertEqual(report['quarantine_ids'], ['cl1'])

    def test_acknowledged_conflict_stays_quarantined(self):
        candidate, corpus = fixture()
        corpus['source_flags'] = [dict(id='f1', evidence_refs=['#/texts/0'], kind='source_conflict', description='Contradiction')]
        candidate['source_issues'] = [dict(id='f1', kind='source_conflict', description='Contradiction',
            evidence_refs=['#/texts/0'], affected_claim_ids=['cl1'])]
        candidate['claims'][0].update(disposition='quarantine', issue_ids=['f1'])
        report = validate_candidate(candidate, corpus)
        self.assertTrue(report['structural_pass'])
        self.assertEqual(report['claims'][0]['staging_status'], 'quarantined')
        self.assertEqual(report['review_queue_ids'], [])
        self.assertFalse(report['claims'][0]['eligible_for_publication'])

    def test_issue_link_cannot_be_omitted(self):
        candidate, corpus = fixture()
        candidate['source_issues'] = [dict(id='i', kind='unclear_quantity', description='Ambiguous amount',
            evidence_refs=['#/texts/0'], affected_claim_ids=['cl1'])]
        report = validate_candidate(candidate, corpus)
        self.assertIn('cl1:source_issue_requires_linked_quarantine', report['errors'])
        self.assertEqual(report['review_queue_ids'], [])

    def test_quarantine_without_reason_is_invalid(self):
        candidate, corpus = fixture()
        candidate['claims'][0]['disposition'] = 'quarantine'
        self.assertFalse(validate_candidate(candidate, corpus)['structural_pass'])

    def test_bad_entity_evidence_invalidates_whole_batch(self):
        candidate, corpus = fixture()
        candidate['entities'][0]['evidence_refs'] = ['#/texts/999']
        report = validate_candidate(candidate, corpus)
        self.assertEqual(report['review_queue_ids'], [])
        self.assertEqual(report['claims'][0]['staging_status'], 'invalid')

    def test_quantity_change_is_not_grounded(self):
        candidate, corpus = fixture()
        candidate['claims'][0]['parameters'][0]['quantities'][0]['values'] = ['60', '999']
        self.assertIn('cl1:q:quantity_number_not_in_evidence', validate_candidate(candidate, corpus)['errors'])

    def test_molar_is_not_millimolar(self):
        candidate, corpus = fixture()
        corpus['elements'][0]['text'] = 'Add 60 to 200 µL of 1 mM Tris per milliliter.'
        quantity = candidate['claims'][0]['parameters'][0]['quantities'][0]
        quantity.update(comparator='eq', values=['1'], unit='M', denominator=None)
        self.assertIn('cl1:q:quantity_unit_not_in_evidence', validate_candidate(candidate, corpus)['errors'])

    def test_denominator_is_not_silently_added(self):
        candidate, corpus = fixture()
        candidate['claims'][0]['parameters'][0]['quantities'][0]['denominator']['value'] = '5'
        self.assertIn('cl1:q:denominator_number_not_in_evidence', validate_candidate(candidate, corpus)['errors'])

    def test_reversed_or_nonfinite_interval_is_invalid(self):
        candidate, _ = fixture()
        q = candidate['claims'][0]['parameters'][0]['quantities'][0]
        for values in (['200', '60'], ['NaN', '200']):
            q['values'] = values
            with self.assertRaises(ValidationError): ClaimExtraction.model_validate(candidate)

    def test_unresolved_scope_cannot_enter_normal_review(self):
        candidate, corpus = fixture()
        candidate['claims'][0]['scope'].update(status='unresolved', product_ids=[])
        self.assertIn('cl1:unresolved_scope_requires_quarantine', validate_candidate(candidate, corpus)['errors'])

    def test_empty_candidate_is_not_extraction_success(self):
        candidate, corpus = fixture()
        candidate['claims'] = []
        self.assertEqual(validate_candidate(candidate, corpus)['candidate_status'], 'empty_candidate')

    def test_no_condition_evaluation_from_unresolved_prose(self):
        group = ConditionGroup.model_validate(dict(all_of=[dict(field='need', role='trigger',
            operator='source_text', value_kind='text', values=['if required'], unit=None,
            source_text='if required', evidence_refs=['#/texts/0'])]))
        self.assertIsNone(evaluate_conditions([group], {'need': {'value': 'if required', 'unit': None}}))

    def test_numeric_ranges_and_unknown_units(self):
        group = ConditionGroup.model_validate(dict(all_of=[dict(field='sample_pH', role='applicability',
            operator='between', value_kind='decimal', values=['6', '9'], unit='pH',
            source_text='between 6 and 9', evidence_refs=['#/texts/0'])]))
        self.assertTrue(evaluate_conditions([group], {'sample_pH': {'value': '7', 'unit': 'pH'}}))
        self.assertFalse(evaluate_conditions([group], {'sample_pH': {'value': '10', 'unit': 'pH'}}))
        self.assertIsNone(evaluate_conditions([group], {}))
        self.assertIsNone(evaluate_conditions([group], {'sample_pH': {'value': '7', 'unit': 'mL'}}))

    def test_or_of_and_uses_three_valued_logic(self):
        leaf = dict(field='mode', role='applicability', operator='equals', value_kind='categorical',
            values=['A'], unit=None, source_text='mode A', evidence_refs=['#/texts/0'])
        a = ConditionGroup.model_validate(dict(all_of=[leaf]))
        b = ConditionGroup.model_validate(dict(all_of=[{**leaf, 'field': 'other'}]))
        self.assertTrue(evaluate_conditions([a, b], {'mode': {'value': 'A', 'unit': None}}))
        self.assertIsNone(evaluate_conditions([a, b], {'mode': {'value': 'B', 'unit': None}}))
        self.assertFalse(evaluate_conditions([a, b], {'mode': {'value': 'B', 'unit': None}, 'other': {'value': 'B', 'unit': None}}))

    def test_sentence_cannot_be_used_as_not_equals_operand(self):
        for kind in ('text', 'categorical'):
            with self.assertRaises(ValidationError):
                ConditionGroup.model_validate(dict(all_of=[dict(field='sample_pH', role='trigger',
                    operator='not_equals', value_kind=kind, values=['sample pH should be between 6 and 9'],
                    unit=None, source_text='Adjust if required', evidence_refs=['#/texts/0'])]))

    def test_written_repeat_count_is_supported_without_inventing_duration(self):
        from ingestion.claim_validation import numbers
        self.assertIn(2, numbers('Washing (perform this step two times totally)'))
        self.assertNotIn(12, numbers('overnight'))

    def test_schema_has_no_implicit_defaults_or_optional_object_keys(self):
        schema = ClaimExtraction.model_json_schema()
        def walk(node):
            if isinstance(node, dict):
                self.assertNotIn('default', node)
                if node.get('type') == 'object':
                    self.assertFalse(node['additionalProperties'])
                    self.assertEqual(set(node['properties']), set(node['required']))
                for value in node.values(): walk(value)
            elif isinstance(node, list):
                for value in node: walk(value)
        walk(schema)

    def test_changed_frozen_input_is_rejected(self):
        from ingestion.claim_bundle import digest, verify_bundle
        def dump(path, data):
            path.write_text(json.dumps(data), encoding='utf8')
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.claim-contract-test-') as folder:
            root = Path(folder)
            self.assertTrue(root.resolve().is_relative_to(Path(__file__).resolve().parents[1]))
            names = ['source.pdf', 'source-map.json', 'document.json', 'input.json', 'schema.json',
                     'prompt.txt', 'manual-prompt.txt', 'conversion-profile.json', 'review-template.json']
            for name in names: (root / name).write_text('{}', encoding='utf8')
            dump(root / 'schema.json', ClaimExtraction.model_json_schema())
            dump(root / 'plan.json', dict(contract_version='0.2', files={n: digest(root / n) for n in names}))
            verify_bundle(root)
            (root / 'input.json').write_text('{"source_flags": []}', encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'Changed prepared input'):
                verify_bundle(root)


if __name__ == '__main__':
    unittest.main()
