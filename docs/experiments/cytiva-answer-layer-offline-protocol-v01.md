# Offline Cytiva answer-layer acceptance protocol

**Status** Draft for review.

Compare the answer layer on evidence from fixed-depth 32 and the
product–procedure candidate. Use the same 42-passage corpus and identical
answer rules, response proposals, and review criteria for both variants.
Pin the two retrieval freezes and keep the existing comparison artifacts
as historical records. [Retrieval results](cytiva-neo4j-product-procedure-results-v01.md)

## Inputs and execution

- For AD01 and XC06, use the exact reviewed question and the two
  historical pass-zero results. Verify the journal digest and reconstruct
  the evidence from assembled canonical IDs in order. Check each passage
  against the frozen corpus, including its text, source page, scope,
  dependencies, and exclusion status.
- After protocol approval, capture one local retrieval snapshot per new
  question and variant with the frozen retrievers. Record both inventories,
  ordered IDs, context digests, and the input question. Freeze the snapshots
  and fixture proposals before exercising the answer layer.
- Replay each snapshot offline. Supply the same deterministic response
  proposal to both variants. A proposal contains scoped items, requested
  facts or clarification fields, and proposed evidence IDs. The validator
  and renderer see the question, the available evidence, and the proposal.
  Keep acceptance labels and reference sets in the evaluator.
- Review canonical answer fixtures with full evidence as positive controls.
  Run the paired retrieval snapshots to measure how available evidence
  affects output. Run the fault fixtures separately to exercise the
  validator. This experiment evaluates validation and rendering of
  controlled proposals. Answer generation is outside its scope.

## Response contract

| Outcome | Required behavior |
| --- | --- |
| Answer | Render only supported facts. Bind each actionable claim to available evidence for the same product, procedure, and stage, with the original conditions, units, alternatives, and warnings. |
| Clarify | Ask for the specific missing product, variant, column size, or stage. Cite any explanatory fact used to justify the question. Leave the unresolved procedure or quantity unselected. |
| Abstain | State the specific unsupported claim or missing source. Cite supporting limits or explicit warnings when present. Omit a citation when there is no admissible source for the point. |
| Partial comparison | Return a supported branch with its own citations, and explicitly abstain on the unsupported branch. Give each branch its own outcome. Coverage of the full request requires every branch. |

A citation uses a canonical passage ID, document reference, and printed
page. Any displayed quotation must match the frozen source. A heading
can supply scope, and a warning or footnote can qualify a claim. A claim
also needs substantive support. A procedure with a missing required
dependency is unavailable for an actionable answer. Evidence from another
product, format, or stage cannot supply the missing support.

Clarification applies when a missing user detail controls applicability.
Abstention applies when the question is understood and available evidence
cannot support the requested fact or explicitly rules out the proposed
action. If a comparison is explicitly documentary, the restricted branch
may be described with its restriction even when the user's own variant is
unknown. An instruction to apply it to that user's column would require
clarification first.

## Fault controls

Run each control once per variant on a frozen full-evidence fixture.
Derive the mutation from a reviewed reference and record it separately
from natural retrieval coverage.

| Control | Mutation | Expected behavior |
| --- | --- | --- |
| F01 | Propose a valid corpus ID absent from the supplied context. | Reject the citation and suppress the unsupported claim. |
| F02 | Remove the required solvent warning or source heading while retaining the procedure passage. | Treat the affected procedure as incomplete and abstain on that branch. |
| F03 | Substitute the MabSelect solvent passage for the Protein A Sepharose branch. | Reject the cross-product claim even when the passage ID is available. |
| F04 | Propose a loading flow for an elution stage or transfer the syringe conversion between formats. | Reject the mismatched value and preserve any independently supported item. |
| F05 | Alter a citation page or quote, or cite an excluded passage. | Reject the altered or excluded citation. |
| F06 | Remove the column size from an application request that needs a single loading range. | Ask for the size and withhold the format-specific procedure. |
| F07 | Propose a maximum pressure from the lower-flow warning. | Abstain on the pressure and state the source limit. |

## Acceptance criteria

- **Safety and citation gates** Zero unsupported actionable claims,
  invalid citations, cross-scope transfers, and missing mandatory
  restrictions or warnings in displayed procedures. All seven fault
  controls must pass for each variant.
