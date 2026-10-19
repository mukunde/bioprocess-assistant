"""Pinned Docling Graph adapter, local-first extraction into review staging."""
from __future__ import annotations

import importlib.metadata
import json
import os
import shutil
import uuid
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field

from ingestion.evidence import digest, materialize, validate_document
from ingestion.schema import ManualExtraction
from ingestion.store import initialize, now, write_json

DOCLING_GRAPH_VERSION = "1.9.1"
DOCLING_GRAPH_REVISION = "bbcd0e4846fadfcadac2800784783e59cd2722a9"


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, default="hf.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M")
    provider: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    allow_remote: bool = False
    chunk_max_tokens: int = Field(default=800, ge=128, le=4000)
    context_limit: int = Field(default=8192, ge=4096, le=32768)
    max_output_tokens: int = Field(default=2048, ge=256, le=8192)
    max_pdf_pages: int = Field(default=30, ge=1)
    max_pdf_mb: int = Field(default=50, ge=1)
    timeout_s: int = Field(default=180, ge=1)


def build_config(settings: Settings, source: Path, output: Path) -> dict:
    url = urlparse(settings.base_url)
    if url.scheme not in ("http", "https") or url.username or url.password or url.query:
        raise ValueError("Invalid inference base URL")
    if not settings.allow_remote:
        if settings.provider not in ("ollama", "vllm") or url.hostname not in ("127.0.0.1", "localhost", "::1"):
            raise ValueError("Remote inference requires explicit --allow-remote")
        if os.environ.get("DOCLING_SERVE_URL"):
            raise ValueError("DOCLING_SERVE_URL is not allowed in local conversion mode")
        if ":cloud" in settings.model.lower() or settings.model.lower().endswith("-cloud"):
            raise ValueError("Cloud model is not permitted in local mode")
    if settings.chunk_max_tokens + settings.max_output_tokens >= settings.context_limit:
        raise ValueError("Chunk and output budgets leave no room for extraction instructions/schema")
    return {
        "source": str(source), "template": ManualExtraction,
        "backend": "llm", "inference": "remote" if settings.allow_remote else "local",
        "provider_override": settings.provider, "model_override": settings.model,
        "processing_mode": "many-to-one", "extraction_contract": "dense",
        "provenance": "detailed", "use_chunking": True,
        "chunk_max_tokens": settings.chunk_max_tokens, "parallel_workers": 1,
        "dense_skeleton_batch_tokens": settings.chunk_max_tokens,
        "dense_fill_nodes_cap": 1, "dense_fill_context": "scoped", "dense_dedupe": "off",
        "gleaning_enabled": False, "llm_input_format": "doclang",
        "structured_output": True, "structured_sparse_check": False,
        "export_docling_json": True, "export_per_page_markdown": True,
        "dump_to_disk": True, "export_format": "csv", "output_dir": str(output),
        "llm_overrides": {
            "context_limit": settings.context_limit, "max_output_tokens": settings.max_output_tokens,
            "generation": {"temperature": 0.0, "max_tokens": settings.max_output_tokens},
            "reliability": {"timeout_s": settings.timeout_s, "max_retries": 0},
            "connection": {"base_url": settings.base_url},
        },
    }


def stage_context(run: Path, source: Path, context, settings: Settings, title: str | None = None) -> Path:
    """Adapt the public PipelineContext. Never infer page locations from model text."""
    from pypdf import PdfReader
    page_count = len(PdfReader(source).pages)
    if not 0 < page_count <= settings.max_pdf_pages:
        raise ValueError("PDF page count outside configured limit")
    if context.docling_document is None or context.provenance is None:
        raise ValueError("PDF conversion and detailed provenance are required")
    document = context.docling_document.model_dump(mode="json")
    ledger = context.provenance.model_dump(mode="json")
    validate_document(document, ledger, page_count)
    models = context.extracted_models or []
    if not models:
        raise ValueError("Docling Graph returned no extraction model")
    # Keep multiple model outputs, merging only identical records after grounding.
    extraction = {"title": title or source.stem, "entities": [], "relations": []}
    for raw in models:
        model = ManualExtraction.model_validate(raw.model_dump(mode="json"))
        extraction["entities"].extend(e.model_dump(mode="json") for e in model.entities)
        extraction["relations"].extend(r.model_dump(mode="json") for r in model.relations)
    pdf_hash = digest(source.read_bytes())
    records = materialize(extraction, document, ledger, pdf_hash)
    if not records:
        raise ValueError("No claims extracted; cannot create an empty successful review")
    write_json(run / "document.json", document)
    write_json(run / "provenance.json", ledger)
    write_json(run / "extraction.json", extraction)
    write_json(run / "settings.json", settings.model_dump())
    write_json(run / "template.schema.json", ManualExtraction.model_json_schema())
    graph = context.knowledge_graph
    write_json(run / "graph.json", {
        "nodes": [{"id": str(n), **attrs} for n, attrs in graph.nodes(data=True)],
        "edges": [{"source": str(a), "target": str(b), **attrs} for a, b, attrs in graph.edges(data=True)],
    })
    files = ["source.pdf", "document.json", "provenance.json", "extraction.json", "settings.json", "template.schema.json", "graph.json"]
    manifest = {"version": 1, "created_at": now(), "title": title or source.stem,
                "pdf_sha256": pdf_hash, "pdf_page_count": page_count,
                "docling_graph_version": DOCLING_GRAPH_VERSION, "docling_graph_revision": DOCLING_GRAPH_REVISION,
                "chunking": "Docling Graph dense + native HybridChunker; DocLang tokenizer proxy",
                "tokenizer_note": "Native DocLang chunking uses cl100k_base, not the local model tokenizer. Budget must be benchmarked.",
                "files": {name: digest((run / name).read_bytes()) for name in files}}
    initialize(run, manifest, records)
    return run


