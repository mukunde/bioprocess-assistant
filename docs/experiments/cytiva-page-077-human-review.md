# Cytiva page 77: completed human documentary review

Date: 2026-10-22. Status: **ten cards validated with reservations; none pending**.

## Scope

The project user reviewed the exact T1 conversion of table 3.5 on original and
printed page 77, its seven adjacent remarks, and observed conservation/partition
in the existing K800 output. This is documentary review, not independent
scientific validation, a general extraction benchmark, an executable laboratory
protocol, production retrieval validation or graph publication permission.

Coverage checks confirm:

- All 68 table cells reviewed once: four headers and 16 data rows across four
  columns, including ten empty species cells and 32 pH-column cells.
- The six visual species groups are approved separately; raw blank cells remain
  empty. Absence of other subclasses implies no biological absence.
- Seven remarks, represented by eight converted text items, reviewed once.
  The desalting sentence spans two source items, both retained.
- K800 retains the table's 58 nonempty converted cells and all adjacent remarks
  in two chunks of 760 and 414 tokens. Its ten backing-item geometry entries and
  source references resolve; excerpt page 1 maps to original/printed page 77.

T0 remains an unapproved flattened-table diagnostic. The approved documentary
scope concerns this exact T1 result and the separately recorded interpretations,
not all T1 conversions, new runs, images or figure semantics.

## Retained reservations

| Card | Main reservation |
|---|---|
| P77-layout-species | Preserve ten blank source cells; six species/subclass groups are separate metadata restricted to table 3.5, not automatic forward filling. |
| P77-pH | Keep ranges, inclusive inequalities, Approx., n.a./n.a. spellings and the Rat IgG3 potassium-isothiocyanate condition. No invented tolerance, numeric replacement or operating setpoint. |
| P77-applicability-1 | Keep free-versus-matrix-coupled protein context and qualified guidelines; do not silently harmonize source statements or infer each pH measurement method. |
| P77-applicability-2 | High salt is conditional. Preserve two alternative buffers with their own pH values, without automatically aligning them to table ranges or inventing a recipe. |
| P77-applicability-3 | Avoid excessive washing only under the stated weak-interaction condition; no numeric wash parameters or guaranteed yield loss. |
| P77-applicability-4 | Keep the labile-antibody condition, specific elution and separate alternatives, room temperature/pulses without invented numbers, and both absorption and potassium-isothiocyanate precautions. |
| P77-applicability-5 | Preserve and/or and one sentence across two source items. No invented buffer target or desalting parameters; Chapter 2 is a reference, not imported instructions. |
| P77-applicability-6 | Preserve series versus larger-column alternatives and large-scale context; no inferred capacity addition, sizing, flow rate or quantitative performance guarantee. |
| P77-applicability-7 | Reuse is only to be considered for identical samples, dependent on sample nature. No automatic authorization, zero-contamination guarantee, cycle count or cleaning protocol. |
| P77-chunking | Approve observed conservation only. The Rat IgG3 potassium-isothiocyanate condition is in chunk 0 and the structural/immunological caution in chunk 1. A table-only result can omit relevant context. |

The source subscript typography is flattened in conversion, the extracted HTML
does not reproduce visual group separators, and the green/red hand icons have no
separate typed-warning representation. Those limits are not repaired by review.
K0 has 1469 tokens; K800 totals 1174 under different serialization/contextualization.
That difference is not a compression or omission rate. K600/K1400 and larger-table
secondary splitting were not exercised.

## Source-reference correction

The initial authored reference added final stops to the Goat IgG2 and second
Guinea pig binding entries. Independent PDF rendering and native text inspection
confirm that the manual prints `n.a` in those two positions, matching conversion.
They are reference errors, not conversion punctuation losses. The historical
reference and checks remain frozen; the
[trial report](cytiva-conversion-chunking-results-077-088.md) now records the correction.
This is not an independently annotated exhaustive gold benchmark.

## Audit trail and current state

Ignored local artifacts are under
`data/experiments/cytiva/visual-validation-v01/page-077-review-20261022-a/`.
Preparation views and initial pending records remain unchanged. Current decisions
are separate in `human-review/review-after-010.json`, with ten immutable events
from `001-P77-layout-species.json` through `010-P77-chunking.json`.

Each event preserves the original French human message, timestamp, reviewed-card
digest and reservations. `human_approved: true` in the final cumulative state is
explicitly scoped to documentary fidelity and diagnostic conservation;
`production_retrieval_validated` and `publication_allowed` remain false.

The final `human-review/verification-after-010.json` confirms card hashes,
event/state hash links, original quotations, coverage, unchanged conversion/chunk
inputs and all 214 previously frozen artifacts/review files. No extraction,
conversion or chunker was rerun for these decisions; the tokenizer recount was
local with zero recorded network attempts. No new model/API call was made.

T1 document SHA-256:
`201beee7ce8d23936cde9c82e77e093d61e79133706247a7fbc12b59e7dd7a52`.
Final cumulative review file SHA-256:
`b284c018e064f32fe513ad04b823736702cc242a8a3cedd5546eaf306928aa89`.

## Compact versionable package

The [reviewed page-77 package](../../experiments/cytiva/reviewed-page-077/README.md)
contains the ten exact reviewed cards, final decisions, original French quotations,
reservations and source coordinates. Its journal replays the ten original state
hashes without duplicating all cumulative records. The standard-library
[verifier](../../experiments/cytiva/verify_page077_package.py) checks coverage,
source bindings and scope; the original full conversion can also be replayed
locally. PDFs, images and full conversion artifacts remain outside the package.
The export preserves the historical pending status in cards and records approval
only in the decision journal and final review.

## Next steps

1. Review the compact package before versioning. Its integrity checks establish
   record consistency, not new scientific or retrieval validation.
2. Before retrieval integration, explicitly represent approved species scope and
   links between conditions and precautions, including the cross-chunk
   potassium-isothiocyanate example. Do not fill raw source cells.
3. Test context retrieval and applicability enforcement separately. Neither the
   review nor the 800-token observation authorizes production serving.
4. Continue the representative-page protocol before generalizing to figures,
   continuation tables or secondary splitting.
