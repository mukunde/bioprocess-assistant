"""Chainlit regression tests; no model, database or network calls.

Run with the application dependencies installed:
    python -m unittest discover -s tests -p test_app.py -v
"""
import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import app
import agent
from anthropic import APIConnectionError, RateLimitError
from neo4j.exceptions import AuthError, ServiceUnavailable
import httpx
from chainlit.context import init_http_context


class MessageFailureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        init_http_context()

    def setUp(self):
        self.session = patch.object(app.cl, "user_session").start()
        self.session.get.return_value = 0.0
        self.send = patch.object(app.cl.Message, "send", new_callable=AsyncMock).start()
        self.addCleanup(patch.stopall)

    async def assert_failure(self, error):
        replies = []
        async def capture(message):
            replies.append(message.content)
        with patch.object(app, "run_agent", side_effect=error), \
                patch.object(app.cl.Message, "send", new=capture), \
                self.assertLogs(app.logger, level="ERROR") as logs:
            await app.on_message(SimpleNamespace(content="high column pressure"))
        self.assertEqual(replies, [app.SERVICE_ERROR_MESSAGE])
        self.assertNotIn("sensitive-internal-detail", replies[0])
        self.assertNotIn("score", replies[0])
        self.assertIn(type(error).__name__, "\n".join(logs.output))

    async def test_model_connection_and_rate_limit_errors_are_safe(self):
        request = httpx.Request("POST", "https://example.invalid")
        errors = [
            APIConnectionError(request=request, message="sensitive-internal-detail"),
            RateLimitError("sensitive-internal-detail", response=httpx.Response(429, request=request), body=None),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                await self.assert_failure(error)

    async def test_neo4j_connection_and_authentication_errors_are_safe(self):
        for error in [ServiceUnavailable("sensitive-internal-detail"), AuthError("sensitive-internal-detail")]:
            with self.subTest(error=type(error).__name__):
                await self.assert_failure(error)

    async def test_unexpected_errors_also_hide_internal_details(self):
        await self.assert_failure(RuntimeError("sensitive-internal-detail"))

    async def test_cancellation_is_not_reported_as_service_failure(self):
        with patch.object(app, "run_agent", side_effect=asyncio.CancelledError):
            with self.assertRaises(asyncio.CancelledError):
                await app.on_message(SimpleNamespace(content="question"))
        self.send.assert_not_awaited()

    async def test_zero_threshold_and_success_survive(self):
        replies = []
        def answer(*args, **kwargs):
            self.assertEqual(args[1], 0.0)
            kwargs["answer_metadata"].update(status="answer")
            return "Sourced graph facts", 4.0, 0.0
        async def capture(message):
            replies.append(message.content)
        with patch.object(app, "run_agent", side_effect=answer), patch.object(app.cl.Message, "send", new=capture):
            await app.on_message(SimpleNamespace(content="pressure"))
        self.assertEqual(len(replies), 1)
        self.assertIn("Sourced graph facts", replies[0])
        self.assertIn("réponse sourcée", replies[0])
        self.assertIn("0.00", replies[0])

    async def test_real_agent_database_failure_is_contained(self):
        tool_call = SimpleNamespace(stop_reason="tool_use", content=[SimpleNamespace(
            type="tool_use", name="query_graph", id="q1", input={"symptom":"pressure"})])
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY":"test-never-sent"}), \
                patch.object(agent, "Anthropic") as sdk, \
                patch.object(agent, "query_graph", side_effect=ServiceUnavailable("offline")), \
                self.assertLogs(app.logger, level="ERROR"):
            sdk.return_value.messages.create.return_value = tool_call
            await app.on_message(SimpleNamespace(content="pressure"))
        self.send.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
