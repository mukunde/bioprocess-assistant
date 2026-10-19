"""No Docling/model downloads or paid calls: use synthetic conversion fixtures."""
import copy
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import tempfile
import threading
import sys
import unittest
from http.client import HTTPConnection
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
from pypdf import PdfWriter

from ingestion.evidence import locate_quotes, materialize, validate_document
from ingestion.pipeline import Settings, build_config, stage_context, revise_run
from ingestion.publish import export_snapshot, publish_snapshot
from ingestion.review import make_server
from ingestion.schema import ManualExtraction
from ingestion.store import approved_records, connect, decide, list_records


def fixture():
    document = {"texts": [
        {"self_ref": "#/texts/0", "label": "text", "text": "High pressure may indicate fouling.",
         "prov": [{"page_no": 1, "bbox": {"l": 10, "t": 20, "r": 200, "b": 30, "coord_origin": "TOPLEFT"}}]},
        {"self_ref": "#/texts/1", "label": "text", "text": "Fouling can be addressed by cleaning.",
         "prov": [{"page_no": 1}]}], "tables": []}
    ledger = {"document": {"document_id": "fixture"}, "nodes": {}, "chunks": {
        "0": {"text": "High pressure may indicate fouling.", "page_numbers": [1],
              "doc_item_refs": ["#/texts/0"], "headings": ["Troubleshooting"], "resplit_of": None},
        "1": {"text": "Fouling can be addressed by cleaning.", "page_numbers": [1],
              "doc_item_refs": ["#/texts/1"], "headings": ["Cleaning"], "resplit_of": None}}}
    extraction = {"title": "Synthetic fixture", "entities": [
        {"kind": "Symptom", "name": "High pressure", "description": "High pressure", "source_quotes": ["High pressure may indicate fouling."]},
        {"kind": "Cause", "name": "Fouling", "description": "Fouling", "source_quotes": ["High pressure may indicate fouling."]},
        {"kind": "Action", "name": "Cleaning", "description": "Cleaning", "source_quotes": ["Fouling can be addressed by cleaning."]}],
        "relations": [{"subject_kind": "Symptom", "subject_name": "High pressure", "predicate": "INDICATES", "object_kind": "Cause", "object_name": "Fouling", "source_quotes": ["High pressure may indicate fouling."]}]}
    return document, ledger, extraction


