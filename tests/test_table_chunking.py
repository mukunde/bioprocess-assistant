"""Row/cell regressions use synthetic data, never the proprietary manual."""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from ingestion.table_chunking import (OversizedUnit, chunk_table, row_groups,
                                      serialize_table, validate_chunks)
from experiments.cytiva.repair_table152 import extract_cells, replace_rows, run_chunks, repair
from experiments.cytiva.visual_validation import ROOT, digest


def cell(row, col, text, span=1):
    return {'text': text, 'row_span': span, 'col_span': 1,
            'start_row_offset_idx': row, 'end_row_offset_idx': row+span,
            'start_col_offset_idx': col, 'end_col_offset_idx': col+1,
            'column_header': row == 0, 'bbox': None}


def table():
    grid = [[cell(0, c, t) for c,t in enumerate(['Product', 'Volume', 'Capacity', 'Use'])]]
    grid += [[cell(r, c, t) for c,t in enumerate(
        [f'Product {r}', f'{r} mL', '50 mg/column' if r % 2 else 'N/A 3', '' if r % 2 else '•'])]
        for r in range(1, 7)]
    return {'self_ref': '#/tables/0', 'data': {'grid': grid, 'num_rows': 7, 'num_cols': 4,
                                            'table_cells': [c for row in grid for c in row]}}


CTX = {'caption': 'A caption with <markup> & context', 'caption_status': 'native',
       'notes': [{'ref': '#/texts/1', 'text': '3 Conditions apply; not a capacity of zero.'}]}
COUNT = len  # Small deterministic budget; real-run audit uses cached cl100k_base.


class TableChunkingTests(unittest.TestCase):
    def test_whole_rows_units_markers_headers_and_notes_survive_each_chunk(self):
        t = table()
        one = len(serialize_table(t, [1], CTX)); two = len(serialize_table(t, [1, 2], CTX))
        budget = two + 5
        chunks = chunk_table(t, CTX, COUNT, budget)
        self.assertGreater(len(chunks), 1)
        check = validate_chunks(t, chunks, CTX, COUNT, budget)
        self.assertEqual(check['ordered_rows_once'], 6)
        self.assertTrue(all('50 mg/column' in c['text'] or 'N/A 3' in c['text'] for c in chunks))
        self.assertTrue(all('<header>' in c['text'] and '<notes' in c['text'] for c in chunks))
        self.assertGreater(budget, one)

    def test_explicit_native_rowspan_is_atomic_without_product_fill(self):
        t = table(); original = deepcopy(t)
        first = t['data']['grid'][1][0]
        first.update(row_span=3, end_row_offset_idx=4)
        for r in (2, 3):
            t['data']['grid'][r][0] = first
        t['data']['table_cells'] = [c for c in t['data']['table_cells']
                                   if c['start_col_offset_idx'] != 0 or c['start_row_offset_idx'] not in (2, 3)]
        self.assertEqual(row_groups(t), [[1, 2, 3], [4], [5], [6]])
        budget = len(serialize_table(t, [1, 2, 3], CTX))
        chunks = chunk_table(t, CTX, COUNT, budget)
        validate_chunks(t, chunks, CTX, COUNT, budget)
        self.assertIn('<span/>', chunks[0]['text'])
        self.assertEqual(chunks[0]['text'].count('Product 1'), 1)
        self.assertNotIn('Product 2', chunks[0]['text'])
        self.assertEqual(original['data']['grid'][2][0]['text'], 'Product 2')

    def test_candidate_blank_product_group_is_atomic_and_stays_blank(self):
        t = table(); t['data']['grid'][2][0]['text'] = ''
        ctx = {**CTX, 'candidate_row_groups': [[1, 2]]}
        chunks = chunk_table(t, ctx, COUNT, len(serialize_table(t, [1,2], ctx)))
        self.assertEqual(chunks[0]['rows'], [1, 2])
        row = ET.fromstring(chunks[0]['text']).find('./table/body/row[@id="2"]')
        self.assertIsNone(row[0].text)

    def test_oversized_row_or_span_is_quarantined_never_truncated(self):
        t = table(); t['data']['grid'][1][2]['text'] = 'x' * 5000
        with self.assertRaisesRegex(OversizedUnit, 'no output truncation'):
            chunk_table(t, CTX, COUNT, 800)

    def test_transitive_span_groups_and_invalid_candidates(self):
        t = table()
        a = t['data']['grid'][1][0]; a.update(row_span=3, end_row_offset_idx=4)
        b = t['data']['grid'][3][1]; b.update(row_span=2, end_row_offset_idx=5)
        for r in (2, 3): t['data']['grid'][r][0] = a
        t['data']['grid'][4][1] = b
        self.assertEqual(row_groups(t)[0], [1, 2, 3, 4])
        with self.assertRaises(ValueError): row_groups(t, [[1, 3]])
        with self.assertRaises(ValueError): row_groups(t, [[0, 1]])

    def test_audit_rejects_lost_cell_note_and_row(self):
        t = table(); chunks = chunk_table(t, CTX, COUNT, 2000)
        for mutation in ('cell', 'note', 'row'):
            bad = deepcopy(chunks)
            if mutation == 'cell': bad[0]['text'] = bad[0]['text'].replace('50 mg/column', '50', 1)
            if mutation == 'note': bad[0]['text'] = bad[0]['text'].replace('Conditions apply;', 'Missing;', 1)
            if mutation == 'row': bad[0]['rows'] = []
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_chunks(t, bad, CTX, COUNT, 2000)

    def test_embedded_header_and_header_data_span_fail_closed(self):
        t = table(); t['data']['grid'][2][0]['column_header'] = True
        with self.assertRaises(ValueError): row_groups(t)

    def test_malformed_grid_and_inconsistent_spans_fail_closed(self):
        t = table(); t['data']['grid'][2].pop()
        with self.assertRaises(ValueError): row_groups(t)
        t = table(); t['data']['grid'][2][0]['row_span'] = 2
        with self.assertRaises(ValueError): row_groups(t)
        t = table(); t['data']['table_cells'][0]['end_row_offset_idx'] = 2
        with self.assertRaises(ValueError): row_groups(t)


