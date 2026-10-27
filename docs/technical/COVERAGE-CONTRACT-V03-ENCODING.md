# Coverage v03: machine encoding following CC01-CC06 approval

The [actual collective approval](../decisions/2026-10-27-coverage-contract-CC-review.json)
records the human reply `ok go` to CC01-CC06. The
[original proposal](COVERAGE-CONTRACT-V03-PROPOSAL.md) remains unchanged as the
pre-approval snapshot. This document selects concrete field names and boundary
fixtures for implementation; it does not claim separate human approval of these
subsequently authored encodings. No runtime or historical reference is modified.

## Version and scope

The standalone [schema](coverage-summary-v03.schema.json) uses
`coverage-0.3-proposed`. It is an application-produced summary, never caller input
or an override of source policy. The future v03 integration must add this versioned
summary at the structured-control and bridge boundaries, with explicit component
identities. Do not load it into old v01/v02 schemas or modify pinned components.
Do not reinterpret the legacy `all_supported_ready_units_covered` field. A retained
legacy projection must remain labelled with its old version/semantics.

## Fields and their authority

| Field | Meaning |
|---|---|
| `inventory_complete` | The whole positive request is identified, not merely the recognizable fragment |
| `known_requested_units` | Number of identified positive information units, keeping owners/items/selectors separate |
| `accounted_units` | Number of known units with exactly one explicit terminal outcome |
| `all_known_units_accounted_for` | Every known key has one outcome and no duplicate/orphan outcome exists; cardinality equality alone is insufficient |
| `assessment_complete` | Documentary eligibility and valid context admission have been assessed for the known inventory; independent of whether the original text inventory is complete |
| `has_assessment_error` | Execution, provenance/context integrity or accounting failure prevents a complete global assessment |
| `eligible_ready_context_coverage` | Valid covered and eligible-ready counts, applicability state and denominator scope |
| `request_support` | Supported known-unit count, known-unit denominator and `all_requested_units_supported` |
| `has_unserved_known_units` | At least one identified positive unit lacks valid support; this flag alone says nothing about unrecognized text |
| `full_service` | Exact alias of the new `all_requested_units_supported`, not of eligible-context coverage |

An information unit is identified by stable task/item/information identity plus
occurrence identity where needed. Two different buffer uses need distinct items;
generated IDs must not collapse positive units. That parser repair remains future
work, not something this summary may infer or fix after planning.

The eligible-ready set is fixed before assembly. A budget-incomplete unit remains
eligible and uncovered. Unsupported/missing/quarantined/clarification units remain
in the whole-request denominator and keep their distinct outcomes; an exclusion
directive itself and an inactive negated exclusion add no positive unit.
Positive units blocked by a restriction remain globally counted and unserved.

Covered means a valid full admissible dependency/guard bundle and exact unit
binding, provenance and resource checks, not a document hit. Counts are derived
from validated unit evidence. They are not model confidence, answer-quality or
scientific-suitability scores.

## Counts, scope and state

Let K be known positive units, A the units with one valid outcome, S validly
supported known units, E the pre-assembly eligible-ready set, and C its members
with valid admitted context. Enforce `0 <= A,S <= K` and `0 <= C <= E <= K`.
The request-support denominator always equals K. It never drops blocked units.

When E cannot be established, both eligible/covered counts are null. Unknown is
not zero. If a known-subset audit is reliable, its paired integer counts may be
retained even while global coverage is not assessed or in error; they must be
explicitly labelled `known_units_only`, not a complete-request ratio.

Evaluate the global state in this precedence order:

1. `error` when `has_assessment_error=true`.
2. `not_assessed` when inventory, exact accounting or assessment is incomplete.
3. `not_applicable` when the assessed eligible-ready count is zero.
4. `complete` when the nonempty eligible-ready set is entirely validly covered.
5. `partial` when at least one eligible-ready unit lacks valid context.

The scope is `complete_request` only with complete inventory/accounting/assessment
and no assessment error. Otherwise it is `known_units_only` for reliable integer
subset counts or `unassessed` for null counts. No global success is inferred from
known-subset C=E. No percentage field is emitted; 0/0 is never displayed as 100%.

`has_unserved_known_units` is `S < K`. It can be false with incomplete inventory,
so consumers must inspect inventory completeness too. With K=0 it is false,
while full service remains false: no positive request was answered.

Full service is true only if K>0, inventory/accounting/assessment are complete,
there is no assessment error, S=K and the eligible-context state is complete.
All support must be valid; new `all_requested_units_supported` and `full_service`
must agree exactly. One unsupported/quarantined/missing unit keeps both false,
without automatically changing otherwise complete eligible coverage.

## Partial errors and retained evidence

A unit-local operational error does not erase valid independently served siblings.
Their validated support can remain counted while global coverage reports `error`.
A global context-integrity error cannot count unvalidated context as support;
historical candidate bindings belong in a rejected/audit record, not the valid
covered count. Errors have explicit outcomes when known and are not relabelled
as missing documentary evidence.

Missing/duplicate/orphan outcome associations are accounting errors: keep the
identified request, report global error, and never claim full service. They are
not an opportunity to deduplicate away a requested unit.

## Declarative fixtures and future acceptance

The [12 boundary fixtures](coverage-summary-v03-examples.json) describe proposed
summary objects, not outputs of an implemented v03 or a new FV experiment:

| Fixture | Boundary |
|---|---|
| CE01 | FV06 meaning: context 1/1, request support 1/3, partial service |
| CE02 | Nonempty fully supported request |
| CE03 | Eligible unit rejected by budget remains in E |
| CE04 | All positive units quarantined, no eligible-ready set |
| CE05 | All positive units lack documentary support |
| CE06 | Zero positive units, no vacuous success |
| CE07 | Incomplete original inventory despite fully covered known subset |
| CE08 | Documentary eligibility not yet assessable |
| CE09 | Unit-local runtime error with a valid independent sibling |
| CE10 | Global context integrity failure |
| CE11 | Missing known-unit outcome is an accounting error |
| CE12 | Positive request blocked by an active restriction stays counted |

Static schema and formula consistency checks are in
[the encoding report](coverage-summary-v03-checks.json). They validate the proposed
encoding only; they are not runtime conformance or successful language handling.
Before a future v03 freeze, exercise the same boundaries through actual engine
and bridge outputs and distinguish interpretation, documentary outcomes, context
assembly, whole-request service and handling-evaluation gates. Refusal/clarification
can be correctly handled while full service is false. No runtime flag certifies
the wording of an eventual generated answer.

The FV06 frozen score/reference stays unchanged, as do all other historical
trials, source exclusions, mandatory warnings and resource limits. No automatic
mapping migration, parser repair, serving activation or new prospective test is
performed by this encoding preparation.
