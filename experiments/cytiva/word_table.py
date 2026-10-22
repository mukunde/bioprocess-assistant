"""Bounded word-coordinate table experiment; no inference or automatic filling.

Consumes a frozen PDF-word export and an explicit page-specific layout. This is
not a general PDF table detector or an adapter into approved chatbot knowledge.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import time


def canonical_spec_sha256(value):
    """Portable JSON identity; original input byte hashes remain separate."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def inside(box, region):
    return (box['l'] >= region['l'] and box['r'] <= region['r'] and
            box['t'] >= region['t'] and box['b'] <= region['b'])


def intersects(box, region):
    return (min(box['r'], region['r']) > max(box['l'], region['l']) and
            min(box['b'], region['b']) > max(box['t'], region['t']))


def lines(words, overlap=0.5):
    """Group vertically overlapping words, preserving tokens and geometric order."""
    groups = []
    for word in sorted(words, key=lambda w: (w['bbox']['t'], w['bbox']['l'], w['id'])):
        b = word['bbox']
        candidates = []
        for i, group in enumerate(groups):
            height = min(b['b']-b['t'], group['b']-group['t'])
            common = max(0, min(b['b'], group['b'])-max(b['t'], group['t']))
            if common / height >= overlap:
                candidates.append((common / height, i))
        if candidates:
            group = groups[max(candidates)[1]]
            group['words'].append(word)
            group['t'], group['b'] = min(group['t'], b['t']), max(group['b'], b['b'])
        else:
            groups.append({'t': b['t'], 'b': b['b'], 'words': [word]})
    for group in groups:
        group['words'].sort(key=lambda w: (w['bbox']['l'], w['id']))
    return sorted(groups, key=lambda g: g['t'])


def whitespace_cut(words, anchor, axis, window, minimum):
    """Choose the nearest preceding full whitespace gap, never bisect a token."""
    start, end = ('l', 'r') if axis == 'x' else ('t', 'b')
    low = anchor-window
    intervals = sorted((max(low, w['bbox'][start]), min(anchor, w['bbox'][end]))
                       for w in words if w['bbox'][end] > low and w['bbox'][start] < anchor)
    gaps = []
    cursor = low
    for left, right in intervals:
        if left-cursor >= minimum:
            gaps.append((cursor, left))
        cursor = max(cursor, right)
    if anchor-cursor >= minimum:
        gaps.append((cursor, anchor))
    if not gaps:
        raise ValueError(f'No unambiguous {axis} separator before {anchor}')
    gap = gaps[-1]
    return {'position': sum(gap)/2, 'whitespace_interval': list(gap)}


