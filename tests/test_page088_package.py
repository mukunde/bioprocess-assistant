"""Offline integrity regressions for the curated page-88 review."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_page088_package import PACKAGE, file_digest, local_digest, verify


class Page088PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package=Path(self.temp.name)/'package'
        shutil.copytree(PACKAGE,self.package)

    def mutate(self,name,change,refresh=False):
        path=self.package/name
        value=json.loads(path.read_text(encoding='utf-8'));change(value)
        path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        if refresh:
            manifest=self.package/'manifest.json'
            m=json.loads(manifest.read_text(encoding='utf-8'));m['files'][name]=file_digest(path)
            manifest.write_text(json.dumps(m),encoding='utf-8')

    def test_offline_package(self):
        result=verify(self.package)
        self.assertEqual(result['cells'],40)
        self.assertEqual(result['pending'],0)
        self.assertFalse(result['publication_allowed'])

    def test_windows_checkout(self):
        for f in self.package.iterdir():
            f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
        self.assertEqual(verify(self.package)['status'],'passed')

    def test_changed_quantity_rejected(self):
        self.mutate('packet.json',lambda p:p['table']['cells'][2][1].update(text='999 mg'),refresh=True)
        with self.assertRaisesRegex(ValueError,'Wrong packet binding'):verify(self.package)

    def test_changed_human_quotation_rejected(self):
        self.mutate('events.json',lambda j:j['events'][0]['decision'].update(original_human_message='fabricated'),refresh=True)
        with self.assertRaisesRegex(ValueError,'Event decision mismatch'):verify(self.package)

    def test_missing_reservation_rejected(self):
        self.mutate('review.json',lambda r:r['decisions'][0].update(reservations=[]),refresh=True)
        with self.assertRaises(ValueError):verify(self.package)

    def test_changed_state_chain_rejected(self):
        self.mutate('manifest.json',lambda m:m['lineage']['review_state_file_sha256'].update({'004':'0'*64}))
        with self.assertRaisesRegex(ValueError,'Replayed state hash mismatch'):verify(self.package)

    def test_publication_is_not_authorized_by_review(self):
        self.mutate('review.json',lambda r:r.update(publication_allowed=True),refresh=True)
        review=json.loads((self.package/'review.json').read_text(encoding='utf-8'))
        self.mutate('manifest.json',lambda m:m['lineage'].update(final_review_original_file_sha256=local_digest(review)))
        with self.assertRaisesRegex(ValueError,'Wrong approval scope'):verify(self.package)

    def test_unexpected_source_artifact_rejected(self):
        (self.package/'source.pdf').write_bytes(b'not a PDF')
        with self.assertRaisesRegex(ValueError,'Unexpected package file'):verify(self.package)


if __name__=='__main__':unittest.main()
