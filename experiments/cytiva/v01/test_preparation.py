import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path
from experiments.cytiva.v01.check_result import check
from experiments.cytiva.paths import V01 as HERE

def read(name): return json.loads((HERE/name).read_text(encoding='utf-8'))

@unittest.skipUnless((HERE/'input.json').exists(), 'Private frozen v0.1 artifacts are not present in this checkout')
class PreparationTests(unittest.TestCase):
    def test_identical_inputs_without_reference_answers(self):
        a,b=read('request-sonnet.json'),read('request-sol.json')
        self.assertEqual(a['system'],b['instructions'])
        self.assertEqual(a['messages'][0]['content'],b['input'])
        self.assertEqual(a['output_config']['format']['schema'],b['text']['format']['schema'])
        self.assertNotIn('expected_cards_to_review',b['input'])
        self.assertNotIn('review_focus',b['input'])
    def test_budget_is_shared_and_counts_maximum_outputs(self):
        p=read('plan.json')
        total=sum(Decimal(r['reserved_eur_with_margin']) for r in p['reservations'].values())
        self.assertEqual(total,Decimal(p['total_reserved_eur']))
        self.assertLessEqual(total,Decimal('1'))
        self.assertEqual(p['max_generation_attempts_total'],2)
        self.assertEqual(p['automatic_retries'],0)
        for r in p['reservations'].values():
            expected=(Decimal(r['input_tokens_ceiling'])*2+Decimal(r['output_tokens_ceiling'])*10)/1000000
            self.assertEqual(Decimal(r['reserved_usd']),expected)
    def fixture(self):
        return dict(entities=[dict(id='a',kind='Action',name='Clean column'),dict(id='s',kind='Symptom',name='Pressure increase')],
                    claims=[dict(id='r',subject_id='a',predicate='RECOMMENDED_FOR',object_id='s',modality='recommended',
                                 conditions=[],parameters=[],evidence_refs=['#/texts/78'],scope_refs=['#/texts/0'])],uncertainties=[])
    def run_check(self,value): return check(value,read('schema.json'),read('input.json'))
    def test_valid_refs_do_not_approve_semantics(self):
        r=self.run_check(self.fixture())
        self.assertTrue(r['structural_pass'])
        self.assertFalse(r['manual_approval'])
        self.assertEqual(r['semantic_validation'],'not_performed')
    def test_fake_reference_rejected(self):
        v=self.fixture();v['claims'][0]['evidence_refs']=['#/texts/9999']
        self.assertFalse(self.run_check(v)['structural_pass'])
    def test_inverted_relation_rejected(self):
        v=self.fixture();v['claims'][0]['subject_id']='s';v['claims'][0]['object_id']='a'
        self.assertFalse(self.run_check(v)['structural_pass'])
    def test_empty_result_not_success(self):
        self.assertFalse(self.run_check(dict(entities=[],claims=[],uncertainties=[]))['structural_pass'])
    def test_parameter_without_evidence_rejected(self):
        v=self.fixture();v['claims'][0]['parameters']=[dict(name='time',value_text='10 min',evidence_refs=[])]
        self.assertFalse(self.run_check(v)['structural_pass'])

if __name__=='__main__': unittest.main()
