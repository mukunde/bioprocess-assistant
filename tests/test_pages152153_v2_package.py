"""Offline v2 lineage, scoped annotations and physical-quarantine regressions."""
import hashlib,json
from pathlib import Path
import shutil,tempfile,unittest
import xml.etree.ElementTree as ET

from experiments.cytiva.verify_pages152153_v2_package import (
    ROOT,PACKAGE,BASE_PACKAGE,CID,read,file_digest,verify,check_annotations,check_evidence)


class Pages152153V2PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT,prefix='.pages152153-v2-test-')
        self.addCleanup(self.temp.cleanup)
        self.package=Path(self.temp.name)/'package'; shutil.copytree(PACKAGE,self.package)
        self.base=read(BASE_PACKAGE/'cards.json')

    def change(self,name,mutation):
        p=self.package/name; value=read(p); mutation(value)
        p.write_text(json.dumps(value,ensure_ascii=False)+'\n',encoding='utf-8')
        m=read(self.package/'manifest.json'); m['files'][name]=file_digest(p)
        (self.package/'manifest.json').write_text(json.dumps(m,ensure_ascii=False),encoding='utf-8')

    def payload(self):return read(self.package/'cards.json')

    @staticmethod
    def refresh_text(payload,index):
        p=payload['evidence']['primary_chunks'][index]
        payload['card']['K800_fragments'][index]['sha256']=hashlib.sha256(p['text'].encode('utf-8')).hexdigest()

    def test_offline_package_and_prior_review(self):
        result=verify(self.package)
        self.assertTrue(result['event_chain_replayed'] and result['prior_review_verified'])
        self.assertEqual(result['primary_rows'],40); self.assertEqual(result['quarantined_rows'],3)
        self.assertFalse(result['production_ready'])

    def test_portable_lf_and_crlf_checkouts(self):
        for ending in (b'\n',b'\r\n'):
            for p in self.package.iterdir():p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',ending))
            self.assertTrue(verify(self.package)['event_chain_replayed'])

    def test_original_french_validation_cannot_be_reworded(self):
        self.change('events.json',lambda j:j['event']['decision'].update(original_human_message='Reworded'))
        with self.assertRaisesRegex(ValueError,'Original event/quotation'):verify(self.package)

    def test_final_reservations_cannot_be_removed(self):
        self.change('review.json',lambda j:j['cards'][CID].update(reservations=[]))
        with self.assertRaisesRegex(ValueError,'Final state'):verify(self.package)

    def test_existing_v1_dependency_digest_is_required(self):
        m=read(self.package/'manifest.json'); m['dependencies'][next(iter(m['dependencies']))]='0'*64
        (self.package/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'dependencies digest'):verify(self.package)

    def test_frozen_preparation_card_is_not_promoted(self):
        self.change('cards.json',lambda j:j['card'].update(human_approved=True))
        with self.assertRaisesRegex(ValueError,'Frozen card'):verify(self.package)

    def test_conservation_approval_is_not_production_approval(self):
        self.change('review.json',lambda j:j.update(production_ready=True))
        with self.assertRaisesRegex(ValueError,'Final state'):verify(self.package)

    def test_inherited_human_quotation_still_matches_v1(self):
        p=self.payload()
        for approvals in (p['annotations']['approvals'],p['card']['approved_annotation_sources']):
            approvals['n1']['original_human_message']='Changed in both copies'
        with self.assertRaisesRegex(ValueError,'Inherited quotation'):
            check_annotations(p,self.base,read(BASE_PACKAGE/'review.json'),read(BASE_PACKAGE/'events.json'))

    def test_note_link_cannot_move_to_unmarked_capacity_cell(self):
        p=self.payload()
        for links in (p['annotations']['note_bindings'],p['card']['source_note_bindings']):links[3]['row']=4
        with self.assertRaisesRegex(ValueError,'note-cell scope'):
            check_annotations(p,self.base,read(BASE_PACKAGE/'review.json'),read(BASE_PACKAGE/'events.json'))

    def test_quarantine_row_cannot_be_inserted_into_primary(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][1]
        root=ET.fromstring(part['text'])
        blocked=ET.fromstring(p['evidence']['quarantine_chunks'][0]['text']).find('./table/body/row')
        root.find('./table/body').insert(0,blocked)
        part['text']=ET.tostring(root,encoding='unicode'); part['rows'].insert(0,1)
        p['card']['K800_fragments'][1]['rows'].insert(0,1)
        self.refresh_text(p,1)
        with self.assertRaisesRegex(ValueError,'row partition'):check_evidence(p,self.base)

    def test_note_body_without_corresponding_cell_link_is_rejected(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][4]
        part['text']=part['text'].replace('<notes scope="explicit-cell-links-only">',
            '<notes scope="explicit-cell-links-only"><note ref="#/texts/3">Wrong inherited scope</note>',1)
        self.refresh_text(p,4)
        with self.assertRaisesRegex(ValueError,'Unscoped'):check_evidence(p,self.base)

    def test_na_raw_label_is_preserved(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][4]
        part['text']=part['text'].replace('N/A 3','0',1); self.refresh_text(p,4)
        with self.assertRaisesRegex(ValueError,'Cell text'):check_evidence(p,self.base)

    def test_covered_rowspan_cannot_become_filled_text(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][4]
        part['text']=part['text'].replace('<span/>','<c>PreDictor MabSelect</c>',1); self.refresh_text(p,4)
        with self.assertRaisesRegex(ValueError,'span anchor'):check_evidence(p,self.base)

    def test_reviewed_group_annotation_is_retained(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][3]
        part['text']=part['text'].replace('<row-group rows="19 20" approval="g1"/>','',1); self.refresh_text(p,3)
        with self.assertRaisesRegex(ValueError,'Group annotation'):check_evidence(p,self.base)

    def test_continuation_caption_is_not_native(self):
        p=self.payload(); part=p['evidence']['primary_chunks'][4]
        part['text']=part['text'].replace('status="reviewed-continuation"','status="native"',1); self.refresh_text(p,4)
        with self.assertRaisesRegex(ValueError,'Caption context'):check_evidence(p,self.base)

    def test_unexpected_source_assets_are_rejected(self):
        p=self.package/'source.pdf'; p.write_bytes(b'not an allowed artifact')
        with self.assertRaisesRegex(ValueError,'inventory'):verify(self.package)

    def test_private_absolute_paths_are_rejected(self):
        m=read(self.package/'manifest.json'); m['extra']='C:/Users/private/source.pdf'
        (self.package/'manifest.json').write_text(json.dumps(m),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Private paths'):verify(self.package)

    def test_wrong_optional_local_artifacts_are_rejected(self):
        p=Path(self.temp.name)/'wrong'; p.mkdir(); (p/'document.json').write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Wrong annotated document'):verify(self.package,annotated_run=p)
        (p/'manifest.json').write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Wrong chunks manifest'):verify(self.package,chunks_run=p)


if __name__=='__main__':unittest.main()
