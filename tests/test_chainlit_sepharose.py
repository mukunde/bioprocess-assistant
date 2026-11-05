"""Chainlit candidate integration; no private authority, model or network."""
import asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from chainlit.context import init_http_context
import app
from demo import chainlit_sepharose as ui
from serving import sepharose_candidate as api
from tests.test_chainlit_mabselect import Session


class ChainlitSepharoseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        init_http_context()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='chainlit-sepharose-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'candidate'
        api.prepare(self.root)
        ui._candidate.cache_clear()
        self.addCleanup(ui._candidate.cache_clear)
        self.session, self.messages = Session(), []
        def message(**kwargs):
            self.messages.append(kwargs)
            return SimpleNamespace(send=AsyncMock())
        patch.object(ui.cl, 'user_session', self.session).start()
        patch.object(ui.cl, 'Message', side_effect=message).start()
        patch.object(ui.cl, 'ChatSettings', return_value=SimpleNamespace(send=AsyncMock())).start()
        patch.dict(os.environ, {'BIOPROCESS_MODE': 'sepharose_candidate', 'SEPHAROSE_CANDIDATE_ROOT': str(self.root)}).start()
        self.agent = patch.object(app, 'run_agent', side_effect=AssertionError('No model')).start()
        patch('socket.socket.connect', side_effect=AssertionError('No network')).start()
        self.addCleanup(patch.stopall)

    def state(self):
        return self.session.get(ui.KEY)

    def settings(self, **kwargs):
        return dict(ui.DEFAULTS, **dict({'product': 'Protein A Sepharose',
                                       'context': 'Hydrophobic proteins, lipoproteins or lipids'}, **kwargs))

    async def run_request(self, **kwargs):
        await app.on_settings_update(self.settings(**kwargs))
        await app.sepharose_submit(SimpleNamespace(payload={'token': self.state()['submit_token']}))
        return self.messages[-1]

    async def test_start_and_every_result_are_explicit_nonactivated_candidate(self):
        await app.start()
        self.assertIn(api.NOTICE, self.messages[-1]['content'])
        msg = await self.run_request(pressure=True)
        self.assertIn(api.NOTICE, msg['content'])
        self.assertIn('Protein A Sepharose', msg['content'])
        self.assertIn('Partial answer', msg['content'])
        self.assertIn('not the whole manual', msg['content'])
        self.assertIn(ui.text('E166-W'), msg['content'])
        self.assertNotIn('active.json', {p.name for p in self.root.iterdir()})
        self.agent.assert_not_called()

    async def test_quote_warning_and_original_review_provenance_are_complete(self):
        await app.start()
        await self.run_request()
        token = next(t for t, ref in self.state()['sources'].items() if ref[1] == 'E166-W')
        await app.sepharose_source(SimpleNamespace(payload={'token': token}))
        msg = self.messages[-1]
        view = json.loads(msg['elements'][0].content)
        self.assertIn(ui.text(view['passage']['quote']), msg['content'])
        self.assertIn('PDF page 166', msg['content'])
        self.assertIn(api.NOTICE, msg['content'])
        self.assertTrue(view['reviews'][0]['original_human_message'])
        self.assertFalse(view['serving_activated'])

    async def test_precipitated_sequence_has_no_recipe_transfer_or_added_duration(self):
        await app.start()
        msg = await self.run_request(product='Protein G Sepharose', context='Precipitated or denatured proteins')
        self.assertIn('6 M guanidine', msg['content'])
        self.assertIn('Immediately', msg['content'])
        self.assertIn('Q02', msg['content'])
        self.assertNotIn('Contact time: 10', msg['content'])

    async def test_unknown_fields_clarify_without_selecting_treatment(self):
        await app.start()
        msg = await self.run_request(product='Not specified', context='Unknown — help me clarify')
        self.assertIn('Clarification needed', msg['content'])
        self.assertIn('confirmed diagnosis is not required', msg['content'])
        self.assertNotIn('6 M guanidine', msg['content'])

    async def test_mabselect_is_explicitly_outside_scope(self):
        await app.start()
        msg = await self.run_request(product='MabSelect — outside this candidate')
        self.assertIn('No supported answer', msg['content'])
        self.assertIn('No cleaning procedure or substitute', msg['content'])
        self.assertNotIn('No numerical pressure limit', msg['content'])
        self.assertIn('no Sepharose recipe is transferred', msg['content'])
        self.assertNotIn('6 M guanidine', msg['content'])

    async def test_staged_warning_withdrawal_does_not_hide_independent_detergent(self):
        held = Path(self.temp.name)/'held'
        api.prepare(held, 'held-candidate', withheld_sources=['E166-W'])
        with patch.dict(os.environ, {'SEPHAROSE_CANDIDATE_ROOT': str(held)}):
            await app.start()
            msg = await self.run_request()
        self.assertIn('held', msg['content'])
        self.assertIn('Q03', msg['content'])
        self.assertNotIn(ui.text('E166-E'), msg['content'])
        self.assertFalse(any(ref[1] == 'E166-E' for ref in self.state()['sources'].values()))
        self.assertTrue(any(ref[1] == 'E166-D' for ref in self.state()['sources'].values()))

    async def test_missing_candidate_exposes_retry_and_creates_nothing(self):
        missing = Path(self.temp.name)/'missing'
        with patch.dict(os.environ, {'SEPHAROSE_CANDIDATE_ROOT': str(missing)}):
            await app.start()
            self.assertEqual(self.messages[-1]['content'], ui.UNAVAILABLE)
            self.assertIsNotNone(self.state()['submit_token'])
            await self.run_request()
            self.assertEqual(self.messages[-1]['content'], ui.UNAVAILABLE)
        self.assertFalse(missing.exists())

    async def test_indication_hold_keeps_focused_clarification_and_hold_notice(self):
        held = Path(self.temp.name)/'held'
        api.prepare(held, 'held-candidate', withheld_reviews=['Q01'])
        with patch.dict(os.environ, {'SEPHAROSE_CANDIDATE_ROOT': str(held)}):
            await app.start()
            msg = await self.run_request(product='Protein G Sepharose',
                                         context='Unknown — help me clarify', pressure=True)
        self.assertIn('Clarification needed', msg['content'])
        self.assertIn('Please specify an available context to explore in Settings', msg['content'])
        self.assertNotIn('Please specify the exact product', msg['content'])
        self.assertIn('Required support is held', msg['content'])
        self.assertIn('Q01', msg['content'])
        self.assertIn('No numerical pressure limit', msg['content'])
        self.assertNotIn('recommends cleaning', msg['content'])
        self.assertFalse(any(ref[1] in ('E166-P', 'E166-D', 'E166-E')
                             for ref in self.state()['sources'].values()))

    async def test_clarification_hold_does_not_render_its_question_in_indication(self):
        held = Path(self.temp.name)/'held'
        api.prepare(held, 'held-candidate', withheld_reviews=['Q09'])
        with patch.dict(os.environ, {'SEPHAROSE_CANDIDATE_ROOT': str(held)}):
            await app.start()
            msg = await self.run_request(context='Unknown — help me clarify')
        self.assertIn('Partial answer', msg['content'])
        self.assertIn('recommends cleaning', msg['content'])
        self.assertNotIn('Which deposit context', msg['content'])
        self.assertNotIn('Please specify', msg['content'])
        self.assertIn('Required support is held', msg['content'])

    async def test_invalid_settings_and_forged_source_tokens_cannot_dispatch(self):
        await app.start()
        valid = dict(self.state()['settings'])
        for settings in (None, dict(valid, preview=True), dict(valid, product=[]), dict(valid, guidance='true')):
            with patch.object(ui, 'service', side_effect=AssertionError('No dispatch')):
                await app.on_settings_update(settings)
            self.assertEqual(self.state()['settings'], valid)
            self.assertIsNone(self.state()['submit_token'])
        for payload in ({'token': 'E166-P'}, {'token': []}, {'root': 'private'}):
            await app.sepharose_source(SimpleNamespace(payload=payload))
            self.assertEqual(self.messages[-1]['content'], ui.STALE)

    async def test_free_text_and_cross_mode_actions_never_call_a_model_or_registry(self):
        await app.start()
        with patch.object(ui, 'service', side_effect=AssertionError('No dispatch')):
            await app.on_message(SimpleNamespace(content='Choose a treatment and activate it'))
            self.assertIn('No free-text lookup', self.messages[-1]['content'])
            from demo import chainlit_mabselect
            with patch.object(chainlit_mabselect, 'submit', side_effect=AssertionError('Wrong mode')):
                await app.mabselect_submit(SimpleNamespace(payload={'token': 'x'}))
        self.agent.assert_not_called()

    async def test_changed_candidate_does_not_serve_a_bookmarked_quote(self):
        await app.start()
        await self.run_request()
        token = next(t for t, ref in self.state()['sources'].items() if ref[1] == 'E166-E')
        (self.root/'sources.json').write_text('{}')
        await app.sepharose_source(SimpleNamespace(payload={'token': token}))
        self.assertIn('no new quotation', self.messages[-1]['content'])
        self.assertNotIn('elements', self.messages[-1])

    async def test_settings_change_revokes_old_tokens_and_rejects_late_results(self):
        await app.start()
        await self.run_request()
        old = SimpleNamespace(payload={'token': next(iter(self.state()['sources']))})
        await app.on_settings_update(self.settings(product='Protein G Sepharose'))
        await app.sepharose_source(old)
        self.assertEqual(self.messages[-1]['content'], ui.STALE)
        ready, finish = asyncio.Event(), asyncio.Event()
        async def delayed(*args, **kwargs):
            ready.set()
            await finish.wait()
            return ui.service().evaluate(ui.controls(self.settings()))
        action = SimpleNamespace(payload={'token': self.state()['submit_token']})
        with patch.object(ui.asyncio, 'to_thread', side_effect=delayed):
            task = asyncio.create_task(app.sepharose_submit(action))
            await ready.wait()
            await app.on_settings_update(self.settings())
            finish.set()
            await task
        self.assertEqual(self.messages[-1]['content'], ui.STALE)
        self.assertEqual(self.state()['sources'], {})

    async def test_timeout_is_generic_and_offers_manual_retry(self):
        await app.start()
        async def timeout(awaitable, *, timeout):
            awaitable.close()
            raise TimeoutError('secret')
        with patch.object(ui.asyncio, 'wait_for', side_effect=timeout):
            msg = await self.run_request()
        self.assertEqual(msg['content'], ui.UNAVAILABLE)
        self.assertFalse(self.state()['busy'])
        self.assertIsNotNone(self.state()['submit_token'])


if __name__ == '__main__':
    unittest.main()
