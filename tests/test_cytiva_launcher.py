"""Offline startup diagnostics and real Windows PowerShell entry-point checks."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.metadata
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from demo import launch


class LauncherChecks(unittest.TestCase):
    def setUp(self):
        guard=patch.object(socket.socket,'connect',side_effect=AssertionError('No network'))
        guard.start();self.addCleanup(guard.stop)

    def test_preflight_passes_without_constructing_engine_or_server(self):
        with patch('demo.cytiva.Demo') as demo,patch.object(launch,'HTTPServer') as server:
            report=launch.check()
        self.assertTrue(report['ready']);self.assertEqual(report['errors'],[])
        self.assertTrue(report['freeze']['environment_verified'])
        self.assertEqual(report['freeze']['pinned_files'],36)
        demo.assert_not_called();server.assert_not_called()

    def test_missing_and_wrong_dependencies_have_exact_diagnostics(self):
        original=importlib.metadata.version
        def version(name):
            if name=='jsonschema':raise importlib.metadata.PackageNotFoundError(name)
            return 'invalid' if name=='tiktoken' else original(name)
        with patch.object(importlib.metadata,'version',side_effect=version):report=launch.check()
        self.assertFalse(report['ready'])
        self.assertTrue(any('jsonschema' in x and 'not installed' in x for x in report['errors']))
        self.assertTrue(any('tiktoken' in x and 'invalid' in x for x in report['errors']))

    def test_frozen_file_error_stops_before_dependency_probe(self):
        with (patch.object(launch,'verify',side_effect=ValueError('Frozen component changed')),
              patch.object(importlib.metadata,'version') as version):
            report=launch.check()
        self.assertFalse(report['ready']);version.assert_not_called()
        self.assertIn('do not regenerate',report['remedy'])

    def test_wrong_python_version_is_reported(self):
        with patch.object(launch.platform,'python_version',return_value='0.0.0'):report=launch.check()
        self.assertFalse(report['ready']);self.assertIn('found 0.0.0',' '.join(report['errors']))

    def test_missing_and_corrupt_cache_fail_closed(self):
        lock=json.loads((launch.ROOT/launch.PACKAGE/'method-lock.json').read_text(encoding='utf-8'))
        asset=(launch.ROOT/lock['environment']['tokenizer_asset_file']).resolve()
        is_file=Path.is_file
        with patch.object(Path,'is_file',lambda p:False if p==asset else is_file(p)):
            missing=launch.check()
        self.assertFalse(missing['ready']);self.assertIn('cache missing',' '.join(missing['errors']))
        asset_data=asset.read_bytes();sha256=launch.hashlib.sha256
        def corrupt(data):
            return MagicMock(hexdigest=lambda:'0'*64) if data==asset_data else sha256(data)
        with patch.object(launch.hashlib,'sha256',side_effect=corrupt):bad=launch.check()
        self.assertFalse(bad['ready']);self.assertIn('cache hash',' '.join(bad['errors']))

    def test_check_only_json_never_starts_a_service(self):
        out=io.StringIO()
        with redirect_stdout(out),patch.object(launch,'serve') as serve:
            code=launch.main(['--check','--json'])
        self.assertEqual(code,0);self.assertTrue(json.loads(out.getvalue())['ready'])
        serve.assert_not_called()

    def test_port_conflict_and_runtime_failure_have_distinct_exit_codes(self):
        with redirect_stderr(io.StringIO()) as errors,patch.object(launch,'HTTPServer',side_effect=OSError('busy')):
            self.assertEqual(launch.serve(8766),2)
        self.assertIn('port may already be in use',errors.getvalue())
        with redirect_stderr(io.StringIO()) as errors,patch('demo.cytiva.Demo',side_effect=ValueError('bad runtime')):
            self.assertEqual(launch.serve(8766),3)
        self.assertIn('No server was started',errors.getvalue())


@unittest.skipUnless(os.name=='nt','Windows PowerShell entry point')
class WindowsLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell=shutil.which('powershell.exe')
        if not cls.shell:raise RuntimeError('Windows PowerShell is required for launcher tests')
        cls.script=launch.ROOT/'Start-CytivaDemo.ps1'

    def run_script(self,*args,cwd=None):
        return subprocess.run([self.shell,'-NoProfile','-NonInteractive','-File',str(self.script),*args],
                              cwd=cwd or launch.ROOT,capture_output=True,text=True,timeout=45,
                              creationflags=subprocess.CREATE_NO_WINDOW)

    def test_auto_discovery_check_only(self):
        result=self.run_script('-CheckOnly')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('Frozen v03: 36 files',result.stdout)
        self.assertIn('CheckOnly does not start',result.stdout)

    def test_explicit_python_from_other_working_directory_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='launcher test ') as directory:
            result=self.run_script('-PythonPath',sys.executable,'-CheckOnly',cwd=directory)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn(sys.executable,result.stdout)

    def test_missing_python_and_invalid_port_are_errors(self):
        for args in (('-PythonPath',str(launch.ROOT/'missing python.exe'),'-CheckOnly'),('-Port','70000','-CheckOnly')):
            with self.subTest(args=args):
                result=self.run_script(*args)
                self.assertNotEqual(result.returncode,0)
                self.assertNotIn('Cytiva demo ready:',result.stdout)

    def test_occupied_port_is_not_replaced_or_killed(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1',0));occupied.listen()
            port=occupied.getsockname()[1]
            result=self.run_script('-PythonPath',sys.executable,'-Port',str(port))
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertIn('port may already be in use',result.stderr+result.stdout)
            self.assertEqual(occupied.getsockname()[1],port)
