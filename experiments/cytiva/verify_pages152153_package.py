"""Offline compact documentary-review verifier; Python standard library only."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent/'reviewed-pages-152-153'
ORDER = ['P152-HiTrap-HiScreen', 'P152-153-continuity', 'P152-N1',
         'P152-N2', 'P153-N3', 'P152-153-chunking']
FILES = {'README.md', 'cards.json', 'events.json', 'review.json'}
SUPPORT = {'docs/experiments/cytiva-table-152-153-'+name for name in
           ['protocol.md', 'results.md', 'results.csv', 'review.csv', 'repair.md', 'human-review.md']}
SUPPORT |= {'experiments/cytiva/pages152153_table_spec.json', 'experiments/cytiva/repair_table152.py',
            'ingestion/table_chunking.py', 'tests/test_table_chunking.py'}
PDF_SHA = 'a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a'
DOCUMENT_SHA = '5fefd6c8712202b1352e0521791dc73ed06ee2acb8e7f6aa9b9bf85cd1f47bb9'
NATIVE_SHA = '9ae4ee2f1be39731d27a0b3aad854cc4ad068c27555e8c05aa51e9de70948681'
TOKENS = [212, 782, 794, 547, 659, 661, 720]
COUNTS = {'cards': 6, 'validated_with_reservation': 6, 'pending': 0, 'note_cell_bindings': 15,
          'reconstructed_cells': 30, 'reconstructed_blanks': 13, 'source_glyphs': 108,
          'data_rows': 43, 'grid_positions': 430, 'chunks': 7, 'K0_tokens': 3579,
          'K800_total_tokens': 4375, 'K800_max_tokens': 794}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def local_digest(value):
    # Historical Windows write_text/open('w'): preserve original JSON key order.
    text = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').replace('\n', '\r\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def table_record(table):
    """Selected table-only evidence; no page images, full document or raw grids."""
    grid = table['data']['grid']
    spans = []
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if (cell['row_span'] > 1 or cell['col_span'] > 1) and (
                    cell['start_row_offset_idx'], cell['start_col_offset_idx']) == (r, c):
                spans.append({'row': r, 'col': c, 'rows': cell['row_span'], 'cols': cell['col_span']})
    return {'ref': table['self_ref'], 'provenance': table['prov'],
            'headers': [c['text'] for c in grid[0]],
            'rows': [[c['text'] for c in row] for row in grid[1:]], 'spans': spans}


def check_table_xml(element, table, rows, context):
    require(element is not None and element.attrib == {'ref': table['ref']}, 'Table container/ref changed')
    require(element.findtext('caption') == context['caption'] and
            element.find('caption').attrib == {'status': context['caption_status']}, 'Caption context changed')
    require(element.find('notes').attrib == {'scope': 'table-context-not-cell-applicability'}, 'Note context scope changed')
    require([(n.attrib.get('ref'), n.text or '') for n in element.findall('./notes/note')] ==
            [(n['ref'], n['text']) for n in context['notes']], 'Note context changed')
    xml_rows = element.findall('./header/row') + element.findall('./body/row')
    require([int(row.attrib['id']) for row in xml_rows] == [0]+rows, 'XML row coverage changed')
    spans = {}
    for span in table['spans']:
        for r in range(span['row'], span['row']+span['rows']):
            for c in range(span['col'], span['col']+span['cols']):
                spans[(r, c)] = span
    anchors = {}
    for row, row_id in zip(xml_rows, [0]+rows):
        values = table['headers'] if row_id == 0 else table['rows'][row_id-1]
        require(len(row) == len(values) == 10, 'Column count changed')
        for col, (item, expected) in enumerate(zip(row, values)):
            span = spans.get((row_id, col), {'row': row_id, 'col': col, 'rows': 1, 'cols': 1})
            anchor = span['row'], span['col']
            if anchor != (row_id, col):
                require(item.tag == 'span' and not item.attrib and not item.text and
                        anchors.get(anchor) == expected, 'Missing same-chunk span anchor')
            else:
                attrs = {k: str(span[n]) for k,n in [('rows', 'rows'), ('cols', 'cols')] if span[n] > 1}
                require(item.tag == 'c' and item.attrib == attrs and (item.text or '') == expected,
                        'Cell text/unit/marker/span changed')
                anchors[anchor] = expected


def check_evidence(cards, evidence):
    tables = evidence['tables']; context = evidence['context']['table_context']
    require([t['ref'] for t in tables] == ['#/tables/0', '#/tables/1'] and
            [len(t['rows']) for t in tables] == [21, 22], 'Table inventory changed')
    require(tables[0]['headers'] == tables[1]['headers'] == cards[ORDER[1]]['header_occurrences'][0]
            == cards[ORDER[1]]['header_occurrences'][1], 'Header occurrences changed')
    require([t['provenance'][0]['page_no'] for t in tables] == [1, 2], 'Excerpt provenance changed')
    cells = evidence['reconstruction']['cells']
    require(len(cells) == 30 and sum(c['source_blank'] for c in cells) == 13, 'Reconstruction blank count changed')
    require([(c['derived_grid_row'], c['column_index_0based']) for c in cells] ==
            [(r,c) for r in range(19,22) for c in range(10)], 'Reconstruction coordinates changed')
    indices = []
    for c in cells:
        require(c['text'] == tables[0]['rows'][c['derived_grid_row']-1][c['column_index_0based']]
                == ' '.join(c['raw_bounded_text'].split()), 'Reconstructed source text changed')
        require(c['source_blank'] is (not bool(c['text'])) and
                c['original_pdf_page_1based'] == 152 and c['excerpt_page_1based'] == 1,
                'Source blank/page changed')
        glyphs = sorted(c['characters'], key=lambda x:x['index'])
        require(''.join(c['text'].split()) == ''.join(''.join(g['text'] for g in glyphs).split()), 'Glyph evidence changed')
        l,t,r,b = c['bbox_top_left_pt']
        for g in glyphs:
            gl,gt,gr,gb = g['bbox_top_left_pt']
            require(l <= gl <= gr <= r and t <= gt <= gb <= b, 'Glyph outside cell rectangle')
            indices.append(g['index'])
    require(len(indices) == len(set(indices)) == 108, 'Glyph inventory/reuse changed')
    last = tables[0]['rows'][18:21]
    require([r[:3] for r in last] == [['HiTrap MabSelect','1 mL','30 mg/column'],
            ['','5 mL','150 mg/column'],['HiScreen MabSelect','4.7 mL','140 mg/column']], 'HiTrap/HiScreen association changed')
    require([r[9] for r in last] == ['11003490','11003490','28930581'] and
            all(r[3:7] == ['']*4 and r[7:9] == ['\u2022']*2 for r in last), 'Marks/blanks/codes changed')
    require(tables[1]['rows'][0][0] == 'PreDictor MabSelect' and
            cards[ORDER[1]]['native_table153_caption_refs'] == [], 'Continuation evidence changed')
    chunks = evidence['chunks']; meta = cards[ORDER[5]]['K800']
    require(len(chunks) == 7 and [c['token_count'] for c in chunks] == TOKENS and
            meta['total_tokens'] == sum(TOKENS) == 4375 and meta['max_tokens'] == 794, 'Token audit/count changed')
    texts = evidence['source_text_items']
    inventory = ET.fromstring(chunks[0]['text'])
    require(inventory.tag == 'source-text-inventory' and len(texts) == len(inventory) == 8 and
            [(n.attrib['ref'],n.attrib['label'],n.text or '') for n in inventory] ==
            [(t['self_ref'],t['label'],t['text']) for t in texts], 'Native text inventory changed')
    for n, cid in [(3,ORDER[2]),(4,ORDER[3]),(6,ORDER[4])]:
        require(cards[cid]['source_note_item'] == texts[n], 'Note source item changed')
    require(texts[6]['label'] == 'text' and texts[6]['parent'] == {'cref':'#/body'}, 'Native note-3 body status changed')
    coverage = {t['ref']:[] for t in tables}
    for i, part in enumerate(chunks):
        info = meta['chunks'][i]
        require(hashlib.sha256(part['text'].encode('utf-8')).hexdigest() == info['sha256'] and
                part['token_count'] == info['tokens'] and part['human_approved'] is False,
                'Frozen chunk fingerprint/status changed')
        if i == 0:
            continue
        page = 152 if i <= 3 else 153; table = tables[page-152]
        require(part['table_ref'] == info['table_ref'] == table['ref'] and part['rows'] == info['rows'] and
                part['original_pdf_pages'] == info['original_pdf_pages'] == [page] and
                part['excerpt_pages'] == [page-151] and part['document_sha256'] == DOCUMENT_SHA, 'Chunk source anchor changed')
        require(part['quarantined_variant_rows'] == info['quarantined_variant_rows'] ==
                [r for r in part['rows'] if page == 152 and r in [1,9,13]], 'Variant quarantine changed')
        parsed = ET.fromstring(part['text'])
        require(parsed.tag == 'structural-tables' and parsed.attrib == {'version':'1','diagnostic':'true'}, 'XML format changed')
        check_table_xml(parsed.find('table'), table, part['rows'], context[table['ref']])
        coverage[table['ref']] += part['rows']
    for table in tables:
        require(coverage[table['ref']] == list(range(1,len(table['rows'])+1)), 'Missing/reordered/duplicated rows')
        groups = context[table['ref']]['candidate_row_groups']
        groups = groups + [list(range(s['row'],s['row']+s['rows'])) for s in table['spans'] if s['rows']>1]
        for group in groups:
            require(any(p.get('table_ref') == table['ref'] and set(group) <= set(p.get('rows',[])) for p in chunks), 'Atomic group split')
    full = ET.fromstring(evidence['K0_text'])
    require(full.tag == 'structural-document' and len(full.findall('page-break')) == 1, 'K0 boundary changed')
    require(ET.tostring(full.find('source-text-inventory')) == ET.tostring(inventory), 'K0 inventory changed')
    full_tables = full.findall('./structural-tables/table')
    require(len(full_tables)==2, 'K0 table inventory changed')
    for element, table in zip(full_tables,tables):
        check_table_xml(element,table,list(range(1,len(table['rows'])+1)),context[table['ref']])
    require(hashlib.sha256(evidence['K0_text'].encode('utf-8')).hexdigest() == cards[ORDER[5]]['K0']['sha256'], 'K0 fingerprint changed')
    require(local_digest(evidence['context']) == cards[ORDER[5]]['context_sha256'], 'Frozen context changed')


def verify(package=PACKAGE, source_document=None):
    package = Path(package)
    require({p.name for p in package.iterdir()} == FILES | {'manifest.json'}, 'Package file inventory changed')
    m = read(package/'manifest.json')
    require(set(m['files']) == FILES and set(m['supporting_files']) == SUPPORT, 'Manifest inventory changed')
    for name, expected in m['files'].items():
        require(file_digest(package/name) == expected, f'Package digest mismatch: {name}')
    for name, expected in m['supporting_files'].items():
        require(file_digest(ROOT/name) == expected, f'Support digest mismatch: {name}')
    require(m['counts'] == COUNTS and m['publication_allowed'] is False, 'Counts/publication scope changed')
    require(m['source']['pdf_sha256'] == PDF_SHA and m['source']['derived_document_sha256'] == DOCUMENT_SHA and
            m['source']['native_T1_document_sha256'] == NATIVE_SHA and
            m['source']['source_map']['pages'] == [{'excerpt_page_1based':i,'original_pdf_page_1based':151+i,
                'original_pdf_page_index_0based':150+i,'printed_page':str(151+i)} for i in (1,2)], 'Source mapping changed')
    payload = read(package/'cards.json'); cards_list = payload['cards']
    require([c['card_id'] for c in cards_list] == ORDER, 'Card inventory changed')
    cards = {c['card_id']:c for c in cards_list}
    for cid,c in cards.items():
        require(local_digest(c) == m['lineage']['card_sha256'][cid] and canonical(c) == m['canonical_cards'][cid], 'Original card digest changed')
        require(c['status']=='pending_human_review' and c['human_approved'] is False and not c['decisions'], 'Frozen card promoted')
        require(c.get('source_document_sha256',c.get('document_sha256')) == DOCUMENT_SHA and c['source_pdf_sha256']==PDF_SHA, 'Card source changed')
    require(canonical(payload['evidence']) == m['canonical_evidence'], 'Selected evidence digest changed')
    check_evidence(cards,payload['evidence'])
    journal = read(package/'events.json'); review = read(package/'review.json')
    state = deepcopy(journal['initial_review'])
    require(local_digest(state) == m['lineage']['initial_state_sha256'], 'Initial state changed')
    require(len(journal['events'])==6, 'Event count changed')
    for i, event in enumerate(journal['events'],1):
        cid = ORDER[i-1]; decision = event['decision']; filename = f'{i:03}-{cid}.json'
        require(event['event_id'] == f'{i:03}-{cid}' and decision['card_id']==cid and
                decision['decision']=='validated_with_reservation', 'Decision inventory changed')
        require(local_digest(event) == m['lineage']['event_sha256'][event['event_id']], 'Original event/quotation changed')
        require(decision['reviewable_sha256'] == event['reviewable_sha256'] == local_digest(cards[cid]), 'Decision card binding changed')
        require(event['base_review_file_sha256'] == local_digest(state), 'Prior state binding changed')
        require(event['source_document_sha256']==DOCUMENT_SHA and bool(decision['original_human_message']) and
                '\ufffd' not in decision['original_human_message'], 'Decision source/quotation changed')
        if i>1:
            previous = journal['events'][i-2]
            require(event['previous_event_sha256']==local_digest(previous) and
                    event['previous_event_file']==previous['event_id']+'.json', 'Prior event link changed')
        entry = state['cards'][cid]
        require(entry['decision']=='pending' and entry['reviewable_sha256']==local_digest(cards[cid]), 'Invalid pending transition')
        require(bool(decision['reservations']) and decision['reservations'] ==
                cards[cid].get('reservations',decision['reservations']), 'Reservations changed')
        entry.update(decision=decision['decision'],event_file=filename,event_sha256=local_digest(event),
                     human_approved_for_documentary_scope=True)
        for key in ('approved_annotation','approved_cell_note_bindings'):
            if key in decision: entry[key]=deepcopy(decision[key])
        entry['reservations']=deepcopy(decision['reservations'])
        for next_id,pending in event.get('added_pending_cards',{}).items():
            require(next_id not in state['cards'] and pending == {'reviewable_sha256':local_digest(cards[next_id]),'decision':'pending'}, 'Introduced card changed')
            state['cards'][next_id] = deepcopy(pending)
        state.update(deepcopy(event.get('state_updates',{})))
        require(local_digest(state)==m['lineage']['state_sha256'][f'{i:03}'], 'Replayed state changed')
    require(state == review and local_digest(review)==m['lineage']['final_state_sha256'], 'Final state changed')
    require(review['human_approved'] is False and review['publication_allowed'] is False and
            review['production_retrieval_validated'] is False and review['review_status']=='complete_with_reservations' and
            review['review_counts']=={'cards':6,'validated_with_reservation':6,'pending':0,'approved_note_cell_bindings':15}, 'Blanket approval scope changed')
    all_bindings=[]
    for cid,expected in zip(ORDER[2:5],[1,2,12]):
        bindings = review['cards'][cid]['approved_cell_note_bindings']
        require(len(bindings)==expected, 'Note binding count changed')
        candidates=cards[cid]['candidate_cell_note_bindings']
        require(bindings == [{**b,'note_ref':cards[cid]['source_note_item']['self_ref'],
                    'human_approved_for_documentary_scope':True} for b in candidates], 'Note cell scope changed')
        all_bindings += [(b['table_ref'],b['grid_row_0based'],b['column_0based'],b['note_ref']) for b in bindings]
    require(len(all_bindings)==len(set(all_bindings))==15, 'Duplicate note links')
    text = json.dumps([payload,journal,review,m],ensure_ascii=False)
    require(not re.search(r'(?i)[a-z]:[\\/]|data:image/|"(?:api_key|password)"',text), 'Private paths/embedded assets/secrets included')
    if source_document is not None:
        require(hashlib.sha256(Path(source_document).read_bytes()).hexdigest()==DOCUMENT_SHA, 'Wrong original derived document')
        source=read(Path(source_document))
        require([table_record(t) for t in source['tables']]==payload['evidence']['tables'] and
                source['texts']==payload['evidence']['source_text_items'], 'Selected native evidence differs')
    return {'status':'passed',**COUNTS,'event_chain_replayed':True,'source_document_replayed':source_document is not None,
            'remaining_variant_quarantines':[1,9,13],'publication_allowed':False,'production_retrieval_validated':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=PACKAGE)
    parser.add_argument('--source-document',type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(verify(args.package,args.source_document)))
    except (ValueError,KeyError,TypeError,IndexError,OSError,ET.ParseError) as error:
        parser.exit(1,f'Package verification failed: {error}\n')


if __name__=='__main__':
    main()
