"""MR01 regressions: independent approval anchors, portable replay, fail closed."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva.verify_mabselect_design import ARTIFACTS, ROOT, verify
from demo import mabselect


class ApprovedDesignIntegrityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name, _ in ARTIFACTS.values():
            target = self.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)

    def test_replay_needs_only_the_three_portable_artifacts_with_lf_or_crlf(self):
        for ending in (b'\n', b'\r\n'):
            for name, _ in ARTIFACTS.values():
                path = self.root/name
                path.write_bytes(path.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',ending))
            self.assertEqual(verify(self.root)['decisions'], 12)

    def test_review_message_statements_decisions_and_digests_cannot_be_rewritten(self):
        path = self.root/ARTIFACTS['review'][0]
        raw = path.read_bytes()
        mutations = [lambda d:d.update(original_human_message='altered'),
                     lambda d:d.update(contract_before_review_sha256_lf='0'*64),
                     lambda d:d.update(source_dossier_sha256_lf='0'*64),
                     lambda d:d.update(recorded_at_utc='altered'),
                     lambda d:d['decisions'][0].update(statement='altered'),
                     lambda d:d['decisions'][-1].update(statement='altered C4'),
                     lambda d:d['decisions'][0].update(decision='rejected'),
                     lambda d:d['decisions'].pop()]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                data = json.loads(raw);mutation(data)
                path.write_text(json.dumps(data),encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'changed: review'): verify(self.root)
        path.write_bytes(raw)

    def test_changed_or_missing_snapshot_and_dossier_are_rejected(self):
        for role in ('contract','dossier'):
            path = self.root/ARTIFACTS[role][0];raw=path.read_bytes()
            with self.subTest(role=role):
                path.write_bytes(raw+b'changed')
                with self.assertRaisesRegex(ValueError, 'changed: '+role): verify(self.root)
                path.unlink()
                with self.assertRaisesRegex(ValueError, 'unavailable: '+role): verify(self.root)
                path.write_bytes(raw)

    def test_jointly_rewriting_contract_and_its_review_hash_cannot_reapprove_it(self):
        import hashlib
        contract = self.root/ARTIFACTS['contract'][0]
        contract.write_bytes(contract.read_bytes()+b'changed approval basis')
        review = self.root/ARTIFACTS['review'][0]
        data=json.loads(review.read_bytes())
        data['contract_before_review_sha256_lf']=hashlib.sha256(contract.read_bytes()).hexdigest()
        review.write_text(json.dumps(data),encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed: contract'): verify(self.root)

    def test_runtime_rejects_edited_approval_before_loading_original_source_reviews(self):
        path=ROOT/ARTIFACTS['review'][0];read=Path.read_bytes
        data=json.loads(read(path));data['original_human_message']='changed'
        def changed(p):return json.dumps(data).encode() if p==path else read(p)
        with patch.object(Path,'read_bytes',changed),patch.object(mabselect,'verify_q') as source:
            with self.assertRaisesRegex(ValueError,'changed: review'):
                mabselect.evaluate({'mode':'mabselect','product':'mabselect','deposit_context':'precipitated_substances'})
            source.assert_not_called()
