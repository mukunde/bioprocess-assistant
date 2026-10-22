"""Synthetic note binding regressions; no PDF, model, API or private artifacts."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva.table_notes import (attach_notes, main, object_sha,
                                           review_cards, sha, validate_input_hashes, write_review)


def fixture():
    words, textlines, cells = [], [], []
    labels = ['', '', 'Dynamic binding capacity', 'Recommended operating mobile velocity',
              'Recommended CIP reagents', 'Ligand', 'Particle size', 'Available formats']

    def word(text, x, y, small=False):
        raw = {'id': len(words), 'text': text, 'bbox': {'l': x, 'r': x+max(4, len(text)*5),
               't': y-2 if small else y, 'b': y+3 if small else y+10, 'coord_origin': 'TOPLEFT'}}
        words.append(raw)
        return {**copy.deepcopy(raw), 'word_ref': f'/pages/0/words/{raw["id"]}'}

    for r in range(8):
        row = []
        for c in range(5):
            marker = None
            if c == 0:
                text = labels[r]
                marker = {3: '4', 6: '5'}.get(r)
            elif r == 0:
                text = 'Product '+str(c)
            elif r == 2:
                text, marker = '~ 31 mg/mL', {1: '1', 2: '2', 3: '1', 4: '3'}[c]
            elif r == 3:
                text = str(900+c)+' cm/h'
            else:
                text = 'Source words'
            selected, x, y = [], c*300+10, r*50+10
            for token in text.split():
                selected.append(word(token, x, y))
                x += max(4, len(token)*5)+5
            if marker:
                selected.append(word(marker, x, y, small=True))
            row.append({'row': r, 'col': c, 'text': ' '.join(w['text'] for w in selected),
                        'words': selected, 'word_ids': [w['id'] for w in selected]})
        cells.append(row)
    # Deliberately different quantities from the manual prove parsing is source-driven.
    notes = [
        '1 Determined at 11% breakthrough by frontal analysis at a mobile phase velocity of 501 cm/h at a 21 cm bed height (residence time: 2.5 min).',
        '2 Determined at 12% breakthrough by frontal analysis at a mobile phase velocity of 252 cm/h at a 11 cm bed height (residence time: 2.6 min).',
        '3 Determined at 13% breakthrough by frontal analysis at a mobile phase velocity of 103 cm/h at a 12 cm bed height (residence time: 6.1 min).',
        '4 In AxiChrom 999 column, 21 cm bed height operating at < 0.3 Mpa (3 bar, 44 psi), 26°C.',
        '5 d 50v is the median particle size of the cumulative volume distribution.']
    for i, text in enumerate(notes):
        x, y = 20, 500+i*30
        start = x
        for token in text.split():
            w = word(token, x, y)
            x = w['bbox']['r']+5
        textlines.append({'id': i, 'text': text, 'bbox': {'l': start, 'r': x-5,
                          't': y, 'b': y+10, 'coord_origin': 'TOPLEFT'}})
    export = {'source_map': {'source_sha256': '0'*64,
                            'pages': [{'original_pdf_page_1based': 88}]},
              'pages': [{'words': words, 'textlines': textlines}]}
    table = {'status': 'candidate_pending_review', 'original_page_1based': 88,
             'human_approved': False, 'publication_allowed': False, 'cells': cells}
    spec = {'source_sha256': '0'*64, 'original_page_1based': 88, 'automatic_approval': False,
            'row_label_scope': 'same_row_nonempty_product_cells',
            'quantity_normalization': 'none', 'unit_conversion': 'none',
            'notes_bbox': {'l': 0, 'r': 4000, 't': 495, 'b': 650},
            'expected_marker_counts': {'1': 2, '2': 1, '3': 1, '4': 1, '5': 1},
            'superscript_height_ratio_max': 0.75, 'superscript_bottom_raise_ratio_min': 0.25}
    return table, export, spec


class TableNotesTests(unittest.TestCase):
    def identity_fixture(self, canonical=True):
        layout = {'table_bbox': {'l': 1, 'r': 10}, 'fill_missing_cells': False}
        raw = (json.dumps(layout, indent=2)+'\n').replace('\n', '\r\n').encode('utf-8')
        parent = {'word_export_sha256': sha(b'words'), 'spec_sha256': sha(raw)}
        notes = {'layout_sha256': sha(raw)}
        if canonical:
            parent.update(spec_canonical_sha256=object_sha(layout),
                          spec_identity_policy='sha256_canonical_json_utf8')
            notes['layout_canonical_sha256'] = object_sha(layout)
        return {'words': b'words', 'layout': raw}, {'layout': layout,
                'parent_manifest': parent, 'notes_spec': notes}

    def test_new_spec_identity_accepts_lf_crlf_and_json_reformatting(self):
        payloads, parsed = self.identity_fixture()
        expected = validate_input_hashes(payloads, parsed)
        for raw in (payloads['layout'].replace(b'\r\n', b'\n'),
                    json.dumps(parsed['layout'], sort_keys=True).encode('utf-8')):
            with self.subTest(raw=raw):
                payloads['layout'] = raw
                self.assertEqual(validate_input_hashes(payloads, parsed), expected)

    def test_legacy_specs_remain_strict_and_are_not_silently_migrated(self):
        payloads, parsed = self.identity_fixture(canonical=False)
        before = copy.deepcopy(parsed)
        validate_input_hashes(payloads, parsed)
        self.assertEqual(parsed, before)
        payloads['layout'] = payloads['layout'].replace(b'\r\n', b'\n')
        with self.assertRaisesRegex(ValueError, 'legacy parent layout bytes'):
            validate_input_hashes(payloads, parsed)
        # A fresh byte-bound parent still cannot waive the legacy notes binding.
        parsed['parent_manifest']['spec_sha256'] = sha(payloads['layout'])
        with self.assertRaisesRegex(ValueError, 'legacy notes layout bytes'):
            validate_input_hashes(payloads, parsed)

    def test_spec_content_or_source_change_still_fails(self):
        for kind in ('layout', 'notes_binding', 'parent_binding', 'words', 'policy'):
            with self.subTest(kind=kind):
                payloads, parsed = self.identity_fixture()
                if kind == 'layout':
                    parsed['layout']['table_bbox']['r'] = 11
                    payloads['layout'] = json.dumps(parsed['layout']).encode('utf-8')
                elif kind == 'notes_binding': parsed['notes_spec']['layout_canonical_sha256'] = '0'*64
                elif kind == 'parent_binding': parsed['parent_manifest']['spec_canonical_sha256'] = '0'*64
                elif kind == 'words': payloads['words'] = b'changed'
                else: parsed['parent_manifest']['spec_identity_policy'] = 'unsupported'
                with self.assertRaisesRegex(ValueError, 'Frozen input hash mismatch'):
                    validate_input_hashes(payloads, parsed)

    def test_direct_and_row_label_scope_produce_exact_expected_bindings(self):
        table, export, spec = fixture()
        original = copy.deepcopy(table)
        packet = attach_notes(table, export, spec)
        scopes = {n: {tuple(b['cell']) for b in packet['bindings'] if b['note_id'] == n}
                  for n in packet['notes']}
        self.assertEqual(scopes, {'1': {(2, 1), (2, 3)}, '2': {(2, 2)}, '3': {(2, 4)},
                                 '4': {(3, 1), (3, 2), (3, 3), (3, 4)},
                                 '5': {(6, 1), (6, 2), (6, 3), (6, 4)}})
        self.assertEqual(len(packet['anchors']), 6)
        self.assertEqual(table, original)
        self.assertFalse(packet['human_approved'])
        self.assertFalse(packet['publication_allowed'])

    def test_measurement_velocity_does_not_replace_recommended_velocity(self):
        table, export, spec = fixture()
        packet = attach_notes(table, export, spec)
        condition = next(c for c in packet['notes']['2']['conditions']
                         if c['field'] == 'capacity_measurement.mobile_phase_velocity')
        self.assertEqual(condition['value'], '252')
        self.assertEqual(packet['table']['cells'][3][2]['text'], '902 cm/h')
        self.assertEqual(packet['table']['cells'][3][2]['note_refs'], ['4'])

    def test_pressure_operator_units_and_parentheses_are_not_recomputed(self):
        table, export, spec = fixture()
        note = attach_notes(table, export, spec)['notes']['4']
        pressure = next(c for c in note['conditions'] if c['field'].endswith('operating_pressure'))
        self.assertEqual((pressure['operator'], pressure['value'], pressure['unit']), ('lt', '0.3', 'Mpa'))
        self.assertEqual([c['value'] for c in pressure['source_parenthetical_representations']], ['3', '44'])
        self.assertFalse(pressure['unit_conversion_performed'])
        self.assertFalse(pressure['exact_equivalence_asserted'])

    def test_condition_quotes_offsets_and_refs_resolve_to_original_source(self):
        table, export, spec = fixture()
        packet = attach_notes(table, export, spec)
        for note in packet['notes'].values():
            evidence_objects = [c['evidence'] for c in note['conditions']]
            if 'definition' in note:
                evidence_objects.append(note['definition']['evidence'])
            for item in evidence_objects:
                start, end = item['char_span']
                self.assertEqual(note['source_textline']['text'][start:end], item['quote'])
                for ref in item['word_refs']:
                    self.assertIn(export['pages'][0]['words'][int(ref.rsplit('/', 1)[1])]['id'], note['word_ids'])
        self.assertEqual(packet['notes']['5']['conditions'], [])
        self.assertIn('median', packet['notes']['5']['definition']['meaning'])

    def test_missing_value_keeps_no_words_and_has_no_fabricated_binding(self):
        table, export, spec = fixture()
        table['cells'][3][2].update(text='', words=[], word_ids=[])
        packet = attach_notes(table, export, spec)
        self.assertEqual(packet['table']['cells'][3][2]['text'], '')
        self.assertEqual(packet['table']['cells'][3][2]['note_binding_refs'], [])
        cards = review_cards(packet)
        missing = next(c for c in cards if c['id'] == 'P88-unassigned')
        self.assertEqual([(c['row'], c['col']) for c in missing['cells']], [(3, 2)])

    def test_missing_body_unknown_pattern_or_changed_source_is_rejected(self):
        for kind in ('missing', 'pattern', 'tampered-marker', 'policy'):
            with self.subTest(kind=kind):
                table, export, spec = fixture()
                if kind == 'missing':
                    export['pages'][0]['textlines'].pop()
                elif kind == 'pattern':
                    export['pages'][0]['textlines'][0]['text'] = '1 Unsupported wording'
                elif kind == 'tampered-marker':
                    table['cells'][2][1]['words'][-1]['text'] = '2'
                else:
                    spec['unit_conversion'] = 'automatic'
                with self.assertRaises(ValueError):
                    attach_notes(table, export, spec)

    def test_normal_size_digit_is_not_inferred_to_be_a_footnote(self):
        table, export, spec = fixture()
        original = table['cells'][4][1]['words'][0]
        replacement = {**copy.deepcopy(original), 'text': '1'}
        export['pages'][0]['words'][original['id']]['text'] = '1'
        table['cells'][4][1]['words'][0] = replacement
        packet = attach_notes(table, export, spec)
        self.assertEqual(len(packet['anchors']), 6)
        self.assertEqual(packet['table']['cells'][4][1]['note_refs'], [])

    def test_nine_hash_bound_pending_cards_cover_all_forty_cells(self):
        table, export, spec = fixture()
        packet = attach_notes(table, export, spec)
        packet['review_cards'] = review_cards(packet)
        cards = packet['review_cards']
        self.assertEqual(len(cards), 9)
        addresses = [(c['row'], c['col']) for card in cards for c in card['cells']]
        self.assertEqual(len(addresses), len(set(addresses)))
        self.assertEqual(len(addresses), 40)
        for card in cards:
            self.assertEqual(card['reviewable_sha256'], object_sha({k: v for k, v in card.items() if k != 'reviewable_sha256'}))
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root, prefix='.table-notes-test-') as folder:
            write_review(Path(folder), packet, {})
            review = json.loads((Path(folder)/'review.json').read_text(encoding='utf-8'))
        self.assertEqual({c['decision'] for c in review['decisions']}, {'pending'})
        self.assertTrue(all(c['original_human_message'] is None for c in review['decisions']))
        self.assertFalse(review['publication_allowed'])

    def test_existing_output_is_not_overwritten(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root, prefix='.table-notes-test-') as folder:
            sentinel = Path(folder)/'sentinel'; sentinel.write_text('keep', encoding='utf-8')
            argv = ['table_notes', '--table-run', 'missing', '--words', 'missing', '--layout', 'missing',
                    '--notes-spec', 'missing', '--source-image', 'missing', '--output', folder]
            with patch.object(sys, 'argv', argv), self.assertRaises(FileExistsError):
                main()
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep')


if __name__ == '__main__':
    unittest.main()
