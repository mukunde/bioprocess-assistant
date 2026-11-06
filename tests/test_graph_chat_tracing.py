"""Graph chat tracing tests with no Anthropic or Neo4j network calls."""
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import agent
import graph_chat_tracing as tracing
from tests.test_reliability import final_response, graph_result, tool_response

try:
    from opentelemetry.sdk.trace import TracerProvider
except ImportError:
    TracerProvider = None


def run_chat(tracer, responses, search=None):
    client = Mock()
    client.messages.create.side_effect = responses
    search = search or Mock(return_value=graph_result("private-graph-content"))
    with patch.object(agent, "load_graph_dotenv"), patch.object(agent, "local_tracer", return_value=tracer), \
            patch.object(agent, "Anthropic", return_value=client), patch.object(agent, "query_graph", search), \
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "private-api-key"}):
        return agent.run_agent("private-prompt")


class MetadataTests(unittest.TestCase):
    def test_disabled_does_not_initialize_sdk_or_file(self):
        with patch.dict(os.environ, {"BIOPROCESS_GRAPH_CHAT_TRACE": "0"}), \
                patch.object(tracing, "_initialize") as initialize:
            self.assertIsNone(tracing.local_tracer())
            initialize.assert_not_called()

    def test_failed_sdk_start_preserves_answer(self):
        tracer = Mock()
        tracer.start_span.side_effect = RuntimeError("private SDK error")
        result = run_chat(tracer, [final_response(status="refuse", ids=[])])
        self.assertIn("I don't have this information", result[0])

    def test_dotenv_cannot_override_or_supply_trace_switch(self):
        client = Mock()
        client.messages.create.return_value = final_response(status="refuse", ids=[])
        with TemporaryDirectory() as folder, patch.object(agent, "PROJECT_ROOT", Path(folder)), \
                patch.object(agent, "Anthropic", return_value=client):
            for shell, dotenv, expected in ((None, "1", 0), ("0", "1", 0), ("1", "0", 2)):
                with self.subTest(shell=shell), patch.dict(os.environ), \
                        patch.object(tracing._local, "get", return_value=None) as get:
                    os.environ.pop(tracing.TRACE_ENV, None)
                    if shell is not None:
                        os.environ[tracing.TRACE_ENV] = shell
                    (Path(folder) / ".env").write_text(
                        f"{tracing.TRACE_ENV}={dotenv}\nANTHROPIC_API_KEY=offline-dummy\n"
                    )
                    agent.run_agent("offline")
                    agent.run_agent("offline again")
                    self.assertEqual(os.environ.get(tracing.TRACE_ENV), shell)
                    self.assertEqual(get.call_count, expected)
                    self.assertEqual(os.environ["ANTHROPIC_API_KEY"], "offline-dummy")

    def test_unavailable_sdk_leaves_tracer_disabled(self):
        with TemporaryDirectory() as folder, patch.object(
            tracing, "__file__", str(Path(folder) / "graph_chat_tracing.py")
        ), patch.object(tracing, "_provider", side_effect=ImportError("private error")), \
                self.assertLogs(tracing.LOGGER, level="WARNING") as logs:
            self.assertIsNone(tracing._initialize())
        self.assertNotIn("private error", "\n".join(logs.output))

    def test_concurrent_chat_requests_do_not_wait_for_trace_file(self):
        local = tracing._LocalTracer()
        started, release, worker_done = Event(), Event(), Event()
        ready_tracer = Mock()

        def initialize():
            started.set()
            try:
                release.wait(5)
                return ready_tracer
            finally:
                worker_done.set()

        client = Mock()
        client.messages.create.return_value = final_response(status="refuse", ids=[])
        completed = [Event(), Event()]
        results = [None, None]

        def request(index):
            try:
                results[index] = agent.run_agent("offline")[0]
            finally:
                completed[index].set()

        with patch.object(tracing, "_local", local), patch.object(tracing, "_initialize", side_effect=initialize) as init, \
                patch.object(agent, "Anthropic", return_value=client), patch.object(agent, "load_graph_dotenv"), \
                patch.dict(os.environ, {tracing.TRACE_ENV: "1", "ANTHROPIC_API_KEY": "offline"}):
            callers = [Thread(target=request, args=(index,)) for index in range(2)]
            try:
                callers[0].start()
                self.assertTrue(started.wait(2))
                callers[1].start()
                self.assertTrue(all(done.wait(2) for done in completed))
                self.assertFalse(worker_done.is_set())
                self.assertTrue(all("I don't have this information" in text for text in results))
                init.assert_called_once()
            finally:
                release.set()
                for caller in callers:
                    if caller.ident is not None:
                        caller.join(2)
                worker_done.wait(2)

    def test_cost_applies_geo_multiplier_to_all_token_categories(self):
        usage = SimpleNamespace(
            input_tokens=100, output_tokens=20, cache_read_input_tokens=40,
            cache_creation_input_tokens=30, cache_creation=SimpleNamespace(
                ephemeral_5m_input_tokens=10, ephemeral_1h_input_tokens=20),
        )
        for geo, cost in (("global", 0.0007695), ("us", 0.00084645), (None, 0.0007695)):
            with self.subTest(geo=geo):
                usage.inference_geo = geo
                data = tracing.usage_metadata(SimpleNamespace(usage=usage), agent.MODEL)
                self.assertAlmostEqual(data["cost.estimated_usd"], cost)
                self.assertEqual(data.get("usage.inference_geo"), geo)
        usage.inference_geo = "private-unknown"
        data = tracing.usage_metadata(SimpleNamespace(usage=usage), agent.MODEL)
        self.assertNotIn("usage.inference_geo", data)
        self.assertNotIn("cost.estimated_usd", data)

    def test_usage_missing_or_unknown_price_is_not_zero(self):
        self.assertEqual(tracing.usage_metadata(SimpleNamespace(), agent.MODEL), {})
        usage = SimpleNamespace(input_tokens=9, output_tokens=2, cache_creation_input_tokens=5)
        for model in (agent.MODEL, "unknown"):
            values = tracing.usage_metadata(SimpleNamespace(usage=usage), model)
            self.assertEqual(values["usage.input_tokens"], 9)
            self.assertNotIn("cost.estimated_usd", values)


