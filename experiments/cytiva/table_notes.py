"""Bind page-88 table footnotes and prepare pending human review; no inference."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import html
import json
from pathlib import Path
import re
from statistics import median

from experiments.cytiva.word_table import canonical_spec_sha256, inside, reconstruct


def sha(data):
    return hashlib.sha256(data).hexdigest()


def object_sha(value):
    return canonical_spec_sha256(value)


def validate_input_hashes(payloads, parsed):
    """Use canonical identities for new specs; legacy inputs stay byte-strict."""
    parent, notes = parsed['parent_manifest'], parsed['notes_spec']
    layout_identity = canonical_spec_sha256(parsed['layout'])
    if parent['word_export_sha256'] != sha(payloads['words']):
        raise ValueError('Frozen input hash mismatch: word export')
    if 'spec_canonical_sha256' in parent:
        if (parent.get('spec_identity_policy') != 'sha256_canonical_json_utf8' or
                parent['spec_canonical_sha256'] != layout_identity):
            raise ValueError('Frozen input hash mismatch: parent layout identity')
    elif parent['spec_sha256'] != sha(payloads['layout']):
        raise ValueError('Frozen input hash mismatch: legacy parent layout bytes')
    if 'layout_canonical_sha256' in notes:
        if notes['layout_canonical_sha256'] != layout_identity:
            raise ValueError('Frozen input hash mismatch: notes layout identity')
    elif notes['layout_sha256'] != sha(payloads['layout']):
        raise ValueError('Frozen input hash mismatch: legacy notes layout bytes')
    return {'policy': 'sha256_canonical_json_utf8', 'layout': layout_identity,
            'notes_spec': canonical_spec_sha256(notes)}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def evidence(note, phrase):
    """Exact offsets in the immutable source textline, with original word refs."""
    text = note['source_textline']['text']
    matches = list(re.finditer(re.escape(phrase), text))
    if len(matches) != 1:
        raise ValueError(f'Ambiguous or absent condition evidence: {phrase}')
    start, end = matches[0].span()
    cursor = 0
    refs = []
    for word in note['words']:
        stop = cursor+len(word['text'])
        if cursor < end and stop > start:
            refs.append(word['word_ref'])
        cursor = stop+1
    return {'quote': text[start:end], 'char_span': [start, end],
            'textline_ref': note['textline_ref'], 'word_refs': refs}


def structure_note(note):
    """Strict source patterns; preserve lexical quantities, roles and operators."""
    text = note['source_textline']['text']
    number = r'\d+(?:\.\d+)?'
    if note['id'] in ('1', '2', '3'):
        pattern = (rf'{note["id"]} Determined at (?P<breakthrough>{number})% breakthrough '
                   rf'by frontal analysis at a mobile phase velocity of (?P<velocity>{number}) '
                   rf'cm/h at a (?P<height>{number}) cm bed height '
                   rf'\(residence time: (?P<residence>{number}) min\)\.')
        match = re.fullmatch(pattern, text)
        if not match:
            raise ValueError('Unrecognized capacity-measurement note; quarantine required')
        conditions = []
        for field, value, unit, phrase in (
                ('breakthrough', match['breakthrough'], '%', match['breakthrough']+'% breakthrough'),
                ('method', 'frontal analysis', None, 'frontal analysis'),
                ('mobile_phase_velocity', match['velocity'], 'cm/h', match['velocity']+' cm/h'),
                ('bed_height', match['height'], 'cm', match['height']+' cm bed height'),
                ('residence_time', match['residence'], 'min', match['residence']+' min')):
            conditions.append({'field': 'capacity_measurement.'+field, 'operator': 'reported_at',
                               'value': value, 'unit': unit, 'evidence': evidence(note, phrase)})
        return {'role': 'capacity_measurement_context', 'expected_anchor': 'value_cell',
                'row_label': 'Dynamic binding capacity', 'conditions': conditions,
                'limit': 'Measurement context for the cited capacity, not the recommended operating velocity or a universal operating limit.'}
    if note['id'] == '4':
        pattern = (rf'4 In (?P<column>AxiChrom {number} column), (?P<height>{number}) cm '
                   rf'bed height operating at (?P<pressure>< (?P<value>{number}) '
                   rf'(?P<unit>Mpa|MPa)) \((?P<bar>{number}) bar, (?P<psi>{number}) psi\), '
                   rf'(?P<temperature>{number})°C\.')
        match = re.fullmatch(pattern, text)
        if not match:
            raise ValueError('Unrecognized operating-context note; quarantine required')
        conditions = [
            {'field': 'recommended_velocity_context.column', 'operator': 'reported_in',
             'value': match['column'], 'unit': None, 'evidence': evidence(note, match['column'])},
            {'field': 'recommended_velocity_context.bed_height', 'operator': 'reported_at',
             'value': match['height'], 'unit': 'cm', 'evidence': evidence(note, match['height']+' cm bed height')},
            {'field': 'recommended_velocity_context.operating_pressure', 'operator': 'lt',
             'value': match['value'], 'unit': match['unit'], 'unit_normalization': 'not_applied',
             'evidence': evidence(note, match['pressure']),
             'source_parenthetical_representations': [
                 {'value': match['bar'], 'unit': 'bar', 'evidence': evidence(note, match['bar']+' bar')},
                 {'value': match['psi'], 'unit': 'psi', 'evidence': evidence(note, match['psi']+' psi')}],
             'unit_conversion_performed': False, 'exact_equivalence_asserted': False},
            {'field': 'recommended_velocity_context.temperature', 'operator': 'reported_at',
             'value': match['temperature'], 'unit': '°C',
             'evidence': evidence(note, match['temperature']+'°C')}]
        return {'role': 'recommended_velocity_context', 'expected_anchor': 'row_label',
                'row_label': 'Recommended operating mobile velocity', 'conditions': conditions,
                'limit': 'Context of the cited recommended velocities. Preserve the printed pressure and parenthetical units without deriving exact conversions or a universal equipment limit.'}
    if note['id'] == '5':
        pattern = r'5 (?P<symbol>d 50v) is the (?P<meaning>median particle size of the cumulative volume distribution)\.'
        match = re.fullmatch(pattern, text)
        if not match:
            raise ValueError('Unrecognized particle-size definition; quarantine required')
        return {'role': 'particle_size_definition', 'expected_anchor': 'row_label',
                'row_label': 'Particle size', 'conditions': [],
                'definition': {'source_symbol': match['symbol'], 'meaning': match['meaning'],
                               'evidence': evidence(note, match['meaning'])},
                'limit': 'Definition of the reported particle-size metric, not a mean, a threshold, or an operating instruction.'}
    raise ValueError('Unknown note')


def extract_notes(export, spec):
    page = export['pages'][0]
    word_map = {w['id']: {**w, 'word_ref': f'/pages/0/words/{i}'}
                for i, w in enumerate(page['words'])}
    if len(word_map) != len(page['words']):
        raise ValueError('Duplicate source word IDs')
    notes = {}
    for i, line in enumerate(page['textlines']):
        if not inside(line['bbox'], spec['notes_bbox']):
            continue
        marker = line['text'].split(' ', 1)[0]
        if marker not in spec['expected_marker_counts'] or marker in notes:
            raise ValueError('Unknown, duplicated or multiline note in the declared region')
        words = sorted((w for w in word_map.values() if inside(w['bbox'], line['bbox'])),
                       key=lambda w: (w['bbox']['l'], w['id']))
        if ' '.join(w['text'] for w in words) != line['text']:
            raise ValueError('Note word/textline mismatch')
        note = {'id': marker, 'source_textline': copy.deepcopy(line),
                'textline_ref': f'/pages/0/textlines/{i}', 'words': words,
                'word_ids': [w['id'] for w in words]}
        note.update(structure_note(note))
        notes[marker] = note
    if set(notes) != set(spec['expected_marker_counts']):
        raise ValueError('Missing footnote; never fabricate its body')
    footer_ids = {w['id'] for w in word_map.values() if inside(w['bbox'], spec['notes_bbox'])}
    assigned = [wid for n in notes.values() for wid in n['word_ids']]
    if set(assigned) != footer_ids or len(assigned) != len(set(assigned)):
        raise ValueError('Unresolved or reused footnote words')
    return notes


def attach_notes(table, export, spec):
    if (export['source_map']['source_sha256'] != spec['source_sha256'] or
            table['original_page_1based'] != spec['original_page_1based'] or
            spec['automatic_approval'] is not False or
            spec['quantity_normalization'] != 'none' or spec['unit_conversion'] != 'none' or
            spec['row_label_scope'] != 'same_row_nonempty_product_cells'):
        raise ValueError('Source/page/policy mismatch')
    if table['status'] != 'candidate_pending_review' or table['human_approved'] is not False:
        raise ValueError('Expected an unapproved, geometrically resolved candidate')
    for row in table['cells']:
        for cell in row:
            for word in cell['words']:
                match = re.fullmatch(r'/pages/0/words/(\d+)', word['word_ref'])
                if match is None or int(match[1]) >= len(export['pages'][0]['words']):
                    raise ValueError('Unresolved table-word reference')
                original = export['pages'][0]['words'][int(match[1])]
                if any(word[k] != original[k] for k in ('id', 'text', 'bbox')):
                    raise ValueError('Table word no longer matches its frozen source')
    notes = extract_notes(export, spec)
    linked = copy.deepcopy(table)
    anchors, bindings = [], []
    for row in linked['cells']:
        for cell in row:
            cell['note_refs'], cell['note_binding_refs'], cell['marker_word_ids'] = [], [], []
    for row in linked['cells']:
        for cell in row:
            body = [w for w in cell['words'] if not w['text'].isdigit()]
            if not body:
                continue
            height = median(w['bbox']['b']-w['bbox']['t'] for w in body)
            bottom = median(w['bbox']['b'] for w in body)
            for word in cell['words']:
                b = word['bbox']
                if not (word['text'].isdigit() and b['b']-b['t'] <= height*spec['superscript_height_ratio_max']
                        and b['b'] <= bottom-height*spec['superscript_bottom_raise_ratio_min']):
                    continue
                note_id = word['text']
                if note_id not in notes:
                    raise ValueError('Unknown superscript; never infer its note')
                note = notes[note_id]
                kind = 'row_label' if cell['col'] == 0 else 'value_cell'
                if kind != note['expected_anchor']:
                    raise ValueError('Footnote marker in an unexpected cell role')
                label_words = row[0]['words']
                label = ' '.join(w['text'] for w in label_words if not w['text'].isdigit())
                if label != note['row_label']:
                    raise ValueError('Footnote marker attached to the wrong property')
                anchor = {'id': f'N{note_id}-anchor-r{cell["row"]}c{cell["col"]}',
                          'note_id': note_id, 'kind': kind,
                          'cell': [cell['row'], cell['col']], 'marker': copy.deepcopy(word)}
                anchors.append(anchor)
                cell['marker_word_ids'].append(word['id'])
                if note_id not in cell['note_refs']:
                    cell['note_refs'].append(note_id)
                targets = [c for c in row[1:] if c['words']] if kind == 'row_label' else [cell]
                for target in targets:
                    binding = {'id': f'N{note_id}-r{target["row"]}c{target["col"]}',
                               'note_id': note_id, 'anchor_id': anchor['id'],
                               'cell': [target['row'], target['col']],
                               'kind': 'shared_row_context' if kind == 'row_label' else 'direct_cell_reference',
                               'human_approved': False}
                    bindings.append(binding)
                    if note_id not in target['note_refs']:
                        target['note_refs'].append(note_id)
                    target['note_binding_refs'].append(binding['id'])
    if dict(Counter(a['note_id'] for a in anchors)) != spec['expected_marker_counts']:
        raise ValueError('Missing or duplicated printed markers')
    if len({b['id'] for b in bindings}) != len(bindings):
        raise ValueError('Duplicated bindings')
    return {'schema_version': 1, 'status': 'pending_human_review', 'human_approved': False,
            'publication_allowed': False, 'source_map': copy.deepcopy(export['source_map']),
            'table': linked, 'notes': notes, 'anchors': anchors, 'bindings': bindings}


def review_cards(packet):
    cells = packet['table']['cells']
    addresses = [(r, c) for r in range(len(cells)) for c in range(len(cells[r]))]
    groups = [('P88-layout', 'Headers, descriptions, labels and table geometry',
               [(r, c) for r, c in addresses if r < 2 or c == 0], [])]
    for note_id in sorted(packet['notes']):
        targets = [tuple(b['cell']) for b in packet['bindings'] if b['note_id'] == note_id]
        groups.append(('P88-N'+note_id, 'Note '+note_id+' and its product cells', targets, [note_id]))
    for r, title in ((4, 'CIP reagents'), (5, 'Ligands'), (7, 'Available formats')):
        groups.append((f'P88-row-{r}', title, [(r, c) for c in range(1, len(cells[r]))], []))
    covered = [a for _, _, targets, _ in groups for a in targets]
    missing = sorted(set(addresses)-set(covered))
    if missing:
        groups.append(('P88-unassigned', 'Cells without a resolved note binding', missing, []))
        covered.extend(missing)
    if len(covered) != len(set(covered)) or set(covered) != set(addresses):
        raise ValueError('Review cards must cover every cell exactly once')
    cards = []
    for cid, title, targets, note_ids in groups:
        card = {'id': cid, 'title': title, 'cells': [cells[r][c] for r, c in targets],
                'notes': [packet['notes'][n] for n in note_ids],
                'bindings': [b for b in packet['bindings'] if b['note_id'] in note_ids]}
        cards.append({**card, 'reviewable_sha256': object_sha(card)})
    return cards


def cell_html(cell):
    markers = set(cell['marker_word_ids'])
    rendered = []
    for word in cell['words']:
        value = html.escape(word['text'])
        if word['id'] in markers:
            value = f'<a href="#note-{value}"><sup>{value}</sup></a>'
        rendered.append(value)
    return ' '.join(rendered)


def write_review(output, packet, manifest):
    cards = packet['review_cards']
    decisions = {'packet_sha256': object_sha(packet), 'human_approved': False,
                 'publication_allowed': False,
                 'decisions': [{'card_id': c['id'], 'reviewable_sha256': c['reviewable_sha256'],
                                'decision': 'pending', 'reviewer': None,
                                'decided_at_utc': None, 'original_human_message': None,
                                'reservations': []} for c in cards]}
    dump(output/'review.json', decisions)
    md = ['# Human review: Cytiva page 88', '',
          f'**All {len(cards)} decisions are pending. No approval or publication is inferred.**', '',
          '[Original page rendering](original-page-088.png) · [Linked table and notes](review.html)', '',
          'Compare each card against the original rendered page. Reply with its ID, decision and any reservation. Original human wording must be preserved.', '',
          'Decisions: validated, validated_with_reservation, rejected, needs_clarification. Technical preparation never changes a pending decision.', '',
          'Row/column indices below are zero-based. A printed row-label marker is propagated to product cells explicitly, without filling values.', '']
    rows = ['<tr>'+''.join('<td>'+cell_html(c)+'</td>' for c in row)+'</tr>' for row in packet['table']['cells']]
    sections = []
    for card in cards:
        md.extend([f'## {card["id"]}: {card["title"]}', '', '**Decision: pending**', '',
                   '| Cell | Product / context | Source text | Notes |', '|---|---|---|---|'])
        targets = []
        for cell in card['cells']:
            product = packet['table']['cells'][0][cell['col']]['text'] if cell['col'] else 'Row label'
            md.append(f'| r{cell["row"]}c{cell["col"]} | {product} | {cell["text"] or "(empty in source)"} | {", ".join(cell["note_refs"]) or "—"} |')
            targets.append('<li>'+html.escape(f'r{cell["row"]}c{cell["col"]} — {product}: {cell["text"] or "(empty in source)"}')+'</li>')
        paragraphs = []
        for note in card['notes']:
            md.extend(['', '> '+note['source_textline']['text'], '',
                       'Role: `'+note['role']+'`. '+note['limit'], ''])
            if note['conditions']:
                md += ['| Context field | Operator | Source value/unit |', '|---|---|---|']
                for condition in note['conditions']:
                    md.append(f'| {condition["field"]} | {condition["operator"]} | {condition["value"]} {condition["unit"] or ""} |')
            md.extend(['', f'Source: original PDF p.88; `{note["textline_ref"]}`; word IDs {note["word_ids"][0]}–{note["word_ids"][-1]}.', ''])
            paragraphs.append(f'<section id="note-{note["id"]}"><h3>Note {note["id"]}</h3><blockquote>'+
                              html.escape(note['source_textline']['text'])+'</blockquote><p>'+
                              html.escape(note['limit'])+'</p><pre>'+html.escape(json.dumps(note['conditions'],ensure_ascii=False,indent=2))+'</pre></section>')
        md.extend(['', 'Verify text, quantity/unit, scope, every reference and any interpretation limit. No scientific or operational authorization is implied.', '',
                   'Reviewable SHA-256: `'+card['reviewable_sha256']+'`.', ''])
        sections.append('<article><h2>'+html.escape(card['id']+' — '+card['title'])+'</h2><p>Decision: pending</p><ul>'+''.join(targets)+'</ul>'+''.join(paragraphs)+'</article>')
    (output/'human-review.md').write_text('\n'.join(md), encoding='utf-8')
    page = ('<!doctype html><meta charset="utf-8"><title>Cytiva page 88: pending human review</title>'
            '<style>body{font:16px system-ui;margin:24px;color:#172033}td{border:1px solid #cbd5e1;padding:8px;vertical-align:top}'
            'table{border-collapse:collapse;width:100%}pre{white-space:pre-wrap}article{border-top:2px solid #cbd5e1;margin-top:24px}'
            'blockquote{background:#f1f5f9;padding:12px}sup{color:#b91c1c}img{max-width:100%}</style>'
            '<h1>Cytiva page 88 — review pending</h1><p>Read-only preparation. No decision is recorded by this page; reply with card IDs in the review conversation.</p>'
            '<details><summary>Original PDF page 88 (local Poppler rendering)</summary>'
            '<img src="original-page-088.png" alt="Original Cytiva manual page 88, including table 3.6 and five footnotes"></details>'
            '<p>All source words, including markers, are retained. Superscript links show note anchors.</p>'
            '<table>'+''.join(rows)+'</table>'+''.join(sections))
    (output/'review.html').write_text(page, encoding='utf-8')
    manifest['review_cards'] = len(cards)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table-run', type=Path, required=True)
    parser.add_argument('--words', type=Path, required=True)
    parser.add_argument('--layout', type=Path, required=True)
    parser.add_argument('--notes-spec', type=Path, required=True)
    parser.add_argument('--source-image', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    from experiments.cytiva.visual_validation import network_guard
    attempts = network_guard()
    payloads = {name: path.read_bytes() for name, path in
                [('words', args.words), ('layout', args.layout), ('notes_spec', args.notes_spec),
                 ('parent_table', args.table_run/'table.json'), ('parent_manifest', args.table_run/'manifest.json')]}
    parsed = {k: json.loads(v) for k, v in payloads.items()}
    specification_identities = validate_input_hashes(payloads, parsed)
    if parsed['parent_table'] != reconstruct(parsed['words'], parsed['layout']):
        raise ValueError('Parent table no longer matches the source words/layout')
    packet = attach_notes(parsed['parent_table'], parsed['words'], parsed['notes_spec'])
    packet['specification_identities'] = specification_identities
    packet['source_hashes'] = {k: sha(v) for k, v in payloads.items()}
    source_image = args.source_image.read_bytes()
    if not source_image.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Expected a local PNG page rendering')
    packet['source_hashes']['source_image'] = sha(source_image)
    packet['review_cards'] = review_cards(packet)
    args.output.mkdir(parents=True, exist_ok=False)
    dump(args.output/'packet.json', packet)
    (args.output/'original-page-088.png').write_bytes(source_image)
    manifest = {'status': 'pending_human_review', 'human_approved': False, 'publication_allowed': False,
                'source_hashes': packet['source_hashes'], 'notes': len(packet['notes']),
                'printed_anchors': len(packet['anchors']), 'product_cell_bindings': len(packet['bindings']),
                'llm_calls': 0, 'api_calls': 0, 'model_inference_calls': 0, 'network_attempts': attempts,
                'implementation_sha256': sha(Path(__file__).read_bytes())}
    write_review(args.output, packet, manifest)
    manifest['files'] = {p.name: sha(p.read_bytes()) for p in args.output.iterdir() if p.is_file()}
    dump(args.output/'manifest.json', manifest)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'files'}))


if __name__ == '__main__':
    main()
