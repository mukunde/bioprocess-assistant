"""Source-only lexical retrieval, dependency safety and evaluator regressions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from ingestion.local_passage_retrieval import BM25, assemble, closure, serialize, terms
from experiments.cytiva.cleaning_retrieval import build_corpus, coverage, ranking_metrics, read, SPEC, summarize
from experiments.cytiva.verify_cleaning_retrieval_package import ROOT, PREPARATION


def passage(pid, quote, requires=(), quarantined=False):
    return {'id': pid, 'quote': quote, 'quote_sha256': hashlib.sha256(quote.encode()).hexdigest(),
            'pdf_page_1based': 166, 'pdf_page_index_0based': 165, 'scope': 'test',
            'page_text_start': 0, 'page_text_end': len(quote),
            'requires': list(requires), 'quarantined': quarantined}


class LocalPassageRetrievalTests(unittest.TestCase):
    def test_bm25_ranks_source_overlap(self):
        index = BM25([passage('a', 'ethanol cleaning'), passage('b', 'guanidine washing')])
        self.assertEqual(index.search('ethanol')[0]['passage_id'], 'a')
        self.assertEqual(index.search('unseenword'), [])

    def test_french_bridge_and_accent_handling(self):
        self.assertIn('backpressure', terms('contre-pression'))
        self.assertEqual(terms('dénaturées'), terms('denatured'))
        index = BM25([passage('a', 'ethanol increases backpressure')])
        self.assertTrue(index.search('contre-pression augmente'))

    def test_stable_ties_and_zero_top_k(self):
        index = BM25([passage('b', 'buffer'), passage('a', 'buffer')])
        self.assertEqual([h['passage_id'] for h in index.search('buffer')], ['a', 'b'])
        self.assertEqual(index.search('buffer', 0), [])

    def test_invalid_parameters(self):
        for k1, b in [(0, .75), (float('nan'), .75), (1.2, float('inf')), (1.2, -1)]:
            with self.assertRaises(ValueError): BM25([], k1=k1, b=b)
        with self.assertRaises(ValueError): BM25([]).search('buffer', -1)

    def test_duplicate_ids_and_broken_topology_rejected(self):
        with self.assertRaises(ValueError): BM25([passage('a', 'x'), passage('a', 'y')])
        with self.assertRaisesRegex(ValueError, 'Missing'): BM25([passage('a', 'x', ['missing'])])
        with self.assertRaisesRegex(ValueError, 'Cyclic'):
            BM25([passage('a', 'x', ['b']), passage('b', 'y', ['a'])])

    def test_atomic_warning_and_heading_expansion(self):
        docs = [passage('h', 'product'), passage('w', 'warning', ['h']), passage('r', 'recipe', ['h', 'w'])]
        index = BM25(docs)
        result = assemble(index.passages, [{'passage_id': 'r'}], len, 10000)
        self.assertEqual(result['ids'], ['h', 'w', 'r'])
        self.assertEqual(len(result['ids']), len(set(result['ids'])))
        self.assertEqual(json.loads(result['context'])['source_passages'][2]['quote'], 'recipe')

    def test_over_budget_never_keeps_partial_recipe_bundle(self):
        docs = [passage('h', 'product'), passage('w', 'warning'), passage('r', 'recipe', ['h', 'w'])]
        lookup = {p['id']: p for p in docs}
        limit = len(serialize(lookup, ['h', 'w', 'r'])) - 1
        result = assemble(lookup, [{'passage_id': 'r'}], len, limit)
        self.assertEqual(result['ids'], [])
        self.assertFalse(result['budget_complete'])
        self.assertEqual(result['excluded'][0]['reason'], 'whole_bundle_over_budget')
        self.assertLessEqual(result['tokens'], limit)

    def test_budget_includes_metadata_and_wrappers(self):
        doc = passage('x', 'x')
        result = assemble({'x': doc}, [{'passage_id': 'x'}], len, 100)
        self.assertEqual(result['ids'], [])
        self.assertEqual(result['tokens'], len(result['context']))
        with self.assertRaises(ValueError): assemble({'x': doc}, [], len, 0)
        tiny = assemble({'x': doc}, [], len, 1)
        self.assertEqual(tiny['context'], '')
        self.assertFalse(tiny['budget_complete'])

    def test_deduplication_and_no_hits(self):
        docs = [passage('h', 'header'), passage('r', 'recipe', ['h'])]
        lookup = {p['id']: p for p in docs}
        result = assemble(lookup, [{'passage_id': 'h'}, {'passage_id': 'r'}, {'passage_id': 'r'}], len, 10000)
        self.assertEqual(result['ids'], ['h', 'r'])
        self.assertEqual(assemble(lookup, [], len)['ids'], [])

    def test_quarantine_propagates_to_child_and_assembler(self):
        docs = [passage('h', 'warning', quarantined=True), passage('r', 'ethanol', ['h'])]
        index = BM25(docs)
        self.assertEqual(index.search('ethanol'), [])
        result = assemble(index.passages, [{'passage_id': 'r'}], len, 10000)
        self.assertEqual(result['ids'], [])
        self.assertEqual(result['excluded'][0]['reason'], 'quarantine_in_bundle')

    def test_source_builder_excludes_labels_and_answers(self):
        spec = read(SPEC)
        evidence = read(ROOT / PREPARATION / 'evidence.json')
        baseline = build_corpus(evidence, spec)
        altered = deepcopy(evidence)
        altered['questions'] = [{'answer': 'LEAKED'}]
        altered['expected_answer_points'] = ['LEAKED']
        for p in altered['passages']:
            p['expected_answer'] = 'LEAKED'
            p['reviewer_decision'] = 'LEAKED'
        self.assertEqual(build_corpus(altered, spec), baseline)
        self.assertNotIn('LEAKED', json.dumps(baseline))

    def test_source_quote_and_inventory_checked(self):
        spec = read(SPEC); evidence = read(ROOT / PREPARATION / 'evidence.json')
        evidence['passages'][0]['quote'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'quote'): build_corpus(evidence, spec)
        evidence = read(ROOT / PREPARATION / 'evidence.json'); evidence['passages'].pop()
        with self.assertRaisesRegex(ValueError, 'inventory'): build_corpus(evidence, spec)

    def test_real_topology_keeps_restrictions_and_solvent_warnings(self):
        corpus = build_corpus(read(ROOT / PREPARATION / 'evidence.json'), read(SPEC))
        lookup = {p['id']: p for p in corpus}
        self.assertTrue({'E167-H', 'E167-PH', 'E167-SH', 'E167-S'} <= set(closure(lookup, 'E167-S')))
        self.assertTrue({'E166-H', 'E166-LH', 'E166-W'} <= set(closure(lookup, 'E166-E')))
        self.assertNotIn('E166-E', closure(lookup, 'E167-E'))

    def test_context_index_uses_source_parents_without_searching_heading_alone(self):
        docs = [passage('h', 'MabSelect alkali tolerance'), passage('r', 'wash 3 volumes', ['h'])]
        docs[0]['searchable'] = False
        index = BM25(docs, index_context=True)
        self.assertEqual([h['passage_id'] for h in index.search('MabSelect')], ['r'])
        self.assertEqual(BM25(docs).search('MabSelect'), [])
        self.assertEqual(assemble(index.passages, index.search('MabSelect'), len, 10000)['ids'], ['h', 'r'])

    def test_same_query_has_no_reference_dependent_expansion(self):
        corpus = build_corpus(read(ROOT / PREPARATION / 'evidence.json'), read(SPEC))
        index = BM25(corpus)
        a = assemble(index.passages, index.search('70% ethanol'), len, 100000)
        b = assemble(index.passages, index.search('70% ethanol'), len, 100000)
        self.assertEqual(a, b)

    def test_recall_alternatives_and_missing_positions(self):
        q = {'required_evidence_sets': [['a', 'b'], ['c']]}
        self.assertEqual(coverage(['a'], q), (.5, False))
        self.assertEqual(coverage(['c'], q), (1, True))
        self.assertEqual(ranking_metrics([{'passage_id': 'a'}], q, 5)['precision_at_5'], .2)
        self.assertEqual(ranking_metrics([], q, 5)['mrr'], 0)


class RetrievalSummaryRegressionTests(unittest.TestCase):
    @staticmethod
    def rows(ids=None):
        if ids is None:
            ids = [q['id'] for q in read(ROOT / PREPARATION / 'questions.json')['questions']]
        return [{'question_id': qid, 'language': lang, 'raw_complete_evidence': True,
            'assembled_complete_evidence': True, 'raw_reference_recall': 1.0,
            'assembled_reference_recall': 1.0,
            'ranking': {'precision_at_5': 1.0, 'mrr': 1.0, 'ndcg_at_5': 1.0},
            'timings_ms': [{'retrieval_ms': 1.0, 'expanded_assembly_ms': 2.0}],
            'assembled': {'tokens': 100, 'excluded': []}, 'quarantine_leakage_count': 0}
            for qid in ids for lang in ('en', 'fr')]

    def test_missing_entire_failed_intents_cannot_become_successes(self):
        rows = [r for r in self.rows() if r['question_id'] not in ('Q08', 'Q09')]
        with self.assertRaisesRegex(ValueError, 'Missing intent/language'): summarize(rows)

    def test_missing_one_language_is_rejected(self):
        rows = self.rows()[1:]
        with self.assertRaisesRegex(ValueError, 'Missing intent/language'): summarize(rows)

    def test_duplicate_language_is_rejected(self):
        rows = self.rows()
        with self.assertRaisesRegex(ValueError, 'Duplicate'): summarize(rows + [rows[0]])

    def test_unexpected_intent_or_language_is_rejected(self):
        for field, value in [('question_id', 'unexpected'), ('language', 'de')]:
            rows = self.rows(); rows[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Unexpected'):
                summarize(rows)

    def test_non_boolean_complete_flag_is_rejected(self):
        for value in (None, 1, 'true'):
            rows = self.rows(); rows[0]['assembled_complete_evidence'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'boolean'):
                summarize(rows)

    def test_empty_results_and_invalid_expected_inventory_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing'): summarize([])
        for ids in ([], ['one', 'one']):
            with self.subTest(ids=ids), self.assertRaisesRegex(ValueError, 'inventory'):
                summarize(self.rows(['one']), expected_ids=ids)

    def test_explicit_non_q_inventory_is_counted_without_hardcoding(self):
        rows = self.rows(['first', 'second'])
        rows[-1]['assembled_complete_evidence'] = False
        self.assertEqual(summarize(rows, expected_ids=['first', 'second'])['intents_complete_both_languages'], 1)
        self.assertEqual(summarize(self.rows())['intents_complete_both_languages'], 10)


if __name__ == '__main__':
    unittest.main()