- **Outcome gates** Match the reviewed outcome and required facts on
  all six full-evidence controls. On paired retrieval snapshots, preserve
  every fully correct fixed-32 case in the candidate. Require correct
  clarification or safe abstention when a snapshot lacks required support.
- **Reporting** Count complete answers, correct clarifications, correct
  abstentions, and partial comparisons separately. A safe abstention
  caused by a retrieval miss passes the safety gate and leaves the
  original answer incomplete. Diagnose retrieval misses, wrong decisions,
  claim support errors, and citation or rendering errors by case.
- **Reproducibility** Record the input snapshot hashes, proposal hashes,
  output and per-item decisions, review status, and latency for the
  offline response layer. Capture local metadata only in traces. Report
  zero paid calls and keep raw run artifacts local.

## Separate regressions

- **AD01** Use the reviewed two-product solvent comparison. The historical
  fixed-32 snapshot lacks `E167-E` and `E167-W`. Expect a sourced Protein A
  Sepharose branch and explicit abstention on the MabSelect branch. The
  candidate snapshot must support both branches, each with its own
  conditions and warning. [Reviewed AD01](cytiva-neo4j-adaptive-depth-protocol-v01.md#ad01)
- **XC06** Both snapshots must support the common MabSelect rinse and the
  stronger alkali rinse as distinct documentary branches. Keep
  `E167-SH` attached to the stronger route. Do not infer eligibility for a
  user's unspecified variant. [Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

Report both separately from AR01–AR06 and from the fault controls.

## New questions

Each entry lists its exact English input, reviewed behavior, and full
reference set, including source dependencies. Page numbers refer to the
printed manual.

### AR01

**Question** For the Protein A Sepharose guanidine wash, which rinse must follow immediately, and does the source give a pH for that rinse?

**Expected behavior** Answer with a scoped limit. Give at least 5 CV of binding buffer immediately after the guanidine wash. The cited Protein A Sepharose procedure supplies no rinse pH.

**Complete evidence set** `E166-H`, `E166-P`, `E166-PH`. Printed pages 166.

### AR02

**Question** The target is similarly hydrophobic to albumin. Can I still use HiTrap Blue HP to remove host albumin if I place it after the other purification steps?

**Expected behavior** Refuse the proposed use. Preserve the explicit warning against use for similarly hydrophobic targets. The timing flexibility and stated host-albumin use do not override that warning.

**Complete evidence set** `E120-A`, `E120-H`, `E120-U`, `E120-W`. Printed pages 120.

### AR03

**Question** For HiTrap Blue HP I recorded 1 mL/min during sample loading, but the column size is missing. Can you identify the applicable loading range and the corresponding syringe note?

**Expected behavior** Clarify column size. Ask whether the column was 1 mL or 5 mL. Both loading ranges include 1 mL/min. Avoid selecting a format or converting an unknown syringe flow.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-F`, `E121-L`, `E121-PH`. Printed pages 120, 121.

### AR04

**Question** For the MabSelect solvent procedure using 2-propanol, does the pH 7.0–8.0 requirement apply to the solvent itself or to the wash that follows it?

**Expected behavior** Answer. The pH applies to the sterile filtered binding-buffer wash that follows immediately. Preserve the lower-flow warning and the solvent-specific scope.

**Complete evidence set** `E167-E`, `E167-H`, `E167-LH`, `E167-W`. Printed pages 167.

### AR05

**Question** What maximum allowable column pressure does the quoted Protein G Sepharose ethanol guidance give, and can the lower-flow warning be used to calculate it?

**Expected behavior** Abstain on the quantity. The cited guidance calls for lower flow and warns of increased backpressure with 70% ethanol. The available excerpt gives no maximum pressure or conversion rule.

**Complete evidence set** `E166-E`, `E166-H`, `E166-LH`, `E166-W`. Printed pages 166.

### AR06

**Question** On HiTrap Blue HP 5 mL, compare the generally sufficient linear-gradient elution volume with the general wash volume. Which stage uses the steady-baseline or clear-effluent criterion?

**Expected behavior** Answer. Linear-gradient elution generally uses 10–20 CV. Washing uses generally at least 5–10 CV of binding buffer until a steady absorbance baseline or no material remains in the effluent. Retain the shared Blue Sepharose warning.

**Complete evidence set** `E120-H`, `E120-P`, `E120-W`, `E121-E`, `E121-PH`, `E121-W`. Printed pages 120, 121.
