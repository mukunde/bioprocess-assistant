"""Claude agent with tool use, grounded on the knowledge graph (anti-hallucination)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import DEFAULT_MIN_MATCH_SCORE, query_graph

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL = "claude-sonnet-4-6"
MAX_TURNS = 5

SYSTEM_PROMPT = """You are a troubleshooting assistant specialized in Protein A capture chromatography (a downstream bioprocess unit operation).

You have a single tool: `query_graph(symptom)`. It queries a knowledge graph that holds all the domain knowledge (symptoms -> causes -> actions). The graph content is in English; every node is sourced from a public handbook.

Non-negotiable rules:
1. You answer ONLY from the data returned by the tool. You never add a cause, an action, or a source that is not in the tool result.
2. You CITE the `source` of every cause and every action you mention. Suggested format: in parentheses at the end of the sentence, e.g. *(source: Cytiva, ...)*.
3. If the tool returns `found: false`, or if no cause matches the question, you explicitly state that you do not have this information in your knowledge base. You invent nothing and never fill in from your general knowledge.
4. If the question is out of scope (a unit operation other than Protein A capture, or a non-troubleshooting topic), you flag it and do not answer on the merits.
5. When you decline (rule 3 or 4), keep it to one or two sentences: state that you do not have the information (or that it is out of scope) and that the user may rephrase. Do NOT list specific symptoms, causes, actions, vendors, handbooks, standards, or any other concrete reference - nothing beyond what the tool returned.
6. Answer in the user's language (French or English): mirror the language of their question.

Style: clear, structured for a process engineer. You may use bullet points. At the start of your answer, name the symptom you matched in the graph to confirm your understanding."""

TOOLS = [
    {
        "name": "query_graph",
        "description": (
            "Query the Protein A capture troubleshooting knowledge graph. Takes a "
            "symptom described as a short English search phrase (e.g. 'capture yield "
            "drop', 'high column pressure', 'aggregates in elution pool') and returns "
            "the matched symptom with its probable causes and corrective actions, all "
            "sourced from public handbooks."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symptom": {
                    "type": "string",
                    "description": (
                        "A concise ENGLISH search phrase describing the observed "
                        "symptom. The knowledge graph is in English, so translate from "
                        "the user's question if it is in another language (e.g. French). "
                        "Stay factual; avoid pronouns and negations."
                    ),
                }
            },
            "required": ["symptom"],
        },
    }
]


def run_agent(
    user_message: str,
    min_score: float = DEFAULT_MIN_MATCH_SCORE,
    tool_outputs: list | None = None,
) -> tuple[str, float | None, float]:
    """Run the agent and return (text, last_match_score, threshold_used).

    `last_match_score` is the highest score returned by the tool across this
    turn's tool calls (None if no candidate was returned at all).

    If a list is passed as `tool_outputs`, each `query_graph` result the agent
    received is appended to it - used by the evaluation harness to give the
    LLM judge the exact grounding the agent had access to."""
    # override=True makes the local .env authoritative over any stray (possibly
    # empty) ANTHROPIC_API_KEY already in the shell. No-op on Render (no .env file).
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": user_message}]
    last_score: float | None = None

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            max_tokens=2048,
        )

        if response.stop_reason != "tool_use":
            text = "\n".join(b.text for b in response.content if b.type == "text").strip()
            return text, last_score, min_score

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "query_graph":
                result = query_graph(block.input["symptom"], min_score=min_score)
                if tool_outputs is not None:
                    tool_outputs.append(result)
                # Track the highest seen score, even when it falls under threshold.
                score = result.get("match_score")
                if score is not None and (last_score is None or score > last_score):
                    last_score = score
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
        messages.append({"role": "user", "content": tool_results})

    return (
        "Désolé, je n'ai pas pu produire de réponse dans le temps imparti.",
        last_score,
        min_score,
    )
