"""Reviewed cell-note scope, byte-bound lineage and quarantine regressions."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from experiments.cytiva.visual_validation import ROOT, digest
from experiments.cytiva.verify_pages152153_package import PACKAGE,read
from experiments.cytiva.apply_reviewed_tables import build_annotations,load_artifact,prepare,execute
from ingestion.table_chunking import OversizedUnit
from ingestion.reviewed_table_chunking import chunk_reviewed,partitions,serialize_reviewed,validate_reviewed


def fixture():
    def cell(r,c,text):
        return {'text':text,'row_span':1,'col_span':1,'start_row_offset_idx':r,'end_row_offset_idx':r+1,
                'start_col_offset_idx':c,'end_col_offset_idx':c+1,'column_header':r==0}
    grid=[[cell(0,c,t) for c,t in enumerate(['Product','Volume','Capacity','Use'])]]
    grid += [[cell(r,c,t) for c,t in enumerate([f'Product {r}',f'{r} mL','N/A 3' if r==2 else '50 mg/column',''])] for r in range(1,7)]
    grid[5][0]['text']=''
    table={'self_ref':'#/tables/0','prov':[{'page_no':1}],
           'data':{'grid':grid,'num_rows':7,'num_cols':4,'table_cells':[c for row in grid for c in row]}}
    annotations={'caption':'A source caption','continuation':{'from_table':'#/tables/1','to_table':'#/tables/0','approval':'c1'},
        'row_groups':[{'table_ref':'#/tables/0','rows':[4,5],'approval':'g1'}],
        'note_bindings':[{'id':'b01','table_ref':'#/tables/0','row':2,'col':2,'note_ref':'#/texts/6','approval':'n3'}],
        'notes':{'#/texts/6':{'text':'3 Screening of capacity, selectivity and purity.'}},
        'approvals':{k:{'serialization_limit':v} for k,v in [('c1','No inherited note scope.'),('g1','Keep the blank product cell.'),('n3','Preserve N/A; no zero inferred.')]},
        'quarantine':{'#/tables/0':[1,3],'#/tables/1':[]}}
    return table,annotations


class ReviewedTableTests(unittest.TestCase):
    def test_quarantine_is_physically_separate_and_all_rows_preserved(self):
        table,a=fixture()
        primary=chunk_reviewed(table,a,len,10000)
        quarantine=chunk_reviewed(table,a,len,10000,True)
        self.assertEqual([r for c in primary for r in c['rows']],[2,4,5,6])
        self.assertEqual([r for c in quarantine for r in c['rows']],[1,3])
        for blocked,chunks in [(False,primary),(True,quarantine)]:
            self.assertTrue(validate_reviewed(table,chunks,a,len,10000,blocked)['source_cells_unchanged'])
        self.assertNotIn('Product 1',primary[0]['text'])
        self.assertEqual(quarantine[0]['annotation_ids'],[])
        self.assertIn('quarantined="true"',quarantine[0]['text'])

    def test_note_body_requires_its_exact_cell_link(self):
        table,a=fixture()
        linked=serialize_reviewed(table,[2],a)
        unrelated=serialize_reviewed(table,[6],a)
        root=ET.fromstring(linked)
        self.assertEqual(root.find('./table/annotations/note-link').attrib,
                         {'id':'b01','row':'2','col':'2','note':'#/texts/6','approval':'n3'})
        self.assertIn('N/A 3',linked)
        self.assertNotIn('Screening of capacity',unrelated)
        self.assertEqual(ET.fromstring(unrelated).findall('./table/notes/note'),[])

    def test_row_group_stays_indivisible_and_blank_is_not_filled(self):
        table,a=fixture()
        budget=max(len(serialize_reviewed(table,g,a)) for g in partitions(table,a)[False])
        chunks=chunk_reviewed(table,a,len,budget)
        self.assertTrue(any(set([4,5])<=set(c['rows']) for c in chunks))
        grouped=next(c for c in chunks if 4 in c['rows'])
        self.assertIsNone(ET.fromstring(grouped['text']).find('./table/body/row[@id="5"]/c').text)
        with self.assertRaisesRegex(ValueError,'group split'): serialize_reviewed(table,[4],a)

    def test_quarantine_propagates_to_entire_reviewed_group(self):
        table,a=fixture(); a['quarantine']['#/tables/0']=[5]
        self.assertEqual(partitions(table,a)[True],[[4,5]])

    def test_reviewed_continuation_is_not_a_native_caption(self):
        table,a=fixture(); table['self_ref']='#/tables/1'; table['prov']=[{'page_no':2}]
        text=serialize_reviewed(table,[1],a)
        root=ET.fromstring(text)
        self.assertEqual(root.find('./table/caption').get('status'),'reviewed-continuation')
        self.assertEqual(root.find('./table/continuation').attrib,{'of':'#/tables/0','approval':'c1'})
        self.assertIn('No inherited note scope.',text)
        self.assertEqual(root.findall('./table/notes/note'),[])

    def test_budget_includes_annotations_and_limitations(self):
        table,a=fixture()
        with self.assertRaises(OversizedUnit):
            chunk_reviewed(table,a,len,len(serialize_reviewed(table,[2],a))-1)

    def test_tampered_note_link_extra_note_and_source_unit_are_rejected(self):
        table,a=fixture(); chunks=chunk_reviewed(table,a,len,10000)
        for old,new in [('row="2" col="2"','row="2" col="1"'),
                        ('<notes scope="explicit-cell-links-only">','<notes scope="explicit-cell-links-only"><note ref="extra">Wrong scope</note>'),
                        ('50 mg/column','50')]:
            bad=deepcopy(chunks); bad[0]['text']=bad[0]['text'].replace(old,new,1)
            bad[0]['token_count']=len(bad[0]['text'])
            with self.subTest(old=old),self.assertRaises(ValueError): validate_reviewed(table,bad,a,len,10000)

    def test_page_and_blanket_approval_metadata_cannot_drift(self):
        table,a=fixture(); chunks=chunk_reviewed(table,a,len,10000)
        for key,value in [('original_pdf_pages',[153]),('production_ready',True),('quarantined',True)]:
            bad=deepcopy(chunks); bad[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): validate_reviewed(table,bad,a,len,10000)

    def test_span_anchor_and_quarantine_cannot_be_separated(self):
        table,a=fixture(); anchor=table['data']['grid'][1][0]
        anchor.update(row_span=2,end_row_offset_idx=3); table['data']['grid'][2][0]=anchor
        table['data']['table_cells']=[c for c in table['data']['table_cells'] if not(c['start_row_offset_idx']==2 and c['start_col_offset_idx']==0)]
        self.assertIn([1,2],partitions(table,a)[True])
        chunks=chunk_reviewed(table,a,len,10000,True)
        self.assertIn('<span/>',chunks[0]['text'])
        self.assertTrue(validate_reviewed(table,chunks,a,len,10000,True)['atomic_groups_intact'])


class ReviewedArtifactTests(unittest.TestCase):
    def test_verified_review_builds_exactly_fifteen_links_without_mutation(self):
        p=read(PACKAGE/'cards.json'); r=read(PACKAGE/'review.json'); e=read(PACKAGE/'events.json')
        before=deepcopy([p,r,e]); a=build_annotations(p,r,e)
        self.assertEqual([p,r,e],before)
        self.assertEqual(len(a['note_bindings']),15)
        self.assertEqual(a['quarantine']['#/tables/0'],[1,9,13])
        self.assertFalse(a['row_groups'][0]['raw_source_rowspan_created'])
        self.assertFalse(a['human_approved'])

    def test_pending_decision_cannot_be_integrated(self):
        p=read(PACKAGE/'cards.json'); r=read(PACKAGE/'review.json'); e=read(PACKAGE/'events.json')
        r['cards']['P153-N3']['decision']='pending'
        with self.assertRaisesRegex(ValueError,'approval'): build_annotations(p,r,e)

    def test_output_collision_precedes_input_read_for_both_commands(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.reviewed-table-test-') as tmp:
            for command in (prepare,execute):
                with self.subTest(command=command.__name__),self.assertRaises(FileExistsError):
                    command(argparse.Namespace(output=Path(tmp)))

    def test_resigned_local_artifact_cannot_change_reviewed_scope(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.reviewed-table-test-') as tmp:
            run=Path(tmp)
            a=build_annotations(read(PACKAGE/'cards.json'),read(PACKAGE/'review.json'),read(PACKAGE/'events.json'))
            a['quarantine']['#/tables/0']=[]
            (run/'annotations.json').write_text(json.dumps(a),encoding='utf-8')
            (run/'document.json').write_text('{}',encoding='utf-8')
            for source,target in [('review.json','review.json'),('events.json','events.json'),('manifest.json','source-package-manifest.json')]:
                (run/target).write_bytes((PACKAGE/source).read_bytes())
            manifest={'files':{p.name:digest(p) for p in run.iterdir()},'source_package_manifest_sha256':digest(PACKAGE/'manifest.json'),
                      'annotations_sha256':digest(run/'annotations.json')}
            (run/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            with patch('experiments.cytiva.apply_reviewed_tables.verify'),self.assertRaisesRegex(ValueError,'annotation scope'):
                load_artifact(run,PACKAGE)


if __name__=='__main__':
    unittest.main()