def reconstruct(export, spec):
    source = export['source_map']
    if (source['source_sha256'] != spec['source_sha256'] or
            len(export['pages']) != 1 or len(source['pages']) != 1 or
            source['pages'][0]['original_pdf_page_1based'] != spec['original_page_1based']):
        raise ValueError('Source/page mismatch')
    page = export['pages'][0]
    if page['size'] != spec['page_size'] or spec['fill_missing_cells'] is not False:
        raise ValueError('Page geometry mismatch or automatic filling requested')
    if spec['description_rows'] != 1:
        raise ValueError('This bounded experiment requires one declared description row')
    words = []
    seen = set()
    for i, raw in enumerate(page['words']):
        b = raw['bbox']
        if (b['coord_origin'] != 'TOPLEFT' or b['r'] <= b['l'] or b['b'] <= b['t'] or
                raw['id'] in seen):
            raise ValueError('Invalid/duplicate PDF word geometry')
        seen.add(raw['id'])
        words.append({**raw, 'word_ref': f'/pages/0/words/{i}'})
    region = spec['table_bbox']
    selected = [w for w in words if inside(w['bbox'], region)]
    partial = [w for w in words if intersects(w['bbox'], region) and not inside(w['bbox'], region)]
    band = spec['header_band']
    anchors = sorted((w for w in selected if w['text'] == spec['header_anchor_text'] and
                      w['bbox']['t'] >= band['t'] and w['bbox']['b'] <= band['b']),
                     key=lambda w: w['bbox']['l'])
    if len(anchors) != spec['product_columns'] or len(lines(anchors)) != 1:
        raise ValueError('Expected aligned product-header anchors not found')
    xcuts = [whitespace_cut(selected, a['bbox']['l'], 'x', spec['column_gap_search'],
                            spec['minimum_gap']) for a in anchors]
    xs = [region['l']] + [c['position'] for c in xcuts] + [region['r']]
    if xs != sorted(set(xs)):
        raise ValueError('Overlapping or unordered column boundaries')
    label_words = [w for w in selected if w['bbox']['r'] <= xs[1]]
    label_lines = lines(label_words, spec['line_overlap_fraction'])
    if len(label_lines) != spec['labelled_rows']:
        raise ValueError('Unexpected row-label layout; manual inspection required')
    header_bottom = max(w['bbox']['b'] for w in anchors)
    description = [w for w in selected if w['bbox']['t'] > header_bottom and
                   w['bbox']['b'] < label_lines[0]['t']]
    if not description:
        raise ValueError('Declared description row is absent')
    starts = [min(w['bbox']['t'] for w in description)] + [g['t'] for g in label_lines]
    ycuts = [whitespace_cut(selected, y, 'y', spec['row_gap_search'], spec['minimum_gap'])
             for y in starts]
    ys = [region['t']] + [c['position'] for c in ycuts] + [region['b']]
    if ys != sorted(set(ys)):
        raise ValueError('Overlapping or unordered row boundaries')
    cells = [[{'row': r, 'col': c, 'words': [],
               'region': {'l': xs[c], 'r': xs[c+1], 't': ys[r], 'b': ys[r+1]}}
              for c in range(len(xs)-1)] for r in range(len(ys)-1)]
    ambiguous = []
    for word in selected:
        matches = [cell for row in cells for cell in row if inside(word['bbox'], cell['region'])]
        if len(matches) == 1:
            matches[0]['words'].append(word)
        else:
            ambiguous.append(word)
    for row in cells:
        for cell in row:
            grouped = lines(cell['words'], spec['line_overlap_fraction'])
            ordered = [w for g in grouped for w in g['words']]
            cell['lines'] = [{'text': ' '.join(w['text'] for w in g['words']),
                              'word_ids': [w['id'] for w in g['words']]} for g in grouped]
            cell['text'] = ' '.join(g['text'] for g in cell['lines'])
            cell['word_ids'] = [w['id'] for w in ordered]
            cell['words'] = ordered
            cell['status'] = 'source_words_only' if ordered else 'empty_no_source_words'
    return {'status': 'quarantined_geometry' if partial or ambiguous else 'candidate_pending_review',
            'human_approved': False, 'publication_allowed': False,
            'coordinate_origin': 'TOPLEFT', 'original_page_1based': spec['original_page_1based'],
            'serialization': 'Verbatim PDF tokens; spaces between words and lines; no value filling.',
            'layout': {'x_boundaries': xs, 'y_boundaries': ys,
                       'x_whitespace': xcuts, 'y_whitespace': ycuts,
                       'header_word_ids': [w['id'] for w in anchors]},
            'cells': cells, 'selected_word_count': len(selected),
            'ambiguous_words': ambiguous, 'table_boundary_words': partial,
            'outside_table_word_ids': [w['id'] for w in words if not intersects(w['bbox'], region)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--words', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    from experiments.cytiva.visual_validation import network_guard
    attempts = network_guard()
    started = time.perf_counter()
    payload = args.words.read_bytes()
    config = args.spec.read_bytes()
    table = reconstruct(json.loads(payload), json.loads(config))
    seconds = time.perf_counter()-started
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'table.json').write_text(json.dumps(table, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with (args.output/'table.csv').open('w', encoding='utf-8', newline='') as stream:
        csv.writer(stream).writerows([[c['text'] for c in row] for row in table['cells']])
    rows = ['<tr>'+''.join('<td>'+html.escape(c['text'])+'</td>' for c in row)+'</tr>'
            for row in table['cells']]
    (args.output/'table.html').write_text('<!doctype html><meta charset="utf-8">'
        '<title>Table 3.6: word-coordinate candidate</title>'
        '<style>body{font:14px sans-serif}td{border:1px solid #ccc;padding:8px;vertical-align:top}'
        'table{border-collapse:collapse}tr:first-child{font-weight:bold}</style>'
        '<p>Technical candidate, pending human review. No inferred or filled values.</p><table>'+
        ''.join(rows)+'</table>', encoding='utf-8')
    manifest = {'status': table['status'], 'human_approved': False, 'publication_allowed': False,
                'word_export_sha256': hashlib.sha256(payload).hexdigest(),
                'spec_sha256': hashlib.sha256(config).hexdigest(),
                'spec_canonical_sha256': canonical_spec_sha256(json.loads(config)),
                'spec_identity_policy': 'sha256_canonical_json_utf8',
                'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'reconstruction_seconds': seconds, 'llm_calls': 0, 'api_calls': 0,
                'model_inference_calls': 0, 'network_attempts': attempts}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
