"""Real selector-backed documentary handoff, not a new scientific benchmark."""
from copy import deepcopy
from http.server import ThreadingHTTPServer
import http.client
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

from demo import documentary as subject
from demo.documentary_preview import handler_for, source_html
from experiments.cytiva.free_text_v03_freeze import verify

ROOT = Path(__file__).resolve().parents[1]


def request(product='mabselect', context='precipitated_substances', items=None):
    return {'kind':'reviewed_serving_request/v1','request_id':'test-request','language':'en',
            'tasks':[{'task_id':'A','product':product,'deposit_context':context,
                      'requested_items':items or ['cleaning_options'],'excluded_items':[]}]}


class DocumentaryHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = subject.Handoff(preview=True)

    def test_six_accepted_examples_use_actual_selector(self):
        examples=json.loads((ROOT/'docs/technical/reviewed-dossier-serving-interface-examples-v01.json').read_text(encoding='utf-8'))
        with patch('socket.socket', side_effect=AssertionError('No external connection in selector handoff')):
            for case in examples['examples']:
                with self.subTest(case=case['id']):
                    out=self.service.evaluate(case['request'])
                    if case['id']=='SX06':
                        self.assertEqual(out['errors'][0]['code'],'unknown_authority_field');continue
                    self.assertEqual(out['status'],case['expected']['status'])
                    for expected in case['expected'].get('item_states',[]):
                        row=next(x for x in out['items'] if x['task_id']==expected['task_id'] and x['requested_item']==expected['item'])
                        self.assertEqual(row['state'],expected['state'])
                    if 'bundle_keys' in case['expected']:
                        self.assertEqual([x['bundle_key'] for x in out['context']['bundles']],case['expected']['bundle_keys'])

    def test_selector_called_once_per_task_and_preserves_input(self):
        value=request(context='hydrophobic_deposits',items=['cleaning_options','pressure_limit']);before=deepcopy(value)
        with patch.object(subject.selector,'evaluate',wraps=subject.selector.evaluate) as select:
            out=self.service.evaluate(value)
        self.assertEqual(select.call_count,1);self.assertEqual(value,before);self.assertEqual(out['status'],'partial')
        self.assertNotIn('E166-P',[p['source_id'] for p in out['context']['passages']])

    def test_bundle_refs_resolve_exact_product_for_each_task(self):
        value=request();value['tasks'].append(dict(request('sure')['tasks'][0],task_id='B'))
        out=self.service.evaluate(value)
        for task,item in zip(value['tasks'],out['items']):
            bundles=[out['context']['bundles'][int(ref.rsplit('/',1)[1])] for ref in item['bundle_refs']]
            self.assertEqual([b['bundle_key'] for b in bundles],item['bundle_keys'])
            self.assertTrue(all(b['product']==task['product'] for b in bundles))
            self.assertEqual(item['field_origins'][:2],[{'field':f,'request_pointer':f'/tasks/{value["tasks"].index(task)}/{f}'} for f in ('product','deposit_context')])
        self.assertNotEqual(out['items'][0]['bundle_refs'][0],out['items'][1]['bundle_refs'][0])

    def test_clarification_refs_are_explicit_and_shared_only_for_identical_context(self):
        value=request('unknown','unknown');value['tasks'].append(dict(value['tasks'][0],task_id='B'))
        value['tasks'].append(dict(request('sure','unknown')['tasks'][0],task_id='C'))
        out=self.service.evaluate(value)
        self.assertEqual(out['items'][0]['bundle_refs'],out['items'][1]['bundle_refs'])
        self.assertNotEqual(out['items'][0]['bundle_refs'],out['items'][2]['bundle_refs'])
        for item in out['items']:
            self.assertEqual(item['state'],'needs_clarification');self.assertEqual(item['bundle_keys'],[])
            self.assertEqual(len(item['bundle_refs']),1)
            bundle=out['context']['bundles'][int(item['bundle_refs'][0].rsplit('/',1)[1])]
            self.assertEqual(bundle['review_scope'],'Q09')
            self.assertTrue(all(not o['steps'] for o in bundle['options']))

    def test_unexpected_selector_failure_is_task_local_logged_without_payload_and_not_retried(self):
        value=request(items=['cleaning_options','pressure_limit'])
        value['tasks'].append(dict(request('sure')['tasks'][0],task_id='B'))
        original=subject.selector.evaluate
        def failed(payload):
            if payload['product']=='mabselect':raise RuntimeError('private-error-content')
            return original(payload)
        with patch.object(subject.selector,'evaluate',side_effect=failed) as select,self.assertLogs(subject.LOGGER,level='ERROR') as logs:
            out=self.service.evaluate(value)
        self.assertEqual(select.call_count,2);self.assertEqual(out['status'],'partial')
        self.assertEqual([i['state'] for i in out['items']],['unavailable','unavailable','supported'])
        self.assertEqual(out['coverage']['unavailable'],2)
        self.assertTrue(all(not i['bundle_refs'] for i in out['items'][:2]))
        self.assertIn('RuntimeError',''.join(logs.output))
        self.assertNotIn('private-error-content',json.dumps(out)+''.join(logs.output))
        self.assertTrue(all(b['product']=='sure' for b in out['context']['bundles']))

    def test_unexpected_item_failure_does_not_deliver_partial_alternative_set(self):
        original=self.service._bundle
        def failed(scope,task,selected):
            if scope=='N07':raise RuntimeError('private assembly detail')
            return original(scope,task,selected)
        value=request(context='hydrophobic_deposits');value['tasks'].append(dict(request()['tasks'][0],task_id='B'))
        with patch.object(self.service,'_bundle',side_effect=failed),self.assertLogs(subject.LOGGER,level='ERROR'):
            out=self.service.evaluate(value)
        self.assertEqual(out['status'],'partial');self.assertEqual(out['items'][0]['state'],'unavailable')
        self.assertEqual(out['items'][0]['bundle_refs'],[])
        self.assertEqual([b['review_scope'] for b in out['context']['bundles']],['Q05'])
        self.assertEqual(out['items'][1]['bundle_refs'],['/context/bundles/0'])

    def test_original_immediate_force_and_link_are_preserved_for_all_followup_washes(self):
        for product,context in [('mabselect','precipitated_substances'),('sure','precipitated_substances'),('sure_lx','hydrophobic_deposits')]:
            out=self.service.evaluate(request(product,context))
            for bundle in out['context']['bundles']:
                for option in bundle['options']:
                    for previous,step in zip(option['steps'],option['steps'][1:]):
                        if step['phase']=='followup_wash':
                            self.assertIn(step['force_text'],step['wording'])
                            self.assertIn('immediately',step['force_text'].lower())
                            self.assertEqual(step['immediate_after_step_id'],previous['step_id'])
                            self.assertIn(step['wording'],self.service._passages[step['source_ids'][0]]['quote'])

    def test_full_quotes_review_messages_reservations_and_offsets_preserved(self):
        out=self.service.evaluate(request(context='hydrophobic_deposits'))
        for p in out['context']['passages']:
            original=self.service._passages[p['source_id']]
            for key in ('quote','quote_sha256','page_text_start','page_text_end','pdf_page_1based','pdf_page_index_0based'):
                self.assertEqual(p[key],original[key])
        for d in out['context']['reviews']:
            original=self.service._decisions[d['review_id']]
            self.assertEqual(d['original_human_message'],original['original_human_message'])
            self.assertEqual(d['reservations'],original['reservations'])
            self.assertEqual(d['evidence_record_sha256'],original['evidence_sha256'])
        solvent=next(b for b in out['context']['bundles'] if b['review_scope']=='N07')
        self.assertTrue(any('lower flow rate' in w['wording'] for w in solvent['options'][0]['warnings']))
        self.assertTrue(any('increasing gradients' in w['wording'] for w in solvent['options'][0]['warnings']))

    def test_restricted_sequence_never_transfers_to_plain_product(self):
        out=self.service.evaluate(request(items=['restricted_sequence']))
        self.assertEqual(out['status'],'abstained');self.assertEqual(out['context']['bundles'],[])
        out=self.service.evaluate(request('sure',items=['restricted_sequence']))
        self.assertEqual(out['status'],'supported');self.assertEqual([b['review_scope'] for b in out['context']['bundles']],['Q06'])
        steps=out['context']['bundles'][0]['options'][0]['steps']
        self.assertEqual([s['phase'] for s in steps],['conditioning','cleaning','followup_wash'])
        self.assertEqual(''.join(s['wording'] for s in steps),self.service._passages['E167-S']['quote'])

    def test_clarification_keeps_both_missing_fields_and_independent_task(self):
        value=request('unknown','unknown');value['tasks'].append(dict(request()['tasks'][0],task_id='B'))
        out=self.service.evaluate(value);self.assertEqual(out['status'],'partial')
        self.assertEqual(out['items'][0]['clarification_targets'],['product','deposit_context'])
        self.assertEqual(out['items'][1]['state'],'supported')
        for b in out['context']['bundles']:
            if b['review_scope']=='Q09':self.assertTrue(all(not o['steps'] for o in b['options']))

    def test_other_product_abstains_without_incompatibility_claim(self):
        out=self.service.evaluate(request('other'))
        self.assertEqual(out['status'],'abstained');self.assertEqual(out['items'][0]['reason'],'outside_release_scope')
        self.assertEqual(out['context']['bundles'],[])

    def test_invalid_input_and_duplicate_task_ids_never_reach_selector(self):
        values=[]
        for product in (False,0):values.append(request(product))
        value=request();value['tasks'][0].pop('product');values.append(value)
        value=request();value['tasks'].append(dict(value['tasks'][0],product='sure'));values.append(value)
        value=request();value['release_id']='caller-approval';values.append(value)
        value=request();value['tasks'][0]['input_label']='\ud800';values.append(value)
        with patch.object(subject.selector,'evaluate') as select:
            for value in values:self.assertEqual(self.service.evaluate(value)['kind'],'reviewed_serving_validation_error/v1')
            select.assert_not_called()

    def test_exclusions_take_precedence_without_lookup(self):
        value=request(items=['pressure_limit']);value['tasks'][0]['excluded_items']=['pressure_limit']
        with patch.object(subject.selector,'evaluate') as select:
            out=self.service.evaluate(value);select.assert_not_called()
        self.assertEqual(out['response_reason'],'no_requested_item');self.assertEqual(out['coverage']['supported'],0)
        self.assertEqual(out['items'][0]['bundle_refs'],[])
        self.assertIn({'field':'exclusion','request_pointer':'/tasks/0/excluded_items/0'},out['items'][0]['field_origins'])

    def test_budget_exact_boundary_and_one_byte_overflow_keep_atomic_alternatives(self):
        full=self.service.evaluate(request('sure'));size=full['context_measure']['delivered_bytes']
        exact=subject.Handoff(preview=True,context_bytes=size).evaluate(request('sure'))
        self.assertEqual(exact['status'],'supported')
        over=subject.Handoff(preview=True,context_bytes=size-1).evaluate(request('sure'))
        self.assertEqual(over['status'],'unavailable');self.assertEqual(over['items'][0]['reason'],'context_budget_incomplete')
        self.assertEqual(over['context']['bundles'],[])

    def test_repeated_tasks_deduplicate_sources_and_do_not_mutate_registry(self):
        single=self.service.evaluate(request());value=request();value['tasks'].append(dict(value['tasks'][0],task_id='B'))
        out=self.service.evaluate(value)
        self.assertEqual(out['context_measure']['delivered_bytes'],single['context_measure']['delivered_bytes'])
        self.assertEqual([x['task_id'] for x in out['items']],['A','B'])
        out['context']['bundles'][0]['required_source_ids'].clear()
        self.assertEqual(len(subject.selector.REQUIRED['Q05']),3)
        self.assertEqual(self.service.evaluate(request())['status'],'supported')

    def test_missing_warning_blocks_its_item_but_not_independent_product_task(self):
        original=subject.selector.evaluate
        def missing(payload):
            out=original(payload)
            if payload['deposit_context']=='hydrophobic_deposits':out['passages']=[p for p in out['passages'] if p['id']!='E167-W']
            return out
        value=request(context='hydrophobic_deposits');value['tasks'].append(dict(request()['tasks'][0],task_id='B'))
        with patch.object(subject.selector,'evaluate',side_effect=missing):out=self.service.evaluate(value)
        self.assertEqual(out['status'],'partial');self.assertEqual(out['items'][0]['state'],'unavailable')
        self.assertEqual(out['items'][1]['state'],'supported')
        self.assertNotIn('N07',[b['review_scope'] for b in out['context']['bundles']])

    def test_changed_authority_before_or_during_request_clears_all_context(self):
        with patch.object(self.service,'_check',side_effect=[None,ValueError('changed')]):out=self.service.evaluate(request())
        self.assertEqual(out['status'],'unavailable');self.assertEqual(out['response_reason'],'invalid_authority')
        self.assertEqual(out['context']['passages'],[])
        original=subject.digest
        def altered(path):return 'changed' if str(path).endswith('reviewed-dossier-serving-decisions-v01.json') else original(path)
        with patch.object(subject,'digest',side_effect=altered):out=self.service.evaluate(request())
        self.assertEqual(out['status'],'unavailable');self.assertEqual(out['context']['bundles'],[])

    def test_withdrawal_is_not_source_absence_and_never_silently_selects_one_alternative(self):
        held=subject.Handoff(preview=True,withdrawn=[subject.KEYS['N07']])
        out=held.evaluate(request(context='hydrophobic_deposits'))
        self.assertEqual(out['items'][0]['state'],'quarantined');self.assertEqual(out['context']['bundles'],[])
        self.assertIsNone(held.source(held.release_id,'E167-W')['passage'])

    def test_unactivated_default_never_evaluates_a_procedure(self):
        service=subject.Handoff()
        with patch.object(subject.selector,'evaluate') as select:out=service.evaluate(request());select.assert_not_called()
        self.assertEqual(out['response_reason'],'release_not_activated');self.assertIsNone(out['release_id'])

    def test_citations_are_version_bound_and_unregistered_sources_are_not_admitted(self):
        out=self.service.evaluate(request(context='hydrophobic_deposits'))
        for ref in out['citation_refs']:
            view=self.service.source(ref['release_id'],ref['source_id']);self.assertEqual(view['status'],'available')
            self.assertIn(ref['source_id'],ref['href']);self.assertEqual(view['passage']['pdf_page_1based'],167)
        for pid in ('E118-I','E121-EQ','../secret','E166-P'):
            with self.assertRaises(KeyError):self.service.source(self.service.release_id,pid)
        with self.assertRaises(KeyError):self.service.source('another-release','E167-W')

    def test_source_html_escapes_data_and_frozen_v03_stays_valid(self):
        view=self.service.source(self.service.release_id,'E167-W');view['passage']['quote']='<script>alert(1)</script>'
        html=source_html(view).decode('utf-8');self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html)
        self.assertEqual(verify(environment=True)['status'],'frozen')


class DocumentaryHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service=subject.Handoff(preview=True);cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(cls.service));cls.server.daemon_threads=True
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=5)

    def call(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        try:
            c.request(method,path,body,headers or {});r=c.getresponse();return r.status,r.read()
        finally:c.close()

    def test_real_http_handoff_and_source_page(self):
        status,raw=self.call('POST','/api/reviewed/v1/evaluate',json.dumps(request(context='hydrophobic_deposits',items=['cleaning_options','pressure_limit'])),{'Content-Type':'application/json'})
        self.assertEqual(status,200);out=json.loads(raw);self.assertEqual(out['status'],'partial')
        ref=next(x for x in out['citation_refs'] if x['source_id']=='E167-W')
        status,page=self.call('GET',ref['href']);self.assertEqual(status,200)
        self.assertIn(b'PDF page 167',page);self.assertIn(b'lower flow rate',page)
        self.assertIn(b'Original decision and bindings',page)

    def test_http_unexpected_selector_error_returns_documentary_unavailable(self):
        with patch.object(subject.selector,'evaluate',side_effect=RuntimeError('secret detail')),self.assertLogs(subject.LOGGER,level='ERROR'):
            status,raw=self.call('POST','/api/reviewed/v1/evaluate',json.dumps(request()),{'Content-Type':'application/json'})
        out=json.loads(raw);self.assertEqual(status,200);self.assertEqual(out['status'],'unavailable')
        self.assertEqual(out['items'][0]['state'],'unavailable');self.assertEqual(out['context']['bundles'],[])
        self.assertNotIn(b'secret detail',raw)

    def test_origin_body_limit_duplicate_json_and_path_controls(self):
        status,_=self.call('POST','/api/reviewed/v1/evaluate','{}',{'Content-Type':'application/json','Origin':'https://other.example'})
        self.assertEqual(status,403)
        for body in ('{"kind":1,"kind":2}', 'NaN',' '*32769):
            status,raw=self.call('POST','/api/reviewed/v1/evaluate',body,{'Content-Type':'application/json'})
            self.assertEqual(status,400);self.assertIn(b'validation_error',raw)
        self.assertEqual(self.call('GET','/reviewed/v1/releases/x/sources/../../secret')[0],404)
        self.assertEqual(self.call('GET','/',headers={'Host':'other.example'})[0],403)
