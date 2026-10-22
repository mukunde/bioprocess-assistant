"""Verify the compact page-104 documentary review using the standard library."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent / 'reviewed-page-104'
FILES = {'README.md', 'cards.json', 'review.json', 'events.json'}
SUPPORT = {'docs/experiments/cytiva-conversion-chunking-protocol.md',
           'docs/experiments/cytiva-figure-104-protocol.md',
           'docs/experiments/cytiva-figure-104-results.csv',
           'docs/experiments/cytiva-figure-104-results.md',
           'docs/experiments/cytiva-figure-104-review.csv',
           'docs/experiments/cytiva-page-104-human-review.md',
           'experiments/cytiva/page104_figure_spec.json'}
ORDER = ['P104-image-caption', 'P104-paths', 'P104-alternative',
         'P104-applicability', 'P104-VH3', 'P104-chunking']
COUNTS = {'cards': 6, 'validated_with_reservation': 6, 'pending': 0,
          'source_boxes': 14, 'source_paths': 5, 'source_connections': 11,
          'source_alternatives': 1, 'native_typed_diagram_relations': 0,
          'native_text_items': 28, 'picture_text_children': 25, 'chunks': 1,
          'K0_tokens': 392, 'K800_tokens': 316, 'secondary_resplits': 0,
          'direct_anchors': 3, 'reachable_items': 29}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def local_digest(value):
    text = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').replace('\n', '\r\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_content(cards):
    image, paths, alt, app, vh, chunk = [cards[cid] for cid in ORDER]
    caption = image['caption_source_item']
    require(caption['text'] == paths['caption_exact'] ==
            'Fig 3.29. AC media for purification of antibody fragments.', 'Caption mismatch')
    require(caption == app['source_caption_item'] == chunk['native_caption_source_item'] and
            image['picture_ref'] == '#/pictures/0' and
            image['native_caption_refs'] == chunk['native_picture_caption_refs'] == [{'cref': '#/texts/1'}]
            and caption['parent'] == {'cref': '#/pictures/0'}, 'Caption binding changed')
    expected = [['fab', 'fab-kappa', 'fab-capto'], ['fab', 'fab-lambda', 'fab-fabselect'],
                ['scfv', 'scfv-kappa', 'scfv-capto'], ['domain', 'domain-kappa', 'domain-capto'],
                ['domain', 'domain-vh3', 'domain-mabselect']]
    require(paths['proposed_recommended_paths'] ==
            [{'id': f'path-{i}', 'node_ids': p} for i,p in enumerate(expected, 1)], 'Source paths changed')
    nodes = {n['id']: n for n in paths['nodes']}
    require(len(paths['nodes']) == len(nodes) == 14 and len(paths['converted_label_checks']) == 14,
            'Source node inventory changed')
    require({n['node_id'] for n in paths['converted_label_checks']} == set(nodes), 'Label coverage changed')
    require(paths['source_annotated_recommended_connections'] ==
            [{'from': p[j], 'to': p[j+1], 'kind': 'directed_diagram_connection_not_process_sequence'}
             for p in expected for j in (0,1)], 'Source connections changed')
    scope = {'node_id': 'fab-kappaselect', 'path_id': 'path-1',
             'role': 'alternative_to_recommended_product', 'not_a_process_step': True}
    require(alt['proposed_alternative_scope'] == paths['alternative_scope_deferred'] == scope,
            'Alternative scope changed')
    require(alt['source_visual_connection']['from'] == 'fab-capto' and
            alt['source_visual_connection']['to'] == 'fab-kappaselect' and
            alt['native_typed_alternative_relation_present'] is False and
            paths['native_typed_directed_branch_edges'] == 0, 'Automatic edge quarantine changed')
    require(all(n == nodes[n['id']] for n in alt['source_nodes']) and
            {n['id'] for n in alt['source_nodes']} == {'fab', 'fab-kappa', 'fab-capto', 'fab-kappaselect'},
            'Alternative node binding changed')
    paragraph = app['paragraph_source_item']
    require(paragraph == alt['adjacent_paragraph_source_item'] == vh['paragraph_source_item'] and
            paragraph['self_ref'] == '#/texts/0', 'Paragraph copies differ')
    require(len(app['review_units']) == 5 and
            [u['id'] for u in app['review_units']] == ['condition', 'kappa', 'lambda', 'vh3', 'guide'] and
            all(u['source_quote'] in paragraph['text'] for u in app['review_units']) and
            all(q in paragraph['text'] for q in alt['target_quotes']), 'Applicability quotation changed')
    display = vh['proposed_review_representation']
    require(display['display'] == 'VH₃' and display['plain_text_alias'] == 'VH3' and
            display['implemented_in_raw_conversion_or_chunks'] is False, 'VH3 representation changed')
    require([x['self_ref'] for x in vh['diagram_source_text_items']] ==
            ['#/texts/16', '#/texts/17', '#/texts/26'] and
            [x['text'] for x in vh['diagram_source_text_items']] == ['VH', 'Heavy chain', '3'] and
            'heavy chain subtype VH 3 .' in paragraph['text'], 'Raw VH3 representation changed')
    children = vh['raw_diagram_child_order']
    require([x['cref'] for x in children] == [f'#/texts/{i}' for i in range(1,27)], 'Picture child order changed')
    require([children[i-1]['text'] for i in (16,17,26)] == ['VH', 'Heavy chain', '3'], 'Subscript order changed')
    require(len(chunk['chunks']) == 1, 'Unexpected chunk count')
    c = chunk['chunks'][0]; meta = c['native_metadata']; metrics = chunk['metrics']; checks = chunk['checks']
    k0, k800 = chunk['K0_text'], c['text']
    e0 = ET.fromstring(k0); e8 = ET.fromstring('<root>'+k800+'</root>')
    def values(el):
        return [(e.tag, ''.join(e.itertext()).strip()) for e in el.iter()
                if e.tag in ('text', 'caption', 'page_footer')]
    require(values(e0) == values(e8) and len(values(e0)) == 28, 'Text conservation changed')
    for el in (e0,e8):
        require([e.text for e in el.find('picture').findall('text')] ==
                [x['text'] for x in children if x['cref'] != '#/texts/1'], 'Picture text/order changed')
        require(el.find('picture').find('caption').text == caption['text'] and
                el.find('text').text == paragraph['text'], 'Caption/paragraph serialization changed')
        require(not any(e.tag in ('src', 'location') for e in el.iter()), 'Image/location serialization changed')
    require(meta['token_count'] == 316 and meta['char_length'] == len(k800) and meta['resplit_of'] is None and
            meta['text_hash'] == hashlib.blake2b(k800.encode('utf-8'), digest_size=8).hexdigest(),
            'Chunk fingerprint or metadata changed')
    require(meta['page_numbers'] == c['all_item_provenance_pages'] == [1] and
            c['anchor_scope'] == 'backing_items', 'Chunk page/anchor scope changed')
    require(meta['doc_item_refs'] == ['#/texts/0', '#/pictures/0', '#/texts/27'] and
            [g['ref'] for g in meta['item_geometry']] == meta['doc_item_refs'], 'Direct anchors changed')
    for g in meta['item_geometry']:
        l,t,r,b = g['bbox']
        require(g['page_no'] == 1 and 0 <= l < r <= g['page_width'] == 1920 and
                0 <= t < b <= g['page_height'] == 1080, 'Invalid chunk geometry')
    require(metrics['K0_tokens'] == 392 and metrics['variants']['K800']['total_tokens'] == 316 and
            metrics['variants']['K800']['raw_count'] == metrics['variants']['K800']['final_count'] == 1 and
            metrics['variants']['K800']['secondary_resplits'] == 0, 'Token/split audit changed')
    require(checks['native_text_items_preserved'] == 28 and checks['picture_child_text_items_preserved_in_order'] == 25
            and checks['reachable_item_count'] == 29 and
            set(checks['reachable_item_refs']) == {'#/pictures/0'} | {f'#/texts/{i}' for i in range(28)} and
            checks['typed_graph_edges_in_conversion_or_serialization'] == 0 and
            checks['image_src_in_K0'] is checks['image_src_in_K800'] is False and
            checks['actual_future_multimodal_or_serving_input'] == 'not_tested', 'Diagnostic limits changed')
    require(metrics['conversion_sha256'] == checks['conversion_sha256'] ==
            image['source']['conversion_document_sha256'], 'Conversion binding changed')
    return paragraph, caption


def verify(package=PACKAGE, source_document=None):
    m = read(package/'manifest.json')
    require(m['package_version'] == 1 and m['package_hash_policy'] == 'sha256_utf8_lf', 'Unsupported package')
    require(set(m['files']) == FILES and {p.name for p in package.iterdir()} == FILES | {'manifest.json'},
            'Wrong package inventory')
    for name in FILES:
        require(file_digest(package/name) == m['files'][name], 'File digest mismatch: '+name)
    require(set(m['supporting_files']) == SUPPORT, 'Wrong supporting-file inventory')
    for name,h in m['supporting_files'].items():
        require(file_digest(ROOT/name) == h, 'Supporting file changed: '+name)
    cards_list, review, journal = [read(package/n) for n in ('cards.json','review.json','events.json')]
    require([c['id'] for c in cards_list] == ORDER and
            [d['card_id'] for d in review['decisions']] == ORDER, 'Card/decision inventory mismatch')
    cards = {c['id']: c for c in cards_list}
    require(review['human_approved'] is True and review['publication_allowed'] is False and
            review['production_retrieval_validated'] is False and review['actual_model_image_attachment_validated'] is False
            and review['automatic_text_only_diagram_semantics'] == 'quarantined' and
            review['review_status'] == 'documentary_and_diagnostic_conservation_review_completed_with_reservations'
            and bool(review['scope']), 'Wrong final approval scope')
    for c,d in zip(cards_list, review['decisions']):
        require(canonical({k:v for k,v in c.items() if k != 'reviewable_sha256'}) ==
                c['reviewable_sha256'] == d['reviewable_sha256'], 'Card digest mismatch')
        require(local_digest(c) == m['lineage']['card_file_sha256'][c['id']], 'Original card changed')
        require(c['human_approved'] is c['publication_allowed'] is False and
                c['status'] == 'pending_human_review', 'Frozen preparation was promoted')
        require(c['source'] == m['source'], 'Source binding changed')
        require(d['decision'] == 'validated_with_reservation' and
                bool(d['reservations']) and d['reservations'] == c['reservations_to_retain'], 'Reservation changed')
    paragraph,caption = check_content(cards)
    require(m['counts'] == COUNTS, 'Counts changed')
    source = m['source']; smap = source['source_map']
    require(source['original_pdf_page_1based'] == 104 and source['printed_page'] == '104' and source['figure'] == '3.29'
            and smap['pages'] == [{'excerpt_page_1based': 1, 'original_pdf_page_1based': 104,
                                  'original_pdf_page_index_0based': 103, 'printed_page': '104'}], 'Source page mapping changed')
    spec = read(ROOT/'experiments/cytiva/page104_figure_spec.json')
    require(cards['P104-paths']['nodes'] == spec['nodes'] and
            cards['P104-paths']['proposed_recommended_paths'] == spec['recommended_paths'],
            'Source reference content mismatch')
    require(file_digest(ROOT/'experiments/cytiva/page104_figure_spec.json') ==
            cards['P104-paths']['source_candidate_spec_sha256'] == cards['P104-alternative']['source_candidate_spec_sha256'],
            'Original source-reference binding changed')
    state = copy.deepcopy(journal['base_review'])
    require(state['card_id'] == ORDER[0] and state['decision'] == 'pending' and
            state['reviewable_sha256'] == cards[ORDER[0]]['reviewable_sha256'] and
            local_digest(state) == m['lineage']['initial_review_file_sha256'], 'Initial state changed')
    require(len(journal['events']) == len(journal['replay_steps']) == 6, 'Wrong journal length')
    for i,(ev,step) in enumerate(zip(journal['events'],journal['replay_steps']),1):
        cid = ORDER[i-1]
        require(ev['event_id'] == f'{i:03}-'+cid and ev['decision'] == review['decisions'][i-1] and
                ev['reviewable_sha256'] == cards[cid]['reviewable_sha256'] and
                ev['source_document_sha256'] == source['conversion_document_sha256'], 'Event decision/source mismatch')
        require(local_digest(ev) == m['lineage']['event_file_sha256'][ev['event_id']], 'Original event changed')
        require(bool(ev['decision']['original_human_message']) and
                '\ufffd' not in ev['decision']['original_human_message'], 'Damaged human quotation')
        key = 'base_review_file_sha256' if i == 1 else 'previous_review_file_sha256'
        require(ev[key] == local_digest(state), 'Prior state link changed')
        if i > 1:
            require(ev['previous_event_sha256'] == local_digest(journal['events'][i-2]), 'Prior event link changed')
        entries = [state] if i == 1 else state['decisions']
        entries = [copy.deepcopy(ev['decision']) if d['card_id'] == cid else copy.deepcopy(d) for d in entries]
        pending = step['introduced_pending_decisions']
        require(len(pending) == (1 if i < 6 else 0), 'Progressive card introduction changed')
        if pending:
            require(pending[0] == {'card_id': ORDER[i], 'reviewable_sha256': cards[ORDER[i]]['reviewable_sha256'],
                    'decision': 'pending', 'reviewer': None, 'decided_at_utc': None,
                    'original_human_message': None, 'reservations': []}, 'Invalid introduced pending decision')
        entries += copy.deepcopy(pending)
        require('decisions' not in step['state_metadata'] and set(step['state_key_order']) ==
                set(step['state_metadata']) | {'decisions'} and len(step['state_key_order']) ==
                len(step['state_metadata'])+1, 'Invalid replay metadata')
        state = {k: entries if k == 'decisions' else copy.deepcopy(step['state_metadata'][k])
                 for k in step['state_key_order']}
        require(state['publication_allowed'] is False and state['human_approved'] is (i == 6), 'Intermediate scope changed')
        require(local_digest(state) == m['lineage']['review_state_file_sha256'][f'{i:03}'], 'Replayed state hash mismatch')
    require(state == review and local_digest(review) == m['lineage']['final_review_file_sha256'], 'Final review mismatch')
    if source_document is not None:
        require(hashlib.sha256(source_document.read_bytes()).hexdigest() == source['conversion_document_sha256'],
                'Wrong original conversion')
        doc = read(source_document); texts = {x['self_ref']:x for x in doc['texts']}
        selected = [paragraph,caption,cards['P104-alternative']['converted_alternative_source_item'],
                    cards['P104-alternative']['converted_alternative_role_source_item']]
        selected += cards['P104-VH3']['diagram_source_text_items']
        require(all(item == texts[item['self_ref']] for item in selected), 'Native source item mismatch')
        pic = doc['pictures'][0]
        require(pic['captions'] == cards['P104-image-caption']['native_caption_refs'] and
                pic['prov'] == cards['P104-image-caption']['picture_provenance'], 'Native picture binding changed')
        require([{'cref':r['cref'], 'text':texts[r['cref']]['text']} for r in pic['children']] ==
                cards['P104-VH3']['raw_diagram_child_order'], 'Native child order mismatch')
        require(len(texts) == 28 and all(x['text'] in cards['P104-chunking']['K0_text'] and
                x['text'] in cards['P104-chunking']['chunks'][0]['text'] for x in texts.values()), 'Native text loss')
    return {'status': 'passed', **COUNTS, 'event_chain_replayed': True,
            'source_conversion_replayed': source_document is not None,
            'automatic_text_only_diagram_semantics': 'quarantined', 'publication_allowed': False,
            'production_retrieval_validated': False, 'actual_model_image_attachment_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=PACKAGE)
    parser.add_argument('--source-document', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.package, args.source_document)))
    except (ValueError, KeyError, TypeError, IndexError, OSError, ET.ParseError) as error:
        parser.exit(1, f'Package verification failed: {error}\n')


if __name__ == '__main__':
    main()
