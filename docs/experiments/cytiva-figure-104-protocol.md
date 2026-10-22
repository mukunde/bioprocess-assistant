# Cytiva page 104: figure/caption conversion and chunking test

Date: 2026-10-22. Status: **T0/T1 and K0/K800 executed; six-card human documentary review completed with reservations; automatic text-only diagram semantics quarantined**. See the [technical trial results](cytiva-figure-104-results.md).
This is development data, not a held-out evaluation. No semantic extraction,
LLM, VLM, API service or Neo4j publication is part of this test.

## Selected page and reference

Use original PDF page **104** (zero-based index **103**), printed page **104**,
Figure **3.29**. The manual has 183 pages and SHA-256
`a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
The one-page excerpt maps page 1 back to original/printed page 104.

This page was already a candidate in the broader
[conversion/chunking protocol](cytiva-conversion-chunking-protocol.md). It was
selected again from the full-page source rendering before conversion. It combines
five selection paths, repeated product labels, vertical role labels, a separate
alternative product, a caption and a referring paragraph. It is a flow diagram,
not a numerical chart; it does not exercise chart axes, bar heights or tables.

The [structured candidate reference](../../experiments/cytiva/page104_figure_spec.json)
records 14 box occurrences, five recommended paths and eleven logical directed
connections, including the connection to the alternative. These are authored
source annotations, not converter results or approved scientific statements.
They do not count individual drawn line segments or branch junctions.

| Path | Fragment | Chain subtype | Recommended product |
|---|---|---|---|
| 1 | Fab | Kappa light chain | Capto L |
| 2 | Fab | Lambda light chain | Lambda FabSelect |
| 3 | scFv | Kappa light chain | Capto L |
| 4 | Domain antibody | Kappa light chain | Capto L |
| 5 | Domain antibody | VH with subscript 3, Heavy chain | MabSelect |

KappaSelect is shown as an **alternative** on the Fab/Kappa branch. The drawn
connection from the Capto L box does not make it a mandatory subsequent process
step. Do not assign the alternative to the lambda, scFv or domain branches.
The paragraph introduces complementary media when Capto L lacks affinity and
specifies constant-region binding for kappa/lambda Fabs. Preserve that context;
the figure is a general selection guide, not a universal compatibility rule.

Caption: "Fig 3.29. AC media for purification of antibody fragments."
The paragraph refers to "Figure 3.29". Source geometry in the reference uses
normalized top-left page coordinates on a 1920 x 1080 pt page. Regions are
approximate source inspection boxes, not converted object bounds or exact word
boxes. `VH3` is an explicit comparison form; the source subscript must be reviewed.

## Prepared local material

Ignored preparation folder:
`data/experiments/cytiva/visual-validation-v01/page-104-figure-preparation-20261022-a/`.
It holds the full-page Poppler rendering, readable source crops, native PDF text,
character positions, source-region overlay, offline preflight and a hash manifest.
The structured reference and [15-probe review sheet](cytiva-figure-104-review.csv)
were frozen there before conversion. Within that historical preparation snapshot,
all execution values remain `not_run`; current results are recorded separately.
That snapshot is not the current decision register. The later [six-card human
review](cytiva-page-104-human-review.md) is complete with reservations. Reference
corrections require a new version
and reason; do not overwrite the frozen snapshot to fit a conversion result.

Native source-character checks locate all 14 labels and the caption. Thirteen
labels match after whitespace removal; the VH-subscript-3 box has native character
order `VHHeavychain3`, while the visible 3 belongs to VH. This is a source-text
reading-order reservation, not a measured Docling defect. Preserve character
positions and review the subscript visually instead of silently moving the 3.

The preflight verifies the original PDF, installed versions/revision, cached
layout/TableFormer weights and tokenizer. It has no network attempts. This proves
local readiness, not conversion quality. It does not download models or load a
vision-language model. The existing runner's Python audit guard is not an OS
firewall; keep remote services disabled and inspect attempted connections.

## Run sequence

Use the existing [conversion/chunking-only runner](../../experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm).
Do not use `ingestion extract`. No runner code change is needed.
The commands below reproduce the executed diagnostic, from the repository root.
Set `$cytivaPdf` to the actual local original PDF; the runner checks its hash.
Output folders must not already exist. For a repeat, change both run IDs.

```powershell
$cytivaPython = '.\.venv-ingestion\Scripts\python.exe'
$cytivaPdf = 'C:\path\to\cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf'
$cytivaRoot = 'data/experiments/cytiva/visual-validation-v01'
$cytivaConvert = "$cytivaRoot/convert-104-20261022-a"
$cytivaChunk = "$cytivaRoot/chunks-104-20261022-a"
$cytivaReview = "$cytivaRoot/conversion-review-104-20261022-a.json"
& $cytivaPython -m experiments.cytiva.visual_validation convert --source $cytivaPdf --output $cytivaConvert --blocks p104 --artifacts '.local-tools/docling-models' --cell-matching
if ($LASTEXITCODE -ne 0) { throw 'Stop: inspect conversion logs before continuing.' }
```

1. Run T0 and T1 on page 104 only. Both retain page/picture images at scale 2,
   CPU/four threads, OCR disabled, image description/classification disabled and
   remote services disabled. T1 adds the same TableFormer V1 accurate profile as
   the previous trial; T0 is a structural-table control, not an alternative figure
   model. Since this page has no table, do not interpret equal T0/T1 results as
   diagram understanding or promise that TableFormer improves arrows.
2. Inspect each full page once, then source crops versus actual native picture
   crops and rendered conversion. Check labels, arrowheads, branch endpoints,
   caption, paragraph and reading order using the
   [targeted visual review method](../visual-document-review.md). Label a full-page
   fallback separately if no complete usable PictureItem exists. Reflowed text
   does not need identical pixels; a missing branch is a content defect.
3. Freeze T1 `document.json` by byte hash and create a separate diagnostic review
   file. Include `purpose: "diagnostic_chunking_only"`, `human_approved: false`,
   and `blocks.p104` with that exact `document_sha256`, inspection notes and
   `status: "usable_for_diagnostic"` or `"quarantined_diagnostic_only"`. Do not
   create a ready/approved record before inspection. A broken or ambiguous
   diagram must be quarantined; chunking it is diagnostic only.
4. Run K0 serialization and K800 on the same frozen T1 JSON:

```powershell
# Only after creating the inspected, hash-bound diagnostic review above:
& $cytivaPython -m experiments.cytiva.visual_validation chunk --run $cytivaConvert --review $cytivaReview --output $cytivaChunk --budgets 800
if ($LASTEXITCODE -ne 0) { throw 'Stop: inspect chunking logs.' }
```

K800 uses the existing structural/hierarchical HybridChunker with `merge_peers`,
DocLang without geometry in text, `cl100k_base`, and the actual Docling Graph
secondary splitting path. K0 is the unsplit serialization control. Do not rerun
conversion between budgets. Defer K600/K1400, OCR and figure interpretation until
the first diagnostic has been examined. Existing workers stop after 15 minutes
or sampled memory exceeding 8 GiB; report timeout/resource limits separately.

## Checks and acceptance

Complete all 15 review rows; retain `fail`, `ambiguous`, `not_applicable` and
`not_run` separately with evidence. The initial probes V12-V15 are expanded, not
silently replaced or marked passed. Keep these four result layers separate:

1. **Image fidelity:** full diagram detected/cropped and readable, including
   vertical labels and KappaSelect. A saved image says nothing about typed edges.
2. **Conversion structure:** exact caption and native figure/caption references,
   paragraph citation and source anchors resolve. Distinguish an explicit native
   caption link from assistant-inferred spatial association. Record all 14 box
   occurrences, all five paths and the alternative, even where the converter
   supplies no semantic representation. Missing relations are not passes merely
   because an image is available; mark absent or unsupported, preserving fallback.
3. **Serialization/chunk conservation:** inspect actual K0 and K800 text and
   `doc_item_refs`, all provenance entries, page/geometry and figure image access.
   Determine whether the image survives as an accessible asset/reference, a text
   placeholder, or neither. Compare splitting loss against K0, not only the PDF.
4. **Future model input:** record whether image, caption, referring paragraph and
   branch conditions would actually arrive together. Collective presence across
   chunks or inherited parent geometry does not establish that a child contains
   the branch or condition. Report `not_tested` for serving/retrieval and any
   assembler that does not exist. Do not invent or silently inject relation text.

Exact IDs/units/operators must remain intact; here `3` is a subtype identifier,
not a concentration. Whitespace normalization is explicit and reversible. Bag
of words cannot approve branch assignments. Zero incorrect branch/product
associations, zero invented process order and resolvable necessary source anchors
are blocking criteria for subsequent semantic use. Missing visual semantics in a
text-only path requires quarantine or a separately reviewed representation; it
does not prevent evaluating caption/text conservation on their own merits.

Record counts with denominators (14 boxes, five paths, one alternative, one
caption, four role labels), missing/ambiguous objects, native versus reconstructed
context, raw/final chunk counts and exact token counts, secondary splits, actual
input budget and limits. Record cold startup, conversion, exports, chunking,
peak sampled memory and any network attempts separately. Conversion success or
zero API cost is not a content-quality result. No numeric chart extraction,
scientific validation, inference or retrieval benchmark is performed here.

## Review outcome

The technical differences, source/conversion images, caption, five paths,
alternative, paragraph, VH3 representation and K0/K800 conservation have now
undergone [human documentary review](cytiva-page-104-human-review.md): six cards
approved with reservations. This does not approve independent scientific validity,
automatic text-only semantic extraction, actual model image input or production
retrieval. Historical preparations, prior page-77/page-88 decisions, source
artifacts and the r2 package remain frozen.