class EvidenceTests(unittest.TestCase):
    def test_locations_use_docling_pages_and_offsets_not_llm_page_numbers(self):
        document, ledger, _ = fixture()
        evidence, issues = locate_quotes(["High pressure may indicate fouling."], document, ledger)
        self.assertFalse(issues)
        match = evidence[0]["matches"][0]
        self.assertEqual(match["pdf_page_indices"], [0])
        self.assertEqual(match["chunk_ids"], ["0"])
        self.assertEqual(match["text"][match["start"]:match["end"]], match["source_quote"])
        self.assertEqual(evidence[0]["location_status"], "located_in_conversion")

    def test_whitespace_matching_does_not_change_numbers(self):
        doc, ledger, _ = fixture()
        doc["texts"][0]["text"] = "Use 0.1\n M NaOH."
        evidence, issues = locate_quotes(["Use 0.1 M NaOH."], doc, ledger)
        self.assertTrue(evidence)
        self.assertFalse(issues)
        _, issues = locate_quotes(["Use 1 M NaOH."], doc, ledger)
        self.assertTrue(issues)

    def test_missing_quotes_and_page_anchors_are_blocked(self):
        doc, ledger, _ = fixture()
        self.assertTrue(locate_quotes([], doc, ledger)[1])
        self.assertTrue(locate_quotes(["invented"], doc, ledger)[1])
        doc["texts"][0]["prov"] = []
        self.assertTrue(locate_quotes(["High pressure"], doc, ledger)[1])

    def test_ambiguous_occurrences_are_not_silently_reduced_to_one(self):
        doc, ledger, _ = fixture()
        other = copy.deepcopy(doc["texts"][0])
        other["self_ref"] = "#/texts/2"
        doc["texts"].append(other)
        evidence, _ = locate_quotes(["High pressure"], doc, ledger)
        self.assertTrue(evidence[0]["ambiguous"])
        self.assertEqual(len(evidence[0]["matches"]), 2)

    def test_different_length_contexts_keep_all_pages_and_restrictions(self):
        doc, ledger, _ = fixture()
        doc["texts"][0]["text"] = "Clean with NaOH."
        other = copy.deepcopy(doc["texts"][0])
        other.update(self_ref="#/texts/2", text="For resin B only: Clean with NaOH.", prov=[{"page_no": 2}])
        doc["texts"].append(other)
        evidence, issues = locate_quotes(["Clean with NaOH."], doc, ledger)
        self.assertFalse(issues)
        self.assertTrue(evidence[0]["ambiguous"])
        matches = evidence[0]["matches"]
        self.assertEqual([m["pdf_page_indices"] for m in matches], [[0], [1]])
        self.assertIn("For resin B only", matches[1]["text"])

    def test_repeated_quote_in_one_item_keeps_each_offset(self):
        doc, ledger, _ = fixture()
        doc["texts"][0]["text"] = "Clean with NaOH. For resin B only: Clean with NaOH."
        evidence, issues = locate_quotes(["Clean with NaOH."], doc, ledger)
        self.assertFalse(issues)
        self.assertTrue(evidence[0]["ambiguous"])
        matches = evidence[0]["matches"]
        self.assertEqual([m["start"] for m in matches], [0, 35])
        for match in matches:
            self.assertEqual(match["text"][match["start"]:match["end"]], "Clean with NaOH.")

    def test_longer_unanchored_match_cannot_be_hidden_by_shorter_match(self):
        doc, ledger, _ = fixture()
        doc["texts"][0]["text"] = "Clean with NaOH."
        doc["texts"].append({"self_ref": "#/texts/2", "text": "For resin B only: Clean with NaOH.", "prov": []})
        evidence, issues = locate_quotes(["Clean with NaOH."], doc, ledger)
        self.assertEqual(len(evidence[0]["matches"]), 2)
        self.assertTrue(any("no PDF page anchor" in issue for issue in issues))

    def test_table_rows_preserve_headers_and_do_not_join_different_rows(self):
        doc, ledger, _ = fixture()
        doc["tables"] = [{"self_ref": "#/tables/0", "prov": [{"page_no": 1}], "data": {"table_cells": [
            {"text": "Problem", "start_row_offset_idx": 0, "start_col_offset_idx": 0, "column_header": True},
            {"text": "Action", "start_row_offset_idx": 0, "start_col_offset_idx": 1, "column_header": True},
            {"text": "Fouling", "start_row_offset_idx": 1, "start_col_offset_idx": 0},
            {"text": "Clean", "start_row_offset_idx": 1, "start_col_offset_idx": 1},
            {"text": "Breakthrough", "start_row_offset_idx": 2, "start_col_offset_idx": 0},
            {"text": "Reduce load", "start_row_offset_idx": 2, "start_col_offset_idx": 1}]}}]
        evidence, issues = locate_quotes(["Fouling | Clean"], doc, ledger)
        self.assertFalse(issues)
        self.assertEqual(evidence[0]["matches"][0]["table_row"], 1)
        self.assertEqual(len(evidence[0]["matches"][0]["table_headers"]), 2)
        self.assertTrue(locate_quotes(["Fouling | Reduce load"], doc, ledger)[1])

    def test_out_of_range_page_is_rejected(self):
        doc, ledger, _ = fixture()
        ledger["chunks"]["0"]["page_numbers"] = [4]
        with self.assertRaises(ValueError):
            validate_document(doc, ledger, 1)

    def test_relations_have_their_own_evidence_and_type_checks(self):
        doc, ledger, extraction = fixture()
        extraction["relations"][0]["source_quotes"] = []
        records = materialize(extraction, doc, ledger, "pdfhash")
        self.assertTrue(records[-1]["issues"])
        extraction["relations"][0]["subject_kind"] = "Action"
        records = materialize(extraction, doc, ledger, "pdfhash")
        self.assertIn("Invalid domain/range for causal relation", records[-1]["issues"])

    def test_identical_claims_deduplicate_without_fuzzy_merging(self):
        doc, ledger, extraction = fixture()
        extraction["entities"].append(copy.deepcopy(extraction["entities"][0]))
        self.assertEqual(len(materialize(extraction, doc, ledger, "pdfhash")), 4)


