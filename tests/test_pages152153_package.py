"""Portable offline review and tamper regressions; no LLM/PDF models required."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_pages152153_package import (
    PACKAGE, ROOT, ORDER, read, verify, file_digest, check_evidence)


class Pages152153PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT,prefix='.pages152153-test-')
        self.addCleanup(self.temp.cleanup)
        self.package=Path(self.temp.name)/'package'
        shutil.copytree(PACKAGE,self.package)

    def change(self,name,mutation):
        p=self.package/name; value=read(p); mutation(value)
        p.write_text(json.dumps(value,ensure_ascii=False)+'\n',encoding='utf-8')
        m=read(self.package/'manifest.json'); m['files'][name]=file_digest(p)
        (self.package/'manifest.json').write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8')

    def content(self):
        payload=read(self.package/'cards.json')
        return {c['card_id']:c for c in payload['cards']},payload['evidence']

    def test_offline_package(self):
        result=verify(self.package)
        self.assertEqual(result['cards'],6)
        self.assertEqual(result['note_cell_bindings'],15)
        self.assertEqual(result['pending'],0)
        self.assertFalse(result['production_retrieval_validated'])

    def test_lf_and_crlf_checkouts_preserve_original_event_chain(self):
        for ending in (b'\n',b'\r\n'):
            for p in self.package.iterdir():
                p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',ending))
            self.assertTrue(verify(self.package)['event_chain_replayed'])

    def test_unchanged_quotation_is_required_even_with_new_package_digest(self):
        self.change('events.json',lambda j:j['events'][4]['decision'].update(original_human_message='Changed'))
        with self.assertRaisesRegex(ValueError,'Original event/quotation'): verify(self.package)

    def test_removed_reservation_cannot_reuse_prior_approval(self):
        self.change('review.json',lambda r:r['cards'][ORDER[5]].update(reservations=[]))
        with self.assertRaisesRegex(ValueError,'Final state'): verify(self.package)

    def test_blank_product_cannot_be_filled(self):
        self.change('cards.json',lambda p:p['evidence']['reconstruction']['cells'][10].update(text='HiTrap MabSelect'))
        with self.assertRaisesRegex(ValueError,'Selected evidence'): verify(self.package)

    def test_na_cannot_be_normalized_to_zero(self):
        self.change('cards.json',lambda p:p['cards'][4]['candidate_cell_note_bindings'][0]['source_cell'].update(text='0'))
        with self.assertRaisesRegex(ValueError,'Original card digest'): verify(self.package)

    def test_note_scope_cannot_move_to_an_unmarked_cell(self):
        self.change('review.json',lambda r:r['cards']['P153-N3']['approved_cell_note_bindings'][0].update(column_0based=3))
        with self.assertRaisesRegex(ValueError,'Final state'): verify(self.package)

    def test_approved_continuation_cannot_become_native_converter_relation(self):
        self.change('review.json',lambda r:r['cards'][ORDER[1]]['approved_annotation'].update(native_converter_relation=True))
        with self.assertRaisesRegex(ValueError,'Final state'): verify(self.package)

    def test_historical_pending_flags_cannot_be_promoted(self):
        self.change('cards.json',lambda p:p['cards'][5].update(human_approved=True))
        with self.assertRaisesRegex(ValueError,'Original card digest'): verify(self.package)

    def test_no_blanket_dataset_or_production_approval(self):
        for flag in ('human_approved','publication_allowed','production_retrieval_validated'):
            with self.subTest(flag=flag):
                original=read(PACKAGE/'review.json')
                (self.package/'review.json').write_text(json.dumps(original),encoding='utf-8')
                self.change('review.json',lambda r:r.update({flag:True}))
                with self.assertRaisesRegex(ValueError,'Final state'): verify(self.package)

    def test_unexpected_pdf_image_or_directory_rejected(self):
        for name in ('source.pdf','image.png','extra'):
            extra=self.package/name
            if name=='extra': extra.mkdir()
            else: extra.write_bytes(b'not a review artifact')
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'inventory'): verify(self.package)
            if extra.is_dir(): extra.rmdir()
            else: extra.unlink()

    def test_wrong_optional_source_document_is_rejected(self):
        p=Path(self.temp.name)/'wrong.json'; p.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Wrong original derived'): verify(self.package,p)

    def test_cell_unit_cut_rejected_after_refreshing_text_fingerprint(self):
        cards,evidence=self.content(); part=evidence['chunks'][2]
        self.assertIn('50 mg/mL',part['text'])
        part['text']=part['text'].replace('50 mg/mL','50',1)
        cards[ORDER[5]]['K800']['chunks'][2]['sha256']=hashlib.sha256(part['text'].encode('utf-8')).hexdigest()
        with self.assertRaisesRegex(ValueError,'Cell text/unit'): check_evidence(cards,evidence)

    def test_covered_span_must_retain_an_anchor_in_same_chunk(self):
        cards,evidence=self.content(); part=evidence['chunks'][4]
        self.assertIn('<span/>',part['text'])
        part['text']=part['text'].replace('<span/>','<c></c>',1)
        cards[ORDER[5]]['K800']['chunks'][4]['sha256']=hashlib.sha256(part['text'].encode('utf-8')).hexdigest()
        with self.assertRaisesRegex(ValueError,'same-chunk span anchor'): check_evidence(cards,evidence)

    def test_quarantined_variant_rows_are_not_released(self):
        cards,evidence=self.content()
        evidence['chunks'][2]['quarantined_variant_rows']=[]
        with self.assertRaisesRegex(ValueError,'Variant quarantine'): check_evidence(cards,evidence)

    def test_source_character_reuse_is_rejected(self):
        cards,evidence=self.content()
        glyphs=[g for c in evidence['reconstruction']['cells'] for g in c['characters']]
        glyphs[-1]['index']=glyphs[0]['index']
        with self.assertRaises(ValueError): check_evidence(cards,evidence)

    def test_k0_boundary_cannot_be_dropped(self):
        cards,evidence=self.content()
        evidence['K0_text']=evidence['K0_text'].replace('<page-break from-excerpt="1" to-excerpt="2"/>','')
        with self.assertRaisesRegex(ValueError,'K0 boundary'): check_evidence(cards,evidence)


if __name__=='__main__':
    unittest.main()
