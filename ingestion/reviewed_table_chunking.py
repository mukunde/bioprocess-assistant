"""Opt-in structural XML v2: scoped reviewed annotations and isolated quarantine.

The original v1 serializer is unchanged. Approval applies to documentary
annotations only, never every table value or downstream scientific use.
"""
from html import escape
import xml.etree.ElementTree as ET

from ingestion.table_chunking import OversizedUnit, row_groups, row_xml


def selected_annotations(table, rows, annotations):
    ref = table['self_ref']; chosen = set(rows)
    bindings = [b for b in annotations['note_bindings'] if b['table_ref'] == ref and b['row'] in chosen]
    groups = []
    for group in annotations['row_groups']:
        if group['table_ref'] == ref and chosen.intersection(group['rows']):
            if not set(group['rows']) <= chosen:
                raise ValueError('Reviewed group split across fragments')
            groups.append(group)
    continuation = annotations['continuation'] if annotations['continuation']['from_table'] == ref else None
    approvals = sorted({b['approval'] for b in bindings} | {g['approval'] for g in groups}
                       | ({continuation['approval']} if continuation else set()))
    return bindings, groups, continuation, approvals


def partitions(table, annotations):
    """Any quarantine inside an atomic group quarantines the entire group."""
    ref = table['self_ref']
    groups = [g['rows'] for g in annotations['row_groups'] if g['table_ref'] == ref]
    atomic = row_groups(table, groups)
    blocked = set(annotations['quarantine'][ref])
    if not blocked <= set(range(1, table['data']['num_rows'])):
        raise ValueError('Unknown quarantined row')
    return {False: [g for g in atomic if not blocked.intersection(g)],
            True: [g for g in atomic if blocked.intersection(g)]}


def serialize_reviewed(table, rows, annotations, quarantined=False):
    bindings, groups, continuation, approvals = selected_annotations(table, rows, annotations)
    flag = str(quarantined).lower(); ref = escape(table['self_ref'], quote=True)
    table_page = table['prov'][0]['page_no']
    caption_status = 'reviewed-continuation' if continuation else 'native'
    text = (f'<reviewed-tables version="2" diagnostic="true" quarantined="{flag}">'
            f'<table ref="{ref}" original-page="{151+table_page}" logical-table="A1.7">'
            f'<caption status="{caption_status}">{escape(annotations["caption"])}</caption>')
    if continuation:
        text += (f'<continuation of="{escape(continuation["to_table"], quote=True)}" '
                 f'approval="{continuation["approval"]}"/>')
    text += '<header>' + row_xml(table, 0) + '</header><body>'
    text += ''.join(row_xml(table, r) for r in rows) + '</body><annotations>'
    for group in groups:
        text += f'<row-group rows="{" ".join(map(str,group["rows"]))}" approval="{group["approval"]}"/>'
    for b in bindings:
        text += (f'<note-link id="{b["id"]}" row="{b["row"]}" col="{b["col"]}" '
                 f'note="{b["note_ref"]}" approval="{b["approval"]}"/>')
    text += '</annotations><notes scope="explicit-cell-links-only">'
    for ref in sorted({b['note_ref'] for b in bindings}):
        text += f'<note ref="{ref}">{escape(annotations["notes"][ref]["text"])}</note>'
    text += '</notes><limits>'
    for approval in approvals:
        text += f'<limit approval="{approval}">{escape(annotations["approvals"][approval]["serialization_limit"])}</limit>'
    text += '</limits></table></reviewed-tables>'
    return text


def chunk_reviewed(table, annotations, count_tokens, budget, quarantined=False):
    if budget <= 0:
        raise ValueError('A positive budget is required')
    groups = partitions(table, annotations)[quarantined]
    chunks = []; pending = []

    def emit(rows):
        text = serialize_reviewed(table, rows, annotations, quarantined)
        bindings, _, _, approvals = selected_annotations(table, rows, annotations)
        return {'text': text, 'token_count': count_tokens(text), 'table_ref': table['self_ref'],
                'rows': rows, 'quarantined': quarantined, 'role': 'quarantine' if quarantined else 'table-candidate',
                'annotation_ids': [b['id'] for b in bindings], 'approval_ids': approvals,
                'approval_scope': 'documentary_annotations_only', 'production_ready': False,
                'original_pdf_pages': [151+p['page_no'] for p in table['prov']],
                'excerpt_pages': [p['page_no'] for p in table['prov']]}

    for group in groups:
        unit = emit(group)
        if unit['token_count'] > budget:
            raise OversizedUnit(f'{table["self_ref"]} rows {group} with annotations exceed {budget}; no truncation')
        if pending and count_tokens(serialize_reviewed(table, pending+group, annotations, quarantined)) > budget:
            chunks.append(emit(pending)); pending = []
        pending += group
    if pending:
        chunks.append(emit(pending))
    return chunks


