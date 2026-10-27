"""Installer integrity/ isolation regressions; no real downloads or pip installs."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from demo import setup


class CytivaSetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.env = {'tokenizer_asset_file': '.local-tools/tiktoken-cache/test',
                    'tokenizer_asset_sha256': hashlib.sha256(b'valid tokenizer').hexdigest()}
        self.source = self.root/'tokenizer.txt'
        self.source.write_bytes(b'valid tokenizer')

    def test_lock_matches_all_twelve_frozen_dependencies(self):
        env = json.loads((setup.ROOT/setup.PACKAGE/'method-lock.json').read_text())['environment']
        self.assertTrue(setup.validate_requirements(setup.ROOT, env).is_file())
        self.assertEqual(len(env['dependencies']), 12)
        with self.assertRaisesRegex(ValueError, 'differ'):
            setup.validate_requirements(setup.ROOT, {**env, 'dependencies': {'jsonschema': '0'}})

    def test_invalid_requirements_never_reach_pip(self):
        (self.root/'demo').mkdir()
        (self.root/'demo/requirements-windows.lock').write_text('jsonschema==4.26.0\n')
        with self.assertRaisesRegex(ValueError, 'Invalid'):
            setup.validate_requirements(self.root, {'dependencies': {'jsonschema': '4.26.0'}})

    def test_offline_copy_and_repeat_never_open_network(self):
        with patch.object(setup.urllib.request, 'urlopen', side_effect=AssertionError('network')):
            self.assertEqual(setup.prepare_tokenizer(self.root, self.env, offline=True, source=self.source), 'copied_verified')
            self.assertEqual(setup.prepare_tokenizer(self.root, self.env, offline=True), 'already_verified')
        self.assertEqual((self.root/self.env['tokenizer_asset_file']).read_bytes(), b'valid tokenizer')

    def test_corrupt_download_is_not_published(self):
        with patch.object(setup.urllib.request, 'urlopen', return_value=io.BytesIO(b'corrupt')):
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                setup.prepare_tokenizer(self.root, self.env)
        self.assertFalse((self.root/self.env['tokenizer_asset_file']).exists())

    def test_missing_offline_asset_does_not_download(self):
        with patch.object(setup.urllib.request, 'urlopen') as download:
            with self.assertRaisesRegex(ValueError, 'tokenizer-file'):
                setup.prepare_tokenizer(self.root, self.env, offline=True)
        download.assert_not_called()

    def test_corrupt_existing_asset_is_preserved_for_inspection(self):
        asset = self.root/self.env['tokenizer_asset_file']
        asset.parent.mkdir(parents=True); asset.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'Existing tokenizer'):
            setup.prepare_tokenizer(self.root, self.env, source=self.source)
        self.assertEqual(asset.read_bytes(), b'corrupt')

    def test_destination_cannot_escape_clone(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            setup.prepare_tokenizer(self.root, {**self.env, 'tokenizer_asset_file': '../outside'})

    def test_invalid_freeze_stops_before_creating_environment(self):
        with patch.object(setup, 'verify', side_effect=ValueError('freeze drift')), patch.object(setup.venv, 'EnvBuilder') as builder:
            with self.assertRaisesRegex(ValueError, 'freeze drift'):
                setup.install(self.root)
        builder.assert_not_called()

    def prepare_install_root(self):
        package = self.root/setup.PACKAGE; package.mkdir(parents=True)
        lock = json.loads((setup.ROOT/setup.PACKAGE/'method-lock.json').read_text())
        (package/'method-lock.json').write_text(json.dumps(lock))
        (self.root/'demo').mkdir()
        shutil.copyfile(setup.ROOT/'demo/requirements-windows.lock', self.root/'demo/requirements-windows.lock')
        target = self.root/'.venv-demo'; (target/'Scripts').mkdir(parents=True)
        (target/'Scripts/python.exe').touch()
        (target/'pyvenv.cfg').write_text('include-system-site-packages = false\n')

    def test_ready_environment_is_noop_and_existing_venv_must_be_isolated(self):
        self.prepare_install_root()
        with (patch.object(setup, 'verify'), patch.object(setup.subprocess, 'check_output', return_value='3.13.0\n'),
              patch.object(setup.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run,
              patch.object(setup, 'prepare_tokenizer') as tokenizer):
            setup.install(self.root)
        self.assertEqual(run.call_count, 1); tokenizer.assert_not_called()
        (self.root/'.venv-demo/pyvenv.cfg').write_text('include-system-site-packages = true\n')
        with patch.object(setup, 'verify'), patch.object(setup.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'not an isolated'):
                setup.install(self.root)
        run.assert_not_called()

    def test_offline_pip_uses_hashes_and_no_index_in_clone_venv(self):
        self.prepare_install_root()
        wheelhouse = self.root/'wheels'; wheelhouse.mkdir()
        with (patch.object(setup, 'verify'), patch.object(setup.subprocess, 'check_output', return_value='3.13.0\n'),
              patch.object(setup.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)),
              patch.object(setup, 'run') as run, patch.object(setup, 'prepare_tokenizer')):
            setup.install(self.root, offline=True, wheelhouse=wheelhouse, tokenizer_file=self.source)
        args = run.call_args_list[0].args[0]
        self.assertEqual(args[0], self.root/'.venv-demo/Scripts/python.exe')
        for option in ('--isolated', '--no-index', '--no-deps', '--require-hashes', '--only-binary=:all:'):
            self.assertIn(option, args)
        self.assertNotIn('--index-url', args)
        self.assertEqual(run.call_args_list[-1].args[0][-3:], ['demo.launch', '--check', '--json'])
