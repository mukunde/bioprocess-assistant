"""Portable reviewed v03b export; no original private run is needed."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from experiments.cytiva import verify_v03b_reviewed_package as selected


class V03bReviewedPackageTests(unittest.TestCase):
    def test_selected_package_verifies_without_retrieval(self):
        with patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('No retrieval')):
            self.assertEqual(selected.verify()['contexts'],24)

    def test_changed_source_serialization_is_rejected(self):
        results=deepcopy(selected.frozen.read(selected.ROOT/selected.PACKAGE/'results.json'))
        results['contexts'][0]['assembled']['context']='changed'
        refs=selected.frozen.read(selected.ROOT/selected.frozen.PACKAGE/'references.json')['references']
        with self.assertRaisesRegex(ValueError,'quote/provenance'):
            selected.check_results(results,selected.corpus(selected.ROOT),refs)

    def test_changed_recorded_score_is_rejected(self):
        results=deepcopy(selected.frozen.read(selected.ROOT/selected.PACKAGE/'results.json'))
        results['metrics']['complete_both_languages']=12
        refs=selected.frozen.read(selected.ROOT/selected.frozen.PACKAGE/'references.json')['references']
        with self.assertRaisesRegex(ValueError,'metric changed'):
            selected.check_results(results,selected.corpus(selected.ROOT),refs)
