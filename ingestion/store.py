"""Local immutable artifacts and append-only SQLite manual decisions."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from ingestion.evidence import digest


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect(run: Path):
    db = sqlite3.connect(run / "review.sqlite3", timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(run: Path, manifest: dict, records: list[dict]) -> None:
    write_json(run / "records.json", records)
    manifest["files"]["records.json"] = digest((run / "records.json").read_bytes())
    write_json(run / "manifest.json", manifest)
    with connect(run) as db:
        db.executescript("""
            CREATE TABLE run (manifest_sha256 TEXT NOT NULL);
            CREATE TABLE records (id TEXT PRIMARY KEY, content TEXT NOT NULL);
            CREATE TABLE decisions (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL REFERENCES records(id), action TEXT NOT NULL,
                reviewer TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL, source_checked INTEGER NOT NULL);
        """)
        db.execute("INSERT INTO run VALUES (?)", (digest((run / "manifest.json").read_bytes()),))
        db.executemany("INSERT INTO records VALUES (?, ?)",
                       [(r["id"], json.dumps(r, ensure_ascii=False)) for r in records])


def check_integrity(run: Path) -> dict:
    with connect(run) as db:
        row = db.execute("SELECT manifest_sha256 FROM run").fetchone()
    if not row or digest((run / "manifest.json").read_bytes()) != row[0]:
        raise ValueError("Run manifest changed; review is invalid")
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["files"].items():
        path = (run / name).resolve()
        if path.parent != run.resolve() or digest(path.read_bytes()) != expected:
            raise ValueError(f"Artifact changed or invalid path: {name}")
    return manifest


def list_records(run: Path) -> list[dict]:
    check_integrity(run)
    expected = {r["id"]: r for r in json.loads((run / "records.json").read_text(encoding="utf-8"))}
    with connect(run) as db:
        rows = db.execute("SELECT id, content FROM records ORDER BY rowid").fetchall()
        if len(rows) != len(expected):
            raise ValueError("Review records do not match immutable extraction")
        records = []
        for row in rows:
            record = json.loads(row["content"])
            if expected.get(row["id"]) != record:
                raise ValueError("Record was modified outside the review workflow")
            decision = db.execute("SELECT * FROM decisions WHERE record_id=? ORDER BY sequence DESC LIMIT 1",
                                  (row["id"],)).fetchone()
            record["decision"] = dict(decision) if decision else {"action": "pending"}
            records.append(record)
    return records


def decide(run: Path, record_id: str, action: str, reviewer: str, note: str,
           source_checked: bool = False) -> None:
    if action not in ("approve", "reject") or not reviewer.strip() or not note.strip():
        raise ValueError("A decision requires approve/reject, reviewer and an explanatory note")
    records = list_records(run)
    record = next((r for r in records if r["id"] == record_id), None)
    if record is None:
        raise ValueError("Unknown record")
    if action == "approve":
        if source_checked is not True or record["issues"]:
            raise ValueError("Approval requires located evidence and explicit manual PDF verification")
        if record["record_type"] == "relation":
            payload = record["payload"]
            approved = {(r["payload"]["kind"], r["payload"]["name"]) for r in records
                        if r["record_type"] == "entity" and r["decision"]["action"] == "approve"}
            if any((payload[f"{side}_kind"], payload[f"{side}_name"]) not in approved
                   for side in ("subject", "object")):
                raise ValueError("Approve both endpoint entities before the relation")
    with connect(run) as db:
        db.execute("INSERT INTO decisions (record_id, action, reviewer, note, created_at, manifest_sha256, source_checked) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (record_id, action, reviewer.strip(), note.strip(), now(),
                    digest((run / "manifest.json").read_bytes()), int(source_checked)))


def approved_records(run: Path) -> list[dict]:
    records = [r for r in list_records(run) if r["decision"]["action"] == "approve"]
    if not records:
        raise ValueError("No manually approved records")
    endpoints = {(r["payload"]["kind"], r["payload"]["name"]) for r in records if r["record_type"] == "entity"}
    for record in records:
        if record["issues"] or not record["decision"].get("source_checked"):
            raise ValueError("Invalid approved evidence")
        if record["record_type"] == "relation":
            p = record["payload"]
            if any((p[f"{side}_kind"], p[f"{side}_name"]) not in endpoints for side in ("subject", "object")):
                raise ValueError("Approved relation has an unapproved endpoint")
    return records
