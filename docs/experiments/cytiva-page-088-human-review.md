# Cytiva page 88: completed human documentary review

Date: 2026-10-21. Status: **nine cards validated with reservations; no pending card**.

## Scope and result

The project user reviewed table 3.6 on original PDF page 88, printed page 88.
The nine cards cover all 40 logical cells exactly once, including two blank cells.
Five footnotes are connected through six printed anchors to twelve product cells.
This is a review of documentary fidelity, not independent scientific validation,
a general table-extraction benchmark or authorization to publish into the graph.

The reviewed candidate is the page-specific deterministic word-coordinate
reconstruction. It preserves source words and does not fill missing cells.
The earlier Docling cell-matching variants remain diagnostic, quarantined results;
this review does not approve their defective tables or establish a general fix.

## Retained reservations

| Card | Human decision | Limits retained |
|---|---|---|
| P88-layout | Validated with reservation | HTML headers lose bold weight; the velocity label wraps. Approval covers the 16 selected layout cells only. |
| P88-N1 | Validated with reservation | Note 1 describes measurement conditions for the two cited capacities, not a general operating or safety limit. |
| P88-N2 | Validated with reservation | Xtra capacity measurement at 250 cm/h remains distinct from its recommended operating velocity of 300 cm/h. |
| P88-N3 | Validated with reservation | SuRe LX capacity measurement at 100 cm/h and 6 min remains distinct from its recommended operating velocity of 500 cm/h. Different measurement conditions do not establish a comparison at identical conditions. |
| P88-N4 | Validated with reservation | Preserve shared operating context, strict pressure inequality, original Mpa spelling and printed parenthetical units; no automatic conversion, exact equivalence or universal safety limit. |
| P88-N5 | Validated with reservation | The original subscript typography is flattened to d 50v. Preserve the volume-distribution median definition, not a mean, maximum or tolerance. |
| P88-row-4 | Validated with reservation | Reducing agent is a category and 1-thioglycerol an example. Preserve the combination and concentrations; the row is not a complete CIP protocol. |
| P88-row-5 | Validated with reservation | Keep manufacturer ligand descriptions without inferring quantitative tolerances, molecular identity or additional properties. |
| P88-row-7 | Validated with reservation | The pack-volume range applies to Bulk packs only. Preserve commercial spellings; availability is documentary and edition-specific, not currently verified. |

## Audit trail and authoritative state

Local artifacts reside under
`data/experiments/cytiva/visual-validation-v01/table-088-notes-20261021-a/`.

- `review-v3/` remains the byte-identical frozen preparation, including its
  historical all-pending `review.json` and read-only HTML. Do not read those
  historical labels as the latest human-review status.
- `human-review-progress/001-P88-layout.json` through
  `human-review-progress/009-P88-row-7.json` preserve the nine original human
  messages verbatim, timestamps, card hashes and reservations.
- `human-review-progress/review-after-009.json` is the final cumulative review
  state. Its `human_approved: true` is explicitly scoped to documentary review
  with reservations. `publication_allowed` remains false.
- `human-review-progress/verification-after-009.json` records the final audit:
  event/state hash chain, all nine card digests, original messages, unchanged
  source packet, unchanged earlier decisions and 40-cell coverage.

These source-containing local artifacts are ignored and are not expected in a
fresh clone. A selected [compact export](../../experiments/cytiva/reviewed-page-088/README.md)
now preserves the table-only packet, final review and replayable decision journal
without the PDF, full-page native word export or images. The final packet canonical SHA-256 remains
`023fac94a3956b38d389356bb8894ee955af92de87df10248994188d81b37867`.
The final cumulative review file SHA-256 is
`e2a07834837fd7e178b8d1b63f50c8fd3374858362647b13dc834571aed366d5`.

The [targeted visual review](../visual-document-review.md) checked P88-layout
using source overlays and an actual local Chrome capture. Its reports remain
historical evidence of the pending state at the time of that technical check.
The 24 experiment regression tests last passed before this decision-only review;
the final audit separately verifies decision and source integrity. The compact
package has its own standard-library verifier and eight regression tests covering
tampering, missing reservations, publication scope, chain replay and Windows
line endings. The source-containing preparation, conversion and word-reconstruction
working notes are separate from this compact export.

## Next steps

1. Review the prepared compact package and its verification results; it retains
   provenance, original human decisions and all reservations while keeping the
   source PDF and bulky raw artifacts outside Git.
2. If improving subscript or header rendering, create a derivative display and
   rerun targeted visual checks without rewriting frozen evidence or approvals.
3. Before retrieval or graph ingestion, implement a controlled projection that
   carries the approval scope, conditions and reservations. Do not promote the
   entire preparation packet merely because the documentary review is complete.
4. Evaluate additional representative pages before generalizing the deterministic
   layout rules. Retain this page as an explicitly scoped reviewed reference.

Offline check from the repository root:

```powershell
python -m experiments.cytiva.verify_page088_package
python -m unittest tests.test_page088_package -v
```
