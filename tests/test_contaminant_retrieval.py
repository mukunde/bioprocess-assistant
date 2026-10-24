"""Reviewed-input binding, pending-source exclusion and paired adapter regressions."""
from copy import deepcopy
import inspect
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva import contaminant_retrieval as runner
from experiments.cytiva.cleaning_retrieval import build_corpus, read
from ingestion.local_passage_retrieval import BM25, assemble


class ContaminantRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.spec = read(runner.ROOT / runner.PREPARATION / 'source_context.json')
        self.evidence = read(runner.ROOT / runner.PREPARATION / 'evidence.json')
        self.pending = read(runner.PACKAGE / 'manifest.json')['not_individually_reviewed_source_ids']
        self.policy = runner.runtime_policy(self.spec, self.pending)
        self.corpus = build_corpus(self.evidence, self.policy)
        self.index = BM25(self.corpus, index_context=True)

    def test_pending_overlay_does_not_modify_frozen_spec_or_source(self):
        self.assertEqual(self.spec['quarantined_ids'], [])
        self.assertEqual(self.policy['quarantined_ids'], ['E118-I', 'E121-EQ'])
        self.assertFalse(set(self.pending) & set(self.index.docs))
        self.assertEqual(len(self.corpus), 27)
        self.assertEqual(len(self.index.docs), 18)
        self.assertTrue(all(p['human_review_status'] == 'pending' for p in self.evidence['passages']))

    def test_unknown_or_duplicate_pending_ids_rejected(self):
        for ids in (['unknown'], ['E118-I', 'E118-I']):
            with self.assertRaisesRegex(ValueError, 'Invalid pending'):
                runner.runtime_policy(self.spec, ids)

    def test_pending_source_cannot_be_searched_or_forced_into_context(self):
        for pid in self.pending:
            quote = next(p['quote'] for p in self.evidence['passages'] if p['id'] == pid)
            self.assertNotIn(pid, [h['passage_id'] for h in self.index.search(quote, 100)])
            result = assemble(self.index.passages, [{'passage_id': pid}], len, 100000)
            self.assertEqual(result['ids'], [])
            self.assertEqual(result['excluded'][0]['reason'], 'quarantine_in_bundle')

    def test_indirect_pending_dependency_blocks_child(self):
        corpus = deepcopy(self.corpus)
        next(p for p in corpus if p['id'] == 'E119-B')['requires'].append('E118-I')
        index = BM25(corpus, index_context=True)
        self.assertNotIn('E119-B', index.docs)
        result = assemble(index.passages, [{'passage_id': 'E119-B'}], len, 100000)
        self.assertEqual(result['ids'], [])

    def test_runtime_accepts_only_query_text_and_source_index(self):
        self.assertEqual(list(inspect.signature(runner.retrieve).parameters),
                         ['index', 'text', 'count_tokens', 'top_k', 'max_tokens'])
        for p in self.corpus:
            self.assertFalse({'question_en', 'expected_answer_en', 'required_evidence_sets', 'decisions'} & p.keys())
        text = 'HiTrap Blue HP albumin elution'
        a = runner.retrieve(self.index, text, len, 5, 100000)
        b = runner.retrieve(self.index, text, len, 6, 100000)
        self.assertEqual(a['hits'], b['hits'][:len(a['hits'])])
        self.assertTrue(set(a['assembled']['ids']) <= set(b['assembled']['ids']))
        runner.check_context(self.index.passages, b['assembled'], len, 100000, self.pending)

    def test_context_checks_budget_quotes_and_pending_leak(self):
        good = runner.retrieve(self.index, 'HiTrap Blue HP albumin', len, 6, 100000)['assembled']
        for change in ({'tokens': 100001}, {'context': 'changed'}, {'ids': good['ids'] + ['E118-I']}):
            bad = {**good, **change}
            with self.assertRaises(ValueError):
                runner.check_context(self.index.passages, bad, len, 100000, self.pending)


class ContaminantAdapterRunnerTests(unittest.TestCase):
    @staticmethod
    def rows():
        return [{'question_id': 'example', 'language': lang, 'variant': variant,
                 'complete_evidence': True, 'reference_coverage': 1.0, 'hits': [],
                 'assembled': {'ids': [], 'tokens': 10, 'excluded': [], 'context': '{}'},
                 'timings': [{'retrieval_ms': 1, 'assembly_ms': 1}]}
                for variant in ('top5', 'top6') for lang in ('en', 'fr')]

    def test_summary_rejects_incomplete_duplicate_unknown_grids(self):
        rows = self.rows()
        self.assertEqual(runner.summarize(rows, ['example'])['top6']['complete_both_languages'], 1)
        for broken in (rows[:-1], rows + [rows[0]], rows + [{**rows[0], 'variant': 'unknown'}]):
            with self.assertRaises(ValueError): runner.summarize(broken, ['example'])

    def test_summary_rejects_ranking_or_context_loss(self):
        for field, value in [('hits', [{'passage_id': 'x', 'score': 1}]),
                             ('assembled', {'ids': ['x'], 'tokens': 10, 'excluded': [], 'context': '{}'})]:
            rows = self.rows(); rows[0][field] = value
            with self.assertRaises(ValueError): runner.summarize(rows, ['example'])

    def test_existing_output_refused_before_guard_or_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT / 'tmp') as temp, \
             patch.object(runner, 'network_guard') as guard, patch.object(runner, 'token_counter') as counter:
            with self.assertRaisesRegex(ValueError, 'already exists'): runner.run(Path(temp))
            guard.assert_not_called(); counter.assert_not_called()

    def test_tampered_reference_blocks_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT / 'tmp') as temp:
            package = Path(temp) / 'review'; shutil.copytree(runner.PACKAGE, package)
            (package / 'review.json').write_text('{}', encoding='utf-8')
            with patch.object(runner, 'PACKAGE', package), patch.object(runner, 'network_guard', return_value=[]), \
                 patch.object(runner, 'protected_files', return_value={}), patch.object(runner, 'token_counter') as counter:
                with self.assertRaisesRegex(ValueError, 'File digest'): runner.run(Path(temp) / 'run')
                counter.assert_not_called()

    def test_manifest_snapshot_and_review_status_are_bound(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT / 'tmp') as temp, \
             patch.object(runner, 'network_guard', return_value=[]), \
             patch.object(runner, 'token_counter', return_value=(len, {'name': 'test_character_count'})):
            output = Path(temp) / 'run'
            runner.run(output)
            manifest = read(output / 'manifest.json'); rows = read(output / 'results.json')
            self.assertEqual(len(rows), 40)
            self.assertEqual(manifest['pending_source_ids'], ['E118-I', 'E121-EQ'])
            self.assertEqual(manifest['pending_source_leakage'], 0)
            self.assertFalse(manifest['benchmark_results_human_validated'])
            self.assertTrue(manifest['protected_files_unchanged'])
            for f, value in manifest['code_and_input_sha256_lf'].items():
                self.assertEqual(runner.digest(output / 'input-snapshot' / f), value)
            for row in rows:
                self.assertEqual(row['reference_review_decision'], 'validated_with_reservation')
                self.assertEqual(row['reference_status_at_preparation'], 'pending_human_review')
                self.assertFalse(row['response_status_evaluated'])
                self.assertFalse(set(row['assembled']['ids']) & set(manifest['pending_source_ids']))


if __name__ == '__main__':
    unittest.main()
