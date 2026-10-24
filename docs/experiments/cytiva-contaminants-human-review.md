# Cytiva contaminant questions: completed human reference review

Completed on 24 October 2026. **C01–C10 are validated with reservations; no decisions remain pending.**

The review covers the ten question references, expected responses and stated
limits for pages 118–121. Both language formulations remain bound to their
frozen question records. This is documentary review, not independent scientific
validation, operational authorization or approval of retrieval/answer results.
No benchmark has been executed on these questions.

## Decisions and retained limits

| Question | Expected behaviour | Main retained reservations |
|---|---|---|
| C01 | Answer | Source associations are not a confirmed diagnosis. HIC/IEX require selection and optimization; no guaranteed removal. Preserve the manufacturing scope of the serum-free statement. |
| C02 | Answer | HiTrap Phenyl HP is optimal in the specific example. Retain screening advice; do not turn the example into a universal medium/protocol or rule out IEX. |
| C03 | Scoped refusal | No exact IEX pH in the selected subsection. Preserve conditional optimization advice; do not transfer pH 7.0 from Blue-column buffers or invent pH/pI/gradient values. |
| C04 | Answer | Preserve “most” monoclonal antibodies. HIC binds the target while the named contaminants wash through. Blue Sepharose is albumin-specific in this passage; infer no general impossibility for transferrin or quantitative clearance. |
| C05 | Clarify | Ask for decision-relevant sample/application/contaminant context without assuming a contaminant, selecting a technique or requiring a confirmed diagnosis. Preserve the Blue warning and invent no purity threshold. |
| C06 | Answer | Preserve the warning against Blue Sepharose when target hydrophobicity resembles albumin. No numerical similarity threshold, recovery estimate or guaranteed alternative. |
| C07 | Answer | Separate sample-loading/washing flows and 1 mL/5 mL columns. Preserve “generally at least”, alternative wash endpoints, cross-page attribution and the approximate syringe-drop footnote. |
| C08 | Answer | Preserve “usually sufficient” and separate step/linear-gradient alternatives. Keep the correct column-size flow; invent no gradient composition, slope or duration. |
| C09 | Answer | Keep all four buffer formulations separate. Infer no pairing, salt mixing, pH-adjustment recipe or nomenclature correction. Printed subscripts are representation, not independent chemical validation. |
| C10 | Scoped refusal | No loading time without sample volume; column size is not sample volume. No guaranteed complete albumin removal. Keep loading/washing/performance distinct and retain target-hydrophobicity applicability. |

Expected-response inventory: **seven answers, one clarification and two scoped
refusals**. All ten documentary decisions are `validated_with_reservation`;
the two refusals are expected response behaviours, not rejected review items.

## Preserved records and verification

The [preparation](cytiva-contaminants-retrieval-pilot.md),
[questions](../../experiments/cytiva/contaminants-pilot-v01/questions.json),
[evidence](../../experiments/cytiva/contaminants-pilot-v01/evidence.json),
[source topology](../../experiments/cytiva/contaminants-pilot-v01/source_context.json)
and [preparation manifest](../../experiments/cytiva/contaminants-pilot-v01/manifest.json)
remain unchanged. Their pending labels describe the original frozen preparation;
current decisions are recorded separately.

The local review journal is under
`data/experiments/cytiva/contaminants-pilot-v01/human-review/`. It retains the
initial state, ten immutable event records, ten intermediate states and the
current `review.json`. Each event preserves the original French user message,
question/source hashes, reservations, prior-state hash and prior-event hash.
The final verification reconstructs all ten states and checks exact equality
with their recorded snapshots.

The selected required-source sets cover **25 of the 27 corpus records**.
`E118-I` and `E121-EQ` were not individually included in these question reviews.
Completion does not automatically approve every candidate annotation or its use
as a production policy.

Checks passed: all ten event links and state transitions, question/source
bindings, frozen preparation hashes, and preservation of 315 earlier tracked
files/experiment artifacts. There were no model/API calls or retrieval runs.
The local report is
`data/experiments/cytiva/contaminants-pilot-v01/final-human-review-verification.json`.

## Next steps

The [compact reference-review package](../../experiments/cytiva/reviewed-contaminant-questions/README.md)
has been prepared with unchanged decisions and provenance. Its standard-library
verifier reconstructs the ten historical states without requiring local raw
artifacts. This packaging step does not execute retrieval or promote its scope.

1. Review and version the prepared compact package with its supporting files.
   Keep raw source PDF/renders and full local experiment artifacts outside it.
2. Bind a separate dataset adapter to that reviewed package. Preserve the
   existing lexical method and vocabulary; use the new source topology, never
   the cleaning-specific page-166/167 overview IDs. Resolve or explicitly retain
   the pending status of the two source records outside this reference review.
3. Freeze the adapter before measuring paired top-five/top-six retrieval and
   atomic context assembly in a fresh output directory. Report evidence
   coverage, context overhead, budget exclusions and language differences.
4. Retain any failures without tuning this first result in place. Retrieval
   coverage does not establish answer correctness, faithful refusal/clarification
   behaviour or scientific applicability. This remains an assistant-authored,
   known-method new-section development probe, not an independently blind study.