class PipelineConfigTests(unittest.TestCase):
    def test_dense_detailed_sequential_configuration(self):
        conf = build_config(Settings(), Path("source.pdf"), Path("outputs"))
        self.assertEqual(conf["provenance"], "detailed")
        self.assertEqual(conf["extraction_contract"], "dense")
        self.assertEqual(conf["parallel_workers"], 1)
        self.assertTrue(conf["use_chunking"])
        self.assertEqual(conf["llm_overrides"]["reliability"]["max_retries"], 0)

    def test_remote_requires_explicit_setting(self):
        with self.assertRaises(ValueError):
            build_config(Settings(base_url="https://remote.example"), Path("a"), Path("b"))
        conf = build_config(Settings(base_url="https://remote.example", allow_remote=True, provider="mistral"), Path("a"), Path("b"))
        self.assertEqual(conf["inference"], "remote")

    def test_remote_conversion_and_cloud_models_do_not_leak_into_local_mode(self):
        with patch.dict("os.environ", {"DOCLING_SERVE_URL": "https://example.test"}):
            with self.assertRaises(ValueError):
                build_config(Settings(), Path("a"), Path("b"))
        with self.assertRaises(ValueError):
            build_config(Settings(model="model:cloud"), Path("a"), Path("b"))

    def test_unknown_configuration_fields_and_bad_budgets_fail(self):
        with self.assertRaises(ValidationError):
            Settings(unknown_field=True)
        with self.assertRaises(ValueError):
            build_config(Settings(context_limit=4096, chunk_max_tokens=3000, max_output_tokens=2048), Path("a"), Path("b"))


class ReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        temp_root = Path(__file__).resolve().parent.parent / "tmp" / "tests"
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_root)
        self.run = Path(self.temp.name)
        # Blank one-page PDF is only an integrity fixture, not a claimed source
        # of the synthetic text. Real source fidelity requires manual PDF review.
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(self.run / "source.pdf")
        doc, ledger, extraction = fixture()
        graph = MagicMock()
        graph.nodes.return_value = [("node", {"__provenance__": {"match": "verbatim", "pages": [1]}})]
        graph.edges.return_value = []
        context = SimpleNamespace(
            docling_document=SimpleNamespace(model_dump=lambda **kw: doc),
            provenance=SimpleNamespace(model_dump=lambda **kw: ledger),
            extracted_models=[ManualExtraction.model_validate(extraction)], knowledge_graph=graph)
        stage_context(self.run, self.run / "source.pdf", context, Settings())

    def tearDown(self):
        self.temp.cleanup()

    def records(self):
        return list_records(self.run)

    def approve(self, record):
        decide(self.run, record["id"], "approve", "reviewer", "Checked source and conditions", True)

    def test_all_records_start_pending_and_export_is_blocked(self):
        self.assertTrue(all(r["decision"]["action"] == "pending" for r in self.records()))
        with self.assertRaises(ValueError):
            export_snapshot(self.run)

    def test_manual_confirmation_and_note_are_required(self):
        record = self.records()[0]
        for reviewer, note, checked in (("", "note", True), ("reviewer", "", True), ("reviewer", "note", False)):
            with self.assertRaises(ValueError):
                decide(self.run, record["id"], "approve", reviewer, note, checked)

    def test_relation_requires_approved_endpoints(self):
        with self.assertRaises(ValueError):
            self.approve(self.records()[-1])

    def test_approved_snapshot_is_stable_and_preserves_evidence(self):
        for record in self.records():
            self.approve(record)
        a = export_snapshot(self.run)
        self.assertEqual(a, export_snapshot(self.run))
        self.assertEqual(len(a["records"]), 4)
        self.assertTrue(all(r["evidence"] for r in a["records"]))

    def test_changed_pdf_invalidates_review(self):
        self.approve(self.records()[0])
        with (self.run / "source.pdf").open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaises(ValueError):
            export_snapshot(self.run)

    def test_changed_conversion_invalidates_review(self):
        (self.run / "document.json").write_text("{}")
        with self.assertRaises(ValueError):
            self.records()

    def test_manual_revision_rechecks_evidence_and_inherits_no_approvals(self):
        self.approve(self.records()[0])
        extraction = json.loads((self.run / "extraction.json").read_text(encoding="utf-8"))
        extraction["entities"][0]["source_quotes"] = ["Unsupported quotation"]
        corrected = self.run / "corrected.json"
        corrected.write_text(json.dumps(extraction), encoding="utf-8")
        revised = revise_run(self.run, corrected, self.run / "revisions")
        records = list_records(revised)
        self.assertTrue(all(r["decision"]["action"] == "pending" for r in records))
        self.assertTrue(records[0]["issues"])
        with self.assertRaises(ValueError):
            decide(revised, records[0]["id"], "approve", "reviewer", "Check", True)
        self.assertEqual(self.records()[0]["decision"]["action"], "approve")

    def test_mutated_database_record_is_detected(self):
        with connect(self.run) as db:
            db.execute("UPDATE records SET content='{}'")
        with self.assertRaises(ValueError):
            self.records()

    def test_decisions_are_append_only_and_revocation_blocks_relation_export(self):
        for record in self.records():
            self.approve(record)
        decide(self.run, self.records()[0]["id"], "reject", "reviewer", "Needs correction")
        with connect(self.run) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM decisions").fetchone()[0], 5)
        with self.assertRaises(ValueError):
            approved_records(self.run)

    def test_publication_is_one_transaction_and_never_modifies_chatbot_labels(self):
        for record in self.records():
            self.approve(record)
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        tx = MagicMock()
        session.execute_write.side_effect = lambda callback: callback(tx)
        publish_snapshot(driver, "neo4j", export_snapshot(self.run))
        session.execute_write.assert_called_once()
        queries = " ".join(c.args[0] for c in tx.run.call_args_list)
        self.assertNotIn(":Symptom", queries)
        self.assertNotIn("DELETE", queries)
        self.assertNotIn("High pressure", queries)

    def test_loopback_ui_escapes_data_and_rejects_missing_token(self):
        server = make_server(self.run, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/")
            response = connection.getresponse()
            page = response.read().decode()
            self.assertEqual(response.status, 200)
            self.assertIn("textContent", page)
            self.assertIn("frame-ancestors 'none'", response.getheader("Content-Security-Policy"))
            connection.request("POST", "/api/decision", body="{}", headers={"Content-Type": "application/json"})
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 403)
            connection.request("GET", "/../../source.pdf")
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 404)
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)

    @unittest.skipUnless(importlib.util.find_spec("pypdfium2"), "PDFium preview dependency not installed")
    def test_original_pdf_page_is_rendered_as_png_and_bounds_checked(self):
        server = make_server(self.run, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", "/pages/0.png")
            response = connection.getresponse()
            data = response.read()
            self.assertEqual(response.status, 200)
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            connection.request("GET", "/pages/99.png")
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 409)
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)

    def test_parallel_previews_across_servers_serialize_pdfium(self):
        counter_lock = threading.Lock()
        overlap = threading.Event()
        active = peak = entries = 0
        png = b"\x89PNG\r\n\x1a\n"

        def document(*args, **kwargs):
            doc = MagicMock()
            doc.__len__.return_value = 1
            image = doc.__getitem__.return_value.render.return_value.to_pil.return_value
            image.save.side_effect = lambda stream, **kwargs: stream.write(png)
            def enter():
                nonlocal active, peak, entries
                with counter_lock:
                    active += 1
                    entries += 1
                    entry = entries
                    peak = max(peak, active)
                    if active > 1:
                        overlap.set()
                if entry == 1:
                    overlap.wait(0.5)
                return doc
            def exit(*args):
                nonlocal active
                with counter_lock:
                    active -= 1
            doc.__enter__.side_effect = enter
            doc.__exit__.side_effect = exit
            return doc

        # Distinct servers must share PDFium exclusion, not just a per-run lock.
        servers = [make_server(self.run, 0) for _ in range(2)]
        threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in servers]
        for thread in threads:
            thread.start()
        start = threading.Barrier(3)
        def request(port):
            start.wait(5)
            connection = HTTPConnection("127.0.0.1", port, timeout=5)
            try:
                connection.request("GET", "/pages/0.png")
                response = connection.getresponse()
                return response.status, response.read()
            finally:
                connection.close()
        try:
            # Never issue concurrent calls to native PDFium in this regression.
            with patch.dict(sys.modules, {"pypdfium2": SimpleNamespace(PdfDocument=document)}):
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(request, s.server_port) for s in servers]
                    start.wait(5)
                    results = [future.result(10) for future in futures]
            self.assertEqual(results, [(200, png), (200, png)])
            self.assertEqual(entries, 2)
            self.assertEqual(peak, 1)
            self.assertFalse(overlap.is_set())
            self.assertEqual(active, 0)
        finally:
            for server, thread in zip(servers, threads):
                server.shutdown()
                server.server_close()
                thread.join(5)

    def test_render_error_closes_page_and_allows_next_request(self):
        server = make_server(self.run, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        doc = MagicMock()
        doc.__enter__.return_value = doc
        doc.__len__.return_value = 1
        page = doc.__getitem__.return_value
        bitmap = MagicMock()
        bitmap.to_pil.return_value.save.side_effect = lambda stream, **kwargs: stream.write(b"PNG")
        page.render.side_effect = [ValueError("simulated render failure"), bitmap]
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            with patch.dict(sys.modules, {"pypdfium2": SimpleNamespace(PdfDocument=lambda *args: doc)}):
                for expected in (409, 200):
                    connection.request("GET", "/pages/0.png")
                    response = connection.getresponse()
                    response.read()
                    self.assertEqual(response.status, expected)
            self.assertEqual(page.close.call_count, 2)
            self.assertEqual(doc.__exit__.call_count, 2)
            self.assertEqual(bitmap.close.call_count, 1)
            self.assertEqual(bitmap.to_pil.return_value.close.call_count, 1)
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join(5)


if __name__ == "__main__":
    unittest.main()
