"""Top-six candidate regressions; source retrieval never receives answer references."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva import retrieval_depth as runner
from experiments.cytiva.cleaning_retrieval import build_corpus, read
from experiments.cytiva.verify_cleaning_retrieval_package import ROOT, PREPARATION
from ingestion.local_passage_retrieval import BM25, closure
from ingestion.section_context import assemble_sections


class RetrievalDepthTests(unittest.TestCase):
    def setUp(self):
        self.baseline = read(runner.BASELINE)
        self.candidate = read(runner.SPEC)
        self.corpus = build_corpus(read(ROOT / PREPARATION / 'evidence.json'), self.candidate)
        self.index = BM25(self.corpus, index_context=True)
        self.question = next(q for q in read(runner.NEW)['questions'] if q['id'] == 'N05')

    def test_only_top_k_changes_and_frozen_corpus_is_identical(self):
        runner.validate_specs(self.baseline, self.candidate)
        self.assertEqual(self.corpus, build_corpus(read(ROOT / PREPARATION / 'evidence.json'), self.baseline))
        self.assertEqual(self.baseline['retrieval']['top_k'], 5)
        self.assertEqual(self.candidate['retrieval']['top_k'], 6)

    def test_other_policy_or_budget_changes_rejected(self):
        for field, value in [('max_tokens', 4096), ('selection', 'truncate')]:
            changed = deepcopy(self.candidate)
            changed['context'][field] = value
            with self.assertRaisesRegex(ValueError, 'Only retrieval depth'):
                runner.validate_specs(self.baseline, changed)

    def test_n05_missing_pair_is_rank_cutoff_not_budget_or_quarantine(self):
        for language in ('en', 'fr'):
            with self.subTest(language=language):
                text = self.question['question_' + language]
                hits = self.index.search(text, 6)
                self.assertEqual(hits[5]['passage_id'], 'E166-P')
                self.assertEqual(self.index.search(text, 5), hits[:5])
                self.assertIn('E166-PH', closure(self.index.passages, hits[5]['passage_id']))
                old = assemble_sections(self.index.passages, hits[:5], text, len,
                                        self.baseline['section_context'], 100000)
                self.assertEqual(old['excluded'], [])
                self.assertNotIn('E166-P', old['ids'])
                self.assertNotIn('E166-PH', old['ids'])
                new = assemble_sections(self.index.passages, hits, text, len,
                                        self.candidate['section_context'], 100000)
                self.assertTrue(set(self.question['required_evidence_sets'][0]) <= set(new['ids']))

    def test_sixth_bundle_does_not_bypass_quarantine(self):
        for pid in ('E166-PH', 'E166-P'):
            corpus = deepcopy(self.corpus)
            next(p for p in corpus if p['id'] == pid)['quarantined'] = True
            index = BM25(corpus, index_context=True)
            text = self.question['question_en']
            result = assemble_sections(index.passages, index.search(text, 6), text, len,
                                       self.candidate['section_context'], 100000)
            self.assertNotIn('E166-P', result['ids'])
            self.assertNotIn(pid, result['ids'])

    def test_sixth_bundle_still_obeys_atomic_budget_and_exact_provenance(self):
        text = self.question['question_en']
        hits = self.index.search(text, 6)
        old = assemble_sections(self.index.passages, hits[:5], text, len,
                                self.baseline['section_context'], 100000)
        limited = assemble_sections(self.index.passages, hits, text, len,
                                    self.candidate['section_context'], old['tokens'])
        self.assertLessEqual(limited['tokens'], old['tokens'])
        self.assertNotIn('E166-P', limited['ids'])
        self.assertNotIn('E166-PH', limited['ids'])
        self.assertFalse(limited['budget_complete'])
        self.assertEqual(limited['excluded'][-1]['reason'], 'whole_bundle_over_budget')
        result = assemble_sections(self.index.passages, hits, text, len,
                                   self.candidate['section_context'], 100000)
        self.assertEqual(len(result['ids']), len(set(result['ids'])))
        for seed in result['accepted_seeds']:
            self.assertTrue(set(closure(self.index.passages, seed)) <= set(result['ids']))
        for record in json.loads(result['context'])['source_passages']:
            for key, value in record.items():
                self.assertEqual(value, self.index.passages[record['id']][key])

    def test_no_positive_match_stays_empty(self):
        self.assertEqual(self.index.search('zxqvunknown', 6), [])


class RetrievalDepthRunnerTests(unittest.TestCase):
    @staticmethod
    def rows():
        return [{'dataset': 'test', 'variant': variant, 'question_id': 'x', 'language': lang,
                 'complete_evidence': True, 'reference_coverage': 1.0, 'hits': [],
                 'assembled': {'tokens': 10, 'excluded': [], 'context': '{}'},
                 'timings': [{'retrieval_ms': 1, 'assembly_ms': 1}]}
                for variant in ('v03', 'v05') for lang in ('en', 'fr')]

    def test_summary_rejects_missing_duplicate_unknown_and_changed_ranking(self):
        rows = self.rows()
        self.assertEqual(runner.summarize(rows, {'test': ['x']})['test']['v05']['complete_both_languages'], 1)
        invalid_rank = deepcopy(rows)
        invalid_rank[0]['hits'] = [{'passage_id': 'first', 'score': 1}]
        invalid_rank[2]['hits'] = [{'passage_id': 'other', 'score': 1}]
        for broken in (rows[:-1], rows + [rows[0]], rows + [{**rows[0], 'variant': 'bad'}], invalid_rank):
            with self.assertRaises(ValueError):
                runner.summarize(broken, {'test': ['x']})

    def test_existing_output_refused_before_network_or_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as temp, \
             patch.object(runner, 'token_counter') as counter, patch.object(runner, 'network_guard') as guard:
            with self.assertRaisesRegex(ValueError, 'already exists'):
                runner.run(Path(temp))
            counter.assert_not_called()
            guard.assert_not_called()

    def test_invalid_reference_blocks_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as temp, \
             patch.object(runner, 'network_guard', return_value=[]), \
             patch.object(runner, 'verified_reference_reviews', side_effect=ValueError('Invalid review')), \
             patch.object(runner, 'token_counter') as counter:
            with self.assertRaisesRegex(ValueError, 'Invalid review'):
                runner.run(Path(temp) / 'new')
            counter.assert_not_called()

    def test_new_run_binds_snapshots_and_keeps_original_runs(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as temp, \
             patch.object(runner, 'network_guard', return_value=[]), \
             patch.object(runner, 'token_counter', return_value=(len, {'name': 'test_character_count'})):
            output = Path(temp) / 'new'
            runner.run(output)
            manifest = read(output / 'manifest.json')
            self.assertTrue(manifest['previous_runs_unchanged'])
            self.assertEqual(manifest['network_attempts'], [])
            self.assertEqual((manifest['llm_calls'], manifest['api_calls']), (0, 0))
            self.assertEqual(len(read(output / 'results.json')), 72)
            for f, value in manifest['code_and_input_sha256_lf'].items():
                self.assertEqual(runner.digest(output / 'input-snapshot' / f), value)


if __name__ == '__main__':
    unittest.main()
