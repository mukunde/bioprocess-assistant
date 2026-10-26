"""Saved structured evidence is portable and tamper-sensitive; no trial reruns."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from experiments.cytiva import verify_structured_reviewed_package as selected


class StructuredReviewedPackageTests(unittest.TestCase):
    def test_portable_copy_without_private_runs_or_runtime_and_with_crlf(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / selected.PACKAGE
            manifest = selected.frozen.read(selected.ROOT / selected.PACKAGE / 'manifest.json')
            names = list(manifest['supporting_files']) + [
                (selected.PACKAGE / name).as_posix() for name in [*manifest['files'], 'manifest.json']]
            for name in names:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(selected.ROOT / name, target)
            # Simulate a Windows checkout, not a private execution environment.
            doc = package / 'README.md'
            doc.write_bytes(doc.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
            self.assertFalse((root / 'data').exists())
            self.assertFalse((root / '.local-tools').exists())
            with patch.object(selected.frozen, 'make_runtime', side_effect=AssertionError('No runtime')), \
                 patch('socket.socket.connect', side_effect=AssertionError('No network')):
                self.assertEqual(selected.verify(root)['contexts'], 24)

    def changed_content(self, filename, change, message):
        original = selected.frozen.read
        data = deepcopy(original(selected.ROOT / selected.PACKAGE / filename))
        change(data)
        def read(path):
            return data if Path(path) == selected.ROOT / selected.PACKAGE / filename else original(path)
        with patch.object(selected.frozen, 'read', side_effect=read):
            with self.assertRaisesRegex(ValueError, message):
                selected.check_content(selected.ROOT, selected.ROOT / selected.PACKAGE)

    def test_source_corruption_rejected(self):
        def change(data):
            data['contexts'][0]['result']['plan']['context']['source_passages'][0]['quote'] += ' changed'
        self.changed_content('results.json', change, 'source_integrity')

    def test_false_recorded_score_rejected(self):
        self.changed_content('results.json', lambda d: d['metrics']['scores'][0].update(passed=False),
                             'Recorded scores changed')

    def test_quarantine_leak_rejected(self):
        def change(data):
            data['contexts'][0]['result']['plan']['context']['source_passages'][0]['id'] = 'E121-EQ'
        self.changed_content('results.json', change, 'Quarantine leakage')

    def test_review_hash_binding_rejected(self):
        self.changed_content('review.json', lambda d: d['decisions'][0].update(submission_sha256_canonical='0'*64),
                             'content binding changed')

    def test_s01_amendment_scope_rejected(self):
        def change(data):
            data['S01_amendment']['decision']['approved_form_amendment']['scope']['task_id'] = 'A'
        self.changed_content('events.json', change, 'S01 decision changed')

    def test_token_budget_violation_rejected(self):
        self.changed_content('results.json', lambda d: d['contexts'][0]['result']['plan'].update(context_tokens=2049),
                             'resource_invariant')


if __name__ == '__main__':
    unittest.main()
