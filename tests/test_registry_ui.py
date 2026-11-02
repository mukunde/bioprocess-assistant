"""Opt-in registry UI over real loopback HTTP; synthetic authority stays in temp roots."""
from copy import deepcopy
from http.client import HTTPConnection
from pathlib import Path
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from demo import registry_ui as ui
from serving import local_registry as subject
from tests.test_local_registry import approve_fixture, event, request

ROOT = Path(__file__).resolve().parents[1]


class RegistryUIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='registry-ui-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'authority'
        self.folder = subject.prepare(self.root, 'release-v01')
        approve_fixture(self.folder)
        subject.Registry(self.root).activate('release-v01')
        self.server = self.start(self.root)
        self.base = 'http://127.0.0.1:'+str(self.server.server_port)+'/'

    def start(self, root):
        server = ui.create_server(root, port=0)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        def stop():
            server.shutdown(); server.server_close(); thread.join(timeout=5)
        self.addCleanup(stop)
        return server

    def http(self, path, value=None, *, server=None, headers=None):
        server = server or self.server
        conn = HTTPConnection('127.0.0.1', server.server_port, timeout=8)
        self.addCleanup(conn.close)
        fields = {'Connection':'close'}
        if value is not None:
            fields['Content-Type']='application/json'
        fields.update(headers or {})
        conn.request('GET' if value is None else 'POST', path,
                     None if value is None else json.dumps(value), fields)
        response = conn.getresponse()
        return response.status, dict(response.getheaders()), response.read().decode('utf-8')

    def evaluate(self, value=None, **kwargs):
        status, headers, body = self.http('/api/reviewed/v1/evaluate', value or request(), **kwargs)
        return status, headers, json.loads(body)

    def withdraw(self):
        folder = subject.prepare(self.root, 'release-v02')
        # Old and new release scopes are deliberately withdrawn separately.
        events = [event(self.folder,'source','E167-P',number=1),
                  event(folder,'source','E167-P',number=2)]
        approve_fixture(folder,version=2,entries=events)
        subject.Registry(self.root).activate('release-v02')

    def test_cli_requires_explicit_root_and_never_prepares_or_activates(self):
        with patch.object(ui,'create_server') as create, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit): ui.main([])
            create.assert_not_called()
        with self.assertRaises(ValueError): ui.create_server(None)

    def test_page_is_registry_mode_and_citations_use_current_authority(self):
        status,headers,body = self.http('/')
        self.assertEqual(status,200)
        self.assertIn('LOCAL REGISTRY MODE',body)
        self.assertNotIn('NOT AN ACTIVATED SERVING RELEASE',body)
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
        status,_,out = self.evaluate()
        self.assertEqual((status,out['status']),(200,'supported'))
        for ref in out['citation_refs']:
            status,headers,body = self.http(ref['href'])
            passage = next(p for p in out['context']['passages'] if p['source_id']==ref['source_id'])
            self.assertEqual(status,200)
            from html import unescape
            self.assertIn(passage['quote'],unescape(body))
            self.assertIn('CURRENT WITHDRAWAL AUTHORITY CHECKED',body)
            self.assertNotIn('DEVELOPMENT PREVIEW',body)
            self.assertEqual(headers['Cache-Control'],'no-store')

    def test_clarification_and_scoped_pressure_abstention(self):
        _,_,out = self.evaluate(request(product='family_unknown',context='unknown'))
        self.assertEqual(out['status'],'needs_clarification')
        _,_,out = self.evaluate(request(context='hydrophobic_deposits',items=['pressure_limit']))
        self.assertEqual(out['status'],'abstained')
        self.assertEqual(out['items'][0]['state'],'abstained')
        self.assertIsNotNone(out['items'][0]['absence_scope'])

    def test_missing_root_has_no_preview_fallback_and_creates_nothing(self):
        missing = Path(self.temp.name)/'missing'
        server = self.start(missing)
        with patch('demo.documentary.Handoff.evaluate',side_effect=AssertionError('No preview fallback')):
            _,_,out = self.evaluate(server=server)
        self.assertEqual(out['response_reason'],'release_not_activated')
        self.assertEqual(out['context']['passages'],[])
        self.assertFalse(missing.exists())

    def test_invalid_authority_discards_answer_and_old_source_quote(self):
        _,_,out = self.evaluate()
        href = out['citation_refs'][0]['href']
        quote = out['context']['passages'][0]['quote']
        (self.root/'active.json').unlink()
        with patch('demo.documentary.Handoff.evaluate',side_effect=AssertionError('No preview fallback')):
            _,_,failed = self.evaluate()
        self.assertEqual(failed['response_reason'],'invalid_authority')
        self.assertEqual(failed['citation_refs'],[])
        status,_,body = self.http(href)
        self.assertEqual(status,503)
        self.assertNotIn(quote,body)
        self.assertNotIn(str(self.root),body)

    def test_withdrawal_holds_both_current_and_bookmarked_sources_without_hiding_independent_task(self):
        _,_,before = self.evaluate()
        old = next(x for x in before['citation_refs'] if x['source_id']=='E167-P')
        quote = next(x for x in before['context']['passages'] if x['source_id']=='E167-P')['quote']
        self.withdraw()
        combined = request()
        independent = deepcopy(combined['tasks'][0]);independent.update(task_id='B',deposit_context='hydrophobic_deposits')
        combined['tasks'].append(independent)
        _,_,out = self.evaluate(combined)
        states = {x['task_id']:x['state'] for x in out['items']}
        self.assertEqual(states,{'A':'quarantined','B':'supported'})
        self.assertNotIn('E167-P',[x['source_id'] for x in out['context']['passages']])
        for href in (old['href'],'/reviewed/v1/releases/release-v02/sources/E167-P'):
            status,headers,body = self.http(href)
            self.assertEqual(status,200)
            self.assertIn('Source held',body)
            self.assertNotIn(quote,body)
            self.assertEqual(headers['Cache-Control'],'no-store')

    def test_request_cannot_select_authority_and_origin_and_host_are_checked(self):
        for key in ('candidate','registry_root','data_root'):
            value = request();value[key]='elsewhere'
            status,_,out = self.evaluate(value)
            self.assertEqual(status,400)
            self.assertEqual(out['errors'][0]['code'],'unknown_authority_field')
        self.assertEqual(self.evaluate(headers={'Origin':'https://untrusted.example'})[0],403)
        self.assertEqual(self.http('/',headers={'Host':'untrusted.example'})[0],403)
        self.assertEqual(self.http('/api/registry/activate')[0],404)

    def test_malformed_authority_returns_controlled_503_without_quote_or_details(self):
        path = self.folder/'release.json'
        original = path.read_bytes()
        for malformed in ('null', '[{}]'):
            with self.subTest(authority=malformed):
                path.write_text(malformed,encoding='utf-8')
                try:
                    with self.assertLogs('demo.registry_ui',level='ERROR') as logs:
                        status,_,body = self.http('/reviewed/v1/releases/release-v01/sources/E167-P')
                    self.assertEqual(status,503)
                    self.assertEqual(json.loads(body),{'error':'Registry source unavailable; no quotation delivered'})
                    self.assertNotIn(str(self.root),body)
                    self.assertNotIn('TypeError',body)
                    self.assertIn('TypeError',' '.join(logs.output))
                    _,_,out = self.evaluate()
                    self.assertEqual(out['response_reason'],'invalid_authority')
                    self.assertEqual(out['context']['passages'],[])
                finally:
                    path.write_bytes(original)

    def test_unexpected_source_and_render_errors_are_generic_and_logged_privately(self):
        href = '/reviewed/v1/releases/release-v01/sources/E167-P'
        cases = [(subject.Registry,'source',TypeError('sensitive-backend-detail')),
                 (subject.Registry,'source',KeyError('sensitive-backend-detail')),
                 (ui,'source_html',TypeError('sensitive-render-detail')),
                 (ui,'source_html',KeyError('sensitive-render-detail'))]
        for owner,name,error in cases:
            with self.subTest(boundary=name,error=type(error).__name__):
                with patch.object(owner,name,side_effect=error), self.assertLogs('demo.registry_ui',level='ERROR') as logs:
                    status,_,body = self.http(href)
                self.assertEqual(status,503)
                self.assertEqual(json.loads(body),{'error':'Registry source unavailable; no quotation delivered'})
                self.assertNotIn('sensitive-',body)
                self.assertNotIn('sensitive-',' '.join(logs.output))
                self.assertIn(type(error).__name__,' '.join(logs.output))

    def test_unknown_source_is_404_only_under_verified_authority(self):
        href = '/reviewed/v1/releases/release-v01/sources/unregistered-source'
        status,_,body = self.http(href)
        self.assertEqual((status,json.loads(body)),(404,{'error':'Unregistered source'}))
        (self.folder/'release.json').write_text('null',encoding='utf-8')
        with self.assertLogs('demo.registry_ui',level='ERROR'):
            status,_,body = self.http(href)
        self.assertEqual(status,503)
        self.assertNotIn('Unregistered source',body)

    def run_dom(self, scenario='baseline'):
        node = shutil.which('node')
        self.assertIsNotNone(node,'Node/jsdom required for real UI regression; no silent skip')
        result = subprocess.run([node,str(ROOT/'tests/ui/registry.cjs'),self.base,scenario],
                                cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=40,
                                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return json.loads(result.stdout)

    def test_dom_actual_form_renderer_citations_clarification_and_abstention(self):
        self.assertEqual(self.run_dom()['status'],'passed')

    def test_dom_withdrawn_support_has_no_procedure_and_live_warning_remains(self):
        self.withdraw()
        self.assertEqual(self.run_dom('withdrawn')['status'],'passed')

    def test_dom_missing_authority_has_no_fallback_or_stale_citations(self):
        (self.root/'active.json').unlink()
        self.assertEqual(self.run_dom('unavailable')['status'],'passed')

    def test_dom_inputs_changed_during_response_do_not_display_old_support(self):
        self.assertEqual(self.run_dom('stale')['status'],'passed')

    def test_dom_timeout_of_uncooperative_fetch_recovers_and_allows_retry(self):
        self.assertEqual(self.run_dom('timeout')['status'],'passed')

    def test_dom_late_fetch_after_timeout_cannot_replace_successful_retry(self):
        self.assertEqual(self.run_dom('late-fetch')['status'],'passed')

    def test_dom_stalled_body_deadline_cannot_replace_successful_retry(self):
        self.assertEqual(self.run_dom('late-body')['status'],'passed')

    def test_http_reads_never_prepare_activate_or_write_authority(self):
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        before = {p.relative_to(self.root):digest(p) for p in self.root.rglob('*') if p.is_file()}
        with patch.object(subject,'prepare',side_effect=AssertionError('No preparation')), \
                patch.object(subject.Registry,'activate',side_effect=AssertionError('No activation')):
            _,_,out = self.evaluate()
            self.assertEqual(out['status'],'supported')
            for ref in out['citation_refs']: self.assertEqual(self.http(ref['href'])[0],200)
        self.assertEqual(before,{p.relative_to(self.root):digest(p) for p in self.root.rglob('*') if p.is_file()})


if __name__ == '__main__': unittest.main()
