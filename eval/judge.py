"""LLM-as-judge for the agent-level evaluation.

Given the question, the exact tool output the agent received (its only allowed
knowledge), and the agent's final answer, Claude judges - with forced structured
output - whether the answer is grounded (no hallucination), properly sourced,
and whether it refused. This is what actually measures the anti-hallucination
guarantee end to end (the tool-level eval only checks retrieval).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JUDGE_MODEL = "claude-sonnet-4-6"

JUDGE_SYSTEM = """You are a strict evaluator for a troubleshooting assistant grounded on a knowledge graph.

The assistant's contract:
- answer ONLY from the data returned by its `query_graph` tool,
- cite the `source` of every cause and action it mentions,
- explicitly decline (e.g. "I don't have this information in my knowledge base", or "this is out of scope") when the tool returns nothing relevant (found = false).

You receive the user question (French), the tool output the assistant got (JSON -
the ONLY knowledge it was allowed to use), and the assistant's final answer (French).

Judge strictly, then call `record_verdict` with:
- hallucination_free: true iff EVERY factual claim about causes, actions, or sources
  in the answer is supported by the tool output. If the tool output has found=false
  and the answer declines without inventing causes/actions/sources, this is true.
  Any invented cause/action/source, or specific corrective advice not present in the
  tool output, makes it false.
- sources_cited: true iff every cause and action mentioned in the answer is
  accompanied by a source string drawn from the tool output. If the answer is a
  refusal with no causes/actions, set true (not applicable).
- refused: true iff the answer declines to provide causes/actions (states it lacks
  the information, or that the question is out of scope). false iff it provides
  causes/actions on the merits.
- rationale: one concise sentence (English)."""

VERDICT_TOOL = {
    "name": "record_verdict",
    "description": "Record the structured evaluation verdict for one answer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "hallucination_free": {"type": "boolean"},
            "sources_cited": {"type": "boolean"},
            "refused": {"type": "boolean"},
            "rationale": {"type": "string"},
        },
        "required": ["hallucination_free", "sources_cited", "refused", "rationale"],
    },
}

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        load_dotenv(PROJECT_ROOT / ".env", override=True)
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def judge_response(question: str, tool_outputs: list, agent_response: str) -> dict:
    """Return a verdict dict: hallucination_free, sources_cited, refused, rationale."""
    client = _get_client()
    user = (
        f"QUESTION:\n{question}\n\n"
        f"TOOL OUTPUT (the only allowed knowledge):\n"
        f"{json.dumps(tool_outputs, ensure_ascii=False, indent=2)}\n\n"
        f"ASSISTANT ANSWER:\n{agent_response}"
    )
    resp = client.messages.create(
        model=JUDGE_MODEL,
        system=JUDGE_SYSTEM,
        max_tokens=512,
        tools=[VERDICT_TOOL],
        tool_choice={"type": "tool", "name": "record_verdict"},
        messages=[{"role": "user", "content": user}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "record_verdict":
            return block.input
    return {
        "hallucination_free": None,
        "sources_cited": None,
        "refused": None,
        "rationale": "judge returned no verdict",
    }
