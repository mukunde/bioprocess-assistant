"""Portable, offline regression checks for the reviewed page-77 export."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_page077_package import PACKAGE, check_content, file_digest, read, verify


class Page077PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name)/'package'
        shutil.copytree(PACKAGE, self.package)

    def change(self, name, mutate):
        value = read(self.package/name)
        mutate(value)
        (self.package/name).write_text(json.dumps(value, ensure_ascii=False)+'\n', encoding='utf-8')
        manifest = read(self.package/'manifest.json')
        manifest['files'][name] = file_digest(self.package/name)
        (self.package/'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_offline_package(self):
        result = verify(self.package)
        self.assertEqual(result['table_cells'], 68)
        self.assertTrue(result['event_chain_replayed'])
        self.assertFalse(result['production_retrieval_validated'])

    def test_crlf_checkout(self):
        for path in self.package.iterdir():
            path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        self.assertEqual(verify(self.package)['pending'], 0)

    def test_changed_card_with_refreshed_file_digest(self):
        self.change('cards.json', lambda cards: cards[1]['rows'][0]['binding_pH_cell'].update(text='7'))
        with self.assertRaisesRegex(ValueError, 'Card digest'):
            verify(self.package)

    def test_changed_human_quotation(self):
        self.change('events.json', lambda journal: journal['events'][0]['decision'].update(original_human_message='Changed'))
        with self.assertRaisesRegex(ValueError, 'Event decision'):
            verify(self.package)

    def test_removed_reservation(self):
        self.change('review.json', lambda review: review['decisions'][0].update(reservations=[]))
        with self.assertRaisesRegex(ValueError, 'Missing reservation'):
            verify(self.package)

    def test_changed_replay_scope(self):
        self.change('events.json', lambda journal: journal['replay_steps'][0]['state_metadata'].update(scope='Changed'))
        with self.assertRaisesRegex(ValueError, 'Replayed state hash'):
            verify(self.package)

    def test_production_approval_rejected(self):
        self.change('review.json', lambda review: review.update(production_retrieval_validated=True))
        with self.assertRaisesRegex(ValueError, 'approval scope'):
            verify(self.package)

    def test_unexpected_artifact(self):
        (self.package/'manual.pdf').write_bytes(b'not a source PDF')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            verify(self.package)

    def test_blank_species_cannot_be_filled(self):
        cards = {c['id']: c for c in read(self.package/'cards.json')}
        rows = cards['P77-layout-species']['species_subclass_cells']
        next(row[0] for row in rows if not row[0]['text'])['text'] = 'Human'
        with self.assertRaisesRegex(ValueError, 'Species blanks'):
            check_content(cards)

    def test_missing_cross_chunk_caution(self):
        cards = {c['id']: c for c in read(self.package/'cards.json')}
        cards['P77-applicability-4']['source_item']['text'] += ' missing caution'
        with self.assertRaisesRegex(ValueError, 'partition'):
            check_content(cards)

    def test_wrong_original_conversion(self):
        wrong = Path(self.temp.name)/'wrong.json'
        wrong.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Wrong original conversion'):
            verify(self.package, wrong)


if __name__ == '__main__':
    unittest.main()