def validate_reviewed(table, chunks, annotations, count_tokens, budget, quarantined=False):
    expected_groups = partitions(table, annotations)[quarantined]
    coverage = []; ids = []
    for chunk in chunks:
        root = ET.fromstring(chunk['text']); node = root.find('table')
        if root.tag != 'reviewed-tables' or root.attrib != {'version':'2','diagnostic':'true','quarantined':str(quarantined).lower()}:
            raise ValueError('Quarantine/format attributes changed')
        if (chunk['quarantined'] is not quarantined or chunk['production_ready'] is not False
                or chunk['approval_scope'] != 'documentary_annotations_only'
                or chunk['role'] != ('quarantine' if quarantined else 'table-candidate')):
            raise ValueError('Chunk approval/quarantine scope changed')
        if (chunk['original_pdf_pages'] != [151+p['page_no'] for p in table['prov']]
                or chunk['excerpt_pages'] != [p['page_no'] for p in table['prov']]):
            raise ValueError('Chunk provenance metadata changed')
        if count_tokens(chunk['text']) != chunk['token_count'] or chunk['token_count'] > budget:
            raise ValueError('Final serialized budget violated')
        if node.attrib != {'ref':table['self_ref'],'original-page':str(151+table['prov'][0]['page_no']),'logical-table':'A1.7'}:
            raise ValueError('Table source mapping changed')
        parsed = node.findall('./header/row') + node.findall('./body/row')
        row_ids = [int(r.attrib['id']) for r in parsed]
        if row_ids != [0]+chunk['rows']:
            raise ValueError('Header/body row coverage changed')
        anchors = {}
        for row_id, row in zip(row_ids, parsed):
            grid_row = table['data']['grid'][row_id]
            if len(row) != len(grid_row):
                raise ValueError('Column count changed')
            for col, (xml, source) in enumerate(zip(row, grid_row)):
                anchor = source['start_row_offset_idx'], source['start_col_offset_idx']
                if anchor != (row_id,col):
                    if xml.tag != 'span' or xml.attrib or xml.text or anchors.get(anchor) != source['text']:
                        raise ValueError('Missing same-fragment span anchor')
                else:
                    attrs = {k:str(source[k+'_span']) for k in ('row','col') if source[k+'_span']>1}
                    attrs = {('rows' if k=='row' else 'cols'):v for k,v in attrs.items()}
                    if xml.tag != 'c' or xml.attrib != attrs or (xml.text or '') != source['text']:
                        raise ValueError('Source cell text/unit/blank changed')
                    anchors[anchor] = source['text']
        bindings, groups, continuation, approvals = selected_annotations(table, chunk['rows'], annotations)
        expected_links = [{'id':b['id'],'row':str(b['row']),'col':str(b['col']),
                           'note':b['note_ref'],'approval':b['approval']} for b in bindings]
        if [n.attrib for n in node.findall('./annotations/note-link')] != expected_links:
            raise ValueError('Explicit note binding changed')
        if [g.attrib for g in node.findall('./annotations/row-group')] != [
                {'rows':' '.join(map(str,g['rows'])),'approval':g['approval']} for g in groups]:
            raise ValueError('Reviewed row grouping changed')
        expected_cont = [] if not continuation else [{'of':continuation['to_table'],'approval':continuation['approval']}]
        if [c.attrib for c in node.findall('continuation')] != expected_cont:
            raise ValueError('Reviewed continuation changed')
        if node.findtext('caption') != annotations['caption'] or node.find('caption').get('status') != (
                'reviewed-continuation' if continuation else 'native'):
            raise ValueError('Caption status changed')
        expected_notes = [(ref,annotations['notes'][ref]['text']) for ref in sorted({b['note_ref'] for b in bindings})]
        if node.find('notes').get('scope') != 'explicit-cell-links-only' or [
                (n.get('ref'),n.text) for n in node.findall('./notes/note')] != expected_notes:
            raise ValueError('Unscoped or missing note body')
        if [(n.get('approval'),n.text) for n in node.findall('./limits/limit')] != [
                (a,annotations['approvals'][a]['serialization_limit']) for a in approvals]:
            raise ValueError('Serialized limitation changed')
        if chunk['annotation_ids'] != [b['id'] for b in bindings] or chunk['approval_ids'] != approvals:
            raise ValueError('Annotation metadata differs from XML')
        coverage += chunk['rows']; ids += chunk['annotation_ids']
    expected_rows = [r for group in expected_groups for r in group]
    if coverage != expected_rows:
        raise ValueError('Missing, duplicated or mixed quarantine rows')
    for group in expected_groups:
        if not any(set(group)<=set(c['rows']) for c in chunks):
            raise ValueError('Atomic group was cut')
    return {'rows':len(coverage),'grid_positions':len(coverage)*table['data']['num_cols'],
            'note_bindings':len(ids),'xml_valid':True,'source_cells_unchanged':True,
            'atomic_groups_intact':True,'notes_explicitly_scoped':True,'tokens_within_budget':True}
