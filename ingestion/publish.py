"""Publish a manually approved snapshot to a separate Neo4j evidence graph."""
from __future__ import annotations

import json
from pathlib import Path

from ingestion.evidence import digest
from ingestion.store import approved_records, check_integrity


def export_snapshot(run: Path) -> dict:
    manifest = check_integrity(run)
    records = approved_records(run)
    content = {"manifest_sha256": digest((run / "manifest.json").read_bytes()), "records": records}
    return {"snapshot_id": digest(content), "document_sha256": manifest["pdf_sha256"],
            "title": manifest["title"], **content}


def publish_snapshot(driver, database: str, snapshot: dict) -> None:
    """No dynamic labels/Cypher from the model; no mutation of the chatbot graph.

    Records live as reviewed assertions, with typed entity endpoints. A separate
    serving adapter will be required to promote them into the assistant's graph.
    """
    relations = {"INDICATES", "RESOLVED_BY", "APPLIES_TO", "IN_STEP"}
    def write(tx):
        tx.run("MERGE (s:IngestionSnapshot {id:$id}) SET s.document_sha256=$doc, s.title=$title, s.manifest_sha256=$manifest",
               id=snapshot["snapshot_id"], doc=snapshot["document_sha256"], title=snapshot["title"],
               manifest=snapshot["manifest_sha256"]).consume()
        for record in snapshot["records"]:
            p = record["payload"]
            tx.run("""MATCH (s:IngestionSnapshot {id:$snapshot})
                MERGE (c:ReviewedClaim {id:$id, snapshot_id:$snapshot})
                SET c.record_type=$kind, c.payload_json=$payload, c.evidence_json=$evidence,
                    c.review_json=$review
                MERGE (s)-[:CONTAINS]->(c)""",
                   snapshot=snapshot["snapshot_id"], id=record["id"], kind=record["record_type"],
                   payload=json.dumps(p, ensure_ascii=False), evidence=json.dumps(record["evidence"], ensure_ascii=False),
                   review=json.dumps(record["decision"], ensure_ascii=False)).consume()
            if record["record_type"] == "entity":
                tx.run("""MATCH (c:ReviewedClaim {id:$claim, snapshot_id:$snapshot})
                    MERGE (e:ManualEntity {snapshot_id:$snapshot, kind:$kind, name:$name})
                    MERGE (c)-[:DESCRIBES]->(e)""", claim=record["id"], snapshot=snapshot["snapshot_id"],
                       kind=p["kind"], name=p["name"]).consume()
        for record in snapshot["records"]:
            if record["record_type"] != "relation":
                continue
            p = record["payload"]
            if p["predicate"] not in relations:
                raise ValueError("Unknown relation predicate")
            # Predicate is retained on a reified claim so conditions/provenance
            # cannot be lost or merged into a broader, unconditional relation.
            tx.run("""MATCH (c:ReviewedClaim {id:$claim, snapshot_id:$snapshot}),
                    (a:ManualEntity {snapshot_id:$snapshot, kind:$akind, name:$aname}),
                    (b:ManualEntity {snapshot_id:$snapshot, kind:$bkind, name:$bname})
                SET c.predicate=$predicate
                MERGE (c)-[:SUBJECT]->(a) MERGE (c)-[:OBJECT]->(b)""",
                   claim=record["id"], snapshot=snapshot["snapshot_id"], akind=p["subject_kind"],
                   aname=p["subject_name"], bkind=p["object_kind"], bname=p["object_name"], predicate=p["predicate"]).consume()
    with driver.session(database=database) as session:
        for query in (
            "CREATE CONSTRAINT ingestion_snapshot_id IF NOT EXISTS FOR (s:IngestionSnapshot) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT reviewed_claim_snapshot IF NOT EXISTS FOR (c:ReviewedClaim) REQUIRE (c.id, c.snapshot_id) IS UNIQUE",
            "CREATE CONSTRAINT manual_entity_identity IF NOT EXISTS FOR (e:ManualEntity) REQUIRE (e.snapshot_id, e.kind, e.name) IS UNIQUE",
        ):
            session.run(query).consume()
        session.execute_write(write)
