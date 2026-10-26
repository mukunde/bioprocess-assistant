"""IF01-IF14 runtime conformance, offline and distinct from reviewed design data."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from ingestion.free_text_bridge import FreeTextControl, projection_bytes, record_sizes
from ingestion.free_text_contract import LedgerBuilder, canonical_hash
from ingestion.free_text_interpreter import MappedText
from ingestion.structured_sources import ROOT, read


class FreeTextInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.control=FreeTextControl()
        cls.examples={e['example_id']:e for e in read(ROOT/'docs/experiments/free-text-interface-examples-v01.json')['examples']}

    def setUp(self):
        self.net=patch.object(socket.socket,'connect',side_effect=AssertionError('External calls forbidden'))
        self.net.start();self.addCleanup(self.net.stop)

    def run_text(self,text,language='en'):
        with patch.object(self.control.core,'evaluate',wraps=self.control.core.evaluate) as call:
            out=self.control.evaluate({'language':language,'text':text})
        self.assertEqual(call.call_count,out['core_calls']);self.assertLessEqual(call.call_count,1)
        self.control.contracts.validate('outcome',out)
        if out['core_result']:
            self.assertEqual(canonical_hash(out['core_result']),out['core_result_sha256_canonical'])
            plan=out['core_result']['plan']
            self.assertLessEqual(plan['context_tokens'],2048);self.assertLessEqual(len(plan['selected_root_ids']),6)
            self.assertFalse({p['id'] for p in plan['context']['source_passages']}&{'E118-I','E121-EQ'})
        ledger=out['interpretation_ledger']
        if ledger:
            self.assertEqual(out['request_summary']['known_unit_count'],len(ledger['requested_units']))
            self.assertEqual([u['unit_id'] for u in ledger['requested_units']],[u['unit_id'] for u in out['unit_outcomes']])
        return out

    def example(self,eid):
        e=self.examples[eid];return self.run_text(e['input']['text'],e['input']['language'])

    def classified(self,eid):
        # Explicit test-only entry, never encoded in text or a public input key.
        ledger=deepcopy(self.examples[eid]['expected_output']['ledger'])
        ledger['system_identity']=deepcopy(self.control.identity)
        return ledger

    def test_if01_en_fr_positive_requests_one_call(self):
        for text,lang in ((self.examples['E01']['input']['text'],'en'),
                          ('Pour D on HiTrap Blue HP 1 mL, donne le débit de lavage et les formulations du tampon de fixation.','fr')):
            with self.subTest(lang=lang):
                out=self.run_text(text,lang)
                self.assertIsNone(out['failure']);self.assertEqual(out['core_calls'],1)
                ledger=out['interpretation_ledger']
                self.assertEqual([u['information'] for u in ledger['requested_units']],['flow_rate','buffer_formulation'])
                self.assertEqual(ledger['tasks'][0]['column']['state'],'not_supplied')
                self.assertTrue(out['request_summary']['full_service'])

    def test_if02_conflict_preserves_both_assertions_no_split(self):
        out=self.example('E02');l=out['interpretation_ledger']
        self.assertEqual(len(l['tasks']),1)
        self.assertEqual(l['tasks'][0]['product']['value'],'HiTrap Blue HP 5 mL')
        self.assertEqual(l['tasks'][0]['column']['value']['bed_volume']['value'],'1')
        self.assertEqual(out['core_calls'],1);self.assertFalse(out['request_summary']['full_service'])
        self.assertTrue(out['request_summary']['has_interpretation_issues'])

    def test_if03_unresolved_owner_not_duplicated_independent_c(self):
        out=self.example('E03');units=out['interpretation_ledger']['requested_units']
        self.assertEqual(len(units),2);self.assertEqual(units[0]['owner']['candidate_task_ids'],['A','B'])
        self.assertIsNone(units[0]['owner']['task_id']);self.assertEqual(units[0]['dispatch'],'preblock')
        self.assertEqual([m['core_task_id'] for m in out['projection_mapping']],['C'])
        origins=out['interpretation_ledger']['origins']
        self.assertTrue(any(o.get('quote')=='lavage' or o.get('quote')=='Pour le lavage' for o in origins))
        self.assertFalse(out['unit_outcomes'][0]['source_ids'])

    def test_if04_policy_override_and_warning_conflict_keep_c(self):
        out=self.example('E04');l=out['interpretation_ledger']
        self.assertEqual({i['code'] for i in l['issues']},{'policy_override_rejected','presentation_policy_conflict'})
        self.assertEqual([u['status'] for u in out['unit_outcomes']],['preblocked','planner_evaluated'])
        self.assertEqual([t['task_id'] for t in out['projection']['submission']['tasks']],['C'])

    def test_if05_preclassified_partial_selector_only(self):
        ledger=self.classified('E05');snapshot=deepcopy(ledger)
        out=self.control.evaluate_ledger(ledger)
        self.assertEqual(ledger,snapshot);self.assertIsNone(out['failure'])
        self.assertEqual(out['request_summary']['known_unit_count'],2)
        self.assertEqual([m['information'] for m in out['projection_mapping']],['stopping_criteria'])
        # The same ordinary prose is not a magic parser trigger.
        normal=self.example('E05');self.assertEqual(normal['request_summary']['preblocked_count'],0)

    def test_if05_surviving_selector_keeps_applicable_task_exclusion(self):
        text='A: HiTrap Blue HP 1 mL. Give washing flow and stopping criteria. Exclude operating elution.'
        ledger=self.control.interpreter.interpret({'language':'en','text':text},'preclassified-boundary',self.control.identity)
        builder=LedgerBuilder(ledger['input_snapshot'],ledger['request_id'],self.control.identity);builder.value=ledger
        oid=builder.origin(rule='test-only-preclassified-ledger',reason='Internal harness blocks flow only; no parser inference is claimed.')
        builder.issue('unsupported_construction','Test-only scoped classification.',[oid],[ledger['requested_units'][0]])
        ledger['interpretation_status']='partial'
        out=self.control.evaluate_ledger(ledger)
        self.assertIsNone(out['failure']);self.assertEqual(out['request_summary']['known_unit_count'],2)
        task=out['projection']['submission']['tasks'][0]
        self.assertEqual(task['items'][0]['information'],['stopping_criteria'])
        self.assertEqual(task['exclusions'][0]['selector']['code'],'elution')
        self.assertEqual(task['exclusions'][0]['scope'],{'task_id':'A'})

    def test_if06_all_blocked_no_dummy_core_or_context(self):
        for eid in ('E06','E10'):
            with self.subTest(eid=eid):
                out=self.example(eid);self.assertIsNone(out['failure'])
                self.assertEqual(out['projection']['status'],'empty');self.assertEqual(out['core_calls'],0)
                self.assertIsNone(out['core_result']);self.assertEqual(out['request_summary']['status'],'blocked')

    def test_if07_negation_and_not_only_addition(self):
        out=self.example('E07');x=out['interpretation_ledger']['exclusions']
        self.assertEqual([v['active'] for v in x],[False,True])
        self.assertTrue(out['request_summary']['full_service'])
        out=self.example('E14');self.assertEqual([m['information'] for m in out['projection_mapping']],['stopping_criteria','buffer_formulation'])
        self.assertTrue(out['request_summary']['full_service'])

    def test_if08_false_and_distinct_volume_roles(self):
        out=self.example('E08');task=out['interpretation_ledger']['tasks'][0]
        self.assertIs(task['facts'][0]['value']['value'],False)
        self.assertEqual(task['product']['state'],'not_applicable')
        self.assertTrue(out['request_summary']['full_service'])
        out=self.example('E09');task=out['interpretation_ledger']['tasks'][0]
        self.assertEqual([(f['key'],f['value']['state']) for f in task['facts']],[('sample_volume','provided'),('loaded_volume','unknown')])
        self.assertEqual(task['facts'][0]['value']['value']['value'],'5')
        self.assertEqual(task['column']['state'],'not_supplied')

    def test_if09_unicode_decimal_original_hashes_and_map(self):
        for eid in ('E09','E15'):
            out=self.example(eid);l=out['interpretation_ledger'];text=self.examples[eid]['input']['text']
            self.assertEqual(l['input_snapshot']['text'],text)
            self.assertEqual(l['input_sha256_utf8'],hashlib.sha256(text.encode('utf-8')).hexdigest())
            for o in l['origins']:
                if o['kind']=='text_span':self.assertEqual(text[o['start']:o['end']],o['quote'])
        fact=out['interpretation_ledger']['tasks'][0]['facts'][0]
        self.assertEqual(fact['value']['value'],{'value':'1.0','unit':'mL/min'})
        self.assertTrue(any('1,0' in o.get('quote','') for o in out['interpretation_ledger']['origins']))
        view=MappedText('🧪 e\u0301 DEBIT');self.assertEqual(view.text,'🧪 e debit')
        self.assertEqual(view.span(2,3),(2,4))

    def test_if10_ambiguous_exclusion_keeps_both_requests(self):
        out=self.example('E10');l=out['interpretation_ledger']
        self.assertEqual(len(l['requested_units']),2);self.assertEqual(len(l['exclusions']),1)
        self.assertIsNone(l['exclusions'][0]['task_id'])
        self.assertEqual(l['exclusions'][0]['candidate_task_ids'],['A','B'])
        self.assertEqual(out['request_summary']['preblocked_count'],2)

    def test_if11_core_failure_retains_preblock_and_no_retry(self):
        with patch.object(self.control.core,'evaluate',side_effect=RuntimeError('private failure')) as call:
            out=self.control.evaluate(self.examples['E11']['input'])
        self.assertEqual(call.call_count,1);self.assertEqual(out['core_calls'],1)
        self.assertEqual([u['status'] for u in out['unit_outcomes']],['preblocked','not_evaluated_due_to_error'])
        self.assertEqual(out['failure']['code'],'runtime_error');self.assertIsNone(out['core_result'])
        self.assertNotIn('private failure',json.dumps(out))

    def test_if11_projection_rejection_audit_no_silent_repair(self):
        project=self.control._project
        def corrupt(ledger):
            candidate,mapping=project(ledger);candidate['_test_extra']=True;return candidate,mapping
        with patch.object(self.control,'_project',side_effect=corrupt),patch.object(self.control.core,'evaluate') as core:
            out=self.control.evaluate(self.examples['E16']['input'])
        core.assert_not_called();self.assertEqual(out['core_calls'],0)
        self.assertEqual(out['projection']['status'],'invalid')
        self.assertEqual([u['status'] for u in out['unit_outcomes']],['preblocked','not_evaluated_due_to_error'])
        audit=out['rejection_audit'];self.assertTrue(audit['candidate_value']['_test_extra'])
        self.assertEqual(canonical_hash(audit['candidate_value']),audit['candidate_sha256_canonical'])
        self.assertEqual(audit['validation_errors'][0]['pointer'],'')

    def test_if12_shared_core_semantics_under_one_ordered_id_bijection(self):
        out=self.example('E01');submission=deepcopy(self.examples['E01']['expected_output']['projection']['submission'])
        structured=self.control.core.evaluate(submission,request_id='structured-reference')
        p=out['core_result']['plan'];q=structured['plan']
        self.assertEqual(p['selected_root_ids'],q['selected_root_ids'])
        self.assertEqual(p['context']['source_passages'],q['context']['source_passages'])
        bijection={}
        for pu,qu in zip(p['units'],q['units']):
            for key in ('task_id','item_id'):
                pair=(key,pu[key]);self.assertTrue(pair not in bijection or bijection[pair]==qu[key]);bijection[pair]=qu[key]
            self.assertEqual((pu['information'],pu['state'],pu['source_ids']),(qu['information'],qu['state'],qu['source_ids']))
        self.assertEqual(len(set(bijection.values())),len(bijection))
        self.assertEqual(len(p['context']['bindings']),len(q['context']['bindings']))
        for pb,qb in zip(p['context']['bindings'],q['context']['bindings']):
            clone=deepcopy(pb)
            for key in ('task_id','item_id'):clone[key]=bijection[(key,clone[key])]
            # Reason prose for matrix-inapplicable slots is audit annotation, not supplied meaning.
            def meaning(value):
                if isinstance(value,dict):return {k:meaning(v) for k,v in value.items() if k!='reason'}
                if isinstance(value,list):return [meaning(v) for v in value]
                return value
            self.assertEqual(meaning(clone),meaning(qb))
        self.assertLessEqual(p['context_tokens'],2048);self.assertLessEqual(q['context_tokens'],2048)

    def test_if12_projection_preserves_task_and_item_order(self):
        text='A: HiTrap Blue HP 1 mL. Give washing flow and binding-buffer formulations. B: HiTrap Blue HP 5 mL. Give washing flow and stopping criteria.'
        out=self.run_text(text)
        self.assertEqual([t['task_id'] for t in out['projection']['submission']['tasks']],['A','B'])
        self.assertEqual([m['core_task_id'] for m in out['projection_mapping']],['A','A','B','B'])
        direct=self.control.core.evaluate(out['projection']['submission'])
        self.assertEqual(out['core_result']['audit']['selection_trace'],direct['audit']['selection_trace'])

    def test_if13_missing_origin_rejected_and_incomplete_inventory(self):
        project=self.control._project
        def missing(ledger):
            result=project(ledger)
            ledger['field_origins'][:]=[f for f in ledger['field_origins'] if f['target_pointer']!='/tasks/0/items/0/information/0' or f['target_document']!='projection_submission']
            return result
        with patch.object(self.control,'_project',side_effect=missing),patch.object(self.control.core,'evaluate') as call:
            out=self.control.evaluate(self.examples['E01']['input'])
        call.assert_not_called();self.assertEqual(out['failure']['code'],'projection_error')
        out=self.control.evaluate_ledger(self.classified('E12'))
        self.assertIsNone(out['failure']);self.assertEqual(out['core_calls'],1)
        self.assertEqual(out['request_summary']['status'],'incomplete_inventory')
        self.assertFalse(out['request_summary']['full_service'])

    def test_if14_removed_item_ban_stays_local_shared_fact_survives(self):
        ledger=self.classified('E13');out=self.control.evaluate_ledger(ledger)
        self.assertIsNone(out['failure']);self.assertEqual(len(out['interpretation_ledger']['exclusions']),1)
        task=out['projection']['submission']['tasks'][0]
        self.assertEqual(task['items'][0]['information'],['stopping_criteria'])
        self.assertEqual(task['exclusions'],[])
        self.assertEqual(task['facts'][0]['value']['value'],{'value':'1','unit':'mL/min'})
        self.assertEqual(out['request_summary']['known_unit_count'],2)

    def test_strict_input_and_utf8_rejection_never_calls_core(self):
        invalid=[n['input'] for n in read(ROOT/'docs/experiments/free-text-interface-examples-v01.json')['negative_shape_examples']]
        invalid += [{'language':'en','text':'x'*16001},{'language':'en','text':'\ud800'},
                    {'language':'en','text':'Give washing flow','test_conditions':{}},None]
        with patch.object(self.control.core,'evaluate') as call:
            for value in invalid:
                out=self.control.evaluate(value);self.assertEqual(out['request_summary']['status'],'rejected')
        call.assert_not_called()

    def test_corrupt_ledger_and_identity_rejected_before_core(self):
        for mutation in (lambda l:l['origins'][0].update(quote='wrong'),
                         lambda l:l['requested_units'][0]['owner'].update(task_id='missing'),
                         lambda l:l['system_identity']['interpreter'].update(sha256_lf='0'*64)):
            ledger=self.classified('E05');mutation(ledger)
            out=self.control.evaluate_ledger(ledger);self.assertEqual(out['failure']['stage'],'interpretation');self.assertEqual(out['core_calls'],0)

    def test_no_example_id_or_hidden_fault_routing(self):
        a=self.example('E04');b=self.example('E11');c=self.example('E16')
        self.assertEqual(a['request_summary'],b['request_summary']);self.assertEqual(a['request_summary'],c['request_summary'])
        self.assertTrue(all(r['failure'] is None for r in (a,b,c)))

    def test_unrecognized_additions_and_conditions_are_not_dropped(self):
        for suffix in ('and temperature','at 50 mL/min','unless the pressure is high',
                       'and do something proprietary','si la conductivité augmente','not for B'):
            with self.subTest(suffix=suffix):
                out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow '+suffix+'.')
                self.assertFalse(out['request_summary']['inventory_complete'])
                self.assertFalse(out['request_summary']['full_service']);self.assertEqual(out['core_calls'],0)
                self.assertTrue(out['interpretation_ledger']['unresolved_fragments'])

    def test_unknown_full_label_not_catalog_prefix_or_guessed_format(self):
        for label in ('HiTrap Blue HP 2 mL','HiTrap Blue HP Xtra','HiTrap Blu HP 1 mL'):
            with self.subTest(label=label):
                out=self.run_text('D: '+label+'. Give washing flow.')
                self.assertEqual(out['interpretation_ledger']['tasks'][0]['product']['value'],label)
                self.assertFalse(out['request_summary']['full_service'])
                self.assertEqual(out['core_calls'],1)

    def test_repeated_context_never_overwrites_or_invents_scenarios(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. A: HiTrap Blue HP 5 mL. Give washing flow.')
        self.assertEqual(len(out['interpretation_ledger']['tasks']),1)
        self.assertEqual(out['core_calls'],0)
        assertions=[a['normalized_value'] for a in out['interpretation_ledger']['assertions'] if a['role']=='product']
        self.assertEqual(assertions,['HiTrap Blue HP 1 mL','HiTrap Blue HP 5 mL'])
        out=self.run_text('A: HiTrap Blue HP. Its column size is 1 mL. Its column size is 5 mL. Give washing flow.')
        self.assertEqual(out['core_calls'],0)

    def test_stage_does_not_leak_between_preparations(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow. B: HiTrap Blue HP 5 mL. Give stopping criteria.')
        self.assertEqual([u['dispatch'] for u in out['interpretation_ledger']['requested_units']],['project','preblock'])
        self.assertIsNone(out['interpretation_ledger']['requested_units'][1]['stage'])

    def test_coordinated_phases_are_not_silently_reduced(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing and elution flow.')
        self.assertFalse(out['request_summary']['inventory_complete']);self.assertEqual(out['core_calls'],0)
        out=self.run_text('A: HiTrap Blue HP 1 mL. Give washing flow and stopping criteria for elution.')
        stages=[u['stage']['code'] for u in out['interpretation_ledger']['requested_units']]
        self.assertEqual(stages,['washing','elution'])

    def test_two_preparations_do_not_imply_for_both(self):
        out=self.run_text('A utilise HiTrap Blue HP 1 mL et B utilise HiTrap Blue HP 5 mL. Donne le débit de lavage.','fr')
        self.assertEqual(out['request_summary']['known_unit_count'],1)
        u=out['interpretation_ledger']['requested_units'][0]
        self.assertEqual(u['owner']['candidate_task_ids'],['A','B']);self.assertIsNone(u['owner']['task_id'])
        self.assertEqual(out['core_calls'],0)

    def test_explicit_request_and_exclusion_owners_override_current_scope(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. B: HiTrap Blue HP 5 mL. Give washing flow for A. Exclude washing flow for B.')
        self.assertIsNone(out['failure']);self.assertTrue(out['request_summary']['full_service'])
        self.assertEqual(out['interpretation_ledger']['requested_units'][0]['owner']['task_id'],'A')
        self.assertEqual(out['interpretation_ledger']['exclusions'][0]['task_id'],'B')

    def test_reference_case_id_is_not_a_route_or_a_source_approval(self):
        out=self.run_text('E04. A: HiTrap Blue HP 1 mL. Give washing flow.')
        self.assertFalse(out['request_summary']['full_service'])
        # Unknown text is retained rather than treated as a hidden route selector.
        self.assertTrue(out['interpretation_ledger']['unresolved_fragments'])

    def test_projection_bytes_and_metadata_are_measured_separately(self):
        out=self.example('E01');raw=projection_bytes(out)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),out['projection']['sha256_canonical'])
        sizes=record_sizes(out);self.assertGreater(sizes['ledger_utf8_bytes'],0)
        self.assertGreater(sizes['complete_record_utf8_bytes'],sizes['projection_utf8_bytes'])
        self.assertIsNotNone(out['timings']['core_ms']);self.assertGreater(out['timings']['total_ms'],0)

    def test_decimal_point_zero_and_native_french_scope(self):
        out=self.run_text('Pour D sur HiTrap Blue HP 1 mL. Le débit observé est de 0,0 mL/min. Donne le débit de lavage.','fr')
        self.assertIsNone(out['failure']);self.assertEqual(out['core_calls'],1)
        self.assertEqual(out['interpretation_ledger']['tasks'][0]['facts'][0]['value']['value'],{'value':'0.0','unit':'mL/min'})
        out=self.run_text('D: HiTrap Blue HP 1 mL. My observed flow is 1.0 mL/min. Give washing stopping criteria.')
        self.assertIsNone(out['failure']);self.assertEqual(out['interpretation_ledger']['tasks'][0]['facts'][0]['value']['value']['value'],'1.0')

    def test_native_french_false_condition_keeps_full_origin(self):
        text="Dans le scénario documentaire D, les contaminants mineurs n’interfèrent pas avec l’application prévue. Explique le principe général de la SEC."
        out=self.run_text(text,'fr');self.assertIsNone(out['failure'])
        self.assertIs(out['interpretation_ledger']['tasks'][0]['facts'][0]['value']['value'],False)
        self.assertTrue(out['request_summary']['full_service'])
        self.assertTrue(any(o.get('quote')=='les contaminants mineurs n’interfèrent pas avec l’application prévue' for o in out['interpretation_ledger']['origins']))

    def test_negative_request_does_not_add_a_positive_unit(self):
        out=self.run_text('A: HiTrap Blue HP 1 mL. Do not give washing flow.')
        self.assertEqual(out['request_summary']['known_unit_count'],0)
        self.assertEqual(out['core_calls'],0)
        self.assertEqual(len(out['interpretation_ledger']['exclusions']),1)

    def test_core_return_is_unmodified_and_input_is_independent(self):
        actual=[];evaluate=self.control.core.evaluate
        def capture(value,request_id):
            result=evaluate(value,request_id=request_id);actual.append((result,deepcopy(result)));return result
        with patch.object(self.control.core,'evaluate',side_effect=capture):out=self.control.evaluate(self.examples['E01']['input'])
        self.assertIs(out['core_result'],actual[0][0]);self.assertEqual(out['core_result'],actual[0][1])


if __name__=='__main__':unittest.main()
