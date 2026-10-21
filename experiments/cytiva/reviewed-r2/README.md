# Cytiva r2 - documentary development review

Review completed on 20 October 2026, manual CY13981-25Jan21-HB, pages 100–102.
**33 claims: 19 validated, 14 validated with reservations, 0 pending.**

This directory is a selected export of local results. It does not replace the frozen source package or local journals. It contains no PDF, complete conversion, conversation, personal path or secret. The candidate retains the statements derived from the manual.

| File | Purpose |
|---|---|
| `claims.json` | Corrected v5 candidate, 47 entities and 33 claims; only line endings normalized for Git |
| `review.json` | 33 human decisions, per-claim hashes and preserved reservations |
| `manifest.json` | Hashes, evidence provenance without its text, lineage, corrections and checks |

## Verification without models or APIs

From the repository root, with the v0.2 contract's Python dependencies:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.verify_review_package
& '.\.venv-ingestion\Scripts\python.exe' -m unittest experiments.cytiva.test_review_package -v
```

The first check verifies files, the 33 claim/decision links, reservations, provenance-index references and condition probes. It does not rerun lexical evidence validation: the complete source corpus is not distributed.

To rerun it with the original local package (exact hash required):

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.verify_review_package --corpus 'data/experiments/cytiva/pages-100-102-v02-r2/input.json'
```

Hashes detect inconsistencies; they are not a cryptographic signature of reviewer identity. Git preserves the export's history. Package file hashes use UTF-8 with LF line endings: a Windows CRLF checkout does not change their identity. Local artifact and corpus hashes remain hashes of the original bytes. The original local candidate hash is preserved separately; claim hashes and every human decision remain unchanged.

Human messages and intermediate versions remain in the local journal whose hash is recorded in the manifest. No verification command publishes claims. Original human decision text remains in its original language in the JSON records; it has not been translated.

## Corrections and limitations

One GPT-6.1 Sol subscription generation at medium effort produced 32 claims. Review corrected c16's scope and separated its target pH into c33. Other corrections concern equipment choices, conditions, modalities and alternatives/repetition. Editorial additions to c1, c13 and c23 were removed from statements and retained separately in `manifest.json` as review notes rather than manual assertions.

The 14 reservations remain verbatim in `review.json`:

| Claims | Main limitation |
|---|---|
| c3, c4 | Joint equipment choice; interpretation of volumes |
| c7, c27, c28 | Repetitions and compound instructions cannot be executed automatically |
| c12, c13 | Sample-specific incubation conditions; qualitative criteria |
| c14, c16, c17 | Necessity of an action and/or method cannot be determined automatically |
| c18 | Documentary fidelity, without independent scientific validation of the wording |
| c31 | Explicit choice to repeat elution |
| c32 | This claim alone cannot determine a neutralization dose |
| c33 | Target pH without numerical tolerance or an automatic adjustment rule |

The historical c16 reservation describes c33 as « encore en attente » (original wording). c33 was subsequently validated with a reservation. Historical text is not rewritten; each claim's current decision is its own entry.

Claims remain `review_required` in the staging contract: human decisions are separate, with no `approved` state added to the schema. Review is complete, but `publication_allowed` remains false. This package implements neither the adapter into the review database, Neo4j publication nor runtime applicability enforcement.

These are previously inspected development pages, mostly procedural, without extracted symptoms or causes. There is no exhaustive omission reference, recall/F1 measurement, blind test or independent scientific validation. Additional API cost was zero; the subscription interface does not provide reliable token or inference-speed measurements. The 13 condition probes are technical checks, not proof of laboratory applicability.

Next: preserve reservations during future import/rendering, annotate coverage before measuring recall and evaluate new troubleshooting passages. Completing this review does not authorize another import, model call or deployment.
