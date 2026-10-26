# Frozen structured-control challenge S01-S12: results

Date: 26 October 2026. Actual trial completed once after all twelve human
decisions. The frozen method, reviewed references and earlier experiments were
not changed. No model, paid API or network connection was used.

## Outcome

All 24 EN/FR submissions passed their reviewed references; all 12 paired scenarios
passed with no critical semantic differences. There were no runtime errors or
scored failures. The gate is `context_and_diagnostics_pass`. The paired language
forms are correlated observations, not 24 independent scenarios.

| Scenario | EN / FR | Context tokens (each language) | Observed unit states |
|---|---|---|---|
| S01 | Pass / Pass | 1462 | A-elution-buffer/buffer_formulation: supported; B-wash/column_volumes: supported; B-wash/stopping_criteria: supported |
| S02 | Pass / Pass | 1504 | A-load/flow_rate: supported; A-load/syringe_correspondence: supported; B-elute/flow_rate: supported |
| S03 | Pass / Pass | 349 | A-end/stopping_criteria: needs_clarification; B-principles/principle: supported |
| S04 | Pass / Pass | 838 | A-load/flow_rate: needs_clarification; A-binding/buffer_formulation: supported |
| S05 | Pass / Pass | 1190 | A-flow/flow_rate: needs_clarification; A-position/relative_position_in_workflow: supported; B-flow/flow_rate: supported |
| S06 | Pass / Pass | 1181 | A-equilibrate/flow_rate: quarantined; A-equilibrate/buffer_role: quarantined; A-wash-buffer/buffer_role: supported; B-ion/principle: supported; B-ion/ph_vs_pi_condition: quarantined |
| S07 | Pass / Pass | 841 | A-joint/flow_rate: unsupported_selector; A-elution-buffer/buffer_formulation: supported; A-pressure/maximum_pressure: missing_source |
| S08 | Pass / Pass | 625 | A-load/flow_rate: unsupported_selector; A-position/relative_position_in_workflow: supported |
| S09 | Pass / Pass | 1145 | A-load/flow_rate: supported; A-load/syringe_correspondence: supported; A-pressure/maximum_pressure: missing_source |
| S10 | Pass / Pass | 987 | A-note/syringe_correspondence: unsupported_transformation; A-load/flow_rate: supported |
| S11 | Pass / Pass | 348 | A-end/stopping_criteria: needs_clarification; B-flow/flow_rate: out_of_scope; C-principle/principle: supported; D-flow/flow_rate: needs_clarification |
| S12 | Pass / Pass | 1458 | A-modes/column_volumes: supported; A-modes/elution_mode: supported; B-binding/buffer_formulation: supported |

## Analysis of non-served requests

No observed outcome departs from the approved references. Non-served units are
intentional reference outcomes, not hidden failures or successful answers:

- S03-S05 preserve local clarification while serving independent siblings.
- S06 keeps both equilibration units and the pH/pI condition quarantined, while
  serving washing-buffer and general charge-separation information.
- S07 distinguishes an unsupported product/IEX mapping from missing pressure;
  neither becomes a claim of chemical incompatibility or whole-manual absence.
- S08 identifies the invalid preparation/flow restriction without blocking the
  independent workflow-position item or releasing the equilibration source.
- S09 recognizes only the exact printed syringe reference, with missing pressure
  explicit. S10 withholds the unapproved transformation even though E121-F is
  legitimately present in the loading bundle; no binding is assigned to A-note.
- S11 preserves A's contradiction, B's identified out-of-scope product and D's
  ambiguous identity, while serving C's general IEX principle.
- S12 serves the requested CV alternatives and binding formulations without
  requiring an unnecessary size for A or adding operating elution bindings to B.

These results concern plan states, diagnostics, support sets and attribution.
No natural-language answer was generated; omission of an unrequested numerical
value from a future generated answer has not been demonstrated by this trial.

## Integrity, resources and provenance

All 24 raw outcomes were saved before scoring. Exact supporting-source integrity,
required bundles, task/item/column/stage bindings, aggregates and token recounts
passed. E118-I and E121-EQ were absent from admitted passages, roots and bindings.
The runner verified frozen inputs, the actual human review and earlier files
unchanged, with zero attempted network calls. The original frozen manifest and
template retain their historical preparation status; actual approval and actual
execution are separate records.

Contexts range from 348 to 1504 tokens, below the 2,048-token budget; at most 2 roots were selected, below the six-root budget.

Runtime initialization took 317.2 ms. The first evaluation took 862.4 ms and includes lazy tokenizer setup; the other calls ranged from 44.8 to 99.0 ms (median 70.5 ms). These are descriptive observations from one ordered run, not a benchmark, a p95 result or a comparison with an LLM. Preservation and file-hashing overhead is not included in these evaluation timings.

## Limits and next step

This is a same-corpus structured diagnostic challenge authored with knowledge of
the method, not a blinded holdout or evidence of generalization to a new manual.
It does not evaluate free-text parsing, answer faithfulness, scientific validity
or real-process suitability. No automatic adoption or method update follows.

The [compact reviewed package](../../experiments/cytiva/reviewed-structured-control/README.md) now preserves this baseline and all saved outputs. Next,
define a separate structured-versus-free-text comparison before implementing
or evaluating a new interpreter. Keep this run and both quarantines unchanged.

## Saved records

- [All saved outputs and original scores](../../experiments/cytiva/reviewed-structured-control/results.json)
- [Actual human decisions](../../experiments/cytiva/reviewed-structured-control/review.json)
- [Decision history and S01 amendment](../../experiments/cytiva/reviewed-structured-control/events.json)
- [Run verification and artifact provenance](../../experiments/cytiva/reviewed-structured-control/provenance.json)
- [Portable manifest](../../experiments/cytiva/reviewed-structured-control/manifest.json)
- [Exact proposed file list and checks](cytiva-structured-control-s-package.md)

The original local run and intermediate review records remain unchanged. This
export selects the complete saved outputs and approved evidence without source
PDFs, environment files, model assets or private intermediate inventories.
