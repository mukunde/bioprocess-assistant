"""Static freeze guards; no interpreter or prospective execution."""
from copy import deepcopy
import importlib.metadata
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva.free_text_v03_freeze import ROOT,PACKAGE,PINNED,verify


class V03FreezeTests(unittest.TestCase):
    def setUp(self):
        guard=patch.object(socket.socket,'connect',side_effect=AssertionError('No network'))
        guard.start();self.addCleanup(guard.stop)

    def test_static_check_has_no_runtime_or_third_party_import(self):
        import subprocess,sys
        result=subprocess.run([sys.executable,'-S','-m','experiments.cytiva.free_text_v03_freeze'],
                              cwd=ROOT,capture_output=True,text=True,check=True)
        self.assertFalse(json.loads(result.stdout)['runtime_instantiated'])
        self.assertEqual(verify()['pinned_files'],len(PINNED))

    def test_recorded_local_environment_and_tokenizer_asset(self):
        self.assertTrue(verify(environment=True)['environment_verified'])

    def test_changed_dependency_and_crlf_portability(self):
        from experiments.cytiva import free_text_v03_freeze as freeze
        original=freeze.digest
        for name in ('ingestion/coverage_v03.py','docs/technical/coverage-summary-v03.schema.json'):
            def changed(path):return '0'*64 if Path(path)==ROOT/name else original(path)
            with self.subTest(name=name),patch.object(freeze,'digest',side_effect=changed),self.assertRaises(ValueError):verify()
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'a';b=Path(directory)/'b'
            a.write_bytes(b'alpha\nbeta\n');b.write_bytes(b'alpha\r\nbeta\r\n')
            self.assertEqual(freeze.digest(a),freeze.digest(b))

    def test_inventory_policy_and_trial_status_cannot_drift(self):
        original=json.loads((ROOT/PACKAGE/'method-lock.json').read_text(encoding='utf-8'))
        read_text=Path.read_text
        for defect in ('inventory','quarantine','budget','trial','entry_point'):
            lock=deepcopy(original)
            if defect=='inventory':lock['file_sha256_lf'].pop(next(iter(lock['file_sha256_lf'])))
            elif defect=='quarantine':lock['excluded_source_ids']=[]
            elif defect=='budget':lock['context_token_limit']=4096
            elif defect=='trial':lock['evaluation_executed']=True
            else:lock['runtime_entry_points']['free_text']='ingestion.free_text_bridge.FreeTextControl'
            def altered(path,*a,**kw):
                return json.dumps(lock) if path==ROOT/PACKAGE/'method-lock.json' else read_text(path,*a,**kw)
            with self.subTest(defect=defect),patch.object(Path,'read_text',altered),self.assertRaises(ValueError):verify()

    def test_dependency_version_mismatch_fails_without_network(self):
        with patch.object(importlib.metadata,'version',return_value='invalid'),self.assertRaises(ValueError):
            verify(environment=True)
