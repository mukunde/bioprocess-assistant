"""Section overview selection, budget and source-only regressions."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import json
import shutil
from unittest.mock import patch
import experiments.cytiva.section_retrieval as runner

from ingestion.local_passage_retrieval import BM25, assemble, closure, serialize
from ingestion.section_context import section_plan, assemble_sections
from experiments.cytiva.cleaning_retrieval import build_corpus, read
from experiments.cytiva.section_retrieval import SPEC, summarize, run
from experiments.cytiva.verify_cleaning_retrieval_package import ROOT, PREPARATION


class SectionContextTests(unittest.TestCase):
    def setUp(self):
        self.spec = read(SPEC)
        self.policy = self.spec['section_context']
        self.corpus = build_corpus(read(ROOT / PREPARATION / 'evidence.json'), self.spec)
        self.index = BM25(self.corpus, index_context=True)
        self.hits = [{'passage_id': 'E166-E'}]

    def test_explicit_family_handles_punctuation(self):
        plan = section_plan('Protein G Sepharose, backpressure rises.', self.hits, self.policy)
        self.assertEqual(plan['families'], ['protein-ga'])
        self.assertEqual(plan['product_resolution'], 'explicit_family')

    def test_unspecified_product_gets_both_scopes_without_recipe_choice(self):
        plan = section_plan('La contre-pression de ma colonne augmente.', self.hits, self.policy)
        self.assertEqual(plan['product_resolution'], 'unresolved_product')
        self.assertEqual(plan['families'], ['protein-ga', 'mabselect'])
        self.assertTrue({'E166-H', 'E167-H', 'E167-SH'} <= set(plan['overview_ids']))
        self.assertNotIn('E167-S', plan['overview_ids'])

    def test_explicit_comparison_keeps_both_families(self):
        plan = section_plan('Protein A Sepharose and MabSelect pressure', self.hits, self.policy)
        self.assertEqual(len(plan['families']), 2)

    def test_no_positive_hit_does_not_invent_source_context(self):
        result = assemble_sections(self.index.passages, [], 'unknown pressure', len, self.policy, 100000)
        self.assertEqual(result['ids'], [])
        self.assertEqual(result['section_plan']['reason'], 'no_retrieval_evidence')

    def test_non_triggered_request_preserves_original_assembler(self):
        result = assemble_sections(self.index.passages, self.hits, 'ethanol wash', len, self.policy, 100000)
        baseline = assemble(self.index.passages, self.hits, len, 100000)
        self.assertEqual(result['context'], baseline['context'])
        self.assertEqual(result['section_status'], 'not_requested')

    def test_overview_reserved_before_procedure(self):
        result = assemble_sections(self.index.passages, self.hits, 'Protein A Sepharose pressure', len,
                                   self.policy, 100000)
        self.assertTrue(set(self.policy['families'][0]['overview_ids']) <= set(result['ids']))
        self.assertIn('E166-W', result['ids'])
        self.assertEqual(result['section_status'], 'included')
        self.assertEqual(len(result['ids']), len(set(result['ids'])))

    def test_budget_rejects_complete_overview_instead_of_truncating(self):
        plan = section_plan('column pressure', self.hits, self.policy)
        ids = list(dict.fromkeys(p for anchor in plan['overview_ids'] for p in closure(self.index.passages, anchor)))
        limit = len(serialize(self.index.passages, ids)) - 1
        result = assemble_sections(self.index.passages, self.hits, 'column pressure', len, self.policy, limit)
        self.assertEqual(result['section_status'], 'unavailable')
        self.assertFalse(result['budget_complete'])
        self.assertEqual(result['excluded'][0]['reason'], 'whole_section_overview_over_budget')
        self.assertLessEqual(result['tokens'], limit)

    def test_quarantined_overview_cannot_be_forced(self):
        passages = deepcopy(self.index.passages)
        passages['E166-T']['quarantined'] = True
        result = assemble_sections(passages, self.hits, 'Protein A Sepharose pressure', len, self.policy, 100000)
        self.assertEqual(result['section_status'], 'unavailable')
        self.assertNotIn('E166-T', result['ids'])
        self.assertEqual(result['excluded'][0]['reason'], 'section_quarantine')

    def test_all_accepted_recipe_dependencies_are_kept(self):
        question = 'MabSelect pressure ethanol'
        result = assemble_sections(self.index.passages, self.index.search(question), question, len, self.policy, 100000)
        for seed in result['accepted_seeds']:
            self.assertTrue(set(closure(self.index.passages, seed)) <= set(result['ids']))

    def test_source_scope_confusion_never_merges_quotes(self):
        result = assemble_sections(self.index.passages, self.hits, 'column pressure', len, self.policy, 100000)
        import json
        for record in json.loads(result['context'])['source_passages']:
            self.assertEqual(record['quote'], self.index.passages[record['id']]['quote'])
            self.assertEqual(record['scope'], self.index.passages[record['id']]['scope'])

    def test_question_ids_do_not_influence_policy(self):
        # Caller supplies only query text/hits/source policy; reference labels have no entry point.
        a = section_plan('Protein A Sepharose pressure', self.hits, self.policy)
        b = section_plan('Protein A Sepharose pressure', self.hits, self.policy)
        self.assertEqual(a, b)
        self.assertNotIn('question_id', a)

    def test_unknown_alias_is_not_a_prefix_match(self):
        plan = section_plan('MabSelectivity pressure', self.hits, self.policy)
        self.assertEqual(plan['product_resolution'], 'unresolved_product')

    def test_existing_run_directory_refused_before_loading_models(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as directory:
            with self.assertRaisesRegex(ValueError, 'already exists'): run(Path(directory))


class SectionSummaryRegressionTests(unittest.TestCase):
    EXPECTED = {'reviewed': ['first', 'second'], 'new_candidate': ['additional']}

    @classmethod
    def rows(cls):
        return [{'dataset': dataset, 'variant': variant, 'question_id': qid, 'language': lang,
                 'complete_evidence': True, 'reference_coverage': 1.0,
                 'assembled': {'tokens': 100, 'excluded': []},
                 'timings': [{'retrieval_ms': 1.0, 'assembly_ms': 2.0}]}
                for dataset, ids in cls.EXPECTED.items() for variant in ('v02', 'v03')
                for qid in ids for lang in ('en', 'fr')]

    def test_complete_grid_uses_expected_inventory(self):
        result = summarize(self.rows(), expected_datasets=self.EXPECTED)
        self.assertEqual(result['reviewed']['v03']['complete_both_languages'], 2)
        self.assertEqual(result['new_candidate']['v03']['complete_both_languages'], 1)

    def test_missing_failed_intent_or_language_rejected(self):
        rows = self.rows()
        for filtered in ([r for r in rows if r['question_id'] != 'second'],
                         [r for r in rows if not (r['dataset'] == 'new_candidate' and
                          r['variant'] == 'v03' and r['language'] == 'fr')]):
            with self.assertRaisesRegex(ValueError, 'Missing intent/language'):
                summarize(filtered, expected_datasets=self.EXPECTED)

    def test_duplicate_variant_language_rejected(self):
        rows = self.rows()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            summarize(rows + [rows[0]], expected_datasets=self.EXPECTED)

    def test_unexpected_dataset_variant_and_language_rejected(self):
        for field, value in [('dataset', 'unknown'), ('variant', 'v04'), ('language', 'de')]:
            rows = self.rows(); rows[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Unexpected'):
                summarize(rows, expected_datasets=self.EXPECTED)

    def test_missing_entire_variant_rejected(self):
        rows = [r for r in self.rows() if r['variant'] != 'v03']
        with self.assertRaisesRegex(ValueError, 'Missing intent/language'):
            summarize(rows, expected_datasets=self.EXPECTED)

    def test_non_boolean_complete_flag_rejected(self):
        rows = self.rows(); rows[0]['complete_evidence'] = 'true'
        with self.assertRaisesRegex(ValueError, 'boolean'):
            summarize(rows, expected_datasets=self.EXPECTED)


class ReviewedReferenceBindingTests(unittest.TestCase):
    def test_current_review_status_and_hashes_are_derived(self):
        reviews, decisions = runner.verified_reference_reviews()
        self.assertTrue(reviews['new_candidate']['human_reference_reviewed'])
        self.assertEqual(reviews['new_candidate']['validated_intents'], 8)
        self.assertEqual(reviews['reviewed']['validated_intents'], 10)
        self.assertEqual(reviews['new_candidate']['review_sha256_lf'],
                         runner.digest(runner.SECTION_REFERENCE_PACKAGE / 'review.json'))
        self.assertEqual(decisions['new_candidate']['N05'], 'validated_with_reservation')
        self.assertFalse(reviews['new_candidate']['publication_allowed'])
        self.assertFalse(reviews['new_candidate']['benchmark_results_human_validated'])

    def test_tampered_section_review_blocks_run_before_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as directory:
            package = Path(directory) / 'review'; shutil.copytree(runner.SECTION_REFERENCE_PACKAGE, package)
            review = json.loads((package / 'review.json').read_text(encoding='utf-8'))
            review['decisions'][0]['reservations'] = []
            (package / 'review.json').write_text(json.dumps(review), encoding='utf-8')
            output = Path(directory) / 'run'
            with patch.object(runner, 'SECTION_REFERENCE_PACKAGE', package), \
                 patch.object(runner, 'network_guard', return_value=[]), \
                 patch.object(runner, 'token_counter') as tokenizer:
                with self.assertRaisesRegex(ValueError, 'File digest'): runner.run(output)
                tokenizer.assert_not_called()
            self.assertFalse(output.exists())

    def test_new_manifest_binds_both_reviews_without_model_or_download(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as directory:
            output = Path(directory) / 'run'
            # Character count is a test-only stand-in; no measured retrieval score is asserted.
            with patch.object(runner, 'network_guard', return_value=[]), \
                 patch.object(runner, 'token_counter', return_value=(len, {'name': 'test_character_count'})):
                runner.run(output)
            manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
            self.assertTrue(manifest['new_references_human_reviewed'])
            for metadata in manifest['reference_reviews'].values():
                self.assertTrue(metadata['human_reference_reviewed'])
                self.assertEqual(metadata['review_sha256_lf'], runner.digest(ROOT / metadata['review_path']))
                self.assertIn(metadata['review_path'], manifest['code_and_input_sha256_lf'])
                self.assertEqual((output / 'input-snapshot' / metadata['review_path']).read_bytes(),
                                 (ROOT / metadata['review_path']).read_bytes())
            rows = json.loads((output / 'results.json').read_text(encoding='utf-8'))
            self.assertEqual(len(rows), 72)
            self.assertTrue(all(r['reference_review_decision'] == 'validated_with_reservation' for r in rows))
            self.assertTrue(all('reference_status_at_preparation' in r for r in rows))


if __name__ == '__main__':
    unittest.main()
