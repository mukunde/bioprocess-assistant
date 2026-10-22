# Cytiva pages 152–153: derived row reconstruction and structural chunking

Run started: 2026-10-22; final checks: 2026-10-23.
**Technical checks pass; human review pending.**
This follow-up addresses the [original diagnostic](cytiva-table-152-153-results.md).
The [original protocol](cytiva-table-152-153-protocol.md), conversion, native
K0/K800 and source references remain historical, unchanged artifacts. This is a
development experiment, not a held-out evaluation or a production integration.

## Reconstruction of F152-01

The new [local launcher](../../experiments/cytiva/repair_table152.py) reads the
original PDF's native bounded text using inspected column boundaries and three
row bands. It never populates values from an expected-answer list. It verifies
each captured glyph's character index, text and coordinates against the original
PDF, then checks bounded text against those independent character records.
Only whitespace is normalized. A boundary cutting a glyph or inconsistent
evidence fails the reconstruction.

Both the original PDF and original T1 JSON are SHA-256 pinned. Thirty cells
covering the final three variant lines are reconstructed, with 108 verified
glyphs and **13 source blanks retained**. The provenance ledger records source
PDF/excerpt page, cell rectangle, original bounded text and individual glyphs.
Rectangles are inspected extraction regions, not tight word boxes. Reconstructed
cells retain their grid positions in a new Docling-schema-valid JSON.

| Raw source product cell | Volume | Approx. binding capacity | Data-file code |
|---|---|---|---|
| HiTrap MabSelect | 1 mL | 30 mg/column | 11003490 |
| *(blank)* | 5 mL | 150 mg/column | 11003490 |
| HiScreen MabSelect | 4.7 mL | 140 mg/column | 28930581 |

Both HiTrap variant bands and the HiScreen band independently contain marks in
the Prepacked columns/ÄKTA-compatible and Process-development columns. Their
other four application cells are blank. **The code 11003490 is actually printed
on both HiTrap lines**; retaining it twice is not forward filling. The second
HiTrap product cell remains blank. A separate, pending candidate grouping of
derived rows 19–20 keeps the two variants together without manufacturing a
second printed product name or a source rowspan.

Only original table-0 rows 19–20 are replaced by derived rows 19–21. Earlier
rows, the entire second table, all other document fields and native parent
provenance stay unchanged. Table 0 now has 22 rows including its header;
table 1 retains 23. The three other aggregated variant rows (1, 9 and 13) remain
quarantined for per-variant use. This targeted repair does not reconstruct all
physical page-152 variant lines.

## Structural serializer and chunker

The new [experimental module](../../ingestion/table_chunking.py) serializes
complete rows and their original cell spans. Native rowspans and explicit
candidate groups are indivisible, including overlapping/transitive spans.
Every table chunk repeats a full header, caption context and applicable
**table-level note context**. Empty cells remain empty; covered span positions
use an explicit span element instead of repeated product text. Escaping retains
literal text. The entire final XML is token-counted with cached `cl100k_base`.
An oversized row/group is rejected for quarantine, never truncated into a
syntactically or semantically partial cell.

The format is **`structural-table-xml-v1`, not DocLang/OTSL**. K0 is an unbudgeted
full-block control in that format; K800 uses exactly the same derived document
and context. It is an opt-in companion experiment: neither the existing native
runner nor the production ingestion/retrieval path is switched automatically.
The serializer supports the inspected tables/text document, rejects pictures
and unsupported group/header structures, and requires a hash-bound diagnostic
context and artifact manifest. It is not a general PDF layout serializer.

K0 retains an explicit boundary between the two tables. K800 keeps table refs
and excerpt/original-page metadata rather than putting a detached page-break
token in a fragment. One separate text-inventory fragment preserves all eight
native text items with their original refs and labels, including note 3's
original status as body text. This inventory is not a proposed retrieval unit.
Its source order is retained within that inventory; K0's inventory-then-tables
layout is not a claim to reproduce the original full document reading order.

## Result and comparison limits

| Metric | Original native T1/DocLang | Derived structural XML |
|---|---:|---:|
| K0 tokens | 3921 | 3579 |
| K800 fragments | 5 | 7: six table blocks and one text inventory |
| K800 token counts | 100, 765, 481, 773, 371 | 212, 782, 794, 547, 659, 661, 720 |
| K800 total tokens | 2490 | 4375 |
| Maximum tokens | 773 | 794 |
| Complete table containers in table fragments | 0 | 6/6 |
| Quantity/unit, header and N/A/marker cuts | Four observed boundary defects | None in the derived rows |
| Source product association defect F152-01 | Present | Source-derived correction awaiting human review |

