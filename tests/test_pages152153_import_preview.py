import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from experiments.cytiva.pages152153_import_preview import main, prepare


class ImportPreviewTests(unittest.TestCase):
    def test_portable_preview_matches_the_recorded_hashes_and_does_not_claim_local_checks(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            output = Path(directory) / 'preview'
            main(['--output', str(output)])
            self.assertEqual({p.name for p in output.iterdir()},
                             {'import_preview.json', 'quarantine.json', 'verification.json'})
            verification = json.loads((output / 'verification.json').read_text(encoding='utf-8'))
            self.assertFalse(verification['original_pdf_sha256_verified'])
            self.assertFalse(verification['source_review_replay']['annotated_run_replayed'])
            self.assertFalse(verification['source_review_replay']['chunks_run_replayed'])
            self.assertEqual(verification['neo4j_connections'], 0)

    def test_note_links_only_target_reviewed_cells_on_the_correct_pages(self):
        output = prepare()['import_preview.json']
        nodes = {node['id']: node for node in output['nodes']}
        links = [edge for edge in output['relationships'] if edge['kind'] == 'CITES_NOTE']
        self.assertEqual(len(links), 15)
        scopes = {}
        for edge in links:
            cell, note = nodes[edge['from']], nodes[edge['to']]
            a, b = cell['citation'], note['citation']
            self.assertEqual(cell['kind'], 'MarkedCell')
            self.assertEqual(note['kind'], 'TableNote')
            self.assertEqual(a['original_pdf_page_1based'], b['original_pdf_page_1based'])
            self.assertEqual(a['pdf_sha256'], b['pdf_sha256'])
            scopes.setdefault(b['ref'], set()).add((a['original_pdf_page_1based'], a['grid_row_0based'],
                                                   a['column_0based'], cell['text']))
        self.assertEqual(scopes, {
            '#/texts/3': {(152, 5, 0, 'MAbTrap Kit 1')},
            '#/texts/4': {(152, 8, 0, 'Protein G Mag Sepharose Xtra 2'),
                          (152, 17, 0, 'Protein A Mag Sepharose Xtra 2')},
            '#/texts/6': {(153, row, 2, 'N/A 3') for row in (1, 2, 3, 8, 9, 10, 15, 16, 17, 20, 21, 22)},
        })
        continuation, = [edge for edge in output['relationships'] if edge['kind'] == 'CONTINUATION_OF']
        self.assertFalse(continuation['inherit_note_scope'])

    def test_quarantine_has_no_graph_rows_or_note_links(self):
        outputs = prepare()
        preview, quarantine = outputs['import_preview.json'], outputs['quarantine.json']
        self.assertFalse(preview['publication_allowed'])
        self.assertFalse(quarantine['graph_eligible'])
        blocked = [1, 9, 13]
        self.assertEqual([row['citation']['grid_row_0based'] for row in quarantine['rows']], blocked)
        rows = [node for node in preview['nodes'] if node['kind'] == 'TableRow']
        self.assertEqual(len(rows), 40)
        for row in rows:
            cite = row['citation']
            if cite['ref'] == '#/tables/0':
                self.assertNotIn(cite['grid_row_0based'], blocked)
        ids = {node['id'] for node in preview['nodes']}
        self.assertTrue(all(edge['from'] in ids and edge['to'] in ids for edge in preview['relationships']))

    def test_wrong_source_pdf_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf, output = Path(directory) / 'wrong.pdf', Path(directory) / 'preview'
            pdf.write_bytes(b'%PDF-wrong-source')
            with self.assertRaisesRegex(ValueError, 'Original PDF digest mismatch'):
                main(['--pdf', str(pdf), '--output', str(output)])
            self.assertFalse(output.exists())
