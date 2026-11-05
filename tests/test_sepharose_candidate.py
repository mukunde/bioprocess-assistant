"""Separate non-activated documentary candidate; temporary artifacts only."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from serving import sepharose_candidate as api


def request(product='protein_a', context='hydrophobic_deposits', **kwargs):
    return dict(product=product, deposit_context=context, guidance=True, pressure=False, **kwargs)


class SepharoseCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sepharose-candidate-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'candidate'
        api.prepare(self.root)
        self.service = api.Candidate(self.root, preview=True)

    def held(self, **kwargs):
        target = Path(self.temp.name)/'held'
        api.prepare(target, release_id='held-candidate', **kwargs)
        return api.Candidate(target, preview=True)

    def hashes(self):
        return {p.name: api.sha(p) for p in self.root.iterdir()}

    def test_preparation_is_staged_proposed_and_default_service_refuses(self):
        release = api.read(self.root/'release.json')
        self.assertEqual((release['stage'], release['activation'], release['review_status']),
                         ('staged', 'not_authorized', 'awaiting_user_review'))
        self.assertEqual(set(self.hashes()), {'release.json', 'sources.json', 'mapping.json'})
        self.assertFalse(hasattr(self.service, 'activate'))
        out = api.Candidate(self.root).evaluate(request())
        self.assertEqual((out['status'], out['bundles'], out['serving_activated']), ('unavailable', [], False))

    def test_read_only_all_products_contexts_and_source_views_without_network(self):
        before = self.hashes()
        with patch('socket.socket.connect', side_effect=AssertionError('No network')):
            for product in api.PRODUCTS:
                for context in api.CONTEXTS:
                    with self.subTest(product=product, context=context):
                        out = self.service.evaluate(request(product, context))
                        self.assertNotEqual(out['status'], 'unavailable')
                        self.assertFalse(out['serving_activated'])
                        for ref in out['citations']:
                            view = self.service.source(ref['release_id'], ref['source_id'])
                            self.assertEqual(view['status'], 'available')
                            p = view['passage']
                            self.assertEqual(hashlib.sha256(p['quote'].encode()).hexdigest(), p['quote_sha256'])
                            self.assertEqual(p['pdf_page_index_0based']+1, p['pdf_page_1based'])
                            self.assertIn('page_text_sha256', p)
                            self.assertTrue(view['reviews'][0]['original_human_message'])
        self.assertEqual(before, self.hashes())

    def test_precipitated_sequence_keeps_quantities_immediacy_and_no_mabselect_recipe(self):
        out = self.service.evaluate(request('protein_g', 'precipitated_proteins'))
        self.assertEqual(out['status'], 'supported')
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q01', 'Q02'])
        quote = next(p['quote'] for p in out['bundles'][1]['passages'] if p['source_id'] == 'E166-P')
        self.assertIn('6 M guanidine', quote)
        self.assertIn('Immediately', quote)
        self.assertNotIn('sodium hydroxide', quote)
        self.assertTrue(out['bundles'][1]['review']['reservations'])

    def test_hydrophobic_options_remain_alternatives_and_warning_is_indispensable(self):
        out = self.service.evaluate(request())
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q01', 'Q03', 'Q04'])
        ethanol = out['bundles'][2]
        self.assertEqual(ethanol['quote_ids'], ['E166-E', 'E166-W'])
        self.assertIn('E166-W', ethanol['required_source_ids'])
        self.assertIn('example', out['bundles'][1]['wording'])

    def test_unknown_fields_clarify_without_recipe_or_diagnosis(self):
        for product, context in [('unknown', 'unknown'), ('protein_a', 'unknown')]:
            out = self.service.evaluate(request(product, context))
            self.assertEqual(out['status'], 'needs_clarification')
            self.assertFalse(any(b['role'] == 'conditional_option' for b in out['bundles']))
            self.assertIn('does not establish', out['limits'][0])

    def test_mabselect_outside_scope_and_pressure_abstention_no_numeric_substitute(self):
        out = self.service.evaluate(dict(request('mabselect'), pressure=True))
        self.assertEqual(out['status'], 'abstained')
        self.assertTrue(all(b['scope'] == 'Q09' for b in out['bundles']))
        self.assertFalse(any(p['source_id'] in ('E167-P', 'E167-S') for b in out['bundles'] for p in b['passages']))
        out = self.service.evaluate(dict(request(), guidance=False, pressure=True))
        self.assertEqual((out['status'], out['citations']), ('abstained', []))

    def test_warning_withdrawal_simulation_holds_complete_option_and_source(self):
        held = self.held(withheld_sources=['E166-W'])
        out = held.evaluate(request())
        self.assertEqual(out['status'], 'partial')
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q01', 'Q03'])
        self.assertNotIn('E166-E', [p['source_id'] for p in out['citations']])
        self.assertEqual(held.source(out['release_id'], 'E166-E')['status'], 'quarantined')
        self.assertEqual(held.source(out['release_id'], 'E166-D')['status'], 'available')

    def test_scoped_review_withdrawal_keeps_independent_detergent(self):
        held = self.held(withheld_reviews=['Q04'])
        out = held.evaluate(request())
        self.assertEqual(out['status'], 'partial')
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q01', 'Q03'])
        self.assertEqual(held.source(out['release_id'], 'E166-W')['passage'], None)

    def test_indication_withdrawal_blocks_dependent_pressure_options(self):
        held = self.held(withheld_reviews=['Q01'])
        out = held.evaluate(request())
        self.assertEqual((out['status'], out['bundles'], out['citations']), ('quarantined', [], []))

    def test_bad_requests_cannot_select_root_preview_or_approval(self):
        for value in (None, [], dict(request(), preview=True), dict(request(), root='elsewhere'),
                      dict(request(), guidance='true'), dict(request(), product=[]),
                      dict(request(), guidance=False, pressure=False)):
            self.assertEqual(self.service.evaluate(value)['status'], 'invalid_request')

    def test_withdrawn_indication_cannot_leak_through_clarification_wording(self):
        held = self.held(withheld_reviews=['Q01'])
        out = held.evaluate(request('protein_a', 'unknown'))
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q09'])
        self.assertNotIn('recommends cleaning', out['bundles'][0]['wording'])
        self.assertIn('context', out['bundles'][0]['wording'])
        self.assertEqual(out['status'], 'needs_clarification')
        self.assertEqual(out['items'][0]['held_review_scopes'], ['Q01'])
        self.assertFalse(any(b['role'] == 'conditional_option' for b in out['bundles']))

    def test_withdrawn_clarification_cannot_leak_through_indication_wording(self):
        held = self.held(withheld_reviews=['Q09'])
        out = held.evaluate(request('protein_g', 'unknown'))
        self.assertEqual([b['scope'] for b in out['bundles']], ['Q01'])
        self.assertEqual(out['status'], 'partial')
        self.assertNotIn('context', out['bundles'][0]['wording'])
        self.assertNotIn('?', out['bundles'][0]['wording'])
        self.assertEqual(out['items'][0]['held_review_scopes'], ['Q09'])

    def test_clarification_survives_indication_hold_and_pressure_abstention(self):
        held = self.held(withheld_reviews=['Q01'])
        out = held.evaluate(dict(request('protein_g', 'unknown'), pressure=True))
        self.assertEqual(out['status'], 'needs_clarification')
        self.assertEqual([i['state'] for i in out['items']], ['needs_clarification', 'abstained'])
        self.assertEqual(out['items'][0]['held_review_scopes'], ['Q01'])

    def test_no_clarification_is_claimed_when_all_its_support_is_held(self):
        held = self.held(withheld_reviews=['Q01', 'Q09'])
        out = held.evaluate(request('protein_a', 'unknown'))
        self.assertEqual((out['status'], out['bundles'], out['citations']), ('quarantined', [], []))

    def test_missing_root_and_source_errors_create_nothing(self):
        root = Path(self.temp.name)/'missing'
        service = api.Candidate(root, preview=True)
        self.assertEqual(service.evaluate(request())['status'], 'unavailable')
        self.assertIsNone(service.source('x', '../../private')['passage'])
        self.assertFalse(root.exists())

    def test_never_overwrites_candidate_or_writes_private_authority(self):
        before = self.hashes()
        with self.assertRaises(ValueError):
            api.prepare(self.root)
        self.assertEqual(before, self.hashes())
        protected = Path(self.temp.name)/'private'
        with patch.dict('os.environ', {'MABSELECT_REGISTRY_ROOT': str(protected)}):
            with self.assertRaises(ValueError):
                api.prepare(protected/'child')
        self.assertFalse(protected.exists())

    def test_joint_source_and_digest_tampering_is_rejected(self):
        sources = api.read(self.root/'sources.json')
        sources['passages']['E166-W']['quote'] = 'invented warning'
        (self.root/'sources.json').write_text(json.dumps(sources))
        release = api.read(self.root/'release.json')
        release['artifacts_sha256']['sources.json'] = hashlib.sha256(api.canonical(sources)).hexdigest()
        (self.root/'release.json').write_text(json.dumps(release))
        self.assertEqual(self.service.evaluate(request())['status'], 'unavailable')

    def test_changed_candidate_revokes_old_citation_without_returning_cached_quote(self):
        out = self.service.evaluate(request())
        release = api.read(self.root/'release.json')
        release['withdrawal_simulations']['source_ids'].append('E166-W')
        (self.root/'release.json').write_text(json.dumps(release))
        self.assertIsNone(self.service.source(out['release_id'], 'E166-E')['passage'])
        self.assertEqual(self.service.evaluate(request())['status'], 'unavailable')

    def test_mid_lookup_change_discards_every_quote_and_all_citations(self):
        original = self.service._recheck
        def changed(token):
            (self.root/'mapping.json').write_text('{}')
            original(token)
        with patch.object(self.service, '_recheck', side_effect=changed):
            out = self.service.evaluate(request())
        self.assertEqual((out['status'], out['bundles'], out['citations']), ('unavailable', [], []))

    def test_activation_marker_and_wrong_release_are_not_served(self):
        out = self.service.evaluate(request())
        self.assertIsNone(self.service.source('other-release', out['citations'][0]['source_id'])['passage'])
        (self.root/'active.json').write_text('{}')
        self.assertEqual(self.service.evaluate(request())['status'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
