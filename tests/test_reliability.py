"""Offline regressions. Run: python -m unittest discover -s tests -v"""
import io
import json
import math
import os
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agent
from eval import judge, run_eval
from grounding import GroundingError, render_selection
from scripts import load_graph
from tools import DEFAULT_MIN_MATCH_SCORE, query_graph, resolve_min_score


def graph_result(name="High column pressure"):
    return {
        "found": True, "match_score": 4.0, "threshold": 2.5,
        "symptom": {"name": name, "source": "Handbook p.1"},
        "causes": [{"name": "Fouling", "description": "Deposits on the resin.",
                    "source": "Handbook p.2", "actions": [
                        {"name": "Clean", "description": "Use a resin-compatible procedure.",
                         "source": "Handbook p.3"}]}],
    }


def final_response(status="answer", ids=None, language="en", stop_reason="end_turn"):
    text = json.dumps({"status": status, "language": language,
                       "result_ids": [0] if ids is None else ids})
    return SimpleNamespace(stop_reason=stop_reason,
                          content=[SimpleNamespace(type="text", text=text)])


def tool_response(symptom="high column pressure", name="query_graph"):
    return SimpleNamespace(stop_reason="tool_use", content=[
        SimpleNamespace(type="tool_use", name=name, id="query-1",
                        input={"symptom": symptom})])


class GroundingTests(unittest.TestCase):
    def render(self, **kwargs):
        return render_selection(final_response(**kwargs).content[0].text, [graph_result()])

    def test_valid_answer_cites_every_graph_node(self):
        text, metadata = self.render()
        for source in ("Handbook p\\.1", "Handbook p\\.2", "Handbook p\\.3"):
            self.assertIn(source, text)
        self.assertEqual(metadata["symptoms"], ["High column pressure"])

    def test_french_headings_preserve_canonical_facts(self):
        text, _ = self.render(language="fr")
        self.assertIn("Symptôme", text)
        self.assertIn("Use a resin\\-compatible procedure", text)

    def test_refusal_has_no_model_prose(self):
        text, metadata = self.render(status="refuse", ids=[])
        self.assertIn("I don't have this information", text)
        self.assertEqual(metadata["status"], "refuse")

    def test_missing_or_invalid_result_ids_fail_closed(self):
        for ids in ([], [-1], [1], [True], [0, 0], ["0"]):
            with self.subTest(ids=ids), self.assertRaises(GroundingError):
                self.render(ids=ids)

    def test_extra_model_advice_is_rejected(self):
        payload = {"status": "answer", "language": "en", "result_ids": [0],
                   "advice": "Invented protocol"}
        with self.assertRaises(GroundingError):
            render_selection(json.dumps(payload), [graph_result()])

    def test_missing_graph_evidence_is_rejected(self):
        for target, key in (("symptom", "source"), ("cause", "source"),
                            ("action", "source"), ("action", "description")):
            data = graph_result()
            node = data["symptom"] if target == "symptom" else data["causes"][0]
            if target == "action":
                node = node["actions"][0]
            del node[key]
            with self.subTest(target=target, key=key), self.assertRaises(GroundingError):
                render_selection(final_response().content[0].text, [data])

    def test_retrieval_miss_cannot_be_selected(self):
        data = graph_result()
        data["found"] = False
        with self.assertRaises(GroundingError):
            render_selection(final_response().content[0].text, [data])

    def test_path_without_corrective_actions_is_rejected(self):
        data = graph_result()
        data["causes"][0]["actions"] = []
        with self.assertRaises(GroundingError):
            render_selection(final_response().content[0].text, [data])

    def test_graph_markup_is_escaped(self):
        data = graph_result()
        data["causes"][0]["description"] = "<script>x</script> [link](https://example.com)"
        text, _ = render_selection(final_response().content[0].text, [data])
        self.assertNotIn("<script>", text)
        self.assertNotIn("[link](", text)


