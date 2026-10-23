"""Offline consistency and tamper regressions for the cleaning reference review."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from experiments.cytiva.verify_cleaning_retrieval_package import (
    PACKAGE, ROOT, read, verify, file_digest)


class CleaningRetrievalPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp', prefix='cleaning-review-test-')
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'package'
        shutil.copytree(PACKAGE, self.package)

    def change(self, name, mutation):
        path = self.package / name
        data = read(path)
        mutation(data)
        path.write_text(json.dumps(data, ensure_ascii=False) + '\n', encoding='utf-8')
        manifest = read(self.package / 'manifest.json')
        if name in manifest['files']:
            manifest['files'][name] = file_digest(path)
            (self.package / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_offline_replay(self):
        result = verify(self.package)
        self.assertEqual(result['validated_with_reservation'], 10)
        self.assertTrue(result['event_chain_replayed'])
        self.assertFalse(result['publication_allowed'])

    def test_lf_crlf_checkouts(self):
        for ending in (b'\n', b'\r\n'):
            for path in self.package.iterdir():
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', ending))
            self.assertTrue(verify(self.package)['event_chain_replayed'])

    def test_original_french_message_preserved(self):
        self.change('events.json', lambda x: x['events'][0].update(original_human_message='Reworded'))
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_reservations_preserved(self):
        self.change('events.json', lambda x: x['events'][4]['reservations'].pop())
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_required_warning_not_dropped(self):
        self.change('events.json', lambda x: x['events'][3]['evidence_sha256'].pop('E166-W'))
        with self.assertRaisesRegex(ValueError, 'Indispensable evidence'): verify(self.package)

    def test_product_scope_bound(self):
        self.change('events.json', lambda x: x['events'][5]['evidence_sha256'].update({'E167-SH': '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'Evidence binding'): verify(self.package)

    def test_event_order_bound(self):
        def swap(x): x['events'][0], x['events'][1] = x['events'][1], x['events'][0]
        self.change('events.json', swap)
        with self.assertRaisesRegex(ValueError, 'Event order'): verify(self.package)

    def test_final_review_replayed(self):
        self.change('review.json', lambda x: x['decisions'][9].update(reservations=[]))
        with self.assertRaisesRegex(ValueError, 'Final review'): verify(self.package)

    def test_publication_not_implied(self):
        self.change('manifest.json', lambda x: x.update(publication_allowed=True))
        with self.assertRaisesRegex(ValueError, 'Scope promoted'): verify(self.package)

    def test_benchmark_not_implied(self):
        self.change('events.json', lambda x: x['state_metadata'][0].update(benchmark_executed=True))
        with self.assertRaisesRegex(ValueError, 'State scope'): verify(self.package)

    def test_source_identity_bound(self):
        self.change('manifest.json', lambda x: x.update(source_pdf_sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'PDF identity'): verify(self.package)

    def test_historical_snapshot_cannot_be_omitted(self):
        self.change('manifest.json', lambda x: x['historical_files'].pop('review-after-005.json'))
        with self.assertRaisesRegex(ValueError, 'Historical inventory'): verify(self.package)


if __name__ == '__main__':
    unittest.main()
