"""Regression coverage for nested Windows test fixtures and temp restoration."""
from pathlib import Path
import tempfile
import unittest
from scripts.run_tests import test_workspace


class TestWorkspaceTests(unittest.TestCase):
    def test_nested_fixture_uses_selected_root_and_cleans_only_own_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            marker = base / 'keep.txt'
            marker.write_bytes(b'preserve')
            prior = tempfile.tempdir
            with test_workspace(base, windows=False) as selected:
                with tempfile.TemporaryDirectory() as nested:
                    self.assertTrue(Path(nested).is_relative_to(selected))
                    path = Path(nested) / ('a' * 65) / ('b' * 65) / 'snapshot.json'
                    path.parent.mkdir(parents=True)
                    path.write_text('{}', encoding='utf-8')
                    self.assertTrue(path.is_file())
            self.assertEqual(tempfile.tempdir, prior)
            self.assertFalse(selected.exists())
            self.assertEqual(marker.read_bytes(), b'preserve')

    def test_error_restores_prior_temp_and_cleans_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            prior = tempfile.tempdir
            with self.assertRaisesRegex(RuntimeError, 'synthetic'):
                with test_workspace(tmp, windows=False) as selected:
                    raise RuntimeError('synthetic')
            self.assertEqual(tempfile.tempdir, prior)
            self.assertFalse(selected.exists())

    def test_long_windows_root_rejected_before_creating_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / ('long-' * 20)
            with self.assertRaisesRegex(ValueError, '--temp-root'):
                with test_workspace(target, windows=True):
                    self.fail('Must reject before execution')
            self.assertFalse(target.exists())
