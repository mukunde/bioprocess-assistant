"""Offline regression checks for immutable page-104 review records and limits."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_page104_package import PACKAGE, check_content, file_digest, read, verify


class Page104PackageTests(unittest.TestCase):
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

    def content(self):
        return {c['id']:c for c in read(self.package/'cards.json')}

    def test_offline_package(self):
        result = verify(self.package)
        self.assertEqual(result['cards'], 6)
        self.assertEqual(result['pending'], 0)
        self.assertEqual(result['automatic_text_only_diagram_semantics'], 'quarantined')

    def test_crlf_checkout(self):
        for p in self.package.iterdir():
            p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
        self.assertTrue(verify(self.package)['event_chain_replayed'])

    def test_card_change_despite_refreshed_file_digest(self):
        self.change('cards.json', lambda cards: cards[1]['proposed_recommended_paths'][0]['node_ids'].append('fab-kappaselect'))
        with self.assertRaisesRegex(ValueError, 'Card digest'):
            verify(self.package)

    def test_original_human_quotation_preserved(self):
        self.change('events.json', lambda j: j['events'][0]['decision'].update(original_human_message='Changed'))
        with self.assertRaisesRegex(ValueError, 'Event decision'):
            verify(self.package)

    def test_removed_reservation_rejected(self):
        self.change('review.json', lambda r: r['decisions'][0].update(reservations=[]))
        with self.assertRaisesRegex(ValueError, 'Reservation'):
            verify(self.package)

    def test_changed_intermediate_scope_rejected(self):
        self.change('events.json', lambda j: j['replay_steps'][0]['state_metadata'].update(scope='Changed'))
        with self.assertRaisesRegex(ValueError, 'Replayed state hash'):
            verify(self.package)

    def test_quarantine_cannot_be_released(self):
        self.change('review.json', lambda r: r.update(automatic_text_only_diagram_semantics='approved'))
        with self.assertRaisesRegex(ValueError, 'approval scope'):
            verify(self.package)

    def test_model_image_delivery_cannot_be_promoted(self):
        self.change('review.json', lambda r: r.update(actual_model_image_attachment_validated=True))
        with self.assertRaisesRegex(ValueError, 'approval scope'):
            verify(self.package)

    def test_unexpected_image_rejected(self):
        (self.package/'picture.png').write_bytes(b'not an exported asset')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            verify(self.package)

    def test_alternative_cannot_become_sequential_step(self):
        cards = self.content()
        cards['P104-alternative']['proposed_alternative_scope']['not_a_process_step'] = False
        with self.assertRaisesRegex(ValueError, 'Alternative scope'):
            check_content(cards)

    def test_vh3_raw_subscript_cannot_be_rewritten(self):
        cards = self.content()
        cards['P104-VH3']['diagram_source_text_items'][0]['text'] = 'VH3'
        with self.assertRaisesRegex(ValueError, 'Raw VH3'):
            check_content(cards)

    def test_serialization_loss_detected(self):
        cards = self.content()
        c = cards['P104-chunking']['chunks'][0]
        c['text'] = c['text'].replace('<text>scFv</text>', '')
        with self.assertRaisesRegex(ValueError, 'Text conservation'):
            check_content(cards)

    def test_wrong_original_conversion(self):
        p = Path(self.temp.name)/'wrong.json'
        p.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Wrong original conversion'):
            verify(self.package,p)


if __name__ == '__main__':
    unittest.main()
