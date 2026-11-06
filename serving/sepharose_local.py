"""Local, append-only serving decisions for a separate Sepharose authority."""
from contextlib import closing
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4

from serving.sepharose_candidate import Candidate, REQUIRED, ROOT, SCOPES, canonical

VALIDATOR = "project_user_via_conversation"
SOURCE_IDS = frozenset().union(*REQUIRED.values())
NOTICE = "Local documentary service · Protein A/G Sepharose. Laboratory use requires separate approval."


def inventory(sources, reviews):
    result = {}
    for key, items, allowed in (("source_ids", sources, SOURCE_IDS), ("review_ids", reviews, SCOPES)):
        if (not isinstance(items, (list, tuple)) or any(type(item) is not str for item in items)
                or len(set(items)) != len(items) or not set(items) <= set(allowed)):
            raise ValueError("Invalid withdrawal inventory")
        result[key] = sorted(items)
    return result


class Authority:
    """Trusted local operator writes; the serving process opens the DB read-only."""

    def __init__(self, database, candidate_root):
        self.database = Path(database).resolve()
        self.root = Path(candidate_root).resolve()
        protected = [self.root, ROOT / ".local-tools/mabselect-registry-v02-runtime"]
        if os.environ.get("MABSELECT_REGISTRY_ROOT"):
            protected.append(Path(os.environ["MABSELECT_REGISTRY_ROOT"]))
        if (any(self.database.is_relative_to(path.resolve()) for path in protected)
                or self.database.name != "sepharose-authority.sqlite3"):
            raise ValueError("Use a separate Sepharose authority database")

    def initialize(self):
        """Create an empty authority. No approval or release is written."""
        os.close(os.open(self.database, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("CREATE TABLE decisions (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL, digest TEXT NOT NULL)")
            db.execute("CREATE TABLE head (seq INTEGER NOT NULL, digest TEXT)")
            db.execute("INSERT INTO head VALUES (0, NULL)")

    def _candidate(self):
        release, _, fingerprint = Candidate(self.root, preview=True)._snapshot()
        if any(release["withdrawal_simulations"].values()):
            raise ValueError("A simulated candidate cannot serve")
        return release["release_id"], fingerprint

    def _history(self, db, identity):
        current = None
        previous = None
        for seq, payload, digest in db.execute("SELECT seq,payload,digest FROM decisions ORDER BY seq"):
            event = json.loads(payload)
            if (set(event) != {"seq", "previous", "operation", "identity", "inventory", "validator", "decision", "nonce"}
                    or event["seq"] != seq or seq != (current["seq"] + 1 if current else 1)
                    or event["previous"] != previous or event["identity"] != list(identity)
                    or event["validator"] != VALIDATOR or not isinstance(event["decision"], str)
                    or not event["decision"].strip() or canonical(event).decode() != payload or digest != sha256(canonical(event)).hexdigest()):
                raise ValueError("Invalid authority history")
            holds = event["inventory"]
            if holds != inventory(holds["source_ids"], holds["review_ids"]):
                raise ValueError("Invalid authority inventory")
            self._transition(current, event["operation"], holds)
            current, previous = event, digest
        head = db.execute("SELECT seq,digest FROM head").fetchall()
        if head != [(current["seq"] if current else 0, previous)]:
            raise ValueError("Authority head mismatch")
        return current, previous

    @staticmethod
    def _transition(current, operation, holds):
        enabled = current is not None and current["operation"] != "disable"
        if operation == "enable" and not enabled:
            if current and any(not set(values) <= set(holds[key]) for key, values in current["inventory"].items()):
                raise ValueError("Re-enabling must retain the latest withdrawals")
        elif operation == "withdrawals" and enabled:
            return
        elif operation == "disable" and enabled and holds == current["inventory"]:
            return
        else:
            raise ValueError("Invalid authority transition")

    def record(self, operation, *, expected_snapshot, validator, original_human_message,
               source_ids=None, review_ids=None):
        """Record one explicit decision. This operator API is outside Chainlit."""
        if validator != VALIDATOR or type(original_human_message) is not str or not original_human_message.strip():
            raise ValueError("An explicit decision from the designated validator is required")
        with closing(sqlite3.connect(self.database.as_uri() + "?mode=rw", uri=True)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if operation == "disable":
                if source_ids is not None or review_ids is not None:
                    raise ValueError("Disabling preserves the current inventory")
                first = db.execute("SELECT payload FROM decisions ORDER BY seq LIMIT 1").fetchone()
                if first is None:
                    raise ValueError("No release to disable")
                identity = tuple(json.loads(first[0])["identity"])
            else:
                identity = self._candidate()
            if expected_snapshot != identity[1]:
                raise ValueError("Decision snapshot mismatch")
            current, previous = self._history(db, identity)
            holds = current["inventory"] if operation == "disable" and current else inventory(source_ids, review_ids)
            self._transition(current, operation, holds)
            event = dict(seq=current["seq"] + 1 if current else 1, previous=previous, operation=operation,
                         identity=list(identity), inventory=holds, validator=validator,
                         decision=original_human_message, nonce=uuid4().hex)
            digest = sha256(canonical(event)).hexdigest()
            db.execute("INSERT INTO decisions VALUES (?,?,?)", (event["seq"], canonical(event).decode(), digest))
            db.execute("UPDATE head SET seq=?,digest=?", (event["seq"], digest))
        return digest

    def snapshot(self, identity):
        with closing(sqlite3.connect(self.database.as_uri() + "?mode=ro", uri=True)) as db, db:
            db.execute("BEGIN")
            event, generation = self._history(db, identity)
        if not event or event["operation"] == "disable":
            raise ValueError("Sepharose serving is disabled")
        return event["inventory"], generation


class _AuthorizedCandidate(Candidate):
    """Use the staged evaluator under a verified authority snapshot."""

    def __init__(self, authority):
        super().__init__(authority.root, preview=True)
        self.authority = authority

    def _snapshot(self):
        release, sources, fingerprint = super()._snapshot()
        if any(release["withdrawal_simulations"].values()):
            raise ValueError("A simulated candidate cannot serve")
        holds, generation = self.authority.snapshot((release["release_id"], fingerprint))
        effective = deepcopy(release)
        effective["withdrawal_simulations"] = holds
        return effective, sources, generation


class LocalSepharose:
    def __init__(self, authority):
        self.authority = authority

    def current(self, generation):
        try:
            return bool(generation) and _AuthorizedCandidate(self.authority)._snapshot()[2] == generation
        except Exception:
            return False

    def evaluate(self, value):
        candidate = _AuthorizedCandidate(self.authority)
        generation = None
        try:
            generation = candidate._snapshot()[2]
        except Exception:
            pass
        out = candidate.evaluate(value)
        if not self.current(generation) or out["status"] in ("unavailable", "invalid_request"):
            return {"status": "unavailable", "bundles": [], "citations": [], "items": []}
        out.update(stage="local_documentary", serving_activated=True, notice=NOTICE, generation=generation)
        for citation in out["citations"]:
            citation["generation"] = generation
        return out

    def source(self, release_id, source_id, generation):
        unavailable = {"status": "unavailable", "passage": None, "reviews": []}
        if not self.current(generation):
            return unavailable
        view = _AuthorizedCandidate(self.authority).source(release_id, source_id)
        if view["status"] != "available" or not self.current(generation):
            return unavailable
        return dict(view, stage="local_documentary", serving_activated=True, notice=NOTICE, generation=generation)
