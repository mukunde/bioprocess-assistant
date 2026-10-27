"""Development regressions, not a new prospective evaluation or frozen rerun."""
from copy import deepcopy
import socket
import unittest
from unittest.mock import patch

from experiments.cytiva import free_text_evaluation as scoring
from experiments.cytiva.structured_evaluation import read, score_case
from ingestion.free_text_bridge import FreeTextControl
from ingestion.free_text_bridge_v02 import FreeTextControlV02
from ingestion.free_text_interpreter_v02 import MappedText, SCOPE
from ingestion.structured_sources import ROOT, local_token_counter
from tests import test_free_text_interface as interface_tests
from tests import test_free_text_review_regressions as review_tests
import re


class V02RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control = FreeTextControlV02()

    def setUp(self):
        guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('No network'))
        guard.start()
        self.addCleanup(guard.stop)

    def run_text(self, text, language='en'):
        with patch.object(self.control.core, 'evaluate', wraps=self.control.core.evaluate) as call:
            out = self.control.evaluate({'language': language, 'text': text})
        self.assertIsNone(out['failure'])
        self.assertEqual(call.call_count, out['core_calls'])
        self.assertLessEqual(call.call_count, 1)
        self.control.contracts.validate('outcome', out)
        for origin in out['interpretation_ledger']['origins']:
            if origin['kind'] == 'text_span':
                self.assertEqual(text[origin['start']:origin['end']], origin['quote'])
        if out['core_result']:
            plan = out['core_result']['plan']
            self.assertFalse({s['id'] for s in plan['context']['source_passages']} & {'E118-I', 'E121-EQ'})
            self.assertLessEqual(plan['context_tokens'], 2048)
            self.assertLessEqual(len(plan['selected_root_ids']), 6)
        return out

    def test_all_reviewed_FT_inputs_are_now_development_regressions(self):
        folder = ROOT / scoring.PACKAGE
        forms = {r['id']: r for r in read(folder/'submissions.json')['submissions']}
        packet = read(folder/'references.json')
        refs = {r['id']: r for r in packet['references']}
        sources = {s['id']: s for s in packet['source_passages']}
        counter = local_token_counter(ROOT, self.control.core.adapter.config['execution_policy']['tokenizer'])
        for question in read(folder/'questions.json')['questions']:
            for lang in ('en', 'fr'):
                with self.subTest(case=question['id'], language=lang):
                    out = self.run_text(question['question_'+lang], lang)
                    intent, tm, im = scoring.intent_score(out, forms[question['id']]['input_'+lang])
                    self.assertTrue(intent['passed'], intent)
                    normalized = scoring.renamed_core(out['core_result'], tm, im)
                    result = score_case(normalized, refs[question['id']]['documentary'], sources)
                    self.assertTrue(result['passed'], result)
                    from ingestion.structured_sources import compact
                    plan = out['core_result']['plan']
                    self.assertEqual(counter(compact(plan['context'])), plan['context_tokens'])

    def test_single_letter_scope_requires_a_complete_token(self):
        for word in ('son', 'sur', 'usage', 'raison'):
            self.assertIsNone(re.search(SCOPE, MappedText(word).text))
        for text, tid in (('Z: HiTrap Blue HP', 'Z'), ('Z sur HiTrap Blue HP', 'Z')):
            self.assertEqual(re.search(SCOPE, MappedText(text).text).group('id').upper(), tid)

    def test_pressure_limits_do_not_inherit_adjacent_washing(self):
        for lang, text in (
            ('en', 'B: HiTrap Blue HP 5 mL. Give washing flow and maximum pressure for B.'),
            ('fr', 'B : HiTrap Blue HP 5 mL. Donne le débit de lavage et la pression maximale pour B.'),
        ):
            out = self.run_text(text, lang)
            units = out['core_result']['plan']['units']
            self.assertEqual([u['state'] for u in units], ['supported', 'missing_source'])
            self.assertEqual(out['interpretation_ledger']['requested_units'][1]['stage'],
                             {'kind': 'general_topic', 'code': 'operating_limits'})

    def test_explicit_pressure_phase_is_not_silently_generalized(self):
        out = self.run_text('B: HiTrap Blue HP 5 mL. Give maximum pressure for washing for B.')
        self.assertEqual(out['interpretation_ledger']['requested_units'][0]['stage'],
                         {'kind': 'operating_phase', 'code': 'washing'})
        self.assertFalse(out['request_summary']['full_service'])

    def test_unknown_substantive_text_remains_blocking(self):
        for lang, text in (
            ('en', 'B: HiTrap Blue HP 5 mL. Give washing flow using a magic correction.'),
            ('fr', 'B : HiTrap Blue HP 5 mL. Donne le débit de lavage avec une correction magique.'),
        ):
            out = self.run_text(text, lang)
            self.assertFalse(out['interpretation_ledger']['inventory_complete'])
            self.assertEqual(out['core_calls'], 0)
            self.assertFalse(out['request_summary']['full_service'])

    def test_independent_sibling_survives_unknown_column(self):
        out = self.run_text('B : HiTrap Blue HP. Le volume de colonne est inconnu. '
                            'L’échantillon contient 2,5 mL disponibles. Le volume chargé est inconnu. '
                            'Donne le débit de lavage pour B. Indépendamment, C demande le principe général de la SEC.', 'fr')
        self.assertEqual([u['summary_state'] for u in out['unit_outcomes']], ['needs_clarification', 'supported'])
        self.assertEqual(out['interpretation_ledger']['tasks'][0]['facts'][0]['value']['value']['value'], '2.5')

    def test_candidate_identity_is_distinct_and_frozen_ledger_is_rejected(self):
        old = FreeTextControl()
        self.assertNotEqual(old.identity['interpreter'], self.control.identity['interpreter'])
        self.assertNotEqual(old.identity['bridge'], self.control.identity['bridge'])
        ledger = old.interpreter.interpret({'language': 'en', 'text': 'B: HiTrap Blue HP 1 mL. Give washing flow.'},
                                         'old-ledger', old.identity)
        with patch.object(self.control.core, 'evaluate') as call:
            out = self.control.evaluate_ledger(deepcopy(ledger))
        call.assert_not_called()
        self.assertEqual(out['failure']['code'], 'invalid_ledger')

    def test_buffer_preparation_does_not_hide_an_additional_bare_phase(self):
        out = self.run_text('B: HiTrap Blue HP 5 mL. List binding-buffer formulations and elution for B.')
        self.assertFalse(out['interpretation_ledger']['inventory_complete'])
        self.assertEqual(out['core_calls'], 0)

    def test_decomposed_unicode_keeps_exact_source_offsets(self):
        import unicodedata
        text = unicodedata.normalize('NFD', 'B : HiTrap Blue HP 5 mL. Liste les formulations du tampon d’élution pour B ; '
                                    'donne séparément les critères de fin du lavage.')
        out = self.run_text(text, 'fr')
        self.assertTrue(out['request_summary']['full_service'])

    def test_new_command_after_restriction_uses_same_projection_boundaries(self):
        for lang, text in (
            ('en', 'B: HiTrap Blue HP 5 mL. Exclude operating elution and list binding-buffer formulations.'),
            ('fr', 'B : HiTrap Blue HP 5 mL. Exclus l’élution opératoire et liste les formulations du tampon de fixation.'),
        ):
            out = self.run_text(text, lang)
            self.assertTrue(out['request_summary']['full_service'])
            item = out['projection']['submission']['tasks'][0]['items'][0]
            self.assertEqual(item['facets']['buffer_use']['value'], 'binding')
            self.assertEqual(len(out['interpretation_ledger']['exclusions']), 1)


class V02InterfaceCompatibilityTests(interface_tests.FreeTextInterfaceTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.control = FreeTextControlV02()


class V02PriorReviewCompatibilityTests(review_tests.ReviewRegressionTests):
    @classmethod
    def setUpClass(cls):
        cls.control = FreeTextControlV02()


if __name__ == '__main__':
    unittest.main()
