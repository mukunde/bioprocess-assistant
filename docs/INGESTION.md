# Docling Graph ingestion and manual evidence review

This first implementation runs outside Chainlit. It extracts into local staging;
it never inserts new knowledge into the assistant automatically. No hosted model
is called by default. The optional Neo4j publication command creates a separate,
reviewed evidence graph, not the assistant's existing Symptom/Cause/Action graph.

## Runtime installation (Windows PowerShell)

From the repository root, create a dedicated environment:

```powershell
py -3.13 -m venv .venv-ingestion
.\.venv-ingestion\Scripts\python.exe -m pip install -r requirements-ingestion.txt
```

Python 3.11/3.12 can also be used if installed. The dependency file pins Docling
Graph to upstream revision `bbcd0e4846fadfcadac2800784783e59cd2722a9` (1.9.1),
which was inspected for dense extraction, HybridChunker and detailed provenance.
Transitive dependencies are bounded by upstream; this is not a fully locked or
validated industrial environment. The optional runtime may download sizeable
conversion models. It is not added to the chatbot Docker image.

Install/start Ollama separately and download the model before processing PDFs:

```powershell
ollama pull hf.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF:Q4_K_M
```

Configure the serving model context to match the context budget in the settings.
`context_limit` informs extraction planning; it does not reconfigure an already
running inference server. The first local trial on pages 97–99 took approximately
56 minutes and produced no semantic relations; see the
[diagnostic](experiments/cytiva-local-extraction-diagnostic.md). This is a measured
failure case, not a validated default. Start with a bounded micro-test.

The example uses 800-token structural chunks, dense scoped extraction, one worker,
one node per fill request, no gleaning and no automatic retry. These are initial
settings, not a tuned optimum. Native DocLang chunking in the pinned release uses
`cl100k_base` as a tokenizer proxy; it is not the Ministral tokenizer. All prompt,
schema and output overhead must still fit the actual serving context.

## Extract a local manual

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion extract references/manual.pdf --settings ingestion/local.example.json --output data/ingestion --title "Cytiva manual - document reference and revision"
```

The command prints a new run directory, for example `data/ingestion/<run-id>`.
Use that exact path in subsequent commands. Defaults reject non-loopback inference
endpoints and remote Docling conversion. Remote inference requires an explicit
`allow_remote: true` setting. That setting belongs in the JSON file, not a CLI
flag. A local endpoint alone does not prove full network isolation: prepare model
caches and check runtime/server behavior before using confidential documents.

The default maximum is 30 PDF pages and 50 MiB; increase deliberately in settings
for a longer handbook. These are input limits, not an overall LLM-call budget.
Per-call time/output/retry limits are configured; a workflow-wide call/token budget
and OpenTelemetry cost instrumentation remain future work.

Every run contains:

- `source.pdf`: archived source bytes, identified by SHA-256;
- `document.json`: complete Docling conversion, including item/page geometry;
- `provenance.json`: full native ledger, chunks, headings, anchors and spans;
- `graph.json`: native extracted graph, including node provenance;
- `extraction.json`: canonical Pydantic entities and relations;
- `records.json`: atomic review records with independently located quotes;
- `settings.json`, `template.schema.json`, `manifest.json`: configuration and hashes;
- `review.sqlite3`: append-only application review decisions;
- `native/`: upstream exports for diagnosis, never executed as Cypher;
- `status.json`: ready/failed state. Failed runs preserve diagnostic artifacts.

The default data directory is gitignored and excluded from the app image. Keep
custom output paths private too. Do not redistribute source manuals without the
appropriate rights. The application does not upload the PDF for review.

## Chunking and provenance contract

Use the native document-based HybridChunker with hierarchy/headers retained in
provenance. It starts with structural items, then applies a token budget. Table
rows/cells, headings and notes must be inspected on representative PDF pages.
A large row can still be re-split by upstream code; the review highlights
`resplit_of` fragments rather than claiming all rows are preserved perfectly.
Footnote and cross-page applicability is not automatically proven by proximity.

The template extracts Symptom, Cause, Action, Resin and ProcessStep entities,
and INDICATES, RESOLVED_BY, APPLIES_TO and IN_STEP relations. Each entity statement
and each relation must carry its own verbatim `source_quotes`. The model is not
trusted to invent page numbers or filesystem paths. Code locates quotes in Docling
text items or individual table cells/rows, permits whitespace differences, and
retains matches in every supporting item, including repeated occurrences within
one item. Shorter contexts are displayed first, but longer passages and their
restrictions/page anchors are not discarded. Multiple matches are explicitly
marked ambiguous; inspect their applicability before approving. The same table
passage may appear in both cell and row context, so multiple matches do not imply
independent corroboration. Cross-row text is never joined to invent
support. Metadata includes item refs, candidate PDF page indices (zero-based),
character offsets, actual source quote, text hash, chunk IDs, heading trail, table
headers/cell information and original geometry with its coordinate convention.
Native ledger data and full conversion remain available, not just capped node
annotations. Printed page labels and semantic unit conversion are not yet added.

**Located in the conversion is not verified in the PDF.** OCR can misread text;
merely finding words does not prove a relation. Multi-page table anchors may list
several candidate pages. Review the original page image, row, header, units,
negations, restrictions and notes. Exact quote matching does not validate scientific
truth. A semantic LLM judge is not part of this implementation and cannot replace
the manual approval gate.

## Review locally

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion review data/ingestion/<run-id>
```

