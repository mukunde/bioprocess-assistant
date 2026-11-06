from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import agent
from graph_chat_benchmark import FIRST_RUN_RESERVE_USD, run_benchmark, run_targeted_retry
from graph_chat_budget import BenchmarkLimitError
from scripts.view_graph_chat_traces import page, read_traces
from tests.test_reliability import final_response, graph_result, tool_response


def simulate(output_dir=None, *, oversized=False):
    client = Mock()
    api = client.with_options.return_value.messages
    api.count_tokens.return_value.input_tokens = 4501 if oversized else 1200
    answers = [tool_response("yield"), final_response(),
               tool_response("pressure"), final_response(language="fr"),
               final_response("refuse", []), final_response("refuse", [])] * 2
    for response in answers:
        response.usage = SimpleNamespace(input_tokens=1200, output_tokens=70)
    api.create.side_effect = answers
    with patch.object(agent, "Anthropic", side_effect=AssertionError("live client")), patch.object(
        agent, "query_graph", side_effect=lambda symptom, **_: graph_result(
            {"yield": "Capture step yield drop", "pressure": "High column pressure"}[symptom]
        )
    ):
        path, report = run_benchmark(client, output_dir=output_dir, simulated=True)
    return path, report, api


class GraphChatBenchmarkTests(unittest.TestCase):
    def test_eight_results_link_to_distinct_exported_traces(self):
        with TemporaryDirectory() as tmp:
            report_file, report, api = simulate(tmp)
            self.assertEqual(json.loads(report_file.read_text(encoding="utf-8")), report)
            rows = [json.loads(line) for line in
                    (Path(tmp) / report["trace_file"]).read_text(encoding="utf-8").splitlines()]
        results = report["results"]
        self.assertEqual([(r["pass"], r["case"]) for r in results],
                         [(n, f"G{i:02}") for n in (1, 2) for i in range(1, 5)])
        self.assertEqual([r["outcome"] for r in results], ["answer", "answer", "refuse", "refuse"] * 2)
        self.assertEqual(len({r["trace_id"] for r in results}), 8)
        self.assertTrue(report["trace_flush_ok"])
        self.assertIsNone(report["halt"])
        self.assertEqual(api.create.call_count, 12)
        self.assertEqual(Decimal(report["reserved_usd"]), Decimal("0.299376"))
        for result in results:
            self.assertTrue(result["trace_exported"])
            names = [row["name"] for row in rows if row["trace_id"] == result["trace_id"]]
            self.assertEqual(names.count("graph_chat.request"), 1)
            self.assertEqual(names.count("neo4j.search"), int(result["outcome"] == "answer"))

    def test_failed_preflight_preserves_failure_trace_and_halts_both_passes(self):
        with TemporaryDirectory() as tmp:
            _, report, api = simulate(tmp, oversized=True)
        api.create.assert_not_called()
        self.assertEqual(report["halt"], "budget_abort")
        self.assertEqual(len(report["results"]), 1)
        self.assertTrue(report["results"][0]["trace_exported"])
        self.assertEqual(Decimal(report["reserved_usd"]), 0)


    def test_targeted_retry_uses_remaining_budget_and_displays_stop_reason(self):
        client = Mock()
        api = client.with_options.return_value.messages
        api.count_tokens.return_value.input_tokens = 1200
        response = final_response(stop_reason="max_tokens")
        response.usage = SimpleNamespace(input_tokens=1200, output_tokens=1536)
        api.create.return_value = response
        with TemporaryDirectory() as tmp:
            _, report = run_targeted_retry(client, output_dir=tmp, simulated=True)
            traces, skipped = read_traces(Path(tmp))
            self.assertEqual(skipped, 0)
            self.assertIn("max_tokens", page(traces, report["results"][0]["trace_id"], skipped))
        self.assertEqual([(r["pass"], r["case"]) for r in report["results"]],
                         [(1, "G01"), (1, "G02"), (2, "G01"), (2, "G02")])
        self.assertTrue(all(r["outcome"] == "error" for r in report["results"]))
        self.assertEqual(api.create.call_count, 4)
        self.assertTrue(all(c.kwargs["max_tokens"] == 1536 for c in api.create.call_args_list))
        self.assertEqual(Decimal(report["planned_maximum_usd"]), Decimal("0.502128"))
        self.assertEqual(Decimal(report["prior_reserved_usd"]), FIRST_RUN_RESERVE_USD)

    def test_2048_token_targeted_plan_exceeds_ceiling_before_preflight(self):
        client = Mock()
        with self.assertRaisesRegex(BenchmarkLimitError, "cumulative spend ceiling"):
            run_benchmark(client, simulated=True, case_ids=("G01", "G02"),
                          max_output=2048, prior_reserved_usd=FIRST_RUN_RESERVE_USD)
        client.with_options.return_value.messages.count_tokens.assert_not_called()
        client.with_options.return_value.messages.create.assert_not_called()
