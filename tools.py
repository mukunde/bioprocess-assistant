"""Single tool exposed to the agent: query the Neo4j knowledge graph."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parent
_driver: Driver | None = None

_LUCENE_SPECIALS = r'+-&|!(){}[]^"~*?:\/'

# Minimum Lucene relevance score required for a symptom match.
# Without this floor, the full-text search returns the top match even when only
# generic terms like "pool" or "élution" overlap — leading to spurious matches
# (e.g. a query about endotoxines matching the HCP symptom on shared common words).
# Tunable: lower if legitimate queries are being rejected, raise if weak matches still leak.
_MIN_MATCH_SCORE = 2.5


def _get_driver() -> Driver:
    global _driver
    if _driver is None:
        load_dotenv(PROJECT_ROOT / ".env")
        _driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        )
    return _driver


def _sanitize_for_lucene(q: str) -> str:
    # Replace Lucene operators with spaces to avoid query parse errors.
    for c in _LUCENE_SPECIALS:
        q = q.replace(c, " ")
    return " ".join(q.split())


def query_graph(symptom: str) -> dict:
    """Return the best-matching symptom (Neo4j full-text, french analyzer)
    with its causes and corrective actions, all sourced."""
    sanitized = _sanitize_for_lucene(symptom)
    if not sanitized:
        return {"found": False, "symptom": None, "causes": []}

    query = """
    CALL db.index.fulltext.queryNodes('symptom_text', $q) YIELD node AS s, score
    WHERE score >= $threshold
    WITH s ORDER BY score DESC LIMIT 1
    MATCH (s)-[:INDICATES]->(c:Cause)
    OPTIONAL MATCH (c)-[:RESOLVED_BY]->(a:Action)
    RETURN s.name AS symptom_name,
           s.source AS symptom_source,
           c.name AS cause_name,
           c.description AS cause_description,
           c.source AS cause_source,
           a.name AS action_name,
           a.description AS action_description,
           a.source AS action_source
    ORDER BY c.name, a.name
    """
    driver = _get_driver()
    with driver.session(database=os.environ["NEO4J_DATABASE"]) as session:
        rows = list(session.run(query, q=sanitized, threshold=_MIN_MATCH_SCORE))

    if not rows:
        return {"found": False, "symptom": None, "causes": []}

    causes: dict[str, dict] = {}
    for row in rows:
        cname = row["cause_name"]
        if cname not in causes:
            causes[cname] = {
                "name": cname,
                "description": row["cause_description"],
                "source": row["cause_source"],
                "actions": [],
            }
        if row["action_name"]:
            causes[cname]["actions"].append({
                "name": row["action_name"],
                "description": row["action_description"],
                "source": row["action_source"],
            })

    return {
        "found": True,
        "symptom": {
            "name": rows[0]["symptom_name"],
            "source": rows[0]["symptom_source"],
        },
        "causes": list(causes.values()),
    }


if __name__ == "__main__":
    # Smoke test: python tools.py
    import json
    print(json.dumps(query_graph("rendement de capture"), indent=2, ensure_ascii=False))
