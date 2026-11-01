"""MR02/MC12: execute the actual HTML/JS and real loopback API, plus mutants."""
from http.server import HTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import threading
import unittest
from unittest.mock import patch

from demo.cytiva import Demo, handler_for

ROOT=Path(__file__).resolve().parents[1]


class MabSelectUIIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.node=shutil.which('node')
        if not cls.node:
            raise RuntimeError('MC12 UI tests require Node >=22.12 and npm ci --prefix tests/ui; no silent skip')
        cls.server=HTTPServer(('127.0.0.1',0),handler_for(Demo()))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)+'/'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=5)

    def run_dom(self, mutation='none'):
        try:
            return subprocess.run([self.node,str(ROOT/'tests/ui/mabselect.cjs'),self.base,mutation],
                                  capture_output=True,text=True,encoding='utf-8',cwd=ROOT,timeout=40,
                                  creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        except subprocess.TimeoutExpired as exc:
            self.fail(f'MC12 subprocess exceeded 40 seconds: mutation={mutation}; '
                      f'stdout={exc.stdout!r}; stderr={exc.stderr!r}')

    def test_MC12_real_form_payload_blocks_warnings_links_stale_and_old_routes(self):
        run=self.run_dom()
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertEqual(json.loads(run.stdout)['status'],'passed')
        self.assertEqual(len(json.loads(run.stdout)['cases']),7)

    def test_MC12_detects_removal_of_entry_point(self):
        run=self.run_dom('missing-entry')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('Missing MabSelect entry',run.stderr)

    def test_MC12_detects_incorrect_product_payload_wiring(self):
        run=self.run_dom('wrong-payload')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('AssertionError',run.stderr)

    def test_MC12_detects_loss_of_stale_result_handling(self):
        run=self.run_dom('missing-stale')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('Changed product must mark results stale',run.stderr)

    def test_MC12_detects_missing_rendered_warning(self):
        run=self.run_dom('missing-warning')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('AssertionError',run.stderr)

    def test_MC12_detects_broken_source_navigation(self):
        run=self.run_dom('broken-source-link')
        self.assertNotEqual(run.returncode,0)
        self.assertIn('#broken-E167-W',run.stderr)

    def test_timeout_is_a_failure_with_partial_request_diagnostics(self):
        error = subprocess.TimeoutExpired('node', 40, output=b'partial',
                                         stderr=b'[MC12] wrong-payload: loading application')
        with patch('tests.test_mabselect_ui.subprocess.run', side_effect=error) as run:
            with self.assertRaisesRegex(AssertionError, 'mutation=wrong-payload.*loading application'):
                self.run_dom('wrong-payload')
            self.assertEqual(run.call_args.kwargs['timeout'], 40)
