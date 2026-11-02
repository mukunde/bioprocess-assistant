"""Separate documentary freeze: integrity, portability and accepted-case replay."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva import mabselect_handoff_freeze as subject


@contextmanager
def copy_freeze(crlf=False):
    with tempfile.TemporaryDirectory(prefix='msh-') as temp:
        root = Path(temp)
        names = subject.inventory(subject.ROOT)+[(subject.PACKAGE/'method-lock.json').as_posix()]
        for name in names:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            raw=(subject.ROOT/name).read_bytes()
            target.write_bytes(raw.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n') if crlf else raw)
        yield root


class MabSelectHandoffFreezeTests(unittest.TestCase):
    def test_static_verifier_does_not_construct_runtime_or_use_sockets(self):
        with patch('socket.socket',side_effect=AssertionError('network')),patch('demo.documentary.Handoff',side_effect=AssertionError('runtime')):
            result=subject.verify(environment=True)
        self.assertEqual(result['status'],'frozen');self.assertFalse(result['runtime_instantiated'])
        self.assertFalse(result['serving_activated'])

    def test_transitive_source_and_review_inventory_is_complete(self):
        names=subject.inventory(subject.ROOT)
        for name in ('experiments/cytiva/reviewed-cleaning-retrieval/events.json',
                     'experiments/cytiva/reviewed-section-questions/provenance.json',
                     subject.EXAMPLES,'experiments/cytiva/retrieval-pilot-v01/evidence.json'):
            self.assertIn(name,names)
        self.assertNotIn((subject.PACKAGE/'method-lock.json').as_posix(),names)
        self.assertFalse(any('.local-tools' in n or n.startswith('media/') for n in names))

    def test_changed_or_missing_source_is_rejected(self):
        with copy_freeze() as root:
            path=root/'experiments/cytiva/retrieval-pilot-v01/evidence.json'
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'Frozen component changed'):subject.verify(root)
            path.unlink()
            with self.assertRaisesRegex(ValueError,'Missing/unsafe'):subject.verify(root)

    def test_removed_inventory_and_scope_promotion_are_rejected(self):
        with copy_freeze() as root:
            p=root/subject.PACKAGE/'method-lock.json';original=subject.read(p)
            changed=json.loads(json.dumps(original));changed['file_sha256_lf'].pop(subject.EXAMPLES)
            p.write_text(json.dumps(changed),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'inventory'):subject.verify(root)
            original['policy']['serving_activated']=True;p.write_text(json.dumps(original),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'scope or policy'):subject.verify(root)

    def test_crlf_checkout_preserves_freeze_digest_and_quote_bytes(self):
        with copy_freeze(crlf=True) as root:
            result=subject.verify(root)
            self.assertEqual(result['method_lock_sha256_lf'],subject.verify()['method_lock_sha256_lf'])
            original=subject.read(subject.ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json')
            copied=subject.read(root/'experiments/cytiva/retrieval-pilot-v01/evidence.json')
            self.assertEqual(original,copied)

    def test_environment_mismatch_fails_without_installation(self):
        with patch.object(subject.platform,'python_version',return_value='0.0.0'):
            with self.assertRaisesRegex(ValueError,'environment'):subject.verify(environment=True)

    def test_six_cases_replay_with_full_citations_and_no_activation(self):
        result=subject.replay()
        self.assertEqual([r['case_id'] for r in result['cases']],[f'SX{i:02}' for i in range(1,7)])
        self.assertTrue(all(r['status']=='passed' for r in result['cases']))
        self.assertEqual(result['network_attempts'],[]);self.assertEqual(result['llm_calls'],0)
        self.assertFalse(result['serving_activated']);self.assertFalse(result['prospective_evaluation'])
        self.assertEqual(result['cases'][-1]['selector_calls'],0)
        for row in result['cases']:
            self.assertEqual(row['response_sha256'],hashlib.sha256(subject.canonical(row['response'])).hexdigest())
        self.assertTrue(result['cases'][2]['resolved_citations'])

    def test_freeze_failure_prevents_runtime_construction(self):
        with patch.object(subject,'verify',side_effect=ValueError('changed')),patch('demo.documentary.Handoff') as service:
            with self.assertRaisesRegex(ValueError,'changed'):subject.replay()
            service.assert_not_called()

    def test_case_assertions_reject_bad_clarification_and_procedure(self):
        row=subject.replay()['cases'][1];case=subject.read(subject.ROOT/subject.EXAMPLES)['examples'][1]
        row['response']['items'][0]['clarification_targets']=['deposit_context']
        with self.assertRaisesRegex(ValueError,'clarification'):subject.check_case(case,row['response'])
        row['response']['items'][0]['clarification_targets']=['product']
        row['response']['context']['bundles'][0]['options'][0]['role']='procedure'
        with self.assertRaisesRegex(ValueError,'Procedure'):subject.check_case(case,row['response'])

    def test_existing_replay_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='msh-out-') as tmp:
            p=Path(tmp)/'result.json';p.write_text('keep me',encoding='utf-8')
            with patch('sys.argv',['freeze','--replay','--output',str(p)]),patch.object(subject,'replay') as run:
                with self.assertRaises(SystemExit) as error:subject.main()
                self.assertEqual(error.exception.code,1);run.assert_not_called()
            self.assertEqual(p.read_text(encoding='utf-8'),'keep me')
