"""Verify the v2 annotation-conservation review offline; standard library only."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from experiments.cytiva.verify_pages152153_package import (
    ROOT, PACKAGE as BASE_PACKAGE, DOCUMENT_SHA, PDF_SHA, read, canonical,
    local_digest, file_digest, require, check_table_xml, verify as verify_base)

PACKAGE=Path(__file__).parent/'reviewed-pages-152-153-v2'
CID='P152-153-annotated-chunking'
FILES={'README.md','cards.json','events.json','review.json'}
SUPPORT={'docs/experiments/cytiva-table-152-153-annotations.md',
    'docs/experiments/cytiva-table-152-153-annotations-human-review.md',
    'experiments/cytiva/apply_reviewed_tables.py','ingestion/reviewed_table_chunking.py',
    'tests/test_reviewed_table_chunking.py'}
DEPENDENCIES={str((BASE_PACKAGE/n).relative_to(ROOT)).replace('\\','/') for n in FILES|{'manifest.json'}}
DEPENDENCIES.add('experiments/cytiva/verify_pages152153_package.py')
APPROVALS={'g1':'P152-HiTrap-HiScreen','c1':'P152-153-continuity','n1':'P152-N1','n2':'P152-N2','n3':'P153-N3'}
COUNTS={'cards':1,'validated_with_reservation':1,'pending':0,'prior_documentary_decisions':6,
    'approved_note_bindings':15,'primary_rows':40,'quarantined_rows':3,'grid_positions':430,
    'primary_K0_tokens':3952,'quarantine_K0_tokens':446,'primary_K800_chunks':8,
    'quarantine_K800_chunks':1,'primary_K800_tokens':5230,'quarantine_K800_tokens':425,
    'primary_K800_max_tokens':765,'quarantine_K800_max_tokens':425}


def windows_digest(path):
    """Reconstruct historical copied repository bytes after a portable checkout."""
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')).hexdigest()


def text_digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check_annotations(payload, base, base_review, base_events):
    a=payload['annotations']; card=payload['card']
    require(a['document_sha256']==DOCUMENT_SHA and a['source_pdf_sha256']==PDF_SHA,
            'Annotation source changed')
    require(a['human_approved'] is a['production_ready'] is a['publication_allowed'] is False and
            a['annotations_human_validated'] is True and a['approval_scope']=='documentary_annotations_only',
            'Annotation approval scope changed')
    require(a['quarantine']=={'#/tables/0':[1,9,13],'#/tables/1':[]},'Quarantine released or changed')
    require(a['caption']==base['evidence']['source_text_items'][2]['text'],'Caption changed')
    require(a['continuation']=={**base_review['cards']['P152-153-continuity']['approved_annotation'],'approval':'c1'},
            'Reviewed continuation changed')
    require(a['row_groups']==[{'table_ref':'#/tables/0','rows':[19,20],'approval':'g1',
        'source_blank_product_cell':{'row':20,'col':0},'raw_source_rowspan_created':False}],
        'Reviewed grouping/blank changed')
    events={e['decision']['card_id']:e for e in base_events['events']}
    require(set(a['approvals'])==set(APPROVALS) and a['approvals']==card['approved_annotation_sources'],
            'Inherited approval sources changed')
    for aid,cid in APPROVALS.items():
        approval=a['approvals'][aid]; state=base_review['cards'][cid]
        require(approval['card_id']==cid and approval['event_sha256']==state['event_sha256']==local_digest(events[cid]) and
                approval['reviewable_sha256']==state['reviewable_sha256'] and
                approval['original_human_message']==events[cid]['decision']['original_human_message'] and
                approval['reservations']==state['reservations'] and bool(approval['serialization_limit']),
                'Inherited quotation/reservation/source changed')
    expected=[]
    for aid in ('n1','n2','n3'):
        for b in base_review['cards'][APPROVALS[aid]]['approved_cell_note_bindings']:
            expected.append({'id':f'b{len(expected)+1:02}','approval':aid,'table_ref':b['table_ref'],
                'row':b['grid_row_0based'],'col':b['column_0based'],'note_ref':b['note_ref'],
                'source_cell':b['source_cell'],'original_pdf_page_1based':b['original_pdf_page_1based'],
                'excerpt_page_1based':b['excerpt_page_1based']})
    require(a['note_bindings']==card['source_note_bindings']==expected and len(expected)==15,
            'Approved note-cell scope changed')
    native={t['self_ref']:t for t in base['evidence']['source_text_items']}
    require(a['notes']=={ref:native[ref] for ref in ['#/texts/3','#/texts/4','#/texts/6']},
            'Native note text/provenance changed')
    base_cards={c['card_id']:c for c in base['cards']}
    require(a['remaining_reservations']==base_cards['P152-153-chunking']['reservations'],
            'Earlier conservation reservations changed')


def check_xml(text, ref, rows, blocked, a, tables):
    root=ET.fromstring(text); node=root.find('table')
    require(root.tag=='reviewed-tables' and root.attrib=={'version':'2','diagnostic':'true','quarantined':str(blocked).lower()},
            'XML format/quarantine changed')
    page=152 if ref=='#/tables/0' else 153
    require(node is not None and node.attrib=={'ref':ref,'original-page':str(page),'logical-table':'A1.7'},
            'Source table/page changed')
    bindings=[b for b in a['note_bindings'] if b['table_ref']==ref and b['row'] in rows]
    groups=[g for g in a['row_groups'] if g['table_ref']==ref and set(g['rows'])&set(rows)]
    require(all(set(g['rows'])<=set(rows) for g in groups),'Reviewed group cut')
    continuation=a['continuation'] if ref==a['continuation']['from_table'] else None
    expected_cont=[] if continuation is None else [{'of':continuation['to_table'],'approval':'c1'}]
    require([n.attrib for n in node.findall('continuation')]==expected_cont,'Continuation placement changed')
    require([n.attrib for n in node.findall('./annotations/row-group')]==[
        {'rows':' '.join(map(str,g['rows'])),'approval':g['approval']} for g in groups],'Group annotation changed')
    require([n.attrib for n in node.findall('./annotations/note-link')]==[
        {'id':b['id'],'row':str(b['row']),'col':str(b['col']),'note':b['note_ref'],'approval':b['approval']} for b in bindings],
        'Note-link placement changed')
    approvals=sorted({b['approval'] for b in bindings}|{g['approval'] for g in groups}|({'c1'} if continuation else set()))
    require([(n.get('approval'),n.text) for n in node.findall('./limits/limit')]==[
        (aid,a['approvals'][aid]['serialization_limit']) for aid in approvals],'Serialized reservation changed')
    notes=[{'ref':ref,'text':a['notes'][ref]['text']} for ref in sorted({b['note_ref'] for b in bindings})]
    require(node.find('notes').attrib=={'scope':'explicit-cell-links-only'} and
            [(n.get('ref'),n.text) for n in node.findall('./notes/note')]==[(n['ref'],n['text']) for n in notes],
            'Unscoped or missing note body')
    # Reuse the v1 independent cell/span comparator after explicitly checking v2
    # attributes and scope above. Only the comparator's envelope is normalized.
    normalized=deepcopy(node); normalized.attrib={'ref':ref}
    normalized.find('notes').attrib={'scope':'table-context-not-cell-applicability'}
    check_table_xml(normalized,tables[ref],rows,{'caption':a['caption'],
        'caption_status':'reviewed-continuation' if continuation else 'native','notes':notes})
    return [b['id'] for b in bindings],approvals


def check_evidence(payload, base):
    card=payload['card']; a=payload['annotations']; e=payload['evidence']
    tables={t['ref']:t for t in base['evidence']['tables']}
    expected={False:{(ref,r) for ref,t in tables.items() for r in range(1,len(t['rows'])+1)
                     if not(ref=='#/tables/0' and r in [1,9,13])},
              True:{('#/tables/0',r) for r in [1,9,13]}}
    records={r['file']:r for r in card['K800_fragments']}; seen_links=[]; inventory=None
    require(len(records)==9,'Fragment inventory changed')
    all_files={}
    for blocked,bucket,tokens in [(False,'primary',[212,695,765,630,758,703,759,708]),(True,'quarantine',[425])]:
        parts=e[bucket+'_chunks']; prefix='quarantine/' if blocked else ''
        require([p['token_count'] for p in parts]==tokens and all(n<=800 for n in tokens),'Recorded token counts changed')
        coverage=[]
        for i,p in enumerate(parts):
            file=f'{prefix}K800/chunk-{i:03}.xml'; summary=records[file]
            require(text_digest(p['text'])==summary['sha256'] and p['token_count']==summary['tokens'] and
                    p['role']==summary['role'] and p['quarantined'] is summary['quarantined'] is blocked,
                    'Chunk fingerprint/status changed')
            require(p['production_ready'] is False and p['human_review_status']=='new_chunk_conservation_pending' and
                    p['approval_scope']=='documentary_annotations_only' and p['document_sha256']==DOCUMENT_SHA and
                    p['annotations_sha256']==local_digest(a),'Frozen chunk approval/source changed')
            all_files[file]=text_digest(p['text'])
            if p['role']=='source-inventory-not-retrieval':
                require(not blocked and i==0 and not p['annotation_ids'] and not p['approval_ids'],'Inventory role changed')
                inventory=ET.fromstring(p['text'])
                require(inventory.tag=='source-text-inventory' and [(n.get('ref'),n.get('label'),n.text) for n in inventory]==[
                    (t['self_ref'],t['label'],t['text']) for t in base['evidence']['source_text_items']], 'Text inventory changed')
                continue
            require(p['role']==('quarantine' if blocked else 'table-candidate'),'Retrieval/quarantine role changed')
            ref=p['table_ref']; rows=p['rows']; page=152 if ref=='#/tables/0' else 153
            require(ref==summary['table_ref'] and rows==summary['rows'] and
                    p['original_pdf_pages']==[page] and p['excerpt_pages']==[page-151],'Fragment page/row anchor changed')
            ids,approvals=check_xml(p['text'],ref,rows,blocked,a,tables)
            require(ids==p['annotation_ids']==[n['id'] for n in summary['note_links']] and
                    approvals==p['approval_ids']==summary['approval_ids'],'Annotation metadata changed')
            if blocked: require(not ids,'Quarantine carries approved note links')
            else: seen_links+=ids
            coverage.extend((ref,r) for r in rows)
        require(len(coverage)==len(set(coverage)) and set(coverage)==expected[blocked],
                'Primary/quarantine row partition changed')
        for ref in tables:
            observed=[r for t,r in coverage if t==ref]
            require(observed==sorted(observed),'Source row order changed')
        for ref,t in tables.items():
            atomic=[list(range(s['row'],s['row']+s['rows'])) for s in t['spans'] if s['rows']>1]
            atomic += [g['rows'] for g in a['row_groups'] if g['table_ref']==ref]
            for group in atomic:
                if expected[blocked].intersection((ref,r) for r in group):
                    require(any(p.get('table_ref')==ref and set(group)<=set(p.get('rows',[])) for p in parts),
                            'Atomic span/group split')
        k0=e[bucket+'_K0']; root=ET.fromstring(k0); path=prefix+'K0.xml'; control=card['K0_controls'][path]
        require(root.tag=='reviewed-document' and root.attrib=={'version':'2','diagnostic':'true','quarantined':str(blocked).lower()} and
                text_digest(k0)==control['sha256'],'K0 fingerprint/scope changed')
        require(len(root.findall('segment-boundary'))==(0 if blocked else 1),'K0 segment boundary changed')
        if not blocked:
            require(ET.tostring(root.find('source-text-inventory'))==ET.tostring(inventory),'K0 inventory changed')
        else:
            require(root.find('source-text-inventory') is None,'Quarantine inventory scope changed')
        pairs=[]; k0_links=[]
        require([n.find('table').get('ref') for n in root.findall('./reviewed-tables')]==
                (['#/tables/0'] if blocked else ['#/tables/0','#/tables/1']),'K0 segment order changed')
        for node in root.findall('./reviewed-tables'):
            table=node.find('table'); ref=table.get('ref'); rows=[int(r.get('id')) for r in table.findall('./body/row')]
            require(rows==sorted(r for t,r in expected[blocked] if t==ref),'K0 source row order changed')
            ids,_=check_xml(ET.tostring(node,encoding='unicode'),ref,rows,blocked,a,tables)
            k0_links+=ids; pairs.extend((ref,r) for r in rows)
        require(len(pairs)==len(set(pairs))==control['data_rows'] and set(pairs)==expected[blocked], 'K0 partition changed')
        require(len(k0_links)==control['note_links']==(0 if blocked else 15) and len(set(k0_links))==len(k0_links),
                'K0 note coverage changed')
        all_files[path]=text_digest(k0)
        all_files[prefix+'K800/chunks.json']=local_digest(parts)
    require(len(seen_links)==len(set(seen_links))==15 and set(seen_links)=={b['id'] for b in a['note_bindings']},
            'Missing/duplicated note binding')
    all_files['metrics.json']=local_digest(card['metrics'])
    require({n.replace('\\','/'):v for n,v in payload['chunk_manifest']['files'].items()}==all_files,
            'Original output manifest/file hashes changed')


def verify(package=PACKAGE, annotated_run=None, chunks_run=None):
    package=Path(package)
    require({p.name for p in package.iterdir()}==FILES|{'manifest.json'},'Package inventory changed')
    m=read(package/'manifest.json')
    require(set(m['files'])==FILES and set(m['supporting_files'])==SUPPORT and set(m['dependencies'])==DEPENDENCIES,
            'Manifest inventory changed')
    for key,root in [('files',package),('supporting_files',ROOT),('dependencies',ROOT)]:
        for name,value in m[key].items(): require(file_digest(root/name)==value,f'{key} digest changed: {name}')
    verify_base()
    base=read(BASE_PACKAGE/'cards.json'); base_review=read(BASE_PACKAGE/'review.json'); base_events=read(BASE_PACKAGE/'events.json')
    require(m['source']=={'pdf_sha256':PDF_SHA,'document_sha256':DOCUMENT_SHA,
            'source_map':read(BASE_PACKAGE/'manifest.json')['source']['source_map']},'Package source mapping changed')
    payload=read(package/'cards.json'); card=payload['card']; a=payload['annotations']
    journal=read(package/'events.json'); final=read(package/'review.json'); lineage=m['lineage']
    require(m['counts']==COUNTS and m['publication_allowed'] is False and m['production_ready'] is False,'Counts/approval scope changed')
    require(card['card_id']==CID and card['status']=='pending_human_review' and card['human_approved'] is False and not card['decisions'],
            'Frozen card was promoted')
    require(local_digest(card)==lineage['card_sha256'] and canonical(card)==m['canonical_card'],'Original card changed')
    require(canonical(payload)==m['canonical_payload'],'Selected v2 evidence changed')
    require(card['document_sha256']==DOCUMENT_SHA and card['annotations_sha256']==local_digest(a)==lineage['annotations_sha256'],
            'Source/annotation binding changed')
    art=payload['artifact_manifest']; chunks=payload['chunk_manifest']
    require(local_digest(art)==card['source_artifact_manifest_sha256']==lineage['artifact_manifest_sha256'] and
            local_digest(chunks)==card['chunk_manifest_sha256']==lineage['chunk_manifest_sha256'], 'Original manifests changed')
    require(art['document_sha256']==chunks['document_sha256']==DOCUMENT_SHA and
            art['annotations_sha256']==chunks['annotations_sha256']==local_digest(a) and
            chunks['source_artifact_manifest_sha256']==local_digest(art),'Artifact/chunk chain changed')
    parent_manifest=windows_digest(BASE_PACKAGE/'manifest.json')
    require(art['source_package_manifest_sha256']==chunks['source_package_manifest_sha256']==parent_manifest,'Parent package binding changed')
    require(art['files']=={'annotations.json':local_digest(a),'document.json':DOCUMENT_SHA,
        'events.json':windows_digest(BASE_PACKAGE/'events.json'),'review.json':windows_digest(BASE_PACKAGE/'review.json'),
        'source-package-manifest.json':parent_manifest}, 'Copied source artifact binding changed')
    require(art['implementation_sha256']==file_digest(ROOT/'experiments/cytiva/apply_reviewed_tables.py') and
            all(file_digest(ROOT/n.replace('\\','/'))==h for n,h in chunks['implementation'].items()),
            'Reviewed implementation changed')
    for manifest in (art,chunks):
        require(manifest['human_approved'] is manifest['production_ready'] is manifest['publication_allowed'] is False
                and manifest['annotations_human_validated'] is True,'Historical output scope changed')
    check_annotations(payload,base,base_review,base_events)
    check_evidence(payload,base)
    initial=journal['initial_review']; event=journal['event']; d=event['decision']
    require(local_digest(initial)==lineage['initial_state_sha256'] and event['base_review_file_sha256']==local_digest(initial),
            'Initial state changed')
    require(local_digest(event)==lineage['event_sha256'],'Original event/quotation changed')
    require(event['event_id']=='001-'+CID and d['card_id']==CID and d['decision']=='validated_with_reservation' and
            d['reviewable_sha256']==event['reviewable_sha256']==local_digest(card) and
            d['reservations']==card['reservations'] and bool(d['reservations']),'Decision scope/reservations changed')
    require(event['source_document_sha256']==DOCUMENT_SHA and event['annotations_sha256']==local_digest(a) and
            event['chunk_manifest_sha256']==local_digest(chunks) and event['source_artifact_manifest_sha256']==local_digest(art),
            'Decision artifact binding changed')
    require(bool(d['original_human_message']) and '\ufffd' not in d['original_human_message'],'Damaged original quotation')
    state=deepcopy(initial)
    require(state['cards']=={CID:{'reviewable_sha256':local_digest(card),'decision':'pending'}},'Initial card changed')
    state['cards'][CID].update(decision=d['decision'],event_file='001-'+CID+'.json',event_sha256=local_digest(event),
        human_approved_for_observed_conservation=True,approved_scope=d['approved_scope'],reservations=deepcopy(d['reservations']))
    state.update(review_status='completed_with_reservations',
        scope='Completed v2 observed-conservation review only; the six earlier source/documentary decisions remain unchanged.',
        review_counts={'cards':1,'validated_with_reservation':1,'pending':0},preserved_earlier_documentary_decisions=6,
        approved_note_bindings_conserved=15,primary_rows=40,quarantined_rows={'#/tables/0':[1,9,13]})
    require(state==final and local_digest(final)==lineage['final_state_sha256'],'Final state changed')
    require(final['human_approved'] is final['publication_allowed'] is final['production_ready'] is False,'Blanket approval changed')
    text=json.dumps([payload,journal,final,m],ensure_ascii=False)
    require(not re.search(r'(?i)[a-z]:[\\/]|data:image/|"(?:api_key|password)"',text),'Private paths/assets/secrets included')
    if annotated_run is not None:
        run=Path(annotated_run)
        require(hashlib.sha256((run/'document.json').read_bytes()).hexdigest()==DOCUMENT_SHA,'Wrong annotated document')
        require(read(run/'annotations.json')==a and read(run/'manifest.json')==art,'Wrong annotated artifact')
        require({p.name for p in run.iterdir()}==set(art['files'])|{'manifest.json'},'Wrong annotated artifact inventory')
        require(hashlib.sha256((run/'manifest.json').read_bytes()).hexdigest()==local_digest(art),'Wrong artifact manifest bytes')
        for name,h in art['files'].items():
            require(hashlib.sha256((run/name).read_bytes()).hexdigest()==h,'Wrong annotated artifact bytes')
    if chunks_run is not None:
        run=Path(chunks_run)
        require(read(run/'manifest.json')==chunks,'Wrong chunks manifest')
        for name,h in chunks['files'].items():
            require(hashlib.sha256((run/name.replace('\\','/')).read_bytes()).hexdigest()==h,'Wrong local chunk bytes')
    return {'status':'passed',**COUNTS,'prior_review_verified':True,'event_chain_replayed':True,
        'annotated_run_replayed':annotated_run is not None,'chunks_run_replayed':chunks_run is not None,
        'remaining_quarantine_rows':[1,9,13],'production_ready':False,'publication_allowed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=PACKAGE)
    parser.add_argument('--annotated-run',type=Path)
    parser.add_argument('--chunks-run',type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(verify(args.package,args.annotated_run,args.chunks_run)))
    except (ValueError,KeyError,TypeError,IndexError,OSError,ET.ParseError,AttributeError) as error:
        parser.exit(1,f'Package verification failed: {error}\n')


if __name__=='__main__':
    main()
