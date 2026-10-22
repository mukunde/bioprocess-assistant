# Cytiva pages 152-153: conversion and chunking results

Date: 2026-10-22. Status: **technical diagnostic complete; conversion association defect and native chunk structure quarantined; human review pending**.
This development trial uses the prepared candidate source reference. It is not a
held-out benchmark or scientific validation. No extraction LLM/VLM, API call,
paid service, automatic repair or Neo4j import ran.

## Finding

T1 restores both ordered ten-column headers and all 32 product-group labels, but
**F152-01 misassociates a HiTrap MabSelect variant with HiScreen MabSelect at the
bottom of page 152**. K0 faithfully serializes the flawed native tables. K800
introduces additional context/structure loss: table headers, one quantity/unit
pair and an N/A note marker cross chunk boundaries. A token cap is respected,
but the fragments are not self-contained table inputs.

See the [protocol](cytiva-table-152-153-protocol.md),
[source reference](../../experiments/cytiva/pages152153_table_spec.json) and
[16 technical outcomes](cytiva-table-152-153-results.csv).
The original [preparation sheet](cytiva-table-152-153-review.csv) remains frozen
with historical `not_run` values. Every human decision remains pending.

## Frozen inputs and provenance

Source PDF SHA-256:
`a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
Excerpt SHA-256:
`a2f68502193f903b45e8d189befdf63709506557dba7d459d3646c7ddf9bc550`.
Excerpt 1 -> original/printed 152; excerpt 2 -> original/printed 153.

- T0 document SHA-256: `3b29fadf089097412faa31dbde5dd9e8f1342f334801f0eaa9790f8736f6c74a`.
- T1 document SHA-256: `9ae4ee2f1be39731d27a0b3aad854cc4ad068c27555e8c05aa51e9de70948681`.

Both conversions used CPU/four threads, OCR off, page/picture images at scale 2,
remote services and picture/chart enrichments off. T1 enabled TableFormer V1
accurate/cell matching; T0 disabled table structure. The original full pages,
source-native characters and actual exported HTML captures were inspected.
Four headless Chrome captures (T0/T1 x two tables) had no cell overflow and no
page-level external requests. Neither overflow checks nor image similarity
validate the underlying product associations.

## Conversion, continuity and notes

| Check | T0 | T1 |
|---|---|---|
| Native tables | Two 1x1 empty grids; text survives in child groups | Two tables: 21x10 and 23x10 grids |
| Ordered headers | No usable typed grid | 20/20 targeted header occurrences match after whitespace-only comparison |
| Group labels/order | Text retained, no reliable grid association | All 20+12 source group labels found in order |
| Variant lines | Not represented as usable table rows | 20+22 native data rows versus 24+22 physical source variant lines |
| Caption/continuation | Caption binds first table | Same; second table has no caption/reference/continuation link |
| Note bodies | All three present | All three exact bodies preserved |

The four missing explicit page-152 variant lines are not four missing text values:
three same-product 1/5mL pairs are aggregated in one row each; the fourth is the
cross-product collapse below. Page-153 product repetition in the materialized
grid reflects explicit native rowspans, not an automatic filling of raw source
blanks. Inspect table cells/spans rather than treating repeated grid values as
new printed product labels.

### Blocking conversion defect F152-01

The original page separates:

| Product | Volume | Approx. capacity | Data-file code |
|---|---|---|---|
| HiTrap MabSelect, second variant | 5 mL | 150 mg/column | 11003490 |
| HiScreen MabSelect | 4.7 mL | 140 mg/column | 28930581 |

T1 table `#/tables/0`, grid row 20 (zero-based), instead has product
`HiScreen MabSelect`, volume `5 mL 4.7 mL`, capacity
`150 mg/column 140 mg/column`, two application marks in each relevant cell and
code `11003490 28930581`. The words survive, but their typed row association is
wrong. The actual native HTML capture confirms the combined row. Quarantine it;
do not infer a repaired table from label order or aggregate inventory counts.

### Targeted variants and blank/mark cells

HiTrap MabSelect SuRe on page 153 preserves both 1mL/30mg and 5mL/150mg pairs,
including **12/12** selected application cells (four marks and eight blanks),
its source code-continuation blank and explicit native product rowspan.

HiTrap Protein A HP on page 152 retains `1 mL 5 mL` and
`20 mg/column 100 mg/column` in aggregate cells. Its application columns contain
two double-mark cells plus four blanks. This retains the source characters but
does not expose twelve independent per-variant application cells. The association
is ambiguous for automated per-variant use; do not report all 24 selected cells
as independently verified. No row reconstruction or source filling was performed.

### Note scope and cross-page continuity

Native table 0 has caption `#/texts/2` and footnotes `#/texts/3` / `#/texts/4`
(notes 1/2). These are table-level bindings, not typed marker-cell-to-note links.
Note 3 (`#/texts/6`) is a separate body text item; table 1 has no footnote link.
All twelve `N/A 3` capacity occurrences survive with the 6/20/50 µL PreDictor
variants. Superscripts are flattened; neither zero capacity nor a multiplier is
inferred. Product-specific note applicability remains to be explicitly reviewed
and represented. The table continues documentarily, but the converter supplies
no typed continuation relation or title binding from table 1 back to table 0.