class ReconstructionTests(unittest.TestCase):
    @staticmethod
    def source_fixture():
        # Synthetic one-glyph cell, proves population comes from bounded PDF text.
        glyph = {'index': 42, 'text': '9', 'bbox_top_left_pt': [350, 855, 357, 864]}
        chars = {'source_page_1based': 152, 'coordinate_origin': 'top_left',
                 'width_pt': 1920, 'height_pt': 1080, 'characters': [glyph]}
        class NativeText:
            def get_text_bounded(self, l, b, r, t):
                return ' 9 ' if l == 310 and t == 233 else ''
            def get_text_range(self, index, count): return '9' if index == 42 else '8'
            def get_charbox(self, index): return (350, 216, 357, 225)
        return NativeText(), chars

    def test_coordinate_population_preserves_blanks_and_native_proof(self):
        native, chars = self.source_fixture()
        rows, ledger = extract_cells(native, chars)
        self.assertEqual(rows[0][1]['text'], '9')
        self.assertEqual(rows[1][0]['text'], '')
        self.assertEqual(len(ledger), 30)
        entry = ledger[1]
        self.assertEqual(entry['characters'][0]['index'], 42)
        self.assertEqual(entry['raw_bounded_text'], ' 9 ')
        self.assertEqual(sum(e['source_blank'] for e in ledger), 29)

    def test_missing_glyph_wrong_index_box_and_boundary_are_rejected(self):
        native, chars = self.source_fixture()
        for field, value in [('text', '8'), ('index', 43), ('bbox_top_left_pt', [350, 855, 358, 864]),
                             ('bbox_top_left_pt', [309, 855, 357, 864])]:
            bad = deepcopy(chars); bad['characters'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                extract_cells(native, bad)
        bad = deepcopy(chars); bad['characters'] = []
        with self.assertRaises(ValueError): extract_cells(native, bad)

    def test_only_target_rows_change_and_input_is_not_mutated(self):
        native, chars = self.source_fixture(); rows, _ = extract_cells(native, chars)
        grid = [[cell(r,c,f'{r}:{c}') for c in range(10)] for r in range(21)]
        source = {'texts': [{'text':'unchanged'}], 'tables': [
            {'data': {'num_rows':21, 'num_cols':10, 'grid':grid,
                      'table_cells':[c for row in grid for c in row]}}, table()]}
        frozen = deepcopy(source); result = replace_rows(source, rows)
        self.assertEqual(source, frozen)
        self.assertEqual(result['tables'][1], frozen['tables'][1])
        self.assertEqual(result['tables'][0]['data']['grid'][:19], grid[:19])
        self.assertEqual(result['texts'], source['texts'])
        self.assertEqual(result['tables'][0]['data']['num_rows'], 22)
        self.assertEqual(result['tables'][0]['data']['grid'][20][0]['text'], '')


class LauncherTests(unittest.TestCase):
    def fixture(self, root):
        run = root/'run'; run.mkdir()
        t = table(); t['prov'] = [{'page_no':1}]
        doc = {'tables': [t], 'texts': [{'self_ref':'#/texts/0', 'label':'text', 'text':'Native text'}]}
        (run/'document.json').write_text(json.dumps(doc), encoding='utf-8')
        context = {'human_approved':False, 'diagnostic_only':True,
                   'document_sha256':digest(run/'document.json'), 'table_context':{
                       '#/tables/0':{**CTX, 'candidate_row_groups':[], 'quarantined_variant_rows':[]}}}
        (run/'context.json').write_text(json.dumps(context), encoding='utf-8')
        self.seal(run)
        return argparse.Namespace(run=run, output=root/'output', budgets=[800])

    @staticmethod
    def seal(run):
        (run/'manifest.json').write_text(json.dumps({'files':{
            name:digest(run/name) for name in ('document.json','context.json')}}), encoding='utf-8')

    def test_both_launchers_reject_existing_output_before_any_input_read(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.table-test-') as tmp:
            args = argparse.Namespace(output=Path(tmp))
            for command in (run_chunks, repair):
                with self.subTest(command=command.__name__), self.assertRaises(FileExistsError): command(args)

    def test_context_and_manifest_tampering_fail_before_output(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.table-test-') as tmp:
            args = self.fixture(Path(tmp))
            context_path = args.run/'context.json'
            ctx = json.loads(context_path.read_text(encoding='utf-8'))
            ctx['document_sha256'] = 'bad'
            context_path.write_text(json.dumps(ctx), encoding='utf-8')
            with patch('experiments.cytiva.repair_table152.network_guard', return_value=[]):
                with self.assertRaisesRegex(ValueError, 'manifest hash'): run_chunks(args)
                self.seal(args.run)
                with self.assertRaisesRegex(ValueError, 'Context/document'): run_chunks(args)
            self.assertFalse(args.output.exists())

    def test_oversized_input_does_not_leave_a_partial_success(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.table-test-') as tmp:
            args = self.fixture(Path(tmp))
            path = args.run/'document.json'
            doc = json.loads(path.read_text(encoding='utf-8'))
            doc['tables'][0]['data']['grid'][1][2]['text'] = 'x' * 5000
            path.write_text(json.dumps(doc), encoding='utf-8')
            path = args.run/'context.json'; ctx = json.loads(path.read_text(encoding='utf-8'))
            ctx['document_sha256'] = digest(args.run/'document.json')
            path.write_text(json.dumps(ctx), encoding='utf-8'); self.seal(args.run)
            fake = SimpleNamespace(get_encoding=lambda name: SimpleNamespace(encode=lambda text: list(text)))
            with patch('experiments.cytiva.repair_table152.network_guard', return_value=[]), patch.dict('sys.modules', {'tiktoken':fake}):
                with self.assertRaises(OversizedUnit): run_chunks(args)
            self.assertFalse(args.output.exists())


if __name__ == '__main__':
    unittest.main()
