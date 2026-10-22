"""Offline F152-01 reconstruction and opt-in row-safe K0/K800 diagnostic.

Run `python -m experiments.cytiva.repair_table152 --help` from the repo root.
All outputs must be new. Frozen conversion and source artifacts are read-only.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET

from experiments.cytiva.visual_validation import ROOT, digest, dump, fresh, network_guard
from ingestion.table_chunking import chunk_table, serialize_table, validate_chunks

PDF_SHA = 'a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a'
DOC_SHA = '9ae4ee2f1be39731d27a0b3aad854cc4ad068c27555e8c05aa51e9de70948681'
COLUMNS = [80, 310, 440, 664, 839, 1015, 1191, 1367, 1543, 1719, 1859]
# Inspected source bands, top-left PDF points. Never derive values from expected answers.
BANDS = [(847, 870), (870, 890), (890, 920)]


def extract_cells(textpage, source_chars: dict) -> tuple[list[list[dict]], list[dict]]:
    """PDF-native bounded text + independent character-index/box evidence.

    Whole glyphs must fit their rectangle; partial glyphs and missing glyph
    evidence fail closed. Only whitespace is normalized. Empty source cells stay
    empty; no product name, code, application mark or capacity is forward-filled.
    """
    if (source_chars['source_page_1based'], source_chars['coordinate_origin'],
            source_chars['width_pt'], source_chars['height_pt']) != (152, 'top_left', 1920, 1080):
        raise ValueError('Unexpected source geometry')
    rows, ledger = [], []
    for offset, (top, bottom) in enumerate(BANDS):
        row = []
        for col, (left, right) in enumerate(zip(COLUMNS, COLUMNS[1:])):
            glyphs = []
            for char in source_chars['characters']:
                l, t, r, b = char['bbox_top_left_pt']
                if left <= (l+r)/2 < right and top <= (t+b)/2 < bottom:
                    if not (left <= l <= r <= right and top <= t <= b <= bottom):
                        raise ValueError('A reconstruction boundary cuts a source glyph')
                    actual_char = textpage.get_text_range(char['index'], 1)
                    bl, bb, br, bt = textpage.get_charbox(char['index'])
                    actual_box = [bl, 1080-bt, br, 1080-bb]
                    if actual_char != char['text'] or any(abs(a-b) > 0.01 for a,b in zip(actual_box, [l,t,r,b])):
                        raise ValueError('Captured character index/box differs from the original PDF')
                    glyphs.append(char)
            raw = textpage.get_text_bounded(left, 1080-bottom, right, 1080-top)
            text = ' '.join(raw.split())
            actual = ''.join(c['text'] for c in sorted(glyphs, key=lambda c: c['index']))
            if ''.join(text.split()) != ''.join(actual.split()):
                raise ValueError('Bounded text differs from source character evidence')
            cell = {'bbox': {'l': left, 't': top, 'r': right, 'b': bottom, 'coord_origin': 'TOPLEFT'},
                    'row_span': 1, 'col_span': 1, 'start_row_offset_idx': 19+offset,
                    'end_row_offset_idx': 20+offset, 'start_col_offset_idx': col,
                    'end_col_offset_idx': col+1, 'text': text, 'column_header': False,
                    'row_header': False, 'row_section': False, 'fillable': False}
            row.append(cell)
            ledger.append({'derived_grid_row': 19+offset, 'column_index_0based': col,
                           'original_pdf_page_1based': 152, 'excerpt_page_1based': 1,
                           'bbox_top_left_pt': [left, top, right, bottom],
                           'bbox_scope': 'inspected_cell_rectangle_not_tight_glyph_box',
                           'raw_bounded_text': raw, 'text': text, 'source_blank': not text,
                           'characters': glyphs})
        rows.append(row)
    return rows, ledger


def replace_rows(document: dict, rows: list[list[dict]]) -> dict:
    if len(rows) != 3 or any(len(r) != 10 for r in rows):
        raise ValueError('Three reconstructed ten-column rows required')
    repaired = deepcopy(document)
    table = repaired['tables'][0]
    if table['data']['num_rows'] != 21 or table['data']['num_cols'] != 10:
        raise ValueError('Unexpected native table shape')
    # Preserve every original cell through row 18 and the entire second table.
    table['data']['grid'] = table['data']['grid'][:19] + deepcopy(rows)
    table['data']['table_cells'] = [c for c in table['data']['table_cells'] if c['start_row_offset_idx'] < 19]
    table['data']['table_cells'] += [deepcopy(c) for row in rows for c in row]
    table['data']['num_rows'] = 22
    return repaired


def make_context(document: dict) -> dict:
    texts = {t['self_ref']: t for t in document['texts']}
    caption = texts['#/texts/2']['text']
    def notes(*ids):
        return [{'ref': f'#/texts/{i}', 'text': texts[f'#/texts/{i}']['text']} for i in ids]
    return {'schema_version': 1, 'human_approved': False, 'diagnostic_only': True,
            'table_context': {
                '#/tables/0': {'caption': caption, 'caption_status': 'native',
                               'notes': notes(3, 4), 'candidate_row_groups': [[19, 20]],
                               'quarantined_variant_rows': [1, 9, 13],
                               'group_basis': 'Adjacent HiTrap variant bands; raw blank product cell retained. Pending human review.'},
                '#/tables/1': {'caption': caption, 'caption_status': 'candidate-continuation',
                               'notes': notes(6), 'candidate_row_groups': [],
                               'quarantined_variant_rows': [],
                               'note_basis': 'Note 3 is native body text, attached here as candidate table context; no cell applicability inferred.'}},
            'reserves': [
                'No caption is printed on page 153; continuation context is a pending annotation.',
                'Table-level notes do not establish marker-to-cell applicability.',
                'Rows 1, 9, 13 of table 0 retain aggregated same-product variants; quarantine per-variant use.',
                'The blank product cell at table 0 row 20 is not filled; candidate group [19,20] is indivisible.',
                'No scientific validation, retrieval evaluation or production deployment is implied.']}


def repair(args) -> None:
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    attempts = network_guard()
    if digest(args.pdf) != PDF_SHA or digest(args.document) != DOC_SHA:
        raise ValueError('Frozen source or conversion hash differs')
    chars = json.loads(args.characters.read_text(encoding='utf-8'))
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(args.pdf) as pdf:
        if len(pdf) != 183:
            raise ValueError('Unexpected source page count')
        page = pdf[151]
        textpage = page.get_textpage()
        try:
            rows, ledger = extract_cells(textpage, chars)
        finally:
            textpage.close()
            page.close()
    source = json.loads(args.document.read_text(encoding='utf-8'))
    document = replace_rows(source, rows)
    fresh(args.output)
    dump(args.output/'document.json', document)
    dump(args.output/'cell-provenance.json', {'source_sha256': PDF_SHA, 'cells': ledger,
         'human_approved': False, 'raw_product_blank_preserved': True})
    context = make_context(document)
    context['document_sha256'] = digest(args.output/'document.json')
    dump(args.output/'context.json', context)
    dump(args.output/'manifest.json', {'schema_version': 1, 'diagnostic_only': True,
         'human_approved': False, 'status': 'reconstructed_pending_human_review',
         'source_pdf_sha256': PDF_SHA, 'original_document_sha256': DOC_SHA,
         'source_characters_sha256': digest(args.characters), 'pdf_page_1based': 152,
         'changed_rows': {'removed_native': [19, 20], 'derived': [19, 20, 21]},
         'implementation': {str(Path(__file__).resolve().relative_to(ROOT)): digest(Path(__file__))},
         'files': {p.name: digest(p) for p in args.output.iterdir() if p.is_file()},
         'network_attempts': attempts, 'llm_calls': 0, 'api_calls': 0})


def inventory_xml(document: dict) -> str:
    # Full native text inventory retains original refs/labels including the body
    # status of note 3. Repeated table contexts are explicitly separate copies.
    items = ''.join(f'<text ref="{escape(t["self_ref"], quote=True)}" label="{escape(t["label"], quote=True)}">'
                    f'{escape(t["text"])}</text>' for t in document['texts'])
    return '<source-text-inventory>' + items + '</source-text-inventory>'


def run_chunks(args) -> None:
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    started = time.monotonic()
    attempts = network_guard()
    source = args.run/'document.json'
    context = json.loads((args.run/'context.json').read_text(encoding='utf-8'))
    manifest = json.loads((args.run/'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        if digest(args.run/name) != expected:
            raise ValueError('Derived artifact manifest hash mismatch')
    if context.get('human_approved') is not False or context.get('diagnostic_only') is not True:
        raise ValueError('Explicit diagnostic-only context required')
    if context['document_sha256'] != digest(source):
        raise ValueError('Context/document hash mismatch')
    document = json.loads(source.read_text(encoding='utf-8'))
    if args.budgets != sorted(set(args.budgets)) or not set(args.budgets) <= {600, 800, 1400}:
        raise ValueError('Use distinct sorted diagnostic budgets: 600, 800, 1400')
    # The selected two-page document contains tables and text, no pictures/lists.
    if document.get('pictures') or any(g['label'] != 'unspecified' for g in document.get('groups', [])):
        raise ValueError('This diagnostic serializer supports the inspected tables/text document only')
    import tiktoken
    encoder = tiktoken.get_encoding('cl100k_base')  # Guard forbids cache downloads.
    count = lambda text: len(encoder.encode(text))
    inventory = inventory_xml(document)
    k0 = '<structural-document version="1" diagnostic="true">' + inventory
    for i, table in enumerate(document['tables']):
        if i:
            k0 += '<page-break from-excerpt="1" to-excerpt="2"/>'
        k0 += serialize_table(table, list(range(1, table['data']['num_rows'])),
                              context['table_context'][table['self_ref']])
    k0 += '</structural-document>'
    ET.fromstring(k0)
    variants, outputs = {}, {}
    # Compute/validate EVERYTHING before creating output (oversized => no partial success).
    for budget in args.budgets:
        if count(inventory) > budget:
            raise ValueError('Source text inventory exceeds budget; requires structural subdivision')
        chunks = [{'text': inventory, 'token_count': count(inventory), 'scope': 'source-text-inventory',
                   'refs': [t['self_ref'] for t in document['texts']], 'human_approved': False}]
        checks = []
        for i, table in enumerate(document['tables']):
            ctx = context['table_context'][table['self_ref']]
            parts = chunk_table(table, ctx, count, budget)
            checks.append({'table_ref': table['self_ref'], **validate_chunks(table, parts, ctx, count, budget)})
            # Native cells/provenance remain in hash-bound document. Exact original
            # PDF page mapping is explicit, not inferred from a page-break token.
            for part in parts:
                part.update(excerpt_pages=[p['page_no'] for p in table['prov']],
                            original_pdf_pages=[151+p['page_no'] for p in table['prov']],
                            quarantined_variant_rows=sorted(set(part['rows']) & set(ctx['quarantined_variant_rows'])),
                            pending_annotations={'caption_status': ctx['caption_status'],
                                 'note_scope': 'table-context-not-cell-applicability',
                                 'candidate_row_groups': [g for g in ctx['candidate_row_groups'] if set(g) <= set(part['rows'])]},
                            document_sha256=digest(source))
            chunks += parts
        counts = [c['token_count'] for c in chunks]
        variants[f'K{budget}'] = {'chunks': len(chunks), 'tokens': counts, 'total_tokens': sum(counts),
                                  'max_tokens': max(counts), 'checks': checks,
                                  'page_boundary': 'separate table refs and explicit original/excerpt page metadata'}
        outputs[budget] = chunks
    fresh(args.output)
    (args.output/'K0.xml').write_text(k0, encoding='utf-8')
    for budget, chunks in outputs.items():
        folder = args.output/f'K{budget}'; fresh(folder)
        dump(folder/'chunks.json', chunks)
        for i, part in enumerate(chunks):
            (folder/f'chunk-{i:03}.xml').write_text(part['text'], encoding='utf-8')
    dump(args.output/'metrics.json', {'format': 'structural-table-xml-v1-not-doclang',
         'tokenizer': 'cl100k_base', 'K0_tokens': count(k0), 'variants': variants,
         'seconds_including_imports': round(time.monotonic()-started, 3),
         'network_attempts': attempts, 'llm_calls': 0, 'api_calls': 0})
    dump(args.output/'manifest.json', {'diagnostic_only': True, 'human_approved': False,
         'document_sha256': digest(source), 'context_sha256': digest(args.run/'context.json'),
         'repair_manifest_sha256': digest(args.run/'manifest.json'),
         'implementation': {str(p.relative_to(ROOT)): digest(p) for p in
             [Path(__file__).resolve(), ROOT/'ingestion/table_chunking.py']},
         'files': {str(p.relative_to(args.output)): digest(p) for p in args.output.rglob('*') if p.is_file()},
         'status': 'complete_pending_human_review'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('repair')
    for name in ('pdf', 'document', 'characters', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p = commands.add_parser('chunk')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--budgets', type=int, nargs='+', default=[800])
    args = parser.parse_args()
    {'repair': repair, 'chunk': run_chunks}[args.command](args)


if __name__ == '__main__':
    main()
