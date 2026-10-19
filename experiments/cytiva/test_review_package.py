"""Integrity regressions for the curated development review, without local PDFs."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_review_package import PACKAGE, package_digest, verify


class ReviewedPackageTests(unittest.TestCase):
    def test_portable_package_without_private_corpus(self):
        result = verify()
        self.assertFalse(result['source_validation_replayed'])
        self.assertEqual(result['pending'], 0)
        self.assertFalse(result['publication_allowed'])

    def tamper(self, name, mutate):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name) / 'reviewed'
        shutil.copytree(PACKAGE, folder)
        file = folder / name
        data = json.loads(file.read_text(encoding='utf-8'))
        mutate(data)
        file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        # Even after someone refreshes the file hash, internal review bindings must fail.
        manifest_path = folder / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['files'][name] = package_digest(file)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        return folder

    def test_changed_quantity_breaks_claim_review_binding(self):
        def mutate(data):
            claim = next(c for c in data['claims'] if c['id'] == 'c26')
            claim['parameters'][0]['quantities'][0]['values'] = ['301']
        folder = self.tamper('claims.json', mutate)
        # Bind review to the new file to exercise the individual claim digest guard.
        review_path = folder / 'review.json'
        review = json.loads(review_path.read_text(encoding='utf-8'))
        review['candidate_sha256'] = package_digest(folder / 'claims.json')
        review_path.write_text(json.dumps(review), encoding='utf-8')
        manifest_path = folder / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['files']['review.json'] = package_digest(review_path)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Changed reviewed claim: c26'):
            verify(folder)

    def test_removing_reservation_is_rejected(self):
        def mutate(data):
            next(c for c in data['claims'] if c['claim_id'] == 'c32')['reservations'] = []
        with self.assertRaisesRegex(ValueError, 'Reservation mismatch: c32'):
            verify(self.tamper('review.json', mutate))

    def test_publication_cannot_be_enabled_by_review_export(self):
        with self.assertRaisesRegex(ValueError, 'does not authorize publication'):
            verify(self.tamper('review.json', lambda data: data.update(publication_allowed=True)))

    def test_wrong_local_corpus_fails_before_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            corpus = Path(temp) / 'input.json'
            corpus.write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Wrong source corpus'):
                verify(corpus_path=corpus)

    def test_windows_checkout_line_endings_preserve_package_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'reviewed'
            shutil.copytree(PACKAGE, folder)
            for file in folder.iterdir():
                normalized = file.read_bytes().replace(b'\r\n', b'\n')
                file.write_bytes(normalized.replace(b'\n', b'\r\n'))
            self.assertEqual(verify(folder)['status'], 'passed')


if __name__ == '__main__':
    unittest.main()
