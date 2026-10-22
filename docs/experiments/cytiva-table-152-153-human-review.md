# Cytiva pages 152–153: completed documentary review

Review completed: 2026-10-23. **Six cards validated with reservations; no pending
decision among these six cards.** This closes the inspected documentary review,
not a complete audit of every property in table A1.7 or a scientific validation.

The [original conversion diagnostic](cytiva-table-152-153-results.md) and
[derived reconstruction/chunking experiment](cytiva-table-152-153-repair.md)
remain historical records. Their source JSON, contexts, chunks and initial
pending statuses were not rewritten. Later human decisions are separate,
hash-bound, append-only records containing the original French messages verbatim.

## Decisions

| Card | Approved documentary scope | Retained limits |
|---|---|---|
| P152-HiTrap-HiScreen | Separate HiTrap 1 mL / 30 mg/column, HiTrap 5 mL / 150 mg/column, and HiScreen 4.7 mL / 140 mg/column; retain source marks, blanks and printed codes | Blank second HiTrap product cell stays blank; grouping is separate metadata. Capacities remain approximate. No scientific performance/current availability approval. |
| P152-153-continuity | Both native tables belong to logical table A1.7; boundary falls between complete product groups | No caption/continued label is printed on page 153. Continuation is a reviewed annotation; retain two native objects and page anchors, without inherited note scope. |
| P152-N1 | One marker-cell link: MAbTrap Kit to note 1 | Approximately 20 purifications refers to supplied buffer stock solutions using a syringe. No guaranteed count, column-reuse authorization or missing operating parameters inferred. |
| P152-N2 | Two marker-cell links: Protein G Mag Sepharose Xtra and Protein A Mag Sepharose Xtra to note 2 | Paramagnetic-bead description applies to these entries only; no handling protocol, equipment specification or numerical performance inferred. |
| P153-N3 | Twelve N/A superscript-3 capacity-cell links: four PreDictor groups, each with 6/20/50 µL variants | Preserve N/A without expansion, zero substitution or inferred absence of binding capacity. Note 3 supplies no numerical capacity. |
| P152-153-chunking | Observed conservation on the frozen derived K0/K800 experiment | No production retrieval approval, total-request budget guarantee or approval of unresolved variant interpretation. Repeated note context does not encode the approved cell-specific links. |

There are **15 unique approved cell–note bindings: 1 + 2 + 12**. Approval is
limited to the recorded documentary scopes. Global scientific/production
approval and publication authorization remain false.

## Observed chunk conservation

The opt-in format is `structural-table-xml-v1`, distinct from native DocLang/OTSL.
The original native K800 fragments remain unchanged and are not promoted by
this decision.

- K0: one full derived block, **3579 tokens**, including two tables, the native
  text inventory and an explicit page boundary.
- K800: **7 fragments** — six table fragments and one eight-item source-text
  inventory. Counts: **212, 782, 794, 547, 659, 661, 720**; total **4375**.
- **43 derived data rows / 430 grid positions** are preserved, in order, with
  complete row/span groups and value/unit/marker text. Each table fragment
  repeats a full header, caption context and table-level note context.
- K800 keeps exact table/grid-row references and original/excerpt page metadata.
  Its parent table/cell geometry is resolved through the hash-bound document.
- The token limit covers serialized fragment text, not the future assembled
  prompt, tool schemas, retrieved context combination or generation.

Context repetition increases token totals. K0's inventory-first serialization
does not reproduce original PDF reading order, and the inventory is not an
evaluated retrieval unit. Different formats/inputs do not establish a controlled
compression or speedup result.

## Remaining quarantine and implementation work

Table 0 retains three aggregate variant rows, quarantined for per-variant use:

| Derived grid row, zero-based | Product |
|---|---|
| 1 | HiTrap Protein G HP |
| 9 | HiTrap Protein A HP |
| 13 | HiTrap rProtein A FF |

The 43 conserved derived rows must not be described as 46 independently
reconstructed physical variant lines. Complete property annotation for every
product was outside this review.

The frozen chunks/context still carry their historical pending annotations.
Approved continuation, HiTrap grouping and cell–note relations live in the
review records. A future derived artifact must explicitly integrate them and
remeasure its final assembled text budget; their approval does not imply that
integration already happened. Native tables and raw source blanks must remain
preserved.

Recommended next steps:

1. Prepare a compact, provenance-bound review package for version control,
   separating it from source PDFs, images and complete raw conversion outputs.
2. Integrate reviewed annotations in a new derived serving artifact and rerun
   structural/conditional-context checks. Keep the three ambiguous variant rows
   excluded from per-variant answers until specifically reconstructed/reviewed.
3. Evaluate actual retrieval and assembled context on troubleshooting questions;
   this conservation review does not measure answer quality or latency in use.

## Final verification and local records

The six decision events were replayed from the initial state, with each source
card, previous-state digest and six resulting snapshots verified. All 15
approved cell–note coordinates are unique. The **413 pre-repair experiment
files** remain byte-identical. Frozen reconstruction and chunk manifests were
also checked; no source or chunk bytes were changed to record approval.

Local records under the ignored experiment base
`data/experiments/cytiva/visual-validation-v01/pages152153-human-review-20261023-a/`:

- `001-P152-HiTrap-HiScreen.json` through `006-P152-153-chunking.json`:
  immutable decisions with original human quotations, scoped approvals and
  retained reservations.
- `review-after-006.json`: final six-card documentary state.
- `verification-after-006.json`: event replay, hash checks, counts and remaining
  quarantine.
- `manifest-after-006.json`: hashes of the final review artifacts and link to the
  prior manifest.

The global `human_approved: false` flag means no blanket approval of the dataset;
each accepted card has its own `validated_with_reservation` decision and scoped
human approval. Publication and production retrieval flags remain false.

No extraction LLM/VLM, API call or paid service was used for this recording and
verification step. The final checks replay records and hashes; they do not
re-run PDF conversion or the earlier code test suite.
