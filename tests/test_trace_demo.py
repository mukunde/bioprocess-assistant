"""Read-only summaries and the separate demo use only disposable test authority."""
from copy import deepcopy
import contextlib
import io
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from demo import registry_demo, registry_tracing, trace_summary as subject
from tests import test_registry_ui as baseline


def span(*, child=False):
    start = 1793790000000000000
    return {'schema': 'registry-trace/v1',
            'name': 'registry.evaluate' if child else 'POST /api/reviewed/v1/evaluate',
            'trace_id': 'a'*32, 'span_id': ('b' if child else 'c')*16,
            'parent_span_id': 'c'*16 if child else None,
            'kind': 'INTERNAL' if child else 'SERVER',
            'start_time_unix_nano': start, 'end_time_unix_nano': start+1000000,
            'duration_ms': 1.0, 'status': 'UNSET', 'resource': dict(registry_tracing.RESOURCE),
            'attributes': {'bioprocess.outcome': 'supported', 'bioprocess.release_id': 'release-v01'}}


class TraceSummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='trace-summary-')
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name)/'trace.jsonl'

    def write(self, rows):
        self.file.write_text(''.join(json.dumps(row)+'\n' for row in rows), encoding='utf-8')

    def test_parentage_order_and_read_only_file_bytes(self):
        self.write([span(child=True), span()])
        before = self.file.read_bytes()
        summary = subject.read_summary(self.file)
        self.assertTrue(summary['traces'][0]['complete'])
        self.assertEqual(summary['http_requests'], 1)
        text = subject.text_summary(summary)
        self.assertIn('registry.evaluate', text)
        self.assertIn('supported', text)
        self.assertIn('Source views have separate trace IDs', text)
        self.assertEqual(before, self.file.read_bytes())

    def test_untrusted_fields_and_values_never_reach_terminal_or_html(self):
        bad = []
        for key, value in [('name', '<script>PRIVATE</script>'), ('resource', {'secret': 'PRIVATE'}),
                           ('attributes', {'request.body': 'PRIVATE'}),
                           ('attributes', {'bioprocess.source_id': '\x1bPRIVATE'}),
                           ('trace_id', 'PRIVATE'), ('duration_ms', float('nan'))]:
            row = span(); row[key] = value; bad.append(row)
        extra = span(); extra['quote'] = 'PRIVATE'; bad.append(extra)
        self.write(bad + [span()])
        self.file.write_bytes(self.file.read_bytes()+b'{"schema":"PRIVATE","schema":"PRIVATE"}\n')
        summary = subject.read_summary(self.file)
        self.assertEqual(summary['ignored_records'], 8)
        self.assertEqual(summary['spans'], 1)
        self.assertNotIn('PRIVATE', subject.text_summary(summary))
        self.assertNotIn('PRIVATE', subject.html_summary(summary).decode())

    def test_partial_line_is_pending_then_visible_after_newline(self):
        self.write([span()])
        with self.file.open('ab') as output:
            output.write(json.dumps(span(child=True)).encode())
        summary = subject.read_summary(self.file)
        self.assertEqual(summary['pending_records'], 1)
        self.assertFalse(summary['traces'][0]['complete'])
        with self.file.open('ab') as output: output.write(b'\n')
        self.assertTrue(subject.read_summary(self.file)['traces'][0]['complete'])

    def test_missing_cross_trace_parent_and_duplicate_roots_are_not_invented(self):
        root, child = span(), span(child=True)
        child['trace_id'] = 'd'*32
        self.write([root, child])
        summary = subject.read_summary(self.file)
        self.assertEqual(len(summary['traces']), 2)
        self.assertTrue(all(not t['complete'] for t in summary['traces']))
        self.assertIn('partial / unlinked', subject.text_summary(summary))
        second = deepcopy(root); second['span_id'] = 'e'*16
        self.write([root, second, span(child=True)])
        self.assertFalse(subject.read_summary(self.file)['traces'][0]['complete'])

    def test_missing_large_and_malformed_files_have_controlled_diagnostics(self):
        with self.assertRaises(subject.SummaryUnavailable) as failure:
            subject.read_summary(self.file)
        self.assertNotIn(self.temp.name, str(failure.exception))
        self.write([span()])
        with patch.object(subject, 'MAX_BYTES', 16), self.assertRaises(subject.SummaryUnavailable):
            subject.read_summary(self.file)
        self.file.write_bytes(b'not json\n\xff\n'+b'x'*17000+b'\n')
        summary = subject.read_summary(self.file)
        self.assertEqual(summary['ignored_records'], 3)
        self.assertEqual(summary['spans'], 0)
        self.write([span(), span(child=True)])
        with patch.object(subject, 'MAX_SPANS', 1), self.assertRaises(subject.SummaryUnavailable):
            subject.read_summary(self.file)

    def test_duplicate_span_and_impossible_time_are_rejected(self):
        invalid = span(); invalid['end_time_unix_nano'] = -1
        self.write([span(), span(), invalid])
        summary = subject.read_summary(self.file)
        self.assertEqual((summary['spans'], summary['ignored_records']), (1, 2))

    def test_rejection_without_child_does_not_infer_dispatch_or_missing_telemetry(self):
        root = span()
        root['attributes'].update({'http.response.status_code': 400,
                                   'bioprocess.outcome': 'invalid_request'})
        self.write([root])
        summary = subject.read_summary(self.file)
        self.assertIsNone(summary['traces'][0]['complete'])
        self.assertIn('root only / HTTP rejection', subject.text_summary(summary))
        self.assertNotIn('partial / unlinked', subject.text_summary(summary))
        child = span(child=True)
        child['attributes']['bioprocess.outcome'] = 'invalid_request'
        self.write([root, child])
        self.assertTrue(subject.read_summary(self.file)['traces'][0]['complete'])
        root['attributes']['http.response.status_code'] = 200
        self.write([root])
        self.assertFalse(subject.read_summary(self.file)['traces'][0]['complete'])

    def test_standalone_summary_needs_only_standard_library(self):
        self.write([span(), span(child=True)])
        result = subprocess.run([sys.executable, '-S', '-m', 'demo.trace_summary', str(self.file)],
                                cwd=baseline.ROOT, capture_output=True, text=True,
                                encoding='utf-8', timeout=15,
                                env=dict(os.environ, PYTHONIOENCODING='utf-8'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('metadata only', result.stdout)


class TraceDemoTests(unittest.TestCase):
    def setUp(self):
        self.fixture = baseline.RegistryUIIntegrationTests('test_clarification_and_scoped_pressure_abstention')
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.trace_file = Path(self.fixture.temp.name)/'new-session.jsonl'
        self.tracing = registry_tracing.configure(trace_file=self.trace_file)
        self.addCleanup(self.tracing.close)
        self.server = registry_demo.create_server(self.fixture.root, self.trace_file, port=0, tracing=self.tracing)
        thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        def stop():
            self.server.shutdown(); self.server.server_close(); thread.join(timeout=5)
        self.addCleanup(stop)

    def test_request_source_summary_and_baseline_bodies_match(self):
        status, _, page = self.fixture.http('/', server=self.server)
        self.assertEqual(status, 200)
        self.assertIn('href="/demo/traces"', page)
        old_status, _, old = self.fixture.evaluate()
        status, headers, actual = self.fixture.evaluate(server=self.server)
        self.assertEqual((status, actual), (old_status, old))
        ref = actual['citation_refs'][0]
        old_status, _, old_html = self.fixture.http(ref['href'])
        status, _, actual_html = self.fixture.http(ref['href'], server=self.server)
        self.assertEqual((status, actual_html), (old_status, old_html))
        self.assertTrue(self.tracing.flush())
        before = self.trace_file.read_bytes()
        status, summary_headers, summary = self.fixture.http('/demo/traces', server=self.server)
        self.assertEqual(status, 200)
        self.assertIn(headers['X-Trace-Id'], summary)
        self.assertIn('registry.evaluate', summary)
        self.assertIn('registry.source', summary)
        self.assertNotIn(actual['context']['passages'][0]['quote'], summary)
        self.assertNotIn('X-Trace-Id', summary_headers)  # Viewer does not trace itself.
        self.assertEqual(summary_headers['Cache-Control'], 'no-store')
        self.assertIn("frame-ancestors 'none'", summary_headers['Content-Security-Policy'])
        self.assertTrue(self.tracing.flush())
        self.assertEqual(before, self.trace_file.read_bytes())

    def test_summary_failure_does_not_break_later_guidance_or_leak_error(self):
        with patch.object(subject, 'read_summary', side_effect=RuntimeError('PRIVATE_PATH_QUOTE')):
            status, _, body = self.fixture.http('/demo/traces', server=self.server)
            self.assertEqual(status, 503)
            self.assertNotIn('PRIVATE', body)
            self.assertEqual(self.fixture.evaluate(server=self.server)[2], self.fixture.evaluate()[2])

    def test_real_http_rejections_remain_visible_with_correct_child_coverage(self):
        completed = threading.Event()
        original = self.server.RequestHandlerClass
        class Completed(original):
            def finish(self):
                try:
                    super().finish()
                finally:
                    completed.set()
        self.server.RequestHandlerClass = Completed
        cases = [
            ('POST', '/api/reviewed/v1/evaluate', b'{PRIVATE_JSON', None, 400, None),
            ('POST', '/api/reviewed/v1/evaluate', b'{}', None, 400, True),
            ('POST', '/', b'{}', None, 404, True),
            ('GET', '/api/reviewed/v1/evaluate', None, None, 404, True),
            ('POST', '/PRIVATE_ROUTE', b'{}', None, 404, True),
            ('POST', '/reviewed/v1/releases/release-v01/sources/E167-P', b'{}', None, 404, True),
            ('POST', '/api/reviewed/v1/evaluate', b'{}', 'untrusted.example', 403, None),
        ]
        expected_names = ['POST /api/reviewed/v1/evaluate', 'POST /api/reviewed/v1/evaluate', 'POST /',
                          'GET /api/reviewed/v1/evaluate', 'POST unmatched',
                          'POST '+registry_tracing.SOURCE_ROUTE, 'POST /api/reviewed/v1/evaluate']
        for index, (method, path, body, host, status, coverage) in enumerate(cases):
            with self.subTest(method=method, path=path, status=status):
                completed.clear()
                connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=8)
                try:
                    headers = {'Content-Type': 'application/json', 'Connection': 'close'}
                    if host: headers['Host'] = host
                    connection.request(method, path, body, headers)
                    response = connection.getresponse()
                    trace_id = response.getheader('X-Trace-Id')
                    self.assertEqual(response.status, status); response.read()
                finally:
                    connection.close()
                self.assertTrue(completed.wait(5))
                self.assertTrue(self.tracing.flush())
                summary = subject.read_summary(self.trace_file)
                self.assertEqual(summary['ignored_records'], 0)
                trace = next(t for t in summary['traces'] if t['trace_id'] == trace_id)
                self.assertIs(trace['complete'], coverage)
                self.assertEqual(trace['root']['name'], expected_names[index])
                self.assertEqual(trace['root']['attributes']['http.response.status_code'], status)
                self.assertNotIn('PRIVATE', subject.text_summary(summary))

    def test_unexpected_optional_metadata_errors_do_not_block_cli_or_leak_details(self):
        for error in (PermissionError('PRIVATE_METADATA'), RuntimeError('PRIVATE_METADATA')):
            with self.subTest(error=type(error).__name__):
                server = Mock(); server.serve_forever.side_effect = KeyboardInterrupt
                server.server_port = 8786
                tracing = Mock()
                with patch.object(registry_demo.importlib.metadata, 'version', side_effect=error), \
                        patch.object(registry_demo, 'create_server', return_value=server) as create, \
                        patch.object(registry_demo.registry_tracing, 'configure', return_value=tracing) as configure, \
                        contextlib.redirect_stdout(io.StringIO()) as text:
                    code = registry_demo.main(['--registry-root', str(self.fixture.root),
                                               '--trace-dir', str(Path(self.fixture.temp.name)/'metadata-failure')])
                self.assertEqual(code, 0)
                create.assert_called_once(); configure.assert_called_once()
                server.serve_forever.assert_called_once()
                server.server_close.assert_called_once(); tracing.close.assert_called_once()
                self.assertIn('Optional SDK metadata unavailable', text.getvalue())
                self.assertNotIn('PRIVATE_METADATA', text.getvalue())

    def test_viewer_accepts_no_client_file_path_and_rejects_wrong_host(self):
        self.assertEqual(self.fixture.http('/demo/traces?file=private', server=self.server)[0], 404)
        self.assertEqual(self.fixture.http('/demo/traces', server=self.server,
                                          headers={'Host': 'untrusted.example'})[0], 403)
        with self.assertRaises(ValueError):
            registry_demo.create_server(self.fixture.root, self.fixture.root/'private.jsonl', port=0)

    def test_missing_authority_never_creates_or_activates_store(self):
        missing = Path(self.fixture.temp.name)/'missing-authority'
        output = Path(self.fixture.temp.name)/'never-created-traces'
        with contextlib.redirect_stdout(io.StringIO()) as text:
            code = registry_demo.main(['--registry-root', str(missing), '--trace-dir', str(output)])
        self.assertEqual(code, 2)
        self.assertFalse(missing.exists()); self.assertFalse(output.exists())
        self.assertNotIn(str(missing), text.getvalue())

    def test_cli_sessions_are_unique_and_resources_close(self):
        server = Mock(); server.serve_forever.side_effect = KeyboardInterrupt
        server.server_port = 8786
        tracing = Mock()
        directory = Path(self.fixture.temp.name)/'sessions'
        with patch.object(registry_demo, 'create_server', return_value=server), \
                patch.object(registry_demo.registry_tracing, 'configure', return_value=tracing) as configure, \
                contextlib.redirect_stdout(io.StringIO()):
            for _ in range(2):
                self.assertEqual(registry_demo.main(['--registry-root', str(self.fixture.root),
                                                      '--trace-dir', str(directory)]), 0)
        calls = configure.call_args_list
        self.assertNotEqual(calls[0].kwargs['trace_file'], calls[1].kwargs['trace_file'])
        self.assertEqual(calls[0].kwargs['protected_root'], self.fixture.root.resolve())
        self.assertEqual(tracing.close.call_count, 2)
        self.assertEqual(server.server_close.call_count, 2)

    def test_unavailable_trace_sink_and_summary_do_not_block_guidance(self):
        filename = Path(self.fixture.temp.name)/'missing-parent'/'trace.jsonl'
        tracing = registry_tracing.configure(trace_file=filename)
        self.addCleanup(tracing.close)
        self.assertIsNone(tracing.tracer)
        server = registry_demo.create_server(self.fixture.root, filename, port=0, tracing=tracing)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        try:
            self.assertEqual(self.fixture.evaluate(server=server)[2], self.fixture.evaluate()[2])
            self.assertEqual(self.fixture.http('/demo/traces', server=server)[0], 503)
            self.assertFalse(filename.parent.exists())
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=5)

    def test_bind_failure_closes_tracer_without_raw_exception(self):
        tracing = Mock()
        with patch.object(registry_demo, 'create_server', side_effect=OSError('PRIVATE_BIND')), \
                patch.object(registry_demo.registry_tracing, 'configure', return_value=tracing), \
                contextlib.redirect_stdout(io.StringIO()) as text:
            code = registry_demo.main(['--registry-root', str(self.fixture.root),
                                      '--trace-dir', str(Path(self.fixture.temp.name)/'session')])
        self.assertEqual(code, 2); tracing.close.assert_called_once()
        self.assertNotIn('PRIVATE_BIND', text.getvalue())

    def test_cli_rejects_authority_trace_directory_before_writes(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            registry_demo.main(['--registry-root', str(self.fixture.root),
                                '--trace-dir', str(self.fixture.root/'traces')])
        self.assertFalse((self.fixture.root/'traces').exists())
