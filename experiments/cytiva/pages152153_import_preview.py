"""Build a local graph preview from the verified A1.7 review packages."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from experiments.cytiva.verify_pages152153_v2_package import BASE_PACKAGE, PACKAGE, verify


PREVIEW_MANIFEST = Path(__file__).with_name('pages152153_import_preview_manifest.json')

BLOCKED = {('#/tables/0', row) for row in (1, 9, 13)}
LABELS = {
    ("#/tables/0", 1): "HiTrap Protein G HP",
    ("#/tables/0", 9): "HiTrap Protein A HP",
    ("#/tables/0", 13): "HiTrap rProtein A FF",
}
NOTE_TARGETS = {
    'n1': {('#/tables/0', 5, 0)},
    'n2': {('#/tables/0', row, 0) for row in (8, 17)},
    'n3': {('#/tables/1', row, 2) for row in (1, 2, 3, 8, 9, 10, 15, 16, 17, 20, 21, 22)},
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prepare(artifacts=None, pdf=None):
    annotated = artifacts / 'annotated-152-153-20261023-b' if artifacts is not None else None
    chunked = artifacts / 'chunks-annotated-152-153-20261023-b' if artifacts is not None else None
    replay = verify(annotated_run=annotated, chunks_run=chunked)
    manifest = read(PACKAGE / 'manifest.json')
    source = manifest['source']
    if pdf is not None:
        require(digest(pdf) == source['pdf_sha256'], 'Original PDF digest mismatch')
    evidence = read(BASE_PACKAGE / 'cards.json')['evidence']
    annotations = read(PACKAGE / 'cards.json')['annotations']
    tables = {table['ref']: table for table in evidence['tables']}
    native_tables, native_texts = {}, {}
    if annotated is not None:
        document = read(annotated / 'document.json')
        native_tables = {table['self_ref']: table for table in document['tables']}
        native_texts = {item['self_ref']: item for item in document['texts']}
    pages = {page['excerpt_page_1based']: page for page in source['source_map']['pages']}
    require([(p['original_pdf_page_1based'], p['printed_page']) for p in pages.values()]
            == [(152, '152'), (153, '153')], 'Unexpected page mapping')
    require({(ref, row) for ref, rows in annotations['quarantine'].items() for row in rows}
            == BLOCKED, 'Quarantine differs from the approved rows')

    document_id = f'pdf:{source["pdf_sha256"]}'
    table_id = f'{document_id}/A1.7'
    nodes, edges, quarantine = [], [], []

    def add(kind, key, **properties):
        nodes.append({'id': key, 'kind': kind, **properties})

    def connect(kind, start, end, **properties):
        edges.append({'kind': kind, 'from': start, 'to': end, **properties})

    def citation(excerpt_page, ref, **locator):
        return {'pdf_sha256': source['pdf_sha256'], 'document_sha256': source['document_sha256'],
                **pages[excerpt_page], 'ref': ref, **locator}

    add('Document', document_id, source=source)
    add('LogicalTable', table_id, identifier='A1.7', caption=annotations['caption'],
        approval_scope='documentary_annotations_only', row_claims_approved=False)
    connect('CONTAINS_TABLE', document_id, table_id)
    row_ids = {}
    segment_ids = {ref: f'{table_id}{ref}' for ref in tables}
    for ref, table in tables.items():
        segment = segment_ids[ref]
        provenance = table['provenance']
        if native_tables:
            require(native_tables[ref]['prov'] == provenance, f'Table locator mismatch: {ref}')
        excerpt_page = provenance[0]['page_no']
        require(len(table['headers']) == 10 and table['headers'] == tables['#/tables/0']['headers'],
                f'Header continuity mismatch: {ref}')
        table_cite = citation(excerpt_page, ref, provenance=provenance)
        add('TableSegment', segment, citation=table_cite, headers=table['headers'], spans=table['spans'])
        connect('HAS_SEGMENT', table_id, segment)
        for row, cells in enumerate(table['rows'], 1):
            locator = {**table_cite, 'grid_row_0based': row}
            require(len(cells) == len(table['headers']), f'Invalid row width: {ref} {row}')
            item = (ref, row)
            if item in BLOCKED:
                require(cells[0] == LABELS[item], f'Unexpected quarantined product: {item}')
                quarantine.append({'citation': locator, 'original_cells': cells,
                                   'reason': 'aggregate_values_unresolved_per_variant'})
                continue
            row_id = f'{segment}/row/{row}'
            row_ids[item] = row_id
            add('TableRow', row_id, citation=locator, original_cells=cells, status='documentary_context')
            connect('HAS_ROW', segment, row_id)

    continuation = annotations['continuation']
    connect('CONTINUATION_OF', segment_ids[continuation['from_table']], segment_ids[continuation['to_table']],
            review=annotations['approvals']['c1'], inherit_note_scope=False)
    group, = annotations['row_groups']
    group_table = tables[group['table_ref']]
    require([row[:3] for row in group_table['rows'][18:21]] == [
        ['HiTrap MabSelect', '1 mL', '30 mg/column'], ['', '5 mL', '150 mg/column'],
        ['HiScreen MabSelect', '4.7 mL', '140 mg/column']], 'Reviewed HiTrap/HiScreen boundary changed')
    first, second = group['rows']
    connect('GROUPED_WITH', row_ids[group['table_ref'], first], row_ids[group['table_ref'], second],
            grouping=group, review=annotations['approvals']['g1'])

    for ref, item in annotations['notes'].items():
        if native_texts:
            require(item == native_texts[ref], f'Note text/provenance mismatch: {ref}')
        anchor, = item['prov']
        require(anchor['charspan'] == [0, len(item['text'])], f'Incomplete note text anchor: {ref}')
        add('TableNote', f'{table_id}{ref}', text=item['text'],
            citation=citation(anchor['page_no'], ref, provenance=item['prov']))

    targets = {key: set() for key in NOTE_TARGETS}
    for binding in annotations['note_bindings']:
        ref, row, col = (binding[key] for key in ('table_ref', 'row', 'col'))
        approval = binding['approval']
        target = (ref, row, col)
        require(target in NOTE_TARGETS[approval] and target not in targets[approval], 'Incorrect note scope')
        targets[approval].add(target)
        cell = binding['source_cell']
        if native_tables:
            matches = [c for c in native_tables[ref]['data']['table_cells'] if c['start_row_offset_idx'] == row
                       and c['start_col_offset_idx'] == col]
            require(matches == [cell], f'Native cell evidence mismatch: {target}')
        require(cell['text'] == tables[ref]['rows'][row - 1][col], f'Cell evidence mismatch: {target}')
        excerpt_page = binding['excerpt_page_1based']
        require(tables[ref]['provenance'][0]['page_no'] == annotations['notes'][binding['note_ref']]['prov'][0]['page_no']
                == excerpt_page and pages[excerpt_page]['original_pdf_page_1based']
                == binding['original_pdf_page_1based'], f'Binding page mismatch: {target}')
        row_id = row_ids[ref, row]
        cell_id = f'{row_id}/cell/{col}'
        add('MarkedCell', cell_id, text=cell['text'], header=tables[ref]['headers'][col],
            citation=citation(excerpt_page, ref, grid_row_0based=row, column_0based=col, source_cell=cell))
        connect('HAS_MARKED_CELL', row_id, cell_id)
        connect('CITES_NOTE', cell_id, f'{table_id}{binding["note_ref"]}', binding_id=binding['id'],
                review=annotations['approvals'][approval])

    require(targets == NOTE_TARGETS, 'Incomplete approved note scope')
    node_ids = {node['id'] for node in nodes}
    require(len(node_ids) == len(nodes), 'Duplicate staged node')
    require(len({(e['kind'], e['from'], e['to']) for e in edges}) == len(edges), 'Duplicate staged relationship')
    require(all(edge['from'] in node_ids and edge['to'] in node_ids for edge in edges), 'Dangling relationship')
    require(len(row_ids) == 40 and not (row_ids.keys() & BLOCKED) and len(quarantine) == 3,
            'Primary and quarantine partitions are wrong')
    return {
        'import_preview.json': {
            'mode': 'offline_preview', 'publication_allowed': False, 'production_ready': False,
            'source_package_canonical_sha256': manifest['canonical_payload'],
            'nodes': nodes, 'relationships': edges,
        },
        'quarantine.json': {'publication_allowed': False, 'graph_eligible': False, 'rows': quarantine},
        'verification.json': {
            'source_review_replay': replay, 'original_pdf_sha256_verified': pdf is not None,
            'node_counts': dict(Counter(n['kind'] for n in nodes)),
            'relationship_counts': dict(Counter(e['kind'] for e in edges)),
            'note_counts': {key: len(rows) for key, rows in targets.items()},
            'quarantined_rows': len(quarantine), 'neo4j_connections': 0,
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, help='Optional historical visual-validation-v01 directory')
    parser.add_argument('--pdf', type=Path, help='Optional original handbook to check by SHA-256')
    parser.add_argument('--output', type=Path, required=True, help='New directory for the local preview')
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(args.output)
    outputs = prepare(args.artifacts, args.pdf)
    serialized = {name: (json.dumps(content, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
                  for name, content in outputs.items()}
    reference = read(PREVIEW_MANIFEST)
    require(outputs['import_preview.json']['source_package_canonical_sha256'] == reference['source_package_canonical_sha256'],
            'Preview source package changed')
    output_hashes = {name: hashlib.sha256(serialized[name]).hexdigest()
                     for name in ('import_preview.json', 'quarantine.json')}
    require(output_hashes == reference['output_sha256_utf8_lf'], 'Preview or quarantine differs from the recorded run')
    args.output.mkdir(parents=True, exist_ok=False)
    for name, content in serialized.items():
        (args.output / name).write_bytes(content)
    print(json.dumps(outputs['verification.json'], ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
