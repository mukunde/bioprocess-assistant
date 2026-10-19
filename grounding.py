"""Render only graph facts selected by the model; never render model prose."""
from __future__ import annotations

import html
import json
import re


class GroundingError(ValueError):
    """The proposed response cannot be grounded in complete tool results."""


def refusal(language: str = "en") -> str:
    if language == "fr":
        return "Je n'ai pas cette information dans ma base de connaissances. Vous pouvez reformuler votre question."
    return "I don't have this information in my knowledge base. You may rephrase your question."


def _text(node: dict, field: str) -> str:
    value = node.get(field)
    if not isinstance(value, str) or not value.strip():
        raise GroundingError(f"Missing graph field: {field}")
    # Graph content is data, including any Markdown/HTML it may contain.
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", html.escape(value))


def render_selection(raw: str, results: list[dict]) -> tuple[str, dict]:
    """Validate the final JSON and return text plus deterministic answer metadata.

    Result IDs are zero-based indices in the recorded query_graph outputs.
    Refusals contain no model-authored explanation. Descriptions stay verbatim
    in the canonical graph language; reviewed translations can be added later.
    """
    try:
        selection = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise GroundingError("Final answer is not JSON") from exc
    if not isinstance(selection, dict) or set(selection) != {"status", "language", "result_ids"}:
        raise GroundingError("Invalid response fields")
    language = selection["language"]
    ids = selection["result_ids"]
    if language not in ("fr", "en") or not isinstance(ids, list):
        raise GroundingError("Invalid language or result IDs")
    metadata = {"status": selection["status"], "language": language, "symptoms": []}
    if selection["status"] == "refuse" and not ids:
        return refusal(language), metadata
    if selection["status"] != "answer" or not ids:
        raise GroundingError("An answer requires retrieved results")
    if any(type(i) is not int or i < 0 or i >= len(results) for i in ids):
        raise GroundingError("Unknown result ID")
    if len(set(ids)) != len(ids):
        raise GroundingError("Duplicate result IDs")

    labels = ("Symptôme", "Cause possible", "Action", "Source") if language == "fr" else (
        "Symptom", "Possible cause", "Action", "Source"
    )
    sections = []
    for i in ids:
        result = results[i]
        if result.get("found") is not True:
            raise GroundingError("Selected result is a retrieval miss")
        symptom = result.get("symptom")
        causes = result.get("causes")
        if not isinstance(symptom, dict) or not isinstance(causes, list) or not causes:
            raise GroundingError("Incomplete graph path")
        lines = [f"**{labels[0]} : {_text(symptom, 'name')}**",
                 f"{labels[3]} : {_text(symptom, 'source')}"]
        for cause in causes:
            if not isinstance(cause, dict):
                raise GroundingError("Invalid cause")
            lines.extend([f"**{labels[1]} : {_text(cause, 'name')}**",
                          _text(cause, "description"),
                          f"{labels[3]} : {_text(cause, 'source')}"])
            actions = cause.get("actions")
            if not isinstance(actions, list) or not actions:
                raise GroundingError("Cause has no sourced action")
            for action in actions:
                if not isinstance(action, dict):
                    raise GroundingError("Invalid action")
                lines.extend([f"**{labels[2]} : {_text(action, 'name')}**",
                              _text(action, "description"),
                              f"{labels[3]} : {_text(action, 'source')}"])
        sections.append("\n\n".join(lines))
        metadata["symptoms"].append(symptom["name"])
    if language == "fr":
        sections.insert(0, "Les descriptions techniques ci-dessous sont conservées dans la langue anglaise du graphe.")
    return "\n\n---\n\n".join(sections), metadata
