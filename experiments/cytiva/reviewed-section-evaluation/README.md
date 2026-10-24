# Reviewed H01–H10 and frozen section-only results

Completed 24 October 2026: **ten bilingual reference intents validated with
reservations, none pending** (eight answers, one clarification, one corpus-source
limit). Original French human messages and the ten-event chain are preserved.
The frozen one-candidate run completed with **8/10 bilingual intents complete**,
EN 9/10 and FR 8/10; H02 FR and H09 EN/FR miss indispensable sources. The pilot
gate remains blocked. No generated answer or scientific applicability is validated.

| File | Selected contents |
|---|---|
| `review.json` | Exact final review values, question/reference bindings and all reservations |
| `events.json` | Ten original events, with original messages and canonical chain hashes |
| `results.json` | All twenty exact contexts, scores, diagnostics and measured summary |
| `provenance.json` | Frozen manifest/source lineage, original artifact hashes, run review snapshot and preservation attestation |
| `manifest.json` | Portable LF/CRLF file/support digests and completed export status |

The [prepared package](../section-evaluation-v01/PROTOCOL.md), its manifest and
per-reference `pending` flags remain unchanged historical preparation. Its verifier
reports integrity of preparation, not current execution status. `review.json`
contains the later decisions; `results.json` and this export describe the completed
run. The review's `benchmark_authorized: false` is its historical state: later
execution authorization is preserved separately in provenance. No such historical
flag is promoted by rewriting it.

E118-I and E121-EQ remain excluded. H10 validation approves neither passage nor
permission to reuse another phase's numbers. Required source presence is not
answer correctness or validated precision. H/C fact overlap and known sources
prevent an independent or unseen-corpus generalization claim.

## Offline verification

Repository root, standard library only, no PDF or original local runs required:

```powershell
python -S -m experiments.cytiva.verify_section_evaluation_package
python -S -m unittest tests.test_section_evaluation_package -v
```

The verifier checks source serialization, scope dependencies, all review/event
bindings, original selected artifact reconstruction, metrics and frozen inputs.
It checks recorded token bounds; it does not recompute tokenizer counts or timings
without the original environment, authenticate the reviewer, or rerun retrieval.
Original byte-level preservation of 1,222 local files is retained as an attestation,
not newly demonstrable from a fresh clone. Hashes prove consistency, not scientific
truth. No source PDF, complete page images, weights, secrets or private inventory
paths are exported. Selected source quotations already belong to the reviewed
source corpus; no corpus source approval is added here.

This is lot A. It is independent of the later v03b runtime; lot B depends on it.
See the [frozen result report](../../../docs/experiments/cytiva-section-evaluation-results.md).