@unittest.skipUnless(TracerProvider is not None, "Optional OpenTelemetry SDK not installed")
class TraceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.provider = tracing._provider(self.stream)
        self.addCleanup(self.provider.shutdown)
        self.tracer = self.provider.get_tracer("test")

    def rows(self):
        self.assertTrue(self.provider.force_flush(timeout_millis=3000))
        return [json.loads(line) for line in self.stream.getvalue().splitlines()]

    def test_cited_answer_spans_have_linked_timing_and_usage_without_payload(self):
        first = tool_response(symptom="private-search")
        first.usage = SimpleNamespace(
            input_tokens=100, output_tokens=20, cache_read_input_tokens=40,
            cache_creation_input_tokens=30, cache_creation=SimpleNamespace(
                ephemeral_5m_input_tokens=10, ephemeral_1h_input_tokens=20),
        )
        second = final_response()
        second.usage = SimpleNamespace(input_tokens=200, output_tokens=10)
        answer, _, _ = run_chat(self.tracer, [first, second])
        self.assertIn("Fouling", answer)
        rows = self.rows()
        self.assertEqual([r["name"] for r in rows], [
            "anthropic.messages.create", "neo4j.search", "anthropic.messages.create",
            "graph_chat.request",
        ])
        root = rows[-1]
        self.assertIsNone(root["parent_span_id"])
        self.assertEqual(root["attributes"], {"outcome": "answer"})
        self.assertTrue(all(r["trace_id"] == root["trace_id"] for r in rows))
        self.assertTrue(all(r["parent_span_id"] == root["span_id"] for r in rows[:-1]))
        self.assertTrue(all(0 <= r["duration_ms"] <= root["duration_ms"] for r in rows))
        self.assertEqual(rows[1]["attributes"], {"outcome": "matched"})
        self.assertEqual(rows[0]["attributes"]["usage.cache_read_input_tokens"], 40)
        self.assertAlmostEqual(rows[0]["attributes"]["cost.estimated_usd"], 0.0007695)
        self.assertAlmostEqual(rows[2]["attributes"]["cost.estimated_usd"], 0.00075)
        self.assertEqual(rows[0]["attributes"]["cost.pricing_date"], tracing.PRICE_DATE)
        self.assertNotIn("private-", self.stream.getvalue())
        self.assertNotIn("Handbook", self.stream.getvalue())

    def test_end_turn_rejection_exports_only_a_safe_reason(self):
        from scripts.view_graph_chat_traces import page

        incomplete = graph_result()
        incomplete["symptom"].pop("source")
        cases = [
            (SimpleNamespace(stop_reason="end_turn", content=[]),
             graph_result(), "empty_response"),
            (SimpleNamespace(stop_reason="end_turn",
                             content=[SimpleNamespace(type="text", text="secret raw prose")]),
             graph_result(), "invalid_json"),
            (final_response(ids=[9]), graph_result(), "invalid_result_id"),
            (final_response(), {"found": False, "match_score": None}, "retrieval_miss"),
            (final_response(), incomplete, "missing_graph_field"),
        ]
        for response, result, code in cases:
            with self.subTest(code=code):
                answer, _, _ = run_chat(self.tracer, [tool_response(), response],
                                        Mock(return_value=result))
                model, root = self.rows()[-2:]
                self.assertEqual(model["attributes"]["gen_ai.response.stop_reason"], "end_turn")
                self.assertEqual(root["status"], "ERROR")
                self.assertEqual(root["attributes"], {
                    "outcome": "error", "grounding.rejection_reason": code,
                })
                self.assertIn(code, page([(root["trace_id"], [root])], root["trace_id"], 0))
                self.assertNotIn("secret raw prose", answer)
        self.assertNotIn("secret raw prose", self.stream.getvalue())
        self.assertFalse(tracing._permitted("grounding.rejection_reason", "secret raw prose"))

    def test_neo4j_and_anthropic_failures_are_recorded_without_exception_text(self):
        for source, responses, search in (
            ("anthropic.messages.create", [RuntimeError("private-provider-error")], None),
            ("neo4j.search", [tool_response()], Mock(side_effect=RuntimeError("private-db-error"))),
        ):
            with self.subTest(source=source), self.assertRaisesRegex(RuntimeError, "private-"):
                run_chat(self.tracer, responses, search)
            rows = self.rows()
            self.assertEqual([(r["name"], r["status"]) for r in rows[-2:]], [
                (source, "ERROR"), ("graph_chat.request", "ERROR"),
            ])
        self.assertNotIn("private-", self.stream.getvalue())

    def test_initialize_creates_an_ignored_trace_file(self):
        with TemporaryDirectory() as folder, patch.object(
            tracing, "__file__", str(Path(folder) / "graph_chat_tracing.py")
        ), patch.dict(os.environ, {"BIOPROCESS_GRAPH_CHAT_TRACE": "1"}), patch("atexit.register") as register:
            tracer = tracing._initialize()
            self.assertIsNotNone(tracer)
            register.assert_called_once()
            close, provider = register.call_args.args
            try:
                run_chat(tracer, [final_response(status="refuse", ids=[])])
                self.assertTrue(provider.force_flush(timeout_millis=3000))
            finally:
                close(provider)
            files = list((Path(folder) / "tmp" / "graph-chat-traces").glob("*.jsonl"))
            self.assertEqual(len(files), 1)
            rows = [json.loads(line) for line in files[0].read_text().splitlines()]
            self.assertEqual([r["name"] for r in rows], [
                "anthropic.messages.create", "graph_chat.request",
            ])

    def test_disk_error_does_not_replace_refusal(self):
        self.stream.close()
        with self.assertLogs(tracing.LOGGER, level="WARNING") as logs:
            answer, _, _ = run_chat(self.tracer, [final_response(status="refuse", ids=[])])
            self.assertTrue(self.provider.force_flush(timeout_millis=3000))
        self.assertIn("I don't have this information", answer)
        self.assertEqual(len(logs.output), 1)

    def test_no_match_and_refusal_have_distinct_outcomes(self):
        search = Mock(return_value={"found": False, "match_score": None})
        run_chat(self.tracer, [tool_response(), final_response(status="refuse", ids=[])], search)
        rows = self.rows()
        self.assertEqual(rows[1]["attributes"], {"outcome": "no_match"})
        self.assertEqual(rows[-1]["attributes"], {"outcome": "refuse"})
