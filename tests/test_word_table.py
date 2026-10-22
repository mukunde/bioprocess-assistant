"""Word-table safety regressions with synthetic coordinates, no PDF/model/runtime."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva.word_table import canonical_spec_sha256, main, reconstruct, whitespace_cut


def fixture():
    words = []

    def add(text, x, y, width=35, height=10):
        words.append({'id': len(words), 'text': text,
                      'bbox': {'l': x, 't': y, 'r': x+width, 'b': y+height,
                               'coord_origin': 'TOPLEFT'}})

    add('MabSelect', 100, 10)
    add('MabSelect', 250, 10)
    add('B', 295, 10, 10)
    add('Description', 100, 40, 70)
    add('Description', 250, 40, 70)
    add('Speed', 10, 80)
    add('4', 46, 78, 5, 6)
    add('500', 100, 80, 20)
    add('cm/h', 125, 80, 25)
    add('300', 250, 80, 20)
    add('cm/h', 275, 80, 25)
    add('Formats', 10, 120, 45)
    for x in (100, 250):
        add('Pack', x, 120)
        add('Tube', x, 140)
    add('Footnote', 10, 180, 70)
    export = {'source_map': {'source_sha256': '0'*64,
                            'pages': [{'original_pdf_page_1based': 88}]},
              'pages': [{'size': {'width': 400, 'height': 250}, 'words': words}]}
    spec = {'source_sha256': '0'*64, 'original_page_1based': 88,
            'page_size': {'width': 400, 'height': 250}, 'fill_missing_cells': False,
            'description_rows': 1, 'labelled_rows': 2, 'product_columns': 2,
            'table_bbox': {'l': 0, 't': 5, 'r': 400, 'b': 170},
            'header_band': {'t': 5, 'b': 25}, 'header_anchor_text': 'MabSelect',
            'column_gap_search': 40, 'row_gap_search': 20, 'minimum_gap': 0.5,
            'line_overlap_fraction': 0.5}
    return export, spec


class WordTableTests(unittest.TestCase):
    def test_new_manifest_preserves_bytes_and_portable_spec_identity(self):
        root = Path(__file__).resolve().parents[1]
        export, spec = fixture()
        with tempfile.TemporaryDirectory(dir=root, prefix='.word-table-test-') as folder:
            folder = Path(folder)
            words = folder/'words.json'; words.write_text(json.dumps(export), encoding='utf-8')
            outputs = []
            raw_digests = []
            for name, newline in [('lf', '\n'), ('crlf', '\r\n')]:
                raw = (json.dumps(spec, indent=2)+'\n').replace('\n', newline).encode('utf-8')
                config = folder/(name+'.json'); config.write_bytes(raw)
                output = folder/name
                with patch.object(sys, 'argv', ['word_table', '--words', str(words),
                        '--spec', str(config), '--output', str(output)]), patch(
                        'experiments.cytiva.visual_validation.network_guard', return_value=[]), patch('builtins.print'):
                    main()
                manifest = json.loads((output/'manifest.json').read_text(encoding='utf-8'))
                self.assertEqual(manifest['spec_sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(manifest['spec_canonical_sha256'], canonical_spec_sha256(spec))
                self.assertEqual(manifest['spec_identity_policy'], 'sha256_canonical_json_utf8')
                outputs.append(json.loads((output/'table.json').read_text(encoding='utf-8')))
                raw_digests.append(manifest['spec_sha256'])
            self.assertEqual(outputs[0], outputs[1])
            self.assertNotEqual(*raw_digests)

    def test_repeated_values_have_distinct_provenance_and_no_word_reuse(self):
        export, spec = fixture()
        table = reconstruct(export, spec)
        left, right = table['cells'][3][1:]
        self.assertEqual(left['text'], 'Pack Tube')
        self.assertEqual(right['text'], 'Pack Tube')
        self.assertTrue(set(left['word_ids']).isdisjoint(right['word_ids']))
        ids = [wid for row in table['cells'] for cell in row for wid in cell['word_ids']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), table['selected_word_count'])
        self.assertEqual(table['cells'][0][0]['text'], '')
        self.assertFalse(table['human_approved'])
        self.assertFalse(table['publication_allowed'])

    def test_deleted_cell_remains_empty_instead_of_copying_identical_neighbour(self):
        export, spec = fixture()
        export['pages'][0]['words'] = [w for w in export['pages'][0]['words']
                                     if not (w['bbox']['l'] == 250 and w['bbox']['t'] >= 120)]
        table = reconstruct(export, spec)
        self.assertEqual(table['cells'][3][1]['text'], 'Pack Tube')
        missing = table['cells'][3][2]
        self.assertEqual(missing['text'], '')
        self.assertEqual(missing['word_ids'], [])
        self.assertEqual(missing['status'], 'empty_no_source_words')

    def test_superscript_is_not_moved_into_the_velocity_value(self):
        export, spec = fixture()
        table = reconstruct(export, spec)
        self.assertEqual([c['text'] for c in table['cells'][2]],
                         ['Speed 4', '500 cm/h', '300 cm/h'])

    def test_no_separator_is_an_error_rather_than_a_centroid_guess(self):
        word = {'bbox': {'l': 50, 'r': 110, 't': 0, 'b': 10}}
        with self.assertRaisesRegex(ValueError, 'No unambiguous x separator'):
            whitespace_cut([word], 100, 'x', 40, 0.5)

    def test_partial_region_word_quarantines_instead_of_silently_clipping(self):
        export, spec = fixture()
        word = {'id': 999, 'text': 'crossing',
                'bbox': {'l': -5, 'r': 5, 't': 140, 'b': 150, 'coord_origin': 'TOPLEFT'}}
        export['pages'][0]['words'].append(word)
        result = reconstruct(export, spec)
        self.assertEqual(result['status'], 'quarantined_geometry')
        self.assertEqual([w['id'] for w in result['table_boundary_words']], [999])
        self.assertNotIn(999, [wid for row in result['cells'] for cell in row for wid in cell['word_ids']])

    def test_wrong_source_page_geometry_or_requested_filling_are_rejected(self):
        export, spec = fixture()
        mutations = [('source', lambda e, s: e['source_map'].update(source_sha256='wrong')),
                     ('page', lambda e, s: e['source_map']['pages'][0].update(original_pdf_page_1based=89)),
                     ('filling', lambda e, s: s.update(fill_missing_cells=True)),
                     ('origin', lambda e, s: e['pages'][0]['words'][0]['bbox'].update(coord_origin='BOTTOMLEFT')),
                     ('duplicate', lambda e, s: e['pages'][0]['words'].append(copy.deepcopy(e['pages'][0]['words'][0])))]
        for name, mutate in mutations:
            with self.subTest(name=name):
                e, s = copy.deepcopy(export), copy.deepcopy(spec)
                mutate(e, s)
                with self.assertRaises(ValueError):
                    reconstruct(e, s)

    def test_identical_input_replays_deterministically(self):
        export, spec = fixture()
        self.assertEqual(reconstruct(export, spec), reconstruct(export, spec))

    def test_existing_output_is_preserved_before_reading_input(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root, prefix='.word-table-test-') as folder:
            sentinel = Path(folder)/'sentinel'
            sentinel.write_text('keep', encoding='utf-8')
            with patch.object(sys, 'argv', ['word_table', '--words', 'missing.json',
                                          '--spec', 'missing.json', '--output', folder]):
                with self.assertRaises(FileExistsError):
                    main()
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep')


if __name__ == '__main__':
    unittest.main()
