"""Local registry lifecycle; approved decisions exist only in disposable fixtures."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from serving import local_registry as subject
from experiments.cytiva.mabselect_handoff_freeze import verify as verify_freeze


def request(product='mabselect',context='precipitated_substances',items=None):
    return {'kind':'reviewed_serving_request/v1','request_id':'registry-test','language':'en',
            'tasks':[{'task_id':'A','product':product,'deposit_context':context,
                      'requested_items':items or ['cleaning_options'],'excluded_items':[]}]}


def replace(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def approve_fixture(folder,*,version=1,entries=None):
    """Synthetic authorization, ONLY inside a TemporaryDirectory; never project data."""
    rid=folder.name;w=subject.read(folder/'withdrawals.json');w['version']=version
    if entries is not None:w['entries']=deepcopy(entries)
    d=subject.read(folder/'withdrawal-decision.json');d['status']='approved'
    d['original_human_message']='SYNTHETIC TEST ONLY: approve this isolated fixture.'
    d['content_sha256']=subject.withdrawal_content(rid,w);replace(folder/'withdrawal-decision.json',d)
    ref=subject.binding(rid+'-withdrawal-decision',folder/'withdrawal-decision.json')
    w['decision_ref']=ref
    for e in w['entries']:
        if e['decision_ref'] is None:e['decision_ref']=ref
    replace(folder/'withdrawals.json',w)
    release=subject.read(folder/'release.json');release['stage']='activated'
    release['withdrawals_ref']=subject.binding('withdrawals',folder/'withdrawals.json')
    decision={'kind':'local_registry_decision/v1','operation':'activate','release_id':rid,
              'status':'approved','validator':'project_user_via_conversation',
              'content_sha256':subject.release_content(release),
              'original_human_message':'SYNTHETIC TEST ONLY: activate this disposable fixture.'}
    replace(folder/'activation-decision.json',decision)
    release['activation_decision_ref']=subject.binding('activation-decision',folder/'activation-decision.json')
    replace(folder/'release.json',release)


def event(folder,kind,id_,*,action='withdraw',number=1):
    data=subject.read(folder/('mapping.json' if kind=='bundle' else 'source-index.json'))
    rows=data['entries'] if kind=='bundle' else data['reviews'] if kind=='review' else data['passages']
    key='bundle_key' if kind=='bundle' else 'review_id' if kind=='review' else 'source_id'
    target=next(row for row in rows if row[key]==id_)
    return {'event_id':'event-'+str(number),'action':action,'target_kind':kind,'target_id':id_,
            'target_release_id':folder.name,'target_sha256':subject.value_sha(target),
            'decision_ref':None,'reason':'Synthetic withdrawal/reinstatement test'}


class LocalRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='registry-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.folder=subject.prepare(self.root,'release-v01')
        self.registry=subject.Registry(self.root)

    def activate_first(self):
        approve_fixture(self.folder);self.registry.activate(self.folder.name)

    def test_preparation_is_staged_proposed_and_never_creates_active_pointer(self):
        self.assertFalse((self.root/'active.json').exists())
        self.assertEqual(subject.read(self.folder/'release.json')['stage'],'staged')
        self.assertEqual(subject.read(self.folder/'withdrawal-decision.json')['status'],'proposed')
        self.assertEqual(self.registry.evaluate(request())['response_reason'],'release_not_activated')
        with self.assertRaises(ValueError):self.registry.activate(self.folder.name)
        self.assertFalse((self.root/'active.json').exists())

    def test_candidate_replays_all_six_accepted_examples_without_sockets(self):
        cases=subject.freeze.read(subject.ROOT/subject.freeze.EXAMPLES)['examples']
        with patch('socket.socket',side_effect=AssertionError('network')):
            for c in cases:
                out=self.registry.evaluate(c['request'],candidate=self.folder.name)
                subject.freeze.check_case(c,out)
                if out['kind']=='reviewed_documentary_bundle/v1':
                    for ref in out['citation_refs']:
                        view=self.registry.source(ref['release_id'],ref['source_id'],candidate=self.folder.name)
                        self.assertEqual(view['status'],'available')
        self.assertFalse((self.root/'active.json').exists())

    def test_active_defaults_preserve_support_and_exact_citation_resolution(self):
        self.activate_first();out=self.registry.evaluate(request(context='hydrophobic_deposits',items=['cleaning_options','pressure_limit']))
        self.assertEqual(out['status'],'partial');self.assertEqual(out['release_id'],self.folder.name)
        self.assertEqual(out['items'][1]['state'],'abstained')
        for ref in out['citation_refs']:
            view=self.registry.source(ref['release_id'],ref['source_id'])
            self.assertEqual(view['authority_digest'],out['authority_digest'])
            self.assertEqual(view['passage'],next(p for p in out['context']['passages'] if p['source_id']==ref['source_id']))

    def test_missing_withdrawal_file_is_not_an_empty_register(self):
        self.assertEqual(self.registry.evaluate(request(),candidate=self.folder.name)['status'],'supported')
        (self.folder/'withdrawals.json').unlink()
        out=self.registry.evaluate(request(),candidate=self.folder.name)
        self.assertEqual(out['response_reason'],'invalid_authority');self.assertEqual(out['context']['bundles'],[])

    def test_invalid_authorization_and_missing_active_decision_fail_closed(self):
        self.activate_first();(self.folder/'activation-decision.json').unlink()
        self.assertEqual(self.registry.evaluate(request())['response_reason'],'invalid_authority')

    def test_changed_mapping_or_source_index_cannot_be_admitted_by_refreshing_hash(self):
        for name,field in [('mapping.json','mapping_ref'),('source-index.json','source_index_ref')]:
            with self.subTest(name=name):
                original=(self.folder/name).read_bytes();release=subject.read(self.folder/'release.json')
                data=subject.read(self.folder/name)
                if name=='mapping.json':data['entries'][1]['allowed_products'].append('mabselect')
                else:data['passages'][0]['quote']='invented quote'
                replace(self.folder/name,data);release[field]=subject.binding(release[field]['artifact_id'],self.folder/name)
                replace(self.folder/'release.json',release)
                self.assertEqual(self.registry.evaluate(request(),candidate=self.folder.name)['status'],'unavailable')
                (self.folder/name).write_bytes(original);release[field]=subject.binding(release[field]['artifact_id'],self.folder/name);replace(self.folder/'release.json',release)

    def test_missing_runtime_dependency_and_path_escape_are_rejected(self):
        release=subject.read(self.folder/'release.json');release['dependencies'].pop();replace(self.folder/'release.json',release)
        self.assertEqual(self.registry.evaluate(request(),candidate=self.folder.name)['status'],'unavailable')
        with self.assertRaises(ValueError):subject.prepare(self.root,'../unsafe')
        with self.assertRaises(ValueError):self.registry.source('../escape','E167-W')

    def test_release_files_are_immutable_under_prepare(self):
        before=(self.folder/'release.json').read_bytes()
        with self.assertRaises(ValueError):subject.prepare(self.root,self.folder.name)
        self.assertEqual((self.folder/'release.json').read_bytes(),before)

    def test_catalog_cannot_redirect_an_artifact(self):
        catalog=subject.read(self.folder/'catalog.json');catalog['artifacts']['mapping']['path']='../../secret'
        replace(self.folder/'catalog.json',catalog)
        self.assertEqual(self.registry.evaluate(request(),candidate=self.folder.name)['status'],'unavailable')

    def test_source_withdrawal_holds_whole_alternative_item_but_not_other_task(self):
        approve_fixture(self.folder,entries=[event(self.folder,'source','E167-W')]);self.registry.activate(self.folder.name)
        value=request(context='hydrophobic_deposits');value['tasks'].append(dict(request()['tasks'][0],task_id='B'))
        out=self.registry.evaluate(value)
        self.assertEqual(out['status'],'partial');self.assertEqual(out['items'][0]['state'],'quarantined')
        self.assertEqual(out['items'][1]['state'],'supported')
        self.assertNotIn('E167-W',[p['source_id'] for p in out['context']['passages']])
        view=self.registry.source(self.folder.name,'E167-W');self.assertEqual(view['status'],'quarantined');self.assertIsNone(view['passage'])

    def test_bundle_and_scoped_review_withdrawals_are_enforced(self):
        for kind,id_ in [('bundle',subject.core.KEYS['Q05']),('review','Q05')]:
            with self.subTest(kind=kind):
                # Each isolated root has an independently reviewed synthetic first release.
                with tempfile.TemporaryDirectory(prefix='held-') as t:
                    folder=subject.prepare(t,'held-v01');approve_fixture(folder,entries=[event(folder,kind,id_)])
                    reg=subject.Registry(t);reg.activate(folder.name)
                    self.assertEqual(reg.evaluate(request())['items'][0]['state'],'quarantined')

    def test_stale_or_unknown_withdrawal_identity_blocks_authority(self):
        e=event(self.folder,'source','E167-W');e['target_sha256']='0'*64
        approve_fixture(self.folder,entries=[e])
        with self.assertRaises(ValueError):self.registry.activate(self.folder.name)
        self.assertFalse((self.root/'active.json').exists())

    def test_old_source_view_obeys_current_withdrawal_authority(self):
        self.activate_first();second=subject.prepare(self.root,'release-v02')
        approve_fixture(second,version=2,entries=[event(self.folder,'source','E167-W')]);self.registry.activate(second.name)
        old=self.registry.source(self.folder.name,'E167-W');self.assertEqual(old['status'],'quarantined');self.assertIsNone(old['passage'])
        current=self.registry.source(second.name,'E167-W');self.assertEqual(current['status'],'available')
        self.assertEqual(current['release_id'],second.name)  # A reviewed new version is a separate identity.

    def test_reinstatement_preserves_original_events_and_requires_new_version(self):
        approve_fixture(self.folder,entries=[event(self.folder,'source','E167-W')]);self.registry.activate(self.folder.name)
        old_events=subject.read(self.folder/'withdrawals.json')['entries']
        second=subject.prepare(self.root,'release-v02');restore=event(self.folder,'source','E167-W',action='reinstate',number=2)
        approve_fixture(second,version=2,entries=old_events+[restore]);self.registry.activate(second.name)
        self.assertEqual(self.registry.source(self.folder.name,'E167-W')['status'],'available')
        self.assertEqual(subject.read(second/'withdrawals.json')['entries'][0],old_events[0])

    def test_history_rollback_is_refused_without_replacing_pointer(self):
        approve_fixture(self.folder,entries=[event(self.folder,'source','E167-W')]);self.registry.activate(self.folder.name)
        before=(self.root/'active.json').read_bytes();second=subject.prepare(self.root,'release-v02');approve_fixture(second,version=2,entries=[])
        with self.assertRaises(ValueError):self.registry.activate(second.name)
        self.assertEqual((self.root/'active.json').read_bytes(),before)

    def test_reinstatement_without_withdrawal_is_rejected(self):
        approve_fixture(self.folder,entries=[event(self.folder,'source','E167-W',action='reinstate')])
        with self.assertRaises(ValueError):self.registry.activate(self.folder.name)

    def test_pointer_change_during_evaluation_discards_response_without_retry(self):
        self.activate_first();second=subject.prepare(self.root,'release-v02');approve_fixture(second,version=2)
        original=subject.core.Handoff.evaluate
        def changing(service,value):
            out=original(service,value);self.registry.activate(second.name);return out
        with patch.object(subject.core.Handoff,'evaluate',new=changing):out=self.registry.evaluate(request())
        self.assertEqual(out['response_reason'],'authority_changed');self.assertEqual(out['context']['passages'],[])

    def test_withdrawal_change_during_source_lookup_never_delivers_old_quote(self):
        self.activate_first();original=subject.core.Handoff.source
        def changing(service,*args):
            out=original(service,*args);(self.folder/'withdrawals.json').write_text('{}',encoding='utf-8');return out
        with patch.object(subject.core.Handoff,'source',new=changing):
            with self.assertRaises((ValueError,KeyError)):self.registry.source(self.folder.name,'E167-W')

    def test_invalid_client_authority_field_does_not_load_registry(self):
        value=request();value['release_id']=self.folder.name
        with patch.object(self.registry,'_snapshot') as load:
            out=self.registry.evaluate(value);load.assert_not_called()
        self.assertEqual(out['kind'],'reviewed_serving_validation_error/v1')

    def test_unknown_source_and_missing_active_authority_do_not_fallback(self):
        with self.assertRaises(FileNotFoundError):self.registry.source(self.folder.name,'E167-W')
        self.activate_first()
        for id_ in ('E118-I','E121-EQ','not-a-source'):
            with self.assertRaises(KeyError):self.registry.source(self.folder.name,id_)
        (self.root/'active.json').write_text('{}',encoding='utf-8')
        self.assertEqual(self.registry.evaluate(request())['response_reason'],'invalid_authority')

    def test_duplicate_json_keys_and_two_freezes_stay_protected(self):
        (self.folder/'withdrawals.json').write_text('{"entries":[],"entries":[]}',encoding='utf-8')
        self.assertEqual(self.registry.evaluate(request(),candidate=self.folder.name)['status'],'unavailable')
        self.assertEqual(verify_freeze(environment=True)['status'],'frozen')

    def test_pointer_hash_mismatch_never_falls_back_to_previous_snapshot(self):
        self.activate_first();self.assertEqual(self.registry.evaluate(request())['status'],'supported')
        p=self.root/'active.json';active=subject.read(p);active['manifest_sha256_lf']='0'*64;replace(p,active)
        out=self.registry.evaluate(request());self.assertEqual(out['response_reason'],'invalid_authority')
        self.assertEqual(out['context']['passages'],[])

    def test_activation_input_change_does_not_publish_partial_pointer(self):
        approve_fixture(self.folder);original=self.registry._load;calls=[]
        def changed(*args,**kwargs):
            out=original(*args,**kwargs);calls.append(1)
            if len(calls)>1:out['token']='changed'
            return out
        with patch.object(self.registry,'_load',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Activation inputs changed'):self.registry.activate(self.folder.name)
        self.assertFalse((self.root/'active.json').exists());self.assertEqual(list(self.root.glob('.active-*')),[])

    def test_incomplete_or_forged_approval_never_activates(self):
        approve_fixture(self.folder)
        p=self.folder/'activation-decision.json';d=subject.read(p);d['original_human_message']='';replace(p,d)
        release=subject.read(self.folder/'release.json');release['activation_decision_ref']=subject.binding('activation-decision',p);replace(self.folder/'release.json',release)
        with self.assertRaisesRegex(ValueError,'authorization'):self.registry.activate(self.folder.name)
        self.assertFalse((self.root/'active.json').exists())

    def test_restored_valid_pointer_cannot_restore_withdrawn_quote_even_after_restart(self):
        self.activate_first();backup=(self.root/'active.json').read_bytes()
        second=subject.prepare(self.root,'release-v02')
        approve_fixture(second,version=2,entries=[event(self.folder,'source','E167-W')]);self.registry.activate(second.name)
        self.assertEqual(self.registry.source(self.folder.name,'E167-W')['status'],'quarantined')
        (self.root/'active.json').write_bytes(backup)
        restarted=subject.Registry(self.root)
        out=restarted.evaluate(request());self.assertEqual(out['response_reason'],'invalid_authority')
        self.assertEqual(out['context']['passages'],[])
        with self.assertRaisesRegex(ValueError,'durable authority head'):restarted.source(self.folder.name,'E167-W')

    def test_missing_or_corrupted_durable_head_never_reconstructs_it_from_old_pointer(self):
        self.activate_first();log=self.root/'authority-log';head=next(log.glob('*.json'))
        original=head.read_bytes();head.write_text('{}',encoding='utf-8')
        self.assertEqual(self.registry.evaluate(request())['response_reason'],'invalid_authority')
        head.write_bytes(original);log.rename(self.root/'saved-authority-log')
        self.assertEqual(subject.Registry(self.root).evaluate(request())['response_reason'],'invalid_authority')

    def test_interrupted_pointer_replace_keeps_new_head_and_fails_closed_after_restart(self):
        self.activate_first();old_pointer=(self.root/'active.json').read_bytes()
        second=subject.prepare(self.root,'release-v02')
        approve_fixture(second,version=2,entries=[event(self.folder,'source','E167-W')])
        with patch.object(subject.os,'replace',side_effect=OSError('simulated interrupted replace')):
            with self.assertRaises(OSError):self.registry.activate(second.name)
        self.assertEqual((self.root/'active.json').read_bytes(),old_pointer)
        restarted=subject.Registry(self.root);self.assertEqual(restarted._head()['record']['generation'],2)
        self.assertEqual(restarted.evaluate(request())['response_reason'],'invalid_authority')
        self.assertEqual(list(self.root.glob('.active-*')),[])

    def test_authority_journal_chain_and_contiguous_generations_are_checked(self):
        self.activate_first();second=subject.prepare(self.root,'release-v02');approve_fixture(second,version=2);self.registry.activate(second.name)
        head=self.root/'authority-log'/'00000000000000000002.json';record=subject.read(head)
        record['previous_sha256_lf']='0'*64;replace(head,record)
        self.assertEqual(self.registry.evaluate(request())['response_reason'],'invalid_authority')
        head.rename(head.with_name('00000000000000000003.json'))
        with self.assertRaisesRegex(ValueError,'incomplete'):self.registry._head()

    def test_historical_versions_are_fully_validated_once_per_digest_per_operation(self):
        history=[];first=self.folder
        for version in range(1,6):
            folder=first if version==1 else subject.prepare(self.root,'release-v0'+str(version))
            history=history+[event(first,'source','E167-W',action='withdraw' if version%2 else 'reinstate',number=version)]
            approve_fixture(folder,version=version,entries=history)
            history=subject.read(folder/'withdrawals.json')['entries']
        with patch.object(self.registry,'_load_uncached',wraps=self.registry._load_uncached) as load:
            self.registry._load(folder.name);self.assertEqual(load.call_count,5)
            self.registry._load(folder.name);self.assertEqual(load.call_count,10)  # No stale cross-request cache.

    def test_backend_failure_with_unchanged_authority_has_service_outcomes_and_private_diagnostic(self):
        value=request(items=['cleaning_options','pressure_limit']);value['tasks'][0]['excluded_items']=['pressure_limit']
        with patch.object(subject.core.Handoff,'evaluate',side_effect=RuntimeError('private exception contents')),self.assertLogs(subject.LOGGER,level='ERROR') as logs:
            out=self.registry.evaluate(value,candidate=self.folder.name)
        self.assertEqual(out['status'],'unavailable');self.assertEqual(out['response_reason'],'item_outcomes')
        self.assertEqual([i['state'] for i in out['items']],['unavailable','excluded'])
        self.assertEqual(out['items'][0]['reason'],'required_dependency_unavailable')
        self.assertEqual(out['items'][1]['reason'],'excluded_by_request')
        self.assertEqual(out['context']['bundles'],[]);self.assertEqual(out['coverage']['unavailable'],1)
        self.assertIn('RuntimeError',''.join(logs.output))
        self.assertNotIn('private exception contents',json.dumps(out)+''.join(logs.output))

    def test_backend_failure_and_real_authority_change_still_report_authority_changed(self):
        self.activate_first()
        def changed(*_args):
            (self.root/'active.json').write_text('{}',encoding='utf-8');raise RuntimeError('backend and authority changed')
        with patch.object(subject.core.Handoff,'evaluate',side_effect=changed):out=self.registry.evaluate(request())
        self.assertEqual(out['response_reason'],'authority_changed');self.assertEqual(out['context']['passages'],[])

    def test_removed_pointer_after_activation_is_invalid_authority_not_never_activated(self):
        self.activate_first();(self.root/'active.json').unlink()
        self.assertEqual(subject.Registry(self.root).evaluate(request())['response_reason'],'invalid_authority')
