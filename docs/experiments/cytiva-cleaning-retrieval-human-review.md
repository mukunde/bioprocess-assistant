# Cytiva cleaning pilot: completed human reference review

Completed on 23 October 2026: **10 questions validated with reservations; none pending**.
Scope: Appendix 5 cleaning sections, PDF/printed pages 166–167. The reference
contains ten bilingual intents (20 formulations), not 20 independent test cases,
and 17 exact source passages. This is development data, not a held-out benchmark.

## Decisions

| Question | Reference behaviour | Retained limits |
|---|---|---|
| Q01 | Answer the cleaning recommendation | No established cause or deposit-specific recipe from backpressure alone |
| Q02 | Preserve the guanidine/wash sequence | Exact quantities and immediate wash; no added duration, flow or page-167 recipe |
| Q03 | Preserve the detergent example | Example remains an example; no invented detergent volume |
| Q04 | Preserve the ethanol alternative and separate warning | No mandatory addition after detergent, numerical flow or ethanol volume |
| Q05 | Preserve four separate cleaning alternatives | No mixing or sequential combination; retain concentration pairings and conditions |
| Q06 | Preserve the stronger-alkali sequence | Restricted SuRe/SuRe LX scope, three steps, no reuse guarantee |
| Q07 | Distinguish product-specific solvent routes | No transfer of the 12-hour hold to MabSelect and no inferred general prohibition |
| Q08 | Refuse unsupported numerical values | Qualitative help remains; absence conclusion limited to selected pages |
| Q09 | Request product and problem context | No assumed deposit, chosen recipe or required confirmed diagnosis |
| Q10 | Refuse unsupported diagnosis and performance confirmation | No sole lipid cause, guaranteed capacity restoration or inferred impossibility of restoration |

The expected response distribution is **7 answers, 1 clarification and 2 scoped
refusals**. These are reference labels, not measured application results.
Clarification/refusal behaviour is an application policy grounded in the cited
source distinctions, not a verbatim instruction from the manual.

## Provenance and current state

The [preparation dossier](cytiva-cleaning-retrieval-pilot.md),
[questions](../../experiments/cytiva/retrieval-pilot-v01/questions.json),
[evidence](../../experiments/cytiva/retrieval-pilot-v01/evidence.json) and
[preparation manifest](../../experiments/cytiva/retrieval-pilot-v01/manifest.json)
remain unchanged, including their historical pending flags. This later review
supplies scoped decisions and does not silently rewrite the prepared references.

Local decision records are retained in the ignored directory
`data/experiments/cytiva/retrieval-pilot-v01/human-review/`:

- `review-initial.json`: original ten pending decisions.
- `001-Q01.json` through `010-Q10.json`: original French validation messages,
  reservations, question/evidence hashes, source PDF identity and prior-state links.
- `review-after-001.json` through `review-after-010.json`: cumulative snapshots.
- `manifest-after-010.json`: cumulative file identities and review scope.
- `verification-after-010.json`: final deterministic checks.

All ten event/state transitions were replayed and the source-package, question,
evidence and prior-record hashes checked. Previous decisions and preparation
files were preserved. This verifies consistency, not reviewer cryptographic
identity, PDF scientific validity, new extraction quality or retrieval performance.
The PDF was not reconverted or rerendered during the final recording step.

## Compact repository package

The [reviewed package](../../experiments/cytiva/reviewed-cleaning-retrieval/README.md)
now preserves the initial pending state, ten original decision events, minimal
state metadata and exact final review, with a standard-library verifier and
regression tests. It depends on the unchanged prepared references; original local
events and snapshots are not overwritten. File hashes are portable across LF/CRLF
checkouts; historical event/state bytes are reconstructed for lineage checks.
Preparing this package performs no publication or benchmark execution.

## Next step

Implement an isolated local passage-retrieval baseline and context assembler. Index source passages only, never the questions, expected
answers, this summary or decision labels. Measure indispensable-evidence coverage
before/after assembly, product/condition/quantity preservation, context size,
latency and resource use. Test expected clarification/refusal behaviour separately
once a response layer exists; retrieval alone cannot establish those outcomes.

The proposed 2048-token context budget still needs feasibility checking and an
explicitly frozen tokenizer/serialization. A complete evidence bundle that does
not fit must remain visibly incomplete rather than lose a warning. The
[three-arm protocol](retrieval-comparison-protocol.md) remains a separate later
comparison, not a benchmark already executed by this review.

No independent scientific validation, operational suitability, graph publication
or production retrieval is approved. `publication_allowed` and
`benchmark_executed` remain false. No LLM/VLM, embedding model or paid API was
called. Original human messages are preserved verbatim in the local events.
