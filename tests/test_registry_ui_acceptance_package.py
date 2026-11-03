"""Offline integrity checks for the compact historical acceptance export."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import importlib.util
ROOT = Path(__file__).resolve().parents[1]
REL = Path('experiments/cytiva/reviewed-registry-ui-acceptance-v01')
spec = importlib.util.spec_from_file_location('acceptance_packet_verify', ROOT/REL/'verify.py')
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class AcceptancePacketTests(unittest.TestCase):
    def copy_packet(self):
        temp = tempfile.TemporaryDirectory(prefix='ua-packet-')
        self.addCleanup(temp.cleanup); root = Path(temp.name)
        for relative in [REL, subject.PREP]:
            shutil.copytree(ROOT/relative, root/relative)
        lock = subject.load(ROOT/subject.PREP/'method-lock.json')
        for relative in lock['files_sha256_lf']:
            target = root/relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/relative, target)
        return root

    def test_preserved_packet_verifies_without_runtime_or_network(self):
        result = subject.verify()
        self.assertEqual(result['reviewed_cases'], 8)
        self.assertEqual(result['opened_sources_verified'], 13)
        self.assertFalse(result['trial_reexecuted'])
        self.assertFalse(result['network_or_registry_access'])

    def test_observation_edit_is_rejected(self):
        root = self.copy_packet(); path = root/REL/'observations.json'
        data = subject.load(path); data['cases'][0]['response']['status'] = 'abstained'
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Package hash'): subject.verify(root)

    def test_human_decision_edit_is_rejected(self):
        root = self.copy_packet(); path = root/subject.PREP/'review.json'
        data = subject.load(path); data['decisions'][0]['original_human_message'] = 'edited'
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Preparation hash'): subject.verify(root)

    def test_lf_crlf_portability_preserves_hashes_and_decisions(self):
        root = self.copy_packet()
        for path in root.rglob('*'):
            if path.is_file():
                data = path.read_bytes().replace(b'\r\n', b'\n')
                path.write_bytes(data.replace(b'\n', b'\r\n'))
        self.assertEqual(subject.verify(root)['status'], 'passed')

