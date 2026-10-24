"""Selected v05 histories are portable and do not rerun retrieval."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from experiments.cytiva import verify_polarity_navigation_package as selected


class PolarityNavigationPackageTests(unittest.TestCase):
    def test_selected_two_runs_verify_without_retrieval(self):
        with patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('No retrieval')):
            self.assertEqual(selected.verify()['contexts'],176)

    def test_selected_manifest_binds_exact_support_inventory(self):
        m=selected.frozen.read(selected.ROOT/selected.PACKAGE/'manifest.json')
        self.assertEqual(set(m['supporting_files']),selected.SUPPORT)
        self.assertEqual(m['v04_export_manifest_sha256_lf'],selected.frozen.digest(selected.ROOT/selected.a.PACKAGE/'manifest.json'))

    def test_changed_archived_code_is_rejected(self):
        p=deepcopy(selected.frozen.read(selected.ROOT/selected.PACKAGE/'provenance.json'))
        record=p['runs']['attempt-a']
        key=next(iter(record['archived_input_overrides']))
        record['archived_input_overrides'][key]+='\n# changed'
        original=selected.frozen.read
        def changed(path):
            if path==selected.ROOT/selected.PACKAGE/'provenance.json':return p
            return original(path)
        with patch.object(selected.frozen,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Archived development input changed'):
                selected.verify()
