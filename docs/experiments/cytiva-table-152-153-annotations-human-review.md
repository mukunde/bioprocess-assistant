# Cytiva pages 152–153: completed v2 annotation-conservation review

Completed on 23 October 2026: **P152-153-annotated-chunking validated with
reservations; no pending decision for this card.** The six earlier
[documentary decisions](cytiva-table-152-153-human-review.md) remain unchanged.
This new decision approves observed conservation and annotation placement in the
exact [v2 experiment](cytiva-table-152-153-annotations.md), not production use or
scientific performance.

## Validated scope

- **HiTrap grouping g1:** derived rows 19–20 remain together; row 20's product
  cell stays blank. Grouping remains an annotation, without invented source text
  or a new native rowspan.
- **Continuation c1:** the page-153 segment is explicitly related to logical
  table A1.7. Both native tables and page anchors stay distinct, without automatic
  note-scope inheritance. Caption context is identified as reviewed continuation.
- **Note n1:** one cell link for MAbTrap Kit, preserving approximate count and
  syringe wording, without inferred column-reuse authorization.
- **Note n2:** two links for the marked Protein G/Protein A Mag Sepharose Xtra
  entries, preserving material-only scope without a derived handling protocol.
- **Note n3:** twelve links for the marked PreDictor capacity cells. N/A is
  unchanged; neither zero capacity nor a new interpretation is added.
- All **15 links** retain their source cell, note reference and approval
  provenance. Table note bodies are included only with explicit links. Unmarked
  products sharing a fragment do not inherit those notes.
- Physical separation is preserved in both K0 and K800: **40 primary derived
  rows plus three quarantined aggregate rows**, with source text unchanged.

## Output counts

| Measure | Primary | Quarantine |
|---|---:|---:|
| Derived data rows | 40 | 3 |
| K0 tokens | 3952 | 446 |
| K800 fragments | 8, including one source-text inventory | 1 |
| K800 total tokens | 5230 | 425 |
| Maximum tokens per K800 fragment | 765 | 425 |
| Explicit approved cell–note links | 15 | 0 |

The source-text inventory preserves eight native text items; it is a preservation
unit, not a validated retrieval result or an applicability rule. The 800-token
cap covers XML alone, not a complete prompt or assembled multi-fragment context.
K0's inventory-first order does not reproduce original PDF reading order.

## Reservations and remaining work

Table-0 rows **1, 9 and 13** remain quarantined for per-variant interpretation:
HiTrap Protein G HP, HiTrap Protein A HP and HiTrap rProtein A FF. Their aggregate
values must not be silently paired, filled or promoted to automatic answers.
The 43 preserved derived rows are not 46 independently reconstructed physical
variant lines.

Full reservations and provenance remain in the SHA-bound annotation sidecar;
concise limitations are included in XML. The schema remains experimental
`reviewed-structural-table-xml-v2`, distinct from DocLang/OTSL. No complete
property-cell audit, retrieval/answer-quality evaluation, current product
availability check, graph publication or independent scientific validation is
approved. Production defaults remain unchanged.

Recommended next step: prepare a compact provenance-bound v2 review package.
Actual retrieval integration/evaluation remains separate. The three ambiguous
rows must stay excluded from per-variant use unless specifically reconstructed
and reviewed later.

## Decision record and checks

The original French validation message is preserved verbatim in the append-only
event. The event binds the reviewed card, previous state, document, annotation
set, artifact manifest, chunk manifest and displayed comparison by SHA-256.
Replaying the event reproduces the final state; original sources, annotation
sidecar, XML, chunk metadata and the pending preparation card remain unchanged.

Local records under the ignored experiment base
`data/experiments/cytiva/visual-validation-v01/review-annotated-chunks-152-153-20261023-a/`:

- `001-P152-153-annotated-chunking.json`: original message, scoped decision and
  all eight retained reservations.
- `review-after-001.json`: final one-card review, validated with reservations.
- `verification-after-001.json`: hash/transition checks, counts and remaining
  quarantine.
- `manifest-after-001.json`: review artifacts and previous-manifest lineage.

The copied output manifests and chunk metadata keep their historical pending
flags; this later review record supplies the scoped conservation approval.
Global `human_approved`, `production_ready` and `publication_allowed` remain false;
the card-level `human_approved_for_observed_conservation` flag is true.

This final recording step replays the decision and checks hashes; it does not
rerun conversion, chunking or the earlier 212-test suite. No LLM/VLM or paid API
was invoked.
