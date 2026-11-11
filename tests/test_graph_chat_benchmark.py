from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import agent
from graph_chat_benchmark import (
    FIRST_RUN_RESERVE_USD, PRESSURE_PROTOCOL, run_benchmark, run_held_out,
    run_pressure_validation, run_structured_replay, run_targeted_retry,
)
from graph_chat_budget import BenchmarkLimitError
from scripts.view_graph_chat_traces import page, read_traces
from tests.test_reliability import final_response, graph_result, tool_response


def simulate(output_dir=None, *, oversized=False, runner=run_benchmark):
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
        path, report = runner(client, output_dir=output_dir, simulated=True)
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

    def test_structured_replay_uses_separate_budget_for_both_passes(self):
        with TemporaryDirectory() as tmp:
            _, report, api = simulate(tmp, runner=run_structured_replay)
        results = report["results"]
        self.assertEqual([(r["pass"], r["case"], r["outcome"]) for r in results], [
            (n, case, outcome)
            for n in (1, 2)
            for case, outcome in (("G01", "answer"), ("G02", "answer"),
                                  ("G03", "refuse"), ("G04", "refuse"))
        ])
        self.assertTrue(all(r["trace_exported"] for r in results))
        self.assertEqual(len({r["trace_id"] for r in results}), 8)
        self.assertIsNone(report["halt"])
        self.assertEqual(Decimal(report["ceiling_usd"]), Decimal("1.01"))
        self.assertEqual(Decimal(report["prior_reserved_usd"]), 0)
        self.assertEqual(Decimal(report["planned_maximum_usd"]), Decimal("1.004256"))
        self.assertEqual(Decimal(report["reserved_usd"]), Decimal("0.502128"))
        self.assertEqual(report["max_calls_per_case"], 3)
        self.assertEqual(api.create.call_count, 12)
        self.assertEqual(api.count_tokens.call_count, 12)
        for count, create in zip(api.count_tokens.call_args_list, api.create.call_args_list):
            self.assertEqual(count.kwargs["output_config"], agent.SELECTION_OUTPUT)
            self.assertEqual(create.kwargs, {**count.kwargs, "max_tokens": 1536})

    def test_pressure_validation_runs_six_reviewed_cases_once(self):
        client = Mock()
        api = client.with_options.return_value.messages
        first_prompts = []

        def count_tokens(**payload):
            messages = payload["messages"]
            if len(messages) == 1:
                first_prompts.append(messages[0]["content"])
            return SimpleNamespace(input_tokens=1200)

        api.count_tokens.side_effect = count_tokens
        final = [
            final_response(), final_response(language="fr"),
            final_response("refuse", [], language="fr"), final_response("refuse", []),
            final_response(language="fr"), final_response(),
        ]
        responses = [response for item in final for response in (tool_response(), item)]
        for response in responses:
            response.usage = SimpleNamespace(input_tokens=1200, output_tokens=70)
        api.create.side_effect = responses
        with TemporaryDirectory() as tmp, patch.object(
            agent, "Anthropic", side_effect=AssertionError("live client")
        ), patch.object(agent, "query_graph", return_value=graph_result()) as search:
            _, report = run_pressure_validation(client, output_dir=tmp, simulated=True)

        results = report["results"]
        self.assertEqual([(r["pass"], r["case"], r["outcome"]) for r in results], [
            (1, "H08", "refuse"), (1, "G02", "answer"), (1, "P01", "refuse"),
            (1, "P02", "refuse"), (1, "P03", "answer"), (1, "P04", "answer"),
        ])
        for result in results:
            self.assertEqual("Source :" in result["answer"], result["outcome"] == "answer")
        self.assertTrue(all(r["trace_exported"] for r in results))
        self.assertEqual(len({r["trace_id"] for r in results}), 6)
        self.assertIsNone(report["halt"])
        self.assertEqual(report["ceiling_usd"], "0.76")
        self.assertEqual(Decimal(report["prior_reserved_usd"]), 0)
        self.assertEqual(Decimal(report["planned_maximum_usd"]), Decimal("0.753192"))
        self.assertEqual(Decimal(report["reserved_usd"]), Decimal("0.502128"))
        self.assertEqual(report["max_calls_per_case"], 3)
        client.with_options.assert_called_once_with(max_retries=0)
        self.assertEqual(api.create.call_count, 12)
        self.assertEqual(api.count_tokens.call_count, 12)
        self.assertEqual(search.call_count, 6)
        for count, create in zip(api.count_tokens.call_args_list, api.create.call_args_list):
            self.assertEqual(count.kwargs["output_config"], agent.SELECTION_OUTPUT)
            self.assertEqual(create.kwargs, {**count.kwargs, "max_tokens": 1536})
        self.assertEqual(len(first_prompts), 6)
        for prompt, prefix in zip(first_prompts, (
            "The capture dashboard", "La pression de ma colonne",
            "Le voyant de surpression", "The capture skid",
            "Pendant la capture", "The dashboard alarm",
        )):
            self.assertTrue(prompt.startswith(prefix))

    def test_pressure_validation_rejects_changed_variant_before_using_client(self):
        client = Mock()
        with TemporaryDirectory() as tmp:
            altered = Path(tmp) / "pressure.md"
            altered.write_text(PRESSURE_PROTOCOL.read_text(encoding="utf-8-sig").replace(
                "Le voyant de surpression", "Le voyant rouge"), encoding="utf-8")
            with patch("graph_chat_benchmark.PRESSURE_PROTOCOL", altered):
                with self.assertRaisesRegex(ValueError, "approved digest"):
                    run_pressure_validation(client, output_dir=tmp, simulated=True)
        self.assertEqual(client.mock_calls, [])

    def test_pressure_plan_over_ceiling_blocks_before_counting_or_generating(self):
        client = Mock()
        with patch("graph_chat_benchmark.PRESSURE_CEILING_USD", Decimal("0.75")):
            with self.assertRaisesRegex(BenchmarkLimitError, "cumulative spend ceiling"):
                run_pressure_validation(client, simulated=True)
        api = client.with_options.return_value.messages
        api.count_tokens.assert_not_called()
        api.create.assert_not_called()

    def test_held_out_runs_one_pass_with_frozen_prompts_and_structured_output(self):
        client = Mock()
        api = client.with_options.return_value.messages
        api.count_tokens.return_value.input_tokens = 1200
        positives = {1, 2, 7}
        responses = []
        for n in range(1, 9):
            responses.extend([tool_response(f"H{n:02}"), final_response()
                              if n in positives else final_response("refuse", [])])
        for response in responses:
            response.usage = SimpleNamespace(input_tokens=1200, output_tokens=70)
        api.create.side_effect = responses

        def search(symptom, **_):
            if int(symptom[1:]) in positives:
                return graph_result()
            return {"found": False, "match_score": None}

        with TemporaryDirectory() as tmp, patch.object(
            agent, "Anthropic", side_effect=AssertionError("live client")
        ), patch.object(agent, "query_graph", side_effect=search):
            _, report = run_held_out(client, output_dir=tmp, simulated=True)

        results = report["results"]
        self.assertEqual([(r["pass"], r["case"], r["outcome"]) for r in results], [
            (1, f"H{n:02}", "answer" if n in positives else "refuse")
            for n in range(1, 9)
        ])
        self.assertEqual(len({r["trace_id"] for r in results}), 8)
        self.assertTrue(all(r["trace_exported"] for r in results))
        self.assertIsNone(report["halt"])
        self.assertEqual(report["ceiling_usd"], "1.01")
        self.assertEqual(Decimal(report["prior_reserved_usd"]), 0)
        self.assertEqual(Decimal(report["planned_maximum_usd"]), Decimal("1.004256"))
        self.assertEqual(Decimal(report["reserved_usd"]), Decimal("0.669504"))
        client.with_options.assert_called_once_with(max_retries=0)
        self.assertEqual(api.create.call_count, 16)
        self.assertEqual(api.count_tokens.call_count, 16)
        for count, create in zip(api.count_tokens.call_args_list, api.create.call_args_list):
            self.assertEqual(count.kwargs["output_config"], agent.SELECTION_OUTPUT)
            self.assertEqual(create.kwargs, {**count.kwargs, "max_tokens": 1536})
        requests = [call.kwargs["messages"][0]["content"]
                    for call in api.create.call_args_list[::2]]
        self.assertEqual(len(set(requests)), 8)
        self.assertTrue(requests[0].startswith("Depuis que notre pool"))
        self.assertTrue(requests[-1].startswith("The capture dashboard"))

    def test_held_out_rejects_changed_prompt_before_touching_client(self):
        from graph_chat_benchmark import HELD_OUT_REVIEW

        client = Mock()
        with TemporaryDirectory() as tmp:
            changed = Path(tmp) / "review.md"
            source = HELD_OUT_REVIEW.read_text(encoding="utf-8")
            changed.write_text(source.replace("Depuis que notre pool", "Notre pool"),
                               encoding="utf-8")
            with patch("graph_chat_benchmark.HELD_OUT_REVIEW", changed):
                with self.assertRaisesRegex(ValueError, "approved digest"):
                    run_held_out(client, output_dir=tmp, simulated=True)
            self.assertEqual(list(Path(tmp).iterdir()), [changed])
        self.assertEqual(client.mock_calls, [])

    def test_structured_plan_under_original_ceiling_aborts_before_preflight(self):
        client = Mock()
        with self.assertRaisesRegex(BenchmarkLimitError, "cumulative spend ceiling"):
            run_benchmark(client, simulated=True, max_output=1536)
        client.with_options.return_value.messages.count_tokens.assert_not_called()
        client.with_options.return_value.messages.create.assert_not_called()

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