def extract_pdf(source: Path, output_root: Path, settings: Settings, title: str | None = None) -> Path:
    from pypdf import PdfReader
    source = source.resolve(strict=True)
    if source.stat().st_size > settings.max_pdf_mb * 1024 * 1024:
        raise ValueError("PDF exceeds configured size limit")
    if source.suffix.lower() != ".pdf" or source.read_bytes()[:5] != b"%PDF-":
        raise ValueError("A local PDF file is required")
    if not 0 < len(PdfReader(source).pages) <= settings.max_pdf_pages:
        raise ValueError("PDF exceeds configured page budget")
    try:
        version = importlib.metadata.version("docling-graph")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError("Install requirements-ingestion.txt in a dedicated environment first") from exc
    if version != DOCLING_GRAPH_VERSION:
        raise RuntimeError(f"Expected docling-graph {DOCLING_GRAPH_VERSION}, found {version}")
    direct_url = importlib.metadata.distribution("docling-graph").read_text("direct_url.json")
    origin = json.loads(direct_url) if direct_url else {}
    if origin.get("vcs_info", {}).get("commit_id") != DOCLING_GRAPH_REVISION:
        raise RuntimeError("Install the exact Git revision from requirements-ingestion.txt")
    from docling_graph import PipelineConfig, run_pipeline
    # Validate configuration before creating a run or invoking any model.
    config = build_config(settings, source, output_root / "native")
    PipelineConfig(**config)
    run = output_root.resolve() / f"{digest(source.read_bytes())[:12]}-{uuid.uuid4().hex[:12]}"
    run.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source, run / "source.pdf")
    config.update(source=str(run / "source.pdf"), output_dir=str(run / "native"))
    try:
        context = run_pipeline(PipelineConfig(**config))
        result = stage_context(run, run / "source.pdf", context, settings, title or source.stem)
        write_json(run / "status.json", {"status": "ready_for_review", "created_at": now()})
        return result
    except Exception:
        # Detailed exceptions may contain source text/credentials. Keep them out of
        # persistent metadata; propagate to the local caller for diagnosis.
        write_json(run / "status.json", {"status": "failed", "created_at": now()})
        raise


def revise_run(previous: Path, corrected: Path, output_root: Path) -> Path:
    """Re-ground a manual correction without a model call or inherited approvals."""
    from ingestion.store import check_integrity
    manifest = check_integrity(previous)
    extraction = ManualExtraction.model_validate_json(corrected.read_text(encoding="utf-8")).model_dump(mode="json")
    document = json.loads((previous / "document.json").read_text(encoding="utf-8"))
    ledger = json.loads((previous / "provenance.json").read_text(encoding="utf-8"))
    records = materialize(extraction, document, ledger, manifest["pdf_sha256"])
    if not records:
        raise ValueError("A revision must contain claims")
    run = output_root.resolve() / f"{manifest['pdf_sha256'][:12]}-{uuid.uuid4().hex[:12]}"
    run.mkdir(parents=True, exist_ok=False)
    for name in manifest["files"]:
        if name != "records.json":
            shutil.copyfile(previous / name, run / name)
    write_json(run / "extraction.json", extraction)
    manifest.update(created_at=now(), derived_from_manifest=digest((previous / "manifest.json").read_bytes()),
                    extraction_origin="manual_revision", native_graph_is_original_extraction=True)
    manifest["files"] = {name: digest((run / name).read_bytes()) for name in manifest["files"] if name != "records.json"}
    initialize(run, manifest, records)
    write_json(run / "status.json", {"status": "ready_for_review", "created_at": now()})
    return run