Open `http://127.0.0.1:8765`. The server binds only to loopback. It shows the
extracted record, highlighted quote in converted text and original PDF page images
rendered locally with PDFium. All PDFium work, including resource cleanup, is
serialized across review servers in the same process. Geometry is retained but
not yet drawn as an overlay.
No browser PDF plugin or external CDN is needed. Select a record, inspect its
source pages, enter a reviewer identifier and an explanatory note, explicitly
confirm PDF verification, then approve or reject. Approve endpoint entities before
their relation. Missing quotes/page anchors and invalid relation types block approval.

CLI equivalent:

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion decide data/ingestion/<run-id> <record-id> approve --reviewer "Gael" --note "Verified statement, relation and applicability in source PDF" --source-checked
```

The reviewer identity is a local declaration, not authenticated identity. The
SQLite history is append-only through this application, not tamper-proof storage
against a privileged local user. This is not a compliance audit platform.

Changing any registered artifact invalidates the run. Do not edit extraction files
inside an existing run. To correct a claim, copy `extraction.json` outside that
run, edit the copy, and re-stage without any LLM call:

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion revise data/ingestion/<run-id> --extraction tmp/corrected-extraction.json --output data/ingestion
```

A new run rechecks quotes and starts all decisions as pending. The previous run
and its decisions remain intact. Its native `graph.json`/ledger are retained as
original extraction artifacts; the revised canonical records are the review and
publication source of truth.

Existing runs keep their frozen evidence and decisions after a code update. To
apply improved quote localization to an older run, use `revise` with a copy of its
extraction; the new evidence starts pending and does not inherit approvals.

## Export and optional Neo4j publication

Export only currently approved records, with their evidence and decisions:

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion export data/ingestion/<run-id> --output tmp/approved-snapshot.json
```

Unknown/changed artifacts, missing manual verification, empty approval sets and
relations with unapproved endpoints are rejected. Pending/rejected claims are not
exported. The snapshot ID is deterministic for the same artifacts and decisions.

When you deliberately want to publish this approved snapshot, configure the
existing Neo4j environment variables, then run:

```powershell
.\.venv-ingestion\Scripts\python.exe -m ingestion publish data/ingestion/<run-id>
```

Publication uses parameterized queries and one data transaction, plus idempotent
uniqueness constraints. It writes IngestionSnapshot, ManualEntity and ReviewedClaim
nodes. Relations are reified as reviewed claims linked by SUBJECT/OBJECT, retaining
their predicate, conditions and evidence. Re-publishing the same snapshot does not
duplicate data. Later review decisions produce a different historical snapshot;
revocation does not automatically delete an earlier published snapshot. No data
is published during extraction/review, and the chatbot serving graph is not changed.
A context-aware serving/promotion adapter remains a separate next step.

In Neo4j Browser, inspect a bounded portion with:

```cypher
MATCH p=(s:IngestionSnapshot)-[:CONTAINS]->(c:ReviewedClaim)
OPTIONAL MATCH q=(c)-[:SUBJECT|OBJECT|DESCRIBES]->(:ManualEntity)
RETURN p, q LIMIT 100;
```

## Verification and remaining work

```powershell
python -m pip install -r requirements.txt -r eval/requirements.txt
python -m unittest discover -s tests -v
```

Tests exercise synthetic conversion fixtures, PDF hash/quote checks, table row
association, review decisions/revocation, revisions, local HTTP boundaries and
parameterized transaction construction. They do not validate Cytiva content,
actual OCR/chunk boundaries, model extraction quality or real Neo4j concurrency.
The pinned upstream PipelineConfig was also instantiated against the inspected
source. Full Docling conversion/inference requires the optional runtime,
a downloaded/running model and an actual manual. The first real local extraction
was executed separately; the later [conversion/chunking trial](experiments/cytiva-conversion-chunking-results-077-088.md)
used no LLM and found a blocking table-association defect on page 88.

Next: resolve or quarantine conversion defects, confirm the manual reference and
instrument bounded extraction comparisons. Measure errors, latency, memory and
review time before expanding. Ragas, red-teaming and OpenTelemetry integration
remain roadmap work.
