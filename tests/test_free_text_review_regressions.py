"""Regressions for the five implementation-review findings; no model/API calls."""
import socket
import unittest
from unittest.mock import patch

from ingestion.free_text_bridge import FreeTextControl


class ReviewRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.control=FreeTextControl()

    def setUp(self):
        p=patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden'))
        p.start();self.addCleanup(p.stop)

    def run_text(self,text,language='en'):
        with patch.object(self.control.core,'evaluate',wraps=self.control.core.evaluate) as core:
            out=self.control.evaluate({'language':language,'text':text})
        self.assertIsNone(out['failure']);self.assertEqual(core.call_count,out['core_calls'])
        self.assertLessEqual(core.call_count,1);self.control.contracts.validate('outcome',out)
        self.assertEqual(len(out['interpretation_ledger']['requested_units']),out['request_summary']['known_unit_count'])
        self.assertEqual(len(out['unit_outcomes']),out['request_summary']['known_unit_count'])
        return out

    def test_r01_mixed_request_and_exclusion_keeps_positive_denominator(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow but do not include washing stopping criteria. Separately, C asks for the general SEC principle.')
        self.assertEqual(out['request_summary']['known_unit_count'],2)
        self.assertEqual([(m['core_task_id'],m['information']) for m in out['projection_mapping']],[('A','flow_rate'),('C','principle')])
        self.assertEqual(out['interpretation_ledger']['exclusions'][0]['selector']['information'],['stopping_criteria'])
        self.assertTrue(out['request_summary']['full_service'])

    def test_r01_binding_facet_not_contaminated_by_later_elution_ban(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow and binding-buffer formulations but do not include operating elution. Separately, C asks for the general SEC principle.')
        self.assertEqual(out['request_summary']['known_unit_count'],3)
        items=out['projection']['submission']['tasks'][0]['items']
        self.assertEqual(items[1]['facets']['buffer_use']['value'],'binding')
        self.assertTrue(out['request_summary']['full_service'])

    def test_r01_restriction_before_positive_command_does_not_consume_it(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Exclude operating elution and give washing flow.')
        self.assertEqual(out['request_summary']['known_unit_count'],1)
        self.assertTrue(out['request_summary']['full_service'])

    def test_r01_french_mixed_clause_preserves_offsets_and_polarity(self):
        text='A utilise HiTrap Blue HP 1 mL. Donne le débit de lavage mais n’exclus pas les critères de fin du lavage.'
        out=self.run_text(text,'fr')
        self.assertEqual(out['request_summary']['known_unit_count'],1)
        self.assertFalse(out['interpretation_ledger']['exclusions'][0]['active'])
        for origin in out['interpretation_ledger']['origins']:
            if origin['kind']=='text_span':self.assertEqual(text[origin['start']:origin['end']],origin['quote'])

    def test_r02_precise_exclusion_does_not_ban_other_information(self):
        for ban in ('Exclude washing stopping criteria.','Exclus les critères de fin du lavage.'):
            out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow. '+ban)
            self.assertEqual(out['projection']['submission']['tasks'][0]['exclusions'][0]['selector']['information'],['stopping_criteria'])
            self.assertTrue(out['request_summary']['full_service'])

    def test_r02_phase_only_coordination_keeps_owner_and_c_independent(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow. Exclude washing and elution. Separately, C asks for the general SEC principle.')
        exclusions=out['interpretation_ledger']['exclusions']
        self.assertEqual([x['task_id'] for x in exclusions],['A','A'])
        self.assertEqual([x['selector']['code'] for x in exclusions],['washing','elution'])
        c=next(u for u in out['unit_outcomes'] if u.get('core_unit_key',{} ) and u['core_unit_key']['task_id']=='C')
        self.assertEqual(c['status'],'planner_evaluated');self.assertEqual(c['summary_state'],'supported')

    def test_r02_unrepresentable_scoped_restriction_blocks_a_not_c(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow. Exclude washing flow and elution stopping criteria. Separately, C asks for the general SEC principle.')
        self.assertEqual([u['status'] for u in out['unit_outcomes']],['preblocked','planner_evaluated'])
        self.assertEqual(out['projection_mapping'][0]['core_task_id'],'C')
        self.assertFalse(out['request_summary']['full_service'])

    def test_r03_inconsistent_unit_selector_or_phase_rejected_before_core(self):
        env={'language':'en','text':'A: HiTrap Blue HP 1 mL. Give washing flow.'}
        for change in ('selector','phase'):
            ledger=self.control.interpreter.interpret(env,'review-'+change,self.control.identity)
            if change=='selector':ledger['requested_units'][0]['information']='stopping_criteria'
            else:ledger['requested_units'][0]['stage']['code']='elution'
            with patch.object(self.control.core,'evaluate') as core:out=self.control.evaluate_ledger(ledger)
            core.assert_not_called();self.assertEqual(out['failure']['stage'],'interpretation')

    def test_r03_forged_ledger_values_cannot_reuse_real_origins(self):
        env={'language':'en','text':'A: HiTrap Blue HP 1 mL. My observed flow is 1 mL/min. Give washing flow.'}
        for forged in ('fact','product'):
            ledger=self.control.interpreter.interpret(env,'forged-'+forged,self.control.identity)
            if forged=='fact':ledger['tasks'][0]['facts'][0]['value']['value']['value']='99'
            else:
                ledger['tasks'][0]['product']['value']='HiTrap Blue HP 5 mL'
                next(a for a in ledger['assertions'] if a['role']=='product')['normalized_value']='HiTrap Blue HP 5 mL'
            with patch.object(self.control.core,'evaluate') as core:out=self.control.evaluate_ledger(ledger)
            core.assert_not_called();self.assertEqual(out['failure']['stage'],'interpretation')

    def test_r03_projection_context_tampering_rejected_with_candidate_audit(self):
        project=self.control._project
        for field in ('product','column','facts'):
            def corrupt(ledger,field=field):
                candidate,mapping=project(ledger)
                if field=='product':candidate['tasks'][0][field]['value']='HiTrap Blue HP 5 mL'
                elif field=='column':candidate['tasks'][0][field]={'state':'provided','value':{'bed_volume':{'value':'5','unit':'mL'}}}
                else:candidate['tasks'][0][field]=[{'key':'observed_flow','input_role':'user_observation','value':{'state':'provided','value':{'value':'99','unit':'mL/min'}}}]
                return candidate,mapping
            with self.subTest(field=field),patch.object(self.control,'_project',side_effect=corrupt),patch.object(self.control.core,'evaluate') as core:
                out=self.control.evaluate({'language':'en','text':'A: HiTrap Blue HP 1 mL. Give washing flow.'})
                core.assert_not_called();self.assertEqual(out['failure']['code'],'projection_error')
                self.assertIsNotNone(out['rejection_audit'])

    def test_r03_projection_cannot_drop_or_widen_an_exclusion(self):
        project=self.control._project
        for widen in (True,False):
            def corrupt(ledger):
                candidate,mapping=project(ledger)
                if widen:candidate['tasks'][0]['exclusions'][0]['selector']['information']='all'
                else:candidate['tasks'][0]['exclusions']=[]
                return candidate,mapping
            with patch.object(self.control,'_project',side_effect=corrupt),patch.object(self.control.core,'evaluate') as core:
                out=self.control.evaluate({'language':'en','text':'A: HiTrap Blue HP 1 mL. Give washing flow. Exclude washing stopping criteria.'})
            core.assert_not_called();self.assertEqual(out['failure']['code'],'projection_error')

    def test_r04_explicit_unknown_column_is_not_not_stated(self):
        for phrase,language in (('Column size is unknown.','en'),('Column size unknown.','en'),('Le volume de colonne est inconnu.','fr')):
            with self.subTest(phrase=phrase):
                text='A: HiTrap Blue HP 1 mL. '+phrase+' Give washing flow.'
                out=self.run_text(text,language);ledger=out['interpretation_ledger']
                self.assertEqual(ledger['tasks'][0]['column'],{'state':'unknown','value':None})
                self.assertEqual(out['projection']['submission']['tasks'][0]['column'],{'state':'unknown','value':None})
                self.assertTrue(any(a['role']=='column' and a['normalized_value'] is None for a in ledger['assertions']))
                refs=[f for f in ledger['field_origins'] if f['target_document']=='ledger' and f['target_pointer']=='/tasks/0/column/state']
                origins={o['origin_id']:o for o in ledger['origins']}
                self.assertTrue(refs);self.assertTrue(all(origins[i]['kind']=='text_span' for f in refs for i in f['origin_ids']))

    def test_r05_each_selector_uses_its_explicit_owner(self):
        for language,request in (('en','Give washing flow for A and stopping criteria for B.'),
                                 ('fr','Donne le débit de lavage pour A et les critères de fin du lavage pour B.')):
            out=self.run_text('A: HiTrap Blue HP 1 mL. B: HiTrap Blue HP 5 mL. '+request,language)
            self.assertEqual([(u['owner']['task_id'],u['information']) for u in out['interpretation_ledger']['requested_units']],[('A','flow_rate'),('B','stopping_criteria')])
            self.assertTrue(out['request_summary']['full_service'])

    def test_r05_prefix_owner_is_not_a_suffix_of_previous_selector(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. B: HiTrap Blue HP 5 mL. Give washing flow for A and for B stopping criteria.')
        self.assertEqual([u['owner']['task_id'] for u in out['interpretation_ledger']['requested_units']],['A','B'])
        self.assertTrue(out['request_summary']['full_service'])
        out=self.run_text('A: HiTrap Blue HP 1 mL. B: HiTrap Blue HP 5 mL. Give washing flow for A and B.')
        self.assertFalse(out['request_summary']['inventory_complete'])
        self.assertFalse(out['request_summary']['full_service'])


if __name__=='__main__':unittest.main()
