"""Integrate the reviewed pages 152-153 annotations into new offline artifacts.

No conversion, LLM, database or production ingestion is invoked. Original JSON,
review packages, serializers and old chunk outputs remain unchanged.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET

from experiments.cytiva.visual_validation import ROOT, digest, dump, fresh, network_guard
from experiments.cytiva.verify_pages152153_package import PACKAGE, DOCUMENT_SHA, PDF_SHA, local_digest, read, verify
from experiments.cytiva.repair_table152 import inventory_xml
from ingestion.reviewed_table_chunking import chunk_reviewed, partitions, validate_reviewed

CARDS = {'g1':'P152-HiTrap-HiScreen','c1':'P152-153-continuity',
         'n1':'P152-N1','n2':'P152-N2','n3':'P153-N3'}
LIMITS = {
    'g1':'Keep the second product cell blank. Grouping is a documentary annotation.',
    'c1':'Documentary continuation only; do not inherit note scope across pages.',
    'n1':'Approximately 20 purifications with supplied buffers using a syringe; no guaranteed count or column-reuse authorization.',
    'n2':'Material description for the marked entries only; no handling protocol inferred.',
    'n3':'Preserve N/A; do not infer zero, an expansion of N/A or a numerical capacity.'}


def build_annotations(payload, review, journal):
    """Called only after package verification; no inference or cell filling."""
    if review['human_approved'] is not False or review['publication_allowed'] is not False:
        raise ValueError('No blanket or publication approval may be inferred')
    events = {e['decision']['card_id']:e for e in journal['events']}
    approvals = {}
    for aid,cid in CARDS.items():
        state = review['cards'][cid]; event = events[cid]
        if state['decision'] != 'validated_with_reservation' or state['event_sha256'] != local_digest(event):
            raise ValueError('Missing hash-bound documentary approval')
        approvals[aid] = {'card_id':cid,'event_sha256':local_digest(event),
            'reviewable_sha256':state['reviewable_sha256'],
            'original_human_message':event['decision']['original_human_message'],
            'reservations':deepcopy(state['reservations']),'serialization_limit':LIMITS[aid]}
    continuation = deepcopy(review['cards'][CARDS['c1']]['approved_annotation'])
    if not continuation['human_approved'] or continuation['native_converter_relation']:
        raise ValueError('Expected a reviewed, non-native continuation')
    continuation['approval'] = 'c1'
    bindings = []
    for aid,expected in [('n1',1),('n2',2),('n3',12)]:
        selected = review['cards'][CARDS[aid]]['approved_cell_note_bindings']
        if len(selected) != expected:
            raise ValueError('Approved note scope changed')
        for binding in selected:
            if binding['human_approved_for_documentary_scope'] is not True:
                raise ValueError('Unapproved note binding')
            bindings.append({'id':f'b{len(bindings)+1:02}','approval':aid,
                'table_ref':binding['table_ref'],'row':binding['grid_row_0based'],
                'col':binding['column_0based'],'note_ref':binding['note_ref'],
                'source_cell':deepcopy(binding['source_cell']),
                'original_pdf_page_1based':binding['original_pdf_page_1based'],
                'excerpt_page_1based':binding['excerpt_page_1based']})
    texts = {t['self_ref']:t for t in payload['evidence']['source_text_items']}
    return {'schema_version':1,'format':'reviewed-table-annotations-v1','document_sha256':DOCUMENT_SHA,
        'source_pdf_sha256':PDF_SHA,'human_approved':False,'annotations_human_validated':True,
        'approval_scope':'documentary_annotations_only','publication_allowed':False,'production_ready':False,
        'caption':texts['#/texts/2']['text'],'continuation':continuation,
        'row_groups':[{'table_ref':'#/tables/0','rows':[19,20],'approval':'g1',
            'source_blank_product_cell':{'row':20,'col':0},'raw_source_rowspan_created':False}],
        'note_bindings':bindings,'notes':{ref:deepcopy(texts[ref]) for ref in ['#/texts/3','#/texts/4','#/texts/6']},
        'approvals':approvals,'quarantine':{'#/tables/0':[1,9,13],'#/tables/1':[]},
        'remaining_reservations':deepcopy(review['cards']['P152-153-chunking']['reservations'])}


def validate_cells(document, annotations):
    if annotations['quarantine'] != {'#/tables/0':[1,9,13],'#/tables/1':[]}:
        raise ValueError('The three unresolved variant rows must remain quarantined')
    for binding in annotations['note_bindings']:
        table = next(t for t in document['tables'] if t['self_ref']==binding['table_ref'])
        if table['data']['grid'][binding['row']][binding['col']] != binding['source_cell']:
            raise ValueError('Approved binding source cell changed')
    if document['tables'][0]['data']['grid'][20][0]['text'] != '':
        raise ValueError('Blank product cell was filled')


def prepare(args):
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    attempts = network_guard()
    verify(args.package,args.source)
    payload = read(args.package/'cards.json'); review = read(args.package/'review.json')
    journal = read(args.package/'events.json')
    annotations = build_annotations(payload,review,journal)
    document = read(args.source); validate_cells(document,annotations)
    fresh(args.output)
    (args.output/'document.json').write_bytes(args.source.read_bytes())
    dump(args.output/'annotations.json',annotations)
    for name in ('review.json','events.json'):
        (args.output/name).write_bytes((args.package/name).read_bytes())
    (args.output/'source-package-manifest.json').write_bytes((args.package/'manifest.json').read_bytes())
    dump(args.output/'manifest.json',{'format':'reviewed-table-artifact-v1',
        'status':'annotations_integrated_pending_new_chunk_review','document_sha256':digest(args.source),
        'source_package_manifest_sha256':digest(args.package/'manifest.json'),
        'annotations_sha256':digest(args.output/'annotations.json'),
        'annotations_human_validated':True,'human_approved':False,'production_ready':False,'publication_allowed':False,
        'files':{p.name:digest(p) for p in args.output.iterdir() if p.is_file()},
        'implementation_sha256':digest(Path(__file__)), 'network_attempts':attempts,'llm_calls':0,'api_calls':0})


def load_artifact(run, package):
    manifest = read(run/'manifest.json')
    allowed = {'document.json','annotations.json','review.json','events.json','source-package-manifest.json'}
    if set(manifest['files']) != allowed or {p.name for p in run.iterdir()} != allowed|{'manifest.json'}:
        raise ValueError('Annotated artifact inventory mismatch')
    for name,expected in manifest['files'].items():
        if digest(run/name) != expected:
            raise ValueError('Annotated artifact hash mismatch')
    verify(package,run/'document.json')
    if digest(package/'manifest.json') != manifest['source_package_manifest_sha256'] or (
            digest(run/'source-package-manifest.json') != manifest['source_package_manifest_sha256']):
        raise ValueError('Source review package changed')
    for name in ('review.json','events.json'):
        if read(run/name) != read(package/name):
            raise ValueError('Original decisions changed')
    expected = build_annotations(read(package/'cards.json'),read(run/'review.json'),read(run/'events.json'))
    annotations = read(run/'annotations.json')
    if annotations != expected or digest(run/'annotations.json') != manifest['annotations_sha256']:
        raise ValueError('Approved annotation scope changed')
    if any(manifest[k] is not False for k in ('human_approved','production_ready','publication_allowed')):
        raise ValueError('Blanket approval scope changed')
    document = read(run/'document.json'); validate_cells(document,annotations)
    return document,annotations


def execute(args):
    if args.output.exists():
        raise FileExistsError('Outputs are never overwritten')
    start=time.monotonic(); attempts=network_guard()
    document,annotations=load_artifact(args.run,args.package)
    if args.budgets != sorted(set(args.budgets)) or not args.budgets or not set(args.budgets)<={600,800,1400}:
        raise ValueError('Use distinct sorted diagnostic budgets: 600,800,1400')
    import tiktoken
    enc=tiktoken.get_encoding('cl100k_base'); count=lambda t:len(enc.encode(t))
    inventory=inventory_xml(document)
    outputs={}; metrics={}; controls={}
    for blocked in (False,True):
        fragments=[]
        for table in document['tables']:
            parts=chunk_reviewed(table,annotations,count,10**9,blocked)
            validate_reviewed(table,parts,annotations,count,10**9,blocked)
            if parts: fragments.append(parts[0]['text'])
        controls[blocked]=(f'<reviewed-document version="2" diagnostic="true" quarantined="{str(blocked).lower()}">'
            + (inventory if not blocked else '')
            + '<segment-boundary/>'.join(fragments) + '</reviewed-document>')
        ET.fromstring(controls[blocked])
    for budget in args.budgets:
        if count(inventory)>budget:
            raise ValueError('Inventory exceeds budget; no truncation')
        per_bucket={}
        for blocked in (False,True):
            chunks=[]; checks=[]
            if not blocked:
                chunks.append({'text':inventory,'token_count':count(inventory),'role':'source-inventory-not-retrieval',
                    'quarantined':False,'production_ready':False,'refs':[t['self_ref'] for t in document['texts']],
                    'annotation_ids':[],'approval_ids':[]})
            for table in document['tables']:
                parts=chunk_reviewed(table,annotations,count,budget,blocked)
                checks.append({'table_ref':table['self_ref'],**validate_reviewed(table,parts,annotations,count,budget,blocked)})
                chunks+=parts
            for chunk in chunks:
                chunk.update(document_sha256=digest(args.run/'document.json'),
                    annotations_sha256=digest(args.run/'annotations.json'),
                    human_review_status='new_chunk_conservation_pending',approval_scope='documentary_annotations_only')
            per_bucket[blocked]=chunks
            label='quarantine' if blocked else 'primary'; counts=[c['token_count'] for c in chunks]
            metrics[f'{label}_K{budget}']={'chunks':len(chunks),'tokens':counts,'total_tokens':sum(counts),
                'max_tokens':max(counts,default=0),'checks':checks}
        primary_rows=[(c['table_ref'],r) for c in per_bucket[False] if 'table_ref' in c for r in c['rows']]
        blocked_rows=[(c['table_ref'],r) for c in per_bucket[True] for r in c['rows']]
        ids=[aid for c in per_bucket[False] for aid in c['annotation_ids']]
        if len(primary_rows)!=40 or blocked_rows!=[('#/tables/0',r) for r in (1,9,13)] or set(primary_rows)&set(blocked_rows):
            raise ValueError('Quarantine partition changed')
        if not (len(ids)==len(set(ids))==15) or set(ids)!={b['id'] for b in annotations['note_bindings']}:
            raise ValueError('Reviewed note binding coverage changed')
        outputs[budget]=per_bucket
    fresh(args.output)
    for blocked in (False,True):
        folder=args.output/'quarantine' if blocked else args.output
        if blocked: fresh(folder)
        (folder/'K0.xml').write_text(controls[blocked],encoding='utf-8')
        for budget in args.budgets:
            target=folder/f'K{budget}'; fresh(target)
            chunks=outputs[budget][blocked]; dump(target/'chunks.json',chunks)
            for i,chunk in enumerate(chunks):
                (target/f'chunk-{i:03}.xml').write_text(chunk['text'],encoding='utf-8')
    metrics.update(format='reviewed-structural-table-xml-v2',tokenizer='cl100k_base',
        primary_K0_tokens=count(controls[False]),quarantine_K0_tokens=count(controls[True]),
        primary_rows=40,quarantined_rows=3,approved_note_bindings=15,
        seconds_including_imports=round(time.monotonic()-start,3),network_attempts=attempts,llm_calls=0,api_calls=0)
    dump(args.output/'metrics.json',metrics)
    dump(args.output/'manifest.json',{'format':'reviewed-table-chunks-v2','status':'technical_checks_passed_pending_new_chunk_review',
        'source_artifact_manifest_sha256':digest(args.run/'manifest.json'),
        'annotations_sha256':digest(args.run/'annotations.json'),'document_sha256':digest(args.run/'document.json'),
        'source_package_manifest_sha256':digest(args.package/'manifest.json'),
        'annotations_human_validated':True,'human_approved':False,'production_ready':False,'publication_allowed':False,
        'implementation':{str(p.relative_to(ROOT)):digest(p) for p in
            [Path(__file__).resolve(),ROOT/'ingestion/reviewed_table_chunking.py']},
        'files':{str(p.relative_to(args.output)):digest(p) for p in args.output.rglob('*') if p.is_file()}})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare'); p.add_argument('--source',type=Path,required=True)
    p=sub.add_parser('chunk'); p.add_argument('--run',type=Path,required=True)
    p.add_argument('--budgets',type=int,nargs='+',default=[800])
    for cmd in sub.choices.values():
        cmd.add_argument('--package',type=Path,default=PACKAGE)
        cmd.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    {'prepare':prepare,'chunk':execute}[args.command](args)


if __name__=='__main__':
    main()
