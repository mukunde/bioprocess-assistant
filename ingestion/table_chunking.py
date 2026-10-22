"""Experimental row-safe XML for inspected Docling tables; no model calls.

This is structural-table-xml v1, NOT DocLang/OTSL. It is deliberately opt-in:
the production pipeline and the historical native chunker remain unchanged.
Rows connected by explicit rowspans (or reviewed candidate groups) are atomic.
The caller supplies its tokenizer; the final serialized input is budgeted.
"""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


class OversizedUnit(ValueError):
    """A complete structural unit cannot fit. Quarantine instead of truncating."""


def row_groups(table: dict, extra_groups=()) -> list[list[int]]:
    data = table['data']
    size = data['num_rows']
    if size < 2 or data['num_cols'] < 1:
        raise ValueError('A table needs a header and data rows')
    grid = data['grid']
    if len(grid) != size or any(len(row) != data['num_cols'] for row in grid):
        raise ValueError('Non-rectangular table')
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            sr, er = cell['start_row_offset_idx'], cell['end_row_offset_idx']
            sc, ec = cell['start_col_offset_idx'], cell['end_col_offset_idx']
            if not (0 <= sr <= r < er <= size and 0 <= sc <= c < ec <= data['num_cols']):
                raise ValueError('Grid position outside its cell span')
            if cell['row_span'] != er-sr or cell['col_span'] != ec-sc:
                raise ValueError('Cell span dimensions disagree')
            if grid[sr][sc] != cell:
                raise ValueError('Covered grid position differs from its anchor cell')
    if not all(c['column_header'] for c in grid[0]):
        raise ValueError('Exactly one leading header row is required')
    if any(c['column_header'] for row in grid[1:] for c in row):
        raise ValueError('Multi-row or embedded headers need a separate strategy')
    # A cut cannot cross an explicit span, including transitive overlapping spans.
    forbidden = set()
    for cell in data['table_cells']:
        start, end = cell['start_row_offset_idx'], cell['end_row_offset_idx']
        if not (0 <= start < end <= size):
            raise ValueError('Invalid row span')
        if start == 0 and end > 1:
            raise ValueError('Header/data row span is unsupported')
        forbidden.update(range(start + 1, end))
    for group in extra_groups:
        if not group or group != list(range(group[0], group[-1] + 1)) or not (1 <= group[0] <= group[-1] < size):
            raise ValueError('Candidate row groups must be contiguous data rows')
        forbidden.update(group[1:])
    groups = []
    for row in range(1, size):
        if row not in forbidden:
            groups.append([])
        groups[-1].append(row)
    return groups


def row_xml(table: dict, index: int) -> str:
    cells = []
    for col, cell in enumerate(table['data']['grid'][index]):
        if cell['start_row_offset_idx'] < index or cell['start_col_offset_idx'] < col:
            cells.append('<span/>')  # Explicit source span; never forward-filled text.
            continue
        attrs = ''
        for name, short in (('row_span', 'rows'), ('col_span', 'cols')):
            if cell[name] > 1:
                attrs += f' {short}="{cell[name]}"'
        cells.append(f'<c{attrs}>{escape(cell["text"])}</c>')
    return f'<row id="{index}">' + ''.join(cells) + '</row>'


def serialize_table(table: dict, rows: list[int], context: dict) -> str:
    """Headers/caption/notes are repeated context, never new source occurrences.

    Notes retain table-level scope; this does not infer marker-to-cell relations.
    Candidate continuation and blank-product groupings remain unapproved.
    """
    attrs = f' ref="{escape(table["self_ref"], quote=True)}"'
    if context['caption_status'] not in ('native', 'candidate-continuation'):
        raise ValueError('Invalid caption status')
    caption = escape(context.get('caption', ''))
    notes = ''.join(f'<note ref="{escape(n["ref"], quote=True)}">{escape(n["text"])}</note>'
                    for n in context.get('notes', []))
    return ('<structural-tables version="1" diagnostic="true">'
            f'<table{attrs}><caption status="{context["caption_status"]}">{caption}</caption>'
            '<header>' + row_xml(table, 0) + '</header><body>'
            + ''.join(row_xml(table, r) for r in rows)
            + '</body><notes scope="table-context-not-cell-applicability">' + notes
            + '</notes></table></structural-tables>')


def chunk_table(table: dict, context: dict, count_tokens, budget: int) -> list[dict]:
    if budget <= 0:
        raise ValueError('A positive token budget is required')
    result, pending = [], []

    def emit(rows):
        text = serialize_table(table, rows, context)
        ET.fromstring(text)
        return {'text': text, 'table_ref': table['self_ref'], 'rows': rows,
                'token_count': count_tokens(text), 'human_approved': False,
                'anchor_scope': 'exact_grid_rows_with_cell_provenance_in_document'}

    for group in row_groups(table, context.get('candidate_row_groups', [])):
        item = emit(group)
        if item['token_count'] > budget:
            raise OversizedUnit(f'{table["self_ref"]} rows {group}: '
                                f'{item["token_count"]} tokens > {budget}; no output truncation')
        if pending and count_tokens(serialize_table(table, pending + group, context)) > budget:
            result.append(emit(pending))
            pending = []
        pending += group
    if pending:
        result.append(emit(pending))
    return result


def validate_chunks(table: dict, chunks: list[dict], context: dict, count_tokens, budget: int) -> dict:
    """Independent parse/coverage check: exact cells, spans, row order and context."""
    rows = []
    for chunk in chunks:
        root = ET.fromstring(chunk['text'])
        body = root.find('./table/body')
        parsed = list(body)
        if [int(r.attrib['id']) for r in parsed] != chunk['rows']:
            raise ValueError('Row metadata differs from serialized body')
        for row in parsed:
            index = int(row.attrib['id'])
            expected = ET.fromstring(row_xml(table, index))
            if ET.tostring(row) != ET.tostring(expected):
                raise ValueError('Cell text or span changed')
            rows.append(index)
        if ET.tostring(root.find('./table/header/row')) != ET.tostring(ET.fromstring(row_xml(table, 0))):
            raise ValueError('Header changed')
        if root.findtext('./table/caption') != context.get('caption', ''):
            raise ValueError('Caption missing')
        if [n.text or '' for n in root.findall('./table/notes/note')] != [n['text'] for n in context.get('notes', [])]:
            raise ValueError('Note context missing')
        if count_tokens(chunk['text']) != chunk['token_count'] or chunk['token_count'] > budget:
            raise ValueError('Final input token budget violated')
    if rows != list(range(1, table['data']['num_rows'])):
        raise ValueError('Missing, duplicated or reordered data rows')
    for group in row_groups(table, context.get('candidate_row_groups', [])):
        if not any(set(group) <= set(c['rows']) for c in chunks):
            raise ValueError('Atomic span/group was cut')
    return {'exact_cell_text_and_spans': True, 'header_caption_notes_in_every_chunk': True,
            'ordered_rows_once': len(rows), 'atomic_groups_intact': True,
            'xml_valid': True, 'tokens_within_budget': True}
