# Cytiva pages 152-153: continuation-table conversion and chunking test

Date: 2026-10-22. Status: **T0/T1 and K0/K800 executed; conversion association and native chunk structure quarantined; human decisions pending**. See the [trial results](cytiva-table-152-153-results.md).
No LLM/VLM extraction, paid API, source-table repair, automatic table merger,
Neo4j publication or retrieval benchmark is part of this preparation.

## Source and scope

Use original PDF pages **152 and 153 together**, zero-based indices **151 and
152**, printed pages **152 and 153**, from the 183-page manual. SHA-256:
`a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
The excerpt maps page 1 to original 152 and page 2 to original 153;
never treat excerpt numbering as the original citation.

Table A1.7 is captioned on page 152:
"Table A1.7. Summary of products for antibody purification with references to product data files".
Page 153 repeats the same ten ordered headers, without a repeated caption or an
explicit continued label. The documentary continuation is a candidate annotation
based on adjacent pages, repeated headers and visual/content continuity, pending
human confirmation. Do not claim that conversion already produces this link.

The boundary falls between the complete **HiScreen MabSelect** group on page 152
and **PreDictor MabSelect** on page 153. It is not a product row split across the
page break. Two or more native table objects can be a faithful segmented result;
one physical merged object is not an acceptance requirement. Preserve original
segments and page anchors before proposing a separate continuation relation.

The [structured source reference](../../experiments/cytiva/pages152153_table_spec.json)
and [16-probe sheet](cytiva-table-152-153-review.csv) are candidates prepared from
independently rendered pages and native source characters before conversion.
They are development data, not independently approved exhaustive gold.
The broader [protocol](cytiva-conversion-chunking-protocol.md) and its V16-V21
probes remain historical preparation; this test expands those checks.

## Reference coverage and difficult associations

- Ten columns on each page, including all six application/compatibility columns,
  the approximate binding-capacity header and the data-file-code header.
- 20 product groups / 24 variant lines on page 152; 12 groups / 22 lines on page
  153. Total: 32 groups and 46 variant lines. Group names and source medium-volume
  line counts are cross-checked, not all property cells independently annotated.
- Four selected HiTrap variants and all 24 corresponding application cells:
  eight marks and sixteen blanks. Inspect exact row/column association, not just
  finding the glyph or number anywhere on the page.
- Three note bodies, with distinct product/marker scope; twelve PreDictor `N/A`
  capacity occurrences with superscript 3 across four groups and three volumes.

| Page | Product group | Variant volume | Approx. capacity | Marked application columns |
|---|---|---|---|---|
| 152 | HiTrap Protein A HP | 1 mL | 20 mg/column | Syringe compatible; Prepacked columns, ÄKTA compatible |
| 152 | HiTrap Protein A HP | 5 mL | 100 mg/column | Same two columns |
| 153 | HiTrap MabSelect SuRe | 1 mL | 30 mg/column | Prepacked columns, ÄKTA compatible; Process development |
| 153 | HiTrap MabSelect SuRe | 5 mL | 150 mg/column | Same two columns |

The other four application cells in each selected variant line are **source
blanks**, not explicit incompatibility statements. Mark presence does not establish
an operating protocol or current product availability. No experimental performance
is inferred from tabulated approximate capacities or their numerical ratios.

On both selected 5 mL continuation lines, product and data-file-code cells are
visually blank. Preserve them as such. A proposed group scope may associate
variants with the product/code printed once above; that is separate pending
metadata, never automatic filling of raw blank cells. Data-file codes are
strings referring to product data files, not numeric capacities or automatically
catalogue numbers. Retain `11003558` for the selected Protein A group and
`11003490` for the selected SuRe group without copying into source blanks.

## Notes and applicability

| Note | Original text | Candidate scope and retained limit |
|---|---|---|
| 1, page 152 | Includes buffer stock solutions for approximately 20 purifications using a syringe. | MAbTrap Kit marker 1 only; approximate count, no capacity/usage guarantee or complete protocol |
| 2, page 152 | Paramagnetic beads. | Protein G Mag Sepharose Xtra and Protein A Mag Sepharose Xtra marker 2; no handling procedure inferred |
| 3, page 153 | The products are used for high-throughput screening of chromatographic conditions (i.e., capacity, selectivity, purity). | N/A superscript-3 capacity entries in PreDictor MabSelect, SuRe, Xtra and SuRe LX; preserve each 6/20/50 µL variant and its marker |

Do not replace `N/A` by zero, infer no binding capacity or invent an expansion not
provided here. The note describes the stated screening use, not a numerical
capacity. A marker 3 is not a capacity multiplier. Do not attach notes 1/2 to
all continuation-page products merely because the table continues. Retain
mg/column versus mg/mL versus mg/well, µL versus mL, Approx., From and ranges;
no unit conversions, extrapolation or performance calculation is prepared.

## Local preparation and offline readiness

Ignored folder:
`data/experiments/cytiva/visual-validation-v01/pages-152-153-preparation-20261022-a/`.
It contains Poppler renderings of both full pages, native text/character geometry,
readable header/row/note/boundary crops, source checks, the offline preflight and
frozen copies/digests of this protocol, reference and preparation sheet.
No conversion output was inspected to author the reference.

Source checks locate all 20 header occurrences after explicit whitespace-only
comparison, all 32 product names, the four volume/capacity pairs, 24 selected
mark/blank cells and all three note texts. Native medium-volume glyph lines
cross-check 24+22 physical lines; twelve N/A occurrences are located in page
153's capacity column. Coordinate-band/grouping checks are source diagnostics,
not independently approved semantic annotations. Native superscript typography
and note attachment still require human review against images.

The preflight checks source hash, installed Docling/core/Graph versions and pinned
revision, layout/TableFormer cached weights and cached cl100k_base tokenizer.
It records no network attempts; no download is necessary. The existing Python
audit network guard is not an OS firewall. Keep remote services, image description,
classification, chart extraction and all LLM/VLM features disabled.

## Reproduction commands

Use the existing [conversion/chunking-only runner](../../experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm),
not `ingestion extract`. No runner implementation change is needed. From the
repository root, set the real local original PDF path. Output folders must be
new; change the run suffix for a repeat rather than overwrite earlier artifacts.

```powershell
$cytivaPython = '.\.venv-ingestion\Scripts\python.exe'
$cytivaPdf = 'C:\path\to\cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf'
$cytivaRoot = 'data/experiments/cytiva/visual-validation-v01'
$cytivaConvert = "$cytivaRoot/convert-152-153-20261022-a"
$cytivaChunk = "$cytivaRoot/chunks-152-153-20261022-a"
$cytivaReview = "$cytivaRoot/conversion-review-152-153-20261022-a.json"
& $cytivaPython -m experiments.cytiva.visual_validation convert --source $cytivaPdf --output $cytivaConvert --blocks p152-153 --artifacts '.local-tools/docling-models' --cell-matching
if ($LASTEXITCODE -ne 0) { throw 'Stop: inspect conversion logs.' }
```

Run **T0/T1 on the two-page block**, not two independent invocations. T0 disables
table structure; T1 uses TableFormer V1 accurate with cell matching enabled.
Both use CPU/four threads, OCR off, image scale 2, page/picture images on and
remote/enrichment features off. The source is digital; OCR is deferred unless
missing characters are actually observed. Record effective profiles/weights,
startup, conversion/export wall time and peak sampled worker+child memory.
Existing safeguards stop a worker after 15 minutes or sampled memory above 8 GiB;
record failures as resource results, not quality scores.

After conversion, compare each original full page and targeted crops against the
actual native table JSON/grid, exported HTML/CSV and image crops, using the
[targeted visual method](../visual-document-review.md). Check page/charspan/bbox
and **all** provenance entries. Record independent objects versus native explicit
continuation links; adjacency or similar headers alone is not a link supplied
by the converter. Missing title/notes/rows or misassigned units/products are
blocking for later semantic use.

Only after inspecting T1, create the separate review file named above with
`purpose: "diagnostic_chunking_only"`, `human_approved: false` and `blocks.p152-153`.
Bind its `document_sha256` to the exact T1 JSON; set inspected `status` to
`usable_for_diagnostic` or `quarantined_diagnostic_only`, with defects/limits.
Never fabricate a ready review before inspecting the result. Do not merge tables,
fill blanks, move notes or rewrite conversion to improve its scores.

```powershell
# Only after visual inspection and the exact hash-bound diagnostic review:
& $cytivaPython -m experiments.cytiva.visual_validation chunk --run $cytivaConvert --review $cytivaReview --output $cytivaChunk --budgets 800
if ($LASTEXITCODE -ne 0) { throw 'Stop: inspect chunking logs.' }
```

Use **K0/K800 on the same frozen conversion**, with the pinned structural/
hierarchical HybridChunker, merge_peers, DocLang without geometry in text,
cl100k_base and actual Docling Graph secondary splitting. K0 is a full-block
serialization control; K800 need not make one chunk or one table. K600/K1400
are deferred until first inspection establishes a concrete context/budget question.

## Chunk-level checks and decision

For each final chunk, map table segment and all inherited source items to actual
excerpt/original pages. Repeated headers are acceptable and often necessary;
missing or reassigned headers are not. Compare row association, not bags of words.

Check exact product/variant/approximate capacity/unit, all selected mark/blank
cells, data-file identifiers and note markers. For each marker, determine whether
the note body is in the same native chunk, reachable by an explicit source link,
or absent. Page-153 rows must retain a way to identify their table title/continuation
without automatically inheriting page-152 note scope. Collective note presence
across output chunks does not establish usable context for a retrieved row.

If native secondary splitting occurs, inspect every final child's exact text,
recount its tokens and distinguish inherited parent geometry from the actual
child span. If it does not occur, record **not exercised**, not approved. Separate
native context from a proposed future context assembler; none is implemented here.
Reconstructed context, if later attempted, requires separate provenance and a
remeasured budget. Do not equate all pages of a parent table with every child's
actual evidence location.

Complete the 16 probe rows with pass/fail/ambiguous/not_applicable/not_run and
artifact references. Every human decision stays pending until explicitly made.
Count correct selected cells with denominators, missing/duplicate groups/variant
lines, both header occurrences, three note bodies and scoped marker bindings,
actual direct/indirect anchors, raw/final chunk counts, token totals/maxima,
secondary splits, network attempts and time/memory by stage. Distinguish
conversion loss from K0 serializer loss and additional chunking loss.

Quarantine any unit with incorrect product/variant association, dropped quantity,
changed operator/unit, missing critical note, inferred negative from a blank or
invented continuation/note scope. Scope quarantine to affected units where possible;
whole-block chunking may still run as an explicitly quarantined diagnostic.
Successful execution does not validate product performance, current availability,
production retrieval or scientific applicability. The executed [technical trial](cytiva-table-152-153-results.md) found F152-01 and
native header/unit/marker cuts; this protocol has no human approval. Prior
page-77/88/104 packages, raw artifacts and decisions remain untouched.
