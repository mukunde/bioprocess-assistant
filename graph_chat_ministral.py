"""Run the graph chat with the installed Ministral model through loopback Ollama."""
from copy import deepcopy
import json
import os
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from agent import SELECTION_OUTPUT, SYSTEM_PROMPT, TOOLS, apply_pressure_guard
from grounding import GroundingError, refusal, render_selection
from tools import DEFAULT_MIN_MATCH_SCORE, PROJECT_ROOT, load_graph_dotenv, query_graph, validate_min_score

MODEL = "bioprocess-local:latest"
LOCAL_LANGUAGES = {"fr": "Français", "en": "English"}
MAX_TOOL_CALLS = 5


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _chat(messages, **options):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": "15m",
        "options": {"temperature": 0, "num_ctx": 4096, "num_predict": 160},
        **options,
    }
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with build_opener(ProxyHandler({}), _NoRedirect()).open(request, timeout=180) as response:
        reply = json.load(response)
    message = reply.get("message")
    if reply.get("done_reason") != "stop" or not isinstance(message, dict):
        raise ValueError("Incomplete response from the local model")
    return message


def _search_phrases(message):
    calls = message.get("tool_calls", [])
    if not isinstance(calls, list) or len(calls) > MAX_TOOL_CALLS:
        raise ValueError("Invalid local tool requests")
    phrases = []
    for call in calls:
        function = call.get("function") if isinstance(call, dict) else None
        arguments = function.get("arguments") if isinstance(function, dict) else None
        symptom = arguments.get("symptom") if isinstance(arguments, dict) else None
        if not isinstance(symptom, str) or not symptom.strip() or function.get("name") != "query_graph":
            raise ValueError("Invalid local graph search")
        phrases.append(symptom)
    return phrases


def _compact(result):
    return {
        "found": result["found"],
        "symptom": result["symptom"]["name"] if result["found"] else None,
        "causes": [
            {"name": cause["name"], "actions": [action["name"] for action in cause["actions"]]}
            for cause in result["causes"]
        ],
    }


def run_ministral(user_message, min_score=DEFAULT_MIN_MATCH_SCORE, *, language, answer_metadata):
    """Select compact result IDs and render the original, complete graph paths."""
    validate_min_score(min_score)
    if language not in LOCAL_LANGUAGES:
        raise ValueError("Unsupported local answer language")
    answer_metadata.clear()
    answer_metadata.update(status="error", symptoms=[])
    tool = TOOLS[0]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]
    first = _chat(messages, tools=[{"type": "function", "function": {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["input_schema"],
    }}])
    phrases = _search_phrases(first)
    results = []
    if phrases:
        load_graph_dotenv(PROJECT_ROOT / ".env")
        uri = urlsplit(os.environ["NEO4J_URI"])
        if uri.scheme != "bolt" or uri.hostname not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("The local graph chat requires a direct loopback Neo4j connection")
        messages.append({"role": "assistant", "content": "", "tool_calls": first["tool_calls"]})
    for phrase in phrases:
        result = query_graph(phrase, min_score=min_score)
        messages.append({"role": "tool", "tool_name": "query_graph", "content": json.dumps({
            "result_id": len(results), "result": _compact(result),
        }, ensure_ascii=False)})
        results.append(result)

    available = [index for index, result in enumerate(results) if result["found"] is True]
    schema = deepcopy(SELECTION_OUTPUT["format"]["schema"])
    schema["properties"]["language"]["enum"] = [language]
    ids = schema["properties"]["result_ids"]
    if available:
        ids["items"]["enum"] = available
    else:
        ids["maxItems"] = 0
    messages[0]["content"] += (
        "\nThe tool result has an explicit result_id field. Select IDs of whole tool results, "
        "never individual causes or actions. The application requests the response language "
        f"{language}. Allowed result IDs: {json.dumps(available)}."
    )
    final = _chat(messages, format=schema)
    score = max((result["match_score"] for result in results if result["match_score"] is not None), default=None)
    if final.get("tool_calls"):
        return refusal(language), score, min_score
    try:
        rendered, metadata = render_selection(final.get("content"), results)
    except GroundingError:
        return refusal(language), score, min_score
    if metadata["language"] != language:
        return refusal(language), score, min_score
    rendered = apply_pressure_guard(user_message, rendered, metadata)
    answer_metadata.update(metadata)
    return rendered, score, min_score
