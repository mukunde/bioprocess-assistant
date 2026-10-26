"""Freeze/scorer safeguards using toy outputs, never real S planning."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import platform
import socket
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva import structured_evaluation as subject


def toy():
    quote = 'Synthetic support, not a Cytiva statement.'
    sources = {sid: {'id': sid, 'pdf_page_1based': 1, 'pdf_page_index_0based': 0,
        'scope': 'Synthetic fixture only', 'quote': quote, 'quote_sha256': hashlib.sha256(quote.encode()).hexdigest(),
        'page_text_start': 0, 'page_text_end': len(quote)} for sid in ('toy-heading', 'toy-support')}
    unit = {'task_id': 'A', 'item_id': 'A-item', 'information': 'flow_rate', 'state': 'supported',
            'interpretation_state': 'ready', 'documentary_support_state': 'eligible',
            'source_ids': ['toy-support'], 'diagnostics': [], 'reason': 'Synthetic output'}
    binding = {'task_id': 'A', 'item_id': 'A-item', 'information': 'flow_rate',
               'source_ids': ['toy-heading', 'toy-support'], 'product_ref': 'toy-product',
               'stage': {'kind': 'operating_phase', 'code': 'washing'},
               'column': {'state': 'provided', 'value': {'bed_volume': {'value': '1', 'unit': 'mL'}}}, 'facets': {}}
    aggregates = {'all_requested_units_accounted_for': True, 'all_supported_ready_units_covered': True,
                  'has_interpretation_issues': False, 'has_unserved_units': False}
    plan = {'units': [unit], 'context': {'source_passages': list(sources.values()), 'bindings': [binding]},
            'selected_root_ids': ['toy-support'], 'context_tokens': 10, **aggregates}
    ref = {'units': [{'task_id': 'A', 'item_id': 'A-item', 'information': 'flow_rate',
            'expected': {'state': 'supported', 'interpretation_state': 'ready', 'documentary_support_state': 'eligible'},
            'required_diagnostic_codes': [], 'direct_support_ids': ['toy-support'],
            'required_source_sets': [['toy-heading', 'toy-support']],
            'binding': {k: deepcopy(v) for k, v in binding.items() if k not in ('task_id', 'item_id', 'information', 'source_ids')}}],
           'acceptable_context_ids': list(sources), 'expected_aggregates': aggregates}
    return {'plan': plan}, ref, sources


class StructuredEvaluationSafetyTests(unittest.TestCase):
    def test_toy_complete_context_and_diagnostics_pass(self):
        result, reference, sources = toy()
        self.assertTrue(subject.score_case(result, reference, sources)['passed'])
        self.assertFalse(subject.score_case(result, reference, sources)['answer_quality_evaluated'])

    def test_scorer_rejects_partial_dependency_and_cross_task_binding(self):
        for change in ('dependency', 'task', 'column', 'duplicate_binding'):
            result, reference, sources = toy()
            binding = result['plan']['context']['bindings'][0]
            if change == 'dependency':
                binding['source_ids'].remove('toy-heading')
            elif change == 'task':
                binding['task_id'] = 'B'
            elif change == 'column':
                binding['column']['value']['bed_volume']['value'] = '5'
            else:
                result['plan']['context']['bindings'].append(deepcopy(binding))
            with self.subTest(change=change):
                self.assertFalse(subject.score_case(result, reference, sources)['passed'])

    def test_scorer_rejects_source_corruption_missing_fields_and_unknown_ids(self):
        for change in ('quote', 'field', 'unknown', 'duplicate'):
            result, reference, sources = toy()
            passage = result['plan']['context']['source_passages'][0]
            # Detach the toy output from its registry before corrupting it.
            result = deepcopy(result); passage = result['plan']['context']['source_passages'][0]
            if change == 'quote':
                passage['quote'] = 'Altered'
            elif change == 'field':
                del passage['scope']
            elif change == 'unknown':
                passage['id'] = 'excluded-source'
            else:
                result['plan']['context']['source_passages'].append(deepcopy(passage))
            with self.subTest(change=change):
                self.assertFalse(subject.score_case(result, reference, sources)['passed'])

    def test_scorer_recounts_context_including_bindings(self):
        result, reference, sources = toy()
        self.assertTrue(subject.score_case(result, reference, sources, lambda _: 10)['passed'])
        self.assertIn('token_accounting', subject.score_case(result, reference, sources, lambda _: 2049)['failures'])

    def test_scorer_checks_aggregates_and_no_always_clarify_shortcut(self):
        result, reference, sources = toy()
        result['plan']['all_supported_ready_units_covered'] = False
        self.assertFalse(subject.score_case(result, reference, sources)['passed'])
        result, reference, sources = toy()
        result['plan']['units'][0]['state'] = 'needs_clarification'
        result['plan']['context']['source_passages'] = []
        result['plan']['context']['bindings'] = []
        self.assertFalse(subject.score_case(result, reference, sources)['passed'])

    def test_blocked_unit_has_no_binding_even_when_source_shared_with_sibling(self):
        result, reference, sources = toy()
        ref = deepcopy(reference['units'][0]);ref['item_id'] = 'blocked';ref['expected']['state'] = 'needs_clarification'
        ref['binding'] = None;ref['required_source_sets'] = [];ref['required_diagnostic_codes'] = ['missing_context']
        reference['units'].append(ref)
        result['plan']['units'].append({**deepcopy(result['plan']['units'][0]), 'item_id': 'blocked',
            'state': 'needs_clarification', 'source_ids': [], 'diagnostics': [{'code': 'missing_context'}]})
        self.assertTrue(subject.score_case(result, reference, sources)['passed'])
        result['plan']['units'][-1]['source_ids'] = ['toy-support']
        self.assertFalse(subject.score_case(result, reference, sources)['passed'])

    def test_bilingual_comparison_ignores_message_wording_but_not_column(self):
        first, _, _ = toy();second = deepcopy(first)
        second['plan']['units'][0]['reason'] = 'Another display wording'
        self.assertEqual(subject.semantic_result(first), subject.semantic_result(second))
        second['plan']['context']['bindings'][0]['column']['value']['bed_volume']['value'] = '5'
        self.assertNotEqual(subject.semantic_result(first), subject.semantic_result(second))

    def review_fixture(self, folder):
        queries = {qid: {'id': qid, 'question': 'SYNTHETIC UNIT FIXTURE'} for qid in subject.IDS}
        forms = {qid: {'id': qid, 'input': 'SYNTHETIC, NEVER SENT TO CONTROL'} for qid in subject.IDS}
        refs = {qid: {'question_id': qid, 'reservations': ['Synthetic only']} for qid in subject.IDS}
        verified = {'manifest_sha256_lf': 'synthetic-manifest', 'method_lock_sha256_lf': 'synthetic-lock'}
        review = {**verified, 'decisions': [{
            'question_id': qid, 'decision': 'validated_with_reservation',
            'human_quote': 'SYNTHETIC TEST VALUE, NOT AN ACTUAL HUMAN APPROVAL',
            'question_sha256_canonical': subject.canonical(queries[qid]),
            'submission_sha256_canonical': subject.canonical(forms[qid]),
            'reference_sha256_canonical': subject.canonical(refs[qid]),
            'retained_reservations': refs[qid]['reservations'],
            'reviewed_at_utc': datetime.now(timezone.utc).isoformat()} for qid in subject.IDS]}
        path = folder / 'synthetic-review.json';subject.dump(path, review)
        return path, review, verified, queries, forms, refs

    def test_review_gate_binds_all_actual_decisions_and_all_three_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, review, verified, queries, forms, refs = self.review_fixture(Path(tmp))
            self.assertEqual(subject.review_gate(path, verified, queries, forms, refs), review)
            for field, value in [('decision', 'pending'), ('human_quote', ''),
                                 ('submission_sha256_canonical', 'changed'), ('reference_sha256_canonical', 'changed'),
                                 ('reviewed_at_utc', '2026-10-26T00:00:00'), ('retained_reservations', [])]:
                wrong = deepcopy(review);wrong['decisions'][0][field] = value;subject.dump(path, wrong)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    subject.review_gate(path, verified, queries, forms, refs)

    def test_incomplete_review_cannot_construct_runtime_or_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);folder = root / subject.PACKAGE;folder.mkdir(parents=True)
            path, review, verified, queries, forms, refs = self.review_fixture(root)
            review['decisions'] = [];subject.dump(path, review)
            subject.dump(folder / 'questions.json', {'questions': list(queries.values())})
            subject.dump(folder / 'submissions.json', {'submissions': list(forms.values())})
            subject.dump(folder / 'references.json', {'references': list(refs.values())})
            with patch.object(subject, 'verify', return_value=verified), patch.object(subject, 'make_runtime') as factory:
                with self.assertRaisesRegex(ValueError, 'twelve'):
                    subject.run(path, root)
                factory.assert_not_called()
            self.assertFalse((root / 'data').exists())

    def test_cli_needs_separate_review_before_any_run(self):
        with patch.object(subject, 'run') as run, patch('sys.stderr'), self.assertRaises(SystemExit):
            subject.main(['--run'])
        run.assert_not_called()

    def test_synthetic_runner_saves_full_grid_before_scoring_and_never_retries(self):
        # All inputs/approvals/runtime here are synthetic temporary fixtures.
        # No real S question or actual StructuredControl is evaluated.
        for fail_one in (False, True):
            with self.subTest(fail_one=fail_one), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp);folder = root / subject.PACKAGE;folder.mkdir(parents=True)
                path, review, verified, queries, forms, refs = self.review_fixture(root)
                forms = {qid: {'id': qid, 'input_en': {'marker': qid + '-en'},
                                   'input_fr': {'marker': qid + '-fr'}} for qid in subject.IDS}
                for row in review['decisions']:
                    row['submission_sha256_canonical'] = subject.canonical(forms[row['question_id']])
                subject.dump(path, review)
                subject.dump(folder / 'questions.json', {'questions': list(queries.values())})
                subject.dump(folder / 'submissions.json', {'submissions': list(forms.values())})
                subject.dump(folder / 'references.json', {'references': list(refs.values())})
                subject.dump(folder / 'manifest.json', {'file_sha256_lf': {}})
                (root / 'toy-tokenizer.bin').write_bytes(b'TOY TOKENIZER FIXTURE, NOT USED')
                subject.dump(folder / 'method-lock.json', {'python_version': platform.python_version(),
                    'dependency_versions': {}, 'tokenizer_asset_file': 'toy-tokenizer.bin',
                    'tokenizer': {'asset_sha256': hashlib.sha256((root / 'toy-tokenizer.bin').read_bytes()).hexdigest()},
                    'source_registry_file': 'toy-registry.json',
                    'run_directory': 'data/experiments/synthetic-fixture-only', 'excluded_source_ids': []})
                result, _, sources = toy();subject.dump(root / 'toy-registry.json', {'passages': list(sources.values())})
                output = root / 'data/experiments/synthetic-fixture-only'
                received = []
                class ToyRuntime:
                    def evaluate(self, form, request_id):
                        self_request = form['marker']
                        assert set(form) == {'marker'}  # No references, answers or source IDs.
                        received.append(self_request)
                        if fail_one and self_request == subject.IDS[0] + '-en':
                            raise ValueError('Synthetic runtime failure')
                        return deepcopy(result)
                def grade(*args):
                    self.assertEqual(len(received), 24)
                    self.assertEqual(len(subject.read(output / 'contexts-unscored.json')), 24)
                    return {'passed': True, 'failures': [], 'answer_quality_evaluated': False}
                with patch.dict(os.environ, {'PYTHONHASHSEED': '0'}), \
                     patch.object(subject, 'verify', return_value=verified), \
                     patch.object(subject, 'protected_files', return_value={}), \
                     patch.object(subject, 'make_runtime', return_value=ToyRuntime()) as factory, \
                     patch.object(subject, 'score_case', side_effect=grade), \
                     patch('ingestion.structured_sources.local_token_counter', return_value=lambda _: 10):
                    metrics = subject.run(path, root)
                    self.assertEqual(metrics['passed_submissions'], 23 if fail_one else 24)
                    self.assertEqual(metrics['saved_submissions'], 24)
                    self.assertEqual(metrics['bilingual_semantic_failures'], [subject.IDS[0]] if fail_one else [])
                    before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                    with self.assertRaisesRegex(ValueError, 'Existing output'):
                        subject.run(path, root)
                    self.assertEqual(factory.call_count, 1)
                    self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_network_guard_restores_sockets(self):
        original = socket.getaddrinfo
        with subject.offline() as attempts:
            with self.assertRaises(RuntimeError):
                socket.getaddrinfo('example.invalid', 443)
            self.assertEqual(attempts, ['network_call'])
        self.assertIs(socket.getaddrinfo, original)

    def test_real_preparation_verification_never_constructs_the_control(self):
        with patch.object(subject, 'make_runtime', side_effect=AssertionError('No runtime')), \
             patch('ingestion.structured_request.StructuredControl', side_effect=AssertionError('No constructor')):
            checked = subject.verify()
        self.assertEqual(checked['scenarios'], 12)
        self.assertEqual(checked['pending_human_reviews'], 12)
        self.assertFalse(checked['evaluation_executed_by_this_command'])

    def test_real_pending_template_cannot_plan_or_change_existing_output(self):
        folder = subject.ROOT / subject.PACKAGE
        lock = subject.read(folder / 'method-lock.json')
        output = subject.ROOT / lock['run_directory']
        def snapshot():
            return {p.relative_to(output): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in output.rglob('*') if p.is_file()} if output.exists() else None
        before = snapshot()
        with patch.object(subject, 'make_runtime') as factory, self.assertRaisesRegex(ValueError, 'another freeze'):
            subject.run(folder / 'review-template.json')
        factory.assert_not_called()
        self.assertEqual(snapshot(), before)

    def test_frozen_method_drift_is_rejected_without_executing_it(self):
        original = subject.digest
        changed = subject.ROOT / 'ingestion/structured_request.py'
        with patch.object(subject, 'digest', side_effect=lambda p: 'changed' if Path(p) == changed else original(p)), \
                patch.object(subject, 'make_runtime') as factory, self.assertRaisesRegex(ValueError, 'Frozen file'):
            subject.verify()
        factory.assert_not_called()

    def test_reference_bundles_preserve_role_guards_without_runtime_inference(self):
        folder = subject.ROOT / subject.PACKAGE
        packet = subject.read(folder / 'references.json')
        self.assertFalse({'E118-I', 'E121-EQ'} & {p['id'] for p in packet['source_passages']})
        for ref in packet['references']:
            for unit in ref['units']:
                for required in unit['required_source_sets']:
                    if unit['binding']['product_ref'] is not None:
                        self.assertIn('E120-W', required)
        lock = subject.read(folder / 'method-lock.json')
        self.assertFalse(any(p.startswith('tests/') for p in lock['file_sha256_lf']))


if __name__ == '__main__':
    unittest.main()
