"""Replay the Chainlit graph chat with local fixtures and no running services."""
import io
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import call, patch

from chainlit.context import init_http_context

import app
import graph_chat_ministral as local


PRESSURE = "High column pressure"
YIELD = "Capture step yield drop"
PRESSURE_QUERY = "high column pressure"
YIELD_QUERY = "capture yield drop"
THRESHOLD = 3.25


def sourced_result(symptom, reference):
    return {
        "found": True,
        "match_score": 4.2,
        "symptom": {"name": symptom, "source": f"Fixture {reference} symptom"},
        "causes": [{
            "name": "Documented possible cause",
            "description": "Cause recorded in the graph",
            "source": f"Fixture {reference} cause",
            "actions": [{
                "name": "Documented check",
                "description": "Check recorded in the graph",
                "source": f"Fixture {reference} action",
            }],
        }],
    }


def selection(language, *ids):
    return json.dumps({
        "status": "answer" if ids else "refuse",
        "language": language,
        "result_ids": list(ids),
    })


def ollama_response(message):
    return io.BytesIO(json.dumps({"done_reason": "stop", "message": message}).encode())


class OfflineGraphChatTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        init_http_context()

    async def replay(self, prompt, language, searches, final_content):
        state = {}
        session = SimpleNamespace(get=state.get, set=state.__setitem__)
        tool_calls = [
            {"function": {"name": "query_graph", "arguments": {"symptom": phrase}}}
            for phrase, _ in searches
        ]
        with (
            patch.dict(os.environ, {
                "BIOPROCESS_MODE": "graph",
                "BIOPROCESS_GRAPH_BACKEND": "ministral",
                "BIOPROCESS_LOCAL_OLLAMA_PORT": "11435",
                "NEO4J_URI": "bolt://127.0.0.1:7687",
            }),
            patch.object(app.cl, "user_session", session),
            patch.object(app.cl.Message, "send", autospec=True) as send,
            patch.object(app, "run_agent", side_effect=AssertionError("Unexpected Claude call")) as claude,
            patch.object(local, "load_graph_dotenv"),
            patch.object(local, "build_opener") as opener,
            patch.object(local, "query_graph", side_effect=[result for _, result in searches]) as graph,
        ):
            transport = opener.return_value.open
            transport.side_effect = [
                ollama_response({"tool_calls": tool_calls}),
                ollama_response({"content": final_content}),
            ]
            await app.on_settings_update({"graph_language": language, "min_score": THRESHOLD})
            await app.on_message(SimpleNamespace(content=prompt))

        claude.assert_not_called()
        self.assertEqual(graph.call_args_list, [
            call(phrase, min_score=THRESHOLD) for phrase, _ in searches
        ])
        self.assertEqual(transport.call_count, 2)
        first, final = [entry.args[0] for entry in transport.call_args_list]
        self.assertEqual(first.full_url, "http://127.0.0.1:11435/api/chat")
        self.assertEqual(json.loads(first.data)["messages"][-1]["content"], prompt)
        schema = json.loads(final.data)["format"]
        self.assertEqual(schema["properties"]["language"]["enum"], [language])
        send.assert_awaited_once()
        return send.await_args.args[0].content

    def assert_citations(self, reply, reference):
        self.assertEqual(
            [line for line in reply.splitlines() if line.startswith("Source :")],
            [f"Source : Fixture {reference} {kind}" for kind in ("symptom", "cause", "action")],
        )

    async def test_french_reply_keeps_original_citations(self):
        reply = await self.replay(
            "La pression de ma colonne augmente. Quelles causes vérifier ?", "fr",
            [(PRESSURE_QUERY, sourced_result(PRESSURE, "PRESSURE"))], selection("fr", 0),
        )
        self.assertIn(f"**Symptôme : {PRESSURE}**", reply)
        self.assertIn("**Cause possible : Documented possible cause**", reply)
        self.assertIn("réponse sourcée", reply)
        self.assert_citations(reply, "PRESSURE")

    async def test_english_reply_keeps_original_citations(self):
        reply = await self.replay(
            "My capture yield has dropped. What should I check?", "en",
            [(YIELD_QUERY, sourced_result(YIELD, "YIELD"))], selection("en", 0),
        )
        self.assertIn(f"**Symptom : {YIELD}**", reply)
        self.assertIn("**Possible cause : Documented possible cause**", reply)
        self.assertIn("réponse sourcée", reply)
        self.assert_citations(reply, "YIELD")

    async def test_two_symptoms_keep_separate_citations(self):
        reply = await self.replay(
            "Column pressure rose and capture yield dropped. What should I check?", "en",
            [(PRESSURE_QUERY, sourced_result(PRESSURE, "PRESSURE")),
             (YIELD_QUERY, sourced_result(YIELD, "YIELD"))],
            selection("en", 1, 0),
        )
        yield_section, pressure_section = reply.split("\n\n---\n\n")
        self.assertTrue(yield_section.startswith(f"**Symptom : {YIELD}**"))
        self.assertTrue(pressure_section.startswith(f"**Symptom : {PRESSURE}**"))
        self.assert_citations(yield_section, "YIELD")
        self.assert_citations(pressure_section, "PRESSURE")
        self.assertIn("réponse sourcée", reply)

    async def test_unsupported_maximum_pressure_abstains_on_retrieval_miss(self):
        miss = {"found": False, "match_score": 1.2, "symptom": None, "causes": []}
        reply = await self.replay(
            "What is the numerical maximum pressure for my column?", "en",
            [("maximum column pressure", miss)], selection("en"),
        )
        self.assertTrue(reply.startswith("I don't have this information in my knowledge base."))
        self.assertIn("réponse refusée", reply)
        self.assertNotIn("Source :", reply)
        self.assertNotIn("La réponse n'a pas pu être validée", reply)

    async def test_unconfirmed_pressure_abstains_even_with_a_selected_match(self):
        reply = await self.replay(
            "Pressure increase not confirmed. What is the maximum pressure?", "en",
            [(PRESSURE_QUERY, sourced_result(PRESSURE, "PRESSURE"))], selection("en", 0),
        )
        self.assertTrue(reply.startswith("I don't have this information in my knowledge base."))
        self.assertIn("réponse refusée", reply)
        self.assertNotIn("Source :", reply)
        self.assertNotIn(PRESSURE, reply)

    async def test_invalid_json_or_unknown_id_cannot_surface_sources(self):
        for label, invalid in (("invalid JSON", '{"status":'), ("unknown ID", selection("fr", 9))):
            with self.subTest(label=label):
                reply = await self.replay(
                    "La pression de colonne monte.", "fr",
                    [(PRESSURE_QUERY, sourced_result(PRESSURE, "PRESSURE"))], invalid,
                )
                self.assertIn("La réponse n'a pas pu être validée", reply)
                self.assertNotIn("réponse sourcée", reply)
                self.assertNotIn("réponse refusée", reply)
                self.assertNotIn("Source :", reply)
                self.assertNotIn(PRESSURE, reply)
                self.assertNotIn(invalid, reply)
