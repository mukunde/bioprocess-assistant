from decimal import Decimal
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import agent
from graph_chat_budget import BenchmarkLimitError, GraphChatBudget
from tests.test_reliability import final_response, graph_result, tool_response


def with_usage(response):
    response.usage = SimpleNamespace(input_tokens=1234, output_tokens=20)
    return response


class GraphChatBudgetTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.api = self.client.with_options.return_value.messages
        self.api.count_tokens.return_value.input_tokens = 1200
        self.budget = GraphChatBudget(self.client)
        self.client.with_options.assert_called_once_with(max_retries=0)
        self.api.create.side_effect = lambda **_: with_usage(final_response("refuse", []))
        constructor = patch.object(agent, "Anthropic", side_effect=AssertionError("live client"))
        constructor.start()
        self.addCleanup(constructor.stop)
        tracing = patch.object(agent, "local_tracer", return_value=None)
        tracing.start()
        self.addCleanup(tracing.stop)

    def run_chat(self):
        return agent.run_agent("Benchmark question", benchmark_budget=self.budget)

    def test_count_uses_same_full_payload_including_retrieval(self):
        self.api.create.side_effect = [with_usage(tool_response()), with_usage(final_response())]
        counted = []
        self.api.count_tokens.side_effect = lambda **kw: (
            counted.append(len(kw["messages"])), SimpleNamespace(input_tokens=1200)
        )[1]
        with patch.object(agent, "query_graph", return_value=graph_result()):
            answer, *_ = self.run_chat()
        self.assertIn("High column pressure", answer)
        self.assertEqual(counted, [1, 3])
        for count_call, create_call in zip(self.api.count_tokens.call_args_list,
                                           self.api.create.call_args_list):
            self.assertEqual(create_call.kwargs, {**count_call.kwargs, "max_tokens": 512})
            self.assertEqual(count_call.kwargs["output_config"], agent.SELECTION_OUTPUT)
        self.assertEqual(self.budget.reserved_usd, Decimal("0.049896"))

    def test_invalid_or_oversize_count_never_creates_message(self):
        for value in (4501, None, True):
            with self.subTest(value=value):
                self.budget = GraphChatBudget(self.client)
                self.api.count_tokens.return_value.input_tokens = value
                with self.assertRaisesRegex(BenchmarkLimitError, "input token preflight"):
                    self.run_chat()
                self.api.create.assert_not_called()
                self.assertTrue(self.budget.stopped)

    def test_unavailable_count_stops_without_charging_reserve(self):
        self.api.count_tokens.side_effect = TimeoutError
        with self.assertRaisesRegex(BenchmarkLimitError, "preflight unavailable"):
            self.run_chat()
        self.api.create.assert_not_called()
        self.assertEqual(self.budget.reserved_usd, 0)

    def test_reserve_is_retained_on_missing_usage_excess_or_api_failure(self):
        for result, error in (
            (final_response(), BenchmarkLimitError),
            (SimpleNamespace(usage=SimpleNamespace(input_tokens=5001, output_tokens=20)),
             BenchmarkLimitError),
            (TimeoutError(), TimeoutError),
        ):
            with self.subTest(error=error, result=result):
                self.budget = GraphChatBudget(self.client)
                self.api.create.reset_mock()
                self.api.create.side_effect = [result]
                with self.assertRaises(error):
                    self.run_chat()
                self.assertEqual(self.budget.reserved_usd, Decimal("0.024948"))
                with self.assertRaises(BenchmarkLimitError):
                    self.run_chat()
                self.api.create.assert_called_once()

    def test_twenty_four_calls_reserved_and_ninth_submission_blocked(self):
        responses = [with_usage(tool_response()), with_usage(tool_response()),
                     with_usage(final_response())]
        self.api.create.side_effect = responses * 8
        with patch.object(agent, "query_graph", return_value=graph_result()):
            for _ in range(8):
                self.run_chat()
            with self.assertRaisesRegex(BenchmarkLimitError, "submission limit"):
                self.run_chat()
        self.assertEqual(self.api.create.call_count, 24)
        self.assertEqual(self.budget.reserved_usd, Decimal("0.598752"))

    def test_fourth_model_call_blocked_before_preflight(self):
        self.api.create.side_effect = [with_usage(tool_response()) for _ in range(3)]
        with patch.object(agent, "query_graph", return_value=graph_result()):
            with self.assertRaisesRegex(BenchmarkLimitError, "model call limit"):
                self.run_chat()
        self.assertEqual(self.api.count_tokens.call_count, 3)
        self.assertEqual(self.api.create.call_count, 3)

    def test_spend_ceiling_blocks_before_count_or_generation(self):
        self.budget.reserved_usd = Decimal("0.99")
        with self.assertRaisesRegex(BenchmarkLimitError, "spend ceiling"):
            self.run_chat()
        self.api.count_tokens.assert_not_called()
        self.api.create.assert_not_called()
