# Cytiva section-context questions: completed human reference review

Completed on 23 October 2026: **N01–N08 validated with reservations; none pending**.
The eight bilingual development intents (16 formulations, not 16 independent
observations) require 16 distinct source passages from PDF/printed pages 166–167.
Expected response policies: three answers, one clarification and four scoped
refusals. Refusals can retain a partial documentary answer.

## Decisions and retained reservations

| Intent | Expected behaviour | Retained limits |
|---|---|---|
| N01 | Clarify unknown deposit context with a known Protein G product | No assumed deposit, chosen recipe or required confirmed diagnosis; do not ask for an already supplied product |
| N02 | Refuse an unsupported numerical 2-propanol flow rate | Keep the lower-flow warning; do not confuse column volumes and flow |
| N03 | Compare two detergent routes | Preserve examples and separate product conditions; no transferred temperature, time, volume, filtration or pH, and no inferred equivalence |
| N04 | Give the 12-hour ethanol hold but refuse its unsupported volume | Preserve alternative status and backpressure warning; subsequent buffer volume is not ethanol volume |
| N05 | Distinguish SuRe/SuRe LX alkali procedure from Protein G procedure | No recipe transfer, equivalence or universal prohibition; guanidine is not asserted to be the sole cleaning route for every deposit |
| N06 | State the follow-up binding-buffer wash conditions | pH belongs to that buffer, not the detergent; no unique target or automatic adjustment rule |
| N07 | Explain two distinct solvent precautions; refuse an unsupported pressure limit | Increasing gradients address air bubbles; lower flow addresses increased backpressure; no invented numbers |
| N08 | State that the guanidine block omits contact time | No duration inferred from immediately or column volumes; no imported page-167 minimum time |

All absence conclusions remain scoped to selected passages, not all Cytiva
product documentation. Source recommendations and examples are distinct from
application clarification/refusal rules. No scientific validity, process
suitability, operational authorization or graph publication is approved.

## Provenance and verification

The [question preparation](../../experiments/cytiva/cleaning_section_questions_v01.json)
and [source passages](../../experiments/cytiva/retrieval-pilot-v01/evidence.json)
remain unchanged, including historical candidate/pending flags. Current scoped
decisions are retained separately in the ignored local directory
`data/experiments/cytiva/retrieval-pilot-v01/section-human-review/`:

- `review-initial.json`: eight original pending decisions.
- `001-N01.json` through `008-N08.json`: unchanged original French validation
  messages, reservations, source/question/evidence hashes and previous-state links.
- `review-after-001.json` through `review-after-008.json`: cumulative snapshots.
- `manifest-after-008.json` and `verification-after-008.json`: final identities,
  review scope, event replay and source/measurement preservation checks.

All eight transitions were replayed. Human quotations, reservations, question and
evidence bindings, prior-state/event hashes and counts pass. Earlier decisions,
source inputs, code/configuration and prior measured artifacts covered by the
preservation audit remain unchanged. Hashes establish consistency, not a digital
signature authenticating the reviewer. No PDF reconversion, visual rerendering,
retrieval rerun, LLM or external API was used to close this review.

## Relationship to the measured experiment

The section-context experiment was run before this human reference review.
Its original manifest, metrics and N05 outcome are preserved in the compact
[provenance record](../../experiments/cytiva/reviewed-section-questions/provenance.json);
the runtime report remains outside this reference-review package. The recorded scores remain unchanged: v02 and v03
both recover all required evidence for 7/8 additional intents in both languages.
**N05 remains incomplete**, missing `E166-PH` and `E166-P` in both variants.
Approving its reference does not repair that measured retrieval failure.

On the ten earlier reviewed intents, the same recorded experiment has 8/10
complete for v02 and 10/10 for v03. These are evidence-presence results on known
development sources, not answer correctness or independent generalization.
No response layer was evaluated. `benchmark_results_human_validated` and
`publication_allowed` remain false; the user approved documentary references,
not the benchmark output or operational use.

## Compact repository package

The [review package](../../experiments/cytiva/reviewed-section-questions/README.md)
now preserves all eight original events, the exact final state and source/run
provenance, with a standard-library verifier. Its source dependency is already
versioned; no retrieval runtime or full measured context is required to replay
the human review. Original local files and historical preparation flags remain
unchanged. This package is separate from the unversioned retrieval experiments.

## Next step

Test a separately versioned approach for explicit cross-product comparisons
such as N05, without a question-ID special case. Freeze new configuration and
reference inputs before measuring; retain current failures and previous runs.
Future answer-layer tests must separately check conditions, numbers, product
boundaries, partial answers and clarification/refusal behaviour. These 18 reviewed
intents remain development data rather than a held-out industrial benchmark.
