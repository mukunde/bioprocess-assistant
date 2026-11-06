"""Render only graph facts selected by the model; never render model prose."""
from __future__ import annotations

from enum import StrEnum
import html
import json
import re


class RejectionReason(StrEnum):
    INVALID_JSON = "invalid_json"
    INVALID_FIELDS = "invalid_fields"
    INVALID_LANGUAGE_OR_IDS = "invalid_language_or_ids"
    INVALID_RESULT_ID = "invalid_result_id"
    DUPLICATE_RESULT_IDS = "duplicate_result_ids"
    RETRIEVAL_MISS = "retrieval_miss"
    INCOMPLETE_GRAPH_PATH = "incomplete_graph_path"
    EMPTY_RESPONSE = "empty_response"
    INVALID_STATUS_OR_SELECTION = "invalid_status_or_selection"
    MISSING_GRAPH_FIELD = "missing_graph_field"


class GroundingError(ValueError):
    """The proposed response cannot be grounded in complete tool results."""

    def __init__(self, reason: RejectionReason, message: str):
        super().__init__(message)
        self.reason = reason


def refusal(language: str = "en") -> str:
    if language == "fr":
        return "Je n'ai pas cette information dans ma base de connaissances. Vous pouvez reformuler votre question."
    return "I don't have this information in my knowledge base. You may rephrase your question."


def _text(node: dict, field: str) -> str:
    value = node.get(field)
    if not isinstance(value, str) or not value.strip():
        raise GroundingError(RejectionReason.MISSING_GRAPH_FIELD, f"Missing graph field: {field}")
    # Graph content is data, including any Markdown/HTML it may contain.
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", html.escape(value, quote=False))


def render_selection(raw: str, results: list[dict]) -> tuple[str, dict]:
    """Validate the final JSON and return text plus deterministic answer metadata.

    Result IDs are zero-based indices in the recorded query_graph outputs.
    Refusals contain no model-authored explanation. Descriptions stay verbatim
    in the canonical graph language; reviewed translations can be added later.
    """
    if isinstance(raw, str) and not raw.strip():
        raise GroundingError(RejectionReason.EMPTY_RESPONSE, "Final answer is empty")
    try:
        selection = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise GroundingError(RejectionReason.INVALID_JSON, "Final answer is not JSON") from exc
    if not isinstance(selection, dict) or set(selection) != {"status", "language", "result_ids"}:
        raise GroundingError(RejectionReason.INVALID_FIELDS, "Invalid response fields")
    language = selection["language"]
    ids = selection["result_ids"]
    if language not in ("fr", "en") or not isinstance(ids, list):
        raise GroundingError(RejectionReason.INVALID_LANGUAGE_OR_IDS, "Invalid language or result IDs")
    metadata = {"status": selection["status"], "language": language, "symptoms": []}
    if selection["status"] == "refuse" and not ids:
        return refusal(language), metadata
    if selection["status"] != "answer" or not ids:
        raise GroundingError(RejectionReason.INVALID_STATUS_OR_SELECTION, "Invalid status or empty selection")
    if any(type(i) is not int or i < 0 or i >= len(results) for i in ids):
        raise GroundingError(RejectionReason.INVALID_RESULT_ID, "Unknown result ID")
    if len(set(ids)) != len(ids):
        raise GroundingError(RejectionReason.DUPLICATE_RESULT_IDS, "Duplicate result IDs")

    labels = ("Symptôme", "Cause possible", "Action", "Source") if language == "fr" else (
        "Symptom", "Possible cause", "Action", "Source"
    )
    sections = []
    for i in ids:
        result = results[i]
        if result.get("found") is not True:
            raise GroundingError(RejectionReason.RETRIEVAL_MISS, "Selected result is a retrieval miss")
        symptom = result.get("symptom")
        causes = result.get("causes")
        if not isinstance(symptom, dict) or not isinstance(causes, list) or not causes:
            raise GroundingError(RejectionReason.INCOMPLETE_GRAPH_PATH, "Incomplete graph path")
        lines = [f"**{labels[0]} : {_text(symptom, 'name')}**",
                 f"{labels[3]} : {_text(symptom, 'source')}"]
        for cause in causes:
            if not isinstance(cause, dict):
                raise GroundingError(RejectionReason.INCOMPLETE_GRAPH_PATH, "Invalid cause")
            lines.extend([f"**{labels[1]} : {_text(cause, 'name')}**",
                          _text(cause, "description"),
                          f"{labels[3]} : {_text(cause, 'source')}"])
            actions = cause.get("actions")
            if not isinstance(actions, list) or not actions:
                raise GroundingError(RejectionReason.INCOMPLETE_GRAPH_PATH, "Cause has no sourced action")
            for action in actions:
                if not isinstance(action, dict):
                    raise GroundingError(RejectionReason.INCOMPLETE_GRAPH_PATH, "Invalid action")
                lines.extend([f"**{labels[2]} : {_text(action, 'name')}**",
                              _text(action, "description"),
                              f"{labels[3]} : {_text(action, 'source')}"])
        sections.append("\n\n".join(lines))
        metadata["symptoms"].append(symptom["name"])
    if language == "fr":
        sections.insert(0, "Les descriptions techniques ci-dessous sont conservées dans la langue anglaise du graphe.")
    return "\n\n---\n\n".join(sections), metadata
