"""Prepare/check/replay a nonactivated registry candidate. No activation command."""
import argparse
from contextlib import ExitStack
import json
from pathlib import Path
from unittest.mock import patch

from serving.local_registry import Registry, prepare, ROOT, read, sha
from experiments.cytiva import mabselect_handoff_freeze as freeze


def check(data_root,release_id):
    registry=Registry(data_root)
    with registry.lock:state=registry._snapshot(candidate=release_id)
    return {'release_id':release_id,'stage':state['release']['stage'],
            'withdrawal_decision':'proposed_not_approved','withdrawal_entries':len(state['withdrawals']['entries']),
            'bundles':len(state['mapping']['entries']),'sources':len(state['sources']['passages']),
            'reviews':len(state['sources']['reviews']),'dependencies':len(state['release']['dependencies']),
            'authority_digest':state['token'],'active_pointer_exists':(Path(data_root)/'active.json').exists(),
            'durable_head_exists':(Path(data_root)/'authority-log').exists(),
            'serving_activated':False,'freeze':freeze.verify(environment=True)}


def replay(data_root,release_id):
    before=check(data_root,release_id);registry=Registry(data_root);attempts=[]
    def blocked(*_args,**_kwargs):
        attempts.append('socket_operation');raise RuntimeError('No network during candidate replay')
    rows=[]
    with ExitStack() as stack:
        for name in ('socket.socket','socket.create_connection','socket.getaddrinfo'):
            stack.enter_context(patch(name,side_effect=blocked))
        for case in read(ROOT/freeze.EXAMPLES)['examples']:
            out=registry.evaluate(case['request'],candidate=release_id)
            freeze.check_case(case,out)
            citations=[]
            for ref in out.get('citation_refs',[]):
                view=registry.source(ref['release_id'],ref['source_id'],candidate=release_id)
                expected=next(p for p in out['context']['passages'] if p['source_id']==ref['source_id'])
                if view['status']!='available' or view['passage']!=expected:raise ValueError('Citation mismatch')
                citations.append({'source_id':ref['source_id'],'status':view['status'],'quote_sha256':expected['quote_sha256']})
            rows.append({'case_id':case['id'],'status':'passed','request':case['request'],'response':out,'citations':citations})
    if attempts or check(data_root,release_id)!=before:raise ValueError('Candidate changed or attempted network')
    return {'id':release_id+'-candidate-replay-v01','candidate':before,'status':'passed',
            'scope':'accepted_examples_not_independent_answer_or_scientific_validation',
            'registry_code_sha256_lf':sha((ROOT/'serving/local_registry.py').read_bytes()),
            'network_attempts':attempts,'llm_calls':0,'paid_api_calls':0,'serving_activated':False,'cases':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',type=Path,default=ROOT/'serving-data')
    parser.add_argument('--release-id',default='mabselect-local-v02')
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--replay',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and not args.replay:parser.error('--output requires --replay')
    try:
        if args.output and args.output.exists():raise ValueError('Output exists; nothing overwritten')
        if args.prepare:prepare(args.data_root,args.release_id)
        result=replay(args.data_root,args.release_id) if args.replay else check(args.data_root,args.release_id)
        if args.output:
            with args.output.open('x',encoding='utf-8',newline='\n') as out:out.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='cases'}|({'case_results':{r['case_id']:r['status'] for r in result['cases']}} if args.replay else {}),indent=2))
    except (ValueError,OSError,KeyError,RuntimeError) as error:parser.exit(1,'Candidate check failed: '+str(error)+'\n')


if __name__=='__main__':main()
