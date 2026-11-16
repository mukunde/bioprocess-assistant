"""Regressions for local graph selection and deterministic rendering."""
import json
import os
import unittest
from unittest.mock import patch

import graph_chat_ministral as local
from grounding import render_selection


def tool_result(phrase):
    return {"function": {"name": "query_graph", "arguments": {"symptom": phrase}}}


def found(name):
    return {
        "found": True,
        "match_score": 4.2,
        "symptom": {"name": name, "source": "Cytiva symptom p. 1"},
        "causes": [{
            "name": f"{name} cause",
            "description": "Canonical cause description",
            "source": "Cytiva cause p. 2",
            "actions": [{
                "name": f"{name} action",
                "description": "Canonical action description",
                "source": "Cytiva action p. 3",
            }],
        }],
    }


def selection(status, language, result_ids):
    return json.dumps({"status": status, "language": language, "result_ids": result_ids})


class MinistralTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"NEO4J_URI": "bolt://127.0.0.1:7687"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_selected_ids_render_full_sources_while_model_gets_compact_results(self):
        pressure, yield_drop = found("High column pressure"), found("Capture step yield drop")
        miss = {"found": False, "match_score": 1.2, "symptom": None, "causes": []}
        results = [pressure, miss, yield_drop]
        calls = [tool_result(phrase) for phrase in ("pressure", "irrelevant", "yield")]
        raw = selection("answer", "fr", [0, 2])
        metadata = {}
        with patch.object(local, "_chat", side_effect=[{"tool_calls": calls}, {"content": raw}]) as model, \
                patch.object(local, "query_graph", side_effect=results) as search:
            answer, score, threshold = local.run_ministral("Pression et rendement ?", language="fr", answer_metadata=metadata)
        self.assertEqual([call.args[0] for call in search.call_args_list], ["pressure", "irrelevant", "yield"])
        messages, = model.call_args.args
        schema = model.call_args.kwargs["format"]
        self.assertEqual(schema["properties"]["language"]["enum"], ["fr"])
        self.assertEqual(schema["properties"]["result_ids"]["items"]["enum"], [0, 2])
        compact = [json.loads(message["content"]) for message in messages if message["role"] == "tool"]
        self.assertEqual(compact[0]["result"]["causes"][0]["actions"], ["High column pressure action"])
        self.assertNotIn("Cytiva", json.dumps(compact))
        self.assertNotIn("Canonical", json.dumps(compact))
        self.assertEqual((answer, metadata), render_selection(raw, results))
        self.assertEqual((score, threshold), (4.2, 2.5))

    def test_no_search_or_no_match_can_abstain_without_sources(self):
        miss = {"found": False, "match_score": 1.2, "symptom": None, "causes": []}
        for calls in ([], [tool_result("endotoxin")]):
            with self.subTest(calls=calls):
                with patch.object(local, "_chat", side_effect=[
                    {"tool_calls": calls}, {"content": selection("refuse", "en", [])},
                ]) as model, patch.object(local, "query_graph", return_value=miss) as search:
                    metadata = {}
                    answer, _, _ = local.run_ministral("Question", language="en", answer_metadata=metadata)
                self.assertEqual(search.call_count, len(calls))
                self.assertEqual(model.call_args.kwargs["format"]["properties"]["result_ids"]["maxItems"], 0)
                self.assertEqual(metadata["status"], "refuse")
                self.assertNotIn("Source", answer)

    def test_invalid_output_cannot_surface_facts(self):
        for raw in ("not json", selection("answer", "fr", [1]), selection("answer", "en", [0])):
            with self.subTest(raw=raw):
                with patch.object(local, "_chat", side_effect=[
                    {"tool_calls": [tool_result("pressure")]}, {"content": raw},
                ]), patch.object(local, "query_graph", return_value=found("High column pressure")):
                    metadata = {}
                    answer, _, _ = local.run_ministral("Question", language="fr", answer_metadata=metadata)
                self.assertEqual(metadata["status"], "error")
                self.assertNotIn("Cytiva", answer)

    def test_pressure_alarm_guard_still_abstains(self):
        with patch.object(local, "_chat", side_effect=[
            {"tool_calls": [tool_result("pressure")]}, {"content": selection("answer", "en", [0])},
        ]), patch.object(local, "query_graph", return_value=found("High column pressure")):
            metadata = {}
            answer, _, _ = local.run_ministral(
                "Pressure increase not confirmed.", language="en", answer_metadata=metadata,
            )
        self.assertEqual(metadata["status"], "refuse")
        self.assertNotIn("Cytiva", answer)

    def test_remote_neo4j_is_refused_before_search(self):
        with patch.dict(os.environ, {"NEO4J_URI": "neo4j+s://example.com"}), patch.object(
            local, "_chat", return_value={"tool_calls": [tool_result("pressure")]},
        ), patch.object(local, "query_graph") as search:
            with self.assertRaisesRegex(ValueError, "loopback"):
                local.run_ministral("Question", language="en", answer_metadata={})
        search.assert_not_called()
