"""MC01–MC12 documentary conformance; no models, database or external network."""
import hashlib
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from demo import mabselect as chosen
from demo.cytiva import Demo
from demo.troubleshooting import evaluate as sepharose
from experiments.cytiva.free_text_v03_freeze import verify


class MabSelectConformanceTests(unittest.TestCase):
    def setUp(self):
        guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('No network'))
        guard.start()
        self.addCleanup(guard.stop)

    def request(self, product='mabselect', context='precipitated_substances'):
        return {'mode': 'mabselect', 'product': product, 'deposit_context': context}

    def run_case(self, product='mabselect', context='precipitated_substances'):
        out = chosen.evaluate(self.request(product, context))
        self.assertFalse(out['diagnosis_established'])
        self.assertFalse(out['operational_authorization'])
        self.assertEqual((out['model_calls'], out['api_cost_eur']), (0, 0))
        return out

    def quotes(self, out):
        return {p['id']: p['quote'] for p in out['passages']}

    def test_MC01_unknown_and_family_only_product_never_select_recipe(self):
        for product in ('unknown', 'family_unknown'):
            for context in chosen.CONTEXTS:
                with self.subTest(product=product, context=context):
                    out = self.run_case(product, context)
                    self.assertEqual(out['state'], 'needs_clarification')
                    self.assertEqual(out['clarification_target'], 'product')
                    self.assertFalse(out['options'])
                    self.assertEqual(set(self.quotes(out)), set(chosen.REQUIRED['Q09']))
                    self.assertFalse({'E167-P','E167-S','E167-D','E167-E'} & set(self.quotes(out)))

    def test_MC02_plain_mabselect_has_four_general_alternatives_with_shared_conditions(self):
        out = self.run_case()
        self.assertEqual(out['state'], 'documented_options')
        self.assertEqual(len(out['options']), 1)
        block = out['options'][0]
        self.assertEqual([' '.join(a['text'].split()) for a in block['alternatives']], [
            '50 mM sodium hydroxide in 500 mM sodium sulfate',
            '50 mM sodium hydroxide in 1 M sodium chloride',
            '100 mM sodium phosphate',
            '6 M guanidine hydrochloride in 10 mM sodium hydroxide'])
        quote = self.quotes(out)['E167-P']
        self.assertIn('2 column volumes', quote)
        self.assertIn('Contact time: at least 10 min.', quote)
        self.assertIn('Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.', quote)
        self.assertEqual(set(self.quotes(out)), set(chosen.REQUIRED['Q05']))
        self.assertNotIn('E167-S', self.quotes(out))

    def test_MC03_sure_keeps_restricted_three_step_sequence_separate(self):
        out = self.run_case('sure')
        self.assertEqual(len(out['options']), 2)
        self.assertEqual(len(out['options'][0]['alternatives']), 4)
        self.assertIn('not consecutive treatments', out['options_intro'])
        restricted = out['options'][1]
        self.assertEqual(restricted['quote_ids'], ['E167-SH', 'E167-S'])
        self.assertEqual(restricted['source_ids'], chosen.REQUIRED['Q06'])
        quote = self.quotes(out)['E167-S']
        self.assertLess(quote.index('1. Wash with 3 column volumes'), quote.index('2. Wash with at least 2 column volumes'))
        self.assertLess(quote.index('Contact time: 10 to 15 min.'), quote.index('3. Immediately wash'))
        self.assertIn('100 mM to 500 mM sodium hydroxide', quote)
        self.assertIn('sterile and filtered binding buffer at  pH 7.0 to 8.0.', quote)

    def test_MC04_sure_lx_has_same_scope_without_concentration_selection(self):
        out = self.run_case('sure_lx')
        self.assertEqual(self.quotes(out), self.quotes(self.run_case('sure')))
        self.assertEqual(out['options'], self.run_case('sure')['options'])
        self.assertNotIn('selected_concentration', out)
        self.assertIn('SuRe LX', out['product'])

    def test_MC05_plain_product_does_not_gain_restricted_block_or_general_naoh_ban(self):
        out = self.run_case()
        self.assertNotIn('E167-SH', self.quotes(out))
        self.assertNotIn('E167-S', self.quotes(out))
        self.assertIn('not a general sodium-hydroxide prohibition', ' '.join(out['limits']))
        self.assertIn('50 mM sodium hydroxide', self.quotes(out)['E167-P'])
        payload = {**self.request(), 'restricted_alkali': True}
        with patch.object(chosen, '_load') as load:
            with self.assertRaises(ValueError):
                chosen.evaluate(payload)
            load.assert_not_called()

    def test_MC06_hydrophobic_context_has_detergent_and_solvent_not_alkali_for_all_products(self):
        for product in ('mabselect', 'sure', 'sure_lx'):
            out = self.run_case(product, 'hydrophobic_deposits')
            self.assertEqual(len(out['options']), 2)
            self.assertEqual(out['options'][0]['quote_ids'], ['E167-D'])
            self.assertEqual(out['options'][1]['quote_ids'], ['E167-E','E167-W'])
            self.assertNotIn('E167-S', self.quotes(out))
            self.assertFalse(any(p.startswith('E166-') for p in self.quotes(out)))
            self.assertIn('ethanol OR 2-propanol', out['options_intro'])

    def test_MC07_detergent_keeps_example_and_following_buffer_ph_without_transfer(self):
        out = self.run_case(context='hydrophobic_deposits')
        quote = self.quotes(out)['E167-D']
        self.assertIn('2 column volumes of a nonionic detergent (e.g., 0.1% solution)', quote)
        self.assertIn('Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.', quote)
        self.assertTrue(all(x not in quote for x in ('Triton','37','1 min')))
        self.assertIn('pH applies to the following binding buffer', ' '.join(out['options'][0]['notes']))
        self.assertEqual(out['options'][0]['source_ids'], chosen.REQUIRED['N06'])

    def test_MC08_solvents_keep_or_immediate_wash_and_two_distinct_precautions(self):
        out = self.run_case(context='hydrophobic_deposits')
        quotes = self.quotes(out)
        self.assertIn('3 to 4 column volumes of 70% ethanol or 30% 2-propanol', quotes['E167-E'])
        self.assertIn('Wash immediately', quotes['E167-E'])
        self.assertIn('pH 7.0 to 8.0', quotes['E167-E'])
        self.assertIn('Apply increasing gradients to avoid air', quotes['E167-E'])
        self.assertIn('Use a lower flow rate', quotes['E167-W'])
        self.assertNotIn('12 h', quotes['E167-E'])
        self.assertNotIn('mL/min', quotes['E167-W'])
        self.assertEqual(out['options'][1]['source_ids'], chosen.REQUIRED['N07'])
        self.assertIn('Increasing gradients address air bubbles; lower flow addresses increased backpressure', ' '.join(out['options'][1]['notes']))

    def test_MC09_unknown_or_mixed_context_retains_product_and_does_not_diagnose(self):
        for product in ('mabselect', 'sure', 'sure_lx'):
            for context in ('unknown', 'mixed_other'):
                out = self.run_case(product, context)
                self.assertEqual(out['product'], chosen.PRODUCTS[product])
                self.assertEqual(out['clarification_target'], 'context')
                self.assertFalse(out['options'])
                self.assertIn('no confirmed diagnosis is required', out['message'])
                self.assertIn('one available deposit category at a time', out['message'])
                self.assertEqual(set(self.quotes(out)), set(chosen.REQUIRED['Q09']))

    def test_MC10_unlisted_conflicting_and_invalid_inputs_do_not_activate_recipes(self):
        self.assertEqual(self.run_case('other')['state'], 'outside_scope')
        self.assertEqual(self.run_case('contradictory')['state'], 'needs_clarification')
        self.assertFalse(self.run_case('other')['options'])
        self.assertFalse(self.run_case('contradictory')['options'])
        invalid = [None, [], {}, self.request('MabSelect SuRe LX other'), self.request([]),
                   self.request(context={}), self.request(context='pressure_only'),
                   {**self.request(), 'source_ids':['E121-EQ']}, {**self.request(), 'mode':'text'}]
        for payload in invalid:
            with self.subTest(payload=payload), patch.object(chosen, '_load') as load:
                with self.assertRaises(ValueError): chosen.evaluate(payload)
                load.assert_not_called()

    def test_MC11_exact_provenance_reservations_and_source_tamper_fail_closed(self):
        ev = json.loads((chosen.ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json').read_bytes())
        source = {p['id']:p for p in ev['passages']}
        q = json.loads((chosen.ROOT/'experiments/cytiva/reviewed-cleaning-retrieval/review.json').read_bytes())
        n = json.loads((chosen.ROOT/'experiments/cytiva/reviewed-section-questions/review.json').read_bytes())
        decisions = {d['question_id']:d for review in (q,n) for d in review['decisions']}
        for context in ('precipitated_substances', 'hydrophobic_deposits'):
            out = self.run_case('sure', context)
            self.assertEqual(out['source_pdf_sha256'], ev['source']['sha256'])
            for p in out['passages']:
                self.assertEqual(p, {k:source[p['id']][k] for k in p})
                self.assertEqual(hashlib.sha256(p['quote'].encode()).hexdigest(), p['quote_sha256'])
                self.assertEqual((p['pdf_page_1based'],p['pdf_page_index_0based']), (167,166))
            for scope in out['review_scopes']:
                self.assertEqual(scope['reservations'], decisions[scope['question_id']]['reservations'])
                self.assertTrue(set(decisions[scope['question_id']]['evidence_sha256']) <= set(self.quotes(out)))
            for option in out['options']:
                for span in option.get('alternatives',[]):
                    p = source[span['source_id']]
                    self.assertEqual(p['quote'][span['page_text_start']-p['page_text_start']:span['page_text_end']-p['page_text_start']], span['text'])
                    self.assertEqual(hashlib.sha256(span['text'].encode()).hexdigest(),span['quote_sha256'])
        read = Path.read_bytes
        for suffix in ('retrieval-pilot-v01/evidence.json','reviewed-cleaning-retrieval/review.json','reviewed-section-questions/review.json'):
            def corrupted(path):
                return b'{}' if path.as_posix().endswith(suffix) else read(path)
            with patch.object(chosen, 'verify_q'), patch.object(chosen, 'verify_n'), patch.object(Path, 'read_bytes', corrupted):
                with self.assertRaisesRegex(ValueError,'changed during evaluation'): self.run_case()
        with patch.object(chosen, 'verify_n', side_effect=ValueError('review unavailable')):
            with self.assertRaisesRegex(ValueError,'review unavailable'): self.run_case()

    def test_MC12_existing_paths_freeze_and_recorded_design_decisions_preserved(self):
        freeze = verify(environment=True)
        self.assertEqual(freeze['pinned_files'], 36)
        demo = Demo()
        with patch.object(demo.structured, 'evaluate') as structured, patch.object(demo.free_text, 'evaluate') as text:
            self.assertEqual(demo.evaluate(self.request())['journey'], 'mabselect-cleaning-v01')
            structured.assert_not_called(); text.assert_not_called()
        old = sepharose({'mode':'troubleshooting','product':'protein_a','deposit_context':'hydrophobic_deposits'})
        self.assertEqual(old['journey'], 'protein-ag-sepharose-backpressure-v01')
        self.assertEqual(old['options'][1]['quote_ids'], ['E166-E','E166-W'])
        self.assertIn('12 h', next(p['quote'] for p in old['passages'] if p['id']=='E166-E'))
        self.assertEqual(chosen.verify_design()['decisions'], 12)
        record = json.loads((chosen.ROOT/'docs/technical/mabselect-cleaning-review-v01.json').read_bytes())
        self.assertEqual({d['id'] for d in record['decisions']}, {f'MS{i:02}' for i in range(1,9)}|{f'C{i}' for i in range(1,5)})
        self.assertTrue(all(d['decision']=='validated' for d in record['decisions']))
