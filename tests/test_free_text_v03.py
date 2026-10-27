"""FV is development regression evidence here; original trial remains unchanged."""
from copy import deepcopy
import socket
import unittest
from unittest.mock import patch

from experiments.cytiva import free_text_v02_evaluation as scoring
from experiments.cytiva.structured_evaluation import read, score_case
from ingestion.free_text_bridge_v03 import FreeTextControlV03
from ingestion.structured_sources import ROOT
from tests import test_free_text_interface as interface_tests
from tests import test_free_text_review_regressions as review_tests


class V03RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.control=FreeTextControlV03()

    def setUp(self):
        guard=patch.object(socket.socket,'connect',side_effect=AssertionError('No network'))
        guard.start();self.addCleanup(guard.stop)

    def run_text(self,text,lang='fr'):
        with patch.object(self.control.core,'evaluate',wraps=self.control.core.evaluate) as call:
            out=self.control.evaluate({'language':lang,'text':text})
        old=out['compatibility_outcome']
        self.assertLessEqual(call.call_count,1);self.assertEqual(call.call_count,old['core_calls'])
        for origin in (old['interpretation_ledger'] or {}).get('origins',[]):
            if origin['kind']=='text_span':self.assertEqual(text[origin['start']:origin['end']],origin['quote'])
        if old['core_result']:
            plan=old['core_result']['plan']
            self.assertFalse({p['id'] for p in plan['context']['source_passages']}&{'E118-I','E121-EQ'})
            self.assertLessEqual(plan['context_tokens'],2048);self.assertLessEqual(len(plan['selected_root_ids']),6)
        return out

    def test_coordinated_buffer_nouns_remain_explicitly_unresolved(self):
        for lang,phrase in (
            ('fr','Donne les formulations du tampon de fixation et du tampon d’élution pour B.'),
            ('fr','Donne les formulations du tampon d’élution ou du tampon de fixation pour B.'),
            ('en','List formulations of the binding buffer and the elution buffer for B.'),
            ('en','List binding and elution buffer formulations for B.'),
        ):
            with self.subTest(lang=lang,phrase=phrase):
                out=self.run_text('B : HiTrap Blue HP 1 mL. '+phrase,lang)
                ledger=out['compatibility_outcome']['interpretation_ledger']
                self.assertFalse(out['coverage_summary']['inventory_complete'])
                self.assertFalse(out['coverage_summary']['full_service'])
                self.assertTrue(ledger['unresolved_fragments'])
                self.assertTrue(all(u['dispatch']=='preblock' for u in ledger['requested_units']))
                self.assertTrue(any('tampon' in o.get('quote','') or 'buffer' in o.get('quote','')
                                    for o in ledger['origins'] if o['origin_id'] in ledger['unresolved_fragments'][0]['origin_ids']))

    def test_coordinated_buffers_do_not_disappear_in_multi_task_inventory(self):
        out=self.run_text('B : HiTrap Blue HP 1 mL. Q : HiTrap Blue HP 5 mL. '
                          'Donne les formulations du tampon de fixation et du tampon d’élution pour B. '
                          'Donne le débit de lavage pour Q.')
        ledger=out['compatibility_outcome']['interpretation_ledger']
        self.assertFalse(out['coverage_summary']['inventory_complete'])
        self.assertFalse(out['coverage_summary']['full_service'])
        self.assertEqual({u['owner']['task_id'] for u in ledger['requested_units']},{'B','Q'})
        # Existing conservative unknown-clause policy may block siblings too;
        # it must not erase their owner, request, or explicit outcome.
        self.assertEqual(len(out['compatibility_outcome']['unit_outcomes']),len(ledger['requested_units']))

    def test_inherited_phase_keeps_assertion_and_projected_origins_with_sibling_phase(self):
        import unicodedata
        for text in (
            'B : HiTrap Blue HP 1 mL. Pour le chargement. Donne le débit et les critères de fin du lavage pour B.',
            unicodedata.normalize('NFD','B : HiTrap Blue HP 1 mL. Pour le chargement. Donne le débit et le volume de lavage en volumes de colonne pour B.'),
        ):
            with self.subTest(text=text):
                out=self.run_text(text);old=out['compatibility_outcome'];ledger=old['interpretation_ledger']
                unit=ledger['requested_units'][0];origins={o['origin_id']:o for o in ledger['origins']}
                self.assertEqual(unit['stage']['code'],'sample_application')
                self.assertIn('Pour le chargement',[origins[i].get('quote') for i in unit['origin_ids']])
                stages=[a for a in ledger['assertions'] if a['assertion_id'] in unit['assertion_ids'] and a['role']=='stage']
                self.assertEqual(len(stages),1)
                self.assertEqual(stages[0]['normalized_value'],'sample_application')
                self.assertEqual([origins[i]['quote'] for i in stages[0]['origin_ids']],['Pour le chargement'])
                fields=[f for f in ledger['field_origins'] if f['target_document']=='projection_submission'
                        and f['target_pointer'] in ('/tasks/0/items/0/stage/code','/tasks/0/items/0/stage/kind')]
                self.assertEqual(len(fields),2)
                self.assertTrue(all('Pour le chargement' in [origins[i].get('quote') for i in f['origin_ids']] for f in fields))
                self.assertEqual(ledger['requested_units'][1]['stage']['code'],'washing')

    def test_all_24_FV_intents_and_unit_contexts_as_development_regressions(self):
        folder=ROOT/scoring.PACKAGE
        forms={x['id']:x for x in read(folder/'submissions.json')['submissions']}
        packet=read(folder/'references.json');refs={r['id']:r for r in packet['references']}
        sources={s['id']:s for s in packet['source_passages']}
        for q in read(folder/'questions.json')['questions']:
            for lang in ('en','fr'):
                with self.subTest(case=q['id'],lang=lang):
                    out=self.run_text(q['question_'+lang],lang);old=out['compatibility_outcome']
                    self.assertIsNone(old['failure'])
                    intent,tm,im=scoring.intent_score(old,forms[q['id']]['input_'+lang])
                    self.assertTrue(intent['passed'],intent)
                    result=score_case(scoring.renamed_core(old['core_result'],tm,im),refs[q['id']]['documentary'],sources)
                    # The old aggregate definition is intentionally unchanged.
                    expected=['aggregate:all_supported_ready_units_covered'] if q['id']=='FV06' else []
                    self.assertEqual(result['failures'],expected)
                    if q['id']=='FV06':
                        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'complete')
                        self.assertFalse(out['coverage_summary']['full_service'])

    def test_two_buffer_uses_in_one_clause_keep_focused_facets_and_ids(self):
        for lang,text in (
            ('en','B: HiTrap Blue HP 1 mL. List binding-buffer formulations and elution-buffer formulations for B.'),
            ('fr','B : HiTrap Blue HP 1 mL. Liste les formulations du tampon de fixation et les formulations du tampon d’élution pour B.'),
        ):
            out=self.run_text(text,lang);old=out['compatibility_outcome']
            self.assertIsNone(old['failure'])
            items=old['projection']['submission']['tasks'][0]['items']
            self.assertEqual(len({i['item_id'] for i in items}),2)
            self.assertEqual([i['facets']['buffer_use']['value'] for i in items],['binding','elution'])
            self.assertTrue(out['coverage_summary']['full_service'])

    def test_ambiguous_coordinated_buffer_use_is_not_selected(self):
        out=self.run_text('B: HiTrap Blue HP 1 mL. List binding and elution buffer formulations for B.','en')
        self.assertFalse(out['coverage_summary']['full_service'])

    def test_repeated_same_use_retains_occurrence_identity(self):
        out=self.run_text('B: HiTrap Blue HP 1 mL. List binding-buffer formulations for B. List binding-buffer formulations for B.','en')
        self.assertEqual(out['coverage_summary']['known_requested_units'],2)
        ids=[u['item_id'] for u in out['compatibility_outcome']['interpretation_ledger']['requested_units']]
        self.assertEqual(len(set(ids)),2)

    def test_pressure_after_french_postfix_and_comma_stays_general(self):
        out=self.run_text('B : HiTrap Blue HP 5 mL. Donne le débit d’équilibrage, la pression maximale et le débit de lavage pour B.')
        units=out['compatibility_outcome']['core_result']['plan']['units']
        self.assertEqual([u['state'] for u in units],['quarantined','missing_source','supported'])

    def test_french_explicit_pressure_stage_is_preserved(self):
        out=self.run_text('B : HiTrap Blue HP 5 mL. Donne la pression maximale du lavage pour B.')
        self.assertEqual(out['compatibility_outcome']['core_result']['plan']['units'][0]['state'],'unsupported_selector')
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'not_applicable')

    def test_unknown_text_does_not_get_full_service_from_known_coverage(self):
        out=self.run_text('B : HiTrap Blue HP 1 mL. Donne le débit de lavage avec une correction magique.')
        self.assertFalse(out['coverage_summary']['inventory_complete'])
        self.assertFalse(out['coverage_summary']['full_service'])
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'not_assessed')

    def test_zero_positive_request_is_not_full_service(self):
        out=self.run_text('B: HiTrap Blue HP 1 mL. Exclude operating elution.','en')
        self.assertEqual(out['coverage_summary']['known_requested_units'],0)
        self.assertFalse(out['coverage_summary']['full_service'])
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'not_applicable')

    def test_input_rejection_has_error_coverage_without_core_call(self):
        with patch.object(self.control.core,'evaluate') as call:out=self.control.evaluate({'language':'xx','text':'B'})
        call.assert_not_called();self.assertFalse(out['coverage_summary']['inventory_complete'])
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'error')

    def test_ambiguous_french_buffer_uses_remain_unresolved(self):
        out=self.run_text('B : HiTrap Blue HP 1 mL. Liste les formulations du tampon de fixation et d’élution pour B.')
        self.assertFalse(out['coverage_summary']['full_service'])

    def test_decomposed_french_offsets_and_local_elution_attachment(self):
        import unicodedata
        text=unicodedata.normalize('NFD','B : HiTrap Blue HP 1 mL. Donne le débit d’équilibrage et le débit d’élution pour B.')
        out=self.run_text(text)
        self.assertEqual([u['state'] for u in out['compatibility_outcome']['core_result']['plan']['units']],['quarantined','supported'])

    def test_forged_core_context_does_not_get_a_success_summary(self):
        evaluate=self.control.core.evaluate
        def bad(*a,**kw):
            result=evaluate(*a,**kw);result['plan']['context']['source_passages'][0]['id']='E121-EQ'
            return result
        with patch.object(self.control.core,'evaluate',side_effect=bad):
            out=self.run_text('B : HiTrap Blue HP 1 mL. Donne le débit de lavage pour B.')
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'error')
        self.assertEqual(out['coverage_summary']['request_support']['supported_units'],0)


class CompatibilityHarness(FreeTextControlV03):
    """Exercise existing compatibility guarantees through the new boundary."""
    def evaluate(self,envelope):return super().evaluate(envelope)['compatibility_outcome']
    def evaluate_ledger(self,ledger):return super().evaluate_ledger(ledger)['compatibility_outcome']


class V03InterfaceCompatibilityTests(interface_tests.FreeTextInterfaceTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();cls.control=CompatibilityHarness()


class V03PriorReviewCompatibilityTests(review_tests.ReviewRegressionTests):
    @classmethod
    def setUpClass(cls):cls.control=CompatibilityHarness()


if __name__=='__main__':unittest.main()
