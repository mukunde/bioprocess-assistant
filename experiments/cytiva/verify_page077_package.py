"""Offline verification of the curated page-77 review; standard library only."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).parent / 'reviewed-page-077'
FILES = {'README.md', 'cards.json', 'review.json', 'events.json'}
ORDER = ['P77-layout-species', 'P77-pH'] + [f'P77-applicability-{i}' for i in range(1, 8)] + ['P77-chunking']
COUNTS = {'cards': 10, 'table_cells': 68, 'blank_species_cells': 10, 'pH_cells': 32,
          'remarks': 7, 'remark_items': 8, 'chunks': 2,
          'validated_with_reservation': 10, 'pending': 0}


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def local_digest(value):
    text = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').replace('\n', '\r\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_content(cards):
    """Check reviewed cells, independent context groups and existing chunks."""
    cells, coverage = {}, Counter()
    layout, ph = cards['P77-layout-species'], cards['P77-pH']
    source_cells = layout['headers'] + [c for row in layout['species_subclass_cells'] for c in row]
    source_cells += [row[key] for row in ph['rows'] for key in ('binding_pH_cell', 'elution_pH_cell')]
    for cell in source_cells:
        address = (cell['start_row_offset_idx'], cell['start_col_offset_idx'])
        cells[address] = cell
        coverage[address] += 1
    require(set(coverage) == {(r, c) for r in range(17) for c in range(4)} and
            set(coverage.values()) == {1}, 'Table coverage is not exact')
    require(sum(not cells[r, 0]['text'] for r in range(1, 17)) == 10, 'Species blanks changed')
    require([cells[0, c]['text'] for c in range(4)] ==
            ['Species', 'Subclass', 'Protein A binding pH', 'Protein A elution pH'], 'Headers changed')
    expected_groups = [('Human', [1, 2, 3, 4]), ('Cow', [5]), ('Goat', [6]),
                       ('Guinea pig', [7, 8]), ('Mouse', [9, 10, 11, 12]), ('Rat', [13, 14, 15, 16])]
    require([(g['species'], g['data_rows_1based']) for g in layout['proposed_visual_groups']] == expected_groups,
            'Reviewed species scope changed')
    context = {r: species for species, rows in expected_groups for r in rows}
    require([row['data_row_1based'] for row in ph['rows']] == list(range(1, 17)), 'Missing pH row')
    for row in ph['rows']:
        r = row['data_row_1based']
        require(row['species_context'] == context[r] and row['source_species_cell'] == cells[r, 0]
                and row['source_subclass_cell'] == cells[r, 1]
                and row['subclass_as_converted'] == cells[r, 1]['text'], 'pH context/source mismatch')
    for g in layout['proposed_visual_groups']:
        require(g['subclasses_as_converted'] == [cells[r, 1]['text'] for r in g['data_rows_1based']],
                'Group subclasses changed')
    remarks, coverage = {}, Counter()
    for i in range(1, 8):
        card = cards[f'P77-applicability-{i}']
        items = card['source_items'] if 'source_items' in card else [card['source_item']]
        for item in items:
            remarks[item['self_ref']] = item
            coverage[item['self_ref']] += 1
        if i == 5:
            require(card['display_quote'] == ' '.join(x['text'] for x in items), 'Desalting sentence changed')
    require(set(coverage) == {f'#/texts/{i}' for i in range(1, 9)} and
            set(coverage.values()) == {1}, 'Remark coverage is not exact')
    chunk_card = cards['P77-chunking']
    chunks, metrics = chunk_card['chunks'], chunk_card['metrics']
    require(len(chunks) == 2, 'Wrong chunk count')
    known = set(remarks) | {'#/texts/9', '#/tables/0'}
    geometry_count = 0
    for i, chunk in enumerate(chunks):
        text, meta = chunk['text'], chunk['native_metadata']
        require(meta['chunk_id'] == i and meta['token_count'] == [760, 414][i]
                and meta['char_length'] == len(text) and meta['resplit_of'] is None,
                'Chunk metadata mismatch')
        require(meta['text_hash'] == hashlib.blake2b(text.encode('utf-8'), digest_size=8).hexdigest(),
                'Chunk fingerprint mismatch')
        require(meta['page_numbers'] == chunk['all_item_provenance_pages'] == [1], 'Chunk page changed')
        require(set(meta['doc_item_refs']) <= known, 'Unknown backing item')
        for g in meta['item_geometry']:
            l, t, r, b = g['bbox']
            require(g['ref'] in meta['doc_item_refs'] and g['page_no'] == 1 and
                    0 <= l < r <= g['page_width'] and 0 <= t < b <= g['page_height'], 'Invalid geometry')
            geometry_count += 1
    require(geometry_count == 10, 'Wrong backing geometry count')
    require(layout['caption'] in chunks[0]['text'] and
            all(cell['text'] in chunks[0]['text'] for cell in cells.values() if cell['text']),
            'Converted cell/caption missing from table chunk')
    membership = {ref: [i for i, c in enumerate(chunks) if item['text'] in c['text']]
                  for ref, item in remarks.items()}
    require(membership == {f'#/texts/{i}': [0 if i <= 2 else 1] for i in range(1, 9)},
            'Remark/chunk partition changed')
    require(chunk_card['checks']['text_item_membership'] == {**membership, '#/texts/9': [1]},
            'Recorded membership mismatch')
    require(metrics['K0_tokens'] == 1469 and metrics['variants']['K800']['total_tokens'] == 1174
            and metrics['variants']['K800']['secondary_resplits'] == 0, 'Token audit changed')
    require(cells[6, 2]['text'] == cells[8, 2]['text'] == 'n.a', 'Source punctuation correction lost')
    return cells, remarks


def verify(package=PACKAGE, source_document=None):
    manifest = read(package/'manifest.json')
    require(manifest['package_version'] == 1 and manifest['package_hash_policy'] == 'sha256_utf8_lf',
            'Unsupported package contract')
    require(set(manifest['files']) == FILES and
            {f.name for f in package.iterdir() if f.is_file()} == FILES | {'manifest.json'}, 'Wrong package inventory')
    for name in FILES:
        require(file_digest(package/name) == manifest['files'][name], 'File digest mismatch: '+name)
    card_list, review, journal = (read(package/n) for n in ('cards.json', 'review.json', 'events.json'))
    require([c['id'] for c in card_list] == ORDER, 'Card order/inventory mismatch')
    cards = {c['id']: c for c in card_list}
    require([d['card_id'] for d in review['decisions']] == ORDER, 'Decision inventory mismatch')
    decisions = {d['card_id']: d for d in review['decisions']}
    require(review['human_approved'] is True and review['publication_allowed'] is False and
            review['production_retrieval_validated'] is False and
            review['review_status'] == 'documentary_and_diagnostic_conservation_review_completed_with_reservations'
            and bool(review['scope']), 'Wrong approval scope')
    for cid in ORDER:
        card, decision = cards[cid], decisions[cid]
        require(canonical({k:v for k,v in card.items() if k != 'reviewable_sha256'}) ==
                card['reviewable_sha256'] == decision['reviewable_sha256'], 'Card digest mismatch: '+cid)
        require(local_digest(card) == manifest['lineage']['card_file_sha256'][cid], 'Original card changed')
        require(card['human_approved'] is False and card['publication_allowed'] is False,
                'Frozen card was promoted')
        require(decision['decision'] == 'validated_with_reservation' and bool(decision['reservations']),
                'Missing reservation: '+cid)
        require(card['source'] == manifest['source'], 'Source binding changed')
    cells, remarks = check_content(cards)
    require(cards['P77-chunking']['metrics']['conversion_sha256'] == manifest['source']['document_sha256'],
            'Chunk/conversion binding changed')
    require(manifest['counts'] == COUNTS, 'Manifest counts changed')
    state = copy.deepcopy(journal['base_review'])
    require(state['card_id'] == ORDER[0] and state['decision'] == 'pending' and
            state['reviewable_sha256'] == cards[ORDER[0]]['reviewable_sha256'] and
            local_digest(state) == manifest['lineage']['initial_review_file_sha256'], 'Initial review mismatch')
    require(len(journal['events']) == len(journal['replay_steps']) == 10, 'Wrong journal length')
    for i, (event, step) in enumerate(zip(journal['events'], journal['replay_steps']), 1):
        cid = ORDER[i-1]
        require(event['event_id'] == f'{i:03}-'+cid and event['decision'] == decisions[cid],
                'Event decision/order mismatch')
        require(event['reviewable_sha256'] == cards[cid]['reviewable_sha256'] and
                event['source_document_sha256'] == manifest['source']['document_sha256'], 'Event source/card mismatch')
        require(local_digest(event) == manifest['lineage']['event_file_sha256'][event['event_id']],
                'Original event changed')
        require(event['decision']['original_human_message'] and
                '\ufffd' not in event['decision']['original_human_message'], 'Damaged human quotation')
        key = 'base_review_file_sha256' if i == 1 else 'previous_review_file_sha256'
        require(event[key] == local_digest(state), 'Prior state chain mismatch')
        if i > 1:
            require(event['previous_event_sha256'] == local_digest(journal['events'][i-2]), 'Prior event chain mismatch')
        entries = [state] if i == 1 else state['decisions']
        entries = [copy.deepcopy(event['decision']) if d['card_id'] == cid else copy.deepcopy(d) for d in entries]
        pending = step['introduced_pending_decisions']
        require(len(pending) == (1 if i < 10 else 0), 'Wrong progressive-card introduction')
        if pending:
            require(pending[0] == {'card_id': ORDER[i], 'reviewable_sha256': cards[ORDER[i]]['reviewable_sha256'],
                    'decision': 'pending', 'reviewer': None, 'decided_at_utc': None,
                    'original_human_message': None, 'reservations': []}, 'Introduced decision is not pending')
        entries += copy.deepcopy(pending)
        require('decisions' not in step['state_metadata'] and set(step['state_key_order']) ==
                set(step['state_metadata']) | {'decisions'} and len(step['state_key_order']) ==
                len(step['state_metadata'])+1, 'Invalid replay metadata')
        state = {k: entries if k == 'decisions' else copy.deepcopy(step['state_metadata'][k])
                 for k in step['state_key_order']}
        require(state['publication_allowed'] is False and state['human_approved'] is (i == 10),
                'Intermediate approval scope changed')
        require(local_digest(state) == manifest['lineage']['review_state_file_sha256'][f'{i:03}'],
                'Replayed state hash mismatch')
    require(state == review and local_digest(review) == manifest['lineage']['final_review_file_sha256'],
            'Final state differs from journal')
    require(cards['P77-pH']['species_context_decision']['sha256'] ==
            manifest['lineage']['event_file_sha256']['001-P77-layout-species'], 'Species decision binding changed')
    if source_document is not None:
        require(hashlib.sha256(source_document.read_bytes()).hexdigest() == manifest['source']['document_sha256'],
                'Wrong original conversion')
        doc = read(source_document)
        require(all(c == doc['tables'][0]['data']['grid'][r][col] for (r,col),c in cells.items()),
                'Source table mismatch')
        index = {item['self_ref']: item for item in doc['texts']}
        require(all(item == index[ref] for ref,item in remarks.items()) and
                cards['P77-layout-species']['caption'] == index['#/texts/0']['text'], 'Source remark/caption mismatch')
    return {'status': 'passed', **COUNTS, 'event_chain_replayed': True,
            'source_conversion_replayed': source_document is not None,
            'publication_allowed': False, 'production_retrieval_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--source-document', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.package, args.source_document)))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        parser.exit(1, f'Package verification failed: {error}\n')


if __name__ == '__main__':
    main()
