"""Portable reviewed v05 export; no original private run is needed."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from experiments.cytiva import verify_v05_reviewed_package as selected


class V05ReviewedPackageTests(unittest.TestCase):
    def test_selected_package_verifies_without_retrieval(self):
        with patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('No retrieval')), \
             patch('ingestion.polarity_passage_context.navigation_plan',side_effect=AssertionError('No planning')):
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

    def test_changed_collective_approval_scope_is_rejected(self):
        p=deepcopy(selected.frozen.read(selected.ROOT/selected.PACKAGE/'provenance.json'))
        p['collective_approval']['question_ids']=p['collective_approval']['question_ids'][:-1]
        original=selected.frozen.read
        def changed(path):
            if path==selected.ROOT/selected.PACKAGE/'provenance.json':return p
            return original(path)
        with patch.object(selected.frozen,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Collective approval scope'):selected.verify()

    def test_diagnostic_metadata_cannot_change_without_changing_scores(self):
        result=deepcopy(selected.frozen.read(selected.ROOT/selected.PACKAGE/'results.json'))
        row=next(r for r in result['contexts'] if r['question_id']=='X07' and r['language']=='en')
        row['navigation_plan']['clarification_required']=False
        refs=selected.frozen.read(selected.ROOT/selected.frozen.PACKAGE/'references.json')['references']
        with self.assertRaisesRegex(ValueError,'metric changed'):
            selected.check_results(result,selected.corpus(selected.ROOT),refs)


if __name__=='__main__':unittest.main()
