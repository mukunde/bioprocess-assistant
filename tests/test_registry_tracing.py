"""Real OTel SDK, disposable authority and loopback-only collectors; no model calls."""
import builtins
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

from opentelemetry import trace
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from demo import registry_tracing as subject, registry_ui_v02 as ui
from tests import test_registry_ui as baseline


class RegistryTracingTests(unittest.TestCase):
    def setUp(self):
        self.request_servers = []
        self.fixture = baseline.RegistryUIIntegrationTests(
            "test_clarification_and_scoped_pressure_abstention")
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.exporter = InMemorySpanExporter()
        self.tracing = self.track(subject.configure(exporters=[self.exporter]))
        self.server = self.start(self.tracing)

    def track(self, tracing):
        self.addCleanup(tracing.close)
        return tracing

    def start(self, tracing, root=None):
        server = ui.create_server(root or self.fixture.root, port=0, tracing=tracing)
        # Reading Content-Length bytes does not imply do_POST's span finally ran.
        # Synchronize test collection with handler completion, not exporter timing.
        server.test_condition = threading.Condition()
        server.test_pending = 0
        original_finish = server.finish_request
        def finish_request(*args):
            with server.test_condition:
                server.test_pending += 1
            try:
                original_finish(*args)
            finally:
                with server.test_condition:
                    server.test_pending -= 1
                    server.test_condition.notify_all()
        server.finish_request = finish_request
        self.request_servers.append(server)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        def stop():
            server.shutdown(); server.server_close(); thread.join(timeout=5)
        self.addCleanup(stop)
        return server

    def evaluate(self, value=None, server=None, headers=None):
        return self.fixture.evaluate(value, server=server or self.server, headers=headers)

    def spans(self, tracing=None, exporter=None):
        for server in self.request_servers:
            with server.test_condition:
                self.assertTrue(server.test_condition.wait_for(lambda: server.test_pending == 0, timeout=5),
                                'HTTP handler did not finish before trace collection')
        self.assertTrue((tracing or self.tracing).flush())
        return (exporter or self.exporter).get_finished_spans()

    def assert_pair(self, spans, child_name):
        parent = next(s for s in spans if s.kind.name == "SERVER")
        child = next(s for s in spans if s.name == child_name)
        self.assertIsNone(parent.parent)
        self.assertEqual(child.parent.span_id, parent.context.span_id)
        self.assertEqual(child.context.trace_id, parent.context.trace_id)
        self.assertGreaterEqual(parent.end_time, parent.start_time)
        return parent, child

    def test_evaluation_has_real_parent_child_spans_and_correlating_header(self):
        status, headers, data = self.evaluate()
        self.assertEqual((status, data["status"]), (200, "supported"))
        parent, child = self.assert_pair(self.spans(), "registry.evaluate")
        self.assertEqual(headers["X-Trace-Id"], f"{parent.context.trace_id:032x}")
        for span in (parent, child):
            self.assertEqual(span.attributes["bioprocess.release_id"], "release-v01")
            self.assertEqual(span.attributes["bioprocess.outcome"], "supported")
            self.assertEqual(span.status.status_code.name, "UNSET")
            self.assertFalse(span.events)
        self.assertEqual(parent.attributes["http.response.status_code"], 200)

    def test_span_collection_waits_for_parent_end_after_response_bytes_arrive(self):
        root_waiting, release_root = threading.Event(), threading.Event()
        collecting, collected = threading.Event(), threading.Event()
        result, errors = [], []
        original = subject.Span.end
        def delayed_end(span):
            if span.raw is not None and span.raw.kind.name == 'SERVER':
                root_waiting.set()
                release_root.wait(timeout=5)
            original(span)
        def collect():
            collecting.set()
            try:
                result.extend(self.spans())
            except BaseException as error:
                errors.append(error)
            finally:
                collected.set()
        worker = threading.Thread(target=collect, daemon=True)
        try:
            with patch.object(subject.Span, 'end', delayed_end):
                status, _, data = self.evaluate()
                self.assertEqual((status, data['status']), (200, 'supported'))
                self.assertTrue(root_waiting.wait(timeout=2))
                worker.start()
                self.assertTrue(collecting.wait(timeout=2))
                self.assertFalse(collected.wait(timeout=.05), 'Collector must wait for the HTTP root to end')
                release_root.set()
                self.assertTrue(collected.wait(timeout=5))
        finally:
            release_root.set()
            if worker.ident is not None:
                worker.join(timeout=5)
        self.assertEqual(errors, [])
        self.assert_pair(result, 'registry.evaluate')

    def test_citation_is_a_separate_trace_and_exact_source_body_is_retained(self):
        _, _, data = self.evaluate()
        first = self.spans()
        ref = data["citation_refs"][0]
        a, _, old = self.fixture.http(ref["href"])
        b, headers, actual = self.fixture.http(ref["href"], server=self.server)
        self.assertEqual((a, old), (b, actual))
        spans = [s for s in self.spans() if s not in first]
        parent, child = self.assert_pair(spans, "registry.source")
        self.assertNotEqual(parent.context.trace_id, first[0].context.trace_id)
        self.assertEqual(child.attributes["bioprocess.source_id"], ref["source_id"])
        self.assertEqual(parent.attributes["http.route"], subject.SOURCE_ROUTE)
        self.assertEqual(headers["X-Trace-Id"], f"{parent.context.trace_id:032x}")

    def test_all_eight_responses_and_thirteen_sources_match_untraced_baseline(self):
        cases = [
            ("sure", "precipitated_substances", ["cleaning_options", "pressure_limit"]),
            ("sure_lx", "precipitated_substances", ["cleaning_options"]),
            ("sure_lx", "hydrophobic_deposits", ["pressure_limit"]),
            ("sure", "hydrophobic_deposits", ["cleaning_options", "pressure_limit"]),
            ("family_unknown", "hydrophobic_deposits", ["cleaning_options", "pressure_limit"]),
            ("sure", "mixed_other", ["cleaning_options"]),
            ("contradictory", "precipitated_substances", ["pressure_limit"]),
            ("other", "mixed_other", ["cleaning_options", "pressure_limit"]),
        ]
        sources = set()
        for product, context, items in cases:
            value = baseline.request(product=product, context=context, items=items)
            old_status, _, old = self.fixture.evaluate(value)
            status, _, actual = self.evaluate(value)
            self.assertEqual((status, actual), (old_status, old))
            for ref in actual["citation_refs"]:
                if ref["href"] not in sources:
                    old_status, _, old = self.fixture.http(ref["href"])
                    status, _, actual_html = self.fixture.http(ref["href"], server=self.server)
                    self.assertEqual((status, actual_html), (old_status, old))
                    sources.add(ref["href"])
        self.assertEqual(len(sources), 13)
        spans = self.spans()
        evaluations = [s for s in spans if s.name == "registry.evaluate"]
        self.assertEqual(len(evaluations), 8)
        self.assertEqual({s.attributes["bioprocess.outcome"] for s in evaluations},
                         {"supported", "partial", "needs_clarification", "abstained"})
        self.assertTrue(all(s.status.status_code.name == "UNSET" for s in evaluations))

    def test_request_headers_ids_query_strings_and_environment_are_not_captured(self):
        sentinel = "PRIVATE_SENTINEL_NEVER_CAPTURE"
        exporter = InMemorySpanExporter()
        with patch.dict(os.environ, {"OTEL_RESOURCE_ATTRIBUTES": "secret="+sentinel}):
            tracing = self.track(subject.configure(exporters=[exporter]))
        server = self.start(tracing)
        request = baseline.request(); request["request_id"] = sentinel
        self.evaluate(request, server, {"Authorization": sentinel, "User-Agent": sentinel,
                       "baggage": "private="+sentinel,
                       "traceparent": "00-"+"a"*32+"-"+"b"*16+"-01"})
        self.fixture.http("/unknown?private="+sentinel, server=server)
        spans = self.spans(tracing, exporter)
        serialized = "\n".join(s.to_json() for s in spans)
        self.assertNotIn(sentinel, serialized)
        self.assertNotIn("a"*32, serialized)
        self.assertNotIn("blockquote", serialized)
        for span in spans:
            self.assertEqual(dict(span.resource.attributes), subject.RESOURCE)
            self.assertTrue(all(subject.permitted(k, v) for k, v in span.attributes.items()))
            self.assertFalse(span.events)
            self.assertIsNone(span.status.description)
        self.assertIn("GET unmatched", [s.name for s in spans])

    def test_source_failure_records_only_controlled_error_not_message_or_stack(self):
        with patch.object(baseline.subject.Registry, "source",
                          side_effect=RuntimeError("PRIVATE_QUOTE_AND_PASSWORD")):
            status, _, body = self.fixture.http(
                "/reviewed/v1/releases/release-v01/sources/E167-P", server=self.server)
        self.assertEqual(status, 503)
        self.assertNotIn("PRIVATE_", body)
        parent, child = self.assert_pair(self.spans(), "registry.source")
        self.assertEqual(parent.status.status_code.name, "ERROR")
        self.assertEqual(child.status.status_code.name, "ERROR")
        text = parent.to_json()+child.to_json()
        self.assertNotIn("PRIVATE_", text)
        self.assertNotIn("exception.stacktrace", text)

    def test_invalid_request_has_controlled_outcome_without_user_input_metadata(self):
        request = baseline.request(); request["extra"] = "PRIVATE_PAYLOAD"
        status, _, _ = self.evaluate(request)
        self.assertEqual(status, 400)
        spans = self.spans()
        # Validation occurs inside Registry.evaluate; it still gets a child span.
        parent, child = self.assert_pair(spans, "registry.evaluate")
        self.assertEqual(child.attributes["bioprocess.outcome"], "invalid_request")
        self.assertEqual(parent.attributes["http.response.status_code"], 400)
        self.assertNotIn("PRIVATE_PAYLOAD", "".join(s.to_json() for s in spans))

    def test_malformed_json_is_traced_without_a_registry_call_or_body_capture(self):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        self.addCleanup(connection.close)
        connection.request("POST", "/api/reviewed/v1/evaluate", b'{PRIVATE_BAD_JSON',
                           {"Content-Type": "application/json", "Connection": "close"})
        response = connection.getresponse()
        self.assertEqual(response.status, 400); response.read()
        spans = self.spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].attributes["bioprocess.outcome"], "invalid_request")
        self.assertEqual(spans[0].status.status_code.name, "UNSET")
        self.assertNotIn("PRIVATE_BAD_JSON", spans[0].to_json())

    def test_missing_authority_preserves_unavailable_without_creating_store(self):
        missing = Path(self.fixture.temp.name)/"never-created"
        server = self.start(self.tracing, missing)
        _, _, data = self.evaluate(server=server)
        self.assertEqual(data["status"], "unavailable")
        self.assertFalse(missing.exists())
        parent, child = self.assert_pair(self.spans(), "registry.evaluate")
        self.assertEqual(child.attributes["error.type"], "registry_unavailable")
        self.assertEqual(parent.status.status_code.name, "ERROR")

    def test_withdrawal_and_bookmarked_quote_refusal_are_unchanged(self):
        _, _, before = self.evaluate()
        href = next(c["href"] for c in before["citation_refs"] if c["source_id"] == "E167-P")
        self.fixture.withdraw()  # Disposable fixture only.
        status, _, data = self.evaluate()
        old_status, _, old = self.fixture.evaluate()
        self.assertEqual((status, data), (old_status, old))
        status, _, body = self.fixture.http(href, server=self.server)
        self.assertEqual(status, 200)
        self.assertIn("Source held", body)
        self.assertNotIn("<blockquote>", body)
        self.assertEqual(data["items"][0]["state"], "quarantined")

    def test_concurrent_requests_do_not_share_parents(self):
        errors = []
        def request():
            try:
                self.assertEqual(self.evaluate()[0], 200)
            except Exception as error:
                errors.append(error)
        threads = [threading.Thread(target=request) for _ in range(3)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=8)
        self.assertFalse(errors)
        spans = self.spans()
        parents = [s for s in spans if s.kind.name == "SERVER"]
        children = [s for s in spans if s.name == "registry.evaluate"]
        self.assertEqual(len(parents), 3)
        self.assertEqual(len({s.context.trace_id for s in parents}), 3)
        self.assertEqual({s.parent.span_id for s in children}, {s.context.span_id for s in parents})

    def test_global_provider_is_not_replaced(self):
        provider = trace.get_tracer_provider()
        tracing = self.track(subject.configure(exporters=[InMemorySpanExporter()]))
        self.assertIs(trace.get_tracer_provider(), provider)
        self.assertIsNotNone(tracing.tracer)

    def test_sdk_internal_metrics_do_not_use_an_ambient_meter_backend(self):
        with patch.dict(os.environ, {"OTEL_PYTHON_SDK_INTERNAL_METRICS_ENABLED": "true"}), \
                patch("opentelemetry.metrics.get_meter_provider",
                      side_effect=AssertionError("Ambient metrics forbidden")):
            tracing = self.track(subject.configure(exporters=[InMemorySpanExporter()]))
        self.assertIsNotNone(tracing.tracer)
        self.assertEqual(self.evaluate(server=self.start(tracing))[0], 200)

    def test_sdk_span_creation_attributes_and_end_failures_do_not_change_response(self):
        class BrokenSpan:
            def set_attribute(self, *a): raise RuntimeError("PRIVATE_SDK")
            def set_status(self, *a): raise RuntimeError("PRIVATE_SDK")
            def end(self): raise RuntimeError("PRIVATE_SDK")
            def get_span_context(self): raise RuntimeError("PRIVATE_SDK")
        class BrokenTracer:
            def start_span(self, *a, **k): return BrokenSpan()
        server = self.start(subject.Tracing(BrokenTracer()))
        expected = self.fixture.evaluate()[2]
        self.assertEqual(self.evaluate(server=server)[2], expected)
        class NoTracer:
            def start_span(self, *a, **k): raise RuntimeError("PRIVATE_SDK")
        server = self.start(subject.Tracing(NoTracer()))
        self.assertEqual(self.evaluate(server=server)[2], expected)

    def test_export_failure_and_broken_diagnostic_logger_are_nonblocking(self):
        class BrokenExporter:
            def export(self, spans): raise OSError("PRIVATE_EXPORT_DETAIL")
            def shutdown(self): raise OSError("PRIVATE_SHUTDOWN_DETAIL")
        tracing = self.track(subject.configure(exporters=[BrokenExporter()]))
        server = self.start(tracing)
        with patch.object(subject.LOGGER, "warning", side_effect=OSError("PRIVATE_LOG_DETAIL")):
            self.assertEqual(self.evaluate(server=server)[2], self.fixture.evaluate()[2])
            tracing.flush()
        self.assertGreater(tracing.export_failures, 0)

    def test_sdk_failure_health_is_counted_and_warnings_are_once_per_phase(self):
        class BrokenSpan:
            def set_attribute(self, *a): raise RuntimeError("PRIVATE_SDK_DETAIL")
            def set_status(self, *a): raise RuntimeError("PRIVATE_SDK_DETAIL")
            def get_span_context(self): raise RuntimeError("PRIVATE_SDK_DETAIL")
            def end(self): raise RuntimeError("PRIVATE_SDK_DETAIL")
        class BrokenTracer:
            def start_span(self, *a, **k): return BrokenSpan()
        tracing = subject.Tracing(BrokenTracer())
        with patch.object(subject.LOGGER, "warning") as warning:
            for _ in range(2):
                with tracing.span("registry.evaluate") as span:
                    span.attributes({"http.request.method": "GET"})
                    span.error("operation_failed")
                    self.assertIsNone(span.trace_id())
        self.assertEqual(tracing.sdk_failures,
                         {"attributes": 4, "status": 2, "context": 2, "end": 2})
        self.assertEqual(warning.call_count, 4)
        self.assertNotIn("PRIVATE", str(warning.call_args_list))
        self.assertEqual(tracing.export_failures, 0)
        class BrokenStart:
            def start_span(self, *a, **k): raise RuntimeError("PRIVATE_START")
        tracing = subject.Tracing(BrokenStart())
        with patch.object(subject.LOGGER, "warning", side_effect=OSError("PRIVATE_LOG")) as warning:
            server = self.start(tracing)
            for _ in range(2):
                self.assertEqual(self.evaluate(server=server)[2], self.fixture.evaluate()[2])
        self.assertGreaterEqual(tracing.sdk_failures["start"], 4)
        self.assertEqual(warning.call_count, 1)
        self.assertNotIn("PRIVATE", str(warning.call_args_list))

    def test_registration_failure_closes_actual_processor_worker_and_file(self):
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        processors, exporters = [], []
        original = subject.JsonLinesExporter
        def file_sink(*args):
            exporter = original(*args); exporters.append(exporter)
            return exporter
        def processor(*args, **kwargs):
            value = BatchSpanProcessor(*args, **kwargs); processors.append(value)
            self.addCleanup(value.shutdown)
            return value
        with patch.object(subject, "JsonLinesExporter", side_effect=file_sink), \
                patch("opentelemetry.sdk.trace.export.BatchSpanProcessor", side_effect=processor), \
                patch.object(TracerProvider, "add_span_processor", side_effect=RuntimeError("PRIVATE")):
            tracing = self.track(subject.configure(trace_file=Path(self.fixture.temp.name)/"partial.jsonl"))
        self.assertIsNone(tracing.tracer)
        self.assertTrue(exporters[0].stream.closed)
        self.assertFalse(processors[0]._batch_processor._worker_thread.is_alive())
        self.assertEqual(self.evaluate(server=self.start(tracing))[0], 200)

    def test_processor_construction_failure_closes_exporter(self):
        exporters = []
        original = subject.JsonLinesExporter
        def file_sink(*args):
            exporter = original(*args); exporters.append(exporter)
            return exporter
        with patch.object(subject, "JsonLinesExporter", side_effect=file_sink), \
                patch("opentelemetry.sdk.trace.export.BatchSpanProcessor", side_effect=RuntimeError("PRIVATE")):
            tracing = self.track(subject.configure(trace_file=Path(self.fixture.temp.name)/"constructor.jsonl"))
        self.assertIsNone(tracing.tracer)
        self.assertTrue(exporters[0].stream.closed)

    def test_partial_cleanup_is_bounded_for_a_stalled_sink(self):
        entered, release = threading.Event(), threading.Event()
        class Stalled:
            def shutdown(self):
                entered.set(); release.wait(5)
        try:
            started = time.monotonic()
            subject.close_partial(Stalled(), timeout=.02)
            self.assertTrue(entered.is_set())
            self.assertLess(time.monotonic()-started, 1)
        finally:
            release.set()

    def test_blocked_export_does_not_block_later_http_or_unbounded_shutdown(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        class BlockingExporter:
            def export(self, spans):
                entered.set(); release.wait(8)
                return SpanExportResult.SUCCESS
            def shutdown(self): pass
        tracing = self.track(subject.configure(exporters=[BlockingExporter()]))
        server = self.start(tracing)
        self.evaluate(server=server)
        self.assertTrue(entered.wait(3))
        started = time.monotonic()
        # Exceed the bounded queue while the worker is blocked: request threads
        # must keep serving rather than waiting for export capacity.
        for _ in range(300):
            with tracing.span("registry.evaluate"):
                pass
        self.assertEqual(self.evaluate(server=server)[0], 200)
        self.assertLess(time.monotonic()-started, 2)
        tracing.close(timeout=.05)
        self.assertLess(time.monotonic()-started, 2)
        release.set()

    def test_disabled_path_imports_no_sdk_with_standard_library_only(self):
        code = ("import sys; from demo.registry_ui_v02 import create_server; "
                "from demo.registry_tracing import configure; configure(); "
                "assert not any(n.startswith('opentelemetry') for n in sys.modules)")
        result = subprocess.run([sys.executable, "-S", "-c", code], cwd=baseline.ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_missing_sdk_and_invalid_sink_paths_leave_http_available(self):
        original = builtins.__import__
        def missing(name, *args, **kwargs):
            if name.startswith("opentelemetry"): raise ImportError("PRIVATE_DEPENDENCY")
            return original(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=missing):
            tracing = self.track(subject.configure(trace_file=Path(self.fixture.temp.name)/"trace.jsonl"))
        self.assertIsNone(tracing.tracer)
        self.assertEqual(self.evaluate(server=self.start(tracing))[0], 200)
        tracing = self.track(subject.configure(trace_file=Path(self.fixture.temp.name)/"missing"/"trace"))
        self.assertIsNone(tracing.tracer)
        self.assertEqual(self.evaluate(server=self.start(tracing))[0], 200)

    def test_jsonl_is_metadata_only_and_never_overwrites_existing_file(self):
        filename = Path(self.fixture.temp.name)/"trace.jsonl"
        tracing = self.track(subject.configure(trace_file=filename))
        server = self.start(tracing)
        request = baseline.request(); request["request_id"] = "PRIVATE_REQUEST"
        self.evaluate(request, server); tracing.flush()
        rows = [json.loads(line) for line in filename.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["schema"] for r in rows}, {"registry-trace/v1"})
        self.assertNotIn("PRIVATE_REQUEST", filename.read_text(encoding="utf-8"))
        self.assertTrue(all(r["duration_ms"] >= 0 for r in rows))
        before = filename.read_bytes()
        other = self.track(subject.configure(trace_file=filename))
        self.assertIsNone(other.tracer)
        self.assertEqual(filename.read_bytes(), before)

    def test_trace_file_inside_authority_is_refused_without_new_private_files(self):
        filename = self.fixture.root/"trace.jsonl"
        tracing = self.track(subject.configure(trace_file=filename, protected_root=self.fixture.root))
        self.assertIsNone(tracing.tracer)
        self.assertFalse(filename.exists())
        self.assertEqual(self.evaluate(server=self.start(tracing))[0], 200)

    def test_cli_passes_explicit_sinks_and_protected_root_and_closes_on_bind_failure(self):
        from unittest.mock import Mock
        tracing = Mock()
        with patch.object(ui.registry_tracing, "configure", return_value=tracing) as configure, \
                patch.object(ui, "create_server", side_effect=OSError("port unavailable")):
            with self.assertRaises(OSError):
                ui.main(["--registry-root", "private-root", "--trace-file", "trace.jsonl",
                         "--trace-otlp-endpoint", "http://127.0.0.1:4318/v1/traces"])
        configure.assert_called_once_with(trace_file=Path("trace.jsonl"),
                                          otlp_endpoint="http://127.0.0.1:4318/v1/traces",
                                          protected_root=Path("private-root"))
        tracing.close.assert_called_once()

    def test_otlp_rejects_remote_credentials_query_and_nonstandard_routes(self):
        for endpoint in ["https://example.org/v1/traces", "http://192.168.1.1/v1/traces",
                         "http://user:pass@127.0.0.1:4318/v1/traces",
                         "http://127.0.0.1:4318/v1/traces?secret=1",
                         "http://127.0.0.1:4318/other", "http://localhost:4318/v1/traces",
                         "http://127.0.0.1:0/v1/traces"]:
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                subject.LocalOTLPExporter(endpoint)

    def test_loopback_otlp_protobuf_and_missing_collector_are_safe(self):
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
        payloads = []
        class Collector(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                payloads.append((self.path, dict(self.headers), body))
                self.send_response(200); self.send_header("Content-Length", "0"); self.end_headers()
            def log_message(self, *args): pass
        collector = ThreadingHTTPServer(("127.0.0.1", 0), Collector)
        thread = threading.Thread(target=lambda: collector.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        self.addCleanup(collector.server_close); self.addCleanup(collector.shutdown)
        endpoint = f"http://127.0.0.1:{collector.server_port}/v1/traces"
        with patch.dict(os.environ, {"HTTP_PROXY": "http://invalid.example:1",
                                    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=PRIVATE_HEADER"}):
            tracing = self.track(subject.configure(otlp_endpoint=endpoint))
            self.evaluate(server=self.start(tracing)); self.assertTrue(tracing.flush())
        self.assertEqual(len(payloads), 1)
        path, headers, payload = payloads[0]
        self.assertEqual(path, "/v1/traces")
        self.assertNotIn("Authorization", headers)
        decoded = ExportTraceServiceRequest.FromString(payload)
        self.assertEqual(sum(len(scope.spans) for r in decoded.resource_spans
                             for scope in r.scope_spans), 2)
        collector.shutdown(); collector.server_close()
        self.evaluate(server=self.start(tracing)); tracing.flush()
        self.assertGreater(tracing.export_failures, 0)

    def test_otlp_redirect_partial_rejection_and_malformed_body_are_failures_without_retry(self):
        from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
        requests = []
        reply = {"status": 302, "body": b""}
        class Collector(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                requests.append(self.path)
                self.send_response(reply["status"])
                self.send_header("Location", "http://invalid.example/never")
                self.send_header("Content-Length", str(len(reply["body"])))
                self.end_headers(); self.wfile.write(reply["body"])
            def log_message(self, *args): pass
        collector = ThreadingHTTPServer(("127.0.0.1", 0), Collector)
        thread = threading.Thread(target=lambda: collector.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        self.addCleanup(collector.server_close); self.addCleanup(collector.shutdown)
        exporter = subject.LocalOTLPExporter(f"http://127.0.0.1:{collector.server_port}/v1/traces")
        with self.tracing.span("registry.evaluate"):
            pass
        spans = self.spans()
        self.assertEqual(exporter.export(spans), SpanExportResult.FAILURE)
        self.assertEqual(len(requests), 1)
        response = ExportTraceServiceResponse()
        response.partial_success.rejected_spans = 1
        response.partial_success.error_message = "PRIVATE_COLLECTOR_REPLY"
        reply.update(status=200, body=response.SerializeToString())
        self.assertEqual(exporter.export(spans), SpanExportResult.FAILURE)
        reply["body"] = b"not protobuf"
        safe = subject.SafeExporter(exporter, self.tracing)
        self.assertEqual(safe.export(spans), SpanExportResult.FAILURE)
        self.assertEqual(len(requests), 3)

    def test_allowlist_never_serializes_arbitrary_metadata(self):
        for name, value in [("request.body", "SECRET"), ("error.type", "SECRET"),
                            ("bioprocess.release_id", "/private/path"),
                            ("bioprocess.outcome", "SECRET"),
                            ("bioprocess.item_count", True)]:
            self.assertFalse(subject.permitted(name, value))