class AgentBoundaryTests(unittest.TestCase):
    def run_mock(self, responses, result=None):
        client = MagicMock()
        client.messages.create.side_effect = responses
        outputs, metadata = [], {}
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}), \
                patch.object(agent, "load_dotenv"), \
                patch.object(agent, "Anthropic", return_value=client), \
                patch.object(agent, "query_graph", return_value=result or graph_result()) as query:
            text, _, _ = agent.run_agent("Test", tool_outputs=outputs, answer_metadata=metadata)
        return text, outputs, metadata, query

    def test_answer_without_lookup_is_blocked(self):
        text, _, metadata, query = self.run_mock([final_response()])
        self.assertNotIn("Possible cause", text)
        self.assertEqual(metadata["status"], "error")
        query.assert_not_called()

    def test_unstructured_model_prose_is_blocked(self):
        response = SimpleNamespace(stop_reason="end_turn", content=[
            SimpleNamespace(type="text", text="Invented corrective advice")])
        text, _, metadata, _ = self.run_mock([tool_response(), response])
        self.assertNotIn("Invented", text)
        self.assertEqual(metadata["status"], "error")

    def test_complete_grounded_round_trip(self):
        text, outputs, metadata, query = self.run_mock([tool_response(), final_response()])
        self.assertIn("Fouling", text)
        self.assertEqual(outputs, [graph_result()])
        self.assertEqual(metadata["status"], "answer")
        query.assert_called_once_with("high column pressure", min_score=2.5)

    def test_refusal_needs_no_database(self):
        _, _, metadata, query = self.run_mock([final_response(status="refuse", ids=[])])
        self.assertEqual(metadata["status"], "refuse")
        query.assert_not_called()

    def test_truncated_json_is_not_treated_as_an_answer(self):
        _, _, metadata, _ = self.run_mock([
            tool_response(), final_response(stop_reason="max_tokens")])
        self.assertEqual(metadata["status"], "error")

    def test_incomplete_tool_evidence_cannot_reach_user(self):
        data = graph_result()
        del data["causes"][0]["source"]
        text, _, metadata, _ = self.run_mock([tool_response(), final_response()], data)
        self.assertEqual(metadata["status"], "error")
        self.assertNotIn("Fouling", text)

    def test_failed_lookup_can_only_produce_a_refusal(self):
        miss = {"found": False, "match_score": 1, "symptom": None, "causes": []}
        _, _, metadata, _ = self.run_mock([
            tool_response(), final_response(status="refuse", ids=[])], miss)
        self.assertEqual(metadata["status"], "refuse")

    def test_unknown_tool_is_rejected(self):
        _, _, metadata, query = self.run_mock([tool_response(name="invented_tool")])
        self.assertEqual(metadata["status"], "error")
        query.assert_not_called()

    def test_turn_budget_exhaustion_is_an_error(self):
        _, _, metadata, query = self.run_mock([tool_response()] * agent.MAX_TURNS)
        self.assertEqual(metadata["status"], "error")
        self.assertEqual(query.call_count, agent.MAX_TURNS)


