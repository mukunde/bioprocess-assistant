# Coverage indicators before v03: choices pending human approval

Status: proposal only, prepared on 27 October 2026 after PR48. No runtime,
schema, source policy, original reference, method lock or score is changed.
CC01-CC06 below are pending; recommendations are not recorded human decisions.

## Observed discrepancy and existing intent

FV06 has three units: P washing-specific maximum pressure is unsupported by the
adapter; Q general maximum pressure is missing from the exact 25 eligible
excerpts; Q loading flow is supported and has its complete admitted bundle.
Both S and F0 produce those expected individual states in EN and FR.

The [existing specification](TASK-REQUEST-TECHNICAL-SPEC-V01.md) says that
`all_requested_units_accounted_for` means explicit outcomes, not available answers.
It also defines `all_supported_ready_units_covered` over eligible unblocked units,
while stating that it cannot excuse missing adapter mappings. The
[core](../../ingestion/structured_request.py) deliberately resolves that tension
by forcing this flag false whenever an unsupported selector occurs. The FV
reference instead expects true for eligible-unit coverage. Its resulting two
aggregate failures remain part of the official frozen result.

The proposal separates those meanings instead of declaring the intentional
conservative override an accidental code bug. Context support is not generated
answer quality, scientific suitability, laboratory authorization or deployment
readiness.

## CC01 — Separate accounting, context coverage and complete request support

Recommended: retain distinct dimensions:

1. `inventory_complete`: does the application claim it identified the entire
   positive request? Interpretation uncertainty prevents that claim.
2. `all_known_units_accounted_for`: does every identified unit have exactly one
   explicit outcome? A refusal, clarification or failure can be accounted for.
3. `eligible_ready_context_coverage`: are all identified, ready units with eligible
   documentary support covered by valid admitted context?
4. `all_requested_units_supported` / the bridge's `full_service`: are all positive
   requested units faithfully interpreted and documented, with no unserved unit
   or execution/integrity failure and a complete inventory?

Alternative: retain the overloaded conservative flag as the only coverage signal.
That preserves the ambiguity exposed by FV06 and hides whether the available
context was assembled correctly.

## CC02 — Make denominators explicit and prevent success through filtering

Recommended: count information units, identified by task/item/information, not
source passages, roots, tasks or sentences. Preserve requested ordering and owners.

The eligible-ready denominator is established from interpretation/documentary
classification before assembly. A budget-rejected eligible unit stays in that
denominator and is uncovered; it cannot disappear because its final state is not
supported. Valid coverage requires the full admissible support/dependency bundle,
correct provenance, matching unit binding and resource limits, not a source hit.

All known positive units stay in the whole-request denominator: clarification,
unsupported selector/transformation, missing evidence, quarantine, active
restriction blocking a positive unit, budget failure and execution error remain
explicit outcomes. A restriction directive by itself is not a positive unit;
an inactive negated exclusion does not manufacture another request.

For FV06: eligible context coverage is 1/1; documented request support is 1/3;
all three outcomes are accounted for; complete request support is false.
The unsupported and missing-source units receive no source binding.

Alternative: publish a single 1/3 percentage as generic coverage. It describes
request support but does not reveal successful eligible-context assembly.

## CC03 — Preserve partial service and diagnostic distinctions

Recommended: `unsupported_selector`, `missing_source`, `quarantined`,
`needs_clarification`, `budget_incomplete` and operational errors keep their
distinct unit-level meanings. None is silently converted into eligible support.
An unsupported unit does not force eligible-context coverage false when the
independent eligible units are all covered. It does keep whole-request support
false. Do not suppress those independent units as a consequence of the metric.

Conversely, an ambiguous owner/restriction or shared contradictory context may
legitimately block dependent units under the reviewed scope policy. This proposal
does not relax that policy, remove required warnings or override quarantine.
Pressure absence stays bounded to the 25 excerpts; E118-I/E121-EQ stay excluded.

Alternative: one unsupported selector forces every coverage dimension false.
This preserves conservative overall reporting but obscures partial success.

## CC04 — Avoid vacuous success and distinguish missing assessment

Recommended presentation rules:

| Situation | Eligible-context indicator | Complete request support |
|---|---|---|
| Nonempty eligible-ready set, all valid bundles admitted | `complete`, N/N | True only if the full request is also supported and inventory complete |
| Nonempty set, at least one unit lacks a valid bundle | `partial`, n/N | False |
| No eligible-ready units, complete/assessed inventory | `not_applicable`, no percentage | False when positive requests remain unsupported |
| Incomplete interpretation or eligibility assessment | `not_assessed` for global coverage; known-subset counts may be retained as explicitly partial audit | False |
| Runtime or context-integrity failure prevents assessment | `error`; no global success claim | False |
| Zero positive requested units | No 100% claim; `not_applicable` or `no_positive_request` presentation | False; not a complete answered request |

An honest 0/0 is not displayed as 100%. An unknown denominator is not presented
as zero. No missing unit is invented to fill an incomplete inventory. If known
subset counts survive an error, their limited scope must remain explicit.

Alternative: keep Boolean `all([])=true` without an applicability status. This is
mathematically valid but misleading for the intended product/evaluation reporting.

## CC05 — Version the change; preserve every historical contract

Recommended: add explicitly named dimensions in a separately versioned v03
contract, using a new core/adapter path if necessary for replay. Do not silently
reinterpret `all_supported_ready_units_covered` in existing v01/v02 outputs or
reuse the same contract version for changed semantics. Legacy fields remain
historical; any v03 alias/deprecation rule needs an explicit definition before
implementation.

Original FV06 references/scores, all twelve decisions, native outcomes and method
locks remain unchanged. No retrospective replacement score or claim that the
original frozen acceptance gate passed is permitted. Changing these dimensions
alone does not repair buffer item identity or French phase association.

Alternative: rename/reinterpret the old flag in place. This would undermine
replay and make identical keys mean different things across checkpoints.

## CC06 — Evaluate correct handling separately from full answerability

Recommended: a future reference can expect correct refusal/clarification/
quarantine/missing-source handling while also expecting full service false.
A mixed-support case can pass its handling/context test without all its answers
being available. This does not excuse a parser omission, wrong owner/stage,
missing supported sibling, invalid provenance or incorrect diagnostic.

New acceptance must still require exact reviewed intent, every requested outcome,
correct unit-level diagnostics, required eligible support, scope/provenance and
budget constraints. Actual generated-answer correctness remains a separate later
evaluation; a runtime status alone cannot certify an appropriately worded answer.
Any combined score must state its gates; never label handling success as a fully
answered request. Freeze new expectations before the next prospective trial.

Alternative: require full service true for every trial case. That makes deliberately
quarantined or missing-evidence challenge cases impossible to pass for the right
reason.

## Illustrative FV06 report under the proposal, not a replacement result

```json
{
  "inventory_complete": true,
  "all_known_units_accounted_for": true,
  "eligible_ready_context_coverage": {
    "covered_units": 1,
    "eligible_ready_units": 1,
    "status": "complete"
  },
  "request_support": {
    "supported_units": 1,
    "known_requested_units": 3,
    "all_requested_units_supported": false
  },
  "full_service": false,
  "status": "partial"
}
```

This is a semantic example, not an implemented machine schema or another scored
FV run. Final field naming, applicability representation and schema/version IDs
can be specified after these six choices are approved. Before implementation,
include boundary checks for FV06, all-quarantined/missing requests, zero-positive
requests, incomplete inventory, budget exclusion and integrity/runtime failure.
