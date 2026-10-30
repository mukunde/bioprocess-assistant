"""Documentary journey regressions; no model, database or external service."""
import hashlib
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from demo import troubleshooting as selected
from demo.cytiva import Demo


class TroubleshootingTests(unittest.TestCase):
    def setUp(self):
        guard = patch.object(socket.socket, 'connect', side_effect=AssertionError('No network'))
        guard.start(); self.addCleanup(guard.stop)

    def request(self, product='protein_a', context='unknown'):
        return {'mode': 'troubleshooting', 'product': product, 'deposit_context': context}

    def test_unknown_product_preserves_clarification_scope_without_recipes(self):
        out = selected.evaluate(self.request('unknown', 'hydrophobic_deposits'))
        self.assertEqual(out['state'], 'needs_clarification')
        self.assertFalse(out['options'])
        self.assertEqual([r['question_id'] for r in out['review_scopes']], ['Q09'])
        self.assertFalse({'E166-P','E166-D','E166-E','E167-P','E167-S'} & {p['id'] for p in out['passages']})

    def test_pressure_alone_never_selects_a_deposit_or_a_recipe(self):
        for product in ('protein_a','protein_g'):
            out = selected.evaluate(self.request(product))
            self.assertEqual(out['state'], 'needs_clarification')
            self.assertFalse(out['options'])
            self.assertFalse(out['diagnosis_established'])
            self.assertIn('E166-T', {p['id'] for p in out['passages']})
            self.assertTrue(all(r['reservations'] for r in out['review_scopes']))

    def test_protein_sequence_keeps_product_category_and_original_quantities(self):
        out = selected.evaluate(self.request(context='precipitated_proteins'))
        self.assertEqual(out['state'], 'documented_options')
        self.assertEqual(len(out['options']), 1)
        self.assertEqual(out['options'][0]['source_ids'], ['E166-H','E166-PH','E166-P'])
        source = next(p for p in out['passages'] if p['id']=='E166-P')
        self.assertIn('2 column volumes of 6 M guanidine hydrochloride', source['quote'])
        self.assertIn('Immediately wash with at least 5 column volumes', source['quote'])
        self.assertNotIn('E167-P', {p['id'] for p in out['passages']})

    def test_hydrophobic_alternatives_keep_example_hold_and_separate_warning(self):
        for product in ('protein_a','protein_g'):
            out = selected.evaluate(self.request(product, 'hydrophobic_deposits'))
            self.assertEqual(len(out['options']), 2)
            detergent, ethanol = out['options']
            self.assertEqual(detergent['quote_ids'], ['E166-D'])
            self.assertEqual(ethanol['quote_ids'], ['E166-E','E166-W'])
            self.assertTrue({'E166-H','E166-LH','E166-E','E166-W'} <= set(ethanol['source_ids']))
            quotes = {p['id']:p['quote'] for p in out['passages']}
            self.assertIn('for example', quotes['E166-D'])
            self.assertIn('37\u00b0C for 1 min', quotes['E166-D'])
            self.assertIn('12 h', quotes['E166-E'])
            self.assertIn('Use a lower flow rate', quotes['E166-W'])
            self.assertFalse(any(pid.startswith('E167-') for pid in quotes))

    def test_mabselect_never_receives_sepharose_recipe(self):
        for context in selected.CONTEXTS:
            out = selected.evaluate(self.request('mabselect', context))
            self.assertEqual(out['state'], 'outside_scope')
            self.assertFalse(out['options'])
            self.assertFalse(out['operational_authorization'])

    def test_invalid_fields_and_source_overrides_rejected_before_review_loading(self):
        invalid = [None, [], {}, {**self.request(), 'source_ids':['E121-EQ']},
                   self.request('unlisted'), self.request(context='lipids_confirmed'),
                   self.request([]), self.request(context={}),
                   {**self.request(), 'mode':'text'}]
        for payload in invalid:
            with self.subTest(payload=payload), patch.object(selected, 'verify') as guard:
                with self.assertRaises(ValueError): selected.evaluate(payload)
                guard.assert_not_called()

    def test_unavailable_review_fails_closed(self):
        with patch.object(selected, 'verify', side_effect=ValueError('review unavailable')):
            with self.assertRaisesRegex(ValueError, 'review unavailable'):
                selected.evaluate(self.request(context='hydrophobic_deposits'))

    def test_exact_source_provenance_and_reservations_without_reference_answers(self):
        evidence = json.loads((selected.ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json').read_text(encoding='utf-8'))
        review = json.loads((selected.ROOT/'experiments/cytiva/reviewed-cleaning-retrieval/review.json').read_text(encoding='utf-8'))
        indexed = {p['id']:p for p in evidence['passages']}
        decisions = {d['question_id']:d for d in review['decisions']}
        out = selected.evaluate(self.request(context='hydrophobic_deposits'))
        for p in out['passages']:
            self.assertEqual(p, {k:indexed[p['id']][k] for k in p})
            self.assertEqual(hashlib.sha256(p['quote'].encode()).hexdigest(), p['quote_sha256'])
            self.assertEqual(p['pdf_page_index_0based'], p['pdf_page_1based']-1)
        for r in out['review_scopes']:
            self.assertEqual(r['reservations'], decisions[r['question_id']]['reservations'])
        self.assertNotIn('expected_answer_points', json.dumps(out))
        self.assertEqual((out['model_calls'],out['api_cost_eur']), (0,0))

    def test_loaded_evidence_cannot_change_after_package_validation(self):
        original = Path.read_bytes
        source = selected.ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json'
        def changed(path):
            return b'{}' if path==source else original(path)
        with patch.object(selected, 'verify'), patch.object(Path, 'read_bytes', changed):
            with self.assertRaisesRegex(ValueError, 'changed during evaluation'):
                selected.evaluate(self.request())

    def test_new_journey_does_not_dispatch_through_frozen_engines(self):
        demo = Demo()
        with (patch.object(demo.structured,'evaluate') as structured,
              patch.object(demo.free_text,'evaluate') as text):
            out = demo.evaluate(self.request())
        structured.assert_not_called(); text.assert_not_called()
        self.assertEqual(out['journey'], 'protein-ag-sepharose-backpressure-v01')
