"""Regressions for local graph selection and deterministic rendering."""
import json
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import graph_chat_ministral as local
import start_local_graph_chat as launcher
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

    def test_chat_uses_the_configured_loopback_port(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(local, "build_opener") as opener:
            opener.return_value.open.return_value.__enter__.return_value.read.return_value = (
                b'{"done_reason":"stop","message":{"content":"ok"}}'
            )
            self.assertEqual(local._chat([]), {"content": "ok"})
            self.assertEqual(opener.return_value.open.call_args.args[0].full_url,
                             "http://127.0.0.1:11434/api/chat")
            os.environ["BIOPROCESS_LOCAL_OLLAMA_PORT"] = "11435"
            self.assertEqual(local._chat([]), {"content": "ok"})
            self.assertEqual(opener.return_value.open.call_args.args[0].full_url,
                             "http://127.0.0.1:11435/api/chat")

    def test_chat_keeps_the_hybrid_layer_count_for_each_model_call(self):
        for profile, layers in (("CPU", None), ("Hybrid", 13), ("IrisXe", None)):
            with self.subTest(profile=profile), patch.dict(os.environ, {"BIOPROCESS_LOCAL_OLLAMA_PROFILE": profile}), \
                    patch.object(local, "build_opener") as opener:
                connection = opener.return_value.open
                connection.return_value.__enter__.return_value.read.return_value = (
                    b'{"done_reason":"stop","message":{"content":"ok"}}'
                )
                local._chat([], tools=[])
                local._chat([], format={})
                for entry in connection.call_args_list:
                    payload = json.loads(entry.args[0].data)
                    self.assertEqual(payload["options"].get("num_gpu"), layers)

    def test_hybrid_startup_requires_exact_partial_offload_on_iris_xe(self):
        args = SimpleNamespace(profile="Hybrid", ollama_port=11435)
        for device, count, vram, accepted in (
            ("Intel(R) Iris(R) Xe Graphics", 13, 130, True),
            ("Intel(R) Iris(R) Xe Graphics", 27, 270, False),
            ("Intel(R) Iris(R) Xe Graphics", 12, 120, False),
            ("Intel(R) Iris(R) Xe Graphics", 13, 0, False),
            ("Other GPU", 13, 130, False),
        ):
            with self.subTest(device=device, count=count, vram=vram), \
                    patch.object(Path, "read_text", return_value=(
                        f"using device Vulkan0 ({device})\n"
                        f"offloaded {count}/27 layers to GPU\n"
                    )), patch.object(launcher, "request", side_effect=[
                        {}, {}, {"models": [{"name": local.MODEL, "size": 270, "size_vram": vram}]},
                    ]) as request, patch("builtins.print"):
                if accepted:
                    launcher.load_model(args, Path("ollama.log"))
                else:
                    with self.assertRaisesRegex(launcher.StartupError, "Hybrid offload of 13 layers"):
                        launcher.load_model(args, Path("ollama.log"))
                self.assertEqual(request.call_args_list[1].args[2]["options"], {"num_ctx": 4096, "num_gpu": 13})

    def test_chat_rejects_invalid_ports_before_opening_a_connection(self):
        for port in ("http://example.com:11435", "0", "65536", "11435/path"):
            with self.subTest(port=port), patch.dict(os.environ, {"BIOPROCESS_LOCAL_OLLAMA_PORT": port}), \
                    patch.object(local, "build_opener") as opener:
                with self.assertRaisesRegex(ValueError, "Invalid local Ollama port"):
                    local._chat([])
                opener.assert_not_called()

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