class EvaluationTests(unittest.TestCase):
    def row(self, **changes):
        row = {"id": "test", "type": "in_scope", "hallucination_free": True,
               "sources_cited": True, "refused": False, "answers_question": True,
               "contract_ok": True, "rationale": "fixture"}
        row.update(changes)
        return row

    def report(self, rows):
        with redirect_stdout(io.StringIO()):
            return run_eval.report_agent(rows)

    def test_valid_answer_passes(self):
        self.assertTrue(self.report([self.row()]))

    def test_unexpected_refusal_fails(self):
        self.assertFalse(self.report([self.row(refused=True)]))

    def test_wrong_symptom_or_unrelated_answer_fails(self):
        self.assertFalse(self.report([self.row(contract_ok=False)]))
        self.assertFalse(self.report([self.row(answers_question=False)]))

    def test_missing_and_non_boolean_verdicts_fail(self):
        for value in (None, "true", 1):
            self.assertFalse(self.report([self.row(hallucination_free=value)]))

    def test_refusal_must_be_grounded_and_cited(self):
        self.assertTrue(self.report([self.row(type="off_topic", refused=True)]))
        self.assertFalse(self.report([self.row(type="off_topic", refused=False)]))
        self.assertFalse(self.report([self.row(type="off_topic", refused=True, sources_cited=False)]))

    def test_empty_evaluation_is_not_a_success(self):
        self.assertFalse(self.report([]))
        with redirect_stdout(io.StringIO()):
            self.assertFalse(run_eval.report([], 2.5))

    def test_lexical_subset_matches_actual_tool_language(self):
        cases = [{"id": "fr", "lang": "fr"}, {"id": "en", "lang": "en"},
                 {"id": "translated", "lang": "fr", "retrieval_query": "pressure"},
                 {"id": "semantic", "lang": "en", "agent_only": True}]
        self.assertEqual([c["id"] for c in run_eval.retrieval_cases(cases)], ["en", "translated"])

    def test_evaluate_uses_explicit_retrieval_phrase(self):
        case = {"id": "fr", "lang": "fr", "type": "in_scope", "question": "pression",
                "retrieval_query": "high column pressure", "expected_symptom": "High column pressure"}
        with patch.object(run_eval, "query_graph", return_value=graph_result()) as query:
            self.assertTrue(run_eval.evaluate([case], 2.5)[0]["ok"])
            query.assert_called_once_with("high column pressure", min_score=2.5)

    def test_end_to_end_rejects_wrong_selected_symptom(self):
        case = {"id": "wrong", "type": "in_scope", "question": "yield",
                "expected_symptom": "Capture step yield drop"}
        def fake_agent(*args, **kwargs):
            kwargs["answer_metadata"].update(status="answer", symptoms=["High column pressure"])
            return "answer", 4, 2.5
        with patch.object(agent, "run_agent", side_effect=fake_agent), \
                patch.object(judge, "judge_response", return_value=self.row()), \
                redirect_stdout(io.StringIO()):
            rows = run_eval.run_agent_level([case], 2.5)
        self.assertFalse(rows[0]["contract_ok"])

    def test_invalid_judge_schema_fails_closed(self):
        client = MagicMock()
        client.messages.create.return_value = SimpleNamespace(content=[
            SimpleNamespace(type="tool_use", name="record_verdict", input={
                "hallucination_free": "yes", "sources_cited": True, "refused": False})])
        with patch.object(judge, "_get_client", return_value=client):
            verdict = judge.judge_response("q", [], "a")
        self.assertIsNone(verdict["hallucination_free"])


class ImportAndThresholdTests(unittest.TestCase):
    def test_zero_threshold_is_preserved(self):
        self.assertEqual(resolve_min_score(0.0), 0.0)
        self.assertEqual(resolve_min_score(None), DEFAULT_MIN_MATCH_SCORE)

    def test_invalid_thresholds_fail_before_database_access(self):
        for value in (-1, math.nan, math.inf, True, "2.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                query_graph("pressure", min_score=value)

    def test_seed_contains_no_delete_and_schema_no_drop(self):
        seed = load_graph.read_statements(load_graph.SEED_FILE)
        schema = load_graph.read_statements(load_graph.SCHEMA_FILE)
        self.assertTrue(seed)
        self.assertFalse(any("DELETE" in s.upper() for s in seed))
        self.assertFalse(any("DROP" in s.upper() for s in schema))

    def test_seed_uses_one_managed_transaction(self):
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        tx = MagicMock()
        session.execute_write.side_effect = lambda callback: callback(tx)
        load_graph.publish_seed(driver, "neo4j", ["first", "second"])
        session.execute_write.assert_called_once()
        self.assertEqual([c.args[0] for c in tx.run.call_args_list], ["first", "second"])
        self.assertEqual(tx.run.return_value.consume.call_count, 2)
        session.run.assert_not_called()

    def test_seed_failure_propagates_to_managed_transaction(self):
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        tx = MagicMock()
        tx.run.side_effect = [MagicMock(), RuntimeError("invalid seed")]
        session.execute_write.side_effect = lambda callback: callback(tx)
        with self.assertRaises(RuntimeError):
            load_graph.publish_seed(driver, "neo4j", ["first", "bad"])

    def test_index_readiness_is_awaited(self):
        driver = MagicMock()
        load_graph.wait_for_indexes(driver, "neo4j")
        session = driver.session.return_value.__enter__.return_value
        session.run.assert_called_once_with("CALL db.awaitIndexes(120)")
        session.run.return_value.consume.assert_called_once()


if __name__ == "__main__":
    unittest.main()