An independent parser checks all **430 data-grid positions / 43 rows** against
the derived Docling grid, once and in order. It checks span anchors inside the
same chunk, every repeated header/caption/note, final budgets, both page mappings,
the complete K0 tables and all eight native text items. It also verifies that
the repair changed only its intended rows and that **413 pre-existing experiment
files remain byte-identical**. The derived document passes Docling schema
validation.

K0/K800 serialization/chunking took **0.473 seconds including imports** in the
final local run; process-launch/supervisor overhead and independent audits are
excluded. The previous native worker reported 210.338 seconds including heavy
imports and 4.826 seconds for its raw/native passes. These are different
implementations and a single machine/cache sequence, not a controlled speedup
benchmark. No PDF conversion or model weights are loaded by the new chunker.

Repeating complete context increases K800 tokens. Changing both the document and
serialization prevents attributing the token difference to chunking alone.
Lower K0 tokens are not evidence of better compression or retrieval. A later
matched-input retrieval evaluation is still needed before choosing a serving
strategy.

Validation: **182 tests pass**, including 14 new regression tests for structural
boundaries, rowspans, blanks, evidence consistency, oversized-unit rejection,
hash-bound inputs and output collision protection. The separate six r2 package
tests and all three page-77/88/104 package verifiers also pass. The full suite
uses local/mocked services; no inference API is contacted. Its localhost review
server tests require an execution context that permits loopback HTTP. A first
sandbox run was interrupted after stalling there; the complete rerun outside
that restriction passed. The r2 tests initially hit the sandbox's unwritable
default temporary directory, then passed with a workspace-local TEMP/TMP.

## Pending human decisions and quarantine

- Confirm the source-derived HiTrap/HiScreen separation, marks, blanks and codes,
  and the proposed two-line HiTrap grouping.
- Confirm the documentary continuation of table A1.7 onto page 153. No caption
  is printed there: repeated caption context is explicitly a candidate annotation.
- Confirm note scope. Native notes 1/2 are table-0 context; note 3 is explicitly
  added as pending table-1 context. This adds no marker-to-cell applicability
  relation, inferred capacity, zero value, or inherited page-152 note scope.
- Retain quarantine on the three other aggregated variant rows. Chunk metadata
  carries those row IDs and pending annotations; conservation of text does not
  validate its per-variant interpretation.

All human approvals remain false. No graph import, scientific validation or
production retrieval validation follows from this diagnostic.

## Reproduce locally

From the repository root, choose **new output names** each time. Existing output
directories are rejected before any input processing. The original source PDF
must already be present locally; the native character capture comes from the
original preparation run.

```powershell
$tablePython = '.\.venv-ingestion\Scripts\python.exe'
$tableBase = 'data/experiments/cytiva/visual-validation-v01'
$tablePdf = Join-Path $env:USERPROFILE 'Projects/bioprocess-assistant/references/cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf'
$tableRepair = "$tableBase/repaired-152-153-new-run"
$tableChunks = "$tableBase/chunks-row-safe-152-153-new-run"
& $tablePython -m experiments.cytiva.repair_table152 repair --pdf $tablePdf --document "$tableBase/convert-152-153-20261022-a/p152-153/T1/document.json" --characters "$tableBase/pages-152-153-preparation-20261022-a/source-152-characters.json" --output $tableRepair
if ($LASTEXITCODE -ne 0) { throw 'Stop: reconstruction failed.' }
& $tablePython -m experiments.cytiva.repair_table152 chunk --run $tableRepair --output $tableChunks --budgets 800
if ($LASTEXITCODE -ne 0) { throw 'Stop: structural chunking failed.' }
& $tablePython -m unittest tests.test_table_chunking -v
```

The launcher imports no extraction LLM/VLM, invokes no paid service and installs
the existing Python network audit guard. A missing tokenizer cache cannot be
downloaded under that guard. It is not an OS firewall. All recorded network
attempts, LLM calls and API calls are zero.

Final local artifacts under the ignored experiment base:

- `repaired-152-153-20261022-c/`: new document, cell provenance, candidate context
  and source/output/implementation manifest.
- `chunks-row-safe-152-153-20261022-d/`: K0.xml, seven K800 XML fragments with
  metadata, metrics and manifest binding the repair/context/implementation.
- `pages152153-repair-audit-20261022-d/`: independent audit script/checks,
  source crop, reconstructed HTML and final verification record.

Earlier `-b`/`-c` trial outputs are retained locally as provisional iterations;
the directories above identify the final checked pair. No original artifact
was overwritten. The [regression tests](../../tests/test_table_chunking.py) use
synthetic fixtures rather than redistributing the manual.
