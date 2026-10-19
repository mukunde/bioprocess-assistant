"""Locate quotes in immutable Docling items; this does not prove entailment."""
from __future__ import annotations

import hashlib
import json
import re


def digest(value) -> str:
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def source_blocks(document: dict) -> list[dict]:
    """Keep text items and whole table rows; include column/row context in evidence."""
    blocks = []
    for item in document.get("texts", []):
        text = item.get("text", "")
        if text:
            blocks.append(_block(item, text))
    for table in document.get("tables", []):
        cells = table.get("data", {}).get("table_cells", [])
        headers = [c for c in cells if c.get("column_header")]
        rows: dict[int, list] = {}
        for cell in cells:
            rows.setdefault(cell.get("start_row_offset_idx", 0), []).append(cell)
        for row, row_cells in sorted(rows.items()):
            ordered = sorted(row_cells, key=lambda c: c.get("start_col_offset_idx", 0))
            # Quotes can match a cell or a complete row, never an invented flattening
            # joining values across different rows. Header evidence is separate.
            joined = " | ".join(c.get("text", "") for c in ordered)
            block = _block(table, joined)
            block.update(table_row=row, cells=ordered, table_headers=headers)
            blocks.append(block)
            for cell in ordered:
                if cell.get("text"):
                    cell_block = _block(table, cell["text"])
                    cell_block.update(table_row=row, table_column=cell.get("start_col_offset_idx"),
                                      cells=[cell], table_headers=headers)
                    blocks.append(cell_block)
    return blocks


def _block(item: dict, text: str) -> dict:
    return {"item_ref": item["self_ref"], "text": text,
            "pdf_page_indices": sorted({p["page_no"] - 1 for p in item.get("prov", []) if p.get("page_no", 0) > 0}),
            "item_provenance": item.get("prov", []), "label": item.get("label")}


def locate_quotes(quotes: list[str], document: dict, ledger: dict) -> tuple[list[dict], list[str]]:
    evidence, issues = [], []
    blocks = source_blocks(document)
    for quote in quotes:
        if not quote.strip():
            issues.append("Empty source quote")
            continue
        pattern = re.compile(r"\s+".join(re.escape(part) for part in quote.split()))
        matches = []
        for block in blocks:
            for found in pattern.finditer(block["text"]):
                chunks = [str(key) for key, chunk in ledger.get("chunks", {}).items()
                          if block["item_ref"] in chunk.get("doc_item_refs", [])]
                matches.append({**block, "start": found.start(), "end": found.end(),
                                "source_quote": found.group(), "text_sha256": digest(block["text"].encode()),
                                "chunk_ids": chunks,
                                "headings": [h for key in chunks for h in ledger["chunks"][key].get("headings", [])],
                                "split_warning": any(ledger["chunks"][key].get("resplit_of") is not None for key in chunks)})
        # Shorter items are easier to inspect, but longer contexts may carry
        # different restrictions or point to another page. Never discard them.
        if matches:
            matches.sort(key=lambda m: len(m["text"]))
            if any(not m["pdf_page_indices"] for m in matches):
                issues.append(f"Quote has no PDF page anchor: {quote}")
            evidence.append({"requested_quote": quote, "location_status": "located_in_conversion",
                             "ambiguous": len(matches) > 1, "matches": matches})
        else:
            issues.append(f"Quote not found in source items: {quote}")
    if not quotes:
        issues.append("No source quotes supplied")
    return evidence, issues


def validate_document(document: dict, ledger: dict, page_count: int) -> None:
    if not isinstance(ledger.get("chunks"), dict) or not ledger["chunks"]:
        raise ValueError("Docling detailed provenance ledger has no chunks")
    for chunk in ledger["chunks"].values():
        if not isinstance(chunk.get("text"), str):
            raise ValueError("Missing immutable chunk text")
        if any(type(p) is not int or p < 1 or p > page_count for p in chunk.get("page_numbers", [])):
            raise ValueError("Provenance page outside the source PDF")
        # Group refs may also occur; text/table anchors are checked when matched.
    for block in source_blocks(document):
        if any(p < 0 or p >= page_count for p in block["pdf_page_indices"]):
            raise ValueError("Docling item page outside the source PDF")


def materialize(extraction: dict, document: dict, ledger: dict, pdf_hash: str) -> list[dict]:
    from ingestion.schema import ManualExtraction
    model = ManualExtraction.model_validate(extraction)
    records = []
    endpoints = {(e.kind, e.name) for e in model.entities}
    allowed = {"INDICATES": ("Symptom", "Cause"), "RESOLVED_BY": ("Cause", "Action")}
    for record_type, items in (("entity", model.entities), ("relation", model.relations)):
        for item in items:
            payload = item.model_dump(mode="json")
            evidence, issues = locate_quotes(item.source_quotes, document, ledger)
            if record_type == "relation":
                if ((item.subject_kind, item.subject_name) not in endpoints
                        or (item.object_kind, item.object_name) not in endpoints):
                    issues.append("Relation endpoint missing from extracted entities")
                kinds = (item.subject_kind, item.object_kind)
                if item.predicate in allowed and kinds != allowed[item.predicate]:
                    issues.append("Invalid domain/range for causal relation")
                if item.predicate == "APPLIES_TO" and item.object_kind != "Resin":
                    issues.append("APPLIES_TO must point to a Resin")
                if item.predicate == "IN_STEP" and item.object_kind != "ProcessStep":
                    issues.append("IN_STEP must point to a ProcessStep")
            content = {"record_type": record_type, "payload": payload,
                       "evidence": evidence, "issues": issues, "pdf_sha256": pdf_hash}
            records.append({"id": digest(content), **content})
    # Identical outputs collapse without fuzzy entity/condition merging.
    return list({r["id"]: r for r in records}.values())