## K0/K800 on the exact frozen T1

| Metric | K0 | K800 |
|---|---|---|
| Tokens, cached cl100k_base recount | 3921 | 2490 total; maximum 773 |
| Output units | One full-block serialization | Five native chunks: 100, 765, 481, 773, 371 |
| Table content | Both OTSL grids match native T1, including its defect | Collectively retained on diagnostic rejoin; independent context broken |
| Explicit page-break marker | One | Zero; page metadata remains available |
| Docling Graph secondary fallback | Not applicable | Not exercised: all resplit_of values are null |

The four harmful cuts already occur **inside native HybridChunker**, before the
later Docling Graph fallback. `resplit_of: null` does not establish intact rows
or structure. These are actual raw/native outputs, not a reconstruction.

| Boundary | Observed cut |
|---|---|
| 0 -> 1 | First header splits after `Prepacked columns,`, before `ÄKTA compatible` |
| 1 -> 2 | Capacity/unit splits after `50`, before `mg/column` |
| 2 -> 3 | Second table's same header splits at that position |
| 3 -> 4 | A PreDictor capacity splits after `N/A`, before its `3` note marker |

Three of the five isolated chunk bodies are malformed XML forests. The other
two are syntactically well-formed forests of cell tokens/text without a table
host. **None contains a complete self-contained table container.** XML syntax
alone would not establish row/column fidelity, even for those two forests.

An offline diagnostic removed only the repeated contextual heading, concatenated
all fragments and compared parsed structure/text to K0 under whitespace-only
normalization. All table grids and note bodies collectively match; the K0
`page_break` element is absent in K800. This is not a repaired model input or an
implemented assembler. The token difference is not an information-compression
score. Full source page metadata survives, including chunk 2 with both pages,
but parent-table refs/geometry are not exact per-row or child-span anchors.

The full table caption appears only in chunk 0. Notes 1/2 occur only in chunk 2;
MAbTrap Kit and Protein G Mag text occur in chunk 1, while Protein A Mag occurs
in chunk 2. Note 3 occurs only in chunk 4 while most PreDictor rows are in chunk
3. Notes 1/2 are recoverable via parent table footnote references if an assembler
explicitly traverses them; no such serving path was tested. Note 3 has no native
marker/table link. Collective text presence does not supply applicable context
to an individual retrieved row.

## Quarantine and corrective priorities

1. Retain F152-01 quarantine for the incorrect page-152 product/variant association.
   A later deterministic reconstruction from source geometry can be tested in a
   new derived artifact, preserving the raw conversion and its defect.
2. Keep list-valued page-152 variant rows flagged as ambiguous until explicit
   reviewed variant association exists. Page-153 selected checks do not approve
   every unannotated property cell.
3. Quarantine current native K800 table fragments for automated semantic use.
   First test a serializer/chunker that keeps whole rows, headers and complete
   value/unit/note-marker units, with valid structural containers and new regression
   fixtures. Do not treat a higher token cap as a proven fix.
4. Then evaluate explicit continuation and note-scope/context assembly, with exact
   provenance and a remeasured final input budget. The source note/variant scope
   needs human review; no implicit inheritance across pages is authorized.

No code repair, source normalization, artificial raw-table merge, graph import,
production serving or scientific validation is performed by this diagnostic.

## Measurements, artifacts and audit limits

| Worker | Setup/import (s) | Conversion incl. lazy model load (s) | Export (s) | Supervised wall (s) | Sampled peak worker+children RSS |
|---|---:|---:|---:|---:|---:|
| T0 | 208.396 | 74.049 | 2.873 | 289.183 | 916.1 MiB |
| T1 | 126.348 | 136.878 | 2.683 | 270.481 | 1265.7 MiB |
| K0/K800 | Included in worker | No reconversion | Included | 215.781 | 666.6 MiB |

Total supervised wall time was about **775 s (12 min 55 s)**, excluding manual
inspection/capture/audits. The chunk worker reports 210.338 s including imports;
its measured raw-plus-native passes took 4.826 s. Heavy startup and conversion
costs must be distinguished; no throughput conclusion follows from this single
cold/warm sequence. No timeout/resource limit was reached. All recorded pipeline
network attempts and LLM/API call counts are zero; API cost is zero.

Ignored folders under `data/experiments/cytiva/visual-validation-v01/`:
`convert-152-153-20261022-a`, `chunks-152-153-20261022-a`,
`conversion-review-152-153-20261022-a.json` and
`pages152153-diagnostic-20261022-a`. The last contains actual browser captures,
native/selected-cell checks, the reproducible local `audit_chunks.py`, technical
CSV results and final verification/manifest. Original prepared references,
conversion/chunk bytes and prior review packages remain unchanged.

A first derived inspection row view used Windows default decoding for UTF-8 JSON,
garbling copied bullet glyphs. The unchanged v1 and its hash-bound diagnostic gate
are preserved; `conversion-inspection-v2.json` corrects that reporting view with
explicit UTF-8. Source JSON, browser captures, numeric defect evidence and chunk
inputs were not changed. Final comparisons use explicit UTF-8 throughout.
