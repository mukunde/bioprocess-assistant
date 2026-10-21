"""Verify the compact page-88 documentary review using the standard library."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).parent / 'reviewed-page-088'
FILES = {'README.md', 'packet.json', 'review.json', 'events.json'}


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def local_digest(value):
    """Replay original Windows artifacts: UTF-8, indent=2 and CRLF."""
    text=(json.dumps(value, ensure_ascii=False, indent=2)+'\n').replace('\n','\r\n')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify(package=PACKAGE):
    m=read(package/'manifest.json')
    require(m['package_version']==1 and m['package_hash_policy']=='sha256_utf8_lf', 'Unsupported package contract')
    require(set(m['files'])==FILES, 'Wrong manifest inventory')
    require({f.name for f in package.iterdir() if f.is_file()}==FILES|{'manifest.json'}, 'Unexpected package file')
    for name in FILES:
        require(file_digest(package/name)==m['files'][name], 'File digest mismatch: '+name)
    packet,review,journal=(read(package/n) for n in ('packet.json','review.json','events.json'))
    require(canonical(packet)==m['lineage']['packet_canonical_sha256']==review['packet_sha256'], 'Wrong packet binding')
    require(local_digest(packet)==m['lineage']['packet_original_file_sha256'], 'Original packet bytes cannot be reconstructed')
    require(local_digest(review)==m['lineage']['final_review_original_file_sha256'], 'Final review changed')
    require(review['human_approved'] is True and review['publication_allowed'] is False and
            review['review_status']=='documentary_review_completed_with_reservations' and bool(review['approval_scope']), 'Wrong approval scope')
    require(packet['human_approved'] is False and packet['publication_allowed'] is False, 'Frozen preparation was promoted')
    require(packet['source_map']==m['source']['source_map'], 'Source page map changed')
    require(packet['source_hashes']==m['source']['artifact_sha256'], 'Source provenance changed')
    rows=packet['table']['cells']; require(len(rows)==8 and all(len(r)==5 for r in rows), 'Wrong table dimensions')
    require(sum(not c['text'] for r in rows for c in r)==2, 'Blank cells changed')
    require(len(packet['notes'])==5 and len(packet['anchors'])==6 and len(packet['bindings'])==12, 'Wrong note counts')
    cards={c['id']:c for c in packet['review_cards']}
    decisions={d['card_id']:d for d in review['decisions']}
    require(len(cards)==len(packet['review_cards'])==len(decisions)==len(review['decisions'])==9 and set(cards)==set(decisions), 'Missing or duplicate card/decision')
    coverage=Counter()
    for cid,card in cards.items():
        require(canonical({k:v for k,v in card.items() if k!='reviewable_sha256'})==card['reviewable_sha256']==decisions[cid]['reviewable_sha256'], 'Card digest mismatch: '+cid)
        require(decisions[cid]['decision']=='validated_with_reservation' and bool(decisions[cid]['reservations']), 'Missing reservation: '+cid)
        for c in card['cells']:
            require(c==rows[c['row']][c['col']], 'Card/table mismatch')
            coverage[c['row'],c['col']]+=1
    require(set(coverage)=={(r,c) for r in range(8) for c in range(5)} and set(coverage.values())=={1}, 'Cell coverage is not exact')
    for note in packet['notes'].values():
        evidences=[c['evidence'] for c in note['conditions']]
        evidences += [r['evidence'] for c in note['conditions'] for r in c.get('source_parenthetical_representations',[])]
        if 'definition' in note: evidences.append(note['definition']['evidence'])
        for e in evidences:
            start,end=e['char_span']
            require(note['source_textline']['text'][start:end]==e['quote'], 'Evidence span mismatch')
            require(set(e['word_refs']) <= {w['word_ref'] for w in note['words']}, 'Missing evidence word reference')
    anchors={a['id']:a for a in packet['anchors']}
    for b in packet['bindings']:
        r,c=b['cell'];a=anchors[b['anchor_id']]
        require(b['note_id'] in packet['notes'] and a['note_id']==b['note_id'] and b['id'] in rows[r][c]['note_binding_refs'], 'Broken note binding')
    state=copy.deepcopy(journal['base_review'])
    require(local_digest(state)==m['lineage']['base_review_original_file_sha256'], 'Base review mismatch')
    require(state['packet_sha256']==canonical(packet) and all(d['decision']=='pending' for d in state['decisions']), 'Base state is not pending')
    events=journal['events'];require(len(events)==9, 'Wrong event count')
    seen=set()
    for i,event in enumerate(events,1):
        cid=event['decision']['card_id'];require(cid not in seen and cid in decisions, 'Repeated event card');seen.add(cid)
        require(event['packet_sha256']==canonical(packet) and event['decision']==decisions[cid], 'Event decision mismatch')
        require(event['event_id']==f'{i:03}-'+cid, 'Event sequence mismatch')
        require(local_digest(event)==m['lineage']['event_file_sha256'][event['event_id']], 'Event bytes changed')
        require(bool(event['decision']['original_human_message']) and '\ufffd' not in event['decision']['original_human_message'], 'Missing or damaged human quotation')
        previous_key='base_review_file_sha256' if i==1 else 'previous_review_file_sha256'
        require(event[previous_key]==local_digest(state), 'Prior state chain mismatch')
        if i>1: require(event['previous_event_sha256']==local_digest(events[i-2]), 'Prior event chain mismatch')
        state['decisions']=[copy.deepcopy(event['decision']) if d['card_id']==cid else d for d in state['decisions']]
        if i==9:
            for key in ('human_approved','publication_allowed','review_status','approval_scope','completed_at_utc'):state[key]=review[key]
        require(local_digest(state)==m['lineage']['review_state_file_sha256'][f'{i:03}'], 'Replayed state hash mismatch')
    require(state==review, 'Replay did not reach final review')
    require(m['counts']=={'cards':9,'cells':40,'blank_cells':2,'notes':5,'printed_anchors':6,'product_cell_note_bindings':12,'validated_with_reservation':9,'pending':0}, 'Manifest counts mismatch')
    return {'status':'passed',**m['counts'],'publication_allowed':False,'source_pdf_replayed':False,'event_chain_replayed':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=PACKAGE)
    args=parser.parse_args()
    try: print(json.dumps(verify(args.package)))
    except (ValueError,KeyError,TypeError,IndexError,OSError) as e:parser.exit(1, f'Package verification failed: {e}\n')


if __name__=='__main__':main()
